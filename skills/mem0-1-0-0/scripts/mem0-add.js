#!/usr/bin/env node
/**
 * Add memory to mem0
 * Usage: node mem0-add.js "memory text" [--user=abhay]
 * Or pass conversation: node mem0-add.js --messages='[{...}]' [--user=abhay]
 */

import { getMem0Instance, USER_ID } from "./mem0-config.js";

async function addMemory() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error("Usage: mem0-add.js <text> [--user=abhay]");
    console.error("   Or: mem0-add.js --messages='[{...}]' [--user=abhay]");
    process.exit(1);
  }

  let messages = null;
  let text = null;
  let userId = USER_ID;

  // Parse arguments
  for (const arg of args) {
    if (arg.startsWith("--messages=")) {
      try {
        messages = JSON.parse(arg.substring(11));
      } catch (e) {
        console.error("Error parsing messages JSON:", e.message);
        process.exit(1);
      }
    } else if (arg.startsWith("--user=")) {
      userId = arg.split("=")[1];
    } else if (!arg.startsWith("--")) {
      text = arg;
    }
  }

  if (!messages && !text) {
    console.error("Error: Must provide either text or --messages");
    process.exit(1);
  }

  try {
    const memory = getMem0Instance();
    
    let result;
    if (messages) {
      result = await memory.add(messages, { userId });
    } else {
      result = await memory.add(text, { userId });
    }

    console.log("✓ Memory added successfully");
    
    if (result && result.results) {
      console.log(`\nExtracted ${result.results.length} memories:`);
      result.results.forEach((mem, idx) => {
        console.log(`${idx + 1}. ${mem.memory || mem}`);
      });
    }

    // Return JSON for programmatic use
    if (process.env.JSON_OUTPUT) {
      console.log("\n---JSON---");
      console.log(JSON.stringify(result, null, 2));
    }

  } catch (error) {
    console.error("Error adding memory:", error.message);
    process.exit(1);
  }
}

addMemory();
