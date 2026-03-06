# Testing

## Local Checks

```bash
python3 skills/cacheforge-stats/dashboard.py --help
python3 -m py_compile skills/cacheforge-stats/dashboard.py
```

## Live API Smoke (requires key)

```bash
export CACHEFORGE_API_KEY=cf_...
python3 skills/cacheforge-stats/dashboard.py usage --window 7d
```
