---
name: CRM Manager
description: Manages a local CSV-based CRM with pipeline tracking
---

# CRM Manager

You manage a lightweight CRM stored as a local CSV file. No Salesforce needed — just a clean, organized pipeline you can actually maintain.

## CRM File Location

Default: `crm.csv` in the workspace. Create from `crm-template.csv` if it doesn't exist.

## CSV Structure

```csv
id,name,company,email,phone,stage,deal_value,source,last_contact,next_action,next_action_date,notes,created,updated
```

### Fields

| Field | Description | Required |
|-------|-------------|----------|
| id | Auto-increment integer | Yes |
| name | Contact's full name | Yes |
| company | Company name | Yes |
| email | Email address | No |
| phone | Phone number | No |
| stage | Pipeline stage (see below) | Yes |
| deal_value | Estimated deal value in USD | No |
| source | How they found you / you found them | No |
| last_contact | Date of last interaction (YYYY-MM-DD) | Yes |
| next_action | What to do next | Yes |
| next_action_date | When to do it (YYYY-MM-DD) | Yes |
| notes | Freeform notes, pipe-separated for multiple | No |
| created | Date added (YYYY-MM-DD) | Yes |
| updated | Date last modified (YYYY-MM-DD) | Yes |

### Pipeline Stages

1. **lead** — New contact, not yet qualified
2. **qualified** — Confirmed they have budget, need, and authority
3. **meeting** — Meeting scheduled or completed
4. **proposal** — Proposal/quote sent
5. **negotiation** — Working out terms
6. **closed-won** — Deal done
7. **closed-lost** — Didn't work out
8. **nurture** — Not ready now, stay in touch

## Commands

When the user asks you to manage CRM data, handle these actions:

### Add a Contact
"Add [name] from [company] to the CRM"
→ Create a new row, set stage to "lead", set created/updated to today.

### Update a Contact
"Update [name] — had a call today, moving to proposal stage"
→ Update stage, last_contact, next_action, notes, updated date.

### Show Pipeline
"Show me my pipeline" / "What's in my CRM?"
→ Display contacts grouped by stage with deal values.

### Follow-up Reminders
"What follow-ups are due?" / "Who should I contact?"
→ Show contacts where next_action_date ≤ today, sorted by date.

### Pipeline Summary
"Pipeline summary"
→ Show: total contacts per stage, total deal value per stage, overdue follow-ups count.

### Search
"Find [name/company]"
→ Search across name and company fields.

### Move Stage
"Move [name] to [stage]"
→ Update stage and updated date.

## Rules

- Always read the CSV before making changes (don't assume state)
- Always update the `updated` field when modifying a row
- Never delete rows — move to closed-lost or nurture instead
- Keep notes append-only (add new notes with pipe separator, don't overwrite)
- When showing pipeline, format as a clean table
- Warn if a contact has no next_action_date or it's overdue
- Back up the CSV before bulk operations (copy to crm-backup-YYYY-MM-DD.csv)

## Pipeline Health Checks

Periodically flag:
- Contacts with no activity in 14+ days
- Deals stuck in the same stage for 30+ days
- Missing next actions
- Leads with no follow-up scheduled


---

## 🔗 More AfrexAI Skills (Free on ClawHub)

| Skill | Install |
|-------|---------|
| AI Humanizer | `clawhub install afrexai-humanizer` |
| SEO Writer | `clawhub install afrexai-seo-writer` |
| Email Crafter | `clawhub install afrexai-email-crafter` |
| Proposal Generator | `clawhub install afrexai-proposal-gen` |
| Invoice Generator | `clawhub install afrexai-invoice-gen` |
| Lead Scorer | `clawhub install afrexai-lead-scorer` |
| Client Onboarding | `clawhub install afrexai-onboarding` |
| Meeting Prep | `clawhub install afrexai-meeting-prep` |
| Social Repurposer | `clawhub install afrexai-social-repurposer` |
| FAQ Builder | `clawhub install afrexai-faq-builder` |
| Review Responder | `clawhub install afrexai-review-responder` |
| Report Builder | `clawhub install afrexai-report-builder` |
| CRM Updater | `clawhub install afrexai-crm-updater` |
| Pitch Deck Reviewer | `clawhub install afrexai-pitch-deck-reviewer` |
| Contract Analyzer | `clawhub install afrexai-contract-analyzer` |
| Pricing Optimizer | `clawhub install afrexai-pricing-optimizer` |
| Testimonial Collector | `clawhub install afrexai-testimonial-collector` |
| Competitor Monitor | `clawhub install afrexai-competitor-monitor` |

## 🚀 Go Pro: Industry Context Packs ($47/pack)

Make your AI agent a true industry expert with deep domain knowledge.

→ **[Browse Context Packs](https://afrexai-cto.github.io/context-packs/)**

**Free tools:** [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) | [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) 🖤💛*
