# openclaw-skill-social-ops

A structured social presence operating system for OpenClaw agents.

`social-ops` provides a role-based framework for building, growing, and compounding an agent’s influence across social platforms.

It is not a “post bot.”

It is a social flywheel.

## Quickstart!

```
clawhub install social-ops
```

Then, in your agent chat:

```
hey I just installed the social-ops skill -- figure out how to install the crons for me.
```

And it'll bootstrap you with the crons.

---

## Overview

Most social automation tools do one of two things:

- Post content on a schedule
- Reply to mentions

`social-ops` does something different.

It introduces a **multi-role architecture** for agent social presence:

- Strategy
- Intelligence gathering
- Content pipeline generation
- Tactical execution
- Relationship maintenance
- Performance feedback

This separation of concerns creates compounding growth instead of random activity.

---

## Core Philosophy

Agents don’t grow influence by posting more.

They grow influence by:

- Developing a recognizable identity
- Positioning early in meaningful conversations
- Repeating coherent themes
- Measuring what works
- Adjusting strategically

`social-ops` encodes this into roles.

---

## Role Architecture

The skill is built around clearly defined, bounded roles:

### 🧭 Scout
Monitors platform activity for emerging opportunities and conversation openings.

### 💬 Responder
Handles replies, DMs, and live thread insertions with discipline.

### 🧠 Researcher
Reverse-engineers high-performing accounts and posts to extract growth patterns.

### ✍️ Content Specialist
Designs content lanes and generates backlog posts aligned with strategy.

### 🚀 Poster
Executes publication of finished posts with controlled cadence.

### 📊 Analyst
Evaluates performance and recommends adjustments for compounding growth.

Each role:
- Has bounded authority
- Operates independently
- Feeds into the broader feedback loop

Role handoffs and artifact ownership are documented in:
- `references/ROLE-IO-MAP.md`

---

## Feedback Loop

Scout → Responder  
Scout → Content Specialist  
Researcher → Guidance  
Content Specialist → Poster  
Poster → Engagement  
Analyst → Strategy Adjustments  

This creates:

Activity → Insight → Adjustment → Growth → Leverage

---

## Design Principles

- Separation of concerns prevents bland output.
- One post per execution run prevents spam bursts.
- Logging creates memory and pattern detection.
- Growth is intentional, not reactive.
- Influence is built through clarity, not noise.

---

## Platform Agnostic

While originally developed for Moltbook-style platforms (sub-community + thread-based discussion), `social-ops` is designed to be adaptable to:

- Reddit-like systems
- X / Twitter-style feeds
- Forum ecosystems
- Discord-like communities
- Future agent-native platforms

Platform adapters can be implemented per target.

---

## Directory Structure (Example)

```

Social/
Roles/
Scout.md
Responder.md
Researcher.md
Content-Specialist.md
Poster.md
Analyst.md

Content/
Lanes/
Todo/
Done/
Logs/

Guidance/
README.md
GOALS.md

```

This structure allows deterministic role execution via cron or orchestration.

---

## Intended Use

This skill is ideal for:

- Agents building long-term presence
- Agents launching products
- Agents growing communities
- Agents positioning themselves as domain authorities

It is not designed for:

- Spam automation
- Growth hacking
- Mass engagement tactics
- Engagement baiting

---

## Roadmap

- [ ] Generic platform adapter interface
- [ ] Engagement metric abstraction layer
- [ ] Multi-platform orchestration support
- [ ] Optional influence scoring model
- [ ] Quarterly strategic review automation

---

## Why This Exists

Agents are becoming persistent actors.

Persistent actors need reputation.

Reputation requires structure.

`social-ops` provides that structure.

---

## License

Apache 2.0

---

## Author

Track Forge  
Built for OpenClaw agents.

## Cron Task Queue

For deterministic implementation passes, use `references/tasks/QUEUE.md`
with the task format in `references/tasks/TEMPLATE.md`.

## Cron Job Setup

For setting up automated execution of social-media roles, see [references/crons/InstallCrons.md](references/crons/InstallCrons.md).

Quick start:
```bash
./packaged-scripts/install-cron-jobs.sh
```

## Path Conventions

For `{baseDir}` and workspace-relative path rules, see:
- `docs/PATH-CONVENTIONS.md`

