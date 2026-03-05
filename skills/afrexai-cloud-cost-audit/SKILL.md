# Cloud Cost Optimization Audit

Analyze cloud infrastructure spend across AWS, Azure, and GCP. Identify waste, rightsizing opportunities, and reserved instance savings.

## What This Skill Does

When given cloud spend data (billing exports, cost explorer screenshots, or manual input), this skill:

1. **Categorizes spend** across 8 cost domains (compute, storage, networking, databases, AI/ML, observability, security, licensing)
2. **Identifies waste patterns** using 12 common anti-patterns
3. **Calculates savings** with specific dollar amounts per optimization
4. **Prioritizes actions** by effort vs. impact (quick wins → strategic moves)
5. **Generates executive summary** with 90-day roadmap

## Cost Domains & Benchmarks (2026)

### 1. Compute (typically 40-55% of total)
- **Idle instances**: >30% idle = waste. Benchmark: <10% idle capacity
- **Rightsizing**: 60% of instances are oversized by 1+ size category
- **Spot/preemptible**: Batch workloads not on spot = 60-80% overpay
- **Reserved/savings plans**: On-demand for steady-state = 30-50% overpay
- **Container density**: <40% CPU utilization on nodes = poor bin-packing

### 2. Storage (typically 10-20%)
- **Tiering**: Data not accessed in 90 days still on hot storage = 60-80% overpay
- **Snapshot sprawl**: Orphaned snapshots older than 30 days
- **Duplicate data**: Cross-region replication without business justification
- **Object lifecycle**: No lifecycle policies = guaranteed bloat

### 3. Networking (typically 8-15%)
- **Cross-AZ traffic**: Unnecessary data transfer between zones ($0.01-0.02/GB)
- **NAT gateway abuse**: High-throughput through NAT vs. VPC endpoints
- **CDN miss rate**: >20% miss rate = CDN config issue
- **Egress optimization**: No committed use discounts on egress

### 4. Databases (typically 10-20%)
- **Over-provisioned RDS/Cloud SQL**: Multi-AZ for dev/staging environments
- **Read replica sprawl**: Replicas with <5% query load
- **DynamoDB/Cosmos over-provisioning**: Provisioned capacity 3x+ actual usage
- **License waste**: Commercial DB when open-source works

### 5. AI/ML Infrastructure (growing — 5-25%)
- **GPU idle time**: Training instances running 24/7 for 4hr/day workloads
- **Inference over-provisioning**: GPU instances for CPU-viable inference
- **Model storage**: Old model versions consuming storage
- **API costs**: Frontier model API calls without caching layer

### 6. Observability (typically 3-8%)
- **Log ingestion bloat**: Debug logs in production, duplicate log streams
- **Metric cardinality**: High-cardinality custom metrics ($$$)
- **Trace sampling**: 100% trace sampling when 10% suffices
- **Retention overkill**: 13-month retention for non-compliance data

### 7. Security (typically 2-5%)
- **WAF rule bloat**: Managed rule groups not actively tuned
- **Key management**: KMS keys for non-sensitive data
- **Compliance scanning**: Overlapping tools doing same checks

### 8. Licensing (typically 5-15%)
- **Shelfware**: Paid seats not logged in 60+ days
- **Duplicate tools**: Multiple tools solving same problem
- **Enterprise tiers**: Enterprise features unused, paying enterprise price

## 12 Waste Anti-Patterns

| # | Pattern | Typical Waste | Fix Effort |
|---|---------|--------------|------------|
| 1 | Zombie resources (stopped but attached) | 5-15% of bill | Low |
| 2 | Over-provisioned instances | 15-30% compute | Medium |
| 3 | No reserved capacity strategy | 25-40% compute | Medium |
| 4 | Hot storage hoarding | 40-70% storage | Low |
| 5 | Cross-AZ data transfer abuse | 10-30% network | Medium |
| 6 | Dev/staging mirrors production | 20-40% of envs | Low |
| 7 | Orphaned snapshots/AMIs | 3-8% storage | Low |
| 8 | Log ingestion without sampling | 30-60% observability | Low |
| 9 | GPU instances for CPU workloads | 70-85% compute | Medium |
| 10 | No spot/preemptible for batch | 60-80% batch | Medium |
| 11 | Shelfware licenses | 20-40% licensing | Low |
| 12 | No tagging = no accountability | Unmeasurable | High |

## Savings Estimation Framework

For each finding, calculate:
```
Annual Savings = (Current Cost - Optimized Cost) × 12
Implementation Cost = Engineering Hours × Loaded Rate
ROI = (Annual Savings - Implementation Cost) / Implementation Cost
Payback Period = Implementation Cost / (Annual Savings / 12)
```

### Typical Savings by Company Size
| Company Size | Monthly Cloud Spend | Typical Waste % | Annual Savings |
|-------------|-------------------|----------------|---------------|
| Startup (5-15) | $2K-$15K | 35-50% | $8K-$90K |
| Growth (15-50) | $15K-$80K | 25-40% | $45K-$384K |
| Mid-market (50-200) | $80K-$500K | 20-35% | $192K-$2.1M |
| Enterprise (200+) | $500K-$5M+ | 15-25% | $900K-$15M+ |

## Output Format

Generate a report with:
1. **Executive Summary**: Total spend, waste identified, savings potential, top 3 quick wins
2. **Domain Breakdown**: Spend per domain vs. benchmarks
3. **Findings Table**: Each finding with current cost, optimized cost, savings, effort, priority
4. **90-Day Roadmap**: Week 1-2 quick wins, Week 3-6 medium effort, Week 7-12 strategic
5. **Governance Recommendations**: Tagging strategy, budget alerts, review cadence

## Usage

Provide your cloud billing data in any format:
- AWS Cost Explorer export / Azure Cost Management / GCP Billing
- Monthly bill summary
- Architecture description with approximate sizing
- Or just describe your stack and team size for estimates

The agent will analyze and produce the full optimization report.

---

## Want Industry-Specific Cloud Optimization?

Different industries have different compliance, data residency, and workload patterns that change the optimization calculus entirely.

**Get your industry context pack** — pre-built frameworks for Fintech, Healthcare, Legal, SaaS, Ecommerce, Construction, Real Estate, Recruitment, Manufacturing, and Professional Services.

🛒 Browse packs: https://afrexai-cto.github.io/context-packs/
🧮 Calculate your AI savings: https://afrexai-cto.github.io/ai-revenue-calculator/
🤖 Set up your agent: https://afrexai-cto.github.io/agent-setup/

**Bundle deals:**
- Pick 3 packs: $97
- All 10 packs: $197
- Everything bundle: $247
