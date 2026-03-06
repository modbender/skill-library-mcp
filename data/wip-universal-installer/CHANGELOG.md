# Changelog







## 2.1.5 (2026-02-21)

Update description to reflect Universal Interface spec purpose

## 2.1.4 (2026-02-21)

Add one-liner to README: what it does and teaches your AI too

## 2.1.3 (2026-02-21)

Fix npm bin entry: rename install.mjs to install.js so npx wip-install works globally

## 2.1.2 (2026-02-21)

Move detailed content to REFERENCE.md. README keeps Problem, Karpathy, Install prompt.

## 2.1.1 (2026-02-21)

Add Universal Interface badges, agent-driven install prompt, fix description

## 2.1.0 (2026-02-21)

Rename Six Doors to Universal Interface. Update all code and docs.

## 2.0.0 (2026-02-20)

Major refactor. Reframed from "WIP Computer installer" to "the spec for agent-native software."

### Added
- `detect.mjs` ... importable door detection module
- `SPEC.md` ... formal Six Doors specification
- `--dry-run` flag ... detect doors without installing
- `--json` flag ... machine-readable detection output
- `LICENSE` (MIT)
- `SKILL.md` with agent instructions
- `examples/minimal/` ... minimal six-door template

### Changed
- README rewritten around Karpathy's sensor/actuator argument
- `install.mjs` now imports detection logic from `detect.mjs`
- Package name updated: `@wipcomputer/universal-installer`

## 1.0.0 (2026-02-17)

Initial release. Universal installer for WIP.computer repos.

- Detects 6 door types: CLI, Module, MCP, OpenClaw, Skill, CC Hook
- Installs from GitHub URL, org/repo shorthand, or local path
- Supports any WIP.computer convention repo
