#!/usr/bin/env node
/**
 * Search mem0 memories
 * Usage: node mem0-search.js "query text" [--limit=3] [--user=abhay]
 */

import { getMem0Instance, USER_ID } from "./mem0-config.js";

async function searchMemories() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0].startsWith("--")) {
    console.error("Usage: mem0-search.js <query> [--limit=3] [--user=abhay]");
    process.exit(1);
  }

  const query = args[0];
  let limit = 3;
  let userId = USER_ID;

  // Parse optional flags
  for (const arg of args.slice(1)) {
    if (arg.startsWith("--limit=")) {
      limit = parseInt(arg.split("=")[1]);
    } else if (arg.startsWith("--user=")) {
      userId = arg.split("=")[1];
    }
  }

  try {
    const memory = getMem0Instance();
    const results = await memory.search(query, {
      userId,
      limit
    });

    if (results.results.length === 0) {
      console.log("No memories found.");
      process.exit(0);
    }

    console.log(`Found ${results.results.length} memories:\n`);
    results.results.forEach((entry, idx) => {
      console.log(`${idx + 1}. ${entry.memory}`);
      if (entry.metadata) {
        console.log(`   Created: ${entry.metadata.created_at || "unknown"}`);
      }
      console.log();
    });

    // Return JSON for programmatic use
    if (process.env.JSON_OUTPUT) {
      console.log("\n---JSON---");
      console.log(JSON.stringify(results, null, 2));
    }

  } catch (error) {
    console.error("Error searching memories:", error.message);
    process.exit(1);
  }
}

searchMemories();
