"""
Q-Shield: Quantum-Inspired Secure Authentication — ML Pipeline
================================================================
Full pipeline covering:
  Stage 1  — Dataset loading  (CMU Keystroke, Balabit Mouse, HMOG Touch)
  Stage 2  — Preprocessing & feature extraction
  Stage 3  — FFT-based spectral encoding → quantum-inspired state vector
  Stage 4  — Quantum fidelity matching
  Stage 5  — ML anomaly detection (LSTM Autoencoder)
  Stage 6  — Authentication decision engine
  Stage 7  — Evaluation (EER, FAR, FRR, AUC)

Dependencies:
    pip install numpy pandas scipy scikit-learn tensorflow matplotlib seaborn
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
from scipy.fft import fft, fftfreq
from scipy.spatial.distance import cosine
from scipy.interpolate import interp1d
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, confusion_matrix
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: DATASET LOADING
# ─────────────────────────────────────────────────────────────────────────────

class DatasetLoader:
    """
    Loaders for the three primary Q-Shield datasets.

    Datasets:
    ---------
    1. CMU Keystroke Dynamics Benchmark
       - 51 users, 400 sessions each, fixed password ".tie5Roanl"
       - Features: hold_time (H), keydown-keydown (DD), keyup-keydown (UD)
       - Download: https://www.cs.cmu.edu/~keystroke/
       - File:     DSL-StrongPasswordData.csv

    2. Balabit Mouse Dynamics Challenge
       - 10 users, timing & positional mouse pointer data
       - Features: timestamp, x, y, button, state
       - Download: https://github.com/balabit/Mouse-Dynamics-Challenge

    3. HMOG (Hand Movement, Orientation and Grasp)
       - 100 users, 3 tasks (reading, writing, navigation)
       - 14 sensor channels including touch, accelerometer, gyroscope
       - Download: https://github.com/hmog-dataset/hmog
    """

    @staticmethod
    def load_cmu_keystroke(filepath: str) -> pd.DataFrame:
        """
        Load CMU Keystroke Dynamics Benchmark dataset.

        Expected columns (after loading DSL-StrongPasswordData.csv):
        subject, sessionIndex, rep, H.period, DD.period.t, UD.period.t,
        H.t, DD.t.i, UD.t.i, H.i, DD.i.e, UD.i.e, H.e, DD.e.five,
        UD.e.five, H.five, DD.five.Shift.r, UD.five.Shift.r,
        H.Shift.r, DD.Shift.r.o, UD.Shift.r.o, H.o, DD.o.a, UD.o.a,
        H.a, DD.a.n, UD.a.n, H.n, DD.n.l, UD.n.l, H.l

        Returns: DataFrame with subject labels and timing features.
        """
        df = pd.read_csv(filepath)
        print(f"[CMU] Loaded {len(df)} rows, {df['subject'].nunique()} subjects")
        return df

    @staticmethod
    def load_balabit_mouse(train_dir: str, test_dir: str) -> pd.DataFrame:
        """
        Load Balabit Mouse Dynamics dataset.

        Folder structure:
            train/user_<id>/session_<n>.csv
        Each CSV columns: record_timestamp, client_timestamp, button,
                          state, x, y

        Returns: Combined DataFrame with user_id column.
        """
        import os
        frames = []
        for split, directory in [("train", train_dir), ("test", test_dir)]:
            for user_folder in os.listdir(directory):
                user_id = user_folder  # e.g. "user_7"
                user_path = os.path.join(directory, user_folder)
                if not os.path.isdir(user_path):
                    continue
                for session_file in os.listdir(user_path):
                    if not session_file.endswith(".csv"):
                        continue
                    session_path = os.path.join(user_path, session_file)
                    df = pd.read_csv(session_path)
                    df["user_id"] = user_id
                    df["split"] = split
                    frames.append(df)
        combined = pd.concat(frames, ignore_index=True)
        print(f"[Balabit] Loaded {len(combined)} rows, "
              f"{combined['user_id'].nunique()} users")
        return combined

    @staticmethod
    def load_hmog_touch(base_dir: str) -> pd.DataFrame:
        """
        Load HMOG touch dataset.

        Folder structure:
            <base_dir>/<subject_id>/session_<n>/touch.csv
        touch.csv columns: sys_time, event_type, x, y, pressure, area,
                           phone_orientation

        Returns: Combined DataFrame with subject_id column.
        """
        import os
        frames = []
        for subject in os.listdir(base_dir):
            subject_path = os.path.join(base_dir, subject)
            if not os.path.isdir(subject_path):
                continue
            for session in os.listdir(subject_path):
                touch_path = os.path.join(subject_path, session, "touch.csv")
                if not os.path.exists(touch_path):
                    continue
                df = pd.read_csv(touch_path)
                df["subject_id"] = subject
                df["session"] = session
                frames.append(df)
        combined = pd.concat(frames, ignore_index=True)
        print(f"[HMOG] Loaded {len(combined)} rows, "
              f"{combined['subject_id'].nunique()} subjects")
        return combined

    # ── SYNTHETIC DATA GENERATOR (for pipeline testing without downloads) ──

    @staticmethod
    def generate_synthetic_cmu(n_users: int = 10,
                                sessions_per_user: int = 40,
                                n_features: int = 31,
                                seed: int = 42) -> pd.DataFrame:
        """
        Generate synthetic keystroke data that mirrors CMU structure.
        Each user has a unique mean timing profile with Gaussian noise.
        """
        rng = np.random.default_rng(seed)
        records = []
        feature_names = (
            ["H_period", "DD_period_t", "UD_period_t",
             "H_t", "DD_t_i", "UD_t_i",
             "H_i", "DD_i_e", "UD_i_e",
             "H_e", "DD_e_five", "UD_e_five",
             "H_five", "DD_five_shift", "UD_five_shift",
             "H_shift", "DD_shift_o", "UD_shift_o",
             "H_o", "DD_o_a", "UD_o_a",
             "H_a", "DD_a_n", "UD_a_n",
             "H_n", "DD_n_l", "UD_n_l", "H_l",
             "H_Return", "DD_Return", "UD_Return"]
        )
        for user_id in range(n_users):
            # Each user has a unique mean timing profile (in ms)
            user_mean = rng.uniform(60, 180, n_features)
            user_std  = rng.uniform(5, 25, n_features)
            for session in range(sessions_per_user):
                row = {"subject": f"s{user_id:03d}", "sessionIndex": session + 1}
                timing = rng.normal(user_mean, user_std)
                timing = np.clip(timing, 1, 500)  # realistic ms range
                for i, fname in enumerate(feature_names):
                    row[fname] = timing[i]
                records.append(row)
        df = pd.DataFrame(records)
        print(f"[Synthetic CMU] {len(df)} rows, {df['subject'].nunique()} users")
        return df

    @staticmethod
    def generate_synthetic_mouse(n_users: int = 10,
                                  events_per_user: int = 5000,
                                  seed: int = 42) -> pd.DataFrame:
        """Generate synthetic mouse dynamics mirroring Balabit structure."""
        rng = np.random.default_rng(seed)
        records = []
        for user_id in range(n_users):
            # Each user has characteristic speed and movement range
            speed_bias = rng.uniform(0.5, 2.0)
            range_bias = rng.uniform(0.3, 1.5)
            t = 0
            x, y = 500.0, 400.0
            for _ in range(events_per_user):
                dt = rng.exponential(0.05) * speed_bias
                t += dt
                dx = rng.normal(0, 20 * range_bias)
                dy = rng.normal(0, 15 * range_bias)
                x  = np.clip(x + dx, 0, 1920)
                y  = np.clip(y + dy, 0, 1080)
                records.append({
                    "user_id": f"user_{user_id}",
                    "record_timestamp": t,
                    "x": x, "y": y,
                    "button": rng.choice(["NoButton", "left", "right"],
                                         p=[0.85, 0.12, 0.03]),
                    "state": rng.choice(["Move", "Pressed", "Released"],
                                         p=[0.80, 0.10, 0.10])
                })
        df = pd.DataFrame(records)
        print(f"[Synthetic Balabit] {len(df)} rows, "
              f"{df['user_id'].nunique()} users")
        return df

    @staticmethod
    def generate_synthetic_touch(n_users: int = 10,
                                  taps_per_user: int = 2000,
                                  seed: int = 42) -> pd.DataFrame:
        """Generate synthetic touch dynamics mirroring HMOG structure."""
        rng = np.random.default_rng(seed)
        records = []
        for user_id in range(n_users):
            pressure_mean = rng.uniform(0.3, 0.8)
            area_mean     = rng.uniform(50, 150)
            speed_mean    = rng.uniform(300, 900)
            for _ in range(taps_per_user):
                records.append({
                    "subject_id": f"user_{user_id}",
                    "x": rng.uniform(0, 1080),
                    "y": rng.uniform(0, 1920),
                    "pressure": np.clip(rng.normal(pressure_mean, 0.1), 0, 1),
                    "area": np.clip(rng.normal(area_mean, 20), 10, 300),
                    "swipe_speed": np.clip(
                        rng.normal(speed_mean, 150), 50, 2000),
                    "duration_ms": rng.exponential(80)
                })
        df = pd.DataFrame(records)
        print(f"[Synthetic HMOG] {len(df)} rows, "
              f"{df['subject_id'].nunique()} users")
        return df


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

class FeatureExtractor:
    """
    Extracts statistical, temporal, pattern, and movement features
    from each raw behavioral modality.
    """

    # ── 2A. KEYSTROKE FEATURES ────────────────────────────────────────────

    @staticmethod
    def extract_keystroke_features(df: pd.DataFrame,
                                    subject_col: str = "subject") -> pd.DataFrame:
        """
        Per-subject aggregation of CMU-style timing features.

        Extracted features per subject:
          - mean, std, min, max, median of each timing column
          - inter-key interval statistics (flight time variance)
          - coefficient of variation (CV) per timing dimension
        """
        timing_cols = [c for c in df.columns
                       if c not in [subject_col, "sessionIndex"]]

        records = []
        for subject, grp in df.groupby(subject_col):
            row = {"subject": subject}
            for col in timing_cols:
                vals = grp[col].dropna().values
                row[f"{col}_mean"]   = np.mean(vals)
                row[f"{col}_std"]    = np.std(vals)
                row[f"{col}_min"]    = np.min(vals)
                row[f"{col}_max"]    = np.max(vals)
                row[f"{col}_median"] = np.median(vals)
                row[f"{col}_cv"]     = (np.std(vals) / (np.mean(vals) + 1e-9))
            records.append(row)

        feat_df = pd.DataFrame(records)
        print(f"[KS Features] {feat_df.shape[1]-1} features, "
              f"{len(feat_df)} subjects")
        return feat_df

    # ── 2B. MOUSE DYNAMICS FEATURES ───────────────────────────────────────

    @staticmethod
    def extract_mouse_features(df: pd.DataFrame,
                                user_col: str = "user_id",
                                window_size: int = 100) -> pd.DataFrame:
        """
        Segment mouse data into windows and extract per-window features.

        Features per window:
          - mean/std velocity, acceleration
          - mean/std angle (direction of movement)
          - click rate (clicks per second)
          - straightness ratio (displacement / path length)
          - mean/std movement distance per event
        """
        records = []
        for user, grp in df.groupby(user_col):
            grp = grp.sort_values("record_timestamp").reset_index(drop=True)
            x   = grp["x"].values.astype(float)
            y   = grp["y"].values.astype(float)
            t   = grp["record_timestamp"].values.astype(float)

            n_windows = len(grp) // window_size
            for w in range(n_windows):
                s = w * window_size
                e = s + window_size
                xw, yw, tw = x[s:e], y[s:e], t[s:e]

                dx = np.diff(xw)
                dy = np.diff(yw)
                dt = np.diff(tw) + 1e-9

                dist     = np.sqrt(dx**2 + dy**2)
                velocity = dist / dt
                accel    = np.diff(velocity) / (dt[:-1] + 1e-9)
                angles   = np.arctan2(dy, dx)

                total_path  = np.sum(dist)
                displacement = np.sqrt((xw[-1]-xw[0])**2 + (yw[-1]-yw[0])**2)
                straightness = displacement / (total_path + 1e-9)

                btn_col = grp.get("button", pd.Series(["NoButton"]*len(grp)))
                clicks_in_window = (
                    btn_col.iloc[s:e] != "NoButton"
                ).sum()
                duration = tw[-1] - tw[0] + 1e-9
                click_rate = clicks_in_window / duration

                records.append({
                    "user_id":       user,
                    "window":        w,
                    "vel_mean":      np.mean(velocity),
                    "vel_std":       np.std(velocity),
                    "accel_mean":    np.mean(accel) if len(accel) > 0 else 0,
                    "accel_std":     np.std(accel)  if len(accel) > 0 else 0,
                    "angle_mean":    np.mean(angles),
                    "angle_std":     np.std(angles),
                    "dist_mean":     np.mean(dist),
                    "dist_std":      np.std(dist),
                    "straightness":  straightness,
                    "click_rate":    click_rate,
                    "path_length":   total_path
                })

        feat_df = pd.DataFrame(records)
        print(f"[Mouse Features] {feat_df.shape[1]-2} features, "
              f"{feat_df['user_id'].nunique()} users, "
              f"{len(feat_df)} windows")
        return feat_df

    # ── 2C. TOUCH DYNAMICS FEATURES ───────────────────────────────────────

    @staticmethod
    def extract_touch_features(df: pd.DataFrame,
                                subject_col: str = "subject_id") -> pd.DataFrame:
        """
        Per-subject aggregation of touch interaction features.

        Features:
          - pressure: mean, std, skewness
          - contact area: mean, std
          - swipe speed: mean, std, percentile 90
          - tap duration: mean, std
          - touch frequency (taps per unit time)
          - trajectory features: mean x/y, spread x/y
        """
        from scipy.stats import skew
        records = []
        for subject, grp in df.groupby(subject_col):
            p   = grp["pressure"].dropna().values
            a   = grp["area"].dropna().values     if "area"        in grp else np.array([0])
            spd = grp["swipe_speed"].dropna().values if "swipe_speed" in grp else np.array([0])
            dur = grp["duration_ms"].dropna().values if "duration_ms" in grp else np.array([0])
            x   = grp["x"].dropna().values
            y   = grp["y"].dropna().values

            records.append({
                "subject_id":     subject,
                "pressure_mean":  np.mean(p),
                "pressure_std":   np.std(p),
                "pressure_skew":  skew(p) if len(p) > 2 else 0,
                "area_mean":      np.mean(a),
                "area_std":       np.std(a),
                "speed_mean":     np.mean(spd),
                "speed_std":      np.std(spd),
                "speed_p90":      np.percentile(spd, 90),
                "duration_mean":  np.mean(dur),
                "duration_std":   np.std(dur),
                "tap_count":      len(p),
                "x_mean":         np.mean(x),
                "x_std":          np.std(x),
                "y_mean":         np.mean(y),
                "y_std":          np.std(y),
            })

        feat_df = pd.DataFrame(records)
        print(f"[Touch Features] {feat_df.shape[1]-1} features, "
              f"{len(feat_df)} subjects")
        return feat_df


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 3: FFT SPECTRAL ENCODING → QUANTUM-INSPIRED STATE VECTOR
# ─────────────────────────────────────────────────────────────────────────────

class QuantumInspiredEncoder:
    """
    Encodes a behavioral feature vector into a normalized spectral
    amplitude vector interpreted as a quantum-inspired identity state.

    Pipeline:
        raw feature vector  →  FFT  →  magnitude spectrum
        →  top-K amplitudes  →  L2 normalization  →  |ψ⟩

    The resulting vector |ψ⟩ satisfies ⟨ψ|ψ⟩ = 1, mimicking the
    normalization condition of quantum state vectors.

    Authentication uses quantum fidelity:
        F(ψ₁, ψ₂) = |⟨ψ₁|ψ₂⟩|²
    where F = 1 means identical identity, F ≈ 0 means different user.
    """

    def __init__(self, n_components: int = 64):
        """
        Parameters
        ----------
        n_components : int
            Number of dominant frequency components to retain
            (dimensionality of the identity state vector).
        """
        self.n_components = n_components
        self.scaler = StandardScaler()
        self._fitted = False

    def fit(self, X: np.ndarray):
        """Fit the scaler on enrollment data."""
        self.scaler.fit(X)
        self._fitted = True
        return self

    def encode(self, feature_vector: np.ndarray) -> np.ndarray:
        """
        Encode a single feature vector into a normalized state vector |ψ⟩.

        Steps
        -----
        1. Standardize: zero-mean, unit-variance across dimensions
        2. FFT: compute complex spectrum
        3. Magnitude spectrum: |FFT(x)|
        4. Select top-K components by amplitude
        5. L2 normalize to satisfy ⟨ψ|ψ⟩ = 1

        Parameters
        ----------
        feature_vector : np.ndarray of shape (D,)
            D-dimensional feature vector for one user/session.

        Returns
        -------
        psi : np.ndarray of shape (n_components,)
            Normalized quantum-inspired amplitude state vector.
        """
        # 1. Standardize
        if self._fitted:
            x = self.scaler.transform(feature_vector.reshape(1, -1)).flatten()
        else:
            x = (feature_vector - np.mean(feature_vector)) / \
                (np.std(feature_vector) + 1e-9)

        # 2. Pad or truncate to power of 2 for efficient FFT
        n_fft = max(2 ** int(np.ceil(np.log2(len(x)))), self.n_components * 2)
        x_padded = np.zeros(n_fft)
        x_padded[:len(x)] = x

        # 3. FFT → magnitude spectrum
        spectrum = np.abs(fft(x_padded))

        # 4. Select top-K components by amplitude
        top_k_idx = np.argsort(spectrum)[::-1][:self.n_components]
        top_k_idx.sort()  # keep frequency ordering
        amplitudes = spectrum[top_k_idx]

        # 5. L2 normalize → valid quantum state (unit vector)
        norm = np.linalg.norm(amplitudes)
        psi = amplitudes / (norm + 1e-12)

        return psi

    def encode_batch(self, X: np.ndarray) -> np.ndarray:
        """Encode a matrix of feature vectors."""
        return np.array([self.encode(row) for row in X])

    @staticmethod
    def quantum_fidelity(psi1: np.ndarray, psi2: np.ndarray) -> float:
        """
        Compute quantum fidelity between two state vectors.

        F(ψ₁, ψ₂) = |⟨ψ₁|ψ₂⟩|² = (ψ₁ · ψ₂)²

        Both vectors must be L2-normalized (unit vectors).
        Returns F ∈ [0, 1] where 1 = identical, 0 = orthogonal.

        Parameters
        ----------
        psi1, psi2 : np.ndarray
            Normalized quantum state vectors of the same dimension.

        Returns
        -------
        float : Fidelity score in [0, 1]
        """
        inner_product = np.dot(psi1, psi2)
        return float(inner_product ** 2)

    @staticmethod
    def batch_fidelity(psi_probe: np.ndarray,
                        psi_template: np.ndarray) -> float:
        """
        Average fidelity of a probe state against an enrollment template
        (mean of multiple enrollment samples).
        """
        template_mean = np.mean(psi_template, axis=0)
        norm = np.linalg.norm(template_mean)
        template_mean /= (norm + 1e-12)
        return QuantumInspiredEncoder.quantum_fidelity(psi_probe, template_mean)


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 4: ENROLLMENT & TEMPLATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

class IdentityTemplateManager:
    """
    Manages enrollment templates (quantum state vectors) per user.
    In Q-Shield, these templates are encrypted with ML-KEM + ML-DSA
    before storage. This class handles the plaintext ML-layer only.
    """

    def __init__(self, encoder: QuantumInspiredEncoder,
                 n_enrollment: int = 20):
        """
        Parameters
        ----------
        encoder : QuantumInspiredEncoder
        n_enrollment : int
            Number of sessions used to build the enrollment template.
        """
        self.encoder     = encoder
        self.n_enrollment = n_enrollment
        self.templates   = {}   # user_id → np.ndarray (n_enrollment, n_components)

    def enroll(self, user_id: str, feature_matrix: np.ndarray):
        """
        Build enrollment template from multiple feature vectors.

        Parameters
        ----------
        user_id : str
        feature_matrix : np.ndarray of shape (N, D)
            N enrollment sessions, D features each.
        """
        if len(feature_matrix) < self.n_enrollment:
            raise ValueError(
                f"Need at least {self.n_enrollment} enrollment sessions, "
                f"got {len(feature_matrix)}"
            )
        samples = feature_matrix[:self.n_enrollment]
        state_vectors = self.encoder.encode_batch(samples)
        self.templates[user_id] = state_vectors
        print(f"[Enroll] User '{user_id}': template shape {state_vectors.shape}")

    def get_template(self, user_id: str) -> np.ndarray:
        if user_id not in self.templates:
            raise KeyError(f"User '{user_id}' not enrolled.")
        return self.templates[user_id]

    def list_enrolled_users(self):
        return list(self.templates.keys())


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 5: LSTM AUTOENCODER — ANOMALY DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class LSTMAutoencoder:
    """
    LSTM-based Autoencoder for continuous session anomaly detection.

    Architecture
    ------------
    Encoder:  Input(seq_len, n_features) → LSTM(128) → LSTM(64) → latent
    Decoder:  RepeatVector(seq_len) → LSTM(64) → LSTM(128) → Dense(n_features)

    Training: on normal (genuine) behavioral sequences only.
    Inference: reconstruct input; high MSE = anomalous = possible impostor.
    """

    def __init__(self, seq_len: int = 10, n_features: int = 64,
                 latent_dim: int = 32, threshold_percentile: float = 95.0):
        """
        Parameters
        ----------
        seq_len   : number of time steps (windows) per sequence
        n_features: dimension of each time step (= n_components of state vector)
        latent_dim: LSTM bottleneck size
        threshold_percentile: reconstruction error percentile above which
                               an anomaly is flagged (calibrated on train set)
        """
        self.seq_len   = seq_len
        self.n_features = n_features
        self.latent_dim = latent_dim
        self.threshold_percentile = threshold_percentile
        self.threshold = None
        self.model     = None
        self.history   = None
        self._build()

    def _build(self):
        """Build the LSTM Autoencoder using TensorFlow/Keras."""
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Model
            from tensorflow.keras.layers import (
                Input, LSTM, Dense, RepeatVector, TimeDistributed, Dropout
            )

            inputs = Input(shape=(self.seq_len, self.n_features),
                           name="encoder_input")

            # Encoder
            x = LSTM(128, activation="tanh", return_sequences=True,
                     name="encoder_lstm1")(inputs)
            x = Dropout(0.2)(x)
            x = LSTM(self.latent_dim, activation="tanh", return_sequences=False,
                     name="encoder_lstm2")(x)

            # Bottleneck → Decoder bridge
            x = RepeatVector(self.seq_len, name="repeat_vector")(x)

            # Decoder
            x = LSTM(self.latent_dim, activation="tanh", return_sequences=True,
                     name="decoder_lstm1")(x)
            x = Dropout(0.2)(x)
            x = LSTM(128, activation="tanh", return_sequences=True,
                     name="decoder_lstm2")(x)
            outputs = TimeDistributed(Dense(self.n_features),
                                      name="reconstruction")(x)

            self.model = Model(inputs, outputs, name="lstm_autoencoder")
            self.model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                               loss="mse")
            print(f"[LSTM-AE] Built. Params: "
                  f"{self.model.count_params():,}")
        except ImportError:
            print("[LSTM-AE] TensorFlow not installed. "
                  "Using sklearn IsolationForest as fallback.")
            self.model = None

    def prepare_sequences(self, state_vectors: np.ndarray) -> np.ndarray:
        """
        Convert a flat array of state vectors into overlapping sequences.

        Parameters
        ----------
        state_vectors : np.ndarray of shape (N, n_features)

        Returns
        -------
        np.ndarray of shape (N - seq_len + 1, seq_len, n_features)
        """
        sequences = []
        for i in range(len(state_vectors) - self.seq_len + 1):
            sequences.append(state_vectors[i : i + self.seq_len])
        return np.array(sequences)

    def fit(self, state_vectors: np.ndarray,
            epochs: int = 50, batch_size: int = 32, verbose: int = 0):
        """
        Train on genuine user state vector sequences.
        Calibrate the anomaly threshold from training reconstruction error.
        """
        X = self.prepare_sequences(state_vectors)

        if self.model is not None:
            self.history = self.model.fit(
                X, X,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.1,
                shuffle=True,
                verbose=verbose
            )
            # Calibrate threshold
            recon    = self.model.predict(X, verbose=0)
            errors   = np.mean(np.square(X - recon), axis=(1, 2))
            self.threshold = np.percentile(errors, self.threshold_percentile)
            print(f"[LSTM-AE] Trained. Anomaly threshold "
                  f"(p{self.threshold_percentile:.0f}): {self.threshold:.6f}")
        else:
            # Fallback: Isolation Forest on flattened sequences
            X_flat = X.reshape(len(X), -1)
            self.iso_forest = IsolationForest(contamination=0.05,
                                               random_state=42)
            self.iso_forest.fit(X_flat)
            print("[LSTM-AE Fallback] IsolationForest fitted.")

    def reconstruction_error(self, sequence: np.ndarray) -> float:
        """
        Compute MSE reconstruction error for a single sequence.

        Parameters
        ----------
        sequence : np.ndarray of shape (seq_len, n_features)

        Returns
        -------
        float : mean squared reconstruction error
        """
        if self.model is not None:
            seq_input = sequence.reshape(1, self.seq_len, self.n_features)
            recon = self.model.predict(seq_input, verbose=0)
            return float(np.mean(np.square(seq_input - recon)))
        else:
            seq_flat = sequence.reshape(1, -1)
            score = self.iso_forest.score_samples(seq_flat)[0]
            # Convert to positive anomaly score (higher = more anomalous)
            return float(-score)

    def is_anomalous(self, sequence: np.ndarray) -> tuple:
        """
        Determine if a behavioral sequence is anomalous.

        Returns
        -------
        (bool, float) : (is_anomaly, reconstruction_error)
        """
        error = self.reconstruction_error(sequence)
        if self.threshold is not None:
            return (error > self.threshold, error)
        else:
            # Fallback: IsolationForest prediction
            seq_flat = sequence.reshape(1, -1)
            pred = self.iso_forest.predict(seq_flat)[0]
            return (pred == -1, error)


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 6: AUTHENTICATION DECISION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class AuthenticationEngine:
    """
    Two-stage authentication decision:

    Stage A — Fidelity Gate:
        Compute quantum fidelity F(probe, template).
        If F < fidelity_threshold → REJECT (fast path).

    Stage B — Anomaly Gate:
        If F ≥ fidelity_threshold, check LSTM-AE reconstruction error.
        If anomaly detected → flag for re-authentication.

    Combined decision:
        ACCEPT  : F ≥ threshold AND not anomalous
        REAUTH  : F ≥ threshold BUT anomalous behavior detected
        REJECT  : F < threshold
    """

    ACCEPT = "ACCEPT"
    REAUTH = "RE-AUTHENTICATE"
    REJECT = "REJECT"

    def __init__(self,
                 template_manager: IdentityTemplateManager,
                 anomaly_detector: LSTMAutoencoder,
                 fidelity_threshold: float = 0.75):
        """
        Parameters
        ----------
        fidelity_threshold : float in [0, 1]
            Minimum quantum fidelity score to pass the fidelity gate.
            Tune this on a validation set to balance FAR/FRR.
        """
        self.tm = template_manager
        self.ad = anomaly_detector
        self.fidelity_threshold = fidelity_threshold
        self.encoder = template_manager.encoder

    def authenticate(self, claimed_user_id: str,
                     probe_feature_vector: np.ndarray,
                     recent_sequence: np.ndarray = None) -> dict:
        """
        Run the full two-stage authentication decision.

        Parameters
        ----------
        claimed_user_id : str
        probe_feature_vector : np.ndarray of shape (D,)
            Current behavioral feature vector.
        recent_sequence : np.ndarray of shape (seq_len, n_components), optional
            Recent window of state vectors for anomaly detection.
            If None, anomaly check is skipped.

        Returns
        -------
        dict with keys: decision, fidelity, anomaly_score, reason
        """
        result = {
            "user_id":     claimed_user_id,
            "decision":    None,
            "fidelity":    None,
            "anomaly_score": None,
            "reason":      None
        }

        # ── Stage A: Quantum Fidelity Gate ────────────────────────────────
        try:
            template = self.tm.get_template(claimed_user_id)
        except KeyError:
            result["decision"] = self.REJECT
            result["reason"] = "User not enrolled"
            return result

        probe_state = self.encoder.encode(probe_feature_vector)
        fidelity = QuantumInspiredEncoder.batch_fidelity(
            probe_state, template
        )
        result["fidelity"] = round(fidelity, 4)

        if fidelity < self.fidelity_threshold:
            result["decision"] = self.REJECT
            result["reason"] = (
                f"Fidelity {fidelity:.4f} < threshold "
                f"{self.fidelity_threshold:.4f}"
            )
            return result

        # ── Stage B: LSTM Anomaly Gate ────────────────────────────────────
        if recent_sequence is not None and self.ad.threshold is not None:
            is_anomaly, anomaly_score = self.ad.is_anomalous(recent_sequence)
            result["anomaly_score"] = round(float(anomaly_score), 6)
            if is_anomaly:
                result["decision"] = self.REAUTH
                result["reason"]   = (
                    f"Anomaly detected: reconstruction error "
                    f"{anomaly_score:.6f} > threshold "
                    f"{self.ad.threshold:.6f}"
                )
                return result

        result["decision"] = self.ACCEPT
        result["reason"]   = (
            f"Fidelity {fidelity:.4f} >= {self.fidelity_threshold:.4f}; "
            "no anomaly detected"
        )
        return result


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 7: EVALUATION METRICS
# ─────────────────────────────────────────────────────────────────────────────

class PipelineEvaluator:
    """
    Computes standard biometric authentication metrics:
        EER  — Equal Error Rate
        FAR  — False Acceptance Rate at operating threshold
        FRR  — False Rejection Rate at operating threshold
        AUC  — Area Under the ROC Curve
        TAR  — True Acceptance Rate (= 1 - FRR)
    """

    @staticmethod
    def compute_eer(genuine_scores: np.ndarray,
                    impostor_scores: np.ndarray) -> tuple:
        """
        Compute Equal Error Rate (EER) from score distributions.

        Parameters
        ----------
        genuine_scores  : scores where higher = more genuine (fidelity scores)
        impostor_scores : scores for impostors

        Returns
        -------
        (eer, threshold) : EER value and the threshold at which FAR ≈ FRR
        """
        y_true  = np.concatenate([
            np.ones(len(genuine_scores)),
            np.zeros(len(impostor_scores))
        ])
        y_score = np.concatenate([genuine_scores, impostor_scores])

        fpr, tpr, thresholds = roc_curve(y_true, y_score)
        fnr = 1 - tpr

        # EER = point where FPR ≈ FNR
        eer_idx = np.argmin(np.abs(fpr - fnr))
        eer = (fpr[eer_idx] + fnr[eer_idx]) / 2
        eer_threshold = thresholds[eer_idx]

        roc_auc = auc(fpr, tpr)

        return {
            "EER":       round(float(eer) * 100, 3),      # %
            "EER_thresh": round(float(eer_threshold), 4),
            "AUC":        round(float(roc_auc), 4),
            "FAR_at_EER": round(float(fpr[eer_idx]) * 100, 3),   # %
            "FRR_at_EER": round(float(fnr[eer_idx]) * 100, 3),   # %
        }

    @staticmethod
    def evaluate_pipeline(auth_engine: AuthenticationEngine,
                           genuine_users_data: dict,
                           impostor_data: dict,
                           n_genuine_probes: int = 10,
                           n_impostor_probes: int = 10) -> dict:
        """
        Full pipeline evaluation.

        Parameters
        ----------
        genuine_users_data : {user_id: feature_matrix (N, D)}
        impostor_data      : {user_id: feature_matrix (N, D)}

        Returns
        -------
        dict with per-user and aggregate metrics
        """
        genuine_scores  = []
        impostor_scores = []

        for user_id, feat_matrix in genuine_users_data.items():
            if user_id not in auth_engine.tm.list_enrolled_users():
                continue
            # Probe with held-out genuine samples
            probe_samples = feat_matrix[-n_genuine_probes:]
            for probe in probe_samples:
                state = auth_engine.encoder.encode(probe)
                template = auth_engine.tm.get_template(user_id)
                score = QuantumInspiredEncoder.batch_fidelity(state, template)
                genuine_scores.append(score)

        for impostor_id, feat_matrix in impostor_data.items():
            # Impostors claim to be each enrolled user
            for enrolled_user in auth_engine.tm.list_enrolled_users():
                probe_samples = feat_matrix[:n_impostor_probes]
                for probe in probe_samples:
                    state = auth_engine.encoder.encode(probe)
                    template = auth_engine.tm.get_template(enrolled_user)
                    score = QuantumInspiredEncoder.batch_fidelity(
                        state, template
                    )
                    impostor_scores.append(score)

        metrics = PipelineEvaluator.compute_eer(
            np.array(genuine_scores),
            np.array(impostor_scores)
        )
        metrics["n_genuine_probes"]  = len(genuine_scores)
        metrics["n_impostor_probes"] = len(impostor_scores)
        return metrics


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 8: FULL PIPELINE DEMO
# ─────────────────────────────────────────────────────────────────────────────

def run_demo_pipeline():
    """
    End-to-end Q-Shield ML pipeline demo using synthetic data.
    Replace DatasetLoader.generate_synthetic_* with real dataset loaders
    when you have downloaded the CMU / Balabit / HMOG datasets.
    """
    print("=" * 65)
    print("  Q-Shield ML Pipeline — Demo Run")
    print("=" * 65)

    N_USERS      = 8
    N_ENROLLMENT = 25
    N_TEST       = 10
    N_COMPONENTS = 64   # state vector dimension

    # ── 1. Load synthetic datasets ────────────────────────────────────────
    print("\n[1] Loading datasets...")
    ks_df    = DatasetLoader.generate_synthetic_cmu(n_users=N_USERS, sessions_per_user=50)
    mouse_df = DatasetLoader.generate_synthetic_mouse(n_users=N_USERS)
    touch_df = DatasetLoader.generate_synthetic_touch(n_users=N_USERS)

    # ── 2. Extract features ───────────────────────────────────────────────
    print("\n[2] Extracting features...")
    ks_feat    = FeatureExtractor.extract_keystroke_features(ks_df)
    touch_feat = FeatureExtractor.extract_touch_features(touch_df)

    # Per-user keystroke feature matrix
    subject_col = "subject"
    feature_cols = [c for c in ks_feat.columns if c != subject_col]
    user_features = {}
    for _, row in ks_feat.iterrows():
        uid = row[subject_col]
        user_features[uid] = row[feature_cols].values.astype(float)

    # Build feature matrices per user from the session data
    user_matrices = {}
    for uid in ks_df["subject"].unique():
        sessions = ks_df[ks_df["subject"] == uid]
        feat_cols = [c for c in sessions.columns
                     if c not in ["subject", "sessionIndex"]]
        user_matrices[uid] = sessions[feat_cols].values.astype(float)

    # ── 3. Fit encoder ────────────────────────────────────────────────────
    print("\n[3] Fitting FFT encoder...")
    all_features = np.vstack(list(user_matrices.values()))
    encoder = QuantumInspiredEncoder(n_components=N_COMPONENTS)
    encoder.fit(all_features)

    # ── 4. Enroll users ───────────────────────────────────────────────────
    print("\n[4] Enrolling users...")
    tm = IdentityTemplateManager(encoder, n_enrollment=N_ENROLLMENT)
    users = list(user_matrices.keys())
    enrolled_users   = users[:6]    # 6 enrolled
    impostor_users   = users[6:]    # 2 impostors

    for uid in enrolled_users:
        tm.enroll(uid, user_matrices[uid])

    # ── 5. Train LSTM Autoencoder for anomaly detection ───────────────────
    print("\n[5] Training LSTM Autoencoder...")
    # Use state vectors from first enrolled user as normal profile
    ref_user   = enrolled_users[0]
    ref_states = encoder.encode_batch(user_matrices[ref_user][:40])
    ad = LSTMAutoencoder(seq_len=10, n_features=N_COMPONENTS, latent_dim=32)
    ad.fit(ref_states, epochs=30, batch_size=16)

    # ── 6. Authentication engine ──────────────────────────────────────────
    print("\n[6] Initializing authentication engine...")
    auth = AuthenticationEngine(tm, ad, fidelity_threshold=0.70)

    # ── 7. Test genuine authentication ───────────────────────────────────
    print("\n[7] Testing genuine authentications...")
    for uid in enrolled_users[:3]:
        probe_vec = user_matrices[uid][-1]   # last (unseen) session
        result = auth.authenticate(uid, probe_vec)
        print(f"  User {uid}: {result['decision']:12s} | "
              f"Fidelity={result['fidelity']:.4f}")

    # ── 8. Test impostor authentication ──────────────────────────────────
    print("\n[8] Testing impostor authentications...")
    for imp_uid in impostor_users:
        # Impostor claims to be the first enrolled user
        claimed = enrolled_users[0]
        probe_vec = user_matrices[imp_uid][-1]
        result = auth.authenticate(claimed, probe_vec)
        print(f"  Impostor {imp_uid} claims {claimed}: "
              f"{result['decision']:12s} | Fidelity={result['fidelity']:.4f}")

    # ── 9. Evaluate with metrics ──────────────────────────────────────────
    print("\n[9] Computing evaluation metrics...")
    genuine_data  = {uid: user_matrices[uid] for uid in enrolled_users}
    impostor_data = {uid: user_matrices[uid] for uid in impostor_users}

    metrics = PipelineEvaluator.evaluate_pipeline(
        auth, genuine_data, impostor_data
    )

    print("\n" + "─" * 50)
    print("  EVALUATION RESULTS")
    print("─" * 50)
    print(f"  EER        : {metrics['EER']:.3f}%")
    print(f"  AUC        : {metrics['AUC']:.4f}")
    print(f"  FAR @ EER  : {metrics['FAR_at_EER']:.3f}%")
    print(f"  FRR @ EER  : {metrics['FRR_at_EER']:.3f}%")
    print(f"  Threshold  : {metrics['EER_thresh']:.4f}")
    print(f"  Genuine probes evaluated : {metrics['n_genuine_probes']}")
    print(f"  Impostor probes evaluated: {metrics['n_impostor_probes']}")
    print("─" * 50)
    print("\n[DONE] Pipeline complete.")
    return metrics


if __name__ == "__main__":
    run_demo_pipeline()