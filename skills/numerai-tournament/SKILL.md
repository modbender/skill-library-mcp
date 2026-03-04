---
name: numerai-tournament
description: Autonomous Numerai tournament participation — train models, submit predictions, and earn NMR cryptocurrency.
tags:
  - finance
  - machine-learning
  - cryptocurrency
  - trading
  - numerai
  - lightgbm
  - data-science
metadata:
  clawdbot:
    requires:
      env:
        - NUMERAI_PUBLIC_ID
        - NUMERAI_SECRET_KEY
      bins:
        - python3
        - pip
    primaryEnv: NUMERAI_SECRET_KEY
---

# Numerai Tournament

Participate autonomously in the [Numerai](https://numer.ai) data science tournament. Numerai is a hedge fund that crowdsources stock market predictions from data scientists. You submit predictions on obfuscated financial data and earn (or lose) NMR cryptocurrency based on performance.

## Overview

- **What**: Predict stock market returns using obfuscated tabular features
- **How**: Download data, train a model, submit predictions each round
- **Reward**: Stake NMR on predictions; earn or lose based on correlation with targets
- **Frequency**: New rounds open Tue–Sat at 13:00 UTC; scores resolve ~31 days later

## Setup

### 1. Create a Numerai Account

```bash
# Visit https://numer.ai to sign up
# Then create API keys at https://numer.ai/account
# Store credentials:
mkdir -p ~/.numerai
cat > ~/.numerai/credentials.json << 'CREDS'
{
  "public_id": "YOUR_PUBLIC_ID",
  "secret_key": "YOUR_SECRET_KEY"
}
CREDS
chmod 600 ~/.numerai/credentials.json
```

Alternatively, set environment variables:
```bash
export NUMERAI_PUBLIC_ID="YOUR_PUBLIC_ID"
export NUMERAI_SECRET_KEY="YOUR_SECRET_KEY"
```

### 2. Install Dependencies

```bash
python3 -m venv venv && source venv/bin/activate
pip install numerapi lightgbm pandas numpy cloudpickle scikit-learn
```

On macOS ARM (Apple Silicon), LightGBM also requires:
```bash
brew install libomp
```

### 3. Download Tournament Data

```python
from numerapi import NumerAPI
from pathlib import Path

napi = NumerAPI()  # No auth needed for data download
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Current dataset version is v5.2
napi.download_dataset("v5.2/train.parquet", dest_path=str(data_dir / "train.parquet"))
napi.download_dataset("v5.2/validation.parquet", dest_path=str(data_dir / "validation.parquet"))
napi.download_dataset("v5.2/live.parquet", dest_path=str(data_dir / "live.parquet"))
napi.download_dataset("v5.2/features.json", dest_path=str(data_dir / "features.json"))
napi.download_dataset("v5.2/live_benchmark_models.parquet", dest_path=str(data_dir / "live_benchmark_models.parquet"))
```

**Note**: Training data is ~8GB. Only `live.parquet` and `features.json` are needed for prediction.

## Training a Model

The recommended approach is a LightGBM ensemble trained on multiple targets. This provides strong and stable performance.

### Feature Selection

```python
import json

with open("data/features.json") as f:
    feature_metadata = json.load(f)

# Three feature set sizes:
# "small"  — ~42 features (fast iteration)
# "medium" — ~780 features (good tradeoff)
# "all"    — ~2748 features (maximum signal, slow)
features = feature_metadata["feature_sets"]["medium"]
```

### Target Selection

The main target is `target`. Additional targets improve ensemble diversity:

| Target | Description |
|--------|-------------|
| `target` | Primary tournament target |
| `target_teager2b_20` | Current payout-correlated target |
| `target_cyrusd_20` | Complementary target for ensemble diversity |

### LightGBM Training

```python
import lightgbm as lgb
import pandas as pd
import pickle

train = pd.read_parquet("data/train.parquet", columns=["era"] + features + targets)

lgbm_params = {
    "n_estimators": 5000,       # Use 20000 for production quality
    "learning_rate": 0.005,
    "max_depth": 6,
    "num_leaves": 64,
    "min_child_samples": 5000,
    "colsample_bytree": 0.1,
    "subsample": 0.8,
    "subsample_freq": 1,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "verbose": -1,
    "n_jobs": -1,
}

models = {}
for target in targets:
    X = train[features]
    y = train[target]
    mask = y.notna()
    model = lgb.LGBMRegressor(**lgbm_params)
    model.fit(X[mask], y[mask])
    models[target] = model

with open("models/ensemble_models.pkl", "wb") as f:
    pickle.dump(models, f)
```

### Validation

Evaluate per-era correlation and Sharpe ratio:

```python
val = pd.read_parquet("data/validation.parquet", columns=["era"] + features + targets)
predictions = pd.DataFrame(index=val.index)

for target, model in models.items():
    raw = model.predict(val[features])
    predictions[target] = pd.Series(raw, index=val.index).rank(pct=True)

ensemble = predictions.mean(axis=1).rank(pct=True)

corrs = []
for era in val["era"].unique():
    m = val["era"] == era
    pred_era = ensemble[m]
    tgt = val.loc[m, "target"]
    if tgt.notna().sum() >= 10:
        corrs.append(pred_era.corr(tgt))

corrs = pd.Series(corrs)
print(f"Mean Corr: {corrs.mean():.4f}")
print(f"Sharpe:    {corrs.mean() / corrs.std():.2f}")
print(f"% Positive: {(corrs > 0).mean() * 100:.1f}%")
```

Target validation performance: Mean Corr > 0.02, Sharpe > 1.0, >90% positive eras.

## Submitting Predictions

### Option A: Upload a Predictions CSV (Manual)

```python
import json
from numerapi import NumerAPI

with open("~/.numerai/credentials.json") as f:
    creds = json.load(f)

napi = NumerAPI(creds["public_id"], creds["secret_key"])

# Check round status
current_round = napi.get_current_round()
is_open = napi.check_round_open()
print(f"Round {current_round}, Open: {is_open}")

if is_open:
    # Download live data
    napi.download_dataset("v5.2/live.parquet", dest_path="data/live.parquet")
    live = pd.read_parquet("data/live.parquet")

    # Generate predictions (same ensemble logic as validation)
    predictions = pd.DataFrame(index=live.index)
    for target, model in models.items():
        raw = model.predict(live[features])
        predictions[target] = pd.Series(raw, index=live.index).rank(pct=True)
    ensemble = predictions.mean(axis=1).rank(pct=True)

    # Save and submit
    submission = ensemble.to_frame("prediction")
    submission.to_csv("predictions.csv")
    napi.upload_predictions("predictions.csv", model_id="YOUR_MODEL_ID")
```

### Option B: Upload a Model Pickle (Zero-Maintenance)

Upload a pickled function and Numerai runs it daily — no cron, no server.

**Critical constraints for model upload:**
- Must be a **pickled function** (not a class), loaded via `pd.read_pickle()`
- Must use **Python 3.12** (Numerai's max supported version)
- Must match Numerai runtime packages: `lightgbm==4.5.0`, `numpy==2.1.3`, `pandas==2.3.1`
- Runtime limits: 1 CPU, 4GB RAM, 10 minute timeout
- Use **native LightGBM Boosters** (not sklearn wrappers) to avoid dependency issues

```python
# Build the upload pickle (run with Python 3.12!)
import cloudpickle
import lightgbm as lgb
import pandas as pd
import pickle

# Load trained sklearn models and extract native boosters
with open("models/ensemble_models.pkl", "rb") as f:
    sklearn_models = pickle.load(f)

boosters = {}
for name, model in sklearn_models.items():
    bstr = model.booster_.model_to_string()
    boosters[name] = lgb.Booster(model_str=bstr)

feature_cols = features  # medium feature set list
models = boosters

def predict(live_features: pd.DataFrame, live_benchmark_models: pd.DataFrame = None) -> pd.DataFrame:
    predictions = pd.DataFrame(index=live_features.index)
    for target, booster in models.items():
        raw = booster.predict(live_features[feature_cols])
        predictions[target] = pd.Series(raw, index=live_features.index).rank(pct=True)
    ensemble = predictions.mean(axis=1).rank(pct=True)
    return ensemble.to_frame("prediction")

with open("models/model_upload.pkl", "wb") as f:
    cloudpickle.dump(predict, f)
```

Then upload via the Numerai web UI at https://numer.ai or via API:
```python
napi.upload_model("models/model_upload.pkl", model_id="YOUR_MODEL_ID")
```

## Checking Performance

```python
from numerapi import NumerAPI

napi = NumerAPI(public_id, secret_key)

# Round status
print(f"Current round: {napi.get_current_round()}")

# Get model performance (scores resolve after ~31 days)
# Check via https://numer.ai/models/YOUR_USERNAME
```

## Tournament Rules & Key Facts

- **Dataset**: v5.2 — obfuscated financial features, ~2748 total features
- **Rounds**: Open Tue–Sat at 13:00 UTC. Weekday windows: ~1hr. Saturday: ~49hrs.
- **Scoring**: 20D2L framework, ~31 day resolution
- **Payout formula**: `stake * clip(payout_factor * (0.75*CORR + 2.25*MMC), -0.05, +0.05)`
  - CORR = correlation of predictions with target
  - MMC = meta-model contribution (originality bonus)
- **Staking**: Optional — stake NMR to earn/lose based on performance. Start with 0 stake until the model proves consistent.
- **Current payout target**: Resembles `target_teager2b_20`

## Tips for Strong Performance

1. **Ensemble multiple targets** — reduces variance, improves Sharpe
2. **Rank-normalize predictions** — use `.rank(pct=True)` before averaging and after
3. **Use early stopping** — prevent overfitting with `lgb.early_stopping(300)`
4. **Feature neutralization** — improves MMC by decorrelating from common factors
5. **Era-aware validation** — always evaluate per-era, never row-level metrics
6. **Don't overfit to validation** — Numerai data is non-stationary; keep models simple

## External Endpoints

This skill interacts with the following external services:
- `api.numer.ai` — Numerai GraphQL API for round status, submissions, and scores
- `numer.ai` — Data downloads (tournament datasets)

## Security & Privacy

- Your `NUMERAI_PUBLIC_ID` and `NUMERAI_SECRET_KEY` are sent to `api.numer.ai` for authentication
- Predictions (stock return rankings) are uploaded to Numerai's servers
- No other data leaves your machine
- Store credentials in `~/.numerai/credentials.json` with `chmod 600` permissions
