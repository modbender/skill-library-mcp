# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A single-file Python HTTP relay (`relay.py`) that bridges AI assistants to a local Chromium browser via Chrome DevTools Protocol (CDP). The relay listens on `127.0.0.1:18792` and forwards commands to Chromium's CDP on port 9222. This lets AI agents control a browser from the user's local IP, bypassing data-center IP blocks on platforms like Xiaohongshu.

## Running

```bash
# Prerequisites: Chromium with remote debugging
chromium --remote-debugging-port=9222 --remote-allow-origins=*

# Install & run
pip install -r requirements.txt   # aiohttp, websockets
python3 relay.py                   # starts on 127.0.0.1:18792

# Or use the launcher script
bash start.sh          # start (checks CDP availability first)
bash start.sh restart  # restart
bash start.sh stop     # stop
```

Token is auto-generated at startup, written to `/tmp/browser-relay-token`. All API calls (except `/health`) require `Authorization: Bearer <token>`.

## Syntax check (no tests exist)

```bash
python3 -c "import ast; ast.parse(open('relay.py').read())"
```

## Architecture

Everything lives in `relay.py` — a single aiohttp async server:

- **CDP layer** (`get_tabs`, `get_ws`, `cdp_send`): manages WebSocket connections to Chromium tabs, sends CDP commands and awaits responses by message ID
- **Auth middleware** (`auth_middleware`): Bearer token check on all routes except `/health`
- **Route handlers** (`handle_*`): thin wrappers that translate HTTP JSON requests into CDP calls — navigate, screenshot, click (by coords or CSS selector), type, evaluate JS, scroll, keypress, wait for element, tab management

The relay maintains a connection pool (`_ws_connections`) keyed by tab ID, with a shared `aiohttp.ClientSession` for both CDP HTTP and WebSocket calls.

## Key design decisions

- Localhost-only binding — never `0.0.0.0`
- Per-session random token (not persisted across restarts)
- `start.sh` handles PID tracking, venv activation, and CDP availability checks before launching
- `SKILL.md` is an AI-assistant skill definition (not user docs) — paths there should stay relative
