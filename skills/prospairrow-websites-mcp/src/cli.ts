import path from "node:path";
import { bootstrapLogin, listSites, runTask } from "./framework/service.js";

function getArg(flag: string): string | undefined {
  const idx = process.argv.indexOf(flag);
  if (idx >= 0 && idx + 1 < process.argv.length) return process.argv[idx + 1];
  return undefined;
}

function parseParams(): Record<string, unknown> {
  const params: Record<string, unknown> = {};
  const limit = getArg("--limit");
  if (limit !== undefined) {
    const n = Number(limit);
    if (!Number.isNaN(n)) params.limit = n;
  }
  return params;
}

async function main(): Promise<void> {
  const command = process.argv[2];
  const rootDir = path.resolve(process.cwd());

  if (command === "login") {
    const siteId = getArg("--site");
    if (!siteId) throw new Error("Missing --site");
    const result = await bootstrapLogin(rootDir, { siteId });
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  if (command === "run-task") {
    const siteId = getArg("--site");
    const taskId = getArg("--task");
    if (!siteId || !taskId) throw new Error("Missing --site or --task");
    const result = await runTask(rootDir, { siteId, taskId, params: parseParams() });
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  if (command === "list-sites") {
    const result = await listSites(rootDir);
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  throw new Error("Usage: tsx src/cli.ts <login|run-task|list-sites> [--site ...] [--task ...] [--limit ...]");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
