# Output Formats

How reports are rendered.

---

## Chat Message

**Best for:** Quick updates, daily reports, alerts

```
📊 {Report Name} — {Date}

• Metric 1: Value (↑↓→ trend)
• Metric 2: Value
• Metric 3: Value

⚠️ Alert: {if any}

{One-line insight}
```

**Rules:**
- Max 7 metrics
- Show trends (↑↓→)
- Keep under 500 chars
- Lead with most important

---

## PDF

**Best for:** Formal reports, sharing, archival

**Structure:**
1. Title + date range
2. Executive summary (3 bullets)
3. Metrics table with trends
4. Alerts section
5. Historical comparison
6. Notes/context

**Generation:**
1. Create HTML with print-friendly CSS
2. `browser action=pdf targetUrl=file:///path.html`
3. Save to `~/report/{name}/generated/`

---

## HTML

**Best for:** Detailed analysis, web viewing

```html
<!DOCTYPE html>
<html>
<head>
  <title>{Report} — {Date}</title>
  <style>/* Clean styles */</style>
</head>
<body>
  <h1>{Report Name}</h1>
  <p class="period">{Date Range}</p>
  
  <section class="metrics">
    <table>...</table>
  </section>
  
  <section class="trends">
    <!-- Historical data -->
  </section>
</body>
</html>
```

---

## JSON

**Best for:** Data export, integrations, backups

```json
{
  "report": "freelance",
  "generated": "2024-02-13T09:00:00Z",
  "period": {"start": "2024-02-05", "end": "2024-02-11"},
  "metrics": {
    "revenue": {"value": 3400, "previous": 3150, "change": 0.08},
    "hours": {"value": 34, "previous": 32, "change": 0.06}
  },
  "alerts": []
}
```

---

## Format Selection

| Situation | Format |
|-----------|--------|
| Daily check-in | Chat |
| Weekly summary | Chat or PDF |
| Monthly review | PDF |
| Sharing externally | PDF |
| Data backup | JSON |
| Detailed analysis | HTML |

---

## Multiple Formats

One report can generate multiple formats:

```markdown
## Format
- **Primary:** chat (always)
- **Archive:** pdf (save to file monthly)
- **Export:** json (weekly backup)
```
