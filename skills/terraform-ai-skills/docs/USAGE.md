# Usage Guide for Copilot Skills

## Quick Start

### 1. Configure for Your Organization

Edit `config/global.config`:

```bash
# Update these for your org
ORG_NAME="your-org-name"
PROVIDER_NAME="aws"  # or "azure", "gcp", etc.
TERRAFORM_MIN_VERSION="1.5.4"
PROVIDER_MIN_VERSION="5.0.0"
```

### 2. Using Prompts with Copilot

#### Option A: Copy-Paste Method
1. Open a prompt file (e.g., `prompts/1-provider-upgrade.prompt`)
2. Copy the prompt text
3. Paste into GitHub Copilot CLI
4. Variables like `${PROVIDER_MIN_VERSION}` will be read from config

#### Option B: Reference Method
Simply tell Copilot:
```
@copilot follow the instructions in terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

### 3. Using Scripts Directly

Make scripts executable:
```bash
chmod +x terraform-ai-skills/scripts/*.sh
```

Run a script:
```bash
./terraform-ai-skills/scripts/batch-provider-upgrade.sh
```

## Common Workflows

### Workflow 1: Provider Upgrade Only
```
1. Use prompt: 1-provider-upgrade.prompt
2. Copilot will update all versions
3. Validate with: validate-all.sh
```

### Workflow 2: Fix Failing GitHub Actions
```
1. Use prompt: 2-workflow-standardization.prompt
2. Copilot will fix workflows
3. Check GitHub Actions status
```

### Workflow 3: Create Releases
```
1. Use prompt: 3-release-creation.prompt
2. Or run: create-releases.sh
3. Check releases on GitHub
```

### Workflow 4: Full Maintenance (Recommended)
```
1. Use prompt: 4-full-maintenance.prompt
2. Copilot will do everything end-to-end
3. Review final summary report
```

## Tips for Best Results

### 1. Always Configure First
Update `config/global.config` before running any operations.

### 2. Test on One Repo First
For new operations, test on a single repo:
```
@copilot upgrade provider in terraform-aws-vpc only, following the pattern in terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

### 3. Use Checkpoints
After major phases, ask Copilot to create a checkpoint:
```
@copilot create a checkpoint now before we proceed to releases
```

### 4. Review Before Push
Always review changes before pushing:
```bash
git diff HEAD~1
```

### 5. Incremental Approach
For large changes, break into phases:
- Day 1: Provider upgrades
- Day 2: Workflow fixes
- Day 3: Releases

## Customization

### For Different Providers

**AWS:**
```bash
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.0.0"
```

**Azure:**
```bash
PROVIDER_NAME="azurerm"
PROVIDER_MIN_VERSION="3.50.0"
```

**GCP:**
```bash
PROVIDER_NAME="google"
PROVIDER_MIN_VERSION="5.0.0"
```

### For Different Repo Structures

If your repos are named differently:
```bash
REPO_PATTERN="myorg-terraform-*"
```

If you use `main` instead of `master`:
```bash
DEFAULT_BRANCH="main"
```

### For PR-Based Workflow

Instead of direct commits:
```bash
CREATE_PR=true
```

## Troubleshooting

### Issue: Script can't find config
**Solution:** Run scripts from the parent directory:
```bash
cd /path/to/terraform-modules
./terraform-ai-skills/scripts/batch-provider-upgrade.sh
```

### Issue: Copilot doesn't use variables
**Solution:** Explicitly mention the config:
```
@copilot use the configuration from terraform-ai-skills/config/global.config and upgrade all providers
```

### Issue: Some repos skipped
**Solution:** Check EXCLUDE_REPOS in config

### Issue: Validation fails
**Solution:** Run validate script to see details:
```bash
./terraform-ai-skills/scripts/validate-all.sh
```

## Examples for Other Organizations

### Example 1: Cloudposse Modules
```bash
ORG_NAME="cloudposse"
REPO_PATTERN="terraform-aws-*"
PROVIDER_NAME="aws"
```

### Example 2: Azure Modules
```bash
ORG_NAME="Azure"
REPO_PATTERN="terraform-azurerm-*"
PROVIDER_NAME="azurerm"
```

### Example 3: Community Modules
```bash
ORG_NAME="terraform-community-modules"
REPO_PATTERN="tf-*"
PROVIDER_NAME="aws"
```

## Integration with CI/CD

You can run these scripts in CI/CD:

```yaml
# .github/workflows/monthly-maintenance.yml
name: Monthly Maintenance
on:
  schedule:
    - cron: '0 0 1 * *'  # First day of month
  workflow_dispatch:

jobs:
  maintenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run validation
        run: ./terraform-ai-skills/scripts/validate-all.sh
```

## Support

For issues or improvements:
1. Check TROUBLESHOOTING section above
2. Review the prompt files for examples
3. Modify scripts for your specific needs
4. All scripts are bash - easy to customize!
