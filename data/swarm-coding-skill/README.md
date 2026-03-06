# Swarm Coding Skill

Fully autonomous multi-agent software development. Give a plain-English prompt describing an app, and the swarm designs, implements, tests, and delivers a complete project end-to-end.

## Requirements

- Node.js v18+
- OpenRouter API key with access to `qwen/qwen3-coder`
- Workspace with `.env` containing `OPENROUTER_API_KEY`

## Usage

```bash
# From the workspace root, run:
cd clawhub-swarm-coding-skill
node orchestrator.js "Build a dashboard that shows Moltbook stats and ClawCredit status"
```

The orchestrator will:
1. Create a project workspace under `swarm-projects/<timestamp>/`
2. Spawn a Planner (uses qwen-coder) to generate a `swarm.yaml` manifest
3. Execute specialized workers: BackendDev, FrontendDev, QA, DevOps
4. Assemble final project in the same directory
5. Print the final location on success

You can then `cd` into that directory and run `npm install` and `npm start`.

## How It Works

- **Exclusive model**: All agents use `qwen/qwen3-coder` (the correct OpenRouter model ID is `qwen/qwen3-coder`, *not* `openrouter/qwen/qwen3-coder`).
- **Manifest**: A YAML-like JSON describing roles, outputs, and dependencies
- **Workers**: Each runs sequentially based on dependencies; each writes files to a shared `files/` workspace
- **Retry**: Failed tasks are retried once with stricter instructions
- **Quality**: QA must create tests; DevOps adds Docker and CI; all code is production-style

### Model Access

Ensure your OpenRouter API key has `qwen/qwen3-coder` enabled:
1. Go to https://openrouter.ai/keys
2. Edit your key
3. Under "Model Access", check `qwen/qwen3-coder`
4. Save

If you get `"not a valid model ID"` errors, it usually means the model ID format is wrong or your key lacks access.

## Output Structure

```
swarm-projects/
└── swarm-2026-02-14T21-30-00/
    ├── swarm.yaml              # manifest
    ├── tasks.json              # execution log
    ├── DECISIONS.md            # architectural decisions with rationale
    ├── .learnings/             # continuous improvement logs
    │   ├── ERRORS.md           # failures and recovery actions
    │   ├── LEARNINGS.md        # corrections and better approaches
    │   └── FEATURE_REQUESTS.md # missing capabilities
    ├── SWARM_SUMMARY.md        # execution summary with role stats
    ├── files/                  # per-role file trees during creation
    │   ├── backend-dev/
    │   ├── frontend-dev/
    │   ├── qa/
    │   └── devops/
    ├── server.js               # final assembled files (example)
    ├── public/
    ├── test/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .github/workflows/ci.yml
    └── README.md
```

## Continuous Improvement

The swarm skill captures learnings from each run to improve future projects:

- **`DECISIONS.md`** — Records architectural choices (tech stack, auth method, etc.) with rationale. Explains *why* the project is structured this way.
- **`.learnings/`** — Logs errors, corrections, and feature requests:
  - `ERRORS.md` — Worker failures with context and suggested recovery
  - `LEARNINGS.md` — Better approaches discovered, knowledge gaps filled
  - `FEATURE_REQUESTS.md` — Capabilities users requested but aren't available
- **`SWARM_SUMMARY.md`** — Execution overview: role success rates, file counts, learning references, next steps

Review these files after each run to understand what worked, what didn't, and how to improve future swarm projects. Promising patterns can be promoted into the skill's documentation or prompts.

## Notes

- The orchestrator is the only agent that calls OpenRouter; workers are just instructions executed within the same process (sub-agents in a future version)
- File conflicts are avoided by partitioning outputs by role; the manifest defines ownership
- If a task fails twice, the whole run aborts. Check `files/<role>/raw.txt` for the failed output
- Ensure your OpenRouter key has sufficient rate limits; a typical project uses ~5–8 calls
- For demo without spending quota, set `MOCK=1` in the environment to use canned responses (no API calls)

## Example Prompt

> "Build a Node.js and Express API that serves Moltbook posting statistics from local JSON logs, and a vanilla JS frontend that displays them in a dark-themed dashboard with Krump colors."

That will produce a ready-to-run dashboard similar to what you saw earlier.

## Security

Your OpenRouter key is read from `.env`. Never commit that file. All generated code is written under `swarm-projects/`; review before deployment.
