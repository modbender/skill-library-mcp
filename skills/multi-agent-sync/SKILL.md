---
name: multi-agent-sync
description: Coordinate multi-agent tasks with visible group updates. Use when delegating work across multiple topic agents and the user needs transparent progress in-group (start update, mid-progress update, final summary).
---

# Multi-Agent Sync

Use this skill when running multi-agent collaboration in chat groups.

## Objective

Keep execution transparent: do not only run background session calls. Always mirror key progress back to the group thread.

Primary delivery rule:
- In multi-agent tasks, post progress and final summary in the group topic thread (e.g., topic1).
- Keep main/direct chat lightweight for control messages only, because user may continue other tasks there.
- Main session must not block waiting for all agents to finish; dispatch then return immediately with a short status note.

## Mandatory workflow

0. **Planning defaults (must declare in assignment)**
   - For coding subtasks, explicitly state: use `openai-codex-operator` (Codex skill).
   - For multi-agent orchestration, explicitly state: this run follows `multi-agent-sync`.

1. **Kickoff sync**
   - Post a visible group message with:
     - task objective
     - role split (who does what)
     - expected deliverables
     - default skills used in this run (Codex + multi-agent-sync when applicable)
   - Auto-start a temporary watcher job at kickoff (cron/timer) for this task.
2. **Dispatch tasks**
   - Send detailed instructions to each agent session.
   - Include required skill constraints in task text (e.g., coding agent must use Codex skill).
   - Use non-blocking dispatch behavior (do not wait on long `sessions_send` timeouts).
   - After dispatch, immediately send a non-blocking acknowledgment in main/direct chat and release control.
3. **Mid-progress sync**
   - Each agent must post its own progress updates in its own topic (do not replace with a single orchestrator summary).
   - Mandatory milestone labels per agent: `started` → `partial` → `done` (or `blocked`).
   - Also post periodic heartbeat-style updates if an agent is still running.
   - High-frequency mode (user requested): continuously post intermediate updates for each material step/change (no long interval waiting).
   - If a tool call returns timeout, explicitly say "timeout != failure" and continue tracking.
   - If any milestone is missing, orchestrator must immediately backfill a status-correction message and record the miss.
4. **Collect outputs**
   - Use session history/log checks to confirm outputs from each agent.
   - Ensure each agent has at least one visible mid-progress message in the group thread (not only final output).
4.5 **Coordinator periodic rollup (topic1)**
   - Coordinator must post periodic cross-agent rollups in summary topic (topic1):
     - who is started / partial / done / blocked
     - latest artifact or evidence from each agent
     - next checkpoint
   - Rollups complement (not replace) per-agent own progress messages.
   - Recommended cadence: every 1–2 minutes while task is active (adaptive by task length).
   - Hard requirement: after each poll cycle, publish a rollup immediately (do not delay publish after status is known).
   - Prefer a temporary scheduled watcher for active tasks (timer/cron-style).
   - Watcher tick action: poll agent session history (e.g., topic3/topic5), then immediately publish rollup to topic1.
   - Completion action: when all agents are done/blocked, publish final closure and remove watcher immediately.
   - This watcher lifecycle is mandatory whenever this skill is used.
   - Expected behavior in practice: watcher tick posts rollup to topic1; when both worker topics reach done/blocked, watcher publishes closure and is removed in the same flow.

4.6 **Dual mechanism (push + pull)**
   - Push: each agent must proactively post milestone updates in its own topic.
   - Pull: coordinator must poll session history to detect silent completions or stuck states.
   - Do not rely on only one mechanism.

5. **Final sync**
   - Keep agent-level outputs in each agent topic.
   - Post one structured cross-agent final summary in the designated summary topic (usually topic1) with:
     - implementation result
     - test/validation result
     - delivery artifact paths (absolute or repo-relative)
     - implementation principle/approach analysis
     - next actions
   - Do not keep final summary only in main/direct chat.

## State handling rules

- Treat `timeout` as "no reply in window", not hard failure.
- Continue with follow-up checks (`sessions_history` / process logs).
- If no output after retries, post a blocked-status update with missing dependencies.
- Never keep main session waiting for long-running agent completion; use async follow-ups in group thread.
- Rule enforcement: do not close the task until each agent topic has visible `started` + `partial` + `done/blocked` entries.
- If an agent finishes work but did not proactively post `done`, coordinator must immediately issue a status-correction message and mark cause (e.g., timeout window, silent reply).
- If an agent repeatedly misses proactive updates, resend task with explicit milestone format and require immediate `started` ack.
- Coordinator failure mode to avoid: "status known but not published". If detected, immediately send a status-correction post in topic1.

## Output template (group-visible)

Use this 3-part structure in group chat:

1) 任务启动（分工）
2) 执行进度（中间状态）
3) 最终汇总（结果与后续）

## References

- `references/message-templates.md`
