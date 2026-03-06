---
name: materials-workbench
description: Materials editor workbench — React UI and Express server to render JSON schemas to images and generate schemas with AI (declare-render + materials-agents).
version: 1.0.0
metadata:
  clawdbot:
    requires:
      env:
        - OPENAI_API_KEY
      bins:
        - node
    primaryEnv: OPENAI_API_KEY
---
# Materials Workbench

Use this skill when the user wants to run the materials editor workbench: a local web app with a React client and Express server that renders JSON schemas to images (declare-render) and can generate or edit schemas using AI (materials-agents).

## What it is

- **Client** — React + Vite app for editing and previewing render schemas.
- **Server** — Express API that renders schemas to PNG/JPG and uses materials-agents (OpenAI) for schema generation or refinement.

## When to use

- User wants to "run the workbench", "start the materials editor", or "open the schema editor UI".
- User needs a local dev environment for rendering schemas and AI-assisted schema creation.

## Run

From the workbench root:

```bash
pnpm install
pnpm run install:all   # install root, server, and client deps
pnpm run dev           # start server + client (concurrently)
```

- Client usually: http://localhost:5173
- Server usually: http://localhost:3000 (or port in server config)

Set `OPENAI_API_KEY` for AI/generate features.

## Project layout

- `client/` — React frontend (Vite).
- `server/` — Express backend (declare-render, materials-agents, canvas).

## Schema format

Same as materials-cli: declare-render format with `id`, `width`, `height`, `layers` (text, image, container, shape, etc.).
