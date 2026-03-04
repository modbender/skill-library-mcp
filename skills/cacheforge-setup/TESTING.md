# Testing

## Local Checks

```bash
python3 skills/cacheforge-setup/setup.py --help
python3 skills/cacheforge-setup/setup.py provision --help
python3 skills/cacheforge-setup/setup.py openclaw-snippet --help
python3 -m py_compile skills/cacheforge-setup/setup.py
```

## Expected Results

- CLI commands render help without errors.
- Script compiles cleanly.
