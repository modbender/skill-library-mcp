# Workplace Safety & OSHA Compliance

Generate workplace safety programs, incident reports, hazard assessments, and compliance documentation.

## Commands

### `safety audit`
Run a workplace safety audit. Ask for:
- Industry (construction, manufacturing, office, warehouse, healthcare, food service)
- Number of employees
- Recent incidents (last 12 months)
- Current safety programs in place

Generate:
1. **Hazard Assessment Matrix** — identify top risks by severity × probability
2. **OSHA Compliance Checklist** — mapped to relevant standards (29 CFR 1910/1926)
3. **Gap Analysis** — what's missing vs. regulatory requirements
4. **Priority Action Plan** — ranked by risk score, estimated cost, timeline

### `incident report`
Generate a structured incident investigation report:
- Date, time, location, personnel involved
- Incident classification (near miss, first aid, recordable, lost time)
- Root cause analysis (5 Whys + fishbone diagram prompts)
- Corrective actions with owner + deadline
- OSHA 300 log entry guidance

### `safety program`
Build a complete safety program for a specific hazard:
- Lockout/Tagout (LOTO)
- Confined Space Entry
- Fall Protection
- Hazard Communication (HazCom/GHS)
- Personal Protective Equipment (PPE)
- Emergency Action Plan
- Respiratory Protection
- Electrical Safety

Each program includes: purpose, scope, responsibilities, procedures, training requirements, recordkeeping.

### `training matrix`
Generate an employee safety training matrix:
- Role-based training requirements
- Frequency (initial, annual, refresher)
- Regulatory basis for each requirement
- Tracking template with completion dates
- Cost estimates for third-party training

### `jha`
Job Hazard Analysis for a specific task:
- Break task into steps
- Identify hazards per step
- Assign risk rating (severity × likelihood)
- Define controls (elimination → PPE hierarchy)
- Generate field-ready JHA card

## Key Standards Reference

| Standard | Scope |
|----------|-------|
| OSHA 29 CFR 1910 | General industry |
| OSHA 29 CFR 1926 | Construction |
| OSHA 29 CFR 1904 | Recordkeeping |
| ANSI Z10 | OHS management systems |
| ISO 45001 | Occupational H&S |
| NFPA 70E | Electrical safety |

## Penalty Context
- Serious violation: $16,131 per violation (2024)
- Willful/repeat: $161,323 per violation
- Average cost of workplace injury: $42,000 (direct) + $126,000 (indirect)
- ROI of safety programs: $4-$6 returned per $1 invested (OSHA data)

## Output Formats
- Markdown tables for audits and matrices
- Bullet checklists for field use
- Numbered procedures for programs
- Summary dashboards for management review

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business operations. See our [Manufacturing Pack](https://afrexai-cto.github.io/context-packs/) and [Construction Pack](https://afrexai-cto.github.io/context-packs/) for industry-specific agent configurations.*

*Free tools: [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) | [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)*
