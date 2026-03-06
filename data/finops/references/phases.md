# FinOps Phases

FinOps is performed by working iteratively through three phases: **Inform**, **Optimize**, and **Operate**. These phases form a continuous cycle of improvement.

## Overview

```
┌─────────────────────────────────────────────────┐
│                                                 │
│    ┌──────────┐                                │
│    │  INFORM  │ ◄─────────────────┐            │
│    └────┬─────┘                   │            │
│         │                         │            │
│         ▼                         │            │
│    ┌──────────┐                   │            │
│    │ OPTIMIZE │                   │            │
│    └────┬─────┘                   │            │
│         │                         │            │
│         ▼                         │            │
│    ┌──────────┐                   │            │
│    │ OPERATE  │ ──────────────────┘            │
│    └──────────┘                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Key insight**: Teams within an organization may be at different phases simultaneously. Different capabilities and workloads progress at their own pace.

## Phase 1: Inform

### Focus: Visibility & Allocation

The Inform phase establishes visibility into cloud costs and usage, enabling data-driven decisions.

### Key Activities

| Activity | Description |
|----------|-------------|
| **Data ingestion** | Collect cost, usage, efficiency, and sustainability data from all sources |
| **Cost allocation** | Map costs to organizational units using tags, accounts, and business rules |
| **Reporting** | Create dashboards and reports for all stakeholder levels |
| **Anomaly detection** | Identify unexpected cost spikes or unusual patterns |
| **Benchmarking** | Compare performance against internal teams and industry peers |
| **KPI development** | Establish metrics that reveal business value of cloud spend |

### Capabilities Involved
- Data Ingestion
- Allocation
- Reporting & Analytics
- Anomaly Management

### Outcomes
- Accurate allocation of cloud spend to cost centers
- Real-time visibility into spending patterns
- Understanding of who is spending what and why
- Ability to identify optimization opportunities
- Foundation for budgeting and forecasting

### Sample KPIs
- % of spend allocated to cost centers
- Time to surface cost data (latency)
- Tagging compliance rate
- Anomaly detection accuracy

## Phase 2: Optimize

### Focus: Rates & Usage

The Optimize phase identifies and acts on opportunities to improve cloud efficiency using data from the Inform phase.

### Key Activities

| Activity | Description |
|----------|-------------|
| **Rate optimization** | Purchase RIs, Savings Plans, CUDs to reduce effective rates |
| **Workload optimization** | Rightsize underutilized resources, eliminate waste |
| **Architecture optimization** | Redesign systems to use cost-effective services |
| **Usage scheduling** | Turn off non-production resources when not needed |
| **Storage optimization** | Move data to appropriate storage tiers |
| **Spot/preemptible usage** | Leverage interruptible instances where appropriate |

### Capabilities Involved
- Rate Optimization
- Workload Optimization
- Architecting for Cloud
- Cloud Sustainability
- Licensing & SaaS

### Rate Optimization Options

| Mechanism | Type | Flexibility | Typical Discount |
|-----------|------|-------------|-----------------|
| Reserved Instances | Resource-based | Low | 30-72% |
| Savings Plans | Spend-based | Medium | 20-66% |
| CUDs (GCP) | Resource-based | Low | 37-57% |
| Spot Instances | Usage-based | High | 60-90% |
| Negotiated discounts | Contract-based | Varies | Custom |

### Usage Optimization Approaches

| Approach | Impact | Effort |
|----------|--------|--------|
| Delete unused resources | Immediate | Low |
| Rightsize over-provisioned | Quick | Medium |
| Schedule non-production | Quick | Low |
| Storage tiering | Medium-term | Medium |
| Architecture changes | Long-term | High |

### Outcomes
- Reduced effective rates through commitment discounts
- Eliminated waste from unused/over-provisioned resources
- Improved unit economics
- Optimized architectures leveraging cloud-native services
- Balanced coverage and utilization metrics

### Sample KPIs
- Effective Savings Rate (ESR)
- RI/SP Coverage %
- RI/SP Utilization %
- Waste % (unused resources)
- Cost per unit output

## Phase 3: Operate

### Focus: Continuous Improvement & Operations

The Operate phase implements organizational changes to operationalize FinOps using insights from Inform and Optimize phases.

### Key Activities

| Activity | Description |
|----------|-------------|
| **Governance** | Establish and enforce policies, guardrails, and standards |
| **Automation** | Implement automated optimization and compliance |
| **Training** | Educate all personas on FinOps practices |
| **Process improvement** | Refine workflows based on lessons learned |
| **Cultural change** | Embed cost awareness into engineering culture |
| **Tool management** | Evaluate and manage FinOps tooling |

### Capabilities Involved
- FinOps Practice Operations
- Policy & Governance
- FinOps Assessment
- FinOps Tools & Services
- FinOps Education & Enablement
- Invoicing & Chargeback
- Onboarding Workloads
- Intersecting Disciplines

### Governance Examples

| Policy Type | Example |
|-------------|---------|
| Tagging | All resources must have cost-center, owner, environment tags |
| Budget alerts | Alert at 80%, 90%, 100% of budget threshold |
| Approval workflows | Resources over $X require approval |
| Idle resource cleanup | Unused resources auto-terminated after X days |
| Commitment purchasing | Central team purchases all RIs/Savings Plans |

### Automation Opportunities

| Area | Automation Example |
|------|-------------------|
| Tagging | Auto-tag resources from IaC, remediate missing tags |
| Rightsizing | Auto-implement recommendations during low-traffic windows |
| Scheduling | Auto-stop dev/test environments nights and weekends |
| Anomalies | Auto-alert and ticket creation for cost spikes |
| Reporting | Scheduled delivery of cost reports to stakeholders |

### Outcomes
- Established cloud governance policies and compliance monitoring
- Automated optimization and enforcement
- Trained and enabled organization
- Defined team guidelines and escalation paths
- Continuous feedback loop back to Inform phase

### Sample KPIs
- Policy compliance rate
- Training completion rate
- Time to implement optimizations
- Governance exception rate
- FinOps maturity score improvement

## Phase Iteration

### Continuous Cycle

The goal is to continuously develop strategies and refine workflows:

1. **Inform** → Gather data, identify opportunities
2. **Optimize** → Act on opportunities
3. **Operate** → Systematize and automate
4. **Loop back** → Use operational learnings to improve Inform

### Iteration Cadence

| Activity | Typical Cadence |
|----------|-----------------|
| Daily cost review | Daily |
| Anomaly investigation | As triggered |
| Optimization review | Weekly |
| Budget review | Monthly |
| Maturity assessment | Quarterly |
| Strategy review | Annually |

### Avoiding Analysis Paralysis

- Quick action on a regular cadence prevents over-analysis
- Start small and grow the size and scope as you mature
- Perfect allocation is not required before optimization begins
- Balance the time spent in each phase

## Phase Guidance by Maturity

| Maturity | Inform Focus | Optimize Focus | Operate Focus |
|----------|--------------|----------------|---------------|
| Crawl | Basic visibility, allocation | Quick wins (unused, oversized) | Manual governance |
| Walk | Detailed allocation, anomalies | Commitment discounts, rightsizing | Documented processes |
| Run | Real-time, automated | Continuous, automated | Automated governance |
