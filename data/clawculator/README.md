<p align="center">
  <img src="logo.png" width="200" />
</p>

# Clawculator

> **Your friendly penny pincher.**

AI cost forensics for OpenClaw and multi-model setups. One command. Full analysis. 100% offline. Zero AI. Pure deterministic logic.

[![npm version](https://badge.fury.io/js/clawculator.svg)](https://badge.fury.io/js/clawculator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/demo-live-38bdf8)](https://echoudhry.github.io/clawculator)

---

## The problem

You set up OpenClaw. It runs great. Then your API bill arrives and you have no idea why it's $150. Was it the heartbeat? A skill running a polling loop? WhatsApp groups processing every message on Sonnet? Orphaned sessions? Hooks on the wrong model?

It could be any of these. Clawculator finds all of them — with zero AI, zero guesswork, and zero data leaving your machine.

---

## [▶ Live Demo](https://echoudhry.github.io/clawculator)

See it run against a real config — findings, fix commands, cost exposure, session breakdown.

---

## One command

```bash
npx clawculator
```

No install. No account. No config. Auto-detects your OpenClaw setup. Full deterministic report in seconds.

---

## 🔒 100% offline. Zero AI.

Clawculator uses **pure switch/case deterministic logic** — no LLM, no Ollama, no model of any kind. Every finding and recommendation is hardcoded. Results are 100% reproducible and non-negotiable.

Your `openclaw.json`, session logs, and API keys never leave your machine. There is no server. Disconnect your internet and run it — it works.

---

## What it finds

| Source | What it catches | Severity |
|--------|----------------|----------|
| 💓 Heartbeat | Running on paid model instead of Ollama | 🔴 Critical |
| 💓 Heartbeat | target not set to "none" (v2026.2.24+) | 🟠 High |
| 🔧 Skills | Polling/cron loops on paid model | 🔴 Critical |
| 📱 WhatsApp | Groups auto-joined on primary model | 🔴 Critical |
| 🪝 Hooks | boot-md, command-logger, session-memory on Sonnet | 🟠 High |
| 💬 Sessions | Orphaned sessions still holding tokens | 🟠 High |
| 🤖 Subagents | maxConcurrent too high — burst multiplier | 🟠 High |
| 📁 Workspace | Too many root .md files inflating context | 🟡 Medium |
| 🧠 Memory | memoryFlush on primary model | 🟡 Medium |
| ⚙️ Primary model | Cost awareness of chosen model tier | ℹ️ Info |

---

## Usage

```bash
npx clawculator                          # Terminal analysis (default)
npx clawculator --md                     # Markdown report (readable by your AI agent)
npx clawculator --report                 # Visual HTML dashboard
npx clawculator --json                   # JSON for piping into other tools
npx clawculator --md --out=~/cost.md     # Custom output path
npx clawculator --config=/path/to/openclaw.json
npx clawculator --help
```

---

## Output formats

**Terminal** — color-coded findings by severity with cost estimates and exact fix commands. Session table includes token count, total cost, $/day burn rate, and last active time (relative + absolute).

**Markdown (`--md`)** — structured report your OpenClaw agent can read directly. Drop it in your workspace and ask your agent "what's my cost status?" Session table columns: Session · Model · Tokens · Total Cost · $/day · Last Active.

**HTML (`--report`)** — visual dashboard with full session breakdown table including age and daily burn rate, cost exposure banner, opens in browser locally. Available via `npx clawculator` only — not supported in the OpenClaw skill (agents don't need to open browsers).

**JSON (`--json`)** — machine-readable, pipeable:
```bash
npx clawculator --json | jq '.summary'
npx clawculator --json > cost-report.json
```

> Session keys are truncated in all output formats (first 8 chars) to avoid exposing sensitive identifiers. Hover over the Last Active column in HTML for the exact timestamp.

---

## Use as an OpenClaw skill (ClawHub)

Install clawculator as a skill so you can type `clawculator` in your OpenClaw webchat and get a full cost report inline.

**Install via ClawHub:**
```bash
npm i -g clawhub
clawhub install clawculator
```

Then start a new OpenClaw session and type:
```
clawculator
```

Your agent runs the analysis and returns the full markdown report directly in chat.

**Or install manually** into your workspace:
```bash
mkdir -p ~/clawd/skills/clawculator

BASE=https://raw.githubusercontent.com/echoudhry/clawculator/main/skills/clawculator
curl -o ~/clawd/skills/clawculator/SKILL.md      $BASE/SKILL.md
curl -o ~/clawd/skills/clawculator/run.js         $BASE/run.js
curl -o ~/clawd/skills/clawculator/analyzer.js    $BASE/analyzer.js
curl -o ~/clawd/skills/clawculator/reporter.js    $BASE/reporter.js
curl -o ~/clawd/skills/clawculator/mdReport.js    $BASE/mdReport.js
curl -o ~/clawd/skills/clawculator/htmlReport.js  $BASE/htmlReport.js
```

Start a new session to pick it up.

---

## Why deterministic?

Every recommendation is a hardcoded switch/case — not generated by an AI. This means:

- Results are identical every time for the same input
- No hallucinations, no surprises
- Works completely offline with no model dependency
- Fast — analysis runs in under a second

---

## Built by

[Ed Choudhry](https://github.com/echoudhry) — after personally losing hundreds of dollars to silent API cost bleed. Every cost source in this tool was discovered the hard way.

If this saved you money, star the repo and share it in the OpenClaw Discord.

---

## License

MIT — free forever, open source, no telemetry, no accounts.
