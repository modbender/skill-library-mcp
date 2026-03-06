---
name: auditclaw-aws
description: AWS compliance evidence collection for auditclaw-grc. 15 read-only checks across S3, IAM, CloudTrail, VPC, KMS, EC2, RDS, Lambda, EBS, SQS, SNS, Secrets Manager, Config, GuardDuty, and Security Hub.
version: 1.0.1
user-invocable: true
homepage: https://www.auditclaw.ai
source: https://github.com/avansaber/auditclaw-aws
metadata: {"openclaw":{"type":"executable","install":{"pip":"scripts/requirements.txt"},"requires":{"bins":["python3"],"env":["AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY"]}}}
---
# AuditClaw AWS

Companion skill for auditclaw-grc. Collects compliance evidence from AWS accounts using read-only API calls.

**15 checks | Read-only IAM policy | Evidence stored in shared GRC database**

## Security Model
- **Read-only access**: Custom IAM policy with 43 read-only API actions. No write/modify/delete permissions.
- **Credentials**: Uses standard AWS credential chain (`aws configure`, env vars, or IAM instance role). No credentials stored by this skill.
- **Dependencies**: `boto3==1.34.46` (pinned)
- **Data flow**: Check results stored as evidence in `~/.openclaw/grc/compliance.sqlite` via auditclaw-grc

## Prerequisites
- AWS credentials configured (`aws configure` or IAM instance role)
- `pip install -r scripts/requirements.txt`
- auditclaw-grc skill installed and initialized

## Commands
- "Run AWS evidence sweep": Run all checks, store results in GRC database
- "Check S3 encryption": Run S3-specific checks
- "Check IAM compliance": Run IAM-specific checks
- "Check CloudTrail status": Verify CloudTrail configuration
- "Check VPC security": Review VPC flow logs and security groups
- "Show AWS integration health": Last sync, errors, evidence count

## Usage
All evidence is stored in the shared GRC database at ~/.openclaw/grc/compliance.sqlite
via the auditclaw-grc skill's db_query.py script.

To run a full evidence sweep:
```
python3 scripts/aws_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all
```

To run specific checks:
```
python3 scripts/aws_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --checks iam,s3,cloudtrail
```

## Check Categories (15)

| Check | What It Verifies |
|-------|-----------------|
| **iam** | Password policy, MFA enforcement, access key rotation, unused credentials |
| **s3** | Default encryption, public access blocks, versioning, access logging |
| **cloudtrail** | Trail enabled, multi-region, log validation, S3 delivery |
| **vpc** | Flow logs enabled, security group rules, NACL configuration |
| **kms** | Key rotation enabled, key policies, key usage |
| **ec2** | IMDSv2 enforcement, EBS encryption, public IP exposure |
| **rds** | Storage encryption, automated backups, public accessibility |
| **security_hub** | Security Hub enabled, active findings by severity |
| **guardduty** | Detector enabled, active findings, threat intelligence |
| **lambda** | Runtime currency, public access, VPC attachment |
| **cloudwatch** | Log group retention policies, metric alarm coverage |
| **config** | Config recorder active, rule compliance status |
| **eks_ecs** | Container cluster encryption, logging, network policies |
| **elb** | HTTPS listeners, WAF association, access logging |
| **credential_report** | Full IAM credential report analysis |

## Evidence Storage
Each check produces evidence items stored with:
- `source: "aws"`
- `type: "automated"`
- `control_id`: Mapped to relevant SOC2/ISO/HIPAA controls
- `description`: Human-readable finding summary
- `file_content`: JSON details of the check result

## IAM Policy
See `scripts/iam-policy.json` for the minimum IAM permissions needed.
Use the principle of least privilege; the policy uses read-only permissions only.

## Setup Guide

When a user asks to set up AWS integration, guide them through these steps:

### Step 1: Create IAM Policy
Direct the user to AWS Console → IAM → Policies → Create Policy → JSON tab.
The exact policy is in `scripts/iam-policy.json`. Show it with:
  python3 {baseDir}/../auditclaw-grc/scripts/db_query.py --action show-policy --provider aws

The policy contains 43 read-only API actions across 14 AWS services. No write/modify/delete permissions.

### Step 2: Create IAM User
Name: `auditclaw-scanner`. Attach the AuditClawReadOnly policy.
CLI: `aws iam create-user --user-name auditclaw-scanner`

### Step 3: Generate Access Keys
Security Credentials → Create Access Key → CLI use case.
CLI: `aws iam create-access-key --user-name auditclaw-scanner`

### Step 4: Configure Credentials
Store credentials: `aws configure` or set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY env vars.

### Step 5: Verify Connection
Run: `python3 {baseDir}/scripts/aws_evidence.py --test-connection`
This probes each AWS service and reports accessibility.

**Do NOT recommend SecurityAudit or ViewOnlyAccess managed policies.** They grant far more access than needed. Always use our custom policy from `scripts/iam-policy.json`.
