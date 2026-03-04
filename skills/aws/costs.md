# AWS Cost Optimization

## Cost Monitoring Setup

### Billing Alerts (Do This First)
```bash
# Enable billing alerts (one-time, in us-east-1)
aws ce put-anomaly-subscription --subscription-name cost-alerts \
  --threshold 50 --frequency DAILY

# Create budget
aws budgets create-budget --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "Monthly",
    "BudgetLimit": {"Amount": "100", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {"NotificationType": "ACTUAL", "ComparisonOperator": "GREATER_THAN", "Threshold": 80},
    "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "you@email.com"}]
  }]'
```

### Cost Explorer
```bash
# Last 30 days by service
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-30d +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## Top Cost Traps

### 1. NAT Gateway Data Processing
**$0.045/GB processed** — adds up silently.

**Fix:** Use VPC endpoints for S3/DynamoDB (free):
```bash
aws ec2 create-vpc-endpoint --vpc-id vpc-xxx \
  --service-name com.amazonaws.us-east-1.s3 --route-table-ids rtb-xxx
```

### 2. Idle Load Balancers
**$16/month minimum** even with zero traffic.

**Find idle ALBs:**
```bash
aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerArn' | \
  xargs -I{} aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB \
  --metric-name RequestCount --dimensions Name=LoadBalancer,Value={} \
  --start-time $(date -v-7d +%Y-%m-%dT%H:%M:%S) --end-time $(date +%Y-%m-%dT%H:%M:%S) \
  --period 604800 --statistics Sum
```

### 3. Unattached EBS Volumes
```bash
# Find orphaned volumes
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].{ID:VolumeId,Size:Size,Created:CreateTime}'
```

### 4. Old EBS Snapshots
```bash
# Snapshots older than 90 days
aws ec2 describe-snapshots --owner-ids self \
  --query 'Snapshots[?StartTime<=`'$(date -v-90d +%Y-%m-%d)'`].[SnapshotId,VolumeSize,StartTime]'
```

### 5. CloudWatch Logs Forever Retention
```bash
# Find log groups with no retention
aws logs describe-log-groups \
  --query 'logGroups[?!retentionInDays].[logGroupName,storedBytes]'

# Set 14-day retention
aws logs put-retention-policy --log-group-name /aws/lambda/fn --retention-in-days 14
```

### 6. Oversized EC2 Instances
Check CPU utilization — <20% average means oversized:
```bash
aws cloudwatch get-metric-statistics --namespace AWS/EC2 \
  --metric-name CPUUtilization --dimensions Name=InstanceId,Value=i-xxx \
  --start-time $(date -v-7d +%Y-%m-%dT%H:%M:%S) --end-time $(date +%Y-%m-%dT%H:%M:%S) \
  --period 3600 --statistics Average
```

### 7. Cross-AZ Data Transfer
**$0.01/GB each way** between AZs.

**Fix:** Co-locate chatty services in same AZ, or accept the trade-off for availability.

## Savings Strategies

### Reserved Instances (1-3 year commit)
| Term | Payment | Savings |
|------|---------|---------|
| 1 year, no upfront | Monthly | ~30% |
| 1 year, all upfront | One-time | ~40% |
| 3 year, all upfront | One-time | ~60% |

**Only for stable, predictable workloads.**

### Spot Instances (up to 90% off)
Good for:
- Batch processing
- CI/CD workers
- Fault-tolerant workloads

```bash
aws ec2 request-spot-instances --instance-count 1 --type one-time \
  --launch-specification '{"ImageId":"ami-xxx","InstanceType":"t3.medium"}'
```

### Savings Plans
More flexible than RIs — covers EC2, Fargate, Lambda:
```bash
aws savingsplans describe-savings-plans-offerings \
  --product-type EC2_INSTANCE --duration-seconds 31536000
```

### Right-Sizing
Check Compute Optimizer recommendations:
```bash
aws compute-optimizer get-ec2-instance-recommendations
```

## S3 Cost Optimization

### Lifecycle Policies
```bash
aws s3api put-bucket-lifecycle-configuration --bucket my-bucket \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "Archive old data",
      "Status": "Enabled",
      "Filter": {"Prefix": "logs/"},
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"}
      ],
      "Expiration": {"Days": 365}
    }]
  }'
```

### Intelligent-Tiering
Auto-moves objects based on access patterns — small monthly fee but hands-off:
```bash
aws s3api put-bucket-intelligent-tiering-configuration --bucket my-bucket \
  --id auto-tier --intelligent-tiering-configuration '{
    "Id": "auto-tier",
    "Status": "Enabled",
    "Tierings": [
      {"Days": 90, "AccessTier": "ARCHIVE_ACCESS"},
      {"Days": 180, "AccessTier": "DEEP_ARCHIVE_ACCESS"}
    ]
  }'
```

## Monthly Cost Review Checklist

| Check | Action |
|-------|--------|
| Idle EC2 instances | Stop or terminate |
| Unattached EBS volumes | Delete |
| Old snapshots | Delete or lifecycle |
| Unused Elastic IPs | Release |
| Oversized instances | Downsize |
| Log retention | Set policies |
| Reserved capacity | Renew or adjust |
