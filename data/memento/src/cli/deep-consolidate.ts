#!/usr/bin/env npx tsx
/**
 * CLI script to run deep consolidation ("sleep pass") for all Memento agents.
 *
 * Usage:
 *   npx tsx src/cli/deep-consolidate.ts [--agent <id>]
 *
 * Without --agent, runs for all agents found in the DB.
 * Designed to be called from an OpenClaw cron job.
 */

import { resolve, join } from "node:path";
import { existsSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import {
  deepConsolidate,
  applyConfidenceDecay,
  DEFAULT_DEEP_CONFIG,
  type DeepConsolidationResult,
} from "../consolidation/deep-consolidator.js";
import { ConversationDB } from "../storage/db.js";
import type { PluginLogger } from "../types.js";

// ---------------------------------------------------------------------------
// Auto-discover agent databases
// ---------------------------------------------------------------------------

/**
 * Discovers Memento databases for all agents by scanning common OpenClaw
 * workspace locations. Falls back to MEMENTO_AGENT_PATHS env var if set.
 *
 * Env var format: MEMENTO_AGENT_PATHS="main:/path/to/db,drjones:/path/to/db"
 */
function discoverAgentDBs(): Record<string, string> {
  // Allow explicit override via environment variable
  const envPaths = process.env.MEMENTO_AGENT_PATHS;
  if (envPaths) {
    const result: Record<string, string> = {};
    for (const entry of envPaths.split(",")) {
      const [agentId, dbPath] = entry.split(":");
      if (agentId && dbPath) result[agentId.trim()] = resolve(dbPath.trim());
    }
    return result;
  }

  // Auto-discover from standard OpenClaw locations
  const home = homedir();
  const agents: Record<string, string> = {};

  // Main agent: ~/.engram/conversations.sqlite
  const mainDb = join(home, ".engram", "conversations.sqlite");
  if (existsSync(mainDb)) agents["main"] = mainDb;

  // Other agents: scan ~/.openclaw/workspace-*/  and ~/*/
  const openclawDir = join(home, ".openclaw");
  if (existsSync(openclawDir)) {
    try {
      for (const entry of readdirSync(openclawDir, { withFileTypes: true })) {
        if (entry.isDirectory() && entry.name.startsWith("workspace-")) {
          const agentId = entry.name.replace("workspace-", "");
          const dbPath = join(openclawDir, entry.name, ".engram", "conversations.sqlite");
          if (existsSync(dbPath)) agents[agentId] = dbPath;
        }
      }
    } catch { /* permission errors are OK */ }
  }

  // Also scan home directories for agent workspaces (e.g., ~/bob/.engram/)
  try {
    for (const entry of readdirSync(home, { withFileTypes: true })) {
      if (entry.isDirectory() && !entry.name.startsWith(".")) {
        const dbPath = join(home, entry.name, ".engram", "conversations.sqlite");
        if (existsSync(dbPath) && !agents[entry.name]) {
          agents[entry.name] = dbPath;
        }
      }
    }
  } catch { /* permission errors are OK */ }

  return agents;
}

const AGENT_DB_PATHS = discoverAgentDBs();

// ---------------------------------------------------------------------------
// Simple logger
// ---------------------------------------------------------------------------

const logger: PluginLogger = {
  info: (msg: string) => console.log(`[INFO] ${msg}`),
  warn: (msg: string) => console.warn(`[WARN] ${msg}`),
  error: (msg: string) => console.error(`[ERROR] ${msg}`),
  debug: (msg: string) => {
    if (process.env.DEBUG) console.log(`[DEBUG] ${msg}`);
  },
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main(): void {
  const args = process.argv.slice(2);
  const agentIdx = args.indexOf("--agent");
  const targetAgent = agentIdx !== -1 ? args[agentIdx + 1] : null;

  const agents = targetAgent
    ? { [targetAgent]: AGENT_DB_PATHS[targetAgent] }
    : AGENT_DB_PATHS;

  if (targetAgent && !AGENT_DB_PATHS[targetAgent]) {
    console.error(`Unknown agent: ${targetAgent}`);
    console.error(`Known agents: ${Object.keys(AGENT_DB_PATHS).join(", ")}`);
    process.exit(1);
  }

  const allResults: Record<string, DeepConsolidationResult> = {};
  let totalDecayed = 0;
  let totalCreated = 0;
  let totalUpdated = 0;
  let totalMerged = 0;
  let totalErrors = 0;

  for (const [agentId, dbPath] of Object.entries(agents)) {
    if (!existsSync(dbPath)) {
      logger.warn(`Skipping ${agentId} — DB not found at ${dbPath}`);
      continue;
    }

    logger.info(`Running deep consolidation for agent: ${agentId}`);

    try {
      const db = new ConversationDB(dbPath);

      // Step 1: Apply confidence decay
      const decayed = applyConfidenceDecay(
        db,
        agentId,
        DEFAULT_DEEP_CONFIG,
        logger,
      );
      totalDecayed += decayed;

      // Step 2: Run deep consolidation (cluster refresh, merging)
      const result = deepConsolidate(db, agentId, DEFAULT_DEEP_CONFIG, logger);
      allResults[agentId] = result;

      totalCreated += result.clustersCreated;
      totalUpdated += result.clustersUpdated;
      totalMerged += result.clustersMerged;
      totalErrors += result.errors.length;

      // Close DB
      (db as any).close?.();
    } catch (err) {
      logger.error(`Failed for ${agentId}: ${String(err)}`);
      totalErrors++;
    }
  }

  // Summary output (consumed by cron announce)
  const agentCount = Object.keys(allResults).length;
  const parts: string[] = [];

  if (totalDecayed > 0) parts.push(`${totalDecayed} facts decayed`);
  if (totalCreated > 0) parts.push(`${totalCreated} clusters created`);
  if (totalUpdated > 0) parts.push(`${totalUpdated} clusters updated`);
  if (totalMerged > 0) parts.push(`${totalMerged} clusters merged`);
  if (totalErrors > 0) parts.push(`${totalErrors} errors`);

  if (parts.length === 0) {
    console.log(
      `🧠 Deep consolidation complete — ${agentCount} agent(s), nothing to do.`,
    );
  } else {
    console.log(
      `🧠 Deep consolidation complete — ${agentCount} agent(s): ${parts.join(", ")}.`,
    );
  }

  if (totalErrors > 0) {
    for (const [agentId, result] of Object.entries(allResults)) {
      for (const err of result.errors) {
        console.error(`  [${agentId}] ${err}`);
      }
    }
  }
}

main();
