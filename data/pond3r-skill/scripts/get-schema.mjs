#!/usr/bin/env node
/**
 * Get schema for a Pond3r dataset.
 * Usage: node get-schema.mjs --dataset-id <id>
 *        node get-schema.mjs --dataset <id>   # alias
 * Env: POND3R_API_KEY (required)
 */

import { callTool, normalizeToolResult } from "./client.mjs";

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--dataset-id" && argv[i + 1]) {
      args.datasetId = argv[++i];
    } else if (argv[i] === "--dataset" && argv[i + 1]) {
      // Backward-compatible alias for dataset_id.
      args.datasetId = argv[++i];
    }
  }
  return args;
}

async function main() {
  const { datasetId } = parseArgs(process.argv);
  if (!datasetId) {
    console.error("Usage: node get-schema.mjs --dataset-id <dataset_id>");
    process.exit(1);
  }

  const result = await callTool("get_schema", { dataset_id: datasetId });
  console.log(JSON.stringify(normalizeToolResult(result), null, 2));
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
