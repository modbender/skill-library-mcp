---
name: SpecKit Coding Agent
description: A complete Spec-Driven Development (SDD) workflow that transforms
  how you build software. Start with an idea → Create specifications → Generate
  plans → Execute tasks. Powered by spec-kit and OpenCo...
---

# SpecKit Coding Agent

**Version:** 1.1.0

---

## Summary

A complete **Spec-Driven Development (SDD)** workflow that transforms how you build software. Start with an idea → Create specifications → Generate plans → Execute tasks. Powered by spec-kit and OpenCode CLI, this skill ensures every line of code has a traceable requirement behind it.

### Key Features

- **6-Phase Workflow**: Constitution → Specification → Plan → Tasks → Implementation → Track
- **AI-Powered Artifacts**: Each phase generates Markdown documents via OpenCode
- **Living Documentation**: TASKS.md updates automatically as you implement
- **Multi-Agent Ready**: Delegation to subagents with full context preservation
- **Best Practices Built-In**: Clean code, TDD, and incremental delivery baked into the workflow

### Who It's For

- Developers who want specifications before code
- Teams needing traceable requirements
- AI-assisted projects requiring structured context
- Anyone building with OpenCode CLI

### Quick Example

```bash
# Initialize spec-kit
cd my-project && specify init --here --ai opencode

# Generate all artifacts
echo "/speckit.constitution" | opencode run  # Principles
echo "/speckit.specify" | opencode run       # Requirements
echo "/speckit.plan" | opencode run          # Architecture
echo "/speckit.tasks" | opencode run         # Action items

# Delegate to subagents → then update tracking
echo "/speckit.implement" | opencode run     # Marks completed tasks
```

---

This skill integrates **spec-kit** workflow with OpenCode for spec-driven development. Use this workflow to create specifications, plans, and tasks before coding.

### Prerequisites: Install and Initialize Spec-Kit

These steps must be completed before using any speckit commands.

#### Step 1: Install spec-kit
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

#### Step 2: Initialize spec-kit in project
```bash
cd /root/.openclaw/workspace/my-project
specify init --here --ai opencode
```

After initializing, `/speckit.*` commands will be available in your project directory.

---

### Spec-Driven Development Workflow

**Execute One Command at a Time - Sequential Execution Required!**

#### Step 1: Create Constitution
```bash
echo "/speckit.constitution
Create a project constitution focused on clean code principles, simplicity, and test-driven development.
" | opencode run
```
✅ Creates: `CONSTITUTION.md`

#### Step 2: Create Specification
```bash
echo "/speckit.specify
Create a baseline specification for a Python function that calculates factorial numbers recursively.
" | opencode run
```
✅ Creates: `SPECIFICATION.md`

#### Step 3: Create Plan
```bash
echo "/speckit.plan" | opencode run
```
✅ Creates: `PLAN.md`

#### Step 4: Generate Tasks
```bash
echo "/speckit.tasks" | opencode run
```
✅ Creates: `TASKS.md`

#### Step 5: Execute Implementation and Update Tasks

After subagents complete implementation, update tasks.md with execution status:

**Option A: Run /speckit.implement directly**
```bash
echo "/speckit.implement" | /root/.opencode/bin/opencode run
```
**Result:** Updates TASKS.md with executed tasks, marks as complete

**Option B: Manual update if implementation done externally**
```bash
# Manually update TASKS.md to mark completed tasks
# or let /speckit.implement scan and update
```

**Key Benefit:** `/speckit.implement` maintains a living task list with execution history

---

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. /speckit.constitution → CONSTITUTION.md (principles)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. /speckit.specify → SPECIFICATION.md (requirements)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. /speckit.plan → PLAN.md (implementation phases)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. /speckit.tasks → TASKS.md (actionable tasks)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Subagents read all artifacts and implement                   │
│    - CONSTITUTION.md, SPECIFICATION.md, PLAN.md, TASKS.md       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. /speckit.implement → Updates TASKS.md with status            │
│    - Marks [x] completed tasks                                  │
│    - Adds timestamps and metadata                               │
│    - Maintains living task list                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. Code implementation complete with tracked progress           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites (MUST COMPLETE FIRST!)

1. **Install spec-kit:**
   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ```

2. **Initialize spec-kit in your project:**
   ```bash
   cd ~/project
   specify init --here --ai opencode
   ```

3. **Execute workflow SEQUENTIALLY:**

   **Create Constitution**
   ```bash
   echo "/speckit.constitution
   Create a project constitution focused on clean code principles.
   " | opencode run
   ```

   **Create Specification**
   ```bash
   echo "/speckit.specify
   Create a REST API for user management.
   " | opencode run
   ```

   **Create Plan**
   ```bash
   echo "/speckit.plan" | opencode run
   ```

   **Generate Tasks**
   ```bash
   echo "/speckit.tasks" | opencode run
   ```

4. **Delegate to Subagents:**
   - Read all artifacts (CONSTITUTION.md, SPECIFICATION.md, PLAN.md, TASKS.md)
   - Implement tasks from TASKS.md

5. **Update Tasks with Execution Status:**
   ```bash
   echo "/speckit.implement" | /root/.opencode/bin/opencode run
   ```
   This updates TASKS.md to track what has been implemented.

---

## Complete Workflow Examples

### Example: Complete Spec-Driven Development Session

```bash
# Prerequisites (MUST DO FIRST!)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

cd ~/my-new-project
specify init --here --ai opencode

# Step 1: Create Constitution
echo "/speckit.constitution
Create a project constitution focused on clean code principles.
" | opencode run

# Step 2: Create Specification
echo "/speckit.specify
Create a REST API for user management.
" | opencode run

# Step 3: Generate Plan
echo "/speckit.plan" | opencode run

# Step 4: Generate Tasks
echo "/speckit.tasks" | opencode run

# Step 5: Delegate to subagent (read all artifacts first)

# Step 6: Update tasks.md with execution status
echo "/speckit.implement" | /root/.opencode/bin/opencode run
# This updates TASKS.md marking completed tasks
```

### Example: Adding a New Feature

```bash
# Step 1: Create specification for new feature
echo "/speckit.specify
Add authentication endpoints with JWT support.
" | opencode run

# Step 2: Generate plan
echo "/speckit.plan" | opencode run

# Step 3: Generate tasks
echo "/speckit.tasks" | opencode run

# Step 4: Delegate to subagent (read all artifacts first)

# Step 5: Update tasks.md with execution status
echo "/speckit.implement" | /root/.opencode/bin/opencode run
# This updates TASKS.md marking completed tasks
```

---

## Anti-Patterns to Avoid

❌ **DO NOT try to use speckit commands before initialization:**
```bash
cd /root/.openclaw/workspace/new-project
echo "/speckit.constitution" | opencode run  # Won't work!
```

✅ **Do this instead:**
```bash
cd /root/.openclaw/workspace/new-project
specify init --here --ai opencode  # DO THIS FIRST
echo "/speckit.constitution" | opencode run  # NOW it works
```

❌ **DO NOT pipe multiple commands:**
```bash
{ echo "/speckit.constitution"; echo "/speckit.specify"; } | opencode run
```

❌ **DO NOT skip /speckit.implement after implementation:**
```bash
# Wrong: TASKS.md stays with checkboxes empty
# Right: 
echo "/speckit.implement" | opencode run  # Updates TASKS.md
```

**Why:** Without updating TASKS.md, you lose track of what was actually implemented vs what was planned.

❌ **DO NOT execute without reading spec context:**
```bash
# Wrong: Subagent doesn't have spec context
sessions_spawn task="Implement authentication"
# Right: Subagent reads all artifacts
sessions_spawn task="Read CONSTITUTION.md, SPECIFICATION.md, PLAN.md, TASKS.md first."
```

---

## Why Use /speckit.implement?

**Benefits:**
1. **Automatic tracking**: TASKS.md gets updated with execution status
2. **Progress visibility**: Clear view of what's done vs pending
3. **Audit trail**: History of implementation steps
4. **Future reference**: See completed work for maintenance

**Best Practice:**
- Run `/speckit.implement` AFTER subagents complete work
- Or run it periodically to update progress
- The file becomes a living document of project state

---

## /speckit.implement - Execution Tracking

**Purpose:** Updates TASKS.md with execution status, marking completed tasks and tracking implementation progress.

### How It Works

When you run `/speckit.implement`, the system:
1. Scans the project directory for executed work
2. Reads the current TASKS.md
3. Marks tasks as [x] complete based on actual implementation
4. Updates the file with execution metadata

### Usage

```bash
echo "/speckit.implement" | /root/.opencode/bin/opencode run
```

### Example: Updated TASKS.md

After running `/speckit.implement`, TASKS.md transforms from:

**Before:**
```markdown
## Tasks

- [ ] Create HTML structure
- [ ] Implement CSS styling
- [ ] Add JavaScript functionality
```

**After:**
```markdown
## Tasks

- [x] Create HTML structure (completed 2026-02-11 19:42 UTC)
- [ ] Implement CSS styling (in progress)
- [ ] Add JavaScript functionality (pending)
```

### When to Run

| Timing | Action |
|--------|--------|
| After subagent completes | Run `/speckit.implement` to track progress |
| Before review | Check which tasks are done vs pending |
| After each feature | Update task status |
| End of session | Final update for audit trail |

### Manual Update Alternative

If implementation was done externally:

```bash
# Edit TASKS.md manually to mark completed tasks:
- [x] Task completed
- [ ] Task pending
```

Or use the subagent to scan and update automatically.

### Benefits of Consistent Usage

1. **Living Documentation:** TASKS.md becomes a real-time project status
2. **Progress Visibility:** Instantly see what's done, in-progress, pending
3. **Accountability:** Timestamps track when each task was completed
4. **Context Preservation:** Future team members see implementation history
5. **Regression Prevention:** Know exactly what was changed and when

### Best Practices

- Run `/speckit.implement` after EVERY subagent task
- Include in your daily workflow alongside spec commands
- Keep TASKS.md updated even for small changes
- Use timestamps for audit trail
- Reference updated TASKS.md when asking for help or reviews

---

## Fallback Strategy

When using OpenCode for coding tasks, the system follows this fallback strategy:

| Priority | Model | Provider | Role |
|----------|-------|----------|------|
| **Primary** | `opencode/kimi-k2.5-free` | OpenCode | Main model for coding tasks |
| **Fallback 1** | `opencode/minimax-m2.1-free` | OpenCode | High-quality alternative |
| **Fallback 2** | `opencode/glm-4.7-free` | OpenCode | Efficient standard tasks |
| **Secundário** | `openrouter/xiaomi/mimo-v2-flash` | OpenRouter | Cross-provider backup |

### Model Order for Opencode Task Execution

```json
{
  "primary": "opencode/kimi-k2.5-free",
  "fallbacks": [
    "opencode/minimax-m2.1-free",
    "opencode/glm-4.7-free"
  ]
}
```

**Cross-Provider Backup:** When OpenCode models are rate-limited or unavailable, the system falls back to `openrouter/xiaomi/mimo-v2-flash` (OpenRouter) for cross-provider resilience.

The primary model (`kimi-k2.5-free`) is used first, and if unavailable, the system automatically falls back through the other models in order.

### Why This Order?

- **Primary (Kimi K.25):** Best overall capability for coding and complex reasoning tasks
- **Fallback 1 (MiniMax M2.1):** Similar capability level, excellent for complex reasoning
- **Fallback 2 (GLM 4.7):** Efficient model for standard tasks when higher models hit limits
- **Secundário (Xiaomi Mimo v2 Flash):** Different provider (OpenRouter) ensures continuity when OpenCode models are rate-limited

---

## OpenCode

**Default Model:** `opencode/kimi-k2.5-free`

OpenCode is the preferred coding agent for this workspace. It uses kimi-k2.5-free as the primary model with automatic fallbacks to other free models.

```bash
# Basic usage (uses default kimi-k2.5-free model)
bash workdir:~/project background:true command:"opencode run \"Your task\""

# Explicit model specification (optional, defaults to kimi-k2.5-free)
bash workdir:~/project background:true command:"opencode run --model opencode/kimi-k2.5-free \"Your task\""

# If primary is unavailable, it automatically falls back:
# minimax-m2.1-free → glm-4.7-free → (openrouter/xiaomi/mimo-v2-flash as cross-provider backup)
```

---

## The Pattern: workdir + background

```bash
# Create temp space for chats/scratch work
SCRATCH=$(mktemp -d)

# Start agent in target directory ("little box" - only sees relevant files)
bash workdir:$SCRATCH background:true command:"<agent command>"
# Or for project work:
bash workdir:~/project/folder background:true command:"<agent command>"
# Returns sessionId for tracking

# Monitor progress
process action:log sessionId:XXX

# Check if done  
process action:poll sessionId:XXX

# Send input (if agent asks a question)
process action:write sessionId:XXX data:"y"

# Kill if needed
process action:kill sessionId:XXX
```

**Why workdir matters:** Agent wakes up in a focused directory, doesn't wander off reading unrelated files.

---

## Codex CLI

**Model:** `gpt-5.2-codex` is the default (set in ~/.codex/config.toml)

### Building/Creating (use --full-auto or --yolo)
```bash
# --full-auto: sandboxed but auto-approves in workspace
bash workdir:~/project background:true command:"codex exec --full-auto \"Build a snake game with dark theme\""

# --yolo: NO sandbox, NO approvals (fastest, most dangerous)
bash workdir:~/project background:true command:"codex --yolo \"Build a snake game with dark theme\""
```

### Reviewing PRs (vanilla, no flags)

Avoid reviewing PRs in the live clawdbot project folder. Use the project where the PR is submitted (if it's NOT ~/Projects/clawdbot), or clone to a temp folder first.

```bash
# Option 1: Review in the actual project (if NOT clawdbot)
bash workdir:~/Projects/some-other-repo background:true command:"codex review --base main"

# Option 2: Clone to temp folder for safe review (REQUIRED for clawdbot PRs!)
REVIEW_DIR=$(mktemp -d)
git clone https://github.com/clawdbot/clawdbot.git $REVIEW_DIR
cd $REVIEW_DIR && gh pr checkout 130
bash workdir:$REVIEW_DIR background:true command:"codex review --base origin/main"
```

**Why?** Checking out branches in the running Clawdbot repo can break the live instance!

---

## Claude Code

```bash
bash workdir:~/project background:true command:"claude \"Your task\""
```

---

## Pi Coding Agent

```bash
# Install: npm install -g @mariozechner/pi-coding-agent
bash workdir:~/project background:true command:"pi \"Your task\""
```

---

## Pi flags (common)

- `--print` / `-p`: non-interactive; runs prompt and exits.
- `--provider <name>`: pick provider (default: google).
- `--model <id>`: pick model (default: gemini-2.5-flash).

Examples:

```bash
# Set provider + model, non-interactive
bash workdir:~/project background:true command:"pi --provider openai --model gpt-4o-mini -p \"Summarize src/\""
```

---

## tmux (interactive sessions)

Use the tmux skill for interactive coding sessions (always, except very simple one-shot prompts). Prefer bash background mode for non-interactive runs.

---

## Parallel Issue Fixing with git worktrees + tmux

For fixing multiple issues in parallel, use git worktrees (isolated branches) + tmux sessions:

```bash
# 1. Clone repo to temp location
cd /tmp && git clone git@github.com:user/repo.git repo-worktrees
cd repo-worktrees

# 2. Create worktrees for each issue (isolated branches!)
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# 3. Set up tmux sessions
SOCKET="${TMPDIR:-/tmp}/codex-fixes.sock"
tmux -S "$SOCKET" new-session -d -s fix-78
tmux -S "$SOCKET" new-session -d -s fix-99

# 4. Launch Codex in each (after pnpm install!)
tmux -S "$SOCKET" send-keys -t fix-78 "cd /tmp/issue-78 && pnpm install && codex --yolo 'Fix issue #78.'" Enter
tmux -S "$SOCKET" send-keys -t fix-99 "cd /tmp/issue-99 && pnpm install && codex --yolo 'Fix issue #99.'" Enter

# 5. Monitor progress
tmux -S "$SOCKET" capture-pane -p -t fix-78 -S -30

# 6. Cleanup
tmux -S "$SOCKET" kill-server
git worktree remove /tmp/issue-78
git worktree remove /tmp/issue-99
```

**Why worktrees?** Each Codex works in isolated branch, no conflicts. Can run 5+ parallel fixes!

---

## Guidelines

1. **Respect tool choice** — if user asks for Codex, use Codex. Do not offer to build it yourself.
2. **Be patient** — don't kill sessions because they're "slow"
3. **Monitor with process:log** — check progress without interfering
4. **--full-auto for building** — auto-approves changes
5. **Parallel is OK** — run many Codex processes at once for batch work
6. **Avoid starting Codex in ~/clawd/** — it may read sensitive docs. Use target project dir or /tmp for blank slate chats
7. **Avoid checking out branches in ~/Projects/clawdbot/** — that directory contains the LIVE instance. Clone to /tmp or use git worktree for PR reviews

---

## References

- **Spec-Kit GitHub Repository**: https://github.com/github/spec-kit
- **OpenCode CLI Documentation**: https://opencode.ai/docs

### Related Skills

- **opencode-controller**: For controlling OpenCode via slash commands
- **freeride-opencode**: For configuring free models from OpenCode Zen
