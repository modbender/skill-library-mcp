# Testing

## Local Checks

```bash
python3 skills/cacheforge-ops/ops.py --help
python3 -m py_compile skills/cacheforge-ops/ops.py
```

## Live API Smoke (requires key)

```bash
export CACHEFORGE_API_KEY=cf_...
python3 skills/cacheforge-ops/ops.py balance
python3 skills/cacheforge-ops/ops.py info
```
