# OKR Visualization & Display Patterns

## Core Visualization Principles

1. **Glanceable** — Status visible in <3 seconds
2. **Hierarchical** — Company → Team → Individual flow
3. **Progress-forward** — Show trajectory, not just current state
4. **Action-oriented** — Red items demand attention

---

## Status Indicators

### Traffic Light (Most Common)
```
🟢 On Track    (0.7-1.0 or 7-10 confidence)
🟡 At Risk     (0.4-0.6 or 4-6 confidence)  
🔴 Off Track   (0.0-0.3 or 0-3 confidence)
⚪ Not Started (no data yet)
```

### Progress Bars
```
KR1: [████████░░] 80%
KR2: [█████░░░░░] 50%
KR3: [██░░░░░░░░] 20%
```

### Confidence Indicators
```
KR1: ████████░░ 8/10 🟢
KR2: █████░░░░░ 5/10 🟡
KR3: ██░░░░░░░░ 2/10 🔴
```

### Trend Arrows
```
↑ Improving
→ Stable
↓ Declining
```

Combine: `🟡↑` = At risk but improving

---

## Dashboard Layouts

### Executive View (Company Level)
```
┌─────────────────────────────────────────────────┐
│              Q1 2026 OKR DASHBOARD              │
├─────────────────────────────────────────────────┤
│ Overall Score: 0.62 │ On Track: 8 │ At Risk: 4 │
├─────────────────────────────────────────────────┤
│ OKR 1: AI & Automation        🟡 0.55   ↑       │
│ OKR 2: EDI Infrastructure     🟢 0.75   →       │
│ OKR 3: IT Modernization       🟡 0.48   ↓       │
│ OKR 4: $100K Cost Savings     🟢 0.70   ↑       │
└─────────────────────────────────────────────────┘
```

### Team View (Objective Detail)
```
┌─────────────────────────────────────────────────┐
│ OKR 1: AI & AUTOMATION IMPACT           🟡 0.55 │
├─────────────────────────────────────────────────┤
│ KR1: AI notetaker 100%    [██████░░░░] 60% 🟡   │
│ KR2: 3 AI automations     [████░░░░░░] 40% 🟡   │
│ KR3: 5 AI use cases       [██░░░░░░░░] 20% 🔴   │
│ KR4: Spec sheet 1hr→5min  [████████░░] 80% 🟢   │
│ KR5: GPO matching         [█████░░░░░] 50% 🟡   │
└─────────────────────────────────────────────────┘
```

### Individual View (KR Detail)
```
┌─────────────────────────────────────────────────┐
│ KR1: Deploy AI notetaker to 100% by Mar 31     │
├─────────────────────────────────────────────────┤
│ Owner: Project Lead          │ Due: March 31           │
│ Target: 100%         │ Current: 60%            │
│ Status: 🟡 At Risk   │ Confidence: 6/10        │
├─────────────────────────────────────────────────┤
│ Progress Timeline:                              │
│ W1 ░░ → W3 ██ → W5 ████ → W7 ██████ → Now      │
├─────────────────────────────────────────────────┤
│ Last Update: "Onboarding delayed by IT backlog" │
│ Blocker: Need IT to prioritize license setup    │
└─────────────────────────────────────────────────┘
```

---

## Discord-Specific Formats

### Thread Header (Pinned Message)
```
# 🎯 OKR 1: AI & Automation Impact

**Status:** 🟡 At Risk | **Score:** 0.55 | **Owner:** Project Lead

| KR | Status | Progress | Confidence |
|----|--------|----------|------------|
| 1. AI notetaker to 100% | 🟡 | 60% | 6/10 |
| 2. 3 AI automations | 🟡 | 40% | 5/10 |
| 3. 5 AI use cases | 🔴 | 20% | 3/10 |
| 4. Spec sheet 1hr→5min | 🟢 | 80% | 8/10 |
| 5. GPO distributor matching | 🟡 | 50% | 5/10 |

*Last updated: Feb 12, 2026*
```

### Weekly Update (Thread Reply)
```
**📊 Week 6 Update**

🟢 **KR4** (Spec sheet): Up to 80%! Testing this week.
🟡 **KR1** (Notetaker): Stuck at 60%, IT backlog
🟡 **KR2** (Automations): 2/3 done, last one in QA
🔴 **KR3** (Use cases): Need to schedule workshops ASAP
🟡 **KR5** (GPO): Prototyping matching algorithm with AI assistant

**Blockers:** IT ticket #4521 (notetaker licenses)
**Help needed:** Push on IT prioritization
```

---

## Alignment Visualization

### Vertical Cascade View
```
COMPANY OKR
│
├── TEAM A OKR
│   ├── Individual 1 OKR
│   └── Individual 2 OKR
│
└── TEAM B OKR
    ├── Individual 3 OKR
    └── Individual 4 OKR
```

### Dependency Matrix
```
         │ Team A │ Team B │ Team C │
─────────┼────────┼────────┼────────┤
Team A   │   -    │   ←    │        │
Team B   │   →    │   -    │   ←    │
Team C   │        │   →    │   -    │

→ = depends on
← = depended upon by
```

---

## Reporting Cadences

### Weekly Snapshot
- Traffic light status for each KR
- Blockers list
- Top 3 priorities this week

### Monthly Summary
- Score trend (was X, now Y)
- Highlights and lowlights
- Dependency status
- Forecast: on track to hit? miss? by how much?

### End-of-Quarter Report
- Final scores with evidence
- Key learnings
- Recommendations for next quarter
- What to carry forward, what to drop
