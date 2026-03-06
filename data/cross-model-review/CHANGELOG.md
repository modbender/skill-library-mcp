# Changelog

## [1.0.1] - 2026-02-21

### Fixed
- **`--max-rounds` implemented**: `init` now accepts `--max-rounds <n>` (default: 5); stored in `meta.json`
- **`--token-budget` implemented**: `init` now accepts `--token-budget <n>` (default: 8000); stored in `meta.json` (no chunking yet — stored for future use)
- **Removed unused imports**: Removed `os` and top-level `execSync` from `review.js`; `execSync` is no longer used anywhere (TTY confirmation replaced)
- **TTY confirmation fixed**: `execSync('read ...')` replaced with synchronous `readLineSync()` using `fs.readSync` on fd 0 — no shell subprocess needed
- **Intra-batch dedup**: `parse-round` now checks each new issue against other new issues in the same batch (not just prior open issues), detecting duplicates submitted by the reviewer in a single round
- **Stricter unknown family handling**: If both models resolve to `'unknown'` family, warn but allow. If one resolves to `'unknown'`, warn but allow. Only hard-fail when both families are known and equal.

### Documentation
- **SKILL.md**: Corrected verdict source (read from `meta.json` or `parse-round` stdout, NOT `issues.json`); clarified exact shape of `{prior_issues_json}`; added fallback path for reviewer timeout; added file path quoting guidance
- **README.md**: Added Prerequisites section (Node.js >=18, OpenClaw); added complete end-to-end CLI transcript; added Troubleshooting section; added CI badge; added "Why not single-model review?" section; added "When NOT to use" section near top; fixed claims about unimplemented features

### New Files
- `SECURITY.md`: Threat model, prompt injection mitigations, known limitations, safe usage guidance, responsible disclosure contact
- `.github/workflows/ci.yml`: GitHub Actions CI running tests on Node.js 18, 20, 22
- `.editorconfig`: Consistent formatting config for editors

### Tests
- Added: `--max-rounds` and `--token-budget` stored in `meta.json`
- Added: force-approve with `--ci-force` in non-TTY mode
- Added: `--ci-force` without `--override-reason` correctly rejected
- Added: unknown model family (both unknown, one unknown) warns but allows
- Added: intra-batch dedup detection
- Added: verdict stored in `meta.json` after finalize
- Total: 55 tests (up from 36)

---

## [1.0.0] - 2026-02-21

### Added
- Agent-orchestrated adversarial review loop (reviewer spawned via sessions_spawn, agent revises)
- `review.js` helper script with 4 subcommands: init, parse-round, finalize, status
- Stable issue tracking with lifecycle (ISS-NNN IDs, status transitions across rounds)
- Jaccard similarity dedup detection (0.6 threshold) to prevent semantic drift
- Fail-closed gating: exit codes 0 (approved), 1 (revise), 2 (error)
- Cross-model enforcement: rejects same provider family for reviewer and planner
- Force-approve with TTY confirmation, mandatory reason, and audit logging
- `--ci-force` flag for non-interactive environments (requires `--override-reason`)
- Prompt injection mitigation via UNTRUSTED content delimiters
- Token budget support for codebase context (`--token-budget`)
- Per-run isolated workspaces (`tasks/reviews/<timestamp>-<uuid>/`)
- Reviewer prompt template with structured JSON-only output format
- ClawHub-ready README with integration guide

### Security
- Reviewer and planner prompts sandboxed with instruction-level tool restriction
- Plan content wrapped in explicit UNTRUSTED delimiters
- Force-approve requires human confirmation and is audit-logged
