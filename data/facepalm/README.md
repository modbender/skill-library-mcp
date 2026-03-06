# FACEPALM

**Crosscheck OpenClaw console logs with chat history to troubleshoot issues intelligently.**

FACEPALM analyzes OpenClaw console logs (`gateway.log`) and chat history from the last 5 minutes, then uses Codex 5.3 to diagnose and troubleshoot issues. Use it as a standalone troubleshooting tool or integrate it with other skills as needed.

## What it does

**ClawHub:** Update `clawhub install`/`clawhub publish` and all `clawhub.ai/...` links in this file when the new ClawHub instance is live.

When invoked (automatically by Agent Swarm or manually), FACEPALM:

1. Reads `gateway.log` from the last 5 minutes (configurable)
2. Extracts chat history from active session transcripts
3. Crosschecks console errors with chat context
4. Uses Codex 5.3 (`openrouter/openai/gpt-5.3-codex`) via OpenClaw CLI for intelligent troubleshooting
5. Returns actionable diagnosis with root cause analysis and recommended fixes

## Standalone troubleshooting tool

FACEPALM is a **standalone troubleshooting skill** that can be invoked manually or integrated with other skills. It's designed to be used independently or called by other automation tools when troubleshooting is needed.

## Manual usage

Run FACEPALM directly when you need intelligent troubleshooting analysis:

```bash
python3 workspace/skills/FACEPALM/scripts/facepalm.py [--minutes N] [--json] [--model MODEL_ID]
```

**Options:**
- `--minutes N` - Look at last N minutes (default: 5)
- `--json` - Output JSON only (for machine-readable output)
- `--model MODEL_ID` - Override model (default: `openrouter/openai/gpt-5.3-codex`)

**Examples:**

```bash
# Analyze last 5 minutes
python3 workspace/skills/FACEPALM/scripts/facepalm.py

# Analyze last 10 minutes with JSON output
python3 workspace/skills/FACEPALM/scripts/facepalm.py --minutes 10 --json

# Use absolute path from any directory
python3 ~/.openclaw/workspace/skills/FACEPALM/scripts/facepalm.py --minutes 5
```

## Requirements

- **OpenClaw** with `gateway.log` and session transcripts
- **OpenRouter API key** configured (for Codex 5.3 access)
- **`openclaw` CLI** on PATH (for invoking Codex via `openclaw agent`)

## Integration with other skills

FACEPALM can be integrated with other skills or automation tools. For example, you could:

- Call FACEPALM from a monitoring script when errors are detected
- Integrate with workflow automation tools
- Use it as part of a larger troubleshooting pipeline

**Example integration:**
```bash
# From another script or skill
python3 ~/.openclaw/workspace/skills/FACEPALM/scripts/facepalm.py --minutes 5 --json
```

## How it works

1. **Log collection:** Reads `OPENCLAW_HOME/logs/gateway.log` and filters lines from the last N minutes
2. **Chat history extraction:** Finds the main session and reads its transcript (`.jsonl` file) for recent messages
3. **Context formatting:** Combines logs and chat history into a structured prompt
4. **Codex invocation:** Uses `openclaw agent --message <prompt> --model openrouter/openai/gpt-5.3-codex --deliver`
5. **Diagnosis return:** Returns structured diagnosis with root cause, errors found, fixes, and resolution steps

## Output format

**Human-readable:**
```
🔍 FACEPALM Troubleshooting Analysis

Analyzed 45 log lines and 12 chat messages
Model: openrouter/openai/gpt-5.3-codex

============================================================
[Codex diagnosis here]
============================================================
```

**JSON (`--json`):**
```json
{
  "logs_count": 45,
  "chat_messages_count": 12,
  "diagnosis": "[Codex diagnosis]",
  "model_used": "openrouter/openai/gpt-5.3-codex",
  "time_window_minutes": 5
}
```

## Install

**From ClawHub (if published):**

```bash
npm install -g clawhub
clawhub install FACEPALM
```

**From GitHub:**

```bash
git clone https://github.com/RuneweaverStudios/FACEPALM.git
cp -r FACEPALM ~/.openclaw/workspace/skills/
```

**Manual:** Copy this folder into your OpenClaw workspace `skills/` directory (e.g. `~/.openclaw/workspace/skills/FACEPALM/`).

## GitHub repo

1. Create a new repository (e.g. `FACEPALM`) on GitHub. Do **not** add a README or .gitignore (this skill has its own).
2. From this skill directory (the repo root):

   ```bash
   git init
   git add SKILL.md README.md _meta.json scripts/
   git commit -m "Initial FACEPALM skill"
   git branch -M main
   git remote add origin https://github.com/RuneweaverStudios/FACEPALM.git
   git push -u origin main
   ```

3. Replace `RuneweaverStudios` with your GitHub username or org.

## ClawHub

Publish so others can install with `clawhub install FACEPALM`:

```bash
npm install -g clawhub
clawhub login   # if needed
cd /path/to/FACEPALM   # this skill folder as root
clawhub publish .
```

The skill slug will be `FACEPALM`. After publishing, users run:

```bash
clawhub install FACEPALM
```

## Related skills

- **[Agent Swarm](https://clawhub.ai/skills/agent-swarm)** - Automatically invokes FACEPALM when troubleshooting loops detected
- **[gateway-guard](https://clawhub.ai/skills/gateway-guard)** - Keeps gateway auth stable
- **[what-just-happened](https://clawhub.ai/skills/what-just-happened)** - Summarizes gateway restarts

## License

MIT (or your choice).
