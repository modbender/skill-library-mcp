// scripts/hello.ts
// Minimal TypeScript "hello world" demo for an OpenClaw skill.
// Shows how to depend on an npm module (dayjs) and export a simple function.

import dayjs from "dayjs";

/**
 * buildGreeting
 *
 * Returns a friendly greeting string, including a timestamp generated via dayjs.
 */
export function buildGreeting(name: string = "world"): string {
  const now = dayjs().format("YYYY-MM-DD HH:mm:ss");
  return `Hello, ${name}! (Time: ${now})`;
}

// If this file is invoked directly via `ts-node scripts/hello.ts`,
// print an example greeting so you can see it working.
if (require.main === module) {
  // eslint-disable-next-line no-console
  console.log(buildGreeting());
}
