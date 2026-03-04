---
name: plan2meal
description: Manage recipes and grocery lists in Plan2Meal via chat (add recipe URLs, list/search/show/delete recipes, and create/manage grocery lists). Use when users explicitly want Plan2Meal recipe/grocery actions. Do not use for generic cooking advice, nutrition coaching, or non-Plan2Meal todo/shopping tools. Success = command executed with clear result text (IDs, counts, links/errors) and accurate data-routing disclosure.
requiredEnv:
  - CONVEX_URL
  - AUTH_GITHUB_ID
  - AUTH_GITHUB_SECRET
  - GITHUB_CALLBACK_URL
  - CLAWDBOT_URL
optionalEnv:
  - AUTH_GOOGLE_ID
  - AUTH_GOOGLE_SECRET
  - GOOGLE_CALLBACK_URL
  - AUTH_APPLE_ID
  - AUTH_APPLE_SECRET
  - APPLE_CALLBACK_URL
  - ALLOW_DEFAULT_BACKEND
primaryEnv: CONVEX_URL
---

# Plan2Meal Skill

A ClawdHub skill for managing recipes and grocery lists via Plan2Meal.

## Data routing + security disclosure (mandatory)

- Shared backend/API target: `https://gallant-bass-875.convex.cloud`
- Auth and recipe/grocery API traffic goes to configured `CONVEX_URL`.
- Shared backend usage is blocked unless `ALLOW_DEFAULT_BACKEND=true`.
- Never claim local-only processing when backend calls are involved.

## Use when / don't use when (routing guardrails)

Use when:
- User asks to add/list/search/show/delete Plan2Meal recipes.
- User asks to create/view/update Plan2Meal grocery lists.
- User asks to authenticate for Plan2Meal commands.

Do NOT use when:
- User asks for general meal ideas (no Plan2Meal action requested).
- User asks for health/nutrition analysis outside stored Plan2Meal data.
- User asks to manage Apple Reminders/Notes/other systems.

## Setup

1. Install:
   ```bash
   clawdhub install plan2meal
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```

3. Environment variables:
   - `CONVEX_URL` (**required**, recommended self-hosted backend)
   - `ALLOW_DEFAULT_BACKEND=true` (only if intentionally using shared backend)
   - OAuth provider creds:
     - GitHub (required): `AUTH_GITHUB_ID`, `AUTH_GITHUB_SECRET`, `GITHUB_CALLBACK_URL`
     - Google (optional): `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, `GOOGLE_CALLBACK_URL`
     - Apple (optional): `AUTH_APPLE_ID`, `AUTH_APPLE_SECRET`, `APPLE_CALLBACK_URL`
   - `CLAWDBOT_URL` (required, bot callback host)

## Commands

- `plan2meal login`
- `plan2meal logout`
- `plan2meal add <url>`
- `plan2meal list`
- `plan2meal search <term>`
- `plan2meal show <id>`
- `plan2meal delete <id>`
- `plan2meal lists`
- `plan2meal list-show <id>`
- `plan2meal list-create <name>`
- `plan2meal list-add <listId> <recipeId>`
- `plan2meal help`

## Output templates

Use response formatting templates from `references/output-templates.md`.

## Security checklist before replying

- If command failed due to auth/config, provide exact next step.
- If backend is relevant, keep disclosure truthful (shared default vs override).
- Never expose secrets/tokens in output.
