---
name: terraform-ai-skills
description: Use when bulk-managing Terraform modules at scale — upgrading providers across AWS, GCP, Azure, or DigitalOcean repositories, standardizing GitHub Actions workflows, automating semantic releases, running security scans, or performing end-to-end maintenance cycles across 10–200+ module repositories
version: 0.0.2
metadata:
  openclaw:
    requires:
      bins:
        - terraform
        - git
        - bash
      bins_optional:
        - gh
        - tflint
        - tfsec
        - trivy
        - checkov
    os:
      - linux
      - macos
    homepage: https://github.com/anmolnagpal/terraform-ai-skills
    tags:
      - terraform
      - multi-cloud
      - aws
      - gcp
      - azure
      - digitalocean
      - infrastructure-as-code
      - devops
      - automation
      - ci-cd
      - github-copilot
    license: MIT
    author: Anmol Nagpal
---

# Terraform AI Skills — Multi-Cloud Module Management

AI-powered automation for managing Terraform modules at scale across AWS, GCP, Azure, and DigitalOcean. Transforms 56 hours of manual maintenance into 90 minutes.

## When to Use

**Activate this skill when:**
- Upgrading provider versions across 10–200+ module repositories
- Standardizing GitHub Actions workflows across an organization
- Creating semantic versioned releases with automated changelogs
- Performing bulk validation (TFLint, TFSec, Trivy, Checkov)
- Running a complete end-to-end maintenance cycle

**Don't use for:**
- Single Terraform project maintenance
- Writing individual Terraform configurations
- Provider-specific API questions

## Available Skills

### Full Maintenance ⚡ _(Recommended)_
```
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```
Discovery → Provider upgrades → Workflow fixes → Validation → Releases  
**Time:** 45–180 min

### Provider Upgrade 🔄
```
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/1-provider-upgrade.prompt
```
Updates provider constraints, Terraform versions, examples, runs validation.  
**Time:** 10–90 min

### Workflow Standardization 🔧
```
@copilot use terraform-ai-skills/config/gcp.config and follow terraform-ai-skills/prompts/2-workflow-standardization.prompt
```
Pins GitHub Actions to SHAs, removes deprecated actions.  
**Time:** 15–30 min

### Release Creation 🚀
```
@copilot use terraform-ai-skills/config/azure.config and follow terraform-ai-skills/prompts/3-release-creation.prompt
```
Generates changelogs, semantic version tags, GitHub releases.  
**Time:** 10–20 min

## Quick Start

```bash
# 1. Always test on ONE repo first
@copilot use terraform-ai-skills/config/aws.config and upgrade provider in terraform-aws-vpc only

# 2. If successful, run full maintenance
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt

# 3. Verify
git status && gh run list && gh release list
```

## Cloud Provider Support

| Provider     | Config file                   | Terraform | Min Provider |
|--------------|-------------------------------|-----------|--------------|
| AWS          | `config/aws.config`           | 1.10.0+   | 5.80.0+      |
| GCP          | `config/gcp.config`           | 1.10.0+   | 6.20.0+      |
| Azure        | `config/azure.config`         | 1.10.0+   | 4.20.0+      |
| DigitalOcean | `config/digitalocean.config`  | 1.10.0+   | 2.70.0+      |

## Proven Results

| Operation        | Manual (170 repos) | With Skills | Savings |
|------------------|--------------------|-------------|---------|
| Provider upgrade | 56 hours           | 90 minutes  | 97% ⬇️  |
| Workflow fixes   | 20 hours           | 30 minutes  | 97% ⬇️  |
| Full maintenance | 86 hours           | 2–3 hours   | 97% ⬇️  |

## Requirements

- **Terraform** 1.10.0+ · **Git** 2.30+ · **Bash** 4.0+
- **AI assistant:** GitHub Copilot CLI, Claude, ChatGPT, or Cursor
- `gh` CLI _(optional — recommended for releases)_
- TFLint / TFSec / Trivy / Checkov _(optional — enhanced validation)_

## Detailed Reference Guides

For deeper guidance on specific topics:

- **[Provider Configs](references/provider-configs.md)** — Per-cloud config options, customization, env vars
- **[Safety & Rollback](references/safety.md)** — Pre-flight checklist, rollback procedures, emergency recovery
- **[Real-World Examples](references/examples.md)** — Case studies across AWS, GCP, Azure, DigitalOcean
- **[Quick Reference](references/quick-reference.md)** — Command cheat sheet, prompts guide, common patterns

## License

MIT © 2026 Anmol Nagpal
