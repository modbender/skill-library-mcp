---
name: skill-router
description: "Context-based skill auto-routing + federated skill composition. Analyzes user input to auto-select single or multiple skills and execute in order. First gateway for all requests. Use on every request to determine optimal skill combination."
author: 무펭이 🐧
---

# Skill Router

Meta system that analyzes natural language input to auto-select appropriate skill(s), determine order, and chain execution.

## 🚀 v2 Architecture: Low-level Call Protocol

### Execution Flow
```
1. Scan only skills/*/SKILL.md frontmatter (trigger matching)
   - Quick match with description + trigger fields
   - No full body reading → 83% token savings
   
2. Check run field of matched skill for script path
   - run: "./run.sh" → skills/{name}/run.sh
   - run: "./run.js" → skills/{name}/run.js
   
3. Direct script execution with exec
   WORKSPACE=$HOME/.openclaw/workspace \
   EVENTS_DIR=$WORKSPACE/events \
   MEMORY_DIR=$WORKSPACE/memory \
   bash $WORKSPACE/skills/{name}/run.sh [args]
   
4. Agent processes stdout result
   - Parse if JSON
   - Pass through if text
   - Check stderr on error
   
5. Generate events based on events_out
   - Create events/{type}-{date}.json file
   - Subsequent skills consume via events_in
   
6. Check hooks → trigger subsequent skills
   - post: ["skill-a", "skill-b"] → auto-execute
   - on_error: ["notification-hub"] → notify on error
```

### Skill Metadata Scan
```bash
# Extract only frontmatter from all skills
for skill in skills/*/SKILL.md; do
  yq eval '.name, .description, .trigger, .run' "$skill"
done
```

### Execution Example
```bash
# User: "daily report"
# → trigger match: daily-report
# → Execute:
cd $HOME/.openclaw/workspace
WORKSPACE=$PWD \
EVENTS_DIR=$PWD/events \
MEMORY_DIR=$PWD/memory \
bash skills/daily-report/run.sh today

# Agent formats stdout result and delivers to user
```

### Token Savings Effect
- **Before**: SKILL.md 3000 chars × 40 = 120KB (~30K tokens)
- **v2**: SKILL.md 500 chars × 40 = 20KB (~5K tokens)
- **Savings**: 83% token reduction

## Core Concept

OpenClaw already selects 1 skill via description matching, but this skill:
1. **Detect complex intent**: "Analyze competitors and make card news" → competitor-watch + copywriting + cardnews + insta-post
2. **Context-based auto-hooks**: Auto-determine subsequent skills when a skill executes
3. **Skill chain templates**: Pre-define frequently used combinations

## Intent Classification Matrix

### Single Skill Mapping (1:1)

- "commit/push/git" → git-auto
- "DM/instagram message" → auto-reply
- "cost/tokens/how much" → tokenmeter
- "translate/to English" → translate
- "invoice/quote" → invoice-gen
- "code review/PR" → code-review
- "system status/health" → health-monitor
- "trends" → trend-radar
- "performance/reactions/likes" → performance-tracker
- "daily report" → daily-report
- "SEO audit" → seo-audit
- "brand tone" → brand-voice

### Complex Skill Chains (1:N) — Core Pipelines

| Trigger Pattern | Skill Chain | Description |
|---|---|---|
| "create content/post" | seo-content-planner → copywriting → cardnews → insta-post | Full content pipeline |
| "analyze competitors and report" | competitor-watch → daily-report → mail | Research→report |
| "summarize this video as card news" | yt-digest → content-recycler → cardnews → insta-post | Video→content conversion |
| "weekly review" | self-eval + tokenmeter + performance-tracker → daily-report | Comprehensive review |
| "recycle content" | performance-tracker → content-recycler → cardnews | Repackage successful content |
| "review idea and execute" | think-tank(brainstorm) → decision-log → skill-composer | Ideation→decision→execution |
| "market research" | competitor-watch + trend-radar + data-scraper → daily-report | Full research |
| "release" | code-review → git-auto → release-discipline | Safe deployment |
| "morning routine" | health-monitor → tokenmeter → notification-hub → daily-report | Morning auto-check |

## Context-based Auto-chain Rules

Skill A execution complete → analyze results → auto-determine next skill:

**Auto-chain Rules (if → then)**

- IF competitor-watch detects important change → THEN notification-hub(urgent) + include in daily-report
- IF tokenmeter exceeds $500/month → THEN notification-hub(urgent)
- IF code-review detects HIGH severity → THEN block commit + notification-hub
- IF think-tank conclusion has "immediate execution" action → THEN auto-record in decision-log
- IF cardnews generation complete → THEN confirm "post with insta-post?" (approval required)
- IF self-eval detects repeated mistake → THEN trigger learning-engine
- IF performance-tracker finds successful content → THEN suggest content-recycler
- IF trend-radar detects hot trend → THEN auto-suggest seo-content-planner
- IF mail detects important email → THEN notification-hub(important)
- IF health-monitor detects anomaly → THEN attempt auto-recovery + notification-hub(urgent)

## Execution Engine Protocol

```
1. Receive user input
2. Classify intent (single vs complex)
3. If single → execute skill immediately
4. If complex → compose skill chain
   a. Skills without dependencies execute in parallel (sessions_spawn)
   b. Skills with dependencies execute sequentially (pass previous results via events/)
5. Check auto-chain rules on each skill completion
6. Auto-trigger additional skills if needed (or request approval)
7. Synthesize final results and respond
```

## Auto-hook Registration

When skill-router activates, for all skills:

- **pre-hook**: Input validation + security check
- **post-hook**: Generate events/ event + check chain rules
- **on-error**: Error log + notification-hub

## Skill Dependency Graph

```
[User Input]
    ↓
[skill-router] ← Intent classification
    ↓
┌─────────────────────────────────────────┐
│  TIER 1: Data Collection                │
│  competitor-watch, data-scraper,        │
│  trend-radar, tokenmeter, yt-digest     │
└─────────────┬───────────────────────────┘
              ↓ events/
┌─────────────────────────────────────────┐
│  TIER 2: Analysis/Thinking              │
│  think-tank, self-eval, seo-audit,      │
│  code-review, performance-tracker       │
└─────────────┬───────────────────────────┘
              ↓ events/
┌─────────────────────────────────────────┐
│  TIER 3: Production                     │
│  copywriting, cardnews, content-recycler,│
│  translate, invoice-gen                  │
└─────────────┬───────────────────────────┘
              ↓ events/
┌─────────────────────────────────────────┐
│  TIER 4: Deployment/Execution           │
│  insta-post, mail, git-auto,            │
│  release-discipline                     │
└─────────────┬───────────────────────────┘
              ↓ events/
┌─────────────────────────────────────────┐
│  TIER 5: Tracking/Learning              │
│  daily-report, decision-log,            │
│  learning-engine, notification-hub      │
└─────────────────────────────────────────┘
```

## Safety Mechanisms

- Always require approval before external actions (email send, SNS post, payment)
- Prevent infinite loops: Stop after same skill chain repeats 3 times
- Cost limit: Max 5 subagents per chain
- Graceful stop on error + save partial results

---

> 🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
