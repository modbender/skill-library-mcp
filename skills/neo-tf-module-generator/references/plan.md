# Acceptance Test Plan for Terraform Module Generator Skill

## Overview
This document defines the acceptance criteria for the `tf-module-generator` skill. The skill must meet all criteria to be considered complete.

## Functional Acceptance Criteria

### CLI and Invocation
1. The CLI (`scripts/main.js`) must be executable with Node.js and accept the following command-line arguments:
   - `--provider` or `-p`: Cloud provider (aws, azure, gcp) – required.
   - `--resources` or `-r`: Comma-separated list of resource types to include – required.
   - `--output` or `-o`: Output directory path for the generated module – required.
   - `--config` or `-c`: Optional path to a configuration file for provider credentials.
2. The CLI must validate that required arguments are present and print usage instructions if missing.
3. The CLI must exit with code 0 on success and non-zero on failure, with error messages printed to stderr.

### Cloud Resource Scanning
4. For AWS:
   - `scripts/aws-scanner.js` must use the AWS SDK to query existing resources.
   - Supported resource types: `ec2`, `rds`, `s3`, `vpc`.
   - For each selected resource type, the scanner must return an array of resource objects containing all relevant attributes required for Terraform configuration.
5. For Azure:
   - `scripts/azure-scanner.js` must use the Azure SDK.
   - Supported resource types: `compute`, `network`, `storage`.
6. For GCP:
   - `scripts/gcp-scanner.js` must use the GCP SDK.
   - Supported resource types: `compute`, `networking`, `sql`.
7. Scanners must handle authentication via standard provider SDK credential chains (environment variables, shared credentials files, etc.).
8. Scanners must filter resources based on the selected types and return only those resources.

### Code Generation
9. `scripts/terraform-generator.js` must accept the scanner output and generate a Terraform module in the output directory.
10. The module must contain the following files:
    - `main.tf`: Holds resource blocks generated from the appropriate templates in `references/templates/<provider>/`. Each resource block must reference input variables for all configurable properties.
    - `variables.tf`: Defines an input variable for each configurable property used in the resources. Variables must include appropriate type constraints (string, number, bool, list, map) and descriptions. Sensitive variables must set `sensitive = true`.
    - `outputs.tf`: Defines outputs for key attributes of each resource (e.g., id, ARN, IP addresses). Outputs must have descriptions.
    - `versions.tf`: Specifies `required_version` for Terraform (from `assets/terraform-version`) and `required_providers` with source and version constraints for the selected provider.
    - `README.md`: Documents the module, including:
      - Description of what the module creates.
      - List of input variables with descriptions, types, and default values where applicable.
      - List of outputs.
      - Example usage snippet showing how to call the module.
11. If multiple resources of the same type are detected, the generator must create multiple resource blocks with distinct names (e.g., `aws_instance.this[0]`, `aws_instance.this[1]`) or use `for_each`/`count` appropriately to allow managing all discovered resources.
12. The generator must ensure that all variable names are valid Terraform identifiers and that references in resource blocks match the variable names.

### Validation
13. `scripts/validator.js` must perform the following checks automatically after generation:
    - Terraform syntax validation (e.g., using `terraform fmt -check` or an HCL parser).
    - Provider version compatibility check (ensure provider versions in `versions.tf` are valid).
    - Basic best practices: no hardcoded secrets, all external values passed via variables; proper use of `sensitive` flag; resource names follow conventions.
14. If validation fails, the CLI must stop and report errors without leaving incomplete output.

### Agent Integration
15. The skill must be callable via OpenClaw agent sessions using `sessions_spawn` with a task that invokes the CLI (e.g., `task="generate-module", arguments={...}`).
16. The agent must be able to retrieve the generated files and deliver them to the user (e.g., as a ZIP archive or by writing to a shared workspace).
17. The agent must translate user-friendly requests (e.g., "Generate a Terraform module for my AWS EC2 instances") into the appropriate CLI arguments.

### Examples and Documentation
18. The example modules under `assets/examples/` (AWS, Azure, GCP) must be valid, ready-to-use Terraform modules that demonstrate the structure produced by the generator.
19. Each example must include the same file set (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`) and demonstrate typical resource parameters.
20. The `assets/terraform-version` file must contain the exact Terraform version string that the generated modules will require (e.g., `>= 1.0.0`).

### Data and Templates
21. `references/providers.json` must contain schema mappings for all supported resource types, including:
    - Terraform resource type name.
    - List of arguments (with type, optional/required, description).
    - List of attributes that can be exported as outputs.
22. Template files in `references/templates/<provider>/` (e.g., `ec2.tf.tpl`) must contain HCL snippets that can be inserted into `main.tf`. They must use variable interpolation (e.g., `var.<name>`) for all values that should be parameterized.
23. Templates must be valid HCL fragments and must not contain syntax errors.

### Error Handling and Edge Cases
24. If the scanner finds no resources of the requested types, the generator must create a module with placeholder outputs and a warning in the README, or fail gracefully with a clear message (behavior to be decided, but must be consistent).
25. If provider credentials are missing or invalid, the scanner must exit with an informative error.
26. The skill must handle large numbers of resources without performance degradation (batch processing if necessary).
27. The generated module must be idempotent: running the generator multiple times on the same infrastructure should produce functionally identical code (ignoring non-deterministic ordering).

## Non-Functional Acceptance Criteria
- The codebase must follow consistent style (e.g., ESLint for JavaScript).
- All scripts must have error handling and logging.
- The skill must run on standard Node.js (version specified in `package.json`).
- The memory footprint should not exceed 500MB during normal operation.
