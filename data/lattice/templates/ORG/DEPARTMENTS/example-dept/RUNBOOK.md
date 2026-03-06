# <Department Name> — Runbook

## Mission
<!-- Brief restatement -->

## Pipeline-Driven
This department uses the Pipeline framework. Orchestrated by `pipeline-orchestrator` cron every 30 minutes.

### Canonical Paths
- Org: `ORG/`
- Project pipeline: `ORG/PROJECTS/<project>/`
- Repo: `<path-to-repo>`

## Boot
1. Read `ORG/PROJECTS/<project>/STATUS.md`
2. Read `ORG/PROJECTS/<project>/PIPELINE_STATE.json`
3. Check `ASSET_REGISTRY.md` for reusable tooling

## Closeout
1. Update dept HANDOFF (Done / Next / Blockers + links)
2. Update project STATUS / DECISIONS when major progress is made
3. If an asset becomes reusable: register in `ASSET_REGISTRY.md`
