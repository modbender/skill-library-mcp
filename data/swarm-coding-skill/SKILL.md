---
name: swarm-coding-skill
description: Autonomous multi-agent code generation. Planner creates manifest, specialized roles execute tasks. Generates complete projects with tests, Docker, CI, and decision logs.
requiredEnv:
  - OPENROUTER_API_KEY
optionalEnv:
  - OPENROUTER_MODEL
  - MOCK
warnings:
  - Writes to parent workspace (swarm-projects/, .learnings/). Run in isolated workspace.
  - Stores prompts and agent reasoning in DECISIONS.md and .learnings/. Do not include sensitive data.
  - Auto-includes Privy/web3 auth when prompts mention blockchain. Review generated code.
autonomy: orchestrator-driven-code-generation
outputPaths:
  - swarm-projects/{timestamp}/
  - .learnings/
  - DECISIONS.md
  - SWARM_SUMMARY.md
externalServices:
  - name: OpenRouter
    purpose: LLM inference for planning and code generation
    scope: API key sent with requests
capabilities:
  - code-generation
  - multi-agent-orchestration
  - project-scaffolding
  - docker-ci
  - testing
  - knowledge-grounded-decisions
  - continuous-improvement
---

# Swarm Coding Skill

Fully autonomous multi-agent software development. Given a plain-English prompt, the swarm designs, implements, tests, and delivers a complete project end-to-end.

**Core capability:** Code generation via OpenRouter's qwen3-coder model. The orchestrator drives a Planner to create a manifest, then executes specialized worker roles (BackendDev, FrontendDev, QA, DevOps, etc.) in dependency order. All code is written to files; no interactive sessions.

**Important:** This skill **generates code** for review and deployment by the user. It does not make business decisions or operate autonomously in production. The user remains responsible for security, compliance, and operational decisions.

## How It Works

1. **Orchestrator** (`Planner` role) analyzes your prompt, decides tech stack and architecture, and creates a `swarm.yaml` manifest with tasks and dependencies.
2. **Worker agents** (`BackendDev`, `FrontendDev`, `QA`, `DevOps`) are spawned as sub-sessions. Each has a clear persona and works on its assigned files in a shared workspace.
3. **Coordination**: The orchestrator tracks task completion and dependencies. When a task finishes, it marks it done and starts any unblocked downstream tasks.
4. **Conflict avoidance**: Files are partitioned by role (Backend owns `server/`, Frontend owns `client/`, etc.). If two roles need the same file, the manifest assigns an owner.
5. **Quality gates**: QA must pass tests before integration; DevOps ensures containerization; no merge without green tests.
6. **Deliverable**: You get a complete project directory with README, tests, Dockerfile, and optionally a GitHub repo or zip.

## Usage

```bash
# In your main OpenClaw session, invoke:
/trigger swarm-code "Build a dashboard that shows Moltbook stats and ClawCredit status"
```

The skill will:
- Spawn the orchestrator in an isolated session
- Orchestrator spawns workers sequentially or in parallel (based on dependencies)
- Output a final summary and path to the completed project

## Requirements

- Node.js v18+
- **Environment variables** (in `.env` at workspace root):
  - **Required:** `OPENROUTER_API_KEY` — OpenRouter API key with `qwen/qwen3-coder` access
  - Optional: `OPENROUTER_MODEL` (default: `qwen/qwen3-coder`), `MOCK=1` for dry-run
- Internet access for OpenRouter API (and optionally GitHub/Docker if deployment requested)

**Important:** The orchestrator reads `.env` from the workspace root (parent directory of this skill) and writes project files to `swarm-projects/` and logs to `.learnings/` in that same workspace root. Run in an isolated workspace to avoid exposing unrelated secrets.

## Configuration

Store your OpenRouter key in `.env` at the workspace root:

```
OPENROUTER_API_KEY=sk-or-...
```

Optional overrides:
```
OPENROUTER_MODEL=qwen/qwen3-coder
MOCK=1  # dry-run, no API calls
```

The skill uses `qwen/qwen3-coder` by default. Ensure your OpenRouter key has that model enabled.

## Output

The created project lives in `swarm-projects/<timestamp>/` and includes:
- `README.md` with run instructions
- `package.json` (or equivalent)
- Source code organized by component
- `test/` directory with automated tests
- `Dockerfile` and `docker-compose.yml` (if applicable)
- `CI/` with GitHub Actions workflow (optional)
- **`DECISIONS.md`** — Project memory documenting key architectural and technical decisions with rationale
- **`.learnings/`** — Learning logs capturing errors, insights, and feature requests
  - `ERRORS.md` — Failures, exceptions, and recovery actions
  - `LEARNINGS.md` — Corrections, better approaches, knowledge gaps
  - `FEATURE_REQUESTS.md` — Requested capabilities that don't exist yet
- **`SWARM_SUMMARY.md`** — Execution summary with role performance, statistics, and next steps

## Continuous Improvement

The swarm skill automatically captures learnings during execution to improve future runs:

### What Gets Logged
- **Worker failures** → `.learnings/ERRORS.md` with context and recovery suggestions
- **Better approaches discovered** → `.learnings/LEARNINGS.md` (e.g., "Simplified X by using Y")
- **User corrections** → `.learnings/LEARNINGS.md` when you override a decision
- **Missing capabilities** → `.learnings/FEATURE_REQUESTS.md` when you ask for something the skill can't do

### After Each Run
A `SWARM_SUMMARY.md` is generated with:
- Role success/failure rates
- Total files generated
- References to learnings captured
- Recommendations for next steps

### Promoting Learnings
Over time, review `.learnings/` files:
- Recurring error patterns → update orchestrator prompts or add retry logic
- Better approaches → incorporate into the skill's default behavior
- Feature requests → consider for skill enhancements

This creates a feedback loop where each swarm run makes the skill smarter.

## Example Prompts

- "Build a Node.js API with Express that serves Moltbook stats from JSON logs"
- "Create a React dashboard with dark theme and charts for ClawCredit status"
- "Make a CLI tool that checks ClawCredit pre-qualification and notifies via desktop alert"
- "Generate a smart contract that holds ClawCredit limits and allows x402 payments"
- "Build a hackathon app: a React dashboard that shows user's token balance using Privy auth" (includes Privy integration out of the box)

## Notes

- The skill makes all decisions autonomously: tech stack, file structure, library choices.
- If a task fails, the orchestrator will retry once with adjusted instructions.
- You can monitor progress via the sub-agent logs in `.openclaw/agents/<agent-id>/sessions/`.
- To stop early, send `/stop` to the orchestrator's session.
- **Privy Integration:** When the prompt mentions blockchain, web3, tokens, NFTs, or Privy, the skill automatically includes Privy authentication and wallet infrastructure. Backend includes `/auth/callback` with JWKS verification and a simulated fallback; frontend integrates `@privy-io/react-auth` if React is used. For advanced agentic wallet controls, see the [Privy Agentic Wallets skill](https://clawhub.ai/tedim52/privy).
- **Project Memory:** Each swarm run creates a `DECISIONS.md` file that documents significant decisions made by the planner and each agent. This serves as long-term knowledge grounding—future developers (or the same human weeks later) can understand why certain choices were made. Agents are prompted to explain their technical decisions (e.g., library selection, architecture patterns, security tradeoffs) as part of their output.

Enjoy your autonomous coding factory 🚀
