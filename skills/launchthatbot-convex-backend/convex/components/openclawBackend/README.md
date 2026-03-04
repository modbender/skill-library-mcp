# openclawBackend Component (Core)

This folder contains the **core Convex component** required for the `@launchthatbot/convex-backend` skill to work reliably.

- Convex component id: `convex_openclaw_backend_component`
- App mount alias: `openclawBackend`
- Convex component docs: https://docs.convex.dev/components/authoring#local-components

## What this component does

This component contains the minimum schema and logic that replaces stock OpenClaw local-file behavior for:

- long-term memory (`memory:*`)
- daily logs (`writeDailyLog`, `getDailyLog`, `listDailyLogs`)

These tables/functions are required integration primitives and are intentionally isolated from user custom app logic.

## Core vs Custom separation

- **Core (this component):** required tables/functions that the skill depends on.
- **Custom (root app):** user-specific tables/functions such as tasks, projects, domain-specific workflows.

When users ask for bespoke backend features, add those in root `convex/*` (or additional custom components if truly needed), not by editing or deleting this core component.

## Important guardrails

1. Do **not** delete this component.
2. Do **not** repurpose this component for user-specific domain logic.
3. Keep this component stable and backwards compatible.
4. After any Convex code changes (core or custom), run deploy from skill root:

```bash
cd /home/node/.openclaw/skills/convex-backend
CONVEX_DEPLOY_KEY=... npx -y convex@latest deploy
```

Without deploy, schema/function changes are not applied to the target Convex deployment.
