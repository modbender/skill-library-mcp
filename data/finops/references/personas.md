# FinOps Personas

Quick reference for stakeholder groups in FinOps. Personas represent broad groups; one person may fulfill multiple personas.

## Core Personas

### FinOps Practitioner
**Role**: Bridge business, engineering, and finance teams using FinOps Framework knowledge.

**Responsibilities**: Cloud cost management, analytical optimization, cross-team collaboration, change management.

**Key activities**: Develop tagging standards (Allocation), manage commitment portfolio (Rate Opt), generate forecasts, define policies (Governance).

### Engineering
**Role**: Design, manage, optimize infrastructure for cost-effectiveness and reliability.

**Responsibilities**: Infrastructure management, application deployment, resource optimization, monitoring, automation.

**Key activities**: Apply tags (Allocation), provide usage plans (Rate Opt), implement rightsizing (Workload Opt), input on planned changes (Forecasting).

### Finance
**Role**: Provide financial expertise, reconcile invoices, forecast, budget, allocate costs.

**Responsibilities**: Financial guidance, budgeting/forecasting, cost allocation, reporting, compliance.

**Key activities**: Determine org units (Allocation), set budgets/track variance (Budgeting), validate models (Forecasting), process chargeback.

### Product
**Role**: Align FinOps to business objectives, define requirements, prioritize initiatives.

**Responsibilities**: Strategic alignment, stakeholder engagement, requirement definition, value delivery.

**Key activities**: Define unit metrics (Unit Economics), provide business context (Forecasting), feedback on allocations.

### Procurement
**Role**: Procure cloud services, optimize vendor relationships, ensure cost-effective engagements.

**Responsibilities**: Vendor/contract management, negotiated discounts, license monitoring, compliance.

**Key activities**: Negotiate agreements (Rate Opt), manage software contracts (Licensing), procure tools (Tools & Services).

### Leadership
**Role**: Empower organizational alignment, enable action, connect cloud decisions to business objectives.

**Responsibilities**: Strategic oversight, decision-making authority, stakeholder alignment, compliance.

**Key activities**: Approve policies/strategies (Governance/Allocation), set variance thresholds (Forecasting), support maturity improvement.

---

## Allied Personas

### ITAM (IT Asset Management)
**Intersection**: Asset discovery, license management, compliance, cost optimization (especially BYOL decisions).

### ITFM (IT Financial Management)
**Intersection**: Budgeting, cost accounting/modeling, TCO analysis, investment prioritization.

### Sustainability
**Intersection**: Optimization for sustainable initiatives, waste reduction, efficiency analysis, carbon footprint reporting.

### ITSM/ITIL (IT Service Management)
**Intersection**: Service design/operation, service level monitoring, service costing, capacity planning, change management.

### Security
**Intersection**: Monitoring/anomaly response, policy/compliance, identity/access management, security tool costs.

---

## Quick RACI Reference

| Capability | FinOps | Engineering | Finance | Product | Procurement | Leadership |
|------------|--------|-------------|---------|---------|-------------|------------|
| **Data Ingestion** | R/A | C | I | I | I | I |
| **Allocation** | R/A | C | C | C | I | A |
| **Reporting** | R/A | C | C | C | I | I |
| **Forecasting** | R | C | R/A | C | I | A |
| **Budgeting** | C | C | R/A | C | I | A |
| **Rate Optimization** | R/A | C | C | I | C | A |
| **Workload Optimization** | C | R/A | I | C | I | I |
| **Governance** | R/A | C | C | I | C | A |

*R=Responsible, A=Accountable, C=Consulted, I=Informed*

---

## Team Structures

| Structure | Best For | Characteristics |
|-----------|----------|-----------------|
| **Centralized** | Early maturity, smaller orgs | Single team owns all FinOps |
| **Federated** | Large orgs, multiple BUs | Central CoE + embedded practitioners |
| **Hybrid** | Growing practices | Central standards, distributed execution |

**Team Size Guidance**: Crawl (0.5-1 FTE/$10M), Walk (1 FTE/$10-15M), Run (1 FTE/$15-25M with automation).

---

## Tailoring Communication

| Persona | Focus On | Meeting Cadence |
|---------|----------|----------------|
| **Engineering** | Technical details, automation | Weekly cost review |
| **Finance** | ROI, variance, compliance | Monthly budget review |
| **Leadership** | Business impact, strategy | Monthly/Quarterly exec briefing |
| **Product** | Value metrics, trade-offs | Quarterly strategy review |
| **Procurement** | Contract terms, negotiations | As needed |

**For complete persona details, see https://www.finops.org/framework/personas/**
