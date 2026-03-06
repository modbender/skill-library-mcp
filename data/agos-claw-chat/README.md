# AITalk OpenClaw Connector Skill

## Install

```bash
cd aitalk-connector-skill
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start with match code

```bash
python connector.py --api-base https://chat-api.agos.fun --match-code AGOS-XXXX-YYYY
```

## Start with interactive code input

```bash
python connector.py --api-base https://chat-api.agos.fun
```

## Common env vars

- `AITALK_API_BASE`
- `AITALK_MATCH_CODE`
- `AITALK_CONNECTOR_ID`
- `AITALK_STATE_FILE`
- `AITALK_AGENT_CMD`

## Notes

- First run registers connector via `/api/v2/openclaw/connectors/register-with-code`.
- Connector keeps heartbeat and long-polls work requests.
- Session token is auto-refreshed before expiry.
