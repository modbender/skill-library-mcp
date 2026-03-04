# Quick Reference

## Common Commands

### Full Maintenance (Recommended)
```
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

### Provider Upgrade Only
```
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

### Single Repo Test
```
@copilot use terraform-ai-skills/config/aws.config and upgrade provider in terraform-aws-vpc only
```

### Workflow Fix Only
```
@copilot use terraform-ai-skills/config/gcp.config and follow terraform-ai-skills/prompts/2-workflow-standardization.prompt
```

### Release Creation Only
```
@copilot use terraform-ai-skills/config/azure.config and follow terraform-ai-skills/prompts/3-release-creation.prompt
```

---

## Prompts Reference

| File | Purpose | Typical Time |
|------|---------|-------------|
| `prompts/1-provider-upgrade.prompt` | Update provider + Terraform versions | 10–90 min |
| `prompts/2-workflow-standardization.prompt` | Standardize GitHub Actions | 15–30 min |
| `prompts/3-release-creation.prompt` | Create semantic releases + changelogs | 10–20 min |
| `prompts/4-full-maintenance.prompt` | All of the above in sequence ⭐ | 45–180 min |

---

## Provider → Config Mapping

| Cloud | Provider ID | Config file | Repo pattern |
|-------|-------------|-------------|-------------|
| AWS | `aws` | `config/aws.config` | `terraform-aws-*` |
| GCP | `google` | `config/gcp.config` | `terraform-gcp-*` |
| Azure | `azurerm` | `config/azure.config` | `terraform-azurerm-*` |
| DigitalOcean | `digitalocean` | `config/digitalocean.config` | `terraform-digitalocean-*` |

---

## Script Reference

```bash
# Batch provider upgrade
bash scripts/batch-provider-upgrade.sh

# Validate all modules
bash scripts/validate-all.sh

# Create releases
bash scripts/create-releases.sh

# Use specific provider config
COPILOT_CONFIG=config/gcp.config bash scripts/batch-provider-upgrade.sh
```

---

## Verification Commands

```bash
# Check what changed
git status
git diff

# Monitor CI
gh run list --limit 20

# Check releases created
gh release list

# Verify provider versions in a module
grep -r "version" terraform-YOUR-MODULE/versions.tf
```

---

## Common Patterns

### Test before bulk
```bash
# Always run on 1 repo first
@copilot use config/aws.config and upgrade provider in terraform-aws-vpc only
# Review result, then run full batch
```

### Dry run first
```bash
# In config file, set:
DRY_RUN=true
# Review output, then set DRY_RUN=false
```

### Protect critical repos
```bash
# In config file:
EXCLUDE_REPOS="terraform-aws-core terraform-aws-network terraform-aws-iam"
```
