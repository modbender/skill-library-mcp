# letheclaw — ClawHub skill

This skill lets OpenClaw agents use **letheClaw** (strategic memory for AI agents): store and search memories, set criticality, mark operator corrections, and read provenance.

## What you need

- A running letheClaw API.  
  - In Docker with letheClaw: the API is usually at `http://api:8080`.  
  - On the host: often `http://localhost:51234` (see the main repo [README](../README.md) and [QUICKSTART](../QUICKSTART.md)).
- Set **LETHECLAW_API_URL** in your environment to the API base URL (no trailing slash), so the agent knows where to call.

## What the skill does

The agent can:

- **Store** memories (content, tags, source, operator, etc.).
- **Search** memories by meaning (semantic search).
- **List recent** memories.
- **Update criticality** of a memory (0–1, optional reason).
- **Mark correction** when the user corrects a memory (boosts criticality and records the event).
- **Get provenance** for a memory (full history of criticality events and correction count).

Details and request/response shapes are in [SKILL.md](SKILL.md) (used by the agent).

## Install

From the letheClaw repo root (or the folder containing `manifest.yaml` and `SKILL.md`):

```bash
openclaw skill publish .
```

Or follow [ClawHub publishing](https://openclawdoc.com/docs/skills/clawhub/) and install by name after publishing:

```bash
openclaw skill install letheclaw
```

## Configuration

Ensure the agent has network access and that `LETHECLAW_API_URL` is set where the agent runs (e.g. in your OpenClaw or ClawHub environment) to the letheClaw API base URL.

## Links

- Main repo: [letheClaw](../README.md)
- Integration (Docker, OpenClaw): [INTEGRATION.md](../INTEGRATION.md)
- ClawHub: [clawhub.ai](https://clawhub.ai/)
