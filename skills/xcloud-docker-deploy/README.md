# xCloud Docker Deploy Skill

[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-Asif2BD%2Fxcloud--docker--deploy-blue.svg)](https://clawhub.ai/Asif2BD/xcloud-docker-deploy)
[![xCloud](https://img.shields.io/badge/platform-xcloud.host-orange.svg)](https://xcloud.host)

**Paste any `docker-compose.yml`. Get a version that deploys on [xCloud](https://xcloud.host) in minutes.**

---

## What It Does

| Scenario | Signal | Fix |
|----------|--------|-----|
| **Build-from-source** | `build: context: .` in compose | Generates GitHub Actions → builds → pushes to GHCR; replaces `build:` with `image: ghcr.io/...` |
| **Proxy conflict** | Caddy/Traefik/nginx-proxy service | Removes it, adds embedded `nginx-router` with inline config, single port |
| **Multi-port** | Multiple `ports:` on different services | Routes through `nginx-router`, single exposed port for xCloud |
| **External config** | `./nginx.conf:/etc/nginx/...` | Embeds config inline via `configs:` block |
| **Multi-service build** | Multiple services with `build:` | Matrix GitHub Actions workflow, each service gets its own GHCR image |

---

## Install

### OpenClaw (recommended)
```bash
clawhub install Asif2BD/xcloud-docker-deploy
```

### Claude Code (CLI)
```bash
# Download and place in Claude skills directory
curl -L https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill/releases/latest/download/xcloud-docker-deploy.skill \
  -o ~/.claude/skills/xcloud-docker-deploy.skill
```

### Claude.ai (Projects)
Download [xcloud-docker-deploy.skill](https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill/releases/latest/download/xcloud-docker-deploy.skill) and upload to your Claude Project files.

### Cursor / Windsurf / Any AI Agent
Drop `xcloud-docker-deploy.skill` into the agent's skills or workspace folder.

### Manual (any platform)
```bash
git clone https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill.git
# Reference SKILL.md and the references/ folder in your agent's context
```

---

## How to Use

Once installed, just paste your `docker-compose.yml` and say:

> "Make this work on xCloud"

or

> "Adapt this docker-compose.yml for xCloud deployment"

The skill detects which scenarios apply and produces:
- A complete, copy-paste-ready modified `docker-compose.yml`
- GitHub Actions workflow (if build-from-source)
- `.env.example` with all required variables
- Step-by-step xCloud deploy instructions

---

## File Structure

```
xcloud-docker-deploy/
├── SKILL.md                          # Agent instructions (load this)
├── README.md                         # This file
├── SECURITY.md                       # Security disclosure
├── CHANGELOG.md                      # Version history
├── LICENSE                           # Apache 2.0
├── assets/
│   └── github-actions-build.yml      # GitHub Actions template
├── references/
│   ├── xcloud-constraints.md         # xCloud rules & architecture
│   ├── scenario-build-source.md      # Scenario A deep-dive
│   ├── scenario-proxy-conflict.md    # Scenario B deep-dive
│   └── scenario-multi-service-build.md  # Scenario C deep-dive
└── examples/
    ├── rybbit-analytics.md           # Real-world: Caddy + multi-port
    ├── custom-app-dockerfile.md      # Real-world: build-from-source
    └── fullstack-monorepo.md         # Real-world: multi-service build
```

---

## Compatibility

| Platform | Support |
|----------|---------|
| OpenClaw | ✅ Native `.skill` install via ClawHub |
| Claude Code (CLI) | ✅ Drop `.skill` file in skills dir |
| Claude.ai Projects | ✅ Upload `.skill` to Project files |
| Cursor | ✅ Add to project context |
| Windsurf | ✅ Add to project context |
| Any LLM agent | ✅ Reference `SKILL.md` directly |

---

## Author

Built by **M Asif Rahman** ([@Asif2BD](https://github.com/Asif2BD)) — founder of [xCloud.host](https://xcloud.host) and [MissionDeck.ai](https://missiondeck.ai).

- GitHub: [Asif2BD/xCloud-Docker-Deploy-Skill](https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill)
- ClawHub: [clawhub.ai/Asif2BD/xcloud-docker-deploy](https://clawhub.ai/Asif2BD/xcloud-docker-deploy)

---

## License

Apache 2.0 — free to use, modify, and distribute.
