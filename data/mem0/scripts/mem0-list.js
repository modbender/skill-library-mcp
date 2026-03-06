#!/usr/bin/env node
/**
 * List all mem0 memories for a user
 * Usage: node mem0-list.js [--user=abhay]
 */

import { getMem0Instance, USER_ID } from "./mem0-config.js";

async function listMemories() {
  const args = process.argv.slice(2);
  let userId = USER_ID;

  // Parse optional flags
  for (const arg of args) {
    if (arg.startsWith("--user=")) {
      userId = arg.split("=")[1];
    }
  }

  try {
    const memory = getMem0Instance();
    const response = await memory.getAll({ userId });
    const results = response.results || response || [];

    if (!results || results.length === 0) {
      console.log("No memories found.");
      process.exit(0);
    }

    console.log(`Found ${results.length} memories for ${userId}:\n`);
    results.forEach((entry, idx) => {
      console.log(`${idx + 1}. ${entry.memory || entry.text || JSON.stringify(entry)}`);
      if (entry.id) {
        console.log(`   ID: ${entry.id}`);
      }
      if (entry.created_at) {
        console.log(`   Created: ${entry.created_at}`);
      }
      console.log();
    });

    // Return JSON for programmatic use
    if (process.env.JSON_OUTPUT) {
      console.log("\n---JSON---");
      console.log(JSON.stringify(results, null, 2));
    }

  } catch (error) {
    console.error("Error listing memories:", error.message);
    process.exit(1);
  }
}

listMemories();
