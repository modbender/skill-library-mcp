# Task Plan: med-info v0.3.0 growth pass (resources + features + marketing)

## Goal
1) Improve the ClawHub consumer-facing page (SKILL.md copy, examples).
2) Research 100+ public/open resources that can make `med-info` better, document them, and run a smoke-test probe.
3) Implement a small set of high-value new integrations, run checks, then publish a new version.

## Current Phase
Phase 4b (Pharmacist workflow upgrades)

## Phases

### Phase 1: Page review + requirements
- [ ] Review current ClawHub page (what is shown from SKILL.md)
- [ ] Decide what “enticing but accurate” means, tighten copy and examples
- **Status:** in_progress

### Phase 2: Research 100+ resources
- [ ] Build a catalog of 100+ open/public sources (APIs, datasets, docs) relevant to medication info
- [ ] For each: what it adds, access method, and a suggested smoke-test
- **Status:** not_started

### Phase 3: Smoke-test/probe harness
- [ ] Create a resources manifest (JSON/YAML)
- [ ] Implement a probe script that can run quickly and record results
- [ ] Save probe report artifact(s)
- **Status:** not_started

### Phase 4: Implement high-value features
- [x] RxNav interactions integration (`--interactions`)
- [x] PubChem chemical profile (`--chem`)
- [ ] (Optional if time) Drugs@FDA approvals via openFDA drugsfda (`--approvals`)
- **Status:** complete

### Phase 4b: Pharmacist workflow upgrades (2026-02-13)
- [ ] Add pharmacist output profile (curated SPL section bundle)
- [ ] Strengthen NDC mode (NDC-11 normalization, packaging details, marketing status)
- [ ] Add safety flags block (boxed warning present, schedule guess)
- [ ] Add NIOSH hazardous list flag (best-effort, cached; uses NIOSH 2024 list PDF)
- [ ] Add FDA REMS best-effort lookup/linking (graceful degrade if blocked)
- [ ] Update SKILL.md examples + docs + resources manifest
- [ ] Run smoke tests (py_compile + a few real queries)
- **Status:** in_progress

### Phase 5: Checks + publish
- [ ] Run lint/compile checks and a couple real-world queries
- [ ] Bump version and publish to ClawHub
- [ ] Verify listing, rerun VirusTotal scan later if needed
- **Status:** not_started

## Key Questions
1. What is the most useful candidate summary for `--candidates` (set_id, effective_time, product, ingredients, route, dosage_form)?
2. What search strategy for enforcement/shortages is reliable (by brand/generic, by product_ndc, by openfda fields)?

## Decisions Made
| Decision | Rationale |
|---|---|
| Add explicit CLI flags rather than changing default output | Avoid breaking existing workflows |
| Make recalls/shortages opt-in flags | Keeps default fast and avoids noisy results |

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| planning-with-files referenced session-catchup.py missing | 1 | Proceed without catchup, note in findings |
