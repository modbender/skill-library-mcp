---
name: ts-hello-world-demo
description: Minimal TypeScript hello-world skill that demonstrates bundling TS code, a Node dependency, and package.json instructions for use and publication on Clawdhub.
---

# TypeScript Hello World Demo Skill

This is a **hello world** skill that shows how to:

- Bundle TypeScript code in `scripts/`
- Use an npm dependency from that code
- Document `package.json` so others know how to install and run it

## What this skill does

Use this skill when you want a minimal example of:

- A TypeScript function that returns a formatted greeting string
- Using a third-party dependency (here: `dayjs` for timestamps)
- A `package.json` that documents how to install and run the code

## Layout

```text
skill-demo/
  SKILL.md
  package.json
  scripts/
    hello.ts
  references/
    README-usage.md
  assets/
    (optional files used by your skill)
```

## How another agent / developer uses this skill

1. Install dependencies in the skill folder:
   ```bash
   cd /home/ubuntu/skill-demo
   npm install
   ```

2. Run the demo script (via ts-node):
   ```bash
   npx ts-node scripts/hello.ts
   ```

3. In other TypeScript/JavaScript code, import and use the function:
   ```ts
   import { buildGreeting } from "./scripts/hello";

   console.log(buildGreeting("Alice"));
   ```

See `references/README-usage.md` for more details and extension ideas.
