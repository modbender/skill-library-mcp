# Roadmap

Future improvements for openclaw-aws-deploy. Items are organized by priority.

## P2 — Enterprise/Compliance

| # | Item | Description |
|---|------|-------------|
| 11 | Governance tagging | Add Environment, Owner, CostCenter, ManagedBy tags to all resources |
| 12 | Least-privilege Bedrock | Optional model allowlist to restrict Bedrock access to specific models |
| 13 | Permission boundaries | Scoped IAM with Condition blocks for tighter least-privilege policies |
| 14 | Patch lifecycle | SSM Patch Manager integration with maintenance windows for OS updates |
| 15 | Backup/DR | Automated EBS snapshots on schedule + restore runbook |
| 16 | Multi-environment | `--env prod/staging/dev` flag with isolated resource naming and tagging |
| 18 | IaC mode | Export deployment as CloudFormation or Terraform for GitOps workflows |

## UX Improvements

| # | Item | Description |
|---|------|-------------|
| 20 | Progress indicator | Show real-time progress during the 4-6 min bootstrap wait (SSM log tailing) |
| 22 | Update/redeploy | Document and script how to update OpenClaw version on a running instance |
