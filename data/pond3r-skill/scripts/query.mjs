#!/usr/bin/env node
/**
 * Execute a read-only SQL query against Pond3r datasets.
 * Usage: node query.mjs --dataset-id <id> --sql "SELECT * FROM stablecoin_yields LIMIT 10"
 *        node query.mjs --dataset <id> --sql "SELECT ..."
 *        node query.mjs --sql-file /path/to/query.sql
 * Env: POND3R_API_KEY (required)
 *
 * Rules: SELECT only, bare table names, results capped at 10,000 rows.
 */

import { callTool, normalizeToolResult } from "./client.mjs";
import { readFileSync } from "fs";

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--dataset-id" && argv[i + 1]) {
      args.datasetId = argv[++i];
    } else if (argv[i] === "--dataset" && argv[i + 1]) {
      // Backward-compatible alias for dataset_id.
      args.datasetId = argv[++i];
    } else if (argv[i] === "--sql" && argv[i + 1]) {
      args.sql = argv[++i];
    } else if (argv[i] === "--sql-file" && argv[i + 1]) {
      args.sqlFile = argv[++i];
    }
  }
  return args;
}

async function main() {
  const { datasetId, sql, sqlFile } = parseArgs(process.argv);

  let querySql = sql;
  if (sqlFile) {
    querySql = readFileSync(sqlFile, "utf8").trim();
  }

  if (!datasetId || !querySql) {
    console.error("Usage: node query.mjs --dataset-id <dataset_id> --sql \"SELECT ...\" | --sql-file <path>");
    process.exit(1);
  }

  const result = await callTool("query", { dataset_id: datasetId, sql: querySql });
  console.log(JSON.stringify(normalizeToolResult(result), null, 2));
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
