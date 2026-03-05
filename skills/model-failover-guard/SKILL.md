# OpenClaw Model Failover Guard

Automatic model failover + failback guard for OpenClaw.

## Description

When your primary model becomes unstable, this guard can switch to an available fallback model automatically, then switch back to the primary after stability is restored.

## Features

- Monitor model health on an interval
- If primary fails N times consecutively → failover
- Fallback is selected from **all configured models**
- Supports preferred fallback provider
- After fallback is stable for N checks → try failback
- If failback test fails → revert to fallback immediately

## Install

```bash
npx skills add BovmantH/openclaw-model-failover-guard --skill model-failover-guard
```

## Usage

```bash
# Run once
python3 skills/model-failover-guard/scripts/failover.py once

# Run as daemon
python3 skills/model-failover-guard/scripts/failover.py loop
```

## Configuration

Copy `skills/model-failover-guard/config.example.json` to `config.json` and adjust settings.

| Key | Description |
|-----|-------------|
| `primaryModel` | Primary model to monitor |
| `failThreshold` | Consecutive failures before failover |
| `recoverThreshold` | Stable checks before failback |
| `checkIntervalSec` | Health check interval (seconds) |

## Author

- Owner: BovmantH
- Version: 1.0.0

## License

MIT
