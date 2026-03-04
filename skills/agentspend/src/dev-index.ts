#!/usr/bin/env node
import { runCli } from "./cli.js";

const LOCAL_API_BASE_URL = "http://127.0.0.1:8787";

runCli({
  baseUrl: LOCAL_API_BASE_URL,
  programName: "agentspend-dev",
}).catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
