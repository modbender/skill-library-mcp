# ♾️ OpenClaw Infinite Oracle

In ancient Greece, an Oracle was a revelation from the gods to mortals. Mortals could only listen in awe and execute with all their might to produce a Key Result. When an Agent is given an OKR (Oracle-Key Result), given enough time and resources, in what surprising (or terrifying) ways will it succeed (or fail)?

[English](README_EN.md) | [中文](README.md)

**Infinite Oracle** is a skill designed for the OpenClaw ecosystem. It's more than just a background loop script—it's an architectural exploration of how to make an LLM reliably, affordably, and safely pursue an endless objective.

---

## 🏗️ Design Philosophy & Mechanics
Leaving an LLM in an infinite loop usually results in two fatal outcomes: **Context Bloat** (crashing your API budget and making the AI forgetful) and **Getting Stuck in Dead Ends**. To solve this, we implemented several key design choices:

### 1. The Manager-Worker Decoupling
It is a disaster to have the same AI chatting with you while it grinds away in an infinite background loop. Your casual questions will break its coding train of thought, and its massive logs will flush out your chat context.
That's why we use a **decoupled architecture**:

*   **👨‍💼 The Manager (Oracle)**: This is your primary OpenClaw Agent (e.g., `main`). Equipped with the `infinite-oracle` skill, it chats with you via Lark/Feishu or your terminal. You can assign it the smartest (and priciest) model available (like Claude 3.5 Sonnet or GPT-4o) to handle complex orchestration and decisions.
*   **🤖 The Worker (`peco_worker`)**: A separate Agent spawned by the Manager. It gets locked in an isolated background Session to grind away. To save costs, the Manager can assign it a highly cost-effective model (like Qwen or Gemini 1.5 Flash).

### 2. "Human-in-the-Loop": Humans as an API
This is perhaps the most interesting part of the design. While working, the AI inevitably hits physical barriers: it needs an SMS verification code, a bank card linkage, or a facial scan.
In older architectures, the AI would either loop infinitely trying to bypass it or crash completely. We introduced the **[HUMAN_TASK]** mechanism:
* When the Worker hits a hard physical wall, it logs a "Human To-Do" ticket and then *sidesteps* the issue to work on other parts of the project (no idle waiting).
* The same HUMAN_TASK is deduplicated before writing to backlog/Feishu, so repeated blockers do not spam duplicate tickets.
* If the same human dependency repeats twice, the Worker is forced back to PLAN for stronger divergence and non-human workaround attempts.
* If the same human dependency repeats three times, the Worker self-pauses and asks the Manager Agent to notify the human with blocker details.
* You (acting as a fleshy, physical API) see the ticket in a Feishu spreadsheet, grab the verification code from your phone, and type it in.
* The Worker picks up your code on its next iteration and keeps running.
**In a sense, this design makes you work for the AI. But it's exactly this "human-as-a-service" fallback that allows a fully autonomous loop to survive in the real world.**

### 3. FSM & Native Memory (Preventing Context Bloat)
The background `peco_loop.py` is a ruthless supervisor. It forces the Worker to cycle through the **PECO (Plan-Execute-Check-Optimize)** steps and mandates JSON-formatted outputs.

Starting from v1.0.3, we removed the custom session rotation mechanism and now rely on OpenClaw's **native memory system**. The Worker no longer needs "active amnesia"—OpenClaw automatically manages context, allowing the loop to run truly infinitely without token explosion.

### 4. Injecting Persona: The Worker is not a Parrot
When creating the Worker, the Manager doesn't just give it a desk; it injects a hardcore set of principles (`SOUL.md`) into its system settings:
1.  **💡 Divergent Thinking**: If path A is blocked, don't just sit there. Find a login-free alternative or a workaround. **Action beats paralysis.**
2.  **🧱 Capability Accumulation**: Never do a tedious manual task twice. If it successfully scrapes a site once, it must write a Python script or an OpenClaw Skill to automate it for next time. Let capabilities compound.
3.  **🛡️ Strong Security Awareness**: Have a high "Search IQ". Cross-verify tutorials and never execute dangerous commands like `rm -rf` from random SEO articles.

---

## 💬 Conversational UI: How to control it

Once installed, you don't need to touch server commands. Just talk to your Manager Agent:

### 🚀 1. Hiring & Launching
> **"Oracle: To balance cost and performance, decouple the Manager and Worker. Create a new Agent named `peco_worker` and configure it with a cost-effective model. Once done, start the infinite loop with the target: 'Research trending AI monetization models and write an automated scraper for tech news.'"**

*(The Manager will run the Bash commands, build the Worker, inject the persona, and start the `nohup` background process.)*

### 📊 2. Checking Status & Helping Out
> **"What is the current status of the infinite task?"** 
*(It reads the background logs and tells you what the Worker is currently coding.)*

> **"Are there any HUMAN_TASKs waiting for me to solve?"**
*(It reads the backlog and tells you if the Worker is stuck waiting for a phone verification code.)*

### ⚡ 3. The "God Mode" Override
> **"Oracle: The verification code for that site is 8888. Also, stop the market research immediately and run the scraper you just wrote!"**
*(The Manager writes your command into the override file. On the next heartbeat, the Worker reads it and immediately pivots.)*

### 🎯 4. Objective Tuning vs Objective Replacement (New)
> **"Oracle: Keep current context, but tune the objective to prioritize executable scripts and validation reports."**
*(The Manager runs the tuning flow: keep history/context, back up objective state files, append a tuning record, then continue execution.)*

> **"Oracle: The current infinite objective is obsolete. Replace it completely and restart from scratch."**
*(The Manager runs the full replacement flow: stop process, create timestamped backups, clear state/history artifacts, then restart with a brand-new objective.)*

---

## 🛠️ Dual-Track Support: Lark Bitable vs Local Files

We support two modes of tracking progress:

### Local File Mode (Default)
Zero configuration, works out of the box. Logs go to `peco_loop_v3.log`, cries for help go to `human_tasks_backlog.txt`, and overrides go to `peco_override.txt`.
When the loop self-pauses (for example `decision=halt`, circuit-breaker open, or repeated human blocker x3), it also writes a manager-notification fallback record to `peco_manager_notifications.log`.

Objective management notes:
- In tuning mode, changes are appended to `peco_objective_tuning.log` and existing progress/backlog history is preserved.
- In replacement mode, the Manager executes a backup + reset + restart flow to prevent mixing old and new objectives.

### Lark (Feishu) Bitable Mode (Advanced)
If you chat with your main Agent via Lark/Feishu, the Manager will proactively help you create or find a Lark Bitable for syncing progress. The Worker streams its progress and Human Tasks directly to the spreadsheet. You can just check a "Resolved" box and type a code on your phone, and the Worker automatically syncs it back.

Initialization constraints:
- On a brand-new task or a full objective replacement, the Manager initializes a fresh empty table context and creates both the progress/log table and the human-help backlog table.
- Each task maps to exactly one Feishu Bitable document link, and that single link must contain both the cycle-log table and the human-help table.
- Field requirements are unified as: required `loop_status` field set + required `human_backlog` field set; `tasks` is an optional summary table (recommended).
- Saved app credentials/integration IDs (for example app id/app secret) are preserved by default during new-task initialization, and are rotated only when the user explicitly asks for credential reset.
- Do not split one task across two different Feishu Bitable document links (one for logs and one for human-help).

**Note**: If you're using Terminal, Discord, WhatsApp, or other non-Lark channels, the system gracefully falls back to local file mode—the experience remains smooth. (See comments in `peco_loop.py` for Lark setup details.)

---

## 📥 Installation Guide

### Prerequisites
- A functional OpenClaw environment.

### ClawHub Install

```bash
clawhub install infinite-oracle
```

### The "One-Shot" Prompt Install (Let your Agent do it)

Copy and send this to your OpenClaw Agent:

```
Download the repo at git@github.com:KepanWang/openclaw-infinite-oracle.git, install SKILL.md as the infinite-oracle skill, and place peco_loop.py in the working directory. After that, read the skill docs and tell me what you've learned.
```

### Manual Install
```bash
git clone git@github.com:KepanWang/openclaw-infinite-oracle.git
cd openclaw-infinite-oracle

# 1. Install the Skill
mkdir -p ~/.openclaw/skills/infinite-oracle
cp SKILL.md ~/.openclaw/skills/infinite-oracle/SKILL.md

# 2. Deploy the Loop Engine
cp peco_loop.py ~/.openclaw/peco_loop.py
chmod +x ~/.openclaw/peco_loop.py
```

---
*Disclaimer: Unsupervised infinite execution is inherently risky. Please configure a proper sandbox for your Worker Agent and monitor your API billing limits.*
