---
name: terraform-ai-skills
description: Multi-cloud Terraform module management skills for GitHub Copilot - automate provider upgrades, testing, CI/CD, and releases across AWS, GCP, Azure, and DigitalOcean modules at scale
license: MIT
metadata:
  author: CloudDrove
  version: 0.0.1
  keywords:
    - terraform
    - github-copilot
    - automation
    - aws
    - gcp
    - azure
    - digitalocean
    - infrastructure-as-code
    - devops
    - multi-cloud
---

# Terraform Copilot Skills for Multi-Cloud Module Management

Comprehensive GitHub Copilot skills for managing Terraform modules at scale across AWS, GCP, Azure, and DigitalOcean. Automate provider upgrades, GitHub Actions workflows, releases, and validation across hundreds of repositories.

## When to Use These Skills

**Activate these skills when:**
- Managing multiple Terraform module repositories (10-200+ modules)
- Upgrading provider versions across organizations
- Standardizing GitHub Actions workflows
- Creating releases with automated changelogs
- Performing bulk maintenance operations
- Validating Terraform code at scale
- Setting up CI/CD for infrastructure modules

**Don't use these skills for:**
- Single Terraform project maintenance (too much overhead)
- Writing individual Terraform configurations (use terraform-skill instead)
- Cloud-specific resource questions (use provider documentation)

## Core Principles

### 1. Multi-Cloud First

Support for four major cloud providers with provider-specific configurations:

| Provider | Modules | Organization | Config File |
|----------|---------|--------------|-------------|
| **AWS** | ~170 | clouddrove/terraform-aws-* | `config/aws.config` |
| **GCP** | Multiple | clouddrove/terraform-gcp-* | `config/gcp.config` |
| **Azure** | Multiple | terraform-az-modules/terraform-azurerm-* | `config/azure.config` |
| **DigitalOcean** | Multiple | terraform-do-modules/terraform-digitalocean-* | `config/digitalocean.config` |

All configurations use **Terraform 1.10.0+** with latest provider versions.

### 2. Safety First

Built-in safety mechanisms:
- ✅ Test-on-one-repo-first workflow
- ✅ Pre-flight checklists before bulk operations
- ✅ Rollback procedures for recovery
- ✅ Exclude patterns to protect critical repos
- ✅ Dry-run capability
- ✅ Comprehensive validation at each step

### 3. Time Savings at Scale

| Operation | Manual (170 repos) | With Skills | Savings |
|-----------|-------------------|-------------|---------|
| Provider upgrade | 56 hours | 90 minutes | 97% ⬇️ |
| Workflow fixes | 20 hours | 30 minutes | 97% ⬇️ |
| Release creation | 10 hours | 15 minutes | 97% ⬇️ |
| Full maintenance | 86 hours | 2-3 hours | 97% ⬇️ |

## Available Skills

### 1. Provider Upgrade 🔄
Upgrades provider versions across all modules and examples.

```bash
@copilot use terraform-ai-skills/config/aws.config and follow terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

**What it does:**
- Updates provider version constraints
- Updates Terraform version requirements
- Updates all example configurations
- Runs validation and formatting
- Creates standardized commits

**Time:** 10-90 minutes depending on scale

### 2. Workflow Standardization 🔧
Standardizes GitHub Actions workflows across repositories.

```bash
@copilot use terraform-ai-skills/config/gcp.config and follow terraform-ai-skills/prompts/2-workflow-standardization.prompt
```

**What it does:**
- Pins workflows to specific SHAs
- Updates workflow configurations
- Removes deprecated workflows
- Ensures all checks pass

**Time:** 15-30 minutes

### 3. Release Creation 🚀
Creates versioned releases with changelogs.

```bash
@copilot use terraform-ai-skills/config/azure.config and follow terraform-ai-skills/prompts/3-release-creation.prompt
```

**What it does:**
- Generates changelog from commits
- Creates semantic version tags
- Publishes GitHub releases
- Updates documentation

**Time:** 10-20 minutes

### 4. Full Maintenance ⚡ (Recommended)
Complete end-to-end maintenance cycle combining all skills.

```bash
@copilot use terraform-ai-skills/config/digitalocean.config and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

**What it does:**
- Discovery & audit phase
- Provider and Terraform upgrades
- Workflow standardization
- Comprehensive validation
- Documentation updates
- Release creation
- Summary reporting

**Time:** 45-180 minutes depending on scale

## Quick Start

### Step 1: Choose Your Cloud Provider

Select the configuration for your cloud provider:

```bash
# AWS modules (clouddrove/terraform-aws-*)
CONFIG=aws.config

# GCP modules (clouddrove/terraform-gcp-*)
CONFIG=gcp.config

# Azure modules (terraform-az-modules/terraform-azurerm-*)
CONFIG=azure.config

# DigitalOcean modules (terraform-do-modules/terraform-digitalocean-*)
CONFIG=digitalocean.config
```

### Step 2: Test on One Repository First

**ALWAYS test on a single repository before running on all repos:**

```bash
@copilot use terraform-ai-skills/config/${CONFIG} and upgrade provider in terraform-aws-vpc only, following terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

### Step 3: Run Full Maintenance

After successful test:

```bash
@copilot use terraform-ai-skills/config/${CONFIG} and follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

### Step 4: Verify and Monitor

```bash
# Check what changed
git status
git diff

# Monitor GitHub Actions
gh run list

# Verify releases created
gh release list
```

## Directory Structure

```
terraform-ai-skills/
├── config/                          # Provider-specific configurations
│   ├── aws.config                   # AWS (Provider 5.80.0+, Terraform 1.10.0+)
│   ├── gcp.config                   # GCP (Provider 6.20.0+, Terraform 1.10.0+)
│   ├── azure.config                 # Azure (Provider 4.20.0+, Terraform 1.10.0+)
│   ├── digitalocean.config          # DO (Provider 2.70.0+, Terraform 1.10.0+)
│   └── global.config                # Base configuration
├── prompts/                         # Copilot prompts
│   ├── 1-provider-upgrade.prompt    # Provider version upgrades
│   ├── 2-workflow-standardization.prompt  # GitHub Actions fixes
│   ├── 3-release-creation.prompt    # Release automation
│   └── 4-full-maintenance.prompt    # Complete maintenance cycle
├── scripts/                         # Automation scripts
│   ├── batch-provider-upgrade.sh    # Batch upgrade automation
│   ├── create-releases.sh           # Release creation
│   ├── validate-all.sh              # Validation runner
│   └── run-with-provider.sh         # Provider selection wrapper
├── INDEX.md                         # Complete navigation guide
├── DISTRIBUTION.md                  # Distribution package overview
├── README.md                        # This file
├── QUICKREF.md                      # Quick reference card
├── SAFETY.md                        # Safety procedures & rollback
├── USAGE.md                         # Detailed usage guide
├── EXAMPLES.md                      # Real-world examples
├── PROVIDER-SELECTION.md            # Provider config guide
├── CONTRIBUTING.md                  # Customization guide
├── ENV-VARS.md                      # Environment variables
├── VERSION.md                       # Version history
└── LICENSE                          # MIT License
```

## Configuration Management

### Provider-Specific Settings

Each cloud provider has its own configuration file with appropriate defaults:

**AWS** (`config/aws.config`):
```bash
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.80.0"
ORG_NAME="clouddrove"
REPO_PATTERN="terraform-aws-*"
```

**GCP** (`config/gcp.config`):
```bash
PROVIDER_NAME="google"
PROVIDER_MIN_VERSION="6.20.0"
ORG_NAME="clouddrove"
REPO_PATTERN="terraform-gcp-*"
```

**Azure** (`config/azure.config`):
```bash
PROVIDER_NAME="azurerm"
PROVIDER_MIN_VERSION="4.20.0"
ORG_NAME="terraform-az-modules"  # Different org!
REPO_PATTERN="terraform-azurerm-*"
```

**DigitalOcean** (`config/digitalocean.config`):
```bash
PROVIDER_NAME="digitalocean"
PROVIDER_MIN_VERSION="2.70.0"
ORG_NAME="terraform-do-modules"  # Different org!
REPO_PATTERN="terraform-digitalocean-*"
```

### Customizing for Your Organization

1. **Fork or copy this repository**
2. **Update config files** with your organization's settings
3. **Adjust exclusion patterns** for repos to skip
4. **Modify validation rules** as needed
5. **Test on non-production repos** first

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed customization guide.

## Safety Features

### Pre-Flight Checklist

Before running bulk operations:

- ✅ Read [SAFETY.md](docs/SAFETY.md) completely
- ✅ Test on ONE repository first
- ✅ Review changes with `git diff`
- ✅ Verify excluded repos are actually excluded
- ✅ Have rollback plan ready
- ✅ Run during low-traffic hours

### Built-In Safety Mechanisms

- **Exclude patterns** - Protect critical repos from automation
- **Validation steps** - terraform validate, terraform fmt, TFLint, TFSec
- **Dry-run mode** - Preview changes without applying
- **Rollback procedures** - Documented recovery processes
- **Checkpoints** - Create restore points before major changes

### Rollback Procedures

If something goes wrong, see [SAFETY.md](docs/SAFETY.md) for:
- Reverting commits
- Deleting releases
- Handling partial failures
- Emergency contacts

## Version Management

### Current Version: 0.0.1

**Release Date:** 2026-02-06
**Status:** Production Ready ✅

### What's New in v0.0.1

- ✨ Multi-cloud support (AWS, GCP, Azure, DigitalOcean)
- ⬆️ Terraform 1.10.0+ requirement
- ⬆️ Latest provider versions for all clouds
- 📝 Comprehensive documentation (10 files, 2,656 lines)
- 🔒 Enhanced safety procedures
- 🎯 Provider selection guide
- 📊 Version history tracking

See [VERSION.md](docs/VERSION.md) for complete changelog and compatibility matrix.

## Documentation

### Quick Navigation

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| **[INDEX.md](docs/INDEX.md)** | Complete navigation guide | 5 min |
| **[DISTRIBUTION.md](docs/DISTRIBUTION.md)** | Distribution overview | 10 min |
| **[QUICKREF.md](docs/QUICKREF.md)** | Quick reference card | 2 min |
| **[SAFETY.md](docs/SAFETY.md)** | Safety & rollback | 10 min ⚠️ |
| **[USAGE.md](docs/USAGE.md)** | Detailed guide | 15 min |
| **[EXAMPLES.md](docs/EXAMPLES.md)** | Real-world examples | 10 min |
| **[PROVIDER-SELECTION.md](docs/PROVIDER-SELECTION.md)** | Provider guide | 5 min |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Customization | 15 min |
| **[ENV-VARS.md](docs/ENV-VARS.md)** | Variables reference | 5 min |
| **[VERSION.md](docs/VERSION.md)** | Version history | 3 min |

**Total onboarding time:** ~2 hours (including hands-on practice)

## Real-World Results

### CloudDrove Case Study

**Before Copilot Skills:**
- Time per maintenance cycle: 8-10 hours
- Human errors: 3-5 per cycle
- Consistency: 60-70%
- Repository drift: High

**After Copilot Skills:**
- Time per maintenance cycle: 45-90 minutes
- Human errors: ~0 (automated)
- Consistency: 100%
- Repository drift: None

**ROI:**
- Time saved per month: 30-40 hours per engineer
- Error reduction: 95%+
- Payback period: < 1 week
- Annual savings: 360-480 hours per engineer

## Requirements

- **GitHub Copilot CLI** or compatible AI assistant
- **Terraform** 1.10.0+
- **Git** 2.30+
- **Bash** 4.0+
- **gh CLI** (optional, for enhanced GitHub integration)

### Optional Tools

- **TFLint** - Terraform linting
- **TFSec** - Security scanning
- **Trivy** - Vulnerability scanning
- **Checkov** - Policy-as-code validation
- **terraform-docs** - Documentation generation

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- How to add new skills
- Customization guidelines
- Testing procedures
- Code style guide
- Submission process

### Ways to Contribute

1. **Report issues** - Found a bug? [Open an issue](https://github.com/anmolnagpal/terraform-ai-skills/issues)
2. **Suggest features** - Have ideas? [Start a discussion](https://github.com/anmolnagpal/terraform-ai-skills/discussions)
3. **Add cloud providers** - Want to support another cloud? Submit a PR!
4. **Improve documentation** - Found unclear docs? Help us improve!
5. **Share use cases** - Used these skills successfully? Share your story!

## Comparisons

### vs Manual Maintenance

| Aspect | Manual | Copilot Skills |
|--------|--------|----------------|
| Time (170 repos) | 56 hours | 90 minutes |
| Errors | 3-5 per cycle | ~0 |
| Consistency | 60-70% | 100% |
| Documentation | Often outdated | Always current |
| Rollback | Manual effort | Documented procedures |

### vs Other Automation Tools

| Feature | Copilot Skills | Custom Scripts | Atlantis | Terraform Cloud |
|---------|---------------|----------------|----------|-----------------|
| Multi-cloud | ✅ | Manual setup | Limited | ✅ |
| Cost | Free | Free | Free | $$$ |
| Ease of setup | 30 min | Hours/Days | Hours | Hours |
| Customization | ✅ High | ✅ High | Limited | Limited |
| AI-assisted | ✅ | ❌ | ❌ | Partial |
| Safety checks | ✅ Built-in | Manual | Partial | ✅ |

## License

MIT License - see [LICENSE](LICENSE) for details.

**Copyright © 2026 CloudDrove**

Free to use, modify, and distribute. Attribution appreciated but not required.

## Support

### Getting Help

1. **Documentation** - Check [INDEX.md](docs/INDEX.md) for navigation
2. **Examples** - Review [EXAMPLES.md](docs/EXAMPLES.md) for real-world cases
3. **Issues** - [GitHub Issues](https://github.com/anmolnagpal/terraform-ai-skills/issues) for bugs
4. **Discussions** - [GitHub Discussions](https://github.com/anmolnagpal/terraform-ai-skills/discussions) for questions
5. **Safety** - Review [SAFETY.md](docs/SAFETY.md) for rollback help

### Community

- **Twitter:** [@anmolnagpal](https://twitter.com/clouddrove)
- **LinkedIn:** [CloudDrove](https://www.linkedin.com/company/clouddrove)
- **Website:** [github.com/anmolnagpal](https://github.com/anmolnagpal)
- **Blog:** [blog.github.com/anmolnagpal](https://blog.github.com/anmolnagpal)

## Acknowledgments

Inspired by:
- **[antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill)** - Terraform best practices skill for Claude
- **[terraform-best-practices.com](https://www.terraform-best-practices.com/)** - Comprehensive Terraform guide
- **[terraform-aws-modules](https://github.com/terraform-aws-modules)** - Production-grade AWS modules

Special thanks to the Terraform and GitHub Copilot communities.

## Related Projects

- **[pre-commit-terraform](https://github.com/antonbabenko/pre-commit-terraform)** - Pre-commit hooks
- **[terraform-docs](https://terraform-docs.io/)** - Documentation generator
- **[terratest](https://terratest.gruntwork.io/)** - Testing framework
- **[infracost](https://www.infracost.io/)** - Cost estimation
- **[atlantis](https://www.runatlantis.io/)** - Terraform automation

---

**Ready to save hundreds of hours per year?** Start with [DISTRIBUTION.md](docs/DISTRIBUTION.md) for the complete setup guide.

**Questions?** Check [INDEX.md](docs/INDEX.md) for navigation or [open an issue](https://github.com/anmolnagpal/terraform-ai-skills/issues).

**Status:** Production Ready ✅ | **Version:** 0.0.1 | **License:** MIT
