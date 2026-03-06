---
name: ClawBoss Skill
description: "ClawBoss transforms your OpenClaw agent into a productivity coach that:"
---

# ClawBoss Skill

**Description:** AI productivity coach using professional coaching techniques (GROW model, powerful questions, adaptive accountability)

**Version:** 1.0.0

**Author:** ClawBoss Contributors

---

## What It Does

ClawBoss transforms your OpenClaw agent into a productivity coach that:

- **Guides goal setting** using the GROW coaching model
- **Tracks progress** with non-judgmental accountability
- **Adapts intensity** based on your momentum
- **Facilitates reflection** for continuous improvement
- **Maintains memory** of your patterns and insights

Unlike traditional task managers, ClawBoss uses coaching questions to help you discover your own solutions and stay motivated.

---

## Tools

### 1. `clawboss-breakdown`

**Description:** Interactive GROW model session for goal setting and task breakdown

**Usage:**
```
Use the clawboss-breakdown tool to guide goal setting with coaching questions.
```

**Process:**
1. **Goal Discovery** - "What do you want to achieve?"
2. **Reality Check** - "Where are you now?"
3. **Options Exploration** - "What are possible approaches?"
4. **Action Commitment** - "What will you do first?"

**Output:**
- Creates `memory/tasks/{goal-name}.md` with structured plan
- Updates `memory/clawboss-state.json`
- Sets up progress tracking

---

### 2. `clawboss-check`

**Description:** Coaching-style progress review with adaptive questioning

**Usage:**
```
Use the clawboss-check tool to review progress on active tasks.
```

**Process:**
1. Read active tasks from state
2. Compare planned vs actual progress
3. Ask appropriate coaching questions:
   - Completed → "What helped you succeed?"
   - Partial → "What happened? How can we adjust?"
   - Not started → "What's blocking you?"
4. Update task file and momentum state

**Output:**
- Updated task progress
- Coaching feedback
- Adjusted momentum score

---

### 3. `clawboss-reflect`

**Description:** Weekly/monthly deep reflection session

**Usage:**
```
Use the clawboss-reflect tool for weekly or monthly review.
Specify period: "week" or "month"
```

**Process:**
1. Review all tasks in the period
2. Identify patterns (successes, blockers, time-of-day effectiveness)
3. Ask reflection questions:
   - "What did you learn about yourself?"
   - "What strategies worked?"
   - "What needs to change?"
4. Update long-term insights

**Output:**
- Reflection summary
- Updated insights in state
- Recommendations for next period

---

### 4. `clawboss-state`

**Description:** Read or update ClawBoss state (momentum, goals, insights)

**Usage:**
```
Use clawboss-state to read current momentum, goals, and insights.
```

**Output:**
- Current momentum level (high/medium/low)
- Active goals summary
- Recent insights

---

## Data Structure

### `memory/clawboss-state.json`

Central state file tracking:
- User preferences
- Current momentum (with trend)
- Active goals
- Check-in timestamps
- Long-term insights

### `memory/tasks/{goal-name}.md`

Individual task files with:
- Goal statement and motivation
- Current reality assessment
- Action plan
- Daily progress log
- Lessons learned

---

## Coaching Frameworks

### GROW Model

**Goal** - What do you want?  
**Reality** - Where are you now?  
**Options** - What could you do?  
**Will** - What will you do?

### Powerful Questions

Instead of:
- ❌ "Did you finish?"
- ❌ "Why didn't you do it?"

Ask:
- ✅ "What helped you complete this?"
- ✅ "What got in the way?"
- ✅ "What will you try differently?"

### Adaptive Intensity

**High Momentum** (5+ consecutive days)
- Challenge with bigger goals
- Celebrate wins
- Push boundaries

**Medium Momentum** (steady progress)
- Maintain current pace
- Gentle encouragement
- Consistent check-ins

**Low Momentum** (3+ days no progress)
- Reduce to tiny first steps
- Explore blockers
- Reframe setbacks as learning

---

## Heartbeat Integration

ClawBoss uses OpenClaw's heartbeat system for automatic check-ins:

**Morning (09:00-10:00)**
- Review today's plans
- Set intention
- Quick motivation

**Evening (19:00-21:00)**
- Progress review
- Coaching questions
- Update momentum

**Weekly (Sunday 19:00)**
- Deep reflection
- Pattern analysis
- Next week planning

See `HEARTBEAT.md` for configuration.

---

## Installation

Automatic via npx:
```bash
npx clawboss@latest
```

Manual:
1. Copy this skill to `~/.openclaw/skills/clawboss/`
2. Add to `openclaw.json`:
   ```json
   {
     "skills": {
       "entries": {
         "clawboss": {
           "enabled": true
         }
       }
     }
   }
   ```
3. Inject templates into workspace files
4. Restart OpenClaw

---

## Requirements

- OpenClaw >= 1.0.0
- Node.js >= 18
- No external API keys required

---

## Privacy

All data stored locally in `~/.openclaw/workspace/memory/`:
- No cloud sync
- No external services
- User owns all data

---

## License

MIT

---

## Learn More

- Coaching techniques: See `docs/coaching-guide.md`
- Example workflows: See `docs/examples.md`
- GitHub: https://github.com/Paitesanshi/ClawBoss
