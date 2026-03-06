#!/usr/bin/env node
/**
 * List all Pond3r datasets and tables.
 * Usage: node list-datasets.mjs
 * Env: POND3R_API_KEY (required)
 */

import { callTool, normalizeToolResult } from "./client.mjs";

async function main() {
  const result = await callTool("list_datasets", {});
  console.log(JSON.stringify(normalizeToolResult(result), null, 2));
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
