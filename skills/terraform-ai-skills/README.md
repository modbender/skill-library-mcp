# Terraform AI Skills — Multi-Cloud Module Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Terraform](https://img.shields.io/badge/Terraform-1.10+-623CE4?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-5.80+-FF9900?logo=amazon-aws)](https://registry.terraform.io/providers/hashicorp/aws)
[![GCP](https://img.shields.io/badge/GCP-6.20+-4285F4?logo=google-cloud)](https://registry.terraform.io/providers/hashicorp/google)
[![Azure](https://img.shields.io/badge/Azure-4.20+-0078D4?logo=microsoft-azure)](https://registry.terraform.io/providers/hashicorp/azurerm)
[![DigitalOcean](https://img.shields.io/badge/DO-2.70+-0080FF?logo=digitalocean)](https://registry.terraform.io/providers/digitalocean/digitalocean)

> Transform 56 hours of Terraform module maintenance into 90 minutes with AI automation.

AI-powered skill for GitHub Copilot, Claude, and ChatGPT that automates bulk Terraform module management across AWS, GCP, Azure, and DigitalOcean. Proven across 170+ modules with 97% time savings.

## Quick Start

```bash
# 1. Test on one repo first (always)
@copilot use terraform-ai-skills/config/aws.config and upgrade provider in YOUR-MODULE only

# 2. Run full automation
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

## Available Skills

| Skill | Command | Time |
|-------|---------|------|
| **Full Maintenance** ⭐ | `prompts/4-full-maintenance.prompt` | 45–180 min |
| Provider Upgrade | `prompts/1-provider-upgrade.prompt` | 10–90 min |
| Workflow Standardization | `prompts/2-workflow-standardization.prompt` | 15–30 min |
| Release Creation | `prompts/3-release-creation.prompt` | 10–20 min |

## Multi-Cloud Support

| Provider | Config | Terraform | Min Provider |
|----------|--------|-----------|-------------|
| AWS | `config/aws.config` | 1.10.0+ | 5.80.0+ |
| GCP | `config/gcp.config` | 1.10.0+ | 6.20.0+ |
| Azure | `config/azure.config` | 1.10.0+ | 4.20.0+ |
| DigitalOcean | `config/digitalocean.config` | 1.10.0+ | 2.70.0+ |

## Proven Results

| Operation | Manual | With Skills | Savings |
|-----------|--------|-------------|---------|
| Provider upgrade (170 repos) | 56 hours | 90 min | **97%** ⬇️ |
| Workflow standardization | 20 hours | 30 min | **97%** ⬇️ |
| Full maintenance cycle | 86 hours | 2–3 hours | **97%** ⬇️ |

## Installation

```bash
# Claude Code
/plugin install terraform-ai-skills@anmolnagpal

# Manual
git clone https://github.com/anmolnagpal/terraform-ai-skills ~/.claude/skills/terraform-ai-skills
```

## Requirements

- Terraform 1.10.0+ · Git 2.30+ · Bash 4.0+
- GitHub Copilot CLI, Claude, ChatGPT, or Cursor
- `gh` CLI _(optional)_ · TFLint / TFSec / Trivy _(optional)_

## Documentation

| Guide | Purpose |
|-------|---------|
| [SKILL.md](SKILL.md) | Skill manifest & usage |
| [CLAUDE.md](CLAUDE.md) | Claude Code integration guide |
| [references/safety.md](references/safety.md) ⚠️ | Rollback & safety procedures |
| [references/provider-configs.md](references/provider-configs.md) | Config options reference |
| [references/examples.md](references/examples.md) | Real-world case studies |
| [references/quick-reference.md](references/quick-reference.md) | Command cheat sheet |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Customization guide |

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).
[Report Bug](https://github.com/anmolnagpal/terraform-ai-skills/issues/new) · [Request Feature](https://github.com/anmolnagpal/terraform-ai-skills/discussions)

## Related

- [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill) — Terraform skill for Claude
- [terraform-best-practices.com](https://www.terraform-best-practices.com/)
- [pre-commit-terraform](https://github.com/antonbabenko/pre-commit-terraform)

## License

MIT © 2026 [Anmol Nagpal](https://github.com/anmolnagpal)
