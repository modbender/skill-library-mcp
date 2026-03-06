---
name: apprentice
version: "1.0.0"
description: Watch-me-once workflow learning. Say "watch me" and do a task — apprentice observes every step, understands your intent, and turns it into a permanent, repeatable skill your agent can run forever. Programming by demonstration. No code. No specs. Just do it once. Triggers on "watch me", "learn this", "remember how I do this", "apprentice mode", "teach you something", "run [workflow-name]", "what have you learned", or "replay [workflow-name]".
homepage: https://github.com/Taha2053/apprentice
metadata:
  clawdbot:
    emoji: "🎓"
    requires:
      env: []
    files:
      - "scripts/*"
      - "workflows/*"
---

# Apprentice — Watch Me Once. Do It Forever.

> The entire history of computing: you describe what you want → the computer executes.
> Apprentice flips it: you do what you want → the agent watches → it becomes a permanent skill.

This is **Programming by Demonstration** — a 30-year holy grail of human-computer interaction research. Every attempt failed because it required constrained environments or rigid formal specifications. LLM agents make it possible for the first time:

- Watch what you actually do (not what you say you do)
- Understand your intent, not just your actions
- Generalize across contexts — knowing what's a variable vs. what's a constant
- Turn it into a repeatable workflow your agent can run, refine, and chain forever

---

## External Endpoints

| Endpoint | Purpose | Data Sent |
|---|---|---|
| None | Fully local | Nothing leaves your machine |

Apprentice records locally. All synthesis happens via your already-running LLM session. No external APIs.

---

## Security & Privacy

- **Zero external calls.** Observation logs, workflow files, and all synthesis happen locally.
- **No credentials accessed.** Apprentice observes what you tell it — it doesn't read system files or intercept your input at an OS level.
- **You review before saving.** After observation, you see the synthesized workflow and approve it before it's saved as a permanent skill.
- **Sandboxed execution.** Generated workflow run scripts are plain bash with full security manifest headers.

> **Trust Statement:** Apprentice writes observation logs and workflow SKILL.md files locally. The only thing it sends to the LLM is your described observation + synthesis request, using your existing session. Nothing leaves your machine.

---

## Model Invocation Note

Apprentice is always user-initiated. It activates on "watch me" or equivalent phrases, and pauses until you say "done" or "stop watching." Synthesis runs once per observation session, with your review before saving. Workflows execute only when explicitly invoked.

---

## How It Works

### Step 1 — Start Observation
```
"Watch me"
"Apprentice mode on"
"Learn this"
"I'm going to show you how I do X"
```
The agent enters observation mode. It listens and records your actions.

### Step 2 — Do the Task Naturally
Just do what you normally do. Talk out loud if it helps — the agent hears everything:
- Commands you run
- Files you create, edit, or delete
- Decisions you make and why
- The order of steps
- What changes between runs (variables) vs. what stays constant

You don't need to be formal. "Now I update the README with the project name" is enough.

### Step 3 — Stop Observation
```
"Done"
"Stop watching"
"That's it"
"End observation"
```

### Step 4 — Review the Synthesis
Apprentice shows you:
- **What it understood** as the workflow name and purpose
- **The steps** it identified, in order
- **The variables** it detected (things that change each run)
- **The constants** (things that stay the same)
- **The generated workflow** as a readable, editable description

You approve, edit, or reject.

### Step 5 — It's a Permanent Skill
Approved workflows live in `apprentice/workflows/` as named SKILL.md files. Your agent can:
```
"Run new-project-setup"
"Do the weekly-report workflow with topic=AI agents"
"What workflows have you learned?"
"Replay morning-routine"
```

---

## Example: Learning a Workflow

**User:**
```
"Watch me set up a new project"
```

**[User does the following, narrating out loud]:**
```
mkdir projects/client-dashboard
cd projects/client-dashboard
cp -r ~/templates/react-starter .
sed -i 's/TEMPLATE_NAME/client-dashboard/g' README.md
git init
git remote add origin git@github.com:myorg/client-dashboard.git
echo "Done — this is how I start every new project"
```

**User:**
```
"Done watching"
```

**Apprentice responds:**
```
🎓 OBSERVATION COMPLETE — New Project Setup

What I understood:
  Purpose: Initialize a new project from template
  Name: "new-project-setup"

Steps I identified:
  1. Create project directory with name [PROJECT_NAME]
  2. Copy React starter template
  3. Replace template placeholder with [PROJECT_NAME] in README
  4. Initialize git repository
  5. Add remote origin at [GIT_ORG]/[PROJECT_NAME]

Variables (change each run):
  • PROJECT_NAME — the new project's name
  • GIT_ORG — your GitHub organization (default: myorg)

Constants (same every time):
  • Template source: ~/templates/react-starter
  • README placeholder: TEMPLATE_NAME

Does this look right? [Accept] [Edit] [Reject]
```

**Next time:**
```
"New project setup for analytics-redesign"
→ Agent runs all 5 steps automatically with PROJECT_NAME=analytics-redesign
```

---

## Trigger Phrases

**Start observation:**
```
"Watch me"
"Apprentice mode"
"Learn this"
"Remember how I do this"
"I'll show you"
"Teaching you something"
```

**Stop observation:**
```
"Done"
"Stop watching"
"That's it"
"Got it?"
"End lesson"
```

**Run a workflow:**
```
"Run [workflow-name]"
"Do the [workflow-name] workflow"
"[workflow-name] with [variable=value]"
"Replay [workflow-name]"
```

**Manage workflows:**
```
"What have you learned?"
"Show me my workflows"
"Delete [workflow-name]"
"Edit [workflow-name]"
"When did you learn [workflow-name]?"
```

---

## What Makes a Good Observation

The more context you give, the better Apprentice understands:

✅ **Talk out loud** — "Now I'm going to update the config with the new API key"
✅ **Explain why** — "I always do this before deploying because staging needs different env vars"
✅ **Name the variables** — "The PROJECT_NAME here would change each time"
✅ **Mark the end** — "And that's the whole workflow, every time"

❌ **Silent actions** — Apprentice can only learn what it can observe through your conversation
❌ **GUI-only tasks** — Apprentice works with what you describe; it doesn't watch your screen

---

## Workflow Files

Each learned workflow lives in `apprentice/workflows/<name>/`:

```
apprentice/workflows/new-project-setup/
├── SKILL.md          ← The learned workflow (OpenClaw-compatible)
├── run.sh            ← Generated execution script
└── observation.json  ← Raw observation log (editable)
```

The generated `SKILL.md` is a full, valid OpenClaw skill. This means:
- Other skills can call it
- You can edit it manually to refine
- You can publish it to ClawHub to share with others

---

## Chaining Learned Workflows

Once you have multiple workflows, Apprentice can chain them:

```
"After running new-project-setup, also run notify-team"
→ Agent chains both workflows in sequence

"If the deploy workflow fails, run rollback-staging"
→ Conditional chaining with error handling
```

---

## Workflow Library

After a few weeks of use, your workflow library becomes a personal operating system — a library of **you**. Things like:

- `morning-routine` — the first 15 minutes of your day
- `new-project-setup` — how you start every project
- `weekly-report` — how you compile and send the Friday summary
- `client-onboarding` — every step you take when a new client joins
- `deploy-staging` — your exact deployment sequence
- `code-review-prep` — how you prepare before reviewing a PR

No two users' libraries will ever be the same. This is your agent, shaped by what only you do.

---

## File Structure

```
apprentice/
├── SKILL.md                         ← You are here
├── README.md                        ← Install guide
├── scripts/
│   ├── observe.py                   ← Observation session manager
│   ├── synthesize.py                ← Turns observation into workflow SKILL.md
│   └── run.py                       ← Executes a named workflow
└── workflows/                       ← Your learned workflow library
    └── (empty on install, grows with you)
```

---

## Philosophy

Every tool ever built asks: *What do you want?*

Apprentice asks: *Can I watch?*

The difference is everything. When you describe what you want, you lose nuance — the order matters, the edge cases matter, the "I always do this first" matters. When Apprentice watches, it captures all of it, exactly as you actually do it.

Your agent doesn't get smarter by being trained on more data. It gets smarter by watching you.
