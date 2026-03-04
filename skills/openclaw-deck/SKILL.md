---
name: openclaw-deck
description: Multi-column chat deck UI for OpenClaw agents. Launch a local web interface to manage and chat with multiple agents side-by-side.
user-invocable: true
metadata: {"openclaw":{"emoji":"🦞","requires":{"bins":["node","npm"]},"os":["darwin","linux","win32"]}}
---

# OpenClaw Deck

Launch the OpenClaw Deck — a multi-column web UI for chatting with OpenClaw agents side-by-side.

## What this skill does

When invoked, install dependencies (if needed) and start the Vite dev server for the deck UI. The deck connects to the local OpenClaw Gateway via WebSocket proxy.

## Instructions

1. Check if `node_modules` exists in the skill's base directory. If not, run `npm install` in `{baseDir}`.
2. Start the dev server by running `npm run dev` in `{baseDir}`.
3. Tell the user the deck is available at **http://localhost:5173**.
4. Mention available keyboard shortcuts:
   - **Tab** / **Shift+Tab** — move focus between agent column inputs
   - **Cmd+1–9** — jump to a specific column by number
   - **Cmd+K** — open the Add Agent modal

## Requirements

- The OpenClaw Gateway must be running on `ws://127.0.0.1:18789` (default), or the user must set `VITE_GATEWAY_URL` in `.env`.
- Node.js and npm must be installed.
