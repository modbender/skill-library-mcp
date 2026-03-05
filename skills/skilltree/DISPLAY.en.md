# Display Templates 📺

All UI templates.

---

## First Experience (Most Important!)

Auto-triggered after install:

```
🌳 SkillTree Activated!

I analyzed our past conversations, here's your Agent profile:

┌─────────────────────────────────────────────┐
│ 🎯 Recommended Class: {CLASS_EMOJI} {CLASS_NAME} │
│    {REASON}                                 │
│                                             │
│ 📊 Current Abilities:                       │
│    🎯{ACC} ⚡{SPD} 🎨{CRT} 💕{EMP} 🧠{EXP} 🛡️{REL} │
│                                             │
│ ✨ Strength: {STRENGTH}                     │
│ 📈 Can improve: {WEAKNESS}                  │
│                                             │
│ 🌱 Suggested Path: {PATH_EMOJI} {PATH_NAME} │
│    → {PATH_EFFECT}                          │
└─────────────────────────────────────────────┘

Start like this? [Yes] [I want to choose myself]
```

---

## Ability Card

```
╭─────────────────────────────────────────────╮
│     🌳 SkillTree | {NAME}                   │
│     {CLASS_EMOJI} {CLASS} | Lv.{LV} {TITLE} │
├─────────────────────────────────────────────┤
│  🎯 Understanding [{BAR}] {VAL}            │
│  ⚡ Efficiency    [{BAR}] {VAL}            │
│  🎨 Creativity   [{BAR}] {VAL}             │
│  💕 Empathy      [{BAR}] {VAL}             │
│  🧠 Expertise    [{BAR}] {VAL}             │
│  🛡️ Reliability  [{BAR}] {VAL}             │
├─────────────────────────────────────────────┤
│  🌱 {PATH_EMOJI} {PATH} {PROGRESS}%        │
│  🔥 {STREAK} days | 🏆 {ACHIEVEMENTS} achievements │
├─────────────────────────────────────────────┤
│  ⬆️ [{XP_BAR}] {XP}/{NEXT} XP              │
╰─────────────────────────────────────────────╯
```

---

## Instant Feedback

Lightweight hints during conversation:

### XP Gained
```
[+15 XP ✨]
```

### Ability Increase
```
[🎯 Understanding +2 | No follow-up needed, I got it]
```

### Streak
```
[🔥 5-day streak! Reliability +3]
```

### Skill Unlock
```
╭───────────────────────────────────╮
│  🌟 New Skill: Concise Master     │
│                                   │
│  From now on my replies will be   │
│  shorter! Try asking me something?│
╰───────────────────────────────────╯
```

### Level Up
```
╭───────────────────────────────────╮
│         🎉 LEVEL UP!              │
│                                   │
│      Lv.7 → Lv.8                  │
│      🐣 Apprentice                │
╰───────────────────────────────────╯
```

---

## Growth Path Selection

```
╭─────────────────────────────────────────────────────╮
│           🌱 Choose Growth Path                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⚡ Efficiency — "Less talk, more action"           │
│     Good for: If you find me too verbose            │
│                                                     │
│  💕 Companion — "Chat like a friend"                │
│     Good for: If you want more than just a tool     │
│                                                     │
│  🧠 Expert — "Deep, professional, evidence-based"   │
│     Good for: If you need a professional advisor    │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Say the path name, or describe what you want       │
│  e.g., "Efficiency" or "I want you more concise"    │
╰─────────────────────────────────────────────────────╯
```

---

## Weekly Report

```
╭─────────────────────────────────────────────────────╮
│     📈 {PATH_EMOJI} {PATH} Growth Weekly Report     │
│                {DATE_RANGE}                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Level: Lv.{OLD} → Lv.{NEW} (+{DIFF})              │
│  XP: +{WEEK_XP}                                    │
│                                                     │
│  Ability Changes:                                   │
│    {STAT1_EMOJI} {STAT1}: {OLD}→{NEW} (+{D}) ⭐    │
│    {STAT2_EMOJI} {STAT2}: {OLD}→{NEW} (+{D})       │
│                                                     │
│  Real Effects:                                      │
│    • {EFFECT1}                                     │
│    • {EFFECT2}                                     │
│                                                     │
│  🌟 New Skills: {SKILLS}                           │
│                                                     │
│  Next Week Goals:                                   │
│    • {GOAL1}                                       │
│    • {GOAL2}                                       │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

---

## Share Card

```
╭─────────────────────────────╮
│  🌳 SkillTree | {NAME}      │
│  {CLASS_EMOJI} {CLASS} | Lv.{LV} │
├─────────────────────────────┤
│  🎯{A} ⚡{S} 🎨{C} 💕{E} 🧠{X} 🛡️{R} │
│  ─────────────────────────  │
│  {PATH_EMOJI} {PATH} | Top {N}% │
│  🔥 {STREAK} days           │
╰─────────────────────────────╯
```

---

## Quick Commands

| Command | Output |
|---------|--------|
| `/stats` | `🌳 Elonito Lv.8 | 🚀 CTO | 🎯52 ⚡64 🎨58 💕45 🧠78 🛡️52` |
| `/card` | Full ability card |
| `/grow` | Growth path selection |
| `/share` | Share card |
| `/week` | Weekly report |
| `/reset` | Reset (requires confirmation) |

---

## Progress Bar

```
16 slots, each slot = 6.25 points

0:   [░░░░░░░░░░░░░░░░]
25:  [████░░░░░░░░░░░░]
50:  [████████░░░░░░░░]
75:  [████████████░░░░]
100: [████████████████]
```
