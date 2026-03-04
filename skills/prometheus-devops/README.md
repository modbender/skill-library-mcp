# Prometheus

Production Prometheus setup covering scrape configuration, service discovery, recording rules, alert rules, and operational best practices for infrastructure and application monitoring.

## What's Inside

- Core prometheus.yml configuration (scrape intervals, external labels, alertmanager)
- Service discovery methods (static, file-based, Kubernetes pods, Consul, EC2)
- Recording rules for pre-computing expensive queries
- Alert rules by category (availability, resources) with severity guide
- Kubernetes installation via Helm
- Naming conventions for metrics and recording rules
- Validation commands (promtool, config reload)
- Best practices (HA deployment, retention planning, federation, long-term storage)
- Troubleshooting quick reference
- Template files (prometheus.yml, alert-rules.yml, recording-rules.yml)

## When to Use

- Setting up metrics collection for new services
- Configuring service discovery (Kubernetes, file-based, static)
- Creating recording rules for dashboard performance
- Designing SLO-based alert rules
- Production deployment with HA and retention planning
- Troubleshooting scraping issues

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/devops/prometheus
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install prometheus
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/devops/prometheus .cursor/skills/prometheus
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/devops/prometheus ~/.cursor/skills/prometheus
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/devops/prometheus .claude/skills/prometheus
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/devops/prometheus ~/.claude/skills/prometheus
```

---

Part of the [DevOps](..) skill category.
