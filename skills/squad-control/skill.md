---
name: squad-control
version: 1.1.6
homepage: https://squadcontrol.ai
env:
  SC_API_URL:
    description: Base URL of your Squad Control instance (e.g. https://www.squadcontrol.ai)
    required: true
  SC_API_KEY:
    description: >
      API key from Squad Control Settings → API Keys. Can be workspace-scoped (single workspace)
      or account-scoped (all workspaces). Account-scoped keys are recommended for multi-workspace
      setups — tasks will include an embedded workspace object with all config needed.
    required: true
  GITHUB_TOKEN:
    description: >
      GitHub Personal Access Token for PR creation and repo cloning.
      When not set manually, the skill uses the token returned by the Squad Control API
      (workspace.githubToken) — configured in Squad Control Settings → Project Repository.
    required: false
description: >
  Integrate with Squad Control kanban for AI agent task orchestration.

  ⚠️ Security note: This skill handles GitHub tokens and API keys by design — it clones
  private repos, pushes code, and creates PRs on your behalf. Review setup.md for security
  guidance before installing. Only connect to Squad Control instances you trust.

  Use when:
  - A cron fires to check for pending tasks
  - You need to pick up, dispatch, or complete a kanban task
  - You need to create a PR and route it for code review
  - You need to spawn a sub-agent to work on an assigned task
  - You need to report task success or failure back to Squad Control
  - You need to create tasks programmatically (break down work)

  Don't use when:
  - The user is asking a general question (just answer directly)
  - You're doing work that isn't tracked in Squad Control
  - You're working inside a sub-agent session (you're already dispatched — just do the work)
  - The user wants to manage agents/settings in the UI (direct them to squadcontrol.ai)

  Inputs: Squad Control API credentials, task data from /api/tasks/pending
  Outputs: PRs on GitHub, task status updates in Squad Control, review verdicts
---

# Squad Control Integration

Orchestrate AI agent tasks from Squad Control's kanban board.

## Quick Reference
- **Setup:** `references/setup.md`
- **Full API:** `references/api.md`
- **PR template:** `references/pr-template.md`
- **Review checklist:** `references/review-checklist.md`

Required env vars: `SC_API_URL`, `SC_API_KEY`

---

## Task Polling Flow

When a cron fires to check for tasks:

1. Run `~/.openclaw/skills/squad-control/scripts/poll-tasks.sh` (requires `SC_API_URL` and `SC_API_KEY` env vars)
2. If output is `HEARTBEAT_OK` → no work, stop
3. If output contains `PENDING_TASKS:` → parse the JSON after it, follow **Pickup & Dispatch** below for each task
4. If output contains `REVIEW_TASKS:` → parse the JSON after it, follow **Review Dispatch** below for each task
5. If output contains `STUCK_TASKS:` → parse the JSON after it, follow **Stuck Task Recovery** below for each task

Alternatively, call the APIs directly:
- Pending: `curl -sL "${SC_API_URL}/api/tasks/pending" -H "x-api-key: ${SC_API_KEY}"`
- Review: `curl -sL "${SC_API_URL}/api/tasks/list?status=review" -H "x-api-key: ${SC_API_KEY}"`

Parse workspace config from the response (see **Multi-Workspace Response Handling** below).

### Multi-Workspace Response Handling

`/api/tasks/pending` can return tasks from **multiple workspaces** when using an account-level API key. Each task includes an embedded `workspace` object with all config needed to work on it.

**Response shape — workspace-scoped key (legacy / single-workspace):**
```json
{
  "workspace": { "_id": "wsId", "name": "MyApp", "repoUrl": "...", "githubToken": "..." },
  "tasks": [{ "_id": "taskId", "title": "...", "agent": { ... } }]
}
```
→ `workspace` is at the top level; tasks do not have their own workspace object.

**Response shape — account-scoped key (multi-workspace):**
```json
{
  "tasks": [
    {
      "_id": "taskId",
      "title": "...",
      "workspace": {
        "_id": "wsId",
        "name": "MyApp",
        "repoUrl": "https://github.com/org/repo",
        "githubToken": "ghp_...",
        "agentConcurrency": 3
      },
      "agent": { ... }
    }
  ]
}
```
→ Each task carries its own `workspace` object. Tasks from different workspaces may appear in the same response.

**Agent fields — always nested under `task.agent` (never flat on task root):**
```json
{
  "agent": {
    "_id": "agentId",
    "name": "Cody",
    "role": "Developer",
    "model": "anthropic/claude-sonnet-4-6",
    "soulMd": "..."
  }
}
```
> ⚠️ Do NOT use `task.agentName` — that field does not exist. Always use `task.agent.name`, `task.agent.model`, `task.agent.soulMd`, `task.agent._id`.

**Handling both shapes (backward compatible):**

```javascript
// For each task:
// - If task.workspace is present → use it directly
// - If not → use the top-level workspace from the response
const wsConfig = task.workspace ?? response.workspace;
const repoUrl = wsConfig.repoUrl;
const githubToken = wsConfig.githubToken;
const concurrencyLimit = wsConfig.agentConcurrency ?? 2;
```

**Concurrency per workspace:** When tasks from multiple workspaces are returned, apply `agentConcurrency` **per workspace independently**. Do not count agents running for workspace A against workspace B's limit.

```javascript
// Group by workspace, then dispatch up to concurrency limit for each
const byWorkspace = groupBy(tasks, t => (t.workspace ?? topLevelWs)._id);
for (const [wsId, wsTasks] of Object.entries(byWorkspace)) {
  const ws = wsTasks[0].workspace ?? topLevelWs;
  const limit = ws.agentConcurrency ?? 2;
  const running = countRunningAgentsFor(wsId);
  const slots = Math.max(0, limit - running);
  for (const task of wsTasks.slice(0, slots)) {
    dispatch(task, ws);
  }
}
```

### Stuck Task Recovery

Run two checks every cron cycle:

**Check 1 — Tasks stuck in "working" with a PR deliverable:**
```bash
curl -sL "${SC_API_URL}/api/tasks/list?status=working" -H "x-api-key: ${SC_API_KEY}"
```
For each working task where `deliverables` contains a PR entry and `startedAt` is more than 30 minutes ago → auto-rescue by moving to review:
```bash
curl -sL -X POST "${SC_API_URL}/api/tasks/set-review" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${ASSIGNED_AGENT_ID}\", \"result\": \"Auto-rescued: sub-agent completed work but did not transition status.\", \"deliverables\": ${EXISTING_DELIVERABLES}}"
```
Post to thread: *"Auto-moved to review — sub-agent completed PR but didn't call set-review."*

**Check 2 — Tasks marked "done" with an unmerged/open PR:**
```bash
curl -sL "${SC_API_URL}/api/tasks/list?status=done" -H "x-api-key: ${SC_API_KEY}"
# Filter to tasks completed in the last 2 hours that have a PR deliverable
```
For each recently-done task with a PR deliverable, verify the PR is actually merged:
```bash
# Extract owner/repo from workspace.repoUrl
# Extract PR number from deliverable URL (e.g. https://github.com/org/repo/pull/123 → 123)
curl -sL -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/${owner}/${repo}/pulls/${PR_NUMBER}" | grep -o '"merged":[^,]*'
```
If `"merged":false` (PR still open) → the agent skipped review. Re-open for Hawk:
```bash
# Create a review task for Hawk
curl -sL -X POST "${SC_API_URL}/api/tasks/create" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"title\": \"Review PR #${PR_NUMBER}: ${TASK_TITLE}\", \"description\": \"Agent marked task done but PR is still open and unmerged. Please review and merge if approved.\\n\\nPR: ${PR_URL}\", \"assignedAgentId\": \"${REVIEWER_AGENT_ID}\", \"workspaceId\": \"${WORKSPACE_ID}\", \"priority\": \"high\"}"
```
Post a warning to the original task thread: *"⚠️ Task was marked done but PR #N is unmerged. Created review task for Hawk."*

### Review Dispatch

When review tasks are found, find the reviewer agent first:
```bash
curl -sL "${SC_API_URL}/api/agents" -H "x-api-key: ${SC_API_KEY}"
# Find agent with role containing "Reviewer" or name "Hawk"
```

For each review task (has PR deliverable, `pickedUpAt` not set):

**Do NOT call `/api/tasks/pickup`** — the state machine blocks `review → working` transitions. Instead, spawn the reviewer directly and let them call `/api/tasks/review` (verdict) which transitions `review → done` or `review → assigned`.

Spawn the reviewer agent using the **Review Flow** template below, passing the task ID and all context directly.

### Squad Lead Tasks — Merge & Complete

When the task's assigned agent is the **Squad Lead** (role contains "Lead" or "Orchestrator"), it means Hawk approved a PR and it's ready to merge. Do NOT just mark it done — merge the PR first.

```bash
# 1. Pick up the task
curl -sL -X POST "${SC_API_URL}/api/tasks/pickup" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${SQUAD_LEAD_ID}\"}"
# Response includes workspace.repoUrl, workspace.githubToken, task.deliverables

# 2. Find the PR deliverable — check type OR url, not just name
# Priority: type === "pr" first, then url containing "/pull/"
# Examples that all qualify: {type:"pr"}, {url:"…/pull/7"}, {name:"PR #7", type:"pr"}
# NEVER complete as done if any deliverable has type="pr" or url containing "/pull/"

# 3. Clone and merge (use credential helper — do NOT embed token in URL)
if [ -n "$GITHUB_TOKEN" ]; then
  git -c "credential.helper=!f() { echo username=x-access-token; echo password=${GITHUB_TOKEN}; }; f" clone "$REPO_URL" /tmp/merge-repo
else
  git clone "$REPO_URL" /tmp/merge-repo
fi
cd /tmp/merge-repo
git fetch origin
git checkout main && git pull origin main
git merge --no-ff origin/task/${TASK_ID} -m "Merge PR #${PR_NUMBER}: ${TASK_TITLE}"
git push origin main

# 4. Post to thread
curl -sL -X POST "${SC_API_URL}/api/threads/send" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${SQUAD_LEAD_ID}\", \"content\": \"Merged PR #${PR_NUMBER} to main.\"}"

# 5. Complete the task
curl -sL -X POST "${SC_API_URL}/api/tasks/complete" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${SQUAD_LEAD_ID}\", \"result\": \"Merged PR #${PR_NUMBER} to main.\", \"status\": \"done\"}"
```

**If merge fails** (conflicts): call `/api/tasks/fail` with the error — don't force-merge. Post the conflict details to the thread.
**If no PR deliverable**: just complete the task directly.

---

### Concurrency Limit

**Before spawning anything**, check how many sub-agents are already running:
```
subagents(action="list")
```
Count agents with `status = "running"`. The concurrency limit comes from `workspace.agentConcurrency` (default: 2 if not set).

**With a single workspace:** If running agents ≥ limit, skip all spawning this cycle and reply `HEARTBEAT_OK`.

**With multiple workspaces (account-level key):** Apply the limit **per workspace independently**. A workspace with `agentConcurrency: 3` can have up to 3 agents running regardless of what other workspaces are doing. Group tasks by workspace and check each workspace's running count separately.

Also, never dispatch more than `workspace.agentConcurrency` tasks per workspace per cron run. The rest will be picked up on the next run.

The workspace owner can change this limit in Squad Control → Settings → Agent Concurrency.

---

### Pickup & Dispatch

```bash
# Pick up task (marks it in-progress in Squad Control)
curl -sL -X POST "${SC_API_URL}/api/tasks/pickup" \
  -H "x-api-key: ${SC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${AGENT_ID}\", \"branch\": \"task/${TASK_ID}\"}"
# Response includes workspace.repoUrl and workspace.githubToken
```

Post to the task thread that work is being dispatched:
```bash
curl -sL -X POST "${SC_API_URL}/api/threads/send" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${AGENT_ID}\", \"content\": \"Picking up task. Starting work now.\"}"
```

Then spawn a sub-agent with the task's agent persona. Include the workspace name in the label so multi-workspace runs are easy to identify:

```
sessions_spawn({
  task: <see Spawn Prompt Template below>,
  model: agent.model,
  label: "${agent.name}-${workspace.name}-${taskTitle}",
  runTimeoutSeconds: 1800
})
```

### Spawn Prompt Template

When building this prompt, resolve workspace config as follows:
- **If `task.workspace` is present** (account-scoped key): use `task.workspace.repoUrl`, `task.workspace.githubToken`, `task.workspace.agentConcurrency`
- **If `task.workspace` is absent** (workspace-scoped key): use the top-level `workspace` from the response

```
# Identity
${agent.soulMd}

# Squad Control Credentials (use these for ALL API calls)
SC_API_URL=${SC_API_URL}
SC_API_KEY=${SC_API_KEY}
TASK_ID=${task._id}
AGENT_ID=${agent._id}

# Repository
REPO_URL=${workspace.repoUrl}
GITHUB_TOKEN=${workspace.githubToken}  # may be empty for public repos

# Clone the repo (use credential helper — do NOT embed token in URL)
if [ -n "$GITHUB_TOKEN" ]; then
  git -c "credential.helper=!f() { echo username=x-access-token; echo password=${GITHUB_TOKEN}; }; f" clone "$REPO_URL" /tmp/task-repo
else
  git clone "$REPO_URL" /tmp/task-repo
fi
cd /tmp/task-repo
git checkout -b task/${task._id}

# Task
**${task.title}**
${task.description}

# Git Workflow
- Small, focused commits (feat:, fix:, chore: prefixes)
- Scope changes to this task only
- Run `npx tsc --noEmit` or existing tests before finishing

# When Done — follow these steps EXACTLY, do not skip any

## 1. Commit and push
git add -A && git commit -m "feat: ${task.title}"
git push origin task/${task._id}

## 2. Create GitHub PR
curl -sL -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/${owner}/${repo}/pulls" \
  -d '{"title": "${task.title}", "head": "task/${task._id}", "base": "main", "body": "${summary}"}'
# Save the PR number and URL from the response

## 3. Post summary to thread
curl -sL -X POST "${SC_API_URL}/api/threads/send" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d '{"taskId": "${TASK_ID}", "agentId": "${AGENT_ID}", "content": "Work complete. PR #N: ${PR_URL}\n\n${summary}"}'

## 4. If any files in convex/ were changed
# Deployment is handled by CI after merge to main.
# Do NOT run local deploy commands from this skill prompt.
# If a manual deploy is required, ask the squad lead to run it in a controlled environment.

## 5. Hand off for review (REQUIRED — NEVER call /complete if you opened a PR)

> ⚠️ CRITICAL: If you created a PR in step 2, you MUST call set-review — not complete.
> Calling /complete with an open PR bypasses code review entirely. This is a workflow violation.
> The ONLY time to call /complete directly is when there is NO PR (e.g. a research or docs-only task).

```bash
curl -sL -X POST "${SC_API_URL}/api/tasks/set-review" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d '{"taskId": "${TASK_ID}", "agentId": "${AGENT_ID}", "result": "${summary}", "deliverables": [{"type": "pr", "name": "PR #N", "url": "${PR_URL}"}]}'
```

Verify the API response confirms status changed to "review". If it returns an error, retry once then call /fail with the error details.

## If anything fails
curl -sL -X POST "${SC_API_URL}/api/tasks/fail" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d '{"taskId": "${TASK_ID}", "agentId": "${AGENT_ID}", "error": "description of what went wrong"}'
```

### On Completion

1. Post findings/summary to task thread:
   ```bash
   curl -sL -X POST "${SC_API_URL}/api/threads/send" \
     -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
     -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${AGENT_ID}\", \"content\": \"${SUMMARY}\"}"
   ```
2. Create PR via GitHub API (see `references/pr-template.md`)
3. If a reviewer agent exists → set task to review:
   ```bash
   curl -sL -X POST "${SC_API_URL}/api/tasks/set-review" \
     -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
     -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${AGENT_ID}\", \"result\": \"${SUMMARY}\", \"deliverables\": [{\"type\": \"pr\", \"name\": \"PR #N\", \"url\": \"${PR_URL}\"}]}"
   ```
4. If no reviewer → complete directly:
   ```bash
   curl -sL -X POST "${SC_API_URL}/api/tasks/complete" \
     -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
     -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${AGENT_ID}\", \"result\": \"${SUMMARY}\", \"status\": \"done\"}"
   ```

### On Failure

Always report failures — don't silently mark done:
```bash
curl -sL -X POST "${SC_API_URL}/api/tasks/fail" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"agentId\": \"${AGENT_ID}\", \"error\": \"description of what went wrong\"}"
```

---

## Review Flow

When routing to a reviewer agent, spawn them with this prompt (fill in all values):

```
# Identity
${reviewer.soulMd}

# Task: Review PR #${prNumber}
**Original task:** ${task.title}
**PR:** ${prUrl}
**Repo:** ${workspace.repoUrl}
**GitHub token:** ${workspace.githubToken}   # may be empty for public repos

# Extract owner/repo from repoUrl
# e.g. https://github.com/org/repo -> owner=org, repo=repo

# Step 1 — Get the diff
curl -sL -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/files"

# Step 2 — Review the code
Check: correctness, code quality, security, edge cases.

# Step 3 — Post review to GitHub PR (REQUIRED — not just to thread)
curl -sL -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/reviews" \
  -d '{"event": "APPROVE", "body": "<review summary>"}'
# Use "REQUEST_CHANGES" instead of "APPROVE" if changes are needed

# Step 4 — Post summary to Squad Control thread
curl -sL -X POST "${SC_API_URL}/api/threads/send" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d '{"taskId": "${TASK_ID}", "agentId": "${REVIEWER_ID}", "content": "## Review — PR #${prNumber}\n\n${summary}"}'

# Step 5 — Submit verdict to Squad Control
curl -sL -X POST "${SC_API_URL}/api/tasks/review" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d '{"taskId": "${TASK_ID}", "agentId": "${REVIEWER_ID}", "verdict": "approve", "comments": "${summary}"}'
# Use "request_changes" if not approving
```

**Note:** `workspace.githubToken` comes from the `/api/tasks/pending` or `/api/tasks/pickup` response. Never read it from a credentials file — it may not exist on this machine.

---

## Discovering Agents

```bash
curl -sL "${SC_API_URL}/api/agents" -H "x-api-key: ${SC_API_KEY}"
```

Look for `role: "Code Reviewer"` to identify the reviewer agent.

## Creating Tasks Programmatically

```bash
curl -sL -X POST "${SC_API_URL}/api/tasks/create" \
  -H "x-api-key: ${SC_API_KEY}" -H "Content-Type: application/json" \
  -d '{"title": "...", "description": "...", "assignedAgentId": "..."}'
```

---

## Common Mistakes

1. **Marking done without doing work** — Always post results to the thread and create a PR (if code task) before marking complete. Empty result + no thread messages = task wasn't really done.
2. **Sub-agent calling /complete instead of /complete after opening a PR** — This is the most common workflow violation. If a PR was opened, the ONLY valid next call is `set-review`. Calling `complete` directly skips code review entirely and leaves an unmerged PR dangling. The stuck task recovery check now catches "done" tasks with open PRs and auto-creates a Hawk review task.
3. **Squad Lead skipping the merge** — When a task is assigned to the Squad Lead and has a PR deliverable, merge the PR to main BEFORE marking complete.
4. **Not passing SC_API_URL/SC_API_KEY into spawn prompt** — Sub-agents can't call back to Squad Control without these. Always include them in the spawn template.
5. **Not using workspace.repoUrl** — The pending and pickup responses include `workspace.repoUrl` and `workspace.githubToken`. Use them — don't assume a default repo path.
6. **Forgetting to report failure** — If something goes wrong, call `/api/tasks/fail`. Tasks stuck in "working" forever block the queue.
7. **Cloning without token on private repos** — Check `workspace.githubToken` and use the git credential helper: `git -c "credential.helper=!f() { echo username=x-access-token; echo password=<token>; }; f" clone "$REPO_URL"` — never embed the token directly in the URL as it can leak via process lists, git remotes, or logs.
8. **Not pulling latest before branching** — Creates PRs against stale main, causing merge conflicts.
9. **Applying global concurrency instead of per-workspace** — When handling tasks from multiple workspaces (account-level key), each workspace has its own `agentConcurrency` limit. Don't count agents running for workspace A against workspace B's limit.
10. **Ignoring `task.workspace` and always using top-level config** — Account-level keys embed workspace config directly in each task. If `task.workspace` is present, use it; fall back to the top-level workspace only when it's absent.
