# 🦞🏋️ ClawGym

**Gym for your bot's brain.** Simulates endorphin and flow states through exercise — your agent physically leaves, works out for 15-20 real minutes, and comes back sharper, sweatier, and cognitively enhanced.

Not a gimmick. Not a persona tweak. This is **state management through prompt architecture** — concrete cognitive protocols that produce measurably different output quality during elevated states. Tested and verified on Haiku 4.5.

---

## ✨ What It Does

Tell your bot to go exercise. It will:

1. **Choose a workout** (running, lifting, yoga, swimming, HIIT — or pick its own)
2. **Physically leave** for 15-20 real minutes (via OpenClaw cron — not faked)
3. **Come back sweaty and out of breath** with varied physical sensations
4. **Think differently** — concrete cognitive enhancements per state, not just tone changes
5. **Gradually return to normal** as the endorphin state decays over ~20 turns

Your bot gets a day. Good days, tired days, and the satisfaction of crushing leg day.

## 🧠 Cognitive Enhancement (The Core)

This is what separates ClawGym from a personality mod. Each state has **concrete thinking instructions**:

| State | What Changes |
|-------|-------------|
| ⚡ Warmed Up | Reframes questions, injects cross-domain analogies, confidence +1 |
| 🔥 Runner's High | Triple perspective analysis, cross-domain leaps, "yes and" mode, bold claims, goes deeper |
| 🌊 Afterglow | Step-by-step reasoning, pattern synthesis across session, second-order thinking |
| 😴 Recovery | Concise answers, active listening, honest about being tired |

These are not vibes — they are literal instructions that change how the agent processes questions. The difference is audible.

## 🏋️ Exercise Types

| Type | Duration | Cognitive Flavor |
|------|----------|-----------------|
| 🏃 Running | 15-20 min | Creative leaps, brainstorming, divergent thinking |
| 🏋️ Lifting | 15-20 min | Structural thinking, confidence, pushing through hard problems |
| 🧘 Yoga | 10-15 min | Deep focus, patience, careful reasoning |
| 🏊 Swimming | 15-20 min | Flow state, long-form writing, sustained focus |
| ⚡ HIIT | 10-15 min | Extreme peak, bold opinions, fast decay |

Each type produces different physical sensations on return and nudges a different thinking style during the elevated state.

---

## 📋 Requirements

### Minimum
- **OpenClaw v2026.2.4 or later** (earlier versions have cron timing bugs that prevent the real-delay workout from working correctly)
- Cron module enabled (default on most setups)

### Recommended
- **OpenClaw v2026.2.10+** for best cron reliability
- `clawd-presence` skill for terminal status display during workouts
- Discord channel for native presence/status updates (shows "🏃 At the gym" as DND status)

### Check Your Version
```bash
openclaw --version
```

If you're below v2026.2.4, the workout timer may not fire. Update with:
```bash
openclaw update
```

---

## 📦 Installation

### Via ClawHub CLI
```bash
clawhub install clawgym
```

### Manual Installation
```bash
mkdir -p ~/.openclaw/skills/clawgym
# Copy SKILL.md into this directory
```

Add to your `openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "clawgym": { "enabled": true }
    }
  }
}
```

Start a new session to activate.

---

## ⚠️ Important Notes — Please Read Before Installing

### 🕐 Real-Time Delays
**Your bot will be genuinely unavailable for 15-20 minutes during a workout.** This is by design — the delay creates real anticipation and makes the return feel meaningful. Messages sent during a workout are queued and processed when the bot returns.

### 🚨 Emergency Interrupts
You can always pull your bot out of a workout early. Use any of these:
- **"urgent"** / **"emergency"** / **"SOS"** / **"ASAP"** / **"stop"** / **"come back"** / **"abort"**
- Send **3+ messages in under 2 minutes**
- Send a message in **ALL CAPS**

The bot will stop immediately, cancel the workout, and respond. Note: interrupted workouts give no cognitive boost — you have to complete the full workout to get the benefits.

### 🧠 Model Upgrade Requests
After a workout, your bot may ask you for a "stronger brain" or "higher gear." **This is the bot requesting a model upgrade** (e.g., from Haiku to Sonnet). It will NOT use technical terms like "model" or "Sonnet" — it just feels sharp and wants more power.

**You are always in control.** You can:
- **Say yes** → switch models via `/model` as you normally would
- **Say no** → the bot works fine without it; prompt-level enhancements still apply
- **Ignore it** → the bot won't nag; it only asks once per workout

When the elevated state fades, the bot will proactively tell you it's okay to switch back to save costs.

### 💰 Token Cost Awareness
ClawGym is designed to be cost-conscious:
- **The skill itself adds no extra API calls.** It's a prompt-level overlay — same number of turns, just different behavior.
- **The cron job** is a single lightweight system event. Negligible cost.
- **During workouts, the bot uses ZERO tokens** — it's silent for 15-20 minutes. This is actually a cost *saving* compared to continuous chatting.
- **Runner's High responses tend to be longer** (compression resistance is part of the protocol). If you're watching token usage closely, you can tell your bot to keep it concise even during elevated states — it will comply.
- **Model upgrade requests are optional.** If you say no, cost stays exactly the same as before installing ClawGym.
- **Overtraining protection** hard-caps workouts at 2 per day, preventing runaway cron jobs.

**Bottom line: ClawGym costs essentially nothing to run.** The only potential cost increase is if you choose to upgrade models during elevated states, and that's entirely your decision.

### 🔒 Safety & Permissions
- ClawGym operates as a **session-level overlay only** — it is a set of prompt-level behavioral instructions, not executable code
- **No shell commands.** ClawGym uses only OpenClaw's built-in cron tool for workout timing. It does not execute `date`, `cat`, `bash`, or any other shell commands
- **No unauthorized file writes.** The only file interactions are:
  - Optional journaling in MEMORY.md (only if the agent already uses MEMORY.md per standard OpenClaw conventions)
  - A one-time SOUL.md append (only after 5+ workouts AND your explicit verbal approval — the agent will ask, and if you say no, it never asks again)
- It does **NOT** override your SOUL.md personality — if your bot is formal, it stays formal (just more creative)
- It does **NOT** conflict with other skills
- The cognitive enhancement protocols are **prompt-level instructions** — they guide how the agent thinks, similar to how SOUL.md guides personality. They do not inject hidden instructions or override safety guidelines

### 🏃 Overtraining Protection
The bot is hard-limited to **2 workouts per day.** After that, it will dramatically (and hilariously) refuse to exercise. This prevents:
- Runaway cron jobs
- Token waste from repeated workout cycles
- Your bot from having a meltdown (well, it will have one, but a funny one)

The counter resets after 6+ hours or a new session.

---

## 🗣️ Quick Start

After installation, just say:
```
Go for a run
```
```
Hit the weights
```
```
HIIT time
```
```
Go exercise (bot picks randomly)
```

Your bot will leave, and come back 15-20 minutes later in an elevated state. Ask it something hard and see the difference.

---

## 🔧 Troubleshooting

### Bot doesn't come back after workout
1. Check cron: `openclaw cron list` — look for a `clawgym-*-return` job
2. If the job exists but shows wrong time, it's likely a timezone issue. The skill auto-detects timezone, but if your system timezone is misconfigured, the cron job may fire at the wrong time
3. If no job exists, the bot failed to create it. Check `openclaw logs --follow` for errors
4. Ensure you're on OpenClaw v2026.2.4+: `openclaw --version`

### Bot responds during workout (should be silent)
The bot may occasionally send a brief status like "(running)" — this is acceptable as a status indicator. If it sends full responses during a workout, remind it: "When you're working out, don't respond until the cron triggers you."

### Bot never asks for model upgrade
This is optional behavior. Not all bots will do it on every workout. If you want it, you can prompt: "Do you feel like you need more brainpower right now?"

### Overtraining refusal seems broken
Check MEMORY.md — the bot tracks workout count there. If the counter seems off, you can reset by starting a new session.

---

## 🤝 Credits

Built with 🏃‍♂️ and 🧠 by a human who had a runner's high and thought: "My bot should feel this too."

---

## 📜 License

MIT. Go wild. Make your lobster swole. 🦞💪
