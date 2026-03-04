#!/usr/bin/env python3
"""
ML Evolution Agent - Baseline Training Template
Copy and adapt for your competition
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from catboost import CatBoostClassifier
import lightgbm as lgb
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

# ===== CONFIGURATION =====
COMPETITION = "your-competition-name"
DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./submissions")
TARGET_COLUMN = "target"  # Change this
RANDOM_STATE = 42

# ===== LOAD DATA =====
print(f"🚀 {COMPETITION} - Baseline Training")
print("="*60)

train = pd.read_csv(DATA_DIR / "train.csv")
test = pd.read_csv(DATA_DIR / "test.csv")

# Prepare features
features = [col for col in train.columns if col not in ['id', TARGET_COLUMN]]
X = train[features]
y = train[TARGET_COLUMN]
X_test = test[features]
test_id = test['id']

print(f"Train: {X.shape}, Test: {X_test.shape}")

# ===== TARGET STATISTICS (Proven Effective) =====
print("\n📊 Adding Target Statistics...")
for col in features:
    stats = train.groupby(col)[TARGET_COLUMN].agg(['mean', 'count']).reset_index()
    stats.columns = [col, f'{col}_target_mean', f'{col}_count']
    
    train = train.merge(stats, on=col, how='left')
    test = test.merge(stats, on=col, how='left')
    
    train[f'{col}_target_mean'].fillna(train[TARGET_COLUMN].mean(), inplace=True)
    train[f'{col}_count'].fillna(0, inplace=True)
    test[f'{col}_target_mean'].fillna(train[TARGET_COLUMN].mean(), inplace=True)
    test[f'{col}_count'].fillna(0, inplace=True)

# Update features
features = [c for c in train.columns if c not in ['id', TARGET_COLUMN]]
X = train[features]
X_test = test[features]

print(f"Total features: {len(features)}")

# ===== TRAINING =====
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

oof_cat, pred_cat = np.zeros(len(X)), np.zeros(len(X_test))
oof_lgb, pred_lgb = np.zeros(len(X)), np.zeros(len(X_test))
oof_xgb, pred_xgb = np.zeros(len(X)), np.zeros(len(X_test))

print("\n📊 Training...")
for fold, (tr_idx, val_idx) in enumerate(kfold.split(X, y)):
    print(f"Fold {fold+1}/5", end=' ')
    
    # CatBoost
    cat = CatBoostClassifier(
        iterations=1000, learning_rate=0.05, depth=6,
        random_seed=RANDOM_STATE, verbose=False
    )
    cat.fit(X.iloc[tr_idx], y.iloc[tr_idx])
    oof_cat[val_idx] = cat.predict_proba(X.iloc[val_idx])[:, 1]
    pred_cat += cat.predict_proba(X_test)[:, 1] / 5
    
    # LightGBM
    lgbm = lgb.LGBMClassifier(
        n_estimators=1000, learning_rate=0.05, num_leaves=31,
        random_state=RANDOM_STATE, verbose=-1
    )
    lgbm.fit(X.iloc[tr_idx], y.iloc[tr_idx])
    oof_lgb[val_idx] = lgbm.predict_proba(X.iloc[val_idx])[:, 1]
    pred_lgb += lgbm.predict_proba(X_test)[:, 1] / 5
    
    # XGBoost
    xgbm = xgb.XGBClassifier(
        n_estimators=1000, learning_rate=0.05, max_depth=6,
        random_state=RANDOM_STATE, verbosity=0
    )
    xgbm.fit(X.iloc[tr_idx], y.iloc[tr_idx])
    oof_xgb[val_idx] = xgbm.predict_proba(X.iloc[val_idx])[:, 1]
    pred_xgb += xgbm.predict_proba(X_test)[:, 1] / 5
    
    cat_score = roc_auc_score(y.iloc[val_idx], oof_cat[val_idx])
    print(f"Cat: {cat_score:.5f}")

# ===== RESULTS =====
print(f"\n{'='*60}")
print(f"CatBoost: {roc_auc_score(y, oof_cat):.5f}")
print(f"LightGBM: {roc_auc_score(y, oof_lgb):.5f}")
print(f"XGBoost:  {roc_auc_score(y, oof_xgb):.5f}")

# Blend (Proven weights: 50/25/25)
blend = pred_cat * 0.5 + pred_lgb * 0.25 + pred_xgb * 0.25
blend_oof = oof_cat * 0.5 + oof_lgb * 0.25 + oof_xgb * 0.25
print(f"Blend:    {roc_auc_score(y, blend_oof):.5f}")
print(f"{'='*60}")

# ===== SAVE =====
from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = OUTPUT_DIR / f'submission_{timestamp}.csv'

pd.DataFrame({'id': test_id, TARGET_COLUMN: blend}).to_csv(output_file, index=False)
print(f"\n✅ Saved: {output_file}")

# ===== SUBMIT (Optional) =====
# Uncomment to auto-submit
# import subprocess
# subprocess.run(['kaggle', 'competitions', 'submit', '-c', COMPETITION,
#                 '-f', str(output_file), '-m', f'Baseline (CV {roc_auc_score(y, blend_oof):.5f})'])
