# tf-plan-review — Terraform Plan Analyzer & Risk Assessor for OpenClaw

**AI-powered risk assessment for Terraform plans.** Know exactly what will be destroyed, what's dangerous, and what to verify — before you press apply.

## Install

```bash
clawhub install tf-plan-review
```

## What It Does

Point it at a Terraform directory. It runs `terraform plan -json`, classifies every resource change by risk level, detects destroys and security changes, and produces a clear risk report with a pre-apply checklist.

### Risk Classification

Every resource change is classified:

| Level | Meaning | Examples |
|-------|---------|----------|
| 🔴 **Critical** | Data loss, security breach, or service outage risk | Destroy RDS, modify IAM policies, delete security groups |
| 🟠 **Dangerous** | Downtime or manual recovery likely | Replace EC2 instances, destroy load balancers, delete VPCs |
| 🟡 **Moderate** | Capacity or config changes worth reviewing | Update autoscaling, modify monitoring rules |
| 🟢 **Safe** | Low-risk changes | Create new resources, tag updates |

### Features

- **Plan analysis** — risk-assessed summary of every change in the plan
- **Destroy detection** — prominently flags all resources being permanently deleted
- **IAM/security filter** — focused view of security-sensitive changes
- **Blast radius** — traces what depends on destroyed/replaced resources
- **State inspection** — list and filter managed resources
- **Config validation** — check for syntax errors without running a plan
- **Drift detection** — identifies resources changed outside Terraform
- **Pre-apply checklist** — human-readable verification list
- **OpenTofu support** — seamless `tofu` support via `TF_BINARY` env var

## OpenClaw Discord v2 Ready

Compatible with OpenClaw Discord channel behavior documented for v2026.2.14+:
- Compact first risk summary (overall risk + critical/destructive counts)
- Component-style quick actions when available (`Show Critical Changes`, `Show Destroyed Resources`, `Show Pre-Apply Checklist`)
- Numbered-list fallback when components are unavailable

## Usage

Just ask your agent:

> "Review this terraform plan before I apply"
> "What will be destroyed?"
> "Is this plan safe to apply?"
> "Show me the IAM changes in this plan"
> "What's the blast radius?"
> "Validate my terraform config"

### OpenTofu

```bash
# Auto-detects tofu if terraform isn't installed
# Or force it:
export TF_BINARY=tofu
```

## Requirements

- **bash** (Linux/macOS)
- **jq** 1.6+ (required for JSON parsing)
- **terraform** 1.5+ or **tofu** 1.6+ (at least one)
- Valid provider credentials configured (the skill uses `terraform plan`, which needs API access)

## Safety

- **Strictly read-only.** Never runs `terraform apply`. Never modifies state. Never.
- The only commands executed are: `plan`, `validate`, `state list`, `state show`, `init`, `providers`
- Plan output is analyzed in-memory and never cached to disk
- Sensitive values marked by Terraform are never revealed
- No telemetry. No tracking. No phone-home. No API keys needed for the skill itself.
- `set -euo pipefail` in all scripts

## Output

The skill produces:
- **Structured JSON** (stdout) — for agent consumption and programmatic use
- **Markdown risk report** (stderr) — beautiful human-readable assessment

### Sample Risk Report

```
# 🔍 Terraform Plan Risk Assessment

**Overall Risk:** 🔴 CRITICAL

## 📊 Change Summary
| Action | Count |
|--------|-------|
| ➕ Create | 3 |
| ✏️ Update | 2 |
| 💥 Destroy | 1 |
| **Total** | **6** |

## 🚨 HIGH-RISK CHANGES — REVIEW CAREFULLY
| Risk | Action | Resource |
|------|--------|----------|
| 🔴 CRITICAL | delete | `aws_db_instance.production` |
| 🟠 DANGEROUS | replace | `aws_instance.api_server` |

## 💀 RESOURCES BEING DESTROYED
- ⛔ `aws_db_instance.production` — delete

> ⚠️ Destruction is irreversible. Verify backups exist.

## ✅ Pre-Apply Checklist
- [ ] Backups verified for all resources being destroyed
- [ ] Change reviewed by at least one other team member
- [ ] Rollback plan documented
```

## More from Anvil AI

This skill is part of the **Anvil AI** open-source skill suite — production-grade agent skills built by engineers who actually manage infrastructure.

| Skill | What it does |
|-------|-------------|
| **tf-plan-review** | This skill — Terraform plan risk assessment |
| **dep-audit** | Dependency vulnerability auditing (npm, pip, Cargo, Go) |

More skills shipping soon.

---

Built by **[Anvil AI](https://anvil-ai.io)**.


## License

MIT
