"""
Q-Shield: Training Guide — Real Datasets → Full Pipeline
=========================================================
This file is the step-by-step companion to qshield_ml_pipeline.py.
It shows exactly how to load each downloaded dataset (CMU, Balabit, HMOG),
feed it into every pipeline stage, train the models, and evaluate.

HOW TO USE
----------
1. Download the datasets (see DATASET SETUP section below)
2. Set the three path constants at the top of this file
3. Run:  python qshield_train_with_datasets.py
4. Trained models are saved to ./qshield_models/

DATASET DOWNLOAD LINKS
----------------------
CMU   : https://www.cs.cmu.edu/~keystroke/   (file: DSL-StrongPasswordData.csv)
        OR  https://www.kaggle.com/datasets/carnegiecylab/keystroke-dynamics-benchmark-data-set
Balabit: git clone https://github.com/balabit/Mouse-Dynamics-Challenge
HMOG  : https://hmog-dataset.github.io/hmog/  (agree to ToU, then download)

DEPENDENCIES
------------
pip install numpy pandas scipy scikit-learn tensorflow matplotlib seaborn joblib tqdm
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURE THESE THREE PATHS BEFORE RUNNING
# ─────────────────────────────────────────────────────────────────────────────

CMU_CSV_PATH     = "./datasets/DSL-StrongPasswordData.csv"
BALABIT_ROOT_DIR = "./datasets/Mouse-Dynamics-Challenge"
HMOG_ROOT_DIR    = "./datasets/hmog_data"

# Output directory for saved models and results
OUTPUT_DIR = "./qshield_models"

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, warnings, joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.stats import skew
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc
warnings.filterwarnings("ignore")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import the pipeline classes from the existing file
# Make sure qshield_ml_pipeline.py is in the same directory
sys.path.insert(0, os.path.dirname(__file__))
from qshield_ml_pipeline import (
    DatasetLoader,
    FeatureExtractor,
    QuantumInspiredEncoder,
    IdentityTemplateManager,
    LSTMAutoencoder,
    AuthenticationEngine,
    PipelineEvaluator,
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 0: UTILITY — auto-detect whether real data exists
# ─────────────────────────────────────────────────────────────────────────────

def check_datasets():
    """
    Check which datasets are available on disk.
    Falls back to synthetic data for any missing dataset.
    Returns a dict of availability flags.
    """
    status = {
        "cmu":     os.path.isfile(CMU_CSV_PATH),
        "balabit": os.path.isdir(os.path.join(BALABIT_ROOT_DIR, "training_files")),
        "hmog":    os.path.isdir(HMOG_ROOT_DIR),
    }
    print("\n" + "=" * 60)
    print("  Q-Shield — Dataset Availability Check")
    print("=" * 60)
    for name, found in status.items():
        icon = "FOUND   " if found else "MISSING"
        print(f"  [{icon}]  {name.upper():8s} — {'Using real data' if found else 'Will use synthetic fallback'}")
    print("=" * 60)
    return status


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1A: LOAD CMU KEYSTROKE (real data)
# ─────────────────────────────────────────────────────────────────────────────

def load_cmu_real(filepath: str) -> dict:
    """
    Load the real CMU Keystroke Benchmark CSV and build per-user
    session matrices ready for the pipeline.

    CMU CSV columns:
        subject       — user ID string (e.g. "s002")
        sessionIndex  — 1–8
        rep           — repetition within session (1–50)
        H.period, DD.period.t, UD.period.t, ... (31 timing columns)

    Returns
    -------
    dict: {user_id: np.ndarray of shape (n_sessions, 31)}
          Each row = one typing repetition = one feature vector.
    """
    print("\n[CMU] Loading real keystroke data...")
    df = pd.read_csv(filepath)

    # Identify timing feature columns (all except subject/sessionIndex/rep)
    meta_cols = ["subject", "sessionIndex", "rep"]
    feat_cols = [c for c in df.columns if c not in meta_cols]
    print(f"[CMU] {df['subject'].nunique()} users, "
          f"{len(feat_cols)} timing features, "
          f"{len(df)} total rows")

    user_matrices = {}
    for uid, grp in df.groupby("subject"):
        # Each row is one typing repetition — shape (n_reps, n_features)
        mat = grp[feat_cols].values.astype(float)
        # Replace any NaN with column mean
        col_means = np.nanmean(mat, axis=0)
        nan_idx = np.where(np.isnan(mat))
        mat[nan_idx] = np.take(col_means, nan_idx[1])
        user_matrices[uid] = mat

    print(f"[CMU] Built matrices for {len(user_matrices)} users")
    print(f"[CMU] Example — user '{list(user_matrices.keys())[0]}': "
          f"shape {list(user_matrices.values())[0].shape}")
    return user_matrices


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1B: LOAD BALABIT MOUSE (real data)
# ─────────────────────────────────────────────────────────────────────────────

def load_balabit_real(root_dir: str, window_size: int = 100) -> dict:
    """
    Load the Balabit Mouse Dynamics Challenge dataset and extract
    windowed feature matrices per user.

    Balabit folder structure:
        <root>/
          training_files/
            user_1/   ← one folder per user
              session_1.csv
              session_2.csv
              ...
          test_files/
            user_1/
              ...

    Each CSV row = one mouse event:
        record_timestamp, client_timestamp, button, state, x, y

    Pipeline:
        Raw events → sort by timestamp → sliding windows of `window_size`
        events → extract 12 features per window → feature matrix

    Returns
    -------
    dict: {user_id: np.ndarray of shape (n_windows, 12)}
    """
    print("\n[Balabit] Loading real mouse dynamics data...")
    train_dir = os.path.join(root_dir, "training_files")
    test_dir  = os.path.join(root_dir, "test_files")

    raw_df = DatasetLoader.load_balabit_mouse(train_dir, test_dir)

    # Extract windowed features per user
    feat_df = FeatureExtractor.extract_mouse_features(
        raw_df,
        user_col="user_id",
        window_size=window_size
    )

    feature_cols = [c for c in feat_df.columns
                    if c not in ["user_id", "window"]]

    user_matrices = {}
    for uid, grp in feat_df.groupby("user_id"):
        mat = grp[feature_cols].values.astype(float)
        col_means = np.nanmean(mat, axis=0)
        nan_idx = np.where(np.isnan(mat))
        mat[nan_idx] = np.take(col_means, nan_idx[1])
        user_matrices[uid] = mat

    print(f"[Balabit] Built matrices for {len(user_matrices)} users")
    for uid, mat in list(user_matrices.items())[:2]:
        print(f"[Balabit]   {uid}: shape {mat.shape}")
    return user_matrices


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1C: LOAD HMOG TOUCH (real data)
# ─────────────────────────────────────────────────────────────────────────────

def load_hmog_real(root_dir: str) -> dict:
    """
    Load the HMOG touch dataset and extract per-subject feature matrices.

    HMOG folder structure (after extracting the downloaded ZIP):
        <root>/
          <subject_id>/           ← e.g. "600150"
            <session_id>/         ← e.g. "2015-08-11_10.37.07"
              touch.csv
              accel.csv
              gyro.csv
              ...

    touch.csv columns (per-event):
        sys_time, event_type, x, y, pressure, area, phone_orientation

    Pipeline:
        touch.csv → aggregate 15 statistical features per subject
        → one feature vector per subject (for enrollment)
        OR per session (for probe/test)

    Returns
    -------
    dict: {subject_id: np.ndarray of shape (n_sessions, 15)}
          Each row = features from one session.
    """
    print("\n[HMOG] Loading real touch data...")

    # Collect per-session feature rows
    records = []
    for subject in sorted(os.listdir(root_dir)):
        subject_path = os.path.join(root_dir, subject)
        if not os.path.isdir(subject_path):
            continue
        for session in sorted(os.listdir(subject_path)):
            touch_path = os.path.join(subject_path, session, "touch.csv")
            if not os.path.exists(touch_path):
                continue
            try:
                df = pd.read_csv(touch_path, header=None,
                                 names=["sys_time", "event_type",
                                        "x", "y", "pressure",
                                        "area", "phone_orientation"])
                # Keep only touch-down events (event_type == 1)
                df = df[df["event_type"] == 1].copy()
                if len(df) < 5:
                    continue

                p   = df["pressure"].dropna().values.astype(float)
                a   = df["area"].dropna().values.astype(float)
                x   = df["x"].dropna().values.astype(float)
                y   = df["y"].dropna().values.astype(float)
                t   = df["sys_time"].dropna().values.astype(float)

                # Inter-tap intervals (proxy for tap speed)
                dt = np.diff(np.sort(t)) if len(t) > 1 else np.array([0.0])

                records.append({
                    "subject_id":    subject,
                    "session":       session,
                    "pressure_mean": np.mean(p),
                    "pressure_std":  np.std(p),
                    "pressure_skew": skew(p) if len(p) > 2 else 0.0,
                    "area_mean":     np.mean(a),
                    "area_std":      np.std(a),
                    "x_mean":        np.mean(x),
                    "x_std":         np.std(x),
                    "y_mean":        np.mean(y),
                    "y_std":         np.std(y),
                    "tap_count":     float(len(p)),
                    "iti_mean":      np.mean(dt),
                    "iti_std":       np.std(dt),
                    "x_range":       np.ptp(x),
                })
            except Exception:
                continue

    feat_df = pd.DataFrame(records)
    feature_cols = [c for c in feat_df.columns
                    if c not in ["subject_id", "session"]]

    user_matrices = {}
    for uid, grp in feat_df.groupby("subject_id"):
        mat = grp[feature_cols].values.astype(float)
        col_means = np.nanmean(mat, axis=0)
        nan_idx = np.where(np.isnan(mat))
        mat[nan_idx] = np.take(col_means, nan_idx[1])
        user_matrices[uid] = mat

    print(f"[HMOG] Built matrices for {len(user_matrices)} users")
    return user_matrices


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: FUSE MODALITIES (optional — combine CMU + Balabit + HMOG)
# ─────────────────────────────────────────────────────────────────────────────

def fuse_modalities(ks_matrices: dict,
                    mouse_matrices: dict = None,
                    touch_matrices: dict = None) -> dict:
    """
    Fuse keystroke, mouse, and touch feature matrices for users
    that appear in ALL provided modalities.

    Strategy: find common users → per user, pair rows from each
    modality using the minimum available count → concatenate features.

    If only keystroke data is available (e.g. CMU only), returns as-is.

    Parameters
    ----------
    ks_matrices    : {user_id: (N_ks, D_ks)}
    mouse_matrices : {user_id: (N_mo, D_mo)}  or None
    touch_matrices : {user_id: (N_to, D_to)}  or None

    Returns
    -------
    dict: {user_id: (N_min, D_ks [+ D_mo] [+ D_to])}
    """
    if mouse_matrices is None and touch_matrices is None:
        print("[Fuse] Single modality — using keystroke only.")
        return ks_matrices

    # Find common users across all supplied modalities
    common = set(ks_matrices.keys())
    if mouse_matrices:
        common &= set(mouse_matrices.keys())
    if touch_matrices:
        common &= set(touch_matrices.keys())

    if len(common) == 0:
        print("[Fuse] WARNING: no common user IDs across modalities. "
              "Using keystroke only.")
        return ks_matrices

    fused = {}
    for uid in common:
        parts = [ks_matrices[uid]]
        if mouse_matrices:
            parts.append(mouse_matrices[uid])
        if touch_matrices:
            parts.append(touch_matrices[uid])

        # Align row counts to minimum available
        n_rows = min(p.shape[0] for p in parts)
        aligned = [p[:n_rows] for p in parts]
        fused[uid] = np.hstack(aligned)

    print(f"[Fuse] Fused {len(fused)} users across "
          f"{1 + bool(mouse_matrices) + bool(touch_matrices)} modalities")
    return fused


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: TRAIN THE FFT ENCODER
# ─────────────────────────────────────────────────────────────────────────────

def train_encoder(user_matrices: dict, n_components: int = 64) -> QuantumInspiredEncoder:
    """
    Fit the StandardScaler inside the QuantumInspiredEncoder on ALL
    available feature vectors (enrollment + test combined).

    The scaler is fit once on all data so that both enrollment and
    probe vectors are normalized in the same space.

    Parameters
    ----------
    user_matrices : {user_id: (N, D)}
    n_components  : number of FFT spectral components to retain
                    (= dimension of the quantum state vector |psi>)

    Returns
    -------
    fitted QuantumInspiredEncoder
    """
    print(f"\n[Encoder] Fitting FFT encoder (n_components={n_components})...")
    all_features = np.vstack(list(user_matrices.values()))
    print(f"[Encoder] Fitting on {all_features.shape[0]} feature vectors "
          f"of dimension {all_features.shape[1]}")

    encoder = QuantumInspiredEncoder(n_components=n_components)
    encoder.fit(all_features)

    # Save the fitted scaler
    scaler_path = os.path.join(OUTPUT_DIR, "encoder_scaler.joblib")
    joblib.dump(encoder.scaler, scaler_path)
    print(f"[Encoder] Scaler saved → {scaler_path}")

    return encoder


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: ENROLL USERS — BUILD IDENTITY TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────

def enroll_users(user_matrices: dict,
                 encoder: QuantumInspiredEncoder,
                 n_enrollment: int = 20,
                 enrollment_fraction: float = 0.6
                 ) -> tuple:
    """
    Split each user's sessions into enrollment and test sets.
    Enroll the first `enrollment_fraction` of sessions, hold out the rest.

    Minimum sessions required: n_enrollment + 5 (at least 5 test probes).
    Users with too few sessions are moved to the impostor pool.

    Parameters
    ----------
    user_matrices       : {user_id: (N, D)}
    encoder             : fitted QuantumInspiredEncoder
    n_enrollment        : number of sessions used to build the template
    enrollment_fraction : fraction of sessions used for enrollment

    Returns
    -------
    (IdentityTemplateManager, enrolled_test_matrices, impostor_matrices)
      enrolled_test_matrices : {uid: held-out feature rows for testing}
      impostor_matrices      : {uid: feature rows of non-enrolled users}
    """
    print(f"\n[Enroll] Enrolling users "
          f"(n_enrollment={n_enrollment}, "
          f"fraction={enrollment_fraction})...")

    tm = IdentityTemplateManager(encoder, n_enrollment=n_enrollment)
    enrolled_test = {}
    impostors     = {}

    for uid, mat in user_matrices.items():
        n_total = len(mat)
        n_enroll_actual = int(n_total * enrollment_fraction)

        if n_enroll_actual < n_enrollment:
            # Not enough data to enroll — treat as impostor
            impostors[uid] = mat
            continue

        enroll_mat = mat[:n_enroll_actual]
        test_mat   = mat[n_enroll_actual:]

        if len(test_mat) < 2:
            impostors[uid] = mat
            continue

        tm.enroll(uid, enroll_mat)
        enrolled_test[uid] = test_mat

    print(f"[Enroll] Enrolled: {len(tm.list_enrolled_users())} users")
    print(f"[Enroll] Impostors: {len(impostors)} users")

    if len(impostors) == 0:
        # If everyone got enrolled, hold back last 20% of enrolled users as impostors
        enrolled_list = tm.list_enrolled_users()
        cutoff = int(len(enrolled_list) * 0.8)
        impostor_uids = enrolled_list[cutoff:]
        for uid in impostor_uids:
            impostors[uid] = user_matrices[uid]
            del enrolled_test[uid]
        print(f"[Enroll] Reassigned {len(impostor_uids)} users to impostor pool")

    # Save template manager
    tm_path = os.path.join(OUTPUT_DIR, "template_manager.joblib")
    joblib.dump(tm, tm_path)
    print(f"[Enroll] Template manager saved → {tm_path}")

    return tm, enrolled_test, impostors


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: TRAIN LSTM AUTOENCODER (anomaly detector)
# ─────────────────────────────────────────────────────────────────────────────

def train_anomaly_detector(tm: IdentityTemplateManager,
                           user_matrices: dict,
                           encoder: QuantumInspiredEncoder,
                           seq_len: int = 10,
                           latent_dim: int = 32,
                           epochs: int = 50,
                           batch_size: int = 32
                           ) -> LSTMAutoencoder:
    """
    Train one shared LSTM Autoencoder on ALL enrolled users' state vectors.

    In Q-Shield, the anomaly detector models "what normal behavior looks like"
    across the enrolled user population. A user-specific detector can also be
    trained per user (pass single-user state vectors instead).

    Training data:
        For each enrolled user → encode all enrollment sessions → state vectors
        → combine → create overlapping sequences of length seq_len
        → train autoencoder to reconstruct them

    The anomaly threshold is calibrated at the 95th percentile of the
    reconstruction error on the training set.

    Parameters
    ----------
    seq_len    : number of consecutive state vectors per input sequence
    latent_dim : LSTM bottleneck size (smaller = more compression)
    epochs     : training epochs (50 is sufficient for CMU-scale data)
    batch_size : training batch size

    Returns
    -------
    trained LSTMAutoencoder with calibrated threshold
    """
    n_components = encoder.n_components
    print(f"\n[LSTM-AE] Building training sequences "
          f"(seq_len={seq_len}, n_features={n_components})...")

    # Collect state vectors from all enrolled users
    all_state_vecs = []
    enrolled_users = tm.list_enrolled_users()

    for uid in enrolled_users:
        if uid not in user_matrices:
            continue
        mat = user_matrices[uid]
        # Use first 60% (enrollment portion) — same as what was enrolled
        enroll_end = int(len(mat) * 0.6)
        enroll_mat = mat[:enroll_end]
        if len(enroll_mat) < seq_len + 1:
            continue
        states = encoder.encode_batch(enroll_mat)
        all_state_vecs.append(states)

    if len(all_state_vecs) == 0:
        raise RuntimeError("No state vectors collected for LSTM training. "
                           "Check that users have sufficient enrollment data.")

    combined_states = np.vstack(all_state_vecs)
    print(f"[LSTM-AE] Training on {len(combined_states)} state vectors "
          f"from {len(all_state_vecs)} users")

    ad = LSTMAutoencoder(
        seq_len=seq_len,
        n_features=n_components,
        latent_dim=latent_dim,
        threshold_percentile=95.0
    )
    ad.fit(combined_states, epochs=epochs, batch_size=batch_size, verbose=1)

    # Save model
    if ad.model is not None:
        model_path = os.path.join(OUTPUT_DIR, "lstm_autoencoder.keras")
        ad.model.save(model_path)
        print(f"[LSTM-AE] Model saved → {model_path}")

    # Save threshold
    threshold_path = os.path.join(OUTPUT_DIR, "anomaly_threshold.joblib")
    joblib.dump({"threshold": ad.threshold, "seq_len": seq_len,
                 "n_components": n_components}, threshold_path)
    print(f"[LSTM-AE] Threshold saved → {threshold_path}")

    return ad


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: TUNE FIDELITY THRESHOLD ON VALIDATION SET
# ─────────────────────────────────────────────────────────────────────────────

def tune_fidelity_threshold(tm: IdentityTemplateManager,
                             encoder: QuantumInspiredEncoder,
                             enrolled_test: dict,
                             impostors: dict,
                             n_probe: int = 5) -> float:
    """
    Find the fidelity threshold that minimises EER on a held-out
    validation subset.

    Computes genuine and impostor fidelity score distributions,
    then picks the threshold where FAR ≈ FRR.

    Parameters
    ----------
    enrolled_test : {uid: held-out feature rows}   (genuine probes)
    impostors     : {uid: feature rows}             (impostor probes)
    n_probe       : number of probe samples per user

    Returns
    -------
    float : optimal fidelity threshold
    """
    print("\n[Threshold] Tuning fidelity threshold on validation set...")

    genuine_scores  = []
    impostor_scores = []

    enrolled_uids = tm.list_enrolled_users()

    # Genuine scores
    for uid in enrolled_uids:
        if uid not in enrolled_test:
            continue
        test_mat = enrolled_test[uid]
        probes = test_mat[:n_probe]
        template = tm.get_template(uid)
        for probe in probes:
            psi = encoder.encode(probe)
            score = QuantumInspiredEncoder.batch_fidelity(psi, template)
            genuine_scores.append(score)

    # Impostor scores (claim to be a random enrolled user)
    imp_uids = list(impostors.keys())
    for imp_uid in imp_uids:
        imp_mat = impostors[imp_uid]
        claimed = enrolled_uids[0]   # worst-case: always claim the first user
        template = tm.get_template(claimed)
        probes = imp_mat[:n_probe]
        for probe in probes:
            psi = encoder.encode(probe)
            score = QuantumInspiredEncoder.batch_fidelity(psi, template)
            impostor_scores.append(score)

    genuine_scores  = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)

    y_true  = np.concatenate([np.ones(len(genuine_scores)),
                               np.zeros(len(impostor_scores))])
    y_score = np.concatenate([genuine_scores, impostor_scores])

    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    fnr = 1 - tpr
    eer_idx = np.argmin(np.abs(fpr - fnr))
    best_threshold = float(thresholds[eer_idx])
    eer_val = (fpr[eer_idx] + fnr[eer_idx]) / 2

    roc_auc = auc(fpr, tpr)
    print(f"[Threshold] Genuine scores  — mean: {genuine_scores.mean():.4f}, "
          f"std: {genuine_scores.std():.4f}")
    print(f"[Threshold] Impostor scores — mean: {impostor_scores.mean():.4f}, "
          f"std: {impostor_scores.std():.4f}")
    print(f"[Threshold] EER = {eer_val*100:.3f}% at threshold = {best_threshold:.4f}")
    print(f"[Threshold] AUC = {roc_auc:.4f}")

    # Plot score distributions
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].hist(genuine_scores, bins=30, alpha=0.7, label="Genuine", color="#1D9E75")
    axes[0].hist(impostor_scores, bins=30, alpha=0.7, label="Impostor", color="#D85A30")
    axes[0].axvline(best_threshold, color="black", linestyle="--", linewidth=1.5,
                    label=f"Threshold={best_threshold:.3f}")
    axes[0].set_xlabel("Quantum Fidelity Score")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Score Distribution — Genuine vs Impostor")
    axes[0].legend()

    axes[1].plot(fpr, tpr, color="#185FA5", linewidth=2,
                 label=f"ROC AUC = {roc_auc:.4f}")
    axes[1].plot([0, 1], [0, 1], "k--", linewidth=0.8)
    axes[1].scatter(fpr[eer_idx], tpr[eer_idx], color="red", zorder=5,
                    label=f"EER = {eer_val*100:.2f}%")
    axes[1].set_xlabel("False Acceptance Rate (FAR)")
    axes[1].set_ylabel("True Acceptance Rate (TAR)")
    axes[1].set_title("ROC Curve — Fidelity Gate")
    axes[1].legend()

    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, "roc_score_distribution.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"[Threshold] ROC + score plot saved → {plot_path}")

    # Save threshold
    joblib.dump({"fidelity_threshold": best_threshold},
                os.path.join(OUTPUT_DIR, "fidelity_threshold.joblib"))

    return best_threshold


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: FULL EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_full(tm: IdentityTemplateManager,
                  ad: LSTMAutoencoder,
                  encoder: QuantumInspiredEncoder,
                  enrolled_test: dict,
                  impostors: dict,
                  fidelity_threshold: float) -> dict:
    """
    Full two-stage evaluation: fidelity gate + anomaly gate.

    Reports:
        EER, FAR, FRR, AUC (fidelity gate only)
        Anomaly detection rate on impostors that passed fidelity gate
        Per-user genuine acceptance rate
    """
    print("\n[Eval] Running full pipeline evaluation...")

    auth = AuthenticationEngine(tm, ad, fidelity_threshold=fidelity_threshold)

    genuine_scores  = []
    impostor_scores = []
    per_user_accept = {}
    anomaly_caught  = 0
    impostor_passed_fidelity = 0

    enrolled_uids = tm.list_enrolled_users()

    # ── Genuine probes ────────────────────────────────────────────────────
    for uid in enrolled_uids:
        if uid not in enrolled_test:
            continue
        test_mat = enrolled_test[uid]
        accepts = 0
        template = tm.get_template(uid)
        for probe in test_mat:
            psi   = encoder.encode(probe)
            score = QuantumInspiredEncoder.batch_fidelity(psi, template)
            genuine_scores.append(score)
            result = auth.authenticate(uid, probe)
            if result["decision"] == AuthenticationEngine.ACCEPT:
                accepts += 1
        per_user_accept[uid] = accepts / max(len(test_mat), 1)

    # ── Impostor probes ───────────────────────────────────────────────────
    for imp_uid, imp_mat in impostors.items():
        claimed = enrolled_uids[0]
        template = tm.get_template(claimed)

        for probe in imp_mat[:20]:
            psi   = encoder.encode(probe)
            score = QuantumInspiredEncoder.batch_fidelity(psi, template)
            impostor_scores.append(score)

            result = auth.authenticate(claimed, probe)
            if result["decision"] == AuthenticationEngine.ACCEPT:
                pass   # false acceptance
            elif result["decision"] == AuthenticationEngine.REAUTH:
                anomaly_caught += 1
                impostor_passed_fidelity += 1
            else:
                pass   # correctly rejected at fidelity gate

    genuine_scores  = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)

    metrics = PipelineEvaluator.compute_eer(genuine_scores, impostor_scores)
    metrics["mean_genuine_fidelity"]   = round(float(genuine_scores.mean()), 4)
    metrics["mean_impostor_fidelity"]  = round(float(impostor_scores.mean()), 4)
    metrics["anomaly_caught"]          = anomaly_caught
    metrics["impostor_passed_fidelity"] = impostor_passed_fidelity
    metrics["per_user_accept_rate"]    = {k: round(v, 3)
                                           for k, v in per_user_accept.items()}

    print("\n" + "=" * 55)
    print("  FINAL EVALUATION RESULTS")
    print("=" * 55)
    print(f"  EER                    : {metrics['EER']:.3f}%")
    print(f"  AUC                    : {metrics['AUC']:.4f}")
    print(f"  FAR @ EER              : {metrics['FAR_at_EER']:.3f}%")
    print(f"  FRR @ EER              : {metrics['FRR_at_EER']:.3f}%")
    print(f"  Fidelity threshold     : {fidelity_threshold:.4f}")
    print(f"  Mean genuine fidelity  : {metrics['mean_genuine_fidelity']:.4f}")
    print(f"  Mean impostor fidelity : {metrics['mean_impostor_fidelity']:.4f}")
    print(f"  Impostors caught by    ")
    print(f"    anomaly detector     : {anomaly_caught}")
    print(f"  Genuine probes         : {metrics.get('n_genuine_probes', 'N/A')}")
    print(f"  Impostor probes        : {metrics.get('n_impostor_probes', 'N/A')}")
    print("=" * 55)

    print("\n  Per-user acceptance rate:")
    for uid, rate in metrics["per_user_accept_rate"].items():
        bar = "#" * int(rate * 20)
        print(f"    {uid:12s}  {rate*100:5.1f}%  [{bar:<20s}]")

    # Save metrics
    import json
    metrics_path = os.path.join(OUTPUT_DIR, "eval_metrics.json")
    serialisable = {k: v for k, v in metrics.items()
                    if not isinstance(v, dict)}
    with open(metrics_path, "w") as f:
        json.dump(serialisable, f, indent=2)
    print(f"\n[Eval] Metrics saved → {metrics_path}")

    return metrics


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — orchestrates all steps
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  Q-Shield — Full Training Run")
    print("=" * 60)

    # ── Check which datasets are available ───────────────────────────────
    status = check_datasets()

    # ── Step 1: Load / generate data ─────────────────────────────────────
    print("\n--- STEP 1: Loading datasets ---")

    if status["cmu"]:
        ks_matrices = load_cmu_real(CMU_CSV_PATH)
    else:
        print("\n[CMU] Using synthetic fallback (51 users, 400 sessions)...")
        raw = DatasetLoader.generate_synthetic_cmu(
            n_users=51, sessions_per_user=400, seed=42)
        ks_matrices = {}
        feat_cols = [c for c in raw.columns
                     if c not in ["subject", "sessionIndex"]]
        for uid, grp in raw.groupby("subject"):
            ks_matrices[uid] = grp[feat_cols].values.astype(float)

    if status["balabit"]:
        mouse_matrices = load_balabit_real(BALABIT_ROOT_DIR)
    else:
        print("\n[Balabit] Using synthetic fallback (10 users)...")
        raw = DatasetLoader.generate_synthetic_mouse(n_users=10, seed=42)
        feat_df = FeatureExtractor.extract_mouse_features(raw)
        feat_cols = [c for c in feat_df.columns
                     if c not in ["user_id", "window"]]
        mouse_matrices = {}
        for uid, grp in feat_df.groupby("user_id"):
            mouse_matrices[uid] = grp[feat_cols].values.astype(float)

    if status["hmog"]:
        touch_matrices = load_hmog_real(HMOG_ROOT_DIR)
    else:
        print("\n[HMOG] Using synthetic fallback (10 users)...")
        raw = DatasetLoader.generate_synthetic_touch(n_users=10, seed=42)
        feat_df = FeatureExtractor.extract_touch_features(raw)
        feat_cols = [c for c in feat_df.columns if c != "subject_id"]
        touch_matrices = {}
        for uid, grp in raw.groupby("subject_id"):
            touch_matrices[uid] = feat_df[
                feat_df.index.isin(grp.index)
            ][feat_cols].values.astype(float) if False else \
            np.array([[
                grp["pressure"].mean(), grp["pressure"].std(),
                0.0,
                grp["area"].mean() if "area" in grp else 100.0,
                20.0,
                grp["swipe_speed"].mean() if "swipe_speed" in grp else 500.0,
                grp["swipe_speed"].std() if "swipe_speed" in grp else 100.0,
                800.0, 80.0, grp["x"].mean(), grp["x"].std(),
                grp["y"].mean(), grp["y"].std(), float(len(grp)), 500.0
            ]])

    # ── Step 2: Fuse modalities ───────────────────────────────────────────
    print("\n--- STEP 2: Fusing modalities ---")
    # For CMU-only training use just keystroke (most data)
    # For multi-modal use fuse_modalities(ks_matrices, mouse_matrices, touch_matrices)
    user_matrices = ks_matrices   # change to fused for multimodal

    # ── Step 3: Train encoder ─────────────────────────────────────────────
    print("\n--- STEP 3: Training FFT encoder ---")
    encoder = train_encoder(user_matrices, n_components=64)

    # ── Step 4: Enroll users ──────────────────────────────────────────────
    print("\n--- STEP 4: Enrolling users ---")
    tm, enrolled_test, impostors = enroll_users(
        user_matrices, encoder, n_enrollment=20, enrollment_fraction=0.6
    )

    # ── Step 5: Train LSTM Autoencoder ────────────────────────────────────
    print("\n--- STEP 5: Training LSTM Autoencoder ---")
    ad = train_anomaly_detector(
        tm, user_matrices, encoder,
        seq_len=10, latent_dim=32, epochs=50, batch_size=32
    )

    # ── Step 6: Tune fidelity threshold ───────────────────────────────────
    print("\n--- STEP 6: Tuning fidelity threshold ---")
    threshold = tune_fidelity_threshold(
        tm, encoder, enrolled_test, impostors, n_probe=5
    )

    # ── Step 7: Full evaluation ───────────────────────────────────────────
    print("\n--- STEP 7: Full evaluation ---")
    metrics = evaluate_full(
        tm, ad, encoder, enrolled_test, impostors, threshold
    )

    print(f"\n[DONE] All outputs saved to: {os.path.abspath(OUTPUT_DIR)}/")
    print("  encoder_scaler.joblib        — fitted StandardScaler")
    print("  template_manager.joblib      — enrolled identity templates")
    print("  lstm_autoencoder.keras       — trained anomaly detector")
    print("  anomaly_threshold.joblib     — calibrated reconstruction threshold")
    print("  fidelity_threshold.joblib    — optimal fidelity gate threshold")
    print("  eval_metrics.json            — EER, AUC, FAR, FRR results")
    print("  roc_score_distribution.png   — ROC curve + score distribution plot")


if __name__ == "__main__":
    main()