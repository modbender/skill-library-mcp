---
name: circleci
description: "CircleCI CI/CD — manage pipelines, workflows, jobs, and insights via REST API"
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🔄", "requires": {"env": ["CIRCLECI_TOKEN"]}, "primaryEnv": "CIRCLECI_TOKEN", "homepage": "https://www.agxntsix.ai"}}
---

# 🔄 CircleCI

CircleCI CI/CD — manage pipelines, workflows, jobs, and insights via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `CIRCLECI_TOKEN` | ✅ | Personal API token from circleci.com |

## Quick Start

```bash
# Get current user
python3 {{baseDir}}/scripts/circleci.py me

# List pipelines
python3 {{baseDir}}/scripts/circleci.py pipelines slug <value> --branch <value>

# Get pipeline
python3 {{baseDir}}/scripts/circleci.py pipeline-get id <value>

# Trigger pipeline
python3 {{baseDir}}/scripts/circleci.py pipeline-trigger slug <value> --branch <value> --parameters <value>

# Get pipeline config
python3 {{baseDir}}/scripts/circleci.py pipeline-config id <value>

# List workflows
python3 {{baseDir}}/scripts/circleci.py workflows id <value>

# Get workflow
python3 {{baseDir}}/scripts/circleci.py workflow-get id <value>

# Cancel workflow
python3 {{baseDir}}/scripts/circleci.py workflow-cancel id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `me` | Get current user |
| `pipelines` | List pipelines |
| `pipeline-get` | Get pipeline |
| `pipeline-trigger` | Trigger pipeline |
| `pipeline-config` | Get pipeline config |
| `workflows` | List workflows |
| `workflow-get` | Get workflow |
| `workflow-cancel` | Cancel workflow |
| `workflow-rerun` | Rerun workflow |
| `jobs` | List workflow jobs |
| `job-get` | Get job details |
| `job-cancel` | Cancel job |
| `job-artifacts` | List job artifacts |
| `insights-workflows` | Workflow insights |
| `contexts` | List contexts |
| `envvars` | List project env vars |
| `envvar-set` | Set env var |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/circleci.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/circleci.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
