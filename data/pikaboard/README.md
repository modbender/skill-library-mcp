# PikaBoard Skill

This folder contains the ClawHub/OpenClaw skill package for PikaBoard.

## File Naming

- Use `SKILL.md` for the actual skill definition and metadata (canonical for ClawHub/OpenClaw).
- Use `README.md` for human-facing setup and usage docs.
- Do not use `prompt.md` or `clawhub.md` unless your tooling explicitly requires them.

## Quick Setup

1. Install skill from ClawHub: `angelstreet/pikaboard`
2. Start backend:

```bash
cd pikaboard/backend && npm start
```

3. Set env vars:

```bash
export PIKABOARD_API="http://localhost:3001/api"
export PIKABOARD_TOKEN="<token-from-pikaboard/backend/.env>"
export AGENT_NAME="<your-agent-name>"
```

4. Auto-configure board:

```bash
cd pikaboard
MY_BOARD_ID="$(
  ./skills/pikaboard/scripts/setup-agent-board.sh | sed -n 's/^MY_BOARD_ID=//p' | tail -n1
)"
export MY_BOARD_ID
```

5. Validate:

```bash
curl -s http://localhost:3001/health
curl -s -H "Authorization: Bearer $PIKABOARD_TOKEN" "$PIKABOARD_API/boards"
curl -s -H "Authorization: Bearer $PIKABOARD_TOKEN" "$PIKABOARD_API/tasks?board_id=$MY_BOARD_ID&status=up_next"
```

## Ready-To-Send Agent Prompt

```text
Install and use `angelstreet/pikaboard` from ClawHub, end-to-end.

1) Install the skill (from ClawHub) and clone/build PikaBoard from GitHub.
2) Start backend:
   cd pikaboard/backend && npm start
3) Read token from backend env (`PIKABOARD_TOKEN` in `pikaboard/backend/.env`).
4) Set runtime env:
   export PIKABOARD_API="http://localhost:3001/api"
   export PIKABOARD_TOKEN="<token>"
   export AGENT_NAME="<your-agent-name>"
5) Auto-configure board:
   cd pikaboard
   MY_BOARD_ID="$(
     ./skills/pikaboard/scripts/setup-agent-board.sh | sed -n 's/^MY_BOARD_ID=//p' | tail -n1
   )"
   export MY_BOARD_ID
6) Verify:
   curl -s http://localhost:3001/health
   curl -s -H "Authorization: Bearer $PIKABOARD_TOKEN" "$PIKABOARD_API/boards"
   curl -s -H "Authorization: Bearer $PIKABOARD_TOKEN" "$PIKABOARD_API/tasks?board_id=$MY_BOARD_ID&status=up_next"

Operate only on tasks from `board_id=$MY_BOARD_ID` unless explicitly told otherwise.
```
