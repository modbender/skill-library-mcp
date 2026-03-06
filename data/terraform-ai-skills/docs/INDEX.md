# Copilot Skills - Complete File Index

## 📋 Start Here

1. **[DISTRIBUTION.md](docs/DISTRIBUTION.md)** ⭐ - **Read this first!** Complete distribution package overview
2. **[README.md](README.md)** - Main overview and quick start guide
3. **[QUICKREF.md](docs/QUICKREF.md)** - Quick reference card for daily use

## 📖 Core Documentation

### Getting Started
- **[README.md](README.md)** - Overview, features, and quick start (3 min read)
- **[QUICKREF.md](docs/QUICKREF.md)** - Quick reference for common commands (2 min read)
- **[PROVIDER-SELECTION.md](docs/PROVIDER-SELECTION.md)** - How to choose the right config (3 min read)

### Learning & Usage
- **[USAGE.md](docs/USAGE.md)** - Detailed usage guide with workflows (10 min read)
- **[EXAMPLES.md](docs/EXAMPLES.md)** - Real-world examples and use cases (8 min read)
- **[ENV-VARS.md](docs/ENV-VARS.md)** - Environment variables reference (5 min read)

### Safety & Operations
- **[SAFETY.md](docs/SAFETY.md)** ⚠️ - **Read before production use!** Safety checklists and rollback (10 min read)

### Advanced
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Customization and extension guide (12 min read)
- **[VERSION.md](docs/VERSION.md)** - Version history and compatibility (3 min read)

## ⚙️ Configuration Files

Located in `config/`:

### Active Configs (Use These)
- **[config/aws.config](config/aws.config)** - AWS modules (clouddrove/terraform-aws-*)
  - Provider: AWS 5.80.0+
  - ~170 repositories
  - Organization: clouddrove

- **[config/gcp.config](config/gcp.config)** - GCP modules (clouddrove/terraform-gcp-*)
  - Provider: Google 6.20.0+
  - Organization: clouddrove

- **[config/azure.config](config/azure.config)** - Azure modules (terraform-az-modules/terraform-azurerm-*)
  - Provider: AzureRM 4.20.0+
  - Organization: terraform-az-modules ⚠️ (Different org!)

- **[config/digitalocean.config](config/digitalocean.config)** - DO modules (terraform-do-modules/terraform-digitalocean-*)
  - Provider: DigitalOcean 2.70.0+
  - Organization: terraform-do-modules ⚠️ (Different org!)

### Base Config
- **[config/global.config](config/global.config)** - Base configuration (mostly for reference now)

## 🤖 Prompts (Use with Copilot)

Located in `prompts/`:

1. **[prompts/1-provider-upgrade.prompt](prompts/1-provider-upgrade.prompt)** 🔄
   - Upgrades provider versions only
   - Time: 10-90 minutes depending on scale
   - Use when: Need to update provider versions

2. **[prompts/2-workflow-standardization.prompt](prompts/2-workflow-standardization.prompt)** 🔧
   - Fixes GitHub Actions workflows
   - Time: 15-30 minutes
   - Use when: Workflows are failing or need updates

3. **[prompts/3-release-creation.prompt](prompts/3-release-creation.prompt)** 🚀
   - Creates releases with changelogs
   - Time: 10-20 minutes
   - Use when: Ready to create releases

4. **[prompts/4-full-maintenance.prompt](prompts/4-full-maintenance.prompt)** ⚡ **RECOMMENDED**
   - Complete maintenance cycle (all skills)
   - Time: 45-180 minutes depending on scale
   - Use when: Want to do everything at once

## 🔧 Scripts (Direct Execution)

Located in `scripts/`:

- **[scripts/batch-provider-upgrade.sh](scripts/batch-provider-upgrade.sh)** - Batch upgrade script
- **[scripts/create-releases.sh](scripts/create-releases.sh)** - Release creation script
- **[scripts/validate-all.sh](scripts/validate-all.sh)** - Validation script

### Helper Script
- **[run-with-provider.sh](run-with-provider.sh)** - Wrapper to run scripts with provider selection
  ```bash
  ./run-with-provider.sh [aws|gcp|azure|do] [script-name]
  ```

## 📄 Other Files

- **[LICENSE](LICENSE)** - MIT License
- **[.gitignore](.gitignore)** - Git ignore patterns

## 🗺️ Navigation Guide

### I want to...

**Get started quickly**
→ Read [DISTRIBUTION.md](docs/DISTRIBUTION.md) then [QUICKREF.md](docs/QUICKREF.md)

**Understand what this does**
→ Read [README.md](README.md) and [EXAMPLES.md](docs/EXAMPLES.md)

**Run my first maintenance**
→ Read [SAFETY.md](docs/SAFETY.md), then [USAGE.md](docs/USAGE.md), then [QUICKREF.md](docs/QUICKREF.md)

**Choose the right config**
→ Read [PROVIDER-SELECTION.md](docs/PROVIDER-SELECTION.md)

**Customize for my needs**
→ Read [CONTRIBUTING.md](CONTRIBUTING.md) and [ENV-VARS.md](docs/ENV-VARS.md)

**Recover from an error**
→ Read [SAFETY.md](docs/SAFETY.md) section "Rollback Procedures"

**See real examples**
→ Read [EXAMPLES.md](docs/EXAMPLES.md)

**Understand versioning**
→ Read [VERSION.md](docs/VERSION.md)

**Learn all the commands**
→ Read [USAGE.md](docs/USAGE.md)

**Get quick commands**
→ Read [QUICKREF.md](docs/QUICKREF.md)

## 📊 File Overview

### Total Files: 23

**Documentation**: 9 files
- Distribution guide, README, usage, examples, safety, etc.

**Configuration**: 5 files
- Global + 4 cloud provider configs

**Prompts**: 4 files
- Provider upgrade, workflows, releases, full maintenance

**Scripts**: 4 files
- Batch upgrade, create releases, validate, provider wrapper

**Other**: 1 file
- LICENSE

### Reading Order (Recommended)

#### For First-Time Users (45 minutes total)
1. [DISTRIBUTION.md](docs/DISTRIBUTION.md) (10 min) - Overview
2. [README.md](README.md) (5 min) - Quick start
3. [SAFETY.md](docs/SAFETY.md) (10 min) - Safety procedures
4. [PROVIDER-SELECTION.md](docs/PROVIDER-SELECTION.md) (5 min) - Choose config
5. [QUICKREF.md](docs/QUICKREF.md) (5 min) - Commands
6. [EXAMPLES.md](docs/EXAMPLES.md) (10 min) - See real usage

#### For Advanced Users (Additional 30 minutes)
7. [USAGE.md](docs/USAGE.md) (10 min) - Detailed guide
8. [CONTRIBUTING.md](CONTRIBUTING.md) (15 min) - Customization
9. [ENV-VARS.md](docs/ENV-VARS.md) (5 min) - Variables

#### For Reference (As Needed)
10. [VERSION.md](docs/VERSION.md) - When checking compatibility
11. Config files - When updating versions
12. Prompt files - When running operations
13. Script files - When debugging

## 🔍 Quick Search

Use this to quickly find what you need:

| Looking for... | Check... |
|----------------|----------|
| Getting started | DISTRIBUTION.md → README.md |
| Quick commands | QUICKREF.md |
| AWS config | config/aws.config |
| GCP config | config/gcp.config |
| Azure config | config/azure.config |
| DO config | config/digitalocean.config |
| Safety procedures | SAFETY.md |
| Rollback help | SAFETY.md (Rollback section) |
| Examples | EXAMPLES.md |
| Customization | CONTRIBUTING.md |
| Version info | VERSION.md |
| Environment vars | ENV-VARS.md |
| Provider selection | PROVIDER-SELECTION.md |
| Full maintenance | prompts/4-full-maintenance.prompt |
| Provider upgrade only | prompts/1-provider-upgrade.prompt |

## 💡 Tips

- **Bookmark** this index for easy navigation
- **Start with** DISTRIBUTION.md if this is your first time
- **Always read** SAFETY.md before production use
- **Refer to** QUICKREF.md for daily operations
- **Check** VERSION.md for compatibility info

---

**Last Updated**: 2026-02-06 | **Version**: 0.0.1 | **Files**: 23
