# TaxClaw v0.1 Runbook

## Setup

```bash
cd ~/.openclaw/workspace/skills/taxclaw
bash setup.sh

# Config is created (if missing) at:
#   ~/.config/taxclaw/config.yaml
```

## Start the web UI

```bash
cd ~/.openclaw/workspace/skills/taxclaw
bash start.sh
# open http://localhost:8421
```

## Ingest via CLI

```bash
cd ~/.openclaw/workspace/skills/taxclaw
./bin/taxclaw ingest /path/to/doc.pdf --filer doug --year 2025

./bin/taxclaw list
```

## Export

### Single document

```bash
./bin/taxclaw export --id <doc-id> --format wide > out-wide.csv
./bin/taxclaw export --id <doc-id> --format long > out-long.csv
./bin/taxclaw export --id <doc-id> --format json > out.json
```

### All documents

```bash
./bin/taxclaw export --all --format wide > taxclaw-all-wide.csv
./bin/taxclaw export --all --format long > taxclaw-all-long.csv
./bin/taxclaw export --all --format json > taxclaw-all.json
```

## Smoke test

```bash
cd ~/.openclaw/workspace/skills/taxclaw
./scripts/smoke.sh
```
