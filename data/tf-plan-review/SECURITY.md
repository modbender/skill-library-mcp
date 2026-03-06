# SECURITY.md — tf-plan-review Security Model

## What Data This Skill Touches

| Data | Access | Notes |
|------|--------|-------|
| `.tf` / `.tf.json` configuration files | **Read-only** | Read by `terraform plan` and `terraform validate` |
| Terraform plan JSON output | **Read-only, in-memory** | Parsed for risk analysis, never cached to disk |
| Terraform state | **Read-only** | Queried via `terraform state list` / `terraform state show` |
| Provider APIs (AWS, GCP, Azure, etc.) | **Read-only** | `terraform plan` makes read-only API calls to compare desired vs actual state |
| Cloud credentials | **Never accessed directly** | Used by Terraform's provider plugins, never read or logged by this skill |

## Network Behavior

This skill does **not** make any network requests itself. The underlying `terraform` or `tofu` binary contacts:

- **Provider APIs** (AWS, GCP, Azure, etc.) — for plan comparison against live infrastructure
- **Terraform Registry** — for provider/module downloads during `terraform init`
- **State backend** (S3, GCS, Azure Blob, Terraform Cloud, etc.) — for state retrieval

No data is sent to CacheForge or any third party beyond what standard Terraform operations do.

## Commands This Skill Runs

**Allowed (read-only):**
- `terraform plan -json -input=false -no-color`
- `terraform validate -json -no-color`
- `terraform state list`
- `terraform state show <resource>`
- `terraform init -input=false -no-color` (required before plan)
- `terraform init -input=false -backend=false -no-color` (for validate-only)
- `terraform providers`

**NEVER run (state-modifying / destructive):**
- ❌ `terraform apply`
- ❌ `terraform destroy`
- ❌ `terraform import`
- ❌ `terraform taint` / `terraform untaint`
- ❌ `terraform state mv` / `terraform state rm` / `terraform state push`
- ❌ `terraform force-unlock`
- ❌ `terraform workspace new` / `terraform workspace delete`

## Abuse Cases & Mitigations

| Abuse Case | Risk | Mitigation |
|------------|------|------------|
| User asks agent to apply the plan | **High** | Skill explicitly refuses. SKILL.md has hard rule: NEVER run apply. Agent is instructed to redirect to manual apply with checklist. |
| Plan output contains secrets in resource attributes | **High** | Script extracts only resource addresses, types, and actions — not attribute values. Sensitive values marked by TF are never revealed. |
| Cloud credentials exposed in error messages | **Medium** | Script captures plan errors via JSON diagnostics, not raw stderr which may contain creds. |
| terraform init downloads malicious provider | **Medium** | Only runs init when `.terraform` directory is missing. Uses `-input=false` to prevent interactive prompts. User is responsible for trusting their provider sources. |
| State inspection reveals sensitive attributes | **Medium** | `state` subcommand lists resource addresses only (via `state list`), not attribute values. If attribute inspection is added later, sensitive fields must be redacted. |
| Shell injection via directory names | **Low** | All paths are quoted. JSON construction uses `jq --arg` for safe interpolation. No `eval` or backtick execution. |
| Denial of service via huge plan (10K+ resources) | **Low** | Plan output is parsed by `jq` which handles large JSON efficiently. Timeout enforced via `TF_PLAN_TIMEOUT` (default 600s). |
| Symlink traversal to unintended directories | **Low** | `resolve_dir` uses `cd && pwd` which follows symlinks to real path. This is by design — if user specifies a symlinked directory, they intend to analyze the target. |

## Input Validation

- **Directory paths:** Validated via `cd "$DIR" && pwd` (fails on non-existent)
- **Subcommands:** Strict case-match dispatch — unknown subcommands are rejected
- **Filter strings:** Passed to `grep -i` for state filtering — no regex injection risk (grep, not eval)
- **JSON parsing:** All output parsing uses `jq` with explicit field access and `--arg` for safe variable interpolation
- **No eval, no source, no backticks:** The script never executes dynamic strings

## Sensitive Data in Terraform

Terraform plan JSON can contain sensitive information:

1. **Resource attribute values** — database passwords, API keys, certificates
2. **Provider configuration** — access keys, secret keys, tokens
3. **Backend configuration** — storage credentials, encryption keys
4. **Output values** — potentially sensitive exports

This skill mitigates exposure by:
- Extracting only **structural** information (resource type, address, action) not attribute values
- Never caching plan output to disk (processed in-memory via pipes)
- Never logging raw terraform output
- Respecting Terraform's `(sensitive)` markers

## Rate Limiting

Not applicable — this skill runs locally on user request. Provider APIs have their own rate limits, which Terraform handles internally.

## What This Skill Does NOT Do

- Does not modify infrastructure (no apply, destroy, import)
- Does not modify Terraform state (no state mv, rm, push)
- Does not expose cloud credentials
- Does not reveal sensitive attribute values
- Does not cache or persist plan output
- Does not phone home or send telemetry
- Does not execute .tf file content (only Terraform parses the HCL)
- Does not create, write, or modify any files (the only exception is `terraform init` creating `.terraform/`)
