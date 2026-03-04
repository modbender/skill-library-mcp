# Reusable Asset Registry

> Purpose: Make reuse discoverable, requestable, and trackable.
>
> Rule: New assets must have an owner. L0/L1/L2 tiering. L1+ reuse requires a REUSE_REQUEST.

---

## Asset Tiers
- **L0 (ready to use)**: Has RUNBOOK + minimal tests + stable I/O
- **L1 (usable with coordination)**: Needs access/env/interface negotiation
- **L2 (one-off delivery)**: No reuse guarantee; needs upgrade to become L1/L0

---

## Directory

### Example: Infrastructure
- L1: Pipeline Orchestrator Framework
  - Owner: Infrastructure
  - Where: `PROJECTS/pipeline-framework/`
  - Docs: `DESIGN.md` + `IMPLEMENTATION.md`
  - Guide: `PIPELINE_GUIDE.md`
  - Templates: `PROJECTS/pipeline-framework/templates/`

<!-- Add your assets here following the pattern above -->

---

## TODO
- [ ] Standardize `ASSETS/<asset>/` directories (README/RUNBOOK/STATE) for each L1/L0 asset
- [ ] Add keyword index (tags) and interface fields (inputs/outputs) for discoverability
