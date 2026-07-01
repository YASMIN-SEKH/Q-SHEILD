#!/usr/bin/env python3
"""
Q-Shield v2 Backend Initialization
Verifies models are loaded and system is ready for authentication
"""

import sys
import os
from pathlib import Path
import joblib
import pandas as pd

MODELS_DIR = Path(__file__).parent / "qshield_results"

def verify_models():
    """Verify all required models are present and loadable"""
    required_files = [
        'enrolled_templates.pkl',
        'enrolled_session_psi.pkl',
        'fusion_lr.pkl',
        'xgb_model.pkl',
        'xgb_scaler.pkl',
        'lda_projector.pkl',
        'label_encoder.pkl',
        'per_subject_eer.csv',
        'comparison_table.csv',
    ]
    
    print("=" * 60)
    print("Q-Shield v2 Backend Initialization")
    print("=" * 60)
    print(f"\nModels directory: {MODELS_DIR}")
    print(f"Directory exists: {MODELS_DIR.exists()}")
    
    missing = []
    for filename in required_files:
        filepath = MODELS_DIR / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"✓ {filename:<30} ({size_mb:.1f} MB)")
        else:
            print(f"✗ {filename:<30} MISSING")
            missing.append(filename)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} required files:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    # Test loading
    print("\nLoading models...")
    try:
        templates = joblib.load(MODELS_DIR / 'enrolled_templates.pkl')
        print(f"✓ Loaded {len(templates)} enrolled templates")
        
        fusion = joblib.load(MODELS_DIR / 'fusion_lr.pkl')
        print(f"✓ Loaded fusion model (coef shape: {fusion.coef_.shape})")
        
        xgb = joblib.load(MODELS_DIR / 'xgb_model.pkl')
        print(f"✓ Loaded XGBoost model (n_features: {xgb.n_features_in_})")
        
        eer_df = pd.read_csv(MODELS_DIR / 'per_subject_eer.csv')
        print(f"✓ Loaded EER data ({len(eer_df)} subjects)")
        print(f"  Average EER: {eer_df['eer_pct'].mean():.4f}%")
        
        print("\n✅ All models verified and loaded successfully!")
        print(f"\n📊 System Ready:")
        print(f"   Enrolled subjects: {len(templates)}")
        print(f"   Subjects with EER: {len(eer_df)}")
        print(f"   API version: 2.0.0")
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_models()
    sys.exit(0 if success else 1)
