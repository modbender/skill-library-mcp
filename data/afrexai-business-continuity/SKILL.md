---
name: Business Continuity Planner
description: Build a complete Business Continuity Plan (BCP) and Disaster
  Recovery (DR) strategy for any organization.
---

# Business Continuity Planner

Build a complete Business Continuity Plan (BCP) and Disaster Recovery (DR) strategy for any organization.

## What It Does
- Maps critical business functions and their dependencies
- Assigns Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)
- Creates communication chains and escalation paths
- Generates a full BCP document ready for stakeholder sign-off
- Identifies single points of failure before they break

## How to Use

Tell the agent about your business and it will walk you through building a BCP:

```
"Create a business continuity plan for our 40-person SaaS company"
"We need a disaster recovery plan — our main systems are AWS-hosted"
"Map our critical functions and set RTOs for each"
```

## Process

### 1. Business Impact Analysis
Ask the user about:
- Core revenue-generating functions
- Customer-facing systems
- Internal operations (payroll, comms, data)
- Key vendors and third-party dependencies

For each function, determine:
- **Impact of downtime** (revenue loss per hour, contractual penalties, reputation damage)
- **RTO** — how fast must it recover? (minutes, hours, days)
- **RPO** — how much data loss is acceptable?

### 2. Risk Assessment
Identify threats across categories:
- **Technology**: server failure, cyberattack, data corruption, cloud outage
- **People**: key person risk, mass absence, skills gap
- **Facilities**: office access, power, connectivity
- **Supply chain**: vendor failure, payment disruption
- **External**: regulatory change, natural disaster, pandemic

Rate each: Likelihood (1-5) × Impact (1-5) = Risk Score

### 3. Recovery Strategies
For each critical function, define:
- Primary recovery method
- Backup/alternative approach
- Manual workaround (if systems are down)
- Responsible person + backup person
- Dependencies that must recover first

### 4. Communication Plan
Build a contact tree:
- Crisis management team (names, roles, phone numbers)
- Escalation triggers (what constitutes a crisis?)
- Internal notification sequence
- External stakeholder communication (clients, vendors, regulators)
- Media/PR response template

### 5. BCP Document Output

Generate a structured document with:

```markdown
# Business Continuity Plan — [Company Name]
## Version: 1.0 | Last Updated: [Date] | Next Review: [Date + 6 months]

### 1. Purpose & Scope
### 2. Business Impact Analysis (table)
### 3. Risk Register (table with scores)
### 4. Recovery Strategies (per function)
### 5. Communication Plan & Contact Tree
### 6. IT Disaster Recovery Procedures
### 7. Testing Schedule (tabletop exercises quarterly, full test annually)
### 8. Document Control & Review Cycle
```

### 6. Testing & Maintenance
Recommend:
- **Tabletop exercise** quarterly — walk through a scenario verbally
- **Simulation test** bi-annually — actually invoke recovery procedures
- **Full DR test** annually — failover to backup systems
- **Review trigger**: after any real incident, org change, or new system deployment

## Output Format
Deliver the BCP as a single markdown document the user can save, print, or convert to PDF. Include tables for the Business Impact Analysis and Risk Register.

## Tips
- Start with the functions that make money. Everything else is secondary.
- A plan that exists but hasn't been tested is just a document, not a plan.
- The #1 cause of extended outages isn't technical failure — it's nobody knowing who to call.
- Keep it practical. A 5-page plan people actually read beats a 50-page plan nobody opens.
