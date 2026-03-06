# Changelog

## [1.0.0] - 2026-03-03

### Added
- Initial release
- **Scenario A** — Build-from-source: GitHub Actions + GHCR workflow generation
- **Scenario B** — Proxy conflict: removes Caddy/Traefik/nginx-proxy, adds nginx-router with inline config
- **Scenario C** — Multi-service build: matrix GitHub Actions workflow for parallel image builds
- `references/xcloud-constraints.md` — full xCloud rules and architecture
- `references/scenario-build-source.md` — Scenario A deep-dive
- `references/scenario-proxy-conflict.md` — Scenario B deep-dive
- `references/scenario-multi-service-build.md` — Scenario C deep-dive (new)
- `examples/rybbit-analytics.md` — real-world Caddy + multi-port example
- `examples/custom-app-dockerfile.md` — real-world build-from-source example
- `examples/fullstack-monorepo.md` — real-world multi-service build example
- `assets/github-actions-build.yml` — reusable GitHub Actions template
- ClawHub + SkillsMP compatible packaging
- Works with OpenClaw, Claude Code, Claude.ai Projects, Cursor, Windsurf, any AI agent
