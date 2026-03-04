# Business Process Audit

Identify automation opportunities across any business. Analyzes workflows, estimates time savings, and prioritizes which processes to automate first based on ROI.

## When to Use
- Evaluating which business processes to automate
- Building a business case for AI agent deployment
- Identifying bottlenecks and manual work that costs money
- Planning digital transformation or ops optimization

## How It Works

Ask the user about their business (or infer from context). Then analyze across these 8 categories:

### 1. Communication & Email (avg 28% of work week)
- Email triage and response
- Meeting scheduling and follow-ups
- Internal notifications and updates
- Client communication workflows

### 2. Data Entry & Processing (avg 19% of work week)
- Invoice processing and AP/AR
- CRM data entry and updates
- Report generation
- Form processing

### 3. Customer Operations (avg 15% of work week)
- Lead qualification and routing
- Onboarding workflows
- Support ticket triage
- Renewal and upsell identification

### 4. Document Management (avg 12% of work week)
- Contract review and extraction
- Compliance document processing
- Filing and organization
- Version control and approvals

### 5. Financial Operations (avg 10% of work week)
- Expense categorization
- Reconciliation
- Forecasting data prep
- Billing and collections

### 6. HR & People Ops (avg 8% of work week)
- Resume screening
- Onboarding checklists
- Time-off management
- Performance review prep

### 7. Sales & Marketing (avg 5% of work week)
- Lead research and enrichment
- Content scheduling
- Pipeline reporting
- Competitor monitoring

### 8. IT & Security (avg 3% of work week)
- Access provisioning
- Monitoring and alerts
- Backup verification
- Compliance checks

## Output Format

Generate a structured audit report:

```
# Business Process Audit Report
## Company: [Name]
## Industry: [Industry]
## Team Size: [N employees]

### Executive Summary
- Total estimated hours wasted on manual work: X hrs/week
- Potential annual savings: $X
- Top 3 automation priorities (by ROI)

### Process Analysis

For each of the 8 categories:
| Process | Current State | Hours/Week | Automation Potential | Est. Savings | Priority |
|---------|--------------|------------|---------------------|-------------|----------|

Priority scoring: (hours × hourly_cost × automation_percentage) / implementation_effort

### Recommended Automation Roadmap
#### Phase 1 (Week 1-2): Quick wins — processes with >80% automation potential
#### Phase 2 (Month 1): Medium complexity — integration-dependent processes  
#### Phase 3 (Quarter 1): Complex workflows — multi-system orchestration

### ROI Summary
- Implementation cost estimate: $X
- Monthly savings estimate: $X/mo
- Payback period: X months
- 12-month net ROI: X%
```

## Assumptions for Calculations
- Average US knowledge worker salary: $75,000/year ($36/hr fully loaded)
- Average work week: 40 hours
- Automation typically captures 60-85% of manual task time
- Implementation timeline: 1-4 weeks depending on complexity

## Tips
- Be specific about the business — generic audits are worthless
- Ask about their tech stack (what tools they already use)
- Focus on processes that are repetitive, rule-based, and high-volume
- Include both time savings AND error reduction benefits
- Always quantify in dollars, not just hours
