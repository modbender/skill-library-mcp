# FinOps Domains and Capabilities

Quick reference for the 22 capabilities across 4 domains. For comprehensive details, see https://www.finops.org/framework/capabilities/

## Domain Overview

| Domain | Capabilities |
|--------|--------------|
| **Understand Usage & Cost** | Data Ingestion, Allocation, Reporting & Analytics, Anomaly Management |
| **Quantify Business Value** | Planning & Estimating, Forecasting, Budgeting, Benchmarking, Unit Economics |
| **Optimize Usage & Cost** | Architecting for Cloud, Rate Optimization, Workload Optimization, Cloud Sustainability, Licensing & SaaS |
| **Manage the FinOps Practice** | Practice Operations, Policy & Governance, Assessment, Tools & Services, Education & Enablement, Invoicing & Chargeback, Onboarding Workloads, Intersecting Disciplines |

---

## Domain 1: Understand Usage & Cost

### 1.1 Data Ingestion
Collect and normalize cost/usage data from all sources (CUR, Cost Export, BigQuery). Normalize with FOCUS format.

### 1.2 Allocation
Assign costs using tags/accounts for accountability. **Methods**: Direct, Proportional, Fixed, Even-split. **KPI**: 50% Crawl, 80% Walk, 90% Run allocated.

### 1.3 Reporting & Analytics
Create dashboards and trending analysis by persona. Enable self-service analytics.

### 1.4 Anomaly Management
Detect and alert on unexpected cost events. Track cost spikes, drops, usage changes, and rate changes.

---

## Domain 2: Quantify Business Value

### 2.1 Planning & Estimating
Quantify anticipated costs before they occur. **Approaches**: Bottom-up, Top-down, Analogous, Parametric.

### 2.2 Forecasting
Model future costs using historical data and planned changes. **Methods**: Trend (stable), Driver-based (business-linked), Rolling, ML. **KPI**: Variance 20% Crawl, 15% Walk, 12% Run.

### 2.3 Budgeting
Set spending thresholds aligned to forecasts. **Types**: Operational, Project, Capital, Reserve.

### 2.4 Benchmarking
Compare against internal teams and industry peers (data.finops.org). Track cost efficiency, optimization rates, maturity.

### 2.5 Unit Economics
Connect costs to business outputs. **Examples**: Cost per transaction, per user, cloud cost ratio.

---

## Domain 3: Optimize Usage & Cost

### 3.1 Architecting for Cloud
Design cost-effective systems using cloud-native services. **Levers**: Serverless, managed services, storage tiering, regional selection.

### 3.2 Rate Optimization
Reduce rates via commitment discounts. **Types**: RIs (30-72%), Savings Plans (20-66%), CUDs (37-57%), Spot (60-90%). **KPI**: Coverage 70-80%, Utilization 80%+, Break-even <9mo.

### 3.3 Workload Optimization
Match resources to actual needs. **Savings**: Delete unused (100%), Rightsize (20-50%), Schedule non-prod (60-70%), Storage tiering (40-80%).

### 3.4 Cloud Sustainability
Optimize for environmental impact. Consider region carbon intensity, instance efficiency, renewable energy.

### 3.5 Licensing & SaaS
Manage software licenses and SaaS subscriptions. Track usage, optimize allocation, consider BYOL.

---

## Domain 4: Manage the FinOps Practice

### 4.1 FinOps Practice Operations
Define team structure, establish operating cadence, manage stakeholders, track practice KPIs.

### 4.2 Policy & Governance
Establish policies and guardrails. **Examples**: Tagging requirements, budget alerts, approved instances, region restrictions.

### 4.3 FinOps Assessment
Conduct maturity assessments, benchmark against framework, track progress over time.

### 4.4 FinOps Tools & Services
Evaluate and manage tools. **Categories**: Native CSP (Cost Explorer, Cost Management), Third-party (CloudHealth, Kubecost), Open source (OpenCost).

### 4.5 FinOps Education & Enablement
Train organization on FinOps. Develop training by persona, create playbooks, enable self-service.

### 4.6 Invoicing & Chargeback
Process invoices, implement showback/chargeback. **Showback**: Awareness only. **Chargeback**: P&L impact, stronger accountability.

### 4.7 Onboarding Workloads
Define processes for bringing new workloads into practice. Establish standards, create profiles.

### 4.8 Intersecting Disciplines
Coordinate with ITAM (licenses), ITFM (budgeting), Security (compliance), Sustainability (carbon), ITSM (service costing).

---

## Capability Dependencies

**Foundation**: Data Ingestion → Allocation → Reporting (enables all others)

**Optimization**: Rate ←→ Workload Optimization (coordinate, don't commit to waste)

**Value**: Planning → Forecasting → Budgeting → Unit Economics → Benchmarking

**Quick reference only. For detailed capability guidance, see https://www.finops.org/framework/capabilities/**
