# Report Configuration Schema

Every report has a `config.md` following this structure.

---

## Full Schema

```markdown
# {Report Name}

## Metadata
- **Created:** YYYY-MM-DD
- **Status:** active | paused | archived

## Schedule
- **Frequency:** daily | weekly | monthly | on-demand
- **Time:** HH:MM (24h format)
- **Day:** Monday (for weekly) | 1 (for monthly)
- **Timezone:** Europe/Madrid

## Metrics

| Metric | Type | Input | Description |
|--------|------|-------|-------------|
| revenue | currency | manual | Weekly income |
| hours | number | prompt | Hours worked |
| rate | calculated | hours/revenue | Effective rate |

## Format
- **Primary:** chat | pdf | html
- **Secondary:** (optional additional format)

## Delivery
- **Channel:** telegram | file | email
- **Recipients:** (if email)

## Alerts (optional)

| Metric | Condition | Level |
|--------|-----------|-------|
| revenue | < 2000 | high |
| hours | > 50 | medium |

## Data Prompt (if input=prompt)
"Weekly update: hours worked and total revenue?"
```

---

## Field Options

### Schedule Frequencies
| Value | Meaning |
|-------|---------|
| daily | Every day |
| weekly | Once per week |
| biweekly | Every 2 weeks |
| monthly | Once per month |
| quarterly | Every 3 months |
| on-demand | Only when requested |

### Metric Types
| Type | Example |
|------|---------|
| number | hours, count, score |
| currency | revenue, expenses |
| percentage | growth, utilization |
| text | status, notes |
| boolean | completed, active |

### Input Methods
| Method | Description |
|--------|-------------|
| manual | User provides anytime |
| prompt | Agent asks before report |
| api | Fetched automatically |
| calculated | Derived from others |

### Alert Levels
| Level | Behavior |
|-------|----------|
| critical | Immediate notification |
| high | Same day notification |
| medium | Include in next report |
| low | Note in report only |

---

## Minimal Config

Simplest valid report:

```markdown
# Daily Standup

## Schedule
- **Frequency:** daily
- **Time:** 09:00

## Metrics
| Metric | Type | Input |
|--------|------|-------|
| yesterday | text | prompt |
| today | text | prompt |
| blockers | text | prompt |

## Format
- **Primary:** chat

## Delivery
- **Channel:** telegram

## Data Prompt
"Standup time! What did you do yesterday? What's the plan today? Any blockers?"
```

---

## Multiple Schedules

One report, different frequencies:

```markdown
## Schedule
- **Quick update:** daily, 09:00, chat
- **Full report:** weekly, Monday 09:00, pdf
- **Archive:** monthly, 1st, html+file
```

Each schedule can have different format/delivery.

---

## Validation

Before creating report:
- [ ] Name is unique (no duplicate in ~/report/)
- [ ] At least one metric defined
- [ ] Schedule frequency set (or on-demand)
- [ ] Format specified
- [ ] Delivery channel valid
