# Copilot Skills - Provider Selection Guide

## How to Select the Right Config

When working with Copilot, specify which cloud provider config to use:

### AWS Modules (clouddrove/terraform-aws-*)
```bash
@copilot use terraform-multicloud-skills/config/aws.config and [your task]
```

### GCP Modules (clouddrove/terraform-gcp-*)
```bash
@copilot use terraform-multicloud-skills/config/gcp.config and [your task]
```

### Azure Modules (terraform-az-modules/terraform-azurerm-*)
```bash
@copilot use terraform-multicloud-skills/config/azure.config and [your task]
```

### DigitalOcean Modules (terraform-do-modules/terraform-digitalocean-*)
```bash
@copilot use terraform-multicloud-skills/config/digitalocean.config and [your task]
```

## Full Example Commands

### Upgrade AWS Modules
```bash
@copilot use config from terraform-multicloud-skills/config/aws.config and follow terraform-multicloud-skills/prompts/4-full-maintenance.prompt
```

### Quick Provider Update (Azure)
```bash
@copilot use terraform-multicloud-skills/config/azure.config and upgrade provider versions in all matching repos
```

### Fix GCP Workflows Only
```bash
@copilot use terraform-multicloud-skills/config/gcp.config and follow terraform-multicloud-skills/prompts/2-workflow-standardization.prompt
```

## Script Usage with Configs

Scripts automatically load the correct config when run from provider-specific directories:

```bash
# Option 1: Set config environment variable
export COPILOT_CONFIG="terraform-multicloud-skills/config/aws.config"
./terraform-multicloud-skills/scripts/batch-provider-upgrade.sh

# Option 2: Pass as argument (if script supports it)
./terraform-multicloud-skills/scripts/batch-provider-upgrade.sh --config=aws

# Option 3: Modify script's CONFIG_FILE path
```

## Quick Reference Matrix

| Provider | Org | Pattern | Min Version |
|----------|-----|---------|-------------|
| AWS | clouddrove | terraform-aws-* | 5.80.0 |
| GCP | clouddrove | terraform-gcp-* | 6.20.0 |
| Azure | terraform-az-modules | terraform-azurerm-* | 4.20.0 |
| DO | terraform-do-modules | terraform-digitalocean-* | 2.70.0 |

All use Terraform 1.10.0+
