---
name: Proactive Claw
description: >
  🦞 The most powerful proactive engine for OpenClaw. Your personal assistant that learns from you and helps you be more productive.

version: 1.2.32

metadata:
  openclaw:
    requires:
      bins: [python3]
      config: [credentials.json, config.json]
    install:
      - kind: shell
        label: "Run scripts/setup.sh to install dependencies and configure Google OAuth or Nextcloud CalDAV"
---

# 🦞 Proactive Claw

Proactive Claw is a **proactive execution engine** that **collaborates with you** and **learns from you**.

It helps you be more productive by making smart suggestions at the right moment — and (by default) only applying what you approve.

**Everything can run locally.**

---

## Safety in one glance ✅

✅ Asks before applying changes (default)  
✅ Writes only what you approve (no surprise calendar edits)  
✅ Optional daemon (off by default)  
✅ Everything can run locally (small/local scoring model recommended)  
✅ Local state folder is transparent and deletable  

---

## Why people install it (what you feel in week 1)

- You show up prepared more often.
- Your calendar becomes more realistic (buffers appear where they matter).
- Deep work blocks stop getting shredded by “just one quick meeting.”
- Follow-ups stop slipping.
- Proactive Claw learns your style quickly:
  prep durations, preferred times, what you reject, what you always accept.

In short: it becomes your personal assistant.

---

## Graph A — the simple loop (how it works at a glance)

```text
+--------------------------+        +--------------------------+
| Calendar                 |        | Chat                     |
| Google Calendar/Nextcloud|        | (your control loop)      |
+------------+-------------+        +------------+-------------+
             |  events <-> suggestions           | prompts <-> decisions
             |                                   |
             +-------------------+---------------+
                                 |
                                 v
                  +--------------------------------------+
                  |            Proactive Claw             |
                  |  - notices what's coming              |
                  |  - prioritizes what matters           |
                  |  - suggests prep / buffers / followup |
                  |  - learns from your feedback          |
                  |  - applies only what you approve      |
                  +--------------------------------------+
```

**Key idea:** Proactive Claw is proactive, but you remain the decision-maker (by default).

---

## Quick start (2 minutes)

1) Install + bootstrap:
```bash
bash scripts/setup.sh
```

2) Run a safe preview:
```bash
python3 scripts/daemon.py --simulate
```

3) Approve a suggestion in chat, then run once:
```bash
python3 scripts/daemon.py
```

---

## Modes (choose your vibe)

- **Suggest (default):** asks before applying changes (`max_autonomy_level=confirm`)
- **Background suggestions:** optional daemon, still asks for approval
- **Autonomous (advanced):** explicit opt-in only (not recommended until you’ve used it for a while)

---

## Presets (easy setup)

You don’t need to tune dozens of settings. Pick a preset.

**Presets are just a starting point.** Proactive Claw adjusts to you with every interaction (approvals, edits, rejections), and quickly becomes personal.

### A) Calm mode (minimal interruptions)
Choose this if you want only high-value suggestions.
- fewer prompts
- only important events get prep/buffers

### B) Builder mode (deep work protected)
Choose this if you code/build and need long focus blocks.
- defends 2–3h deep work windows
- suggests moving meetings that fragment focus
- stronger buffers + recovery time

### C) Meetings-heavy week
Choose this when your schedule is packed.
- adds buffers + reset breaks
- prevents back-to-back collapse
- proposes follow-ups so action doesn’t slip

(If you want, these presets can be expressed as a small copy/paste block in `config.json`.)

---

## Chat scoring model (built-in; small/local recommended)

Proactive Claw includes a **chat scoring model** to rank signals (importance, urgency, disruption risk) so it knows:
- what matters,
- when to ask you,
- and when to stay quiet.

**Recommendation:** use a **small model**, ideally **local** (fast, cheap, private).  
Your planning model can be bigger; scoring should stay small and fast.

---

## Scenarios (mini transcripts)

### 1) Presentation tomorrow → prep + buffer
You: Tomorrow I’m presenting the roadmap to the board.  
Claw (score = 0.92): High impact. You usually prep ~70 minutes for presentations.  
Claw: Want me to reserve **08:40–09:50** for prep + a **10-min buffer** before the 10:00 meeting?

### 2) Deep work protection (developer mode)
Claw (score = 0.78): This meeting would split your deep work block (09:30–12:00).  
Claw: Prefer to **move it to 13:00**, or keep it and add a **20-min recovery buffer** after?

### 3) Back-to-back day → buffers + reset
Claw (score = 0.81): Tomorrow is back-to-back from 10:00–14:00.  
Claw: Add **10-min buffers** between meetings + a **25-min reset break** around midday?

### 4) Follow-up that tends to slip
You: I promised I’ll send the summary.  
Claw (score = 0.66): Time-sensitive.  
Claw: Want a **20-min follow-up block** right after the meeting (or at **17:10**)?

### 5) It becomes personal fast (recurring pattern)
Claw (score = 0.71): I’ve noticed a pattern for “Client Review” meetings:
- you prefer **30-min prep** the same day
- **10-min buffer** before
- no meetings after **18:00**  
Claw: Want me to propose this pattern whenever a new “Client Review” appears (still asking you to approve)?

---

## Graph B — technical architecture (backend = Google OR Nextcloud)

```text
TECHNICAL ARCHITECTURE (backend = Google OR Nextcloud)

             +----------------------------------------------+
             |        Calendar backend (choose ONE)         |
             |  +-----------------------+  OR  +----------+ |
             |  | Google (OAuth/API)    |      | Nextcloud| |
             |  +-----------------------+      | (CalDAV) | |
             |                                 +----------+ |
             +-----------------------+----------------------+
                                     ^
        events / changes (propose+apply, Actions only)       |
                                     |
                                     v
+----------------------+      +------------------------------------------+      +----------------------+
|  OpenClaw Chat UI    | <--> |           Proactive Claw Core            | <--> |  Local state         |
| prompts <-> decisions|      | 1) Ingest: events + chat signals         |      | config/token/SQLite  |
| feedback loop        |      | 2) Score: urgency/importance (local rec) |      | logs (optional)      |
+----------------------+      | 3) Plan : prep + buffers + follow-ups    |      +----------------------+
                              | 4) Approve (default): ask/confirm in chat|
                              | 5) Apply : write approved changes        |
                              | 6) Learn : from your approvals/edits     |
                              +------------------------------------------+
                                     ^
                                     |
                           Optional (explicit opt-in)
                                     |
                                     v
                              +----------------------+
                              | Optional daemon      |
                              | periodic scan/suggest|
                              +----------------------+
```

---

# Setup

## 0) Requirements
- `python3` available on your machine
- Google backend: `credentials.json` (OAuth client)  
  OR
- Nextcloud backend: CalDAV URL + app password (or token)

---

## 1) Install dependencies + bootstrap config
```bash
bash scripts/setup.sh
```

---

## 2) Choose your calendar backend

### Option A — Google Calendar (OAuth)
You provide:
- `credentials.json` (OAuth client)

Proactive Claw creates:
- `token.json` after OAuth

### Option B — Nextcloud (CalDAV)
You provide:
- CalDAV base URL
- app password

---

## 3) Configure behavior

Interactive wizard:
```bash
python3 scripts/config_wizard.py
```

Safe defaults:
```bash
python3 scripts/config_wizard.py --defaults
```

---

## 4) Optional background execution
```bash
bash scripts/install_daemon.sh
```

---

## FAQ

### Will this mess up my calendar?
By default: **no.** Proactive Claw suggests changes in chat and applies only what you approve (`max_autonomy_level = confirm`).

### Where does it store data?
Locally under:
`~/.openclaw/workspace/skills/proactive-claw/`

### Does everything run locally?
Yes — it can. The scoring model is recommended to be small/local. The calendar backend still connects to your chosen provider because that’s where your calendar lives.

### Can I use it without Google?
Yes — use **Nextcloud (CalDAV)**.

### What is the optional daemon?
A user-level scheduler (no sudo) that runs periodically so Proactive Claw can suggest proactively. It is **off by default**.

### What does “learning” mean here?
It learns your preferences from your approvals/edits over time: prep durations, preferred times, buffer sizes, meeting types that matter, and deep work rules.

### What is the chat scoring model?
A lightweight model that assigns numeric scores (e.g., 0.66, 0.92) to decide what matters and when to prompt you. Recommended: small/local model.

---

## Troubleshooting (by symptom)

- **“Too many prompts”** → use Calm mode; reject a few times; it will adapt  
- **“Not proactive enough”** → enable daemon; increase sensitivity  
- **“Prep blocks are wrong length”** → edit them twice; it will converge  
- **“OAuth issues”** → re-run setup; revoke token and re-auth if needed  

---

## Uninstall

1) Remove daemon (if installed)  
2) Delete:
`~/.openclaw/workspace/skills/proactive-claw/`  
3) Revoke Google OAuth access if you used Google:
myaccount.google.com/permissions

---

## Glossary

- **Prep block:** time reserved before an event to prepare  
- **Buffer:** short gap that prevents schedule collisions  
- **Deep work:** uninterrupted focus block  
- **Daemon:** optional background scheduler (off by default)  
- **Score:** 0–1 number indicating importance/urgency  

---

## To improve this 100×, here’s what would help:
1) Your config key list (or config.example.json) so I can turn presets into copy/paste blocks safely.  
2) Whether you want scores displayed as `0.92` or `92/100` (both numeric; one is friendlier).  
3) If you want an “Advanced” section for autonomous mode or prefer to keep it out of the main doc.
