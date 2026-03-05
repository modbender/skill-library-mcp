# Water Coach Setup

**First-time only**

---

## Data Location

User data is stored in: `memory/data/` (outside skill folder)
- `memory/data/water_config.json`
- `memory/data/water_log.csv`
- `memory/data/body_metrics.csv`

---

## Setup Checklist

- [ ] Create data files (auto-created on first run)
- [ ] Ask user weight
- [ ] **CONFIRM goal with user**
- [ ] Set up cron jobs
- [ ] Configure heartbeat
- [ ] Run python tests

---

## 1. Create Data Files

The data folder is created automatically on first run:
```bash
python3 skills/water-coach/scripts/water_coach.py water status
```

---

## 2. Ask User Weight

**Required.** Ask: "What's your weight?"

```bash
python3 skills/water-coach/scripts/water_coach.py water set_body_weight 80
```

---

## 3. CONFIRM Goal (IMPORTANT!)

> **GOAL is USER'S CHOICE, not automatic!**

After setting weight, agent MUST ask:

```
"Your weight is 80kg. 
Based on this, the suggested goal is 2800ml (80 × 35ml).

Is this goal OK for you? 
Or do you want a different goal? (e.g., doctor recommended 1.5L)"
```

If user wants different goal:
```bash
# Update config manually or ask user their preferred goal
```

---

## 4. Cron Jobs (Base Notifications)

| Job | Time | Command |
|-----|------|---------|
| Morning | 9am | water status |
| Lunch | 12pm | water status |
| Afternoon | 3pm | water status |
| Pre-dinner | 6pm | water status |
| Evening | 9pm | water status |

---

## 5. Cron Jobs (Briefings)

| Job | Time | Command |
|-----|------|---------|
| Weekly | Sunday 8pm | analytics week |
| Monthly | 2nd day 8pm | analytics month |

---

## 6. Heartbeat (Dynamic Extras)

Update HEARTBEAT.md:

```markdown
## Water Coach Dynamic

Execute: python3 skills/water-coach/scripts/water_coach.py water dynamic

If should_send: true → send + increment
```

---

## 7. Tests

```bash
python3 -m pytest skills/water-coach/scripts/test/test_water.py -v
```

---

## Verify Setup

```bash
# Check config
python3 skills/water-coach/scripts/water_coach.py water status

# Check goal
python3 skills/water-coach/scripts/water_coach.py water goal
```
