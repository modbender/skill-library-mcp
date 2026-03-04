# Configuration Files

Provider-specific configuration files for Terraform AI Skills.

## 🔧 How to Configure

### Quick Start

1. **Choose your provider** (aws, gcp, azure, digitalocean)
2. **Edit the config file** for your organization
3. **Update these key values:**
   - `ORG_NAME` - Your GitHub organization
   - `REPO_PATTERN` - Your module naming pattern
   - `EXCLUDE_REPOS` - Repos to skip

### Example Configuration

```bash
# config/aws.config
ORG_NAME="mycompany"
REPO_PATTERN="terraform-aws-*"
EXCLUDE_REPOS="terraform-aws-archived terraform-aws-template"
```

## 📁 Available Configs

| File | Provider | Default Pattern | Purpose |
|------|----------|-----------------|---------|
| `aws.config` | AWS | `terraform-aws-*` | AWS provider modules |
| `gcp.config` | Google Cloud | `terraform-gcp-*` | GCP provider modules |
| `azure.config` | Microsoft Azure | `terraform-azurerm-*` | Azure provider modules |
| `digitalocean.config` | DigitalOcean | `terraform-digitalocean-*` | DigitalOcean modules |
| `global.config` | Base config | N/A | Shared settings |

## 🎯 Common Patterns

Different organizations use different naming conventions:

```bash
# Pattern examples:
terraform-aws-*          # Most common (HashiCorp style)
tf-aws-*                 # Short prefix
terraform-*-aws          # Suffix style
infra-aws-*              # Custom prefix
aws-terraform-*          # Provider-first
module-aws-*             # Module prefix
```

## 🔐 Security Best Practices

- **Never commit credentials** - Use GitHub secrets or environment variables
- **Use read-only tokens** when possible
- **Review EXCLUDE_REPOS** - Protect critical infrastructure
- **Test on non-production** first

## 🚀 Advanced Configuration

### Custom Workflow Settings

```bash
# Use shared workflows (optional)
SHARED_WORKFLOWS_REPO="your-org/github-shared-workflows"
WORKFLOW_SHA="abc123..."  # Pin to specific version
```

### Validation Options

```bash
# Enable/disable tools
RUN_TERRAFORM_VALIDATE=true
RUN_TFLINT=true
RUN_TFSEC=true
RUN_TRIVY=false  # Disable if not installed
```

### Branch & PR Settings

```bash
DEFAULT_BRANCH="main"     # or "master"
CREATE_PR=true            # Create PR instead of direct commit
```

## 📖 More Information

- [ENV-VARS.md](../docs/ENV-VARS.md) - Complete variable reference
- [PROVIDER-SELECTION.md](../docs/PROVIDER-SELECTION.md) - Choosing configs
- [EXAMPLES.md](../docs/EXAMPLES.md) - Real-world configurations

## 💡 Examples

### Open Source Project

```bash
# terraform-aws-modules organization
ORG_NAME="terraform-aws-modules"
REPO_PATTERN="terraform-aws-*"
EXCLUDE_REPOS="terraform-aws-template"
```

### Enterprise Setup

```bash
# Internal platform team
ORG_NAME="acme-platform"
REPO_PATTERN="infra-*"
EXCLUDE_REPOS="infra-prod-* infra-staging-*"  # Protect production
CREATE_PR=true  # Require review
```

### Consulting Firm

```bash
# Multiple clients
ORG_NAME="consulting-firm"
REPO_PATTERN="client-*-terraform-*"
EXCLUDE_REPOS="client-archived-*"
```

---

**Need Help?** See [docs/USAGE.md](../docs/USAGE.md) or [open an issue](https://github.com/anmolnagpal/terraform-ai-skills/issues)
