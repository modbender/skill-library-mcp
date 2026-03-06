# Sys-updater Refactor Plan (2026-02-19)

## Scope
Refactor technical debt identified in review while keeping runtime behavior stable.

## Goals
1. Reduce duplication across package managers (npm/pnpm/brew).
2. Make pending/planned transitions deterministic and auditable.
3. Keep 06:00/09:00 flows stable with no sudo-policy regressions.

## Risks
- Breaking manager-specific edge cases (especially brew link recovery).
- Divergence between tracked state and real outdated state.

## Superpowers Pipeline

### 1) Spec (what “done” means)
- Shared manager registry used by check/review/upgrade code paths.
- npm/pnpm upgrade logic unified into one function.
- behavior parity preserved for:
  - pending->planned escalation
  - brew link recovery
  - post-upgrade recheck
- scripts compile + dry-run flows pass.

### 2) Plan
- [x] Add manager registry helpers in `pkg_maint.py`.
- [x] Refactor `check_mode` to generic manager loop.
- [x] Refactor `review_mode` to generic manager loop.
- [x] Extract shared npm/pnpm upgrade routine.
- [x] Keep brew upgrade logic specialized (link recovery).
- [x] Validate via py_compile + dry-run checks.

### 3) Execution notes
- Introduced:
  - `MANAGER_ORDER`, `MANAGER_TRACK_PATHS`, `MANAGER_CHECKERS`
  - `_load_all_tracked`, `_save_all_tracked`, `_count_flag`
  - `_upgrade_node_manager` (shared npm/pnpm path)
- Preserved brew-specific recovery logic.
- Kept report and state formats backward-compatible.

### 4) Validation
- `python3 -m py_compile scripts/*.py` ✅
- `python3 scripts/pkg_maint.py check` ✅
- `python3 scripts/pkg_maint.py upgrade --dry-run` ✅
- `python3 scripts/apt_maint.py report_9am` ✅
- `python3 scripts/apt_maint.py auto-review --dry-run` ✅

## Result
Core manager orchestration debt reduced; behavior remains stable.

## Next refactor batch
1. Extract manager adapters into `scripts/managers/*.py` (full modularization).
2. Add tests for:
   - pnpm no-importer case
   - stale pending -> planned
   - brew link recovery path
3. Add strict run markers in 06:00 flow (`START/END`) with correlation id.
