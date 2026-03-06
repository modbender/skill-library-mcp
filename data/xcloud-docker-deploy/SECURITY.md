# Security Policy — xCloud Docker Deploy Skill

## Overview

This skill contains **no executable scripts**. It is a pure documentation and instruction set that guides AI agents to transform `docker-compose.yml` files for xCloud deployment.

## What This Skill Contains

| File | Type | Network Access | Code Execution |
|------|------|----------------|----------------|
| `SKILL.md` | Instructions | None | None |
| `references/*.md` | Reference docs | None | None |
| `assets/github-actions-build.yml` | Template (YAML) | None — template only | None |
| `examples/*.md` | Example docs | None | None |

## What This Skill Does NOT Do

- No scripts, binaries, or executables
- No network requests of any kind
- No file system modifications
- No subprocess calls
- No data collection or telemetry

## Generated Output Security

The skill guides AI agents to generate:

1. **Modified `docker-compose.yml`** — removes `build:` directives and proxy services. No security-sensitive changes.
2. **GitHub Actions workflow** — uses `GITHUB_TOKEN` (scoped to the repository, no extra permissions). The `packages: write` permission is required only to push to GHCR.
3. **`.env.example`** — lists variable names only, no values. Never hardcodes secrets.

## Reporting Vulnerabilities

If you find a security issue with this skill or its generated output, open an issue at:
https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill/issues

## Provenance

- Source: https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill
- ClawHub: https://clawhub.ai/Asif2BD/xcloud-docker-deploy
- Author: M Asif Rahman / Asif2BD
- Audited by: Oracle (Matrix Zion) — 2026-03-03
