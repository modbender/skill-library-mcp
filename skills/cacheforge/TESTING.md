# Testing

## Local Checks

```bash
openclaw skills check
openclaw skills info cacheforge
bash skills/cacheforge/scripts/bootstrap-companions.sh
```

## Expected Results

- `cacheforge` is eligible in `openclaw skills check`.
- Bootstrap returns `status=ok` when companion skills are present.
- If companions are missing and `clawhub` is available, bootstrap installs them.
