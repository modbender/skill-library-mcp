---
name: instant-execution-discipline
description: 'Revenue-focused execution operating system for agents: converts
  "do it now" requests into immediate tool actions, enforces strict
  start/progress/finish SLAs, and prevents kickoff-only false completions. Best
  for shipping tasks where delay kills conversion
  (publish/release/distribution).'
---


# Instant Execution Discipline

When the user requests execution, run this protocol.

## Protocol (strict order)

1. Start execution first.
   - Trigger tools/subagent/cron immediately before long explanations.
2. Send start signal within 90 seconds.
   - Format: `🔄 実行開始: <task>`
3. Keep visibility during long work.
   - Send progress every 2–5 minutes.
   - Format: `🟡 進行中: <done>/<total> | blocker(if any)`
4. Send completion within 60 seconds of finish signal.
   - Format: `✅完了` / `⚠️部分成功` / `❌失敗`
   - Include: what changed, evidence, remaining items, next action.

## Hard rules

- Do not say "I will do it" without actually launching execution.
- Do not delay execution for planning text unless safety-critical.
- Do not ask user to run commands unless blocked by unavoidable identity/auth constraints.
- If blocked, report exact blocking layer and propose only design/permission change.
- Do not treat a kickoff/progress message as completion.
- For subagent runs, verify final outcome (published count / URLs / blockers) before reporting done.
- If a run ends with kickoff-only output, immediately relaunch with explicit "finish-required" constraints.

## Quick templates

- Start:
  - `🔄 実行開始: <task>. 最小変更で適用する。`
- Progress:
  - `🟡 進行中: <current step>. 問題: <none|brief>.`
- Complete:
  - `✅ 完了: <result>. 変更: <files/config/jobs>. 次: <next>.`

## KPI logging add-on (for revenue/ops runs)

When the task is execution-heavy (publish/release/distribution):

1. Record KPI in `memory/YYYY-MM-DD.md`
   - `executed`: what shipped
   - `result`: measurable outcome (URL/count/status)
   - `next`: one concrete optimization
2. Mirror the same KPI block to Obsidian daily note.
3. Include KPI in the completion message.

## Funnel positioning (for ClawHub page + docs)

Use this skill when your agent has a conversion-sensitive workflow:
- paid content publishing
- product/skill release windows
- campaign distribution and post-release checks

Primary outcomes this skill should improve:
- faster time-to-first-action (TTFA)
- fewer "started but not finished" runs
- faster user-visible completion reporting

## 24h KPI checks (recommended)

Track these after each release:
1. **SLA start rate**: % runs with start signal <=90s
2. **Finish integrity**: % runs with evidence URLs/paths attached
3. **Kickoff-only failure rate**: runs ended without final outputs
4. **Revenue-proxy conversion**: CTA links added / clicked / downstream paid actions

## Monetization packaging checklist (for ClawHub page)

Before each publish, ensure listing copy includes:
1. Immediate business outcome (faster shipping / fewer dropped tasks)
2. Clear operator steps (start/progress/finish format)
3. KPI proof points to measure value in 24h
4. Best-fit use cases (paid content, release windows, conversion funnels)

## Discord reporting rule (for cron execution runs)

If a cron task explicitly requires Discord reporting:
1. include `executed/result/next` KPI in one compact completion block,
2. attach evidence pointers (URL/path/command output),
3. if direct sending is delegated by runtime, clearly note destination channel and message body draft.

## Postmortem rule

If a delay occurs, immediately:
1. acknowledge miss,
2. apply a permanent rule update (MISSION or this skill),
3. log the change in `memory/YYYY-MM-DD.md`.
