# Delivery Channels & Scheduling

How and when reports get delivered.

---

## Scheduling

Reports run via cron. Common patterns:

| Schedule | Cron | Use Case |
|----------|------|----------|
| Daily 9am | `0 9 * * *` | Standups, health |
| Weekly Monday | `0 9 * * 1` | Business reviews |
| Biweekly | `0 9 * * 1/2` | Sprint reports |
| Monthly 1st | `0 9 1 * *` | Financial summaries |
| Quarterly | `0 9 1 1,4,7,10 *` | OKRs, big picture |

**Multiple schedules per report:**
```markdown
## Schedule
- **Quick:** daily, 09:00, chat
- **Summary:** weekly, Monday, chat
- **Archive:** monthly, 1st, pdf+file
```

---

## Channels

### Telegram (Default)
```
message action=send message="📊 Report..."
message action=send filePath="/path/to/report.pdf"
```

### File System
```
~/report/{name}/generated/
├── 2024-02-weekly.pdf
├── 2024-02-weekly.html
└── 2024-02-weekly.json
```

### Email (If Configured)
Requires email skill + SMTP credentials.

### Webhook
POST JSON to external URL for integrations.

---

## Setting Up Scheduled Reports

When user creates report with schedule:

```
cron action=add job={
  "name": "{report-name}-{frequency}",
  "schedule": {"kind": "cron", "expr": "0 9 * * 1"},
  "payload": {
    "kind": "agentTurn",
    "message": "Generate {report-name} report and deliver via {channel}"
  },
  "sessionTarget": "isolated"
}
```

---

## Data Prompts

If report needs input before generation:

1. **Prompt job** runs before report time
2. Asks user for data
3. Stores in `data.jsonl`
4. **Report job** generates with latest data

Example: Prompt Sunday 8pm, Report Monday 9am

---

## Delivery Failures

If primary channel fails:
1. Retry once after 5 min
2. Fall back to file system (always works)
3. Note failure in next interaction
4. Log to `~/report/{name}/delivery.log`

---

## On-Demand Generation

User can always request:
```
"Run my freelance report"
"Generate monthly summary now"
"Show me the health report"
```

Generates immediately with latest data.
