# Real-World Examples

## Example 1: AWS Provider Upgrade (170 repos)

**Scenario:** CloudDrove needed to upgrade AWS provider from 5.70 → 5.80 across 170 modules.

**Config (`config/aws.config`):**
```bash
ORG_NAME="clouddrove"
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.80.0"
TERRAFORM_MIN_VERSION="1.10.0"
REPO_PATTERN="terraform-aws-*"
EXCLUDE_REPOS="terraform-aws-templates"
```

**Command:**
```
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

**Results:**
- 170 modules upgraded in 90 minutes (vs 56 hours manually)
- 0 validation errors
- 100% workflow pass rate

---

## Example 2: Full Maintenance — DigitalOcean (15 repos)

**Scenario:** Upgrade DO provider + standardize workflows + create releases in one pass.

**Config (`config/digitalocean.config`):**
```bash
ORG_NAME="terraform-do-modules"
PROVIDER_NAME="digitalocean"
PROVIDER_MIN_VERSION="2.70.0"
REPO_PATTERN="terraform-digitalocean-*"
```

**Command:**
```
@copilot use terraform-ai-skills/config/digitalocean.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

**Results:** 15 modules — upgraded, workflows fixed, 15 releases created in 45 minutes.

---

## Example 3: GCP Workflow Standardization

**Scenario:** Pin all GCP module workflows to SHA hashes after a supply chain security audit.

**Command:**
```
@copilot use terraform-ai-skills/config/gcp.config and follow terraform-ai-skills/prompts/2-workflow-standardization.prompt
```

---

## Example 4: Azure Bulk Release Creation

**Scenario:** Create v1.0.0 releases for all Azure modules after a major refactor.

**Config adjustment:**
```bash
SEMANTIC_VERSIONING=true
TAG_PREFIX="v"
USE_EMOJIS=true
```

**Command:**
```
@copilot use terraform-ai-skills/config/azure.config and follow terraform-ai-skills/prompts/3-release-creation.prompt
```

---

## Example 5: Custom Organization Setup

**Scenario:** A company with non-standard naming (`infra-aws-*`) and two separate orgs.

```bash
# config/custom-aws.config
ORG_NAME="my-company-infra"
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.80.0"
REPO_PATTERN="infra-aws-*"
EXCLUDE_REPOS="infra-aws-core infra-aws-shared"
DEFAULT_BRANCH="main"
CREATE_PR=true   # Require PR review
```

**Command:**
```
@copilot use terraform-ai-skills/config/custom-aws.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```
