# Changelog

## [0.1.0] - 2026-03-02

### Initial Release
- 5-phase post-upgrade verification system
- MODEL_GROUND_TRUTH.md template with YAML-formatted config/cron/model declarations
- Auto-repair for config drift (Phase 1) and cron drift (Phase 3)
- LLM provider liveness via `sessions_spawn` (tests real routing path)
- Non-LLM provider liveness via env-injected curl
- Channel liveness with cross-context WhatsApp workaround
- UPGRADE_SOP.md for standardized upgrade procedure
- AGENTS.md GROUND_TRUTH sync rule snippet
