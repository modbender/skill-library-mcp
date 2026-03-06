# AWS Provider Upgrade Example

This example demonstrates upgrading AWS provider across 10 modules.

## Prerequisites

- GitHub Copilot CLI or compatible AI assistant
- Access to github.com/anmolnagpal/terraform-aws-* repositories
- Git configured with push access

## Usage

### Step 1: Test on One Repository

```bash
@copilot use terraform-ai-skills/config/aws.config and upgrade provider in terraform-aws-vpc only
```

### Step 2: Run on Batch

```bash
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

## Expected Results

- All 10 modules updated to AWS Provider 5.80.0+
- Terraform updated to 1.10.0+
- All examples validated
- Commits created with emoji format

## Time: ~30 minutes for 10 modules

## Verification

```bash
# Check versions
for repo in terraform-aws-*; do
  echo "$repo:"
  grep 'required_version' "$repo/versions.tf"
done
```
