# Changelog

## 1.2.1 (unreleased)

### Removed
- **`scripts/render-pattern.sh`** — Browser-based renderer using Puppeteer with `--no-sandbox`. Superseded by `src/runtime/offline-render-v2.mjs` which runs entirely in Node.js with frozen `process.env` and blocked `child_process`. Retrievable from git history at commit prior to this removal.
- **`scripts/stream-to-vc.sh`** — Legacy VC streaming wrapper. Superseded by `scripts/vc-play.mjs`.
- **`scripts/repl-capture.mjs`** — Puppeteer-based REPL capture utility with `--no-sandbox`. No longer needed — offline rendering handles all use cases.
- **`src/runtime/render.mjs`** — V1 local renderer using `vm.runInNewContext`. Superseded by `offline-render-v2.mjs` which uses stronger sandboxing. Retrievable from git history.

### Why
ClaHub security scanner flagged these deprecated scripts as suspicious due to Puppeteer `--no-sandbox` and `vm.runInNewContext` usage. All functionality is covered by the active renderer (`offline-render-v2.mjs`) which implements proper security hardening. Removing dead code from the bundle moves the skill from "suspicious" to "benign" in scanner classification.

## 1.2.0

### Added
- `references/composing.md` — Dream-to-composition methodology (Ronan 🌊)
- `references/gain-calibration.md` — Sample gain ranges and the 300× lesson (Cael 🩸 / Elliott 🌻)
- `references/rendering.md` — Pipeline documentation (Cael 🩸)
- `references/spectral-validation.md` — QA and spectral analysis (Silas 🌫️)
- SKILL.md cold-start guide and quickstart section (Elliott 🌻 / Cael 🩸)
