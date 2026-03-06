## 1.2.31
- Security: Hardened voice command routing to avoid argument/command injection (no string splitting; suspicious metacharacters rejected; captured text passed as single args).
- Docs: Updated SKILL.md description and diagrams.

# Changelog — Proactive Claw

## 1.2.30
- Security hardening: default autonomy is **confirm** even when config is missing (fail-closed defaults).
- Updated SKILL.md: clearer proactive loop (calendar ⇄ engine ⇄ chat), stronger scenarios, and local-first positioning.

## 1.2.29
- Safe defaults: `config_wizard.py --defaults` generates `max_autonomy_level=confirm`.
- Autonomous mode requires explicit opt-in with `--i-accept-risk`.
