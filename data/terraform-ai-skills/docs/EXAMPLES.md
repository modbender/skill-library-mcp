# Real World Examples

## Example 1: CloudDrove DigitalOcean Modules (Current)

**Configuration:**
```bash
ORG_NAME="terraform-do-modules"
PROVIDER_NAME="digitalocean"
PROVIDER_MIN_VERSION="2.70.0"
TERRAFORM_MIN_VERSION="1.5.4"
REPO_PATTERN="terraform-digitalocean-*"
```

**What we did:**
- Upgraded 15 modules
- Fixed 6 workflows
- Created 15 releases
- Updated 35+ examples

**Command:**
```
@copilot follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

**Time:** 45 minutes (vs 5+ hours manually)

---

## Example 2: AWS Modules for Different Org

**Configuration:**
```bash
ORG_NAME="my-company"
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.30.0"
TERRAFORM_MIN_VERSION="1.5.0"
REPO_PATTERN="terraform-aws-*"
DEFAULT_BRANCH="main"
```

**Usage:**
```
@copilot upgrade all AWS provider versions to 5.30.0 using terraform-ai-skills/
```

---

## Example 3: Azure Modules

**Configuration:**
```bash
ORG_NAME="azure-modules"
PROVIDER_NAME="azurerm"
PROVIDER_MIN_VERSION="3.75.0"
TERRAFORM_MIN_VERSION="1.6.0"
REPO_PATTERN="terraform-azurerm-*"
```

**Usage:**
```
@copilot standardize workflows for all Azure modules using terraform-ai-skills/prompts/2-workflow-standardization.prompt
```

---

## Example 4: Google Cloud Modules

**Configuration:**
```bash
ORG_NAME="gcp-terraform"
PROVIDER_NAME="google"
PROVIDER_MIN_VERSION="5.0.0"
TERRAFORM_MIN_VERSION="1.5.4"
REPO_PATTERN="terraform-google-*"
```

---

## Example 5: Multi-Provider Setup

If you have multiple providers, create separate configs:

```bash
# terraform-ai-skills/config/aws.config
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.30.0"

# terraform-ai-skills/config/azure.config
PROVIDER_NAME="azurerm"
PROVIDER_MIN_VERSION="3.75.0"
```

Then specify:
```
@copilot use terraform-ai-skills/config/aws.config and upgrade all AWS modules
```

---

## Example 6: PR-Based Workflow

For organizations requiring PRs:

**Configuration:**
```bash
CREATE_PR=true
DEFAULT_BRANCH="main"
```

**Behavior:**
- Creates feature branch
- Makes all changes
- Opens PR instead of direct commit
- You review and merge

---

## Example 7: Kubernetes Provider

**Configuration:**
```bash
ORG_NAME="k8s-terraform"
PROVIDER_NAME="kubernetes"
PROVIDER_MIN_VERSION="2.20.0"
TERRAFORM_MIN_VERSION="1.5.0"
REPO_PATTERN="terraform-k8s-*"
```

---

## Example 8: Private Module Registry

**Configuration:**
```bash
ORG_NAME="mycompany"
PROVIDER_NAME="custom"
PROVIDER_MIN_VERSION="1.0.0"
TERRAFORM_MIN_VERSION="1.5.0"
REPO_PATTERN="tf-module-*"
```

---

## Example 9: Selective Updates

Update only specific modules:

```bash
# In config
REPO_PATTERN="terraform-aws-vpc|terraform-aws-subnet"
```

Or tell Copilot:
```
@copilot upgrade provider only in terraform-aws-vpc and terraform-aws-subnet using terraform-ai-skills/
```

---

## Example 10: Dry Run

Test what will happen:

```
@copilot show me what terraform-ai-skills/prompts/1-provider-upgrade.prompt will do but don't apply changes yet
```

---

## Common Customizations

### Custom Emoji Set
Edit prompts to use your preferred emojis:
```
- 🚀 Deploy
- 🔧 Config
- 📦 Dependencies
- ✨ Features
```

### Custom Changelog Format
Modify `scripts/create-releases.sh` to match your format.

### Custom Workflow Files
Update `prompts/2-workflow-standardization.prompt` with your workflow list.

### Custom Validation
Add your validation rules to `scripts/validate-all.sh`.

---

## Migration Guide

### From Manual Process

**Before (Manual):**
```
1. Open each repo
2. Edit versions.tf
3. Update examples
4. Run validation
5. Commit and push
6. Create release
7. Update changelog
   
Time: ~20 minutes per repo × 15 repos = 5 hours
```

**After (With Skills):**
```
@copilot follow terraform-ai-skills/prompts/4-full-maintenance.prompt

Time: 45 minutes for all repos! 🎉
```

### From Another Tool

Replace your scripts with these skills:
1. Copy your settings to `config/global.config`
2. Test with one repo
3. Run full maintenance
4. Retire old scripts

---

## Success Metrics

Track your improvements:

**Before Skills:**
- Time per maintenance cycle: 4-6 hours
- Human errors: 2-3 per cycle
- Consistency: Variable

**After Skills:**
- Time per maintenance cycle: 45 minutes
- Human errors: ~0 (automated)
- Consistency: 100%

**ROI:**
- Time saved per month: 15+ hours
- Error reduction: 95%
- Consistency: Perfect
