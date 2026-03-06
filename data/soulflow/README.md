# SoulFlow — Workflow Framework for OpenClaw

**Build custom AI workflows for any task.** Each workflow is a series of steps that execute in isolated agent sessions with full tool access. Define your workflow in JSON, invoke it naturally, and let the agents handle the execution.

## What You Can Build

- **Development pipelines** (security audits, bug fixes, feature development)
- **Content workflows** (research → draft → edit → publish)
- **Operations automation** (deploy → verify → rollback-on-fail)
- **Research pipelines** (gather → analyze → synthesize → report)
- **Any multi-step task** that benefits from isolated, focused agent sessions

**Ships with 3 example dev workflows** to demonstrate the framework. Build your own for anything.

## Quick Start

### Natural Language (Easiest)

Just tell your agent what you need:
```
"Run a security audit on my project at ~/myapp"
"Fix this bug: users can't login with Google OAuth in ~/webapp"
"Build a referral system for ~/webapp"
```

Your agent reads `SKILL.md` and invokes SoulFlow automatically.

### Command Line

```bash
cd ~/.openclaw/workspace/soulflow

# Run a security audit
node soulflow.js run security-audit "Audit the codebase at ~/project for vulnerabilities"

# Fix a bug
node soulflow.js run bug-fix "Login returns 500 when email has uppercase letters in ~/myapp"

# Build a feature
node soulflow.js run feature-dev "Add dark mode toggle to the settings page in ~/myapp"
```

## How It Works

SoulFlow connects to your local OpenClaw gateway via WebSocket and runs each workflow step as an isolated agent session. A dedicated `soulflow-worker` agent is auto-created with minimal context — no memory bleed from your main agent.

**Each step:**
1. Gets a fresh session (no context bloat)
2. Receives the task + output from previous steps
3. Has full tool access (`read`, `write`, `edit`, `exec`, `browser`)
4. Must complete its work and report results

**Automatic notifications:**
When a workflow completes (success or failure), SoulFlow automatically sends a notification to your main agent session with:
- Workflow name and run ID
- Duration and step status
- Key results (extracted from output)
- Error details (if failed)

Your agent will relay the notification to you — no need to manually check status.

## Example Workflows (Included)

These demonstrate what's possible. Build your own for any domain.

### security-audit
**Scan → Prioritize → Fix → Verify**
Development example: Reads your source files, identifies vulnerabilities by severity, applies fixes, then verifies them.

### bug-fix
**Triage → Fix → Verify**
Development example: Investigates the root cause by reading code, applies the fix, then verifies it didn't introduce regressions.

### feature-dev
**Plan → Implement → Review**
Development example: Architects the implementation plan, writes the code, then reviews for quality and correctness.

**Want content workflows? Research pipelines? Deploy automation?** Create your own `.workflow.json` — see below.

## Creating Custom Workflows

### Via Chat

Tell your agent:
```
"Create a SoulFlow workflow for content publishing: research topic → draft article → edit → publish to blog"
```

Your agent will:
1. Design the workflow steps
2. Write the `.workflow.json` file to `workflows/`
3. Show you how to run it

### Via Interactive Builder

```bash
node lib/workflow-builder.js
```

Follow the prompts to define your workflow.

### Manual Creation

Create a `.workflow.json` file in the `workflows/` directory:

```json
{
  "id": "content-pipeline",
  "name": "Content Publishing Pipeline",
  "version": 1,
  "description": "Research, draft, edit, and publish blog content",
  "steps": [
    {
      "id": "research",
      "name": "Research Topic",
      "input": "Research the topic: {{task}}\n\nUse web_search and web_fetch to gather information. Create a research summary with key points, sources, and quotes.\n\nWhen done, end with: STATUS: done\nRESEARCH_FILE: path/to/research.md",
      "expects": "STATUS: done",
      "maxRetries": 1
    },
    {
      "id": "draft",
      "name": "Draft Article",
      "input": "Write a blog post based on this research:\n\n{{research_output}}\n\nOriginal topic: {{task}}\n\nCreate a well-structured article with intro, body, and conclusion. Save to a markdown file.\n\nWhen done, end with: STATUS: done\nDRAFT_FILE: path/to/draft.md",
      "expects": "STATUS: done",
      "maxRetries": 1
    },
    {
      "id": "edit",
      "name": "Edit and Polish",
      "input": "Edit this draft for clarity, grammar, and flow:\n\nDraft file: {{draft_file}}\n\nMake improvements using the `edit` tool. Focus on readability and engagement.\n\nWhen done, end with: STATUS: done\nFINAL_FILE: path/to/final.md",
      "expects": "STATUS: done",
      "maxRetries": 1
    }
  ]
}
```

### Variables

- `{{task}}` — The user's original task description
- `{{stepid_output}}` — Full output from a previous step (e.g. `{{research_output}}`)
- Any `KEY: value` lines in step output become variables (e.g. `DRAFT_FILE: ...` → `{{draft_file}}`)

### Prompt Tips

For best results, write prompts that:
- Explicitly tell the agent to use tools: "Use `read` to examine the file", "Use `edit` to apply the fix"
- Say "Do NOT just describe — actually do it"
- End with "When done, end with: STATUS: done"

## Commands

```bash
node soulflow.js run <workflow> "<task>"    # Run a workflow
node soulflow.js list                       # List available workflows
node soulflow.js runs                       # List past runs
node soulflow.js status [run-id]            # Check run status
node soulflow.js test                       # Test gateway connection
```

## Architecture

- **Zero dependencies** — Pure Node.js 22 (native WebSocket)
- **Gateway-native** — Connects via WebSocket with challenge-response auth
- **Session isolation** — Each step in a fresh session
- **Dedicated worker** — Auto-creates `soulflow-worker` agent with minimal brain files
- **JSON state** — Run history saved to `~/.openclaw/workspace/.soulflow/runs/`
- **10-minute timeout** per step (configurable)

## Requirements

- OpenClaw 2026.2.x or later
- Node.js 22+ (for native WebSocket)
- Gateway with token auth configured

## Security & Permissions

**SoulFlow requires elevated permissions to function:**

- **Reads gateway config** to obtain authentication token
- **Creates a worker agent** (`soulflow-worker`) with full tool access
- **Modifies gateway configuration** to add/manage the worker agent
- **Writes to filesystem** for run state and workflow outputs

These permissions allow workflows to read files, edit code, and run commands — the same capabilities you have when using OpenClaw directly. **Only run workflows from trusted sources.** Review workflow JSON files before execution, especially custom workflows from third parties.

See [Security & Permissions](SKILL.md#security--permissions) for detailed information.

## Installation

### Via ClawHub (Recommended)

```bash
openclaw skills install soulflow
```

### Manual

```bash
cd ~/.openclaw/workspace
git clone https://github.com/soulstack/soulflow.git
cd soulflow
node soulflow.js test
```

## License

MIT

## Credits

Built by [SoulStack](https://soulstack.app) as a framework for multi-step AI workflows. Inspired by the need for better dev automation, generalized for any domain.
