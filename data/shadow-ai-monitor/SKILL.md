---
name: shadow-ai-monitor
description: Shadow AI Monitor - Enterprise-grade dashboard for tracking employee AI tool usage, data exposure risks, and PIPEDA compliance. Generates professional HTML dashboards with interactive drill-downs, compliance analysis, and PDF export. Perfect for CTOs and security teams monitoring ChatGPT, Claude, Gemini, Copilot, and other AI tools. Includes demo data generator for presentations.
---

# Shadow AI Monitor

A professional web dashboard system for tracking employee AI tool usage, identifying data exposure risks, and measuring PIPEDA compliance.

## What This Skill Does

Generates enterprise-grade HTML dashboards showing:

- 📊 **AI Tool Usage Analytics** - Track which tools employees use (ChatGPT, Claude, Gemini, Copilot, Midjourney, Grok, Perplexity, Cursor, GitHub Copilot)
- ⚠️ **Risk Analysis** - Classify data exposure as Low/Medium/High risk
- 📋 **Compliance Scoring** - PIPEDA compliance score (0-100) with detailed requirement breakdown
- 👥 **Employee Insights** - Anonymized usage patterns and heatmaps
- 📈 **Trend Tracking** - Daily usage trends and event logs
- 📄 **Board-Ready Reports** - PDF export with professional styling

## Perfect For

- **Security Teams** monitoring shadow AI adoption
- **CTOs** assessing compliance gaps
- **Legal/Compliance** teams tracking data exposure
- **Sales Teams** demoing AI governance products
- **Consultants** delivering AI risk assessments

## Quick Start

Generate a demo dashboard:

```bash
node scripts/generate_demo_data.js
node scripts/generate_dashboard.js shadow-ai-data.json
```

Open `shadow-ai-dashboard.html` in your browser.

## Features

### 🎯 Interactive Dashboard

**Click to Explore:**
- **Employee Bars** → See top 3 riskiest events, tools used, data categories, dates
- **Compliance Score** → View 5 PIPEDA requirements, pass/fail status, specific fixes
- **Export Button** → Generate PDF with letterhead styling

**Key Metrics:**
- PIPEDA compliance score (color-coded: green ≥85, yellow ≥70, red <70)
- Risk event breakdown (High/Medium/Low)
- Top 3 AI tools by usage
- Top 10 employees (anonymized)

**Visualizations:**
- Bar charts: Tool usage, employee activity
- Doughnut chart: Risk distribution
- Line chart: Daily trends
- Heat map: Employee usage intensity
- Scrollable event log (last 20 events, high-risk highlighted)

### 📋 Personalized Recommendations

Auto-generated advice based on actual data patterns:
- References specific employees and percentages
- Tool-specific recommendations (e.g., "ChatGPT accounts for 48% of usage")
- Compliance-specific action items
- Example: "Employee 5 generated 8 high-risk events involving client matters — review recommended"

### 🔒 PIPEDA Compliance Analysis

Detailed breakdown of 5 core requirements:
1. Consent for Collection
2. Limiting Use, Disclosure & Retention
3. Safeguards
4. Openness
5. Individual Access

Each shows:
- Pass/Fail status
- Requirement description
- Specific action items using your actual data

### 📊 Demo Data Generator

Creates realistic data for a 50-person Canadian organization:

**Configurable:**
- Company name (default: Morrison & Associates)
- Employee count
- AI tools tracked
- Data categories (Client Legal, Financial, Health, Personal, etc.)
- Risk distribution
- Time period (last 7 days default)

**Realistic Patterns:**
- Mix of 9 different AI tools
- Varied risk levels (~25% high, ~35% medium, ~40% low)
- Employee anonymization (Employee 1, Employee 2, etc.)
- Concerning patterns for demo impact

## Files

```
shadow-ai-monitor/
├── SKILL.md                        # This file
├── scripts/
│   ├── generate_demo_data.js      # Demo data generator
│   └── generate_dashboard.js      # HTML dashboard generator
```

## Installation

Via ClawHub:
```bash
clawhub install shadow-ai-monitor
```

Manual:
```bash
mkdir -p ~/.openclaw/skills
cd ~/.openclaw/skills
# Download and extract skill files
```

## Usage

### Basic Demo Dashboard

```bash
cd ~/.openclaw/workspace  # or your working directory
node ~/.openclaw/skills/shadow-ai-monitor/scripts/generate_demo_data.js
node ~/.openclaw/skills/shadow-ai-monitor/scripts/generate_dashboard.js shadow-ai-data.json
open shadow-ai-dashboard.html  # or double-click in Finder/Explorer
```

This generates:
- `shadow-ai-data.json` - Raw usage data
- `shadow-ai-dashboard.html` - Interactive dashboard

### Customizing Demo Data

Edit `scripts/generate_demo_data.js` to customize:

**Company Name:**
```javascript
const output = {
  company: 'Your Company Name',
  // ...
};
```

**Employee Count:**
```javascript
const employees = Array.from({ length: 100 }, (_, i) => ({
  id: `Employee ${i + 1}`,
  // ...
}));
```

**AI Tools Tracked:**
```javascript
const AI_TOOLS = [
  'ChatGPT', 'Claude', 'Gemini', 'Your-Custom-Tool'
];
```

**Data Categories:**
```javascript
const DATA_CATEGORIES = [
  { name: 'Your Category', risk: 'High' },
  // ...
];
```

### Automated Weekly Reports

Set up with OpenClaw cron:

```javascript
{
  "name": "Shadow AI Weekly Report",
  "schedule": {"kind": "cron", "expr": "0 9 * * 1", "tz": "America/Toronto"},
  "payload": {
    "kind": "agentTurn",
    "message": "Generate Shadow AI dashboard: 1) Run demo data generator 2) Generate dashboard 3) Send WhatsApp notification with metrics"
  },
  "sessionTarget": "isolated",
  "delivery": {"mode": "announce", "channel": "whatsapp"}
}
```

## Technical Details

### Data Structure

```json
{
  "generated": "2026-02-22T15:00:00Z",
  "company": "Morrison & Associates",
  "employeeCount": 50,
  "period": "Last 7 days",
  "events": [
    {
      "timestamp": "2026-02-22T10:30:00Z",
      "employee": "Employee 1",
      "employeeRole": "Senior Associate",
      "tool": "ChatGPT",
      "dataCategory": "Client Legal Matters",
      "risk": "High"
    }
  ],
  "metrics": {
    "totalEvents": 268,
    "topTools": [["ChatGPT", 89], ["Claude", 56]],
    "riskCounts": {"Low": 95, "Medium": 83, "High": 90},
    "complianceScore": 68,
    "recommendations": ["..."]
  }
}
```

### Risk Scoring

**High Risk:**
- Client legal matters
- Financial records
- Health information

**Medium Risk:**
- Personal information
- Internal memos
- Proprietary data

**Low Risk:**
- General questions
- Code templates
- Public research

### Compliance Score Calculation

```
Base: 100 points
Deduct: -2 points per % of high-risk events
Deduct: -0.5 points per % of medium-risk events
Range: 0-100
```

Example:
- 268 total events
- 90 high-risk (34%) → -68 points
- 83 medium-risk (31%) → -15.5 points
- **Score: 16/100**

### Dashboard Technology

- **Pure JavaScript** - No npm install required
- **Chart.js via CDN** - Loaded from jsDelivr
- **Dark Theme** - Professional enterprise styling
- **Responsive Design** - Works on desktop and tablet
- **Print-Optimized** - Clean PDF export with letterhead

## Use Cases

### 1. CTO Demo

**Script:**
> "This is Morrison & Associates, a 50-person law firm. Over 7 days, we detected 268 AI tool events. Their PIPEDA compliance score is 16/100 because 34% of interactions involved client legal matters and health records shared with unapproved AI tools."

*Click compliance score* → Show specific PIPEDA failures  
*Click Employee 38* → Show their risky events  
*Click Export* → Board-ready PDF

### 2. Security Assessment

Generate dashboard with your organization's data:
1. Monitor Slack/Teams/Email for AI tool mentions
2. Log to JSON format matching data structure
3. Run dashboard generator
4. Present findings to security team

### 3. Sales Presentation

Demo realistic data showing:
- Concerning compliance gaps
- Specific risk patterns
- Clear ROI through risk reduction
- Professional, board-ready output

### 4. Compliance Audit

Track progress over time:
- Generate weekly snapshots
- Compare compliance scores
- Identify trends (improving/worsening)
- Document remediation efforts

## Security & Privacy

✅ **No External API Calls** - All processing local  
✅ **No Data Collection** - Demo data never leaves your machine  
✅ **No Credentials Required** - Pure JavaScript execution  
✅ **Anonymized Data** - Employee IDs, no PII in demo  
✅ **Open Source** - Review all code before running

## Requirements

- **Node.js** (any recent version)
- **Web Browser** (Chrome, Firefox, Safari, Edge)
- **No npm packages** - Uses only Node.js built-ins

## Roadmap

Future enhancements:
- [ ] Real-time monitoring integration
- [ ] Multi-company comparison
- [ ] Historical trend analysis
- [ ] Custom compliance frameworks (GDPR, HIPAA, SOC 2)
- [ ] Email delivery of reports
- [ ] Slack/Teams integration
- [ ] Live data ingestion from DLP tools

## Support & Contribution

- **Issues:** Report bugs or request features on ClawHub
- **Questions:** OpenClaw Discord community
- **Contributions:** Submit improved visualizations, compliance frameworks, or data sources

## License

MIT - Free for personal and commercial use

## Credits

Built with OpenClaw by the automation engineering community.

---

**Version:** 1.0.0  
**Author:** Automation Engineers  
**Category:** Security, Compliance, Analytics  
**Tags:** AI monitoring, PIPEDA, compliance, security, dashboard
