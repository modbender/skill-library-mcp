# Provider Configuration Reference

Detailed configuration options for each supported cloud provider.

## Configuration File Location

```
terraform-ai-skills/
└── config/
    ├── global.config        # Base defaults (inherited by all providers)
    ├── aws.config           # AWS-specific overrides
    ├── gcp.config           # GCP-specific overrides
    ├── azure.config         # Azure-specific overrides
    └── digitalocean.config  # DigitalOcean-specific overrides
```

## AWS (`config/aws.config`)

```bash
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.80.0"
ORG_NAME="your-org"               # Your GitHub organization
REPO_PATTERN="terraform-aws-*"    # Glob pattern for module repos
TERRAFORM_MIN_VERSION="1.10.0"
DEFAULT_BRANCH="master"
CREATE_PR=false                   # true = PR workflow, false = direct commit
EXCLUDE_REPOS="terraform-aws-templates terraform-aws-examples"
RUN_TFLINT=true
RUN_TFSEC=true
```

## GCP (`config/gcp.config`)

```bash
PROVIDER_NAME="google"            # Note: "google", not "gcp"
PROVIDER_MIN_VERSION="6.20.0"
ORG_NAME="your-org"
REPO_PATTERN="terraform-gcp-*"
TERRAFORM_MIN_VERSION="1.10.0"
```

## Azure (`config/azure.config`)

```bash
PROVIDER_NAME="azurerm"           # Note: "azurerm", not "azure"
PROVIDER_MIN_VERSION="4.20.0"
ORG_NAME="your-org"               # Note: may differ from AWS/GCP org
REPO_PATTERN="terraform-azurerm-*"
TERRAFORM_MIN_VERSION="1.10.0"
```

## DigitalOcean (`config/digitalocean.config`)

```bash
PROVIDER_NAME="digitalocean"
PROVIDER_MIN_VERSION="2.70.0"
ORG_NAME="your-org"
REPO_PATTERN="terraform-digitalocean-*"
TERRAFORM_MIN_VERSION="1.10.0"
```

## All Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `ORG_NAME` | GitHub organization name | — |
| `PROVIDER_NAME` | Provider identifier (`aws`, `google`, `azurerm`, `digitalocean`) | — |
| `PROVIDER_MIN_VERSION` | Minimum provider version (semver) | — |
| `REPO_PATTERN` | Glob pattern matching target repos | — |
| `TERRAFORM_MIN_VERSION` | Minimum Terraform version | `1.10.0` |
| `DEFAULT_BRANCH` | Default branch name | `master` |
| `EXCLUDE_REPOS` | Space-separated list of repos to skip | `""` |
| `CREATE_PR` | Create PR instead of direct commit | `false` |
| `RUN_TERRAFORM_VALIDATE` | Run `terraform validate` | `true` |
| `RUN_TERRAFORM_FMT` | Run `terraform fmt` | `true` |
| `RUN_TFLINT` | Run TFLint | `false` |
| `RUN_TFSEC` | Run TFSec | `false` |
| `SEMANTIC_VERSIONING` | Use semantic versioning for releases | `true` |
| `TAG_PREFIX` | Version tag prefix | `v` |
| `USE_EMOJIS` | Emojis in changelogs | `true` |
| `DRY_RUN` | Preview changes without applying | `false` |
| `VERBOSE` | Enable verbose output | `false` |

## Customizing for Your Organization

1. Copy the relevant config file
2. Set `ORG_NAME` to your GitHub organization
3. Set `REPO_PATTERN` to match your module naming convention
4. Set `EXCLUDE_REPOS` to protect critical repos
5. Test on one repo before running at scale

```bash
# Different naming patterns are supported:
REPO_PATTERN="tf-aws-*"           # Short prefix
REPO_PATTERN="infra-aws-*"        # Custom prefix
REPO_PATTERN="*-terraform-aws"    # Suffix pattern
```
