# Unitask Agent Onboarding (Agent-Driven)

Use this question flow when helping a user set up `unitask-agent`.

## Goal
Get the user from zero to a working Unitask MCP connection safely, with the right scopes.

## Step 1: Confirm account status
Ask:
1. "Do you already have a Unitask account?"

If **No**:
- Direct user to sign up at `https://unitask.app/signup`.
- After signup, ask them to open `Dashboard -> Settings -> API`.

If **Yes**:
- Continue to token setup.

## Step 2: Choose intended capabilities
Ask which actions they want the agent to perform:
1. Read-only planning (`read`)
2. Create/update/move/merge (`read + write`)
3. Deletion operations (`read + write + delete`)

Recommend least privilege by default.

## Step 3: Create API token
Guide user:
1. Open `Unitask -> Dashboard -> Settings -> API`.
2. Create token with selected scopes.
3. Copy token once (never paste token in chat).

## Step 4: Store token securely
Ask where they run the agent:
1. OpenClaw
2. Claude Code
3. VS Code MCP
4. Other MCP client

Then guide to configure:
- Env var key: `UNITASK_API_KEY`
- Header: `Authorization: Bearer <UNITASK_API_KEY>`
- Endpoint: `https://unitask.app/api/mcp`

## Step 5: Connectivity verification
Run these checks in order:
1. `list_tasks` with `limit=5`
2. `list_tags`
3. Optional write test: `create_task` with a temporary title

If any step fails:
- Verify token format and scope.
- Verify header value is injected.
- Verify endpoint URL is exact.

## Step 6: First-value commands (guided)
Offer starter prompts:
- "What are my tasks for today?"
- "Create a task: ship MCP tag support"
- "Tag this task as urgent"
- "Move this subtask under parent X"

## Safety reminders
- Never ask users to paste full API tokens into chat.
- Use dry-run first for compound actions (`move_subtask`, `merge_parent_tasks`).
- Confirm destructive actions before apply.
