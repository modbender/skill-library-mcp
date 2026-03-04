# AWS Security — Best Practices

## IAM Fundamentals

### Never Use Root Account
```bash
# Create admin user instead
aws iam create-user --user-name admin
aws iam attach-user-policy --user-name admin \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Principle of Least Privilege
Start with zero permissions, add only what's needed:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

### Use Roles, Not Users for Services
```bash
# EC2 instance role (no credentials in code)
aws iam create-role --role-name MyAppRole \
  --assume-role-policy-document file://trust-policy.json
```

## Network Security

### VPC Best Practices

```
┌─────────────────────────────────────────┐
│ VPC (10.0.0.0/16)                       │
│  ┌──────────────┐  ┌──────────────┐     │
│  │ Public       │  │ Private      │     │
│  │ 10.0.1.0/24  │  │ 10.0.2.0/24  │     │
│  │              │  │              │     │
│  │ ALB, NAT     │  │ EC2, RDS     │     │
│  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────┘
```

- **Public subnet:** Only load balancers, NAT gateways
- **Private subnet:** All application servers, databases
- **No direct internet access** for private resources

### Security Groups

```bash
# Deny all by default, allow specific
aws ec2 create-security-group --group-name web-sg \
  --description "Web servers"

# Allow HTTPS from ALB only
aws ec2 authorize-security-group-ingress --group-id sg-xxx \
  --protocol tcp --port 443 --source-group sg-alb
```

**Key rules:**
- Never allow 0.0.0.0/0 for SSH (use Session Manager)
- Restrict outbound to required ports
- Reference security groups, not IP ranges

### NACLs (Stateless)
Remember: NACLs need explicit return traffic rules.

```bash
# Allow inbound HTTPS
aws ec2 create-network-acl-entry --network-acl-id acl-xxx \
  --rule-number 100 --protocol tcp --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 --rule-action allow --ingress

# Allow outbound ephemeral (return traffic)
aws ec2 create-network-acl-entry --network-acl-id acl-xxx \
  --rule-number 100 --protocol tcp --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 --rule-action allow --egress
```

## Data Protection

### Encryption at Rest
```bash
# S3 bucket encryption
aws s3api put-bucket-encryption --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]
  }'

# RDS encryption (must be set at creation)
aws rds create-db-instance --db-instance-identifier mydb \
  --storage-encrypted --kms-key-id alias/aws/rds ...
```

### Encryption in Transit
- Use HTTPS everywhere (ALB terminates TLS)
- Require TLS for RDS connections
- Use VPC endpoints to avoid public internet

## S3 Security

### Block Public Access (Account-Wide)
```bash
aws s3control put-public-access-block --account-id 123456789012 \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Bucket Policy Audit
```bash
# Check for public access
aws s3api get-bucket-policy-status --bucket my-bucket
aws s3api get-public-access-block --bucket my-bucket
```

## Secrets Management

### Use Secrets Manager
```bash
# Store secret
aws secretsmanager create-secret --name myapp/db-password \
  --secret-string '{"password":"xxx"}'

# Retrieve in app
aws secretsmanager get-secret-value --secret-id myapp/db-password
```

### Rotate Credentials
Enable automatic rotation for RDS:
```bash
aws secretsmanager rotate-secret --secret-id myapp/db-password \
  --rotation-lambda-arn arn:aws:lambda:...:function:SecretsManagerRotation
```

## Monitoring & Detection

### CloudTrail (Always On)
```bash
aws cloudtrail create-trail --name management-events \
  --s3-bucket-name my-audit-logs --is-multi-region-trail
```

### GuardDuty
```bash
aws guardduty create-detector --enable
```

### Config Rules
```bash
# Example: Detect unencrypted S3 buckets
aws configservice put-config-rule --config-rule '{
  "ConfigRuleName": "s3-bucket-ssl-requests-only",
  "Source": {"Owner": "AWS", "SourceIdentifier": "S3_BUCKET_SSL_REQUESTS_ONLY"}
}'
```

## Security Checklist

| Check | Command |
|-------|---------|
| MFA on root | Console → Security credentials |
| No root access keys | `aws iam list-access-keys --user-name root` |
| CloudTrail enabled | `aws cloudtrail describe-trails` |
| S3 public blocked | `aws s3control get-public-access-block` |
| Default VPC deleted | `aws ec2 describe-vpcs --filters Name=isDefault,Values=true` |
| No wide-open SGs | `aws ec2 describe-security-groups --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==\`0.0.0.0/0\`]]]'` |
