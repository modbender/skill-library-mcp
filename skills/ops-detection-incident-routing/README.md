# Ops Detection + Incident Routing (Public)

This folder is a standalone ClawHub-publishable skill package.

## Publish

```bash
npx clawhub@latest publish . \
  --slug ops-detection-incident-routing \
  --name "Ops Detection + Incident Routing" \
  --version 1.0.0 \
  --changelog "Initial public release"
```

## Local smoke test

```bash
bash scripts/setup.sh
bash scripts/ops-detector-cycle.sh \
  --workspace "$(pwd)/examples/workspace" \
  --state-file "$(pwd)/examples/incident-state.json" \
  --detector-out "$(pwd)/examples/ops-detector.jsonl" \
  --router-out "$(pwd)/examples/router-actions.jsonl"
```

## Re-publish from a used folder

If you previously ran local tests, clean generated runtime artifacts before publishing:

```bash
bash scripts/clean-generated.sh
```
