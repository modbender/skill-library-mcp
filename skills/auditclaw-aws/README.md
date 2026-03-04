# auditclaw-aws

AWS compliance evidence collection companion skill for the [AuditClaw GRC](https://github.com/avansaber/auditclaw-grc) platform.

## Overview

This skill runs automated security checks against an AWS account and stores
evidence in the shared GRC database. It covers 15 AWS services including IAM,
S3, CloudTrail, VPC, KMS, EC2, RDS, Security Hub, GuardDuty, Lambda,
CloudWatch, Config, EKS/ECS, ELB, and credential reports.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. Configure AWS credentials:
   ```bash
   # Option A: IAM user access keys
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"

   # Option B: AWS CLI
   aws configure
   ```

3. Run all checks:
   ```bash
   python3 scripts/aws_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all
   ```

## Checks (15)

| # | Check | What It Verifies |
|---|-------|-----------------|
| 1 | iam | Password policy, MFA enforcement, access key rotation, unused credentials |
| 2 | s3 | Default encryption, public access blocks, versioning, access logging |
| 3 | cloudtrail | Trail enabled, multi-region, log validation, S3 delivery |
| 4 | vpc | Flow logs enabled, security group rules, NACL configuration |
| 5 | kms | Key rotation enabled, key policies, key usage |
| 6 | ec2 | IMDSv2 enforcement, EBS encryption, public IP exposure |
| 7 | rds | Storage encryption, automated backups, public accessibility |
| 8 | security_hub | Security Hub enabled, active findings by severity |
| 9 | guardduty | Detector enabled, active findings, threat intelligence |
| 10 | lambda | Runtime currency, public access, VPC attachment |
| 11 | cloudwatch | Log group retention policies, metric alarm coverage |
| 12 | config | Config recorder active, rule compliance status |
| 13 | eks_ecs | Container cluster encryption, logging, network policies |
| 14 | elb | HTTPS listeners, WAF association, access logging |
| 15 | credential_report | Full IAM credential report analysis |

## Required IAM Permissions

See `scripts/iam-policy.json` for the minimum IAM policy (43 read-only API actions
across 14 services). No write/modify/delete permissions.

All checks use read-only access. No modifications are made to your AWS resources.

## Testing

```bash
python3 -m pytest tests/ -v
```

31 tests, all using `unittest.mock` -- no AWS credentials needed.

## License

MIT License. See [LICENSE](LICENSE) for details.
