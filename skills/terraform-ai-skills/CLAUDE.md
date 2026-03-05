# CLAUDE.md — Skill Development Guide

This file describes how to develop, test, and contribute to the `terraform-ai-skills` skill for Claude Code and other AI assistants.

## What This Skill Does

`terraform-ai-skills` is an AI skill that automates bulk Terraform module maintenance across AWS, GCP, Azure, and DigitalOcean organizations. It is activated when a user needs to manage Terraform modules at scale — not for single-project work.

## Skill Architecture

```
terraform-ai-skills/
├── SKILL.md                    # Primary skill manifest (ClawHub + OpenClaw)
├── CLAUDE.md                   # This file — Claude Code skill guide
├── claw.json                   # Machine-readable manifest
├── config/                     # Per-provider configuration files
│   ├── aws.config
│   ├── gcp.config
│   ├── azure.config
│   ├── digitalocean.config
│   └── global.config
├── prompts/                    # AI workflow prompt files
│   ├── 1-provider-upgrade.prompt
│   ├── 2-workflow-standardization.prompt
│   ├── 3-release-creation.prompt
│   └── 4-full-maintenance.prompt
├── scripts/                    # Bash automation scripts
│   ├── batch-provider-upgrade.sh
│   ├── create-releases.sh
│   └── validate-all.sh
├── references/                 # Detailed reference guides
│   ├── provider-configs.md
│   ├── safety.md
│   ├── examples.md
│   └── quick-reference.md
└── tests/
    └── test-configs.sh
```

## How Claude Should Use This Skill

### Activation Triggers

Activate this skill when the user mentions:
- "upgrade provider" / "update terraform" across multiple repos
- "standardize workflows" / "fix GitHub Actions" at scale
- "create releases" for multiple modules
- "full maintenance" / "bulk update" of terraform modules
- Managing 10+ terraform module repositories

### Workflow Pattern

1. **Identify the cloud provider** → select the appropriate `config/*.config`
2. **Confirm scope** → single repo test first, then bulk
3. **Select prompt** → match to the user's goal
4. **Execute safely** → always validate before bulk operations

### Example Responses

**User:** "I need to upgrade the AWS provider to 5.80 across all my modules"
```
I'll use terraform-ai-skills to handle that. First, let me test on one repo:

@copilot use terraform-ai-skills/config/aws.config and upgrade provider in YOUR-FIRST-MODULE only, following terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

**User:** "Do full maintenance on all our GCP modules"
```
@copilot use terraform-ai-skills/config/gcp.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

## Content Philosophy

- **Progressive disclosure** — SKILL.md contains the essentials; detailed guides live in `references/`
- **Safety first** — always surface the test-one-repo-first pattern before bulk operations
- **Config-driven** — all organization-specific settings belong in `config/*.config`, never hardcoded

## Adding New Skills

1. Create a new prompt file in `prompts/` following the existing naming convention
2. Update the skills table in `SKILL.md`
3. Add a reference guide in `references/` if the skill has complex options
4. Update `claw.json` version (semver bump)
5. Run `tests/test-configs.sh` to validate config files

## Testing

```bash
# Validate all config files
bash tests/test-configs.sh

# Test a single prompt manually
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/1-provider-upgrade.prompt for terraform-aws-vpc only
```

## Versioning

Releases follow [Conventional Commits](https://www.conventionalcommits.org/):

| Commit type | Version bump |
|-------------|--------------|
| `feat!:` / `BREAKING CHANGE:` | Major |
| `feat:` | Minor |
| `fix:` / `docs:` / other | Patch |

Releases are automated via `.github/workflows/release.yml` on `v*.*.*` tags.

## Related Resources

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill) — Terraform skill for Claude (inspiration)
- [pre-commit-terraform](https://github.com/antonbabenko/pre-commit-terraform)
- [terraform-docs](https://terraform-docs.io/)
