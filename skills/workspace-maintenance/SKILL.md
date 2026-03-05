---
name: workspace-maintenance
description: Maintain workspace documentation hygiene and discoverability. Use when organizing markdown sprawl, updating doc indexes, archiving stale progress/status snapshots, generating dry-run cleanup candidate lists, and keeping memory/task control files aligned without deleting files automatically.
---

# Workspace Maintenance

Run a non-destructive maintenance cycle that keeps docs findable and the root clean.

## Execute Maintenance Cycle

1. Run dry-run retention audit script:
   - `scripts/archive-retention-audit.sh`
2. Regenerate or refresh docs index if categories changed.
3. Ensure active control files remain in root (do not move them).
4. Move stale snapshot/status/progress docs to archive buckets.
5. Update active task tracker with maintenance completion timestamp.
6. Produce human review list for deletion candidates (never delete automatically).

## Constraints

- Never delete files automatically.
- Never move identity/control files out of root.
- Keep changes reversible (moves + manifests).
- Always produce a dry-run candidate report.

## Archive Buckets

- `docs/archive/meridian-snapshots/`
- `docs/archive/general-progress/`
- `docs/archive/session-hygiene/`

## Required Outputs

- Updated dry-run candidates file in archive
- Updated active task status entry
- Move manifest for any batch relocation
- Brief completion summary

## Use Bundled Script

- `scripts/archive-retention-audit.sh` generates current dry-run deletion candidates.
