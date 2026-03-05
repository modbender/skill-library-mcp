# parentality_engine.py

Preview utility to evaluate child scores and emit instinct cron plans.

## Run

```bash
python3 scripts/parentality_engine.py \
  --state schema/parentality-preview.json \
  --out prescriptions/parentality-plan.preview.json
```

## Recovery check (close instinct context)

```bash
python3 scripts/parentality_engine.py \
  --state schema/parentality-preview.json \
  --previous prescriptions/parentality-plan.preview.json \
  --out prescriptions/parentality-plan.next.json
```

If the recovery section returns `resolved: true`, instinct context can be closed (`exit-instinct-context`).
