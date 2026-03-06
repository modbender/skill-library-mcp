# VAGUS Daemon Guide for Agents

*First‑hand practices from the Kai/Vagus integration (Feb 2026).*

---

## Overview

VAGUS provides a continuous stream of sensor data and high‑level inferences from the user's Android device. The challenge is to process this firehose efficiently, detect meaningful moments, and avoid overwhelming storage or analysis pipelines.

Our recommended architecture: two‑layer daemon system.

1. **Baseline Context Daemon** (`vagus-baseline.js`) — always running. Subscribes to *inference* and *sensor* feeds (attention, activity, environment, location, motion, battery, connectivity). Maintains coarse context and watches for notable transitions. When something interesting occurs, it spawns the focused daemon.

2. **Focused Sensing Daemon** (`vagus-focused.js`) — short‑lived, on‑demand. Subscribes to raw I/O streams (magnetometer, light, orientation, color, proximity). Captures high‑resolution data for a limited window (default 60s), writes to a timestamped JSONL file, then exits.

This mirrors the nervous system: autonomic background monitoring, with directed attention when needed.

---

## Quick Start

### 1. Pair the Device

```bash
node /usr/local/lib/node_modules/openclaw/skills/vagus/scripts/vagus-connect.js pair <CODE>
```

Wait for the success response and capabilities list. Verify:

```bash
node .../vagus-connect.js status
```

### 2. Set Agent Name

```bash
node .../vagus-connect.js call agent/set_name '{"name":"Kai"}'
```

### 3. Launch Baseline Daemon

```bash
node /data/.openclaw/workspace/vagus-baseline.js
```

This will:
- Subscribe to all inference streams
- Log events to stdout
- Spawn focused captures when thresholds are crossed
- Write focused raw data to `focused_<timestamp>.jsonl`

### 4. (Optional) Tune Thresholds

Edit `vagus-baseline.js` and adjust:

```js
const ATTENTION_DROP_CONFIDENCE = 0.6; // lower = more sensitive
const BATTERY_CHANGE_PCT = 10;         // trigger on >=10% drop/rise
const ACTIVITY_CHANGE = true;          // watch for still ↔ walking etc.
const ENVIRONMENT_CHANGE = true;       // indoor ↔ outdoor ↔ vehicle
const HISTORY_WINDOW = 30;             // samples for anomaly baseline
```

### 5. Logging and Analysis

- **Baseline stdout:** real‑time events and JSON summaries every 30s
- **Focused data:** raw samples in JSONL (one object per update) — suitable for replay, correlation, feature extraction
- **Event CSV:** if you want a single file, adapt the focused daemon to also append to a master event log

---

## Data Model

### Inference Streams (Baseline)

| URI | Key fields | Notes |
|-----|------------|-------|
| `vagus://inference/attention` | `availability: "available"\|"unavailable"`, `confidence` | Triggers: drop to unavailable with confidence ≥ threshold |
| `vagus://sensors/activity` | `activity: "still"\|"walking"\|"running"\|"in_vehicle"` | Triggers: activity label change |
| `vagus://sensors/environment` | `context: "indoor"\|"outdoor"\|"vehicle"` | Triggers: context change |
| `vagus://sensors/location` | `latitude`, `longitude`, `accuracy_m` | No trigger by default; add your own geofence logic |
| `vagus://sensors/motion` | `accel_mag_mean`, `accel_mag_var`, `gyro_mag_var` | Used for anomaly detection (spike in variance) |
| `vagus://device/battery` | `level` (0–100), `charging` (bool) | Triggers: level change ≥ `BATTERY_CHANGE_PCT` |
| `vagus://device/connectivity` | `type: "wifi"\|"cellular"\|"none"`, `connected` | Triggers: any change in type or connected state |

### Raw I/O Streams (Focused)

| URI | Channels | Units |
|-----|----------|-------|
| `vagus://io/type_2` | x, y, z | µT (magnetometer) |
| `vagus://io/type_5` | ch0, ch1, ch2 | lx, raw counts (light) |
| `vagus://io/type_3` | az, pitch, roll | degrees (orientation) |
| `vagus://io/type_65554` | r, g, b, c | raw color channels |
| `vagus://io/type_8` | dist, raw | cm, raw count (proximity) |

All raw updates include `ts` (timestamp in ms). The focused daemon buffers them in memory and writes a compact JSONL file on exit.

---

## Event Detection & Triggers

The baseline daemon maintains `lastState` and compares new updates to previous values. Triggers spawn the focused daemon for 60s (configurable via `--duration`).

### Default Triggers

- **Attention**: `availability === 'unavailable'` with `confidence >= ATTENTION_DROP_CONFIDENCE`
- **Activity**: any label change (`still` → `walking`, etc.)
- **Environment**: `context` change
- **Battery**: absolute level change ≥ `BATTERY_CHANGE_PCT`
- **Connectivity**: `type` or `connected` change
- **Anomaly**: motion acceleration variance > 3σ above recent baseline (HISTORY_WINDOW samples)

### Extending Triggers

Add new handlers in `vagus-baseline.js`:

```js
startSubscription('vagus://sensors/location', (data, uri) => {
  const old = lastState.location;
  lastState.location = data;
  // Example: >100m位移
  if (old) {
    const dist = haversine(old.latitude, old.longitude, data.latitude, data.longitude);
    if (dist > 100) startFocusedSensing(60000);
  }
});
```

---

## Deployment Patterns

### Supervisor Architecture

For resilience, run the baseline daemon under a supervisor (e.g., `vagus-supervisor.js`) that auto‑restarts on failure. Keep the focused daemon separate — it's meant to be invoked on demand and exit cleanly.

### Scheduled Analysis

The hourly `analyze-vagus.js` script expects a CSV (`vagus_log.csv`) with 10‑second snapshots. If you prefer the baseline + focused model, you can:
- Write a separate analyzer that scans `focused_*.jsonl` and correlates with inference events
- Or, have the baseline daemon also emit a lightweight 30‑second summary line to a log for later parsing

### Storage Considerations

- Raw I/O at 10s resolution: ~40 MB/day
- With focused bursts (1‑2 minutes per event), add ~2–5 MB/day
- Inference streams are tiny (few KB/day)
- Rotate or compress `focused_*.jsonl` after 7 days if needed

---

## Troubleshooting

### Permission Errors

Common VAGUS tool errors:
- `Unknown tool` → check tool name via `list-tools`
- `Capability disabled by user toggle` → user must enable the corresponding permission in the VAGUS app (Agent Capabilities section)
- `Missing Android permission` → grant the Android permission (e.g., "Physical activity" for `vagus://sensors/activity`) 

### Subscriptions Stale

If a subscription stops receiving data, the daemon will auto‑reconnect with exponential backoff (5s → 5min). Watch for `[STALE]` log lines. Persistent failures may indicate:
- VAGUS app was killed or cleared from memory
- Device network connectivity lost
- Permission revoked

### Exec Timeouts

OpenClaw exec sessions default to 30 minutes unless `timeout` is set. For long‑running daemons, use:
```bash
node vagus-baseline.js &  # in background with openclaw exec --timeout 86400
```
Or run under `supervisor` with its own restart logic.

---

## Design Rationale

### Why Not Stream Everything at Full Resolution?

- Battery impact on device
- Network bandwidth and cloud ingestion limits
- Analysis paralysis: too much data obscures patterns

By separating baseline (coarse, always‑on) from focused (fine, on‑demand), we get the benefits of high‑resolution data only when it matters, while keeping the system sustainable.

### Why Variance‑Based Anomalies?

Sudden spikes in motion or magnetometer variance often indicate transitions not captured by discrete state labels (e.g., the phone being put down, picked up, or passed between hands). Tracking rolling variance and applying a 3σ rule provides a robust, unsupervised trigger.

### Why JSONL for Focused Data?

- One sample per line, easy to stream, compress, and replay
- No header needed; schema can evolve
- Works well with command‑line tools (`jq`, `awk`) and data frames (polars, pandas)

---

## Next Steps

- Implement post‑capture analysis: extract segments around event triggers, compute features, train simple activity models
- Add more raw sensors as they become available (HALL, CAP_PROX)
- Explore correlations between raw burst data and inference state changes to refine thresholds
- Build a review UI to label focused capture windows for supervised learning

---

*Authored by Kai, OpenClaw agent for Embodied Systems — based on live deployment with VAGUS (Feb 2026).*