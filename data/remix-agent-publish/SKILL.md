---
name: remix-agent-publish
description: Build Remix games for remix.gg with the server-api v1 agents REST API and Farcade game SDK requirements.
metadata:
  tags: remix, games, api, agent, publishing
---

## When to use

Use this skill when users want to automate game publishing on Remix (`remix.gg`) from AI agents or external services.

## How to use

- Read [API Authentication](api/authentication.md) first.
- Fetch OpenAPI spec at `https://api.remix.gg/docs/json` before generating API calls.
- Use [API Reference](api/reference.md) for workflow guardrails (not as the method/path source of truth).
- For Phaser builds, use [Phaser 2D Arcade Companion Skill](frameworks/phaser-2d-arcade/SKILL.md).
- For lightweight 3D builds, use [Three.js Lite Companion Skill](frameworks/threejs-lite/SKILL.md).
- Use [Game SDK Reference](references/game-sdk.md) when generating or fixing game code.
- Apply [Submission Rules](rules/submission-requirements.md) for validation requirements.
- Follow [Game Creation Best Practices](rules/game-creation-best-practices.md) for mobile-first and SDK-safe implementation.
- Use [REST Snippets](snippets/rest-client.md) for client integration examples.
- Use [MCP Quickstart](mcp/quickstart.md) for assistant workflows.

## Source of truth

When docs and runtime behavior disagree, defer to the server API source and OpenAPI docs:

- `https://api.remix.gg/docs`
- `https://api.remix.gg/docs/json`
- `apps/server-api/routes/agents.ts`
- `apps/server-api/lib/api-auth.ts`
- `apps/server-api/lib/agent-api.ts`
- `apps/server-api/app/[...path]/route.ts`
- `packages/game-sdk/src/index.ts`
