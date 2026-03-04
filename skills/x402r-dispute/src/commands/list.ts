/**
 * list command — List disputes via arbiter server or SDK
 */

import type { Command } from "commander";
import { getConfig } from "../config.js";

export function registerListCommand(program: Command): void {
  program
    .command("list")
    .description("List pending disputes")
    .option("-r, --receiver <address>", "Filter by receiver address")
    .option("--offset <n>", "Offset for pagination", "0")
    .option("--count <n>", "Number of results", "20")
    .action(async (options) => {
      const config = getConfig();
      const url = config.arbiterUrl;

      console.log(`\nQuerying disputes from ${url}...`);

      const params = new URLSearchParams();
      if (options.receiver) params.set("receiver", options.receiver);
      params.set("offset", options.offset);
      params.set("count", options.count);

      try {
        const response = await fetch(`${url}/api/disputes?${params.toString()}`);

        if (!response.ok) {
          const error = await response.text();
          console.error(`\nArbiter returned ${response.status}:`, error);
          process.exit(1);
        }

        const data = await response.json() as {
          keys: string[];
          total: string;
          offset: string;
          count: string;
        };

        console.log(`\n=== Disputes (${data.keys.length} of ${data.total}) ===`);

        if (data.keys.length === 0) {
          console.log("  No pending disputes found.");
          return;
        }

        for (let i = 0; i < data.keys.length; i++) {
          console.log(`  [${parseInt(data.offset) + i}] ${data.keys[i]}`);
        }

        console.log(`\n  Showing ${data.offset}-${parseInt(data.offset) + data.keys.length} of ${data.total}`);
      } catch (error) {
        console.error("\nFailed to list disputes:", error instanceof Error ? error.message : error);
        console.error("Is the arbiter server running at", url, "?");
        process.exit(1);
      }
    });
}
