# AWS Services — Quick Reference

## Compute

| Service | Use Case | Pricing Model |
|---------|----------|---------------|
| EC2 | Full control VMs | Per-hour + storage |
| Lambda | Event-driven, <15min | Per-invocation + duration |
| ECS Fargate | Containers, no cluster | Per vCPU/memory-hour |
| EKS | Kubernetes | $0.10/hr + node costs |
| Lightsail | Simple VPS | Fixed monthly |

### When to Use What

```
Need full OS control? → EC2
Short tasks, variable load? → Lambda
Containers, don't want to manage nodes? → Fargate
Already on Kubernetes? → EKS
Just need a simple server? → Lightsail
```

## Database

| Service | Type | Best For |
|---------|------|----------|
| RDS | Relational | PostgreSQL/MySQL workloads |
| Aurora | Relational (AWS) | High availability, auto-scaling |
| DynamoDB | Key-value | High throughput, simple queries |
| ElastiCache | In-memory | Caching, sessions |
| DocumentDB | Document | MongoDB compatibility |

### Database Selection

```
Traditional SQL app? → RDS PostgreSQL
Need auto-scaling reads? → Aurora
Simple key-value, massive scale? → DynamoDB
Caching layer? → ElastiCache Redis
```

## Storage

| Service | Type | Cost/GB/month |
|---------|------|---------------|
| S3 Standard | Object | $0.023 |
| S3 IA | Infrequent | $0.0125 |
| S3 Glacier | Archive | $0.004 |
| EBS gp3 | Block | $0.08 |
| EFS | File (NFS) | $0.30 |

### Storage Selection

```
Static files, backups? → S3
Need filesystem mount? → EFS
Block storage for EC2? → EBS gp3
Archive (rare access)? → Glacier
```

## Networking

| Service | Purpose | Key Cost |
|---------|---------|----------|
| VPC | Network isolation | Free |
| ALB | HTTP load balancing | $0.0225/hr + LCU |
| NLB | TCP/UDP load balancing | $0.0225/hr + LCU |
| CloudFront | CDN | Per-request + transfer |
| Route 53 | DNS | $0.50/zone + queries |
| API Gateway | REST/HTTP APIs | Per-request |

### Load Balancer Selection

```
HTTP/HTTPS traffic? → ALB
Raw TCP/UDP, extreme performance? → NLB
WebSocket? → ALB
gRPC? → ALB (with HTTP/2)
```

## Security & Identity

| Service | Purpose |
|---------|---------|
| IAM | Users, roles, policies |
| Cognito | User authentication |
| Secrets Manager | Rotate credentials |
| KMS | Encryption keys |
| WAF | Web application firewall |
| GuardDuty | Threat detection |

## Messaging & Integration

| Service | Pattern | Use Case |
|---------|---------|----------|
| SQS | Queue | Decouple services |
| SNS | Pub/sub | Fan-out notifications |
| EventBridge | Event bus | Event-driven architecture |
| Step Functions | Orchestration | Complex workflows |

### Messaging Selection

```
Simple job queue? → SQS
Broadcast to many? → SNS
Event routing? → EventBridge
Multi-step workflow? → Step Functions
```

## Observability

| Service | Purpose |
|---------|---------|
| CloudWatch Logs | Log aggregation |
| CloudWatch Metrics | Monitoring |
| CloudWatch Alarms | Alerting |
| X-Ray | Distributed tracing |
| CloudTrail | API audit log |

## Cost Tiers (Typical)

| Tier | Services | Monthly |
|------|----------|---------|
| Free tier | Lambda, DynamoDB, S3 (limits) | $0 |
| Minimal | t3.micro + RDS + S3 | $30-50 |
| Startup | t3.small + RDS + ALB + S3 | $100-200 |
| Growth | ASG + RDS Multi-AZ + ElastiCache | $300-500 |
| Scale | EKS + Aurora + CloudFront | $1000+ |
