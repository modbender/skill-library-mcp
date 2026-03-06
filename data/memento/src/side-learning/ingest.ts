/**
 * Ingest pipeline for side-learning staging files.
 *
 * Reads JSON files from ~/.engram/staging/, validates them against the staging
 * schema, runs facts through Memento's existing dedup pipeline, and promotes
 * them to the main facts table.
 *
 * Processed files are moved to ~/.engram/staging/.processed/ for audit trail.
 *
 * Usage:
 *   npx tsx src/side-learning/ingest.ts [--dry-run] [--agent <id>]
 */

import { resolve, join, basename } from "node:path";
import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync } from "node:fs";
import { homedir } from "node:os";
import { ConversationDB } from "../storage/db.js";
import { processExtractedFacts, type DeduplicationResult } from "../extraction/deduplicator.js";
import type { ExtractedFact } from "../extraction/extractor.js";
import type { PluginLogger } from "../types.js";
import type { StagingFile, StagingFact } from "./staging-schema.js";
import {
  STAGING_DIR,
  PROCESSED_DIR,
  SIDE_LEARNING_DEFAULT_CONFIDENCE,
} from "./staging-schema.js";

// ---------------------------------------------------------------------------
// Logger
// ---------------------------------------------------------------------------

const logger: PluginLogger = {
  info: (msg: string) => console.log(`[ingest] ${msg}`),
  warn: (msg: string) => console.warn(`[ingest:WARN] ${msg}`),
  error: (msg: string) => console.error(`[ingest:ERROR] ${msg}`),
  debug: (msg: string) => {
    if (process.env.DEBUG) console.log(`[ingest:debug] ${msg}`);
  },
};

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

const VALID_CATEGORIES = new Set([
  "preference", "decision", "person", "tool", "pattern",
  "gotcha", "architecture", "convention",
  // Also accept Memento's standard categories
  "identity", "family", "work", "location", "health",
  "finance", "relationship", "hobby", "technical", "other",
]);

const VALID_VISIBILITIES = new Set(["shared", "private", "secret"]);

function validateStagingFile(data: unknown, filePath: string): StagingFile | null {
  if (!data || typeof data !== "object") {
    logger.warn(`Invalid staging file (not an object): ${filePath}`);
    return null;
  }

  const file = data as Record<string, unknown>;

  if (file.version !== 1) {
    logger.warn(`Unsupported schema version ${file.version} in ${filePath}`);
    return null;
  }

  if (!file.source || typeof file.source !== "object") {
    logger.warn(`Missing source metadata in ${filePath}`);
    return null;
  }

  if (!Array.isArray(file.facts) || file.facts.length === 0) {
    logger.warn(`No facts in ${filePath}`);
    return null;
  }

  const agentId = typeof file.agentId === "string" ? file.agentId : "main";

  // Validate and normalize each fact
  const validFacts: StagingFact[] = [];
  for (const fact of file.facts) {
    if (!fact.content || typeof fact.content !== "string") continue;
    if (fact.content.length < 10) continue; // Skip trivially short facts

    validFacts.push({
      content: fact.content,
      summary: typeof fact.summary === "string" ? fact.summary.slice(0, 100) : fact.content.slice(0, 100),
      category: VALID_CATEGORIES.has(fact.category) ? fact.category : "other",
      visibility: VALID_VISIBILITIES.has(fact.visibility) ? fact.visibility as StagingFact["visibility"] : "shared",
      confidence: typeof fact.confidence === "number"
        ? Math.max(0.1, Math.min(1.0, fact.confidence))
        : SIDE_LEARNING_DEFAULT_CONFIDENCE,
    });
  }

  if (validFacts.length === 0) {
    logger.warn(`No valid facts after validation in ${filePath}`);
    return null;
  }

  return {
    version: 1,
    source: file.source as StagingFile["source"],
    agentId,
    facts: validFacts,
  };
}

// ---------------------------------------------------------------------------
// DB path discovery (same logic as deep-consolidate)
// ---------------------------------------------------------------------------

function findAgentDB(agentId: string): string | null {
  const home = homedir();

  // Main agent
  if (agentId === "main") {
    const mainDb = join(home, ".engram", "conversations.sqlite");
    return existsSync(mainDb) ? mainDb : null;
  }

  // Check ~/.openclaw/workspace-<agentId>/
  const workspaceDb = join(home, ".openclaw", `workspace-${agentId}`, ".engram", "conversations.sqlite");
  if (existsSync(workspaceDb)) return workspaceDb;

  // Check ~/<agentId>/
  const homeDb = join(home, agentId, ".engram", "conversations.sqlite");
  if (existsSync(homeDb)) return homeDb;

  return null;
}

// ---------------------------------------------------------------------------
// Ingest
// ---------------------------------------------------------------------------

interface IngestResult {
  filesProcessed: number;
  factsIngested: number;
  factsDuplicate: number;
  factsUpdated: number;
  errors: string[];
}

async function ingestStagingFiles(options: {
  dryRun?: boolean;
  targetAgent?: string;
}): Promise<IngestResult> {
  const { dryRun = false, targetAgent } = options;
  const home = homedir();
  const stagingDir = resolve(home, STAGING_DIR);
  const processedDir = resolve(home, PROCESSED_DIR);

  const result: IngestResult = {
    filesProcessed: 0,
    factsIngested: 0,
    factsDuplicate: 0,
    factsUpdated: 0,
    errors: [],
  };

  if (!existsSync(stagingDir)) {
    logger.info(`No staging directory found at ${stagingDir} — nothing to ingest.`);
    return result;
  }

  // Ensure processed directory exists
  if (!dryRun) {
    mkdirSync(processedDir, { recursive: true });
  }

  // Find all JSON files in staging
  const files = readdirSync(stagingDir)
    .filter((f) => f.endsWith(".json"))
    .sort(); // Process oldest first

  if (files.length === 0) {
    logger.info("No staging files to process.");
    return result;
  }

  logger.info(`Found ${files.length} staging file(s) to process${dryRun ? " (DRY RUN)" : ""}.`);

  // Cache of open DBs per agent
  const dbCache = new Map<string, ConversationDB>();

  for (const fileName of files) {
    const filePath = join(stagingDir, fileName);

    try {
      const raw = readFileSync(filePath, "utf-8");
      const data = JSON.parse(raw);
      const staging = validateStagingFile(data, filePath);

      if (!staging) continue;

      // Filter by target agent if specified
      if (targetAgent && staging.agentId !== targetAgent) {
        logger.debug?.(`Skipping ${fileName} — agent ${staging.agentId} != ${targetAgent}`);
        continue;
      }

      // Find or open DB for this agent
      let db = dbCache.get(staging.agentId);
      if (!db) {
        const dbPath = findAgentDB(staging.agentId);
        if (!dbPath) {
          result.errors.push(`No DB found for agent ${staging.agentId} (${fileName})`);
          continue;
        }
        db = new ConversationDB(dbPath);
        dbCache.set(staging.agentId, db);
      }

      const source = staging.source;
      const projectLabel = source.project
        ? basename(source.project).toLowerCase().replace(/[^a-z0-9-]/g, "-")
        : "unknown";

      logger.info(
        `Processing ${fileName}: ${staging.facts.length} facts from ${source.type}/${projectLabel}` +
        `${source.gitBranch ? ` (${source.gitBranch})` : ""}`
      );

      if (dryRun) {
        for (const fact of staging.facts) {
          logger.info(`  [DRY] ${fact.category}: ${fact.summary}`);
        }
        result.factsIngested += staging.facts.length;
        result.filesProcessed++;
        continue;
      }

      // Convert staging facts to ExtractedFact format for the dedup pipeline.
      // Side-learning facts don't have duplicate_of/supersedes set — the dedup
      // pipeline will treat them as new facts (insert). If a fact with identical
      // content already exists, the DB unique constraint will catch it.
      const extractedFacts: ExtractedFact[] = staging.facts.map((f) => ({
        content: f.content,
        summary: f.summary,
        category: f.category,
        visibility: f.visibility,
        confidence: f.confidence,
        sentiment: "neutral",
      }));

      // Use a synthetic conversation ID for provenance tracking
      const syntheticConvId = `side-learning:${projectLabel}:${source.exportedAt ?? Date.now()}`;

      // Run through the dedup pipeline
      const deduped: DeduplicationResult = await processExtractedFacts(
        extractedFacts,
        syntheticConvId,
        staging.agentId,
        db,
        null, // embeddingEngine — not available in side-learning ingest
        logger,
      );

      result.factsIngested += deduped.factsExtracted;
      result.factsDuplicate += deduped.factsDeduplicated;
      result.factsUpdated += deduped.factsUpdated;
      result.filesProcessed++;

      logger.info(
        `  → ${deduped.factsExtracted} new, ${deduped.factsUpdated} updated, ${deduped.factsDeduplicated} duplicates`
      );

      // Move processed file
      renameSync(filePath, join(processedDir, fileName));
    } catch (err) {
      result.errors.push(`Error processing ${fileName}: ${String(err)}`);
      logger.error(`Failed to process ${fileName}: ${String(err)}`);
    }
  }

  // Close all DBs
  for (const [, db] of dbCache) {
    (db as any).close?.();
  }

  return result;
}

// ---------------------------------------------------------------------------
// CLI entry point
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const dryRun = args.includes("--dry-run");
  const agentIdx = args.indexOf("--agent");
  const targetAgent = agentIdx !== -1 ? args[agentIdx + 1] : undefined;

  const result = await ingestStagingFiles({ dryRun, targetAgent });

  // Summary output
  const parts: string[] = [];
  if (result.factsIngested > 0) parts.push(`${result.factsIngested} ingested`);
  if (result.factsUpdated > 0) parts.push(`${result.factsUpdated} updated`);
  if (result.factsDuplicate > 0) parts.push(`${result.factsDuplicate} duplicates`);
  if (result.errors.length > 0) parts.push(`${result.errors.length} errors`);

  if (result.filesProcessed === 0 && result.errors.length === 0) {
    console.log("📥 Side learning: nothing to ingest.");
  } else {
    console.log(
      `📥 Side learning: ${result.filesProcessed} file(s) processed — ${parts.join(", ")}.` +
      (dryRun ? " (DRY RUN)" : "")
    );
  }

  if (result.errors.length > 0) {
    for (const err of result.errors) {
      console.error(`  ${err}`);
    }
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(`Fatal: ${String(err)}`);
  process.exit(1);
});

export { ingestStagingFiles, type IngestResult };
