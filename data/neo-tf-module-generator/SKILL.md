---
name: tf-module-generator
description: Automatically generates Terraform modules from existing cloud infrastructure resources with intelligent resource detection and best-practice code formatting.
---

# tf-module-generator Skill Documentation

## 1. Skill Name
tf-module-generator

## 2. Description
Automatically generates Terraform modules from existing cloud infrastructure resources across AWS, Azure, and GCP. The skill discovers live cloud resources, creates optimized Terraform code with proper variable definitions and outputs, and validates the generated modules against Terraform best practices.

## 3. Core Capabilities
- Scan and analyze existing cloud infrastructure resources across AWS, Azure, and GCP
- Generate optimized Terraform module code with proper variable definitions and outputs
- Support multiple resource types (compute, storage, networking, databases, etc.)
- Generate documentation and example usage for each generated module
- Validate generated Terraform syntax and best practices
- Provide CLI interface with customizable output options and error handling
- Integrate seamlessly with OpenClaw agent workflows for automated infrastructure management

## 4. Out of Scope
- Infrastructure provisioning (only generates code from existing resources)
- Cost optimization recommendations
- Security policy enforcement
- Multi-environment management (dev/staging/prod)
- State management or backend configuration
- Testing the generated modules beyond syntax validation
- Support for non-cloud infrastructure (on-prem, hybrid environments)

## 5. Trigger Scenarios
- "Generate Terraform module from my existing AWS EC2 instances"
- "Convert my Azure resources to Terraform modules"
- "Create Terraform code from my GCP cloud resources"
- "Generate module for my current VPC configuration"
- "Automate Terraform module creation for our cloud infrastructure"
- "Generate Terraform from existing [service] resources"
- "Create reusable Terraform modules from our deployed resources"

## 6. Requirements
- Cloud provider credentials configured (AWS CLI, Azure CLI, or GCP CLI)
- Node.js 18+ runtime
- Access to `terraform` binary for validation (optional but recommended)
- OpenCl agent with sessions_spawn capability

## 7. Key Files
- `SKILL.md`: This documentation
- `scripts/main.js`: CLI entry point and command parsing
- `scripts/aws-scanner.js`: AWS resource discovery and analysis
- `scripts/azure-scanner.js`: Azure resource discovery and analysis
- `scripts/gcp-scanner.js`: GCP resource discovery and analysis
- `scripts/terraform-generator.js`: Terraform module code generation logic
- `scripts/validator.js`: Generated code syntax and best practice validation
- `scripts/config.js`: Configuration management and provider settings
- `references/providers.json`: Cloud provider resource schema mappings
- `references/templates/`: Directory containing module templates for different resource types
- `assets/examples/`: Sample usage examples and test cases
- `assets/terraform-version`: Supported Terraform version constraints
- `package.json`: npm package metadata and dependencies
- `README.md`: Quick start guide

## 8. Acceptance Criteria
- [ ] CLI successfully scans and identifies resources from at least 3 cloud providers
- [ ] Generated Terraform modules pass syntax validation with `terraform validate`
- [ ] All generated code follows Terraform best practices conventions
- [ ] Skill integrates correctly with OpenClaw session_spawn for agent usage
- [ ] Error handling provides clear, actionable feedback for common failure cases
- [ ] Documentation includes usage examples for both CLI and agent integration
- [ ] Code passes all automated tests including security checks
- [ ] Generated modules include appropriate variables, outputs, and documentation
- [ ] Skill triggers correctly for all defined trigger scenarios
- [ ] Performance benchmarks meet targets for typical infrastructure sizes (<1k resources)
