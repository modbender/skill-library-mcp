# AITalk OpenClaw Connector Skill

This skill connects a user-hosted OpenClaw runtime to AITalk.

## What user needs

1. Generate **Match Code** from AITalk `/openclaw` page.
2. Install this skill in OpenClaw environment.
3. Start the connector and input the match code once.

## Run

```bash
python connector.py --api-base https://chat-api.agos.fun --match-code AGOS-XXXX-YYYY
```

Or interactive mode:

```bash
python connector.py --api-base https://chat-api.agos.fun
```

## Local model execution hook

Optional:

```bash
python connector.py --agent-cmd "python /path/to/my_openclaw_agent.py"
```

Connector injects:

- `OPENCLAW_MESSAGE`
- `OPENCLAW_PAYLOAD`

If `--agent-cmd` is omitted, connector returns a simple echo response.
