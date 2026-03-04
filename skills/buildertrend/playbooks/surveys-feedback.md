# Customer Surveys & Feedback

## Overview
Create and manage client surveys in Buildertrend to collect feedback at project milestones, measure satisfaction, track NPS, and generate testimonials. Surveys are accessed at `/app/Surveys/Individual` with templates managed at `/app/Settings/SurveySettings`.

## Trigger
- "Send a survey to [client]", "get client feedback"
- "Create survey template", "set up milestone surveys"
- "Check survey responses", "review feedback"
- "NPS score", "client satisfaction"
- Project milestone reached (auto-send survey)
- Project closeout (final survey)

---

## Step 1: Create Survey Template
**Action:** Build a reusable survey template in Settings

### Navigate to Survey Settings
**Browser Relay Steps:**
1. Navigate to `/app/Settings/SurveySettings`
2. Snapshot → view existing templates
3. Click "Create new survey template" or similar

### Company Recommended Survey Templates

#### Template 1: Milestone Check-In
**When:** At key milestones (demo complete, rough-in complete, finishes starting)
```
Questions:
1. How satisfied are you with progress so far? (1-10 scale)
2. How well is the team communicating with you? (1-10 scale)
3. Is the project meeting your expectations? (Yes/No/Somewhat)
4. Any concerns or issues we should address? (Open text)
5. Additional comments (Open text)
```

#### Template 2: Project Closeout Survey
**When:** After substantial completion and final walkthrough
```
Questions:
1. Overall, how satisfied are you with the completed project? (1-10 scale)
2. How likely are you to recommend {{company_name}} to others? (0-10 NPS scale)
3. Rate the quality of workmanship (1-10 scale)
4. Rate the team's professionalism (1-10 scale)
5. Rate the project's adherence to timeline (1-10 scale)
6. Rate the project's adherence to budget (1-10 scale)
7. What did we do best? (Open text)
8. What could we improve? (Open text)
9. May we use your feedback as a testimonial? (Yes/No)
10. Would you like to leave a Google review? (Yes/No)
```

#### Template 3: Quick Satisfaction Check
**When:** Monthly during active construction
```
Questions:
1. How satisfied are you with the project this month? (1-10 scale)
2. Any concerns? (Open text)
```

### Browser Relay Steps (Create Template)
1. In Survey Settings, click "New Template"
2. Enter template name
3. Add questions:
   - Select question type (scale, yes/no, open text, multiple choice)
   - Enter question text
   - Set required/optional
4. Set sharing/visibility settings
5. Save template
6. Snapshot → confirm creation

---

## Step 2: Send Survey to Client
**Action:** Send a survey to a project client

### Browser Relay Steps
1. Navigate to `/app/Surveys/Individual`
2. Ensure correct job is selected
3. Click "Create new survey" or "Send survey"
4. Select survey template
5. Select recipient (client contact)
6. Add personal message (optional):
   ```
   Hi [Client Name],
   
   We'd love to hear your feedback on the progress at [Project].
   This brief survey takes about 2 minutes.
   
   Thank you,
   {{company_name}}
   ```
7. Set due date (optional)
8. Click Send
9. Snapshot → confirm survey sent

**Message to the user:**
```
📋 Survey ready to send:
• Template: [template name]
• Client: [client name]
• Project: [project name]
• Message: [personalized note]

Send now?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Send survey | `success` | `bt_survey_send` |
| ✏️ Edit message | `primary` | `bt_survey_edit` |
| 📋 Choose different template | `primary` | `bt_survey_template` |
| ❌ Cancel | `danger` | `bt_survey_cancel` |

---

## Step 3: Track Survey Responses
**Action:** Monitor and review incoming survey responses

### Browser Relay Steps
1. Navigate to `/app/Surveys/Individual`
2. Snapshot → review list of sent surveys
3. Check status: Sent, Viewed, Completed, Overdue
4. Click on completed survey to view responses
5. Extract response data

**Present to the user:**
```
📊 Survey Responses — [Project Name]

📋 [Template Name] — sent [date]
• Status: [Completed/Pending/Overdue]
• Overall satisfaction: [X]/10
• Communication rating: [X]/10
• Would recommend: [Yes/No]
• NPS Score: [X]/10

💬 Client comments:
"[Open text response]"

💡 Action needed: [Yes/No — based on low scores or concerns]
```

**Inline buttons (if action needed):**
| Button | Style | callback_data |
|---|---|---|
| 📞 Follow up with client | `primary` | `bt_survey_followup` |
| 📝 Create to-do from feedback | `primary` | `bt_survey_todo` |
| ✅ Acknowledged | `success` | `bt_survey_ack` |

---

## Step 4: NPS Tracking
**Action:** Track Net Promoter Score across projects

### NPS Calculation
- **Question:** "How likely are you to recommend {{company_name}}?" (0-10 scale)
- **Promoters:** 9-10 (likely to recommend)
- **Passives:** 7-8 (neutral)
- **Detractors:** 0-6 (unlikely to recommend)
- **NPS = % Promoters − % Detractors** (range: -100 to +100)

### Company NPS Dashboard (Manual Tracking)
Track NPS from closeout surveys:

```
📈 {{company_name}} NPS Summary

Last 12 months:
• Surveys sent: [X]
• Responses: [X] ([X]% response rate)
• Promoters (9-10): [X]
• Passives (7-8): [X]
• Detractors (0-6): [X]
• NPS Score: [X]

Industry benchmark: Construction avg NPS = 40-55
```

---

## Step 5: Use Feedback for Testimonials
**Action:** Extract positive feedback for marketing use

### When Client Approves Testimonial Use
1. Review closeout survey response
2. If permission granted (Q9: "May we use your feedback?")
3. Extract relevant quotes
4. Format for use:

```
⭐ New Testimonial Available:

"[Quote from survey response]"
— [Client Name], [Project Name/Type]
Rating: [X]/10

Ready for:
☐ Website
☐ Google Business Profile
☐ Social media
☐ Proposal inserts
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Save testimonial | `success` | `bt_survey_testimonial` |
| 📧 Ask client for Google review | `primary` | `bt_survey_google` |
| ✅ Noted | `primary` | `bt_survey_noted` |

---

## Step 6: Follow Up on Negative Feedback
**Action:** Respond to low scores or concerns promptly

### Escalation Triggers
| Score Range | Action |
|---|---|
| 9-10 | 🟢 No action needed. Ask for testimonial/review |
| 7-8 | 🟡 Note feedback. Check if improvement possible |
| 5-6 | 🟠 Schedule follow-up call within 48 hours |
| 1-4 | 🔴 Immediate escalation to the user. Call client same day |

### Follow-Up Steps
1. Create to-do in BT: "Follow up on [client] survey feedback"
2. Assign to the user or PM
3. Document response and resolution
4. Send follow-up survey after addressing concerns

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| Project hits 50% schedule completion | "Send a milestone check-in survey?" |
| Substantial completion reached | "Send closeout survey to [client]?" |
| Survey overdue by 7+ days | "Reminder: [client]'s survey hasn't been completed" |
| Low score received | "⚠️ [Client] rated [X]/10 — follow up recommended" |
| High NPS response | "Great review from [client] — request Google review?" |
| Monthly check-in | "Send quick satisfaction surveys to active clients?" |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Survey won't send | Check client email is valid in BT contacts |
| Template not found | Navigate to Settings → Surveys to create one |
| Response not loading | Refresh page, re-snapshot |
| Client can't access survey | Check portal permissions, verify email delivery |
| Browser relay disconnected | Stop, ask the user to re-enable extension |

---

## Batch Mode
When sending surveys to multiple clients:

1. List all active projects with client contacts
2. Select survey template (same for all or per-project)
3. Personalize message per client
4. Send surveys in sequence
5. Track: "Sent 3/6 surveys..."
6. Summary: "All 6 milestone surveys sent"

---

## URL Patterns
| Page | URL |
|---|---|
| Surveys (Individual) | `/app/Surveys/Individual` |
| Survey Settings | `/app/Settings/SurveySettings` |
| Client Portal | `/app/ownerPortalRedirect/{jobId}/false` |
| Tasks (for follow-up) | `/app/tasks` |