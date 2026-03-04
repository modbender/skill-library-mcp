# ts-hello-world-demo Skill – Usage

This skill is a **hello world** example showing how to:

- Include TypeScript source in `scripts/`
- Use a Node dependency (`dayjs`)
- Document installation via `package.json`

## Installation

From the skill directory:

```bash
cd /home/ubuntu/skill-demo
npm install
```

This installs:
- `dayjs` (runtime dependency)
- `ts-node` and `typescript` (dev dependencies for running TS directly)

## Running the demo

After `npm install`:

```bash
npm start
# or
npx ts-node scripts/hello.ts
```

You should see output like:

```text
Hello, world! (Time: 2026-03-02 09:15:30)
```

## Programmatic usage

In other TS/JS code (inside this skill, or elsewhere if you copy the file):

```ts
import { buildGreeting } from "./scripts/hello";

console.log(buildGreeting("Alice"));
// -> "Hello, Alice! (Time: 2026-03-02 09:15:30)"
```

## Next steps

To turn this into a more complex skill:

- Add more functions to `scripts/hello.ts` or new files in `scripts/`
- Update `SKILL.md` to describe new capabilities
- Add more dependencies in `package.json` as needed
- Package the skill into a `.skill` file and publish it to Clawdhub
