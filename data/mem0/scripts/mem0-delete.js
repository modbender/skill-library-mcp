#!/usr/bin/env node
/**
 * Delete mem0 memories
 * Usage: node mem0-delete.js <memory_id>
 *    Or: node mem0-delete.js --all --user=abhay
 */

import { getMem0Instance, USER_ID } from "./mem0-config.js";

async function deleteMemories() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error("Usage: mem0-delete.js <memory_id>");
    console.error("   Or: mem0-delete.js --all --user=abhay");
    process.exit(1);
  }

  let memoryId = null;
  let deleteAll = false;
  let userId = USER_ID;

  // Parse arguments
  for (const arg of args) {
    if (arg === "--all") {
      deleteAll = true;
    } else if (arg.startsWith("--user=")) {
      userId = arg.split("=")[1];
    } else if (!arg.startsWith("--")) {
      memoryId = arg;
    }
  }

  try {
    const memory = getMem0Instance();
    
    if (deleteAll) {
      await memory.deleteAll({ userId });
      console.log(`✓ All memories deleted for user: ${userId}`);
    } else if (memoryId) {
      await memory.delete(memoryId);
      console.log(`✓ Memory deleted: ${memoryId}`);
    } else {
      console.error("Error: Must provide memory_id or --all flag");
      process.exit(1);
    }

  } catch (error) {
    console.error("Error deleting memory:", error.message);
    process.exit(1);
  }
}

deleteMemories();
