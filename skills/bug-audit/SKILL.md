---
name: bug-audit
description: Comprehensive bug audit for Node.js web projects. Activate when user asks to audit, review, check bugs, find vulnerabilities, or do security/quality review on a project. Supports game projects (Canvas/Phaser/Three.js), data tools (crawlers/schedulers), WeChat mini-programs, API services, dashboards, and bots. Dynamically generates a tailored audit plan based on project profiling rather than running a fixed checklist.
---

# Bug Audit Flow

Audit any Node.js web project by profiling it first, then selecting relevant audit modules.

## Flow

```
Step 1: Profile → Step 2: Plan → Step 3: Execute → Step 4: Regress → Step 5: Archive
```

## Step 1: Project Profile (5 min)

Read the project's key files and answer:

### 1.1 Basics
- Project name, server.js lines, index.html lines, total files
- Stack: Express / Socket.IO / Phaser / Three.js / Canvas / DOM-only
- DB: SQLite / MySQL / PostgreSQL / none
- Recent modular refactor? (variable ordering bugs likely)

### 1.2 Type Tags (multi-select)

| Signal | Tag |
|--------|-----|
| Canvas/Phaser/physics/game loop | 🎮 game |
| Crawler/scheduler/data sync/Feishu import | 📊 data-tool |
| WeChat OAuth/JS-SDK/official account API | 🔧 wechat |
| Socket.IO/WebSocket realtime | ⚡ realtime |
| External API with key auth | 🔌 api-service |
| Charts/dashboard/monitoring | 📈 dashboard |
| Money/transactions/assets | 💰 finance |
| Admin panel/config.json hot-reload | 🛠️ admin |
| Bot/auto-reply/message handler | 🤖 bot |

### 1.3 Risk Scan

| Question | If yes → focus on |
|----------|-------------------|
| server.js > 1000 lines? | High-density bugs, understand structure first |
| User login / resource system? | Security + economy exploits |
| Cron / scheduled tasks? | Task reliability + error isolation |
| Third-party API calls? | Timeout / retry / fallback |
| Runs in WeChat WebView? | ES6 compat + CDN + debugging |
| Multiplayer realtime? | Concurrency / state sync / memory leaks |
| Recent modular split? | Variable order / cross-file refs / regression |
| Has config.json? | Are values actually read by code? |

## Step 2: Build Plan

Based on the profile, pick modules from `references/modules.md`. Read only the sections that match the project's tags. Do NOT run all modules on every project.

**Required for all projects:** S (Security, if has users), D1 (Atomic ops, if has DB), R1 (Deploy basics).

**Pick by tag:**
- 🎮 game → G1 G2 G3 G4
- 📊 data-tool → D3
- 🔧 wechat → W1 W2 W3
- ⚡ realtime → P1
- 🔌 api-service → A1 A2 A3
- 🤖 bot → B1
- 💰 finance → D1 (extra strict)
- 🛠️ admin → G4 (config validation)

**Always add project-specific items** — the modules are a starting point, not a ceiling. If you spot something unusual during profiling, add it to the plan.

## Step 3: Execute

Run rounds in risk order:

```
Round 1: Quick scan (node -c syntax + HTML tag matching + obvious issues)
Round 2: Security (S modules)
Round 3: Core logic (G/D/A/B modules by type)
Round 4: User path simulation (login → core feature, full walkthrough)
Round 5: Red team (simulate attacker: resource exploits, level skipping, parameter forgery, race conditions)
Round 6: Performance + memory (P modules)
Round 7: Config + compatibility (G4/W modules)
Round 8: Deploy verification (R modules)
```

**Output format per round:**
```
Bug N: [🔴/🟡/🟢] Brief description
- Cause: ...
- Fix: ...
- File: ...
```

**Early exit:** 2 consecutive rounds with 0 new bugs → done.
**Small projects (<1000 lines):** 3-4 rounds is enough.
**API-only (no frontend):** Skip G/W modules.

## Step 4: Regression + Live Verify

### Regression (mandatory)
- Check fixes didn't introduce new bugs
- After modular split: verify cross-file variable/function reachability
- If changed file A, check files that depend on A

### Live smoke test
- Homepage returns 200
- Key APIs return valid JSON
- Login flow works
- Core feature functional

## Step 5: Archive

Update `memory/projects/<project>.md` changelog:
- Date + rounds completed + bugs fixed count
- Key pitfalls discovered (for next audit reference)

## Reference Files

- `references/modules.md` — All audit modules (Security, Data, Performance, Game, WeChat, API, Bot, Deploy). Read sections matching project tags.
- `references/pitfalls.md` — Real-world pitfall lookup table from 200+ bugs across 30+ projects, plus WeChat WebView remote debugging techniques.
