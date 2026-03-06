---
name: pulse-app
description: >
  Use this skill to help developers get started building Pulse Apps — full-stack React extensions
  for Pulse Editor that use Module Federation. Trigger when a user asks to:
  - Create or scaffold a new Pulse App
  - Understand Pulse App architecture (frontend, backend, skills)
  - Add server functions or skills to an existing Pulse App
  - Configure pulse.config.ts or understand app metadata
  - Use @pulse-editor/react-api hooks (useLoading, useActionEffect)
  - Develop, preview, or build a Pulse App
  DO NOT trigger for general React or TypeScript questions unrelated to Pulse Apps.
---

# Pulse App Developer Guide

## What Is a Pulse App?

A Pulse App is a **module-federated, full-stack React extension** that can run standalone or integrate into the Pulse Editor platform. Pulse Editor acts primarily as a hosting environment for these modular apps.

## Project Structure

```
my-pulse-app/
├── pulse.config.ts          # App metadata & Pulse Editor configuration
├── package.json
├── tsconfig.json
├── src/
│   ├── main.tsx             # Frontend entry point (React UI)
│   ├── tailwind.css
│   ├── server-function/     # Backend endpoints (file path = URL path)
│   │   └── echo.ts          # → POST /server-function/echo
│   └── skill/               # Agentic skills (AI-callable actions)
│       └── example-skill/
│           ├── SKILL.md     # Skill definition (Anthropic YAML frontmatter format)
│           └── action.ts    # Action handler (default export function)
```

## Quick Start

### 1. Create a new Pulse App
```bash
pulse create
```

### 2. Start development server
```bash
npm run dev
# Hosts at http://localhost:3030
# Register in Pulse Editor → Settings
```

### 3. Preview in browser (no editor integration)
```bash
npm run preview
# Note: Inter-Module-Communication features won't work in preview mode
```

### 4. Build
```bash
npm run build          # Full build (client + server)
npm run build-client   # Frontend only
npm run build-server   # Backend only
```

---

## Frontend: `src/main.tsx`

The single React entry point rendered by Pulse Editor as an extension UI. Uses Tailwind CSS for styling.

### Key hooks from `@pulse-editor/react-api`

```tsx
import { useLoading, useActionEffect } from "@pulse-editor/react-api";

// useLoading — manage loading states
const { isLoading, setLoading } = useLoading();

// useActionEffect — register a handler for an app action
useActionEffect("mySkillName", {
  beforeAction: (input) => {
    setLoading(true);
    return input; // optionally transform input
  },
  afterAction: (output) => {
    setLoading(false);
    console.log("Action completed:", output);
  },
});
```

### Calling a server function from the frontend
```tsx
const response = await fetch("/server-function/echo", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "hello" }),
});
const data = await response.json();
```

---

## Backend: `src/server-function/`

Files in this directory are automatically mapped to HTTP endpoints:

| File path | Endpoint |
|-----------|----------|
| `src/server-function/echo.ts` | `POST /server-function/echo` |
| `src/server-function/hello/hello-world.ts` | `POST /server-function/hello/hello-world` |

### Example server function
```ts
// src/server-function/echo.ts
import { Request, Response } from "express";

export default async function handler(req: Request, res: Response) {
  const { message } = req.body;
  res.json({ echo: message });
}
```

---

## Skills: `src/skill/`

Skills are **agentic capabilities** — actions callable by AI agents, frontend components via `useActionEffect`, or Pulse Editor's automation platform.

Each skill lives in its own subdirectory with two files:

### `SKILL.md` — Skill definition (Anthropic YAML frontmatter format)
```markdown
---
name: mySkill
description: Brief description of what this skill does
---

# My Skill

Longer description for the AI agent about when and how to use this skill.
```

### `action.ts` — Action handler
```ts
// src/skill/my-skill/action.ts

type Input = {
  /** The main text to process */
  text: string;
  /** Optional count parameter */
  count?: number;
};

type Output = {
  result: string;
  processedCount: number;
};

/**
 * Default export is the action handler.
 * Input/Output types + JSDoc comments are used for AI agent documentation.
 */
export default function mySkill({ text, count = 1 }: Input): Output {
  return {
    result: text.repeat(count),
    processedCount: count,
  };
}
```

### Create a new skill with the CLI
```bash
pulse skill create
```

---

## App Configuration: `pulse.config.ts`

```ts
import { AppConfig } from "@pulse-editor/shared-utils";
import pkg from "./package.json";

const config: AppConfig = {
  id: pkg.name,           // Must match package name — NO hyphens
  version: pkg.version,
  libVersion: pkg.dependencies["@pulse-editor/react-api"],
  displayName: pkg.displayName,
  description: pkg.description,
  visibility: "unlisted", // or "public"
  recommendedHeight: 640,
  recommendedWidth: 360,
  thumbnail: "./src/assets/thumbnail.png",
};

export default config;
```

> **Important:** The `id` field must not contain hyphens. Use underscores or camelCase instead.

---

## Key Concepts

### App Actions
App Actions are the **primary integration mechanism** in Pulse Apps. They:
- Are defined by a skill's `action.ts` default export
- Are callable by AI agents (via `SKILL.md` definition)
- Are callable from the frontend UI (via `useActionEffect`)
- Are callable from external services via a dedicated API endpoint

### `beforeAction` / `afterAction` Pipeline
These work like middleware around action execution:
- `beforeAction(input)` — runs before the action; return value becomes the action's input (use for UI state setup, input transformation)
- `afterAction(output)` — runs after the action completes (use for UI state teardown, handling results)

---

## Common Patterns

### Loading state around an action
```tsx
const { isLoading, setLoading } = useLoading();

useActionEffect("processData", {
  beforeAction: (input) => { setLoading(true); return input; },
  afterAction: (output) => {
    setLoading(false);
    setResult(output.result);
  },
});
```

### Server function with environment variables
```ts
// src/server-function/my-api.ts
import "dotenv/config";

export default async function handler(req, res) {
  const apiKey = process.env.MY_API_KEY;
  // ...
}
```

---

## Limitations

- Single entry point only — multi-page apps are not yet supported
- Inter-Module-Communication (IMC) features require running in Pulse Editor (`npm run dev`), not preview mode

---

## Resources

- Template repo: https://github.com/claypulse/pulse-app-template
- `@pulse-editor/react-api` — React hooks for Pulse Editor integration
- `@pulse-editor/shared-utils` — Shared types including `AppConfig`
- Pulse Editor CLI: `pulse create`, `pulse skill create`
