# Environment Variables Reference

## Provider Configs Support These Variables

### Organization Settings
- `ORG_NAME` - GitHub organization or user name
- `ORG_GITHUB_URL` - Full GitHub URL to organization
- `PROVIDER_NAME` - Cloud provider name (aws, google, azurerm, digitalocean)

### Version Settings
- `TERRAFORM_MIN_VERSION` - Minimum Terraform version required
- `TERRAFORM_RECOMMENDED_VERSION` - Recommended version constraint (e.g., "~> 1.10")
- `PROVIDER_MIN_VERSION` - Minimum provider version required
- `PROVIDER_RECOMMENDED_VERSION` - Recommended provider constraint

### Repository Settings
- `REPO_PATTERN` - Glob pattern to match repositories
- `EXCLUDE_REPOS` - Space-separated list of repos to skip
- `DEFAULT_BRANCH` - Default branch name (master/main)
- `CREATE_PR` - Create PR instead of direct commit (true/false)

### GitHub Actions
- `WORKFLOW_SHA` - SHA pin for shared workflows
- `SHARED_WORKFLOWS_REPO` - Repository containing shared workflows

### Features
- `USE_EMOJIS` - Use emojis in changelogs (true/false)
- `EMOJI_LEGEND` - Include emoji legend (true/false)
- `AUTO_TAG` - Automatically create tags (true/false)
- `TAG_PREFIX` - Prefix for tags (default: "v")
- `SEMANTIC_VERSIONING` - Use semantic versioning (true/false)

### Validation
- `RUN_TERRAFORM_VALIDATE` - Run terraform validate (true/false)
- `RUN_TERRAFORM_FMT` - Run terraform fmt check (true/false)
- `CHECK_WORKFLOWS` - Validate GitHub Actions (true/false)
- `RUN_TFLINT` - Run TFLint (true/false)
- `RUN_TFSEC` - Run TFSec security scanning (true/false)

### Notifications
- `NOTIFY_ON_COMPLETE` - Send notification on completion (true/false)
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications

## Runtime Variables

These can be set when running scripts:

- `COPILOT_CONFIG` - Path to config file to use
- `DRY_RUN` - Show what would happen without making changes
- `VERBOSE` - Enable verbose logging
- `SKIP_VALIDATION` - Skip validation steps
- `FORCE` - Force operation even with warnings

## Example Usage

```bash
# Use specific config
export COPILOT_CONFIG="terraform-ai-skills/config/aws.config"
./terraform-ai-skills/scripts/batch-provider-upgrade.sh

# Dry run mode
export DRY_RUN=true
./terraform-ai-skills/scripts/validate-all.sh

# Verbose output
export VERBOSE=true
./terraform-ai-skills/scripts/create-releases.sh

# Override specific settings
export TERRAFORM_MIN_VERSION="1.11.0"
export CREATE_PR=true
./terraform-ai-skills/scripts/batch-provider-upgrade.sh
```

## Config File Priority

1. Runtime environment variables (highest)
2. Provider-specific config file
3. Global config file
4. Script defaults (lowest)

## Provider-Specific Differences

### AWS Config
```bash
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.80.0"
# AWS provider uses 'aws' prefix
```

### GCP Config
```bash
PROVIDER_NAME="google"
PROVIDER_MIN_VERSION="6.20.0"
# GCP provider uses 'google' not 'gcp'
```

### Azure Config
```bash
PROVIDER_NAME="azurerm"
PROVIDER_MIN_VERSION="4.20.0"
# Azure provider uses 'azurerm' not 'azure'
ORG_NAME="terraform-az-modules"  # Different org!
```

### DigitalOcean Config
```bash
PROVIDER_NAME="digitalocean"
PROVIDER_MIN_VERSION="2.70.0"
ORG_NAME="terraform-do-modules"  # Different org!
```
