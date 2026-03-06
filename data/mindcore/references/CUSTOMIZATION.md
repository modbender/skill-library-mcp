# 🔧 Customization Guide

This guide explains how to modify MindCore's layers, sensors, impulses, and personality to fit your own use case.

## Table of Contents

- [Changing Sensor Count (Layer 1)](#changing-sensor-count-layer-1)
- [Modifying the Impulse Library (Layer 2)](#modifying-the-impulse-library-layer-2)
- [Personality Weights (Layer 3)](#personality-weights-layer-3)
- [Tuning Global Parameters](#tuning-global-parameters)
- [Regenerating the Synapse Matrix](#regenerating-the-synapse-matrix)

---

## Changing Sensor Count (Layer 1)

By default, Layer 1 has **150 sensors** (50 body + 50 environment + 50 social). You can change this to any number.

### Step 1: Update `engine/config.py`

```python
# Example: reduce to 20 sensors total (8 body + 6 env + 6 social)
LAYER1_BODY_NODES    = 8
LAYER1_ENV_NODES     = 6
LAYER1_SOCIAL_NODES  = 6
TOTAL_LAYER1_NODES   = LAYER1_BODY_NODES + LAYER1_ENV_NODES + LAYER1_SOCIAL_NODES  # 20
```

### Step 2: Update `data/Sensor_State.json`

Make sure the JSON keys match your new sensor count. For example, if you only want 8 body sensors:

```json
{
    "body": {
        "hungry": 0,
        "tired": 0,
        "caffeine_high": 0,
        "headache": 0,
        "full_stomach": 0,
        "cold_hands": 0,
        "eye_fatigue": 0,
        "back_pain": 0
    },
    "environment": { ... },
    "social": { ... }
}
```

### Step 3: Update `engine/layer1_sensors.py`

The `LAYER1_KEYS` list defines the sensor reading order. It must match your JSON keys exactly:

```python
LAYER1_KEYS = [
    # body (8)
    "body.hungry", "body.tired", "body.caffeine_high", ...
    # environment (6)
    "environment.is_raining", ...
    # social (6)
    "social.someone_online", ...
]
```

### Step 4: Regenerate the Synapse Matrix

After changing sensor count, you **must** regenerate the synapse matrix (see [below](#regenerating-the-synapse-matrix)).

---

## Modifying the Impulse Library (Layer 2)

By default, Layer 2 has **150 impulses** across 9 categories. You can replace them entirely.

### Step 1: Update `engine/config.py`

```python
TOTAL_LAYER2_NODES = 30  # your new impulse count
```

### Step 2: Update `engine/layer2_impulses.py`

Replace the `IMPULSE_NAMES` list with your own:

```python
IMPULSE_NAMES = [
    # Your custom impulses
    "impulse_check_email",
    "impulse_take_break",
    "impulse_drink_water",
    # ... (must have exactly TOTAL_LAYER2_NODES items)
]
```

Also update `IMPULSE_CATEGORIES` to define which indices belong to which category:

```python
IMPULSE_CATEGORIES = {
    "work":        range(0, 10),
    "health":      range(10, 20),
    "social":      range(20, 30),
}
```

### Step 3: Update `TIME_PERIOD_WEIGHTS`

The time-period weight matrix has shape `(TOTAL_LAYER2_NODES, 5)`, where the 5 columns represent:
- `morning` (6:00-9:00)
- `daytime` (9:00-17:00)
- `evening` (17:00-21:00)
- `night` (21:00-0:00)
- `late_night` (0:00-6:00)

Each value is a multiplier (default `1.0`). Set lower values to suppress an impulse at certain times:

```python
TIME_PERIOD_WEIGHTS = np.ones((30, 5), dtype=np.float64)
TIME_PERIOD_WEIGHTS[0, 4] = 0.1  # "check_email" almost never fires at late_night
```

### Step 4: Regenerate the Synapse Matrix

After changing impulse count, you **must** regenerate the synapse matrix.

---

## Personality Weights (Layer 3)

Layer 3 acts as a **personality gate** — it filters which impulses from Layer 2 actually "win" and get output.

### How It Works

1. Layer 2 produces a list of fired impulses with raw activation strengths
2. Layer 3 multiplies each impulse's strength by its **personality weight** (a float from 0.0 to 1.0)
3. The weighted impulses go through **Softmax sampling** — higher-weighted impulses are more likely to win
4. The top 1-2 impulses are selected as output

### Adjusting Personality Weights

Personality weights are stored in `data/personality_weights.npy` (auto-created on first run). To customize:

```python
import numpy as np

# Load current weights
weights = np.load("data/personality_weights.npy")

# weights.shape = (TOTAL_LAYER2_NODES,)
# Each value is between 0.0 and 1.0

# Example: make this personality love food-related impulses
weights[0:18] = 0.9   # food category (indices 0-17) → high weight

# Example: suppress exercise impulses
weights[73:88] = 0.1   # exercise category → low weight

# Save
np.save("data/personality_weights.npy", weights)
```

### Default Initialization

If `personality_weights.npy` doesn't exist, all weights start at `PERSONALITY_INIT_WEIGHT` (default `0.5`) — a blank-slate personality with no preferences.

### Reinforcement Learning (Future)

The system is designed to support RL-based personality evolution: when the user positively reacts to a certain type of impulse, its weight increases slightly. This is not yet fully implemented but the infrastructure is in place.

### Short-Term Memory Topic Boost

Layer 3 also applies a **topic boost** from short-term memory. When recent conversations mention certain keywords (e.g., "coffee", "exercise"), related impulse categories receive a temporary multiplier (up to `TOPIC_BOOST_MAX = 2.0x`), decaying with a 2-hour half-life.

This is defined via `TOPIC_CATEGORY_MAP` in `engine/layer3_personality.py`:

```python
TOPIC_CATEGORY_MAP = {
    "咖啡": ["food"],
    "运动": ["exercise"],
    "代码": ["study", "creative"],
    # Add your own keyword → category mappings
}
```

---

## Tuning Global Parameters

All tunable hyperparameters are in `engine/config.py`:

### Burst Frequency

| Parameter | Default | Description |
|---|---|---|
| `BURST_BASE_OFFSET` | `12.5` | Sigmoid offset controlling overall firing rate. Lower = more frequent |
| `TICK_INTERVAL_SEC` | `1.0` | Engine tick interval in seconds |

### Noise Generators (Layer 0)

| Parameter | Default | Description |
|---|---|---|
| `PINK_NOISE_NODES` | `1000` | Number of pink noise generators |
| `OU_THETA` | `0.15` | OU process mean-reversion speed |
| `OU_SIGMA` | `0.3` | OU process volatility |
| `HAWKES_MU0` | `0.02` | Hawkes base firing rate |
| `HAWKES_ALPHA` | `0.5` | Hawkes excitation intensity |

### Circadian Rhythm

| Parameter | Default | Description |
|---|---|---|
| `CIRCADIAN_PEAK_HOUR` | `21.0` | Hour of peak activity (24h format) |
| `CIRCADIAN_TROUGH_HOUR` | `4.0` | Hour of minimum activity |
| `CIRCADIAN_MIN_MULT` | `0.05` | Minimum activity multiplier |
| `CIRCADIAN_MAX_MULT` | `1.5` | Maximum activity multiplier |

### Mood Dynamics

| Parameter | Default | Description |
|---|---|---|
| `MOOD_DECAY_RATE` | `0.995` | Per-tick mood decay toward neutral |
| `COMFORT_BASE_DELTA` | `0.2` | How much a comforting interaction heals mood |

---

## Regenerating the Synapse Matrix

The **Synapse Matrix** (`data/Synapse_Matrix.npy`) maps Layer 1 sensors to Layer 2 impulses. It's auto-generated using semantic similarity between sensor names and impulse names via a local NLP model.

**You must regenerate it whenever you change the sensor count or impulse count.**

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from engine.auto_topology import AutoTopologyBuilder
builder = AutoTopologyBuilder()
builder.build_and_save()
print('Done!')
"
```

This uses the `all-MiniLM-L6-v2` model (downloaded automatically, ~80MB) to compute cosine similarity between sensor descriptions and impulse descriptions, creating a biologically-plausible connection matrix.

---

## Example: A Minimal 20-Sensor, 30-Impulse Setup

If you want a lightweight engine for a simple companion bot:

1. Set `LAYER1_BODY_NODES=8`, `LAYER1_ENV_NODES=6`, `LAYER1_SOCIAL_NODES=6` in `config.py`
2. Set `TOTAL_LAYER2_NODES=30`, `TOTAL_LAYER3_NODES=30` in `config.py`
3. Define 20 sensor keys in `Sensor_State.json` and `layer1_sensors.py`
4. Define 30 impulse names in `layer2_impulses.py`
5. Run the synapse matrix auto-builder
6. Start `engine_supervisor.py`

The engine will work identically — just with fewer nodes and faster computation.
