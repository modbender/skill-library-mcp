#!/usr/bin/env node
/**
 * Mem0 configuration for Clawdbot integration
 * Uses Clawdbot's standard LLM and embedding providers
 */

import { Memory } from "mem0ai/oss";
import * as path from "path";
import * as os from "os";

const MEM0_DIR = path.join(os.homedir(), ".mem0");
const HISTORY_DB = path.join(MEM0_DIR, "history.db");

/**
 * Get Mem0 instance with Clawdbot-compatible config
 * @param {Object} options - Configuration options
 * @returns {Memory} Configured Memory instance
 */
export function getMem0Instance(options = {}) {
  const config = {
    version: "v1.1",
    embedder: {
      provider: "openai",
      config: {
        apiKey: process.env.OPENAI_API_KEY || "",
        model: "text-embedding-3-small"
      }
    },
    vectorStore: {
      provider: "memory",
      config: {
        collectionName: "clawdbot_memories",
        dimension: 1536
      }
    },
    llm: {
      provider: "openai",
      config: {
        apiKey: process.env.OPENAI_API_KEY || "",
        model: "gpt-4o-mini" // Fast, cost-effective for memory extraction
      }
    },
    historyDbPath: HISTORY_DB,
    ...options
  };

  return new Memory(config);
}

/**
 * User ID for Abhay
 */
export const USER_ID = "abhay";
