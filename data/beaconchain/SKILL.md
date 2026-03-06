---
name: beaconchain
description: Monitor Ethereum validator dashboard health on beaconcha.in via V2 API, focused on one-check-per-day status and BeaconScore-first triage. Use when the user asks to check validator health, BeaconScore, missed duties, or set up low-anxiety daily monitoring/alerts for a beaconcha.in dashboard.
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "bins": ["python3"],
            "env": ["BEACONCHAIN_API_KEY", "BEACONCHAIN_DASHBOARD_ID"],
          },
        "disableModelInvocation": true,
      },
  }
---

# Beaconchain

Use this skill to reduce validator-check anxiety: do one concise daily health check, then only surface issues.

## Quick Start

1. Set credentials as env vars:
   - `BEACONCHAIN_API_KEY`
   - `BEACONCHAIN_DASHBOARD_ID`
2. Run:

```bash
python3 skills/beaconchain/scripts/check_dashboard.py --json
```

3. Interpret exit code:
   - `0` = good
   - `2` = bad (needs attention)
   - `1` = error (auth/rate-limit/endpoint failure)

## Monitoring Workflow

1. Run `scripts/check_dashboard.py` once per day.
2. If `status=good`, respond with a short reassurance and avoid extra detail.
3. If `status=bad`, report:
   - BeaconScore (if available)
   - Which signal tripped (missed/penalty fallback)
   - Next action: inspect dashboard details and validator logs.
4. If `status=error`, report key checks:
   - API key validity
   - dashboard ID
   - plan/rate-limit permissions.

## Command Patterns

### Basic check

```bash
python3 skills/beaconchain/scripts/check_dashboard.py
```

### JSON output (for cron/parsing)

```bash
python3 skills/beaconchain/scripts/check_dashboard.py --json
```

### Custom threshold

```bash
python3 skills/beaconchain/scripts/check_dashboard.py --warn-threshold 75
```

## Notes

- Script uses `POST /api/v2/ethereum/validators/performance-aggregate` with dashboard selector and reads `data.beaconscore.total` directly.
- Default window is `24h`; supported windows: `24h`, `7d`, `30d`, `90d`, `all_time`.
- Keep responses intentionally terse when healthy to support low-anxiety operations.

## Security & Transparency

- Runtime: `python3` only, using Python standard library (`argparse`, `json`, `urllib`, `datetime`).
- Credentials: reads `BEACONCHAIN_API_KEY` and `BEACONCHAIN_DASHBOARD_ID` (or equivalent CLI flags).
- Network egress: only `https://beaconcha.in/api/v2/ethereum/validators/performance-aggregate`.
- Local filesystem: no writes, no shell execution, no subprocess spawning.

## References

- API overview: `references/api-notes.md`
