# Copilot Skills Version Information

VERSION=0.0.1
RELEASE_DATE=2026-02-06
STATUS=stable

## Supported Providers
- AWS (terraform-aws-*) - Provider v5.80.0+
- GCP (terraform-gcp-*) - Provider v6.20.0+
- Azure (terraform-azurerm-*) - Provider v4.20.0+
- DigitalOcean (terraform-digitalocean-*) - Provider v2.70.0+

## Terraform Version
- Minimum: 1.10.0
- Recommended: ~> 1.10

## Change Log

### v0.0.1 (2026-02-06)
- ✨ Added multi-cloud support (AWS, GCP, Azure, DO)
- ⬆️ Updated Terraform requirement to 1.10.0
- ⬆️ Updated all provider versions to latest
- 📝 Added PROVIDER-SELECTION.md guide
- 📝 Added CONTRIBUTING.md for customization
- 🔒 Added SAFETY.md with checklists
- 🔧 Added run-with-provider.sh wrapper script
- 📦 Separate config files per provider
- 🎯 Enhanced validation with TFLint and TFSec

### Previous (Internal) (Previous)
- Initial release for DigitalOcean
- Basic provider upgrade
- Workflow standardization
- Release creation
- Full maintenance workflow

## Compatibility

| Skills Version | Terraform | Min Provider Versions |
|----------------|-----------|----------------------|
| 0.0.1 | 1.10.0+ | AWS 5.80, GCP 6.20, Azure 4.20, DO 2.70 |
| 1.0.0 | 1.5.4+ | DO 2.70 |

## Upgrade Notes

### From v1.0.0 to v0.0.1
1. Update `global.config` is now base config only
2. Use provider-specific configs: `aws.config`, `gcp.config`, `azure.config`, `digitalocean.config`
3. Update prompts to reference specific provider configs
4. Scripts now support `COPILOT_CONFIG` environment variable
5. Use `run-with-provider.sh` wrapper for easy provider selection

## Known Issues
- None currently

## Roadmap
- [ ] Add policy-as-code validation (OPA)
- [ ] Add cost estimation integration (Infracost)
- [ ] Add drift detection skill
- [ ] Add module dependency graph generator
- [ ] Add automated testing skill
- [ ] Add compliance checking (CIS benchmarks)
