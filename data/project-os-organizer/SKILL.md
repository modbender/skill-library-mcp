---
name: project-os-organizer
description: "Privacy-first, chat-first project manager for vibe coders. Track projects, capture updates, and resume work across local folders, Claude/Codex, and GitHub with explicit opt-in controls."
metadata: {"clawdbot":{"emoji":"🗂️","requires":{"bins":["python3"],"env":["PROJECT_OS_ROOT (required unless explicit remote install opt-in)","PROJECT_OS_INCLUDE_CHAT_ROOTS=1 (optional)","PROJECT_OS_ENABLE_GITHUB_SYNC=1 (optional)"]},"os":["linux","darwin","win32"]}}
---

# Project OS Organizer Skill

## Why This Skill
Use this when a user is juggling many AI-built projects and needs one simple command surface to:
1. See what is active now.
2. Capture progress and next steps fast.
3. Resume any project in one jump (local/GitHub/chat).

## Security Defaults
1. Remote install is disabled by default.
2. Chat transcript indexing is disabled by default.
3. GitHub sync/token usage is disabled by default.
4. Home-directory heuristic discovery is disabled by default.

To opt in explicitly:
1. `PROJECT_OS_INCLUDE_CHAT_ROOTS=1` enables chat transcript indexing.
2. `PROJECT_OS_ENABLE_GITHUB_SYNC=1` enables GitHub username/token integration.
3. `PROJECT_OS_ENABLE_HOME_DISCOVERY=1` enables broad home-directory discovery.
4. `PROJECT_OS_AUTO_SETUP=1 PROJECT_OS_ALLOW_REMOTE_INSTALL=1` allows remote clone/install if `PROJECT_OS_ROOT` is missing.

## Goal
Produce a complete, local-first project inventory that answers:
1. What projects exist right now?
2. Which are active/blocked/stale?
3. What is each project actually about?
4. Where did the user leave off?
5. How can the user jump back in immediately?
6. How can the user quickly edit status/next steps/items without leaving OpenClaw?

## Default Behavior (Natural Language First)
Default action for every user message:
1. Interpret the message.
2. Run: `scripts/project_router.sh "<user message>"`.
3. Return the router output directly in plain language.

Users should not need to type scripts, Python, paths, or flags.

Fallback for power users:
- Use the short wrapper command: `project ...`
- Examples: `project`, `project focus`, `project today`, `project inbox "idea: test"`, `project dashboard start`

Plain-language request mapping:
1. "What am I working on today?" -> activity today
2. "Show my projects" -> grouped project list (Now/Later/Blocked/Done)
3. "Focus list" -> top focus items
4. "Add this idea: ..." -> inbox capture
5. "Next for project-os: ..." -> add next
6. "Mark X blocked" -> set simple status
7. "Start dashboard" -> dashboard start
8. "Resume project X" -> resume pack
9. "Only track A, B, C" -> set tracked scope (activity will only include these)
10. "Mute X" / "Untrack X" / "Show scope" -> scope controls

Response style in non-technical mode:
1. Keep responses short and direct.
2. Do not expose technical command details unless user asks.
3. For activity questions, always return `Activity Criteria` + day sections.
4. If a project name is ambiguous, ask one short clarification question.

## Project Definition
Treat an item as a project if it matches any of these:
1. Git repository folder.
2. Non-git code folder with project markers (`package.json`, `pyproject.toml`, `Cargo.toml`, etc).
3. Chat session (Claude/Codex) that does not match an existing project; create a chat-derived project.
4. Claude workspace chats should map to deeper subprojects when session folders indicate a nested workspace path.

Reject likely non-project folders in collection roots (docs-only, logs, backups, notes-only folders) unless there is strong code/marker evidence.
Reject low-signal chat-only entries as standalone projects unless they contain a useful path hint or meaningful project intent.

## Required Workflow
1. Run `scripts/bootstrap.sh` first.
3. Validate coverage:
   - run `python3 -m project_os.cli --db ~/.project_os/openclaw_test.db --config ~/.project_os/openclaw_test_config.json list-projects --limit 200`
   - run `python3 -m project_os.cli --db ~/.project_os/openclaw_test.db --config ~/.project_os/openclaw_test_config.json list-sessions --limit 50`
   - run `python3 -m project_os.cli --db ~/.project_os/openclaw_test.db --config ~/.project_os/openclaw_test_config.json list-items --status open --limit 80`
   - run `python3 -m project_os.cli --db ~/.project_os/openclaw_test.db --config ~/.project_os/openclaw_test_config.json squash-chat-projects`
4. If user wants visual mode, run `scripts/start_dashboard.sh`.
5. If user wants quick resume context, run `scripts/write_memory.sh` and use `~/.project_os/PROJECT_MEMORY.md`.

## First-Run (Production)
Run this for a first-time user:
1. `scripts/openclaw_smoke_agent.sh`
2. `scripts/read_smoke_result.sh`
3. Confirm:
   - `RESULT_STATUS=ok`
   - `RESULT_DASHBOARD_URL=...`
   - `RESULT_PORT_8765_LISTENING=yes`

If `project-os` repo is not present locally, the skill will fail safely by default and instruct setting `PROJECT_OS_ROOT`. Remote install is explicit opt-in only.

## Operation Modes
- Dashboard mode: simple visual triage (`Focus Today`, `Now`, `Blocked`, `Later`, `Done`) and jump links.
- Dashboard mode includes:
  - Quick Inbox capture (freeform note -> auto-routed update/next/reminder/idea/blocker)
  - Daily Check-In panel (done + next + blocker)
  - Focus list, stale nudges, weekly snapshot, and server health
- Dashboard intentionally avoids recommendation-score noise and focuses on plain language:
  - `What it is` (derived from project files like README/package metadata)
  - `Where left off`
  - `Do next`
  - inline editing: set simple status (`now/later/blocked/done`), set next action, add update/next/reminder/idea/blocker, mark items done/dismissed
  - session resume buttons for both tools (`Resume in Claude` and `Resume in Codex`) when session link is valid
- Memory mode: markdown snapshot for fast resume in any chat.

Default recommendation: use both.

## OpenClaw Command-First Updates
Use CLI commands as the primary interface:
1. `add-update` for what changed.
2. `add-next` for the immediate next step (also updates project `next_action`).
3. `add-reminder` for date/time-based follow-ups.
4. `add-idea` for backlog thoughts.
5. `list-items` and `set-item-status` to triage/close items.
6. Use `scripts/project_actions.sh` for short aliases around these commands.
7. For activity-window questions ("what did I work on today/yesterday"), run `scripts/activity_report.sh --when both` or `scripts/project_actions.sh activity --when both`.
8. Do not guess activity by project name or status; only use timestamp evidence from the report criteria.
9. Activity report excludes archived projects by default (use `--include-archived` only if user asks).
10. Response contract for activity-window answers:
   - always include `Activity Criteria`
   - always include `Today (...)` and/or `Yesterday (...)` headings
   - include at least one evidence line per listed project (`local_commit`, `github_push`, `session`, or `note`)
   - if no projects match, explicitly return `- none`

## OpenClaw Usage
1. In OpenClaw, invoke this skill by name: `project-os-organizer`.
2. For first run setup: `project setup` (or `scripts/easy_mode.sh setup`).
3. Default day-to-day: just type plain English in chat and route through `project_router.sh`.
4. Optional shortcuts use only `project ...`.
5. For one-command local install from this repo, run `scripts/install_openclaw_skill.sh`.
6. For non-interactive OpenClaw agents, use:
   - `scripts/openclaw_smoke.sh` for strict CI-style smoke (non-zero exit on failure)
   - `scripts/openclaw_smoke_agent.sh` for agent-safe smoke (always exits zero, returns `RESULT_STATUS`)
   - `scripts/read_smoke_result.sh` to fetch the last smoke result file when command output is flaky
   - `scripts/bootstrap.sh --noninteractive` (timeout-safe quick mode)
   - `scripts/bootstrap.sh --noninteractive-full` (full refresh mode)
   - `scripts/start_dashboard.sh --detach --restart`
   - Smoke commands return machine-readable lines:
     - `RESULT_STATUS`
     - `RESULT_ERROR`
     - `RESULT_DASHBOARD_URL`
     - `RESULT_DASHBOARD_PID`
     - `RESULT_PORT_8765_LISTENING`
     - `RESULT_CURL_HEAD`
     - `RESULT_SMOKE_LOG`
     - `RESULT_DASHBOARD_LOG`
     - `RESULT_RESULT_FILE`
7. For quick editing from chat:
   - `scripts/project_actions.sh list --limit 80`
   - `scripts/project_actions.sh set-status --project "<name|id>" --status blocked`
   - `scripts/project_actions.sh set-next --project "<name|id>" --text "next step"`
   - `scripts/project_actions.sh add-update --project "<name|id>" --text "what changed"`
   - `scripts/project_actions.sh add-next --project "<name|id>" --text "immediate next step"`
   - `scripts/project_actions.sh add-reminder --project "<name|id>" --text "follow up" --due 2026-03-01`
   - `scripts/project_actions.sh add-blocker --project "<name|id>" --text "what is blocked"`
   - `scripts/project_actions.sh simple-status --project "<name|id>" --status now`
   - `scripts/project_actions.sh focus --limit 3`
   - `scripts/project_actions.sh stale --days 14 --limit 20`
   - `scripts/project_actions.sh weekly --days 7 --limit 12`
   - `scripts/project_actions.sh notify --period daily`
   - `scripts/project_actions.sh inbox --text "freeform note"`
   - `scripts/project_actions.sh checkin --project "<name|id>" --done "..." --next "..." --blocker "..."`
   - `scripts/project_actions.sh duplicates --limit 50`
   - `scripts/project_actions.sh merge --keep "<id|name>" --drop "<id|name>"`
   - `scripts/project_actions.sh ask --text "mark project-os blocked"`
   - `scripts/project_actions.sh set-item --item <id> --status done`
8. For "worked on today/yesterday":
   - `scripts/project_actions.sh activity --when both`
9. For personal scope control:
   - `scripts/project_actions.sh scope --set "project-os" "polymarket-trader-v2"`
   - `scripts/project_actions.sh track --project "project-os"`
   - `scripts/project_actions.sh mute --project "clawd"`
   - `scripts/project_actions.sh scope`
   - Add `--include-archived` only on explicit request.
   - Return the output sections `Activity Criteria`, `Today (...)`, and `Yesterday (...)` so the user sees exactly how projects were counted.

## Safety and Scope
1. Local-first only.
2. Do not mutate repositories/servers automatically.
3. Do not invent project state; infer from scans/sessions and expose uncertainty.
4. Prefer broad root coverage to avoid missing nested subfolders.
5. Keep non-git project discovery at root-level by default (`include_nested_non_git_projects: false`) to avoid noisy submodules.
6. Keep collection discovery strict: include real project subfolders, drop random text-only folders.

## References
- `references/project-definition.md`
- `references/workflow.md`
