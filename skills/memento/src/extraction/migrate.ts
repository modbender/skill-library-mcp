#!/usr/bin/env node
/**
 * Memento Migration Script
 *
 * Bootstraps the Memento knowledge base from existing agent memory files.
 * Uses the same extraction pipeline as live capture (extractor + deduplicator).
 * Tracks processed files in extraction_log so re-runs are safe (incremental).
 *
 * Usage:
 *   npx tsx src/extraction/migrate.ts --all
 *   npx tsx src/extraction/migrate.ts --agent main --dry-run
 *   npx tsx src/extraction/migrate.ts --agent drjones --force
 *   npx tsx src/extraction/migrate.ts --all --model anthropic/claude-haiku-4-5-20251001
 *   npx tsx src/extraction/migrate.ts --agent main --db /custom/path/conversations.sqlite
 */

import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, resolve, basename } from "node:path";
import { homedir } from "node:os";
import { createHash, randomUUID } from "node:crypto";

import { ConversationDB } from "../storage/db.js";
import { extractFacts } from "./extractor.js";
import { processExtractedFacts } from "./deduplicator.js";
import type { ConversationRow } from "../storage/schema.js";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Files to always skip — system/operational, not knowledge */
const SYSTEM_FILES = new Set([
  "SOUL.md",
  "AGENTS.md",
  "USER.md",
  "IDENTITY.md",
  "HEARTBEAT.md",
  "TOOLS.md",
  "BOOTSTRAP.md",
]);

const FILE_CHUNK_THRESHOLD_BYTES = 50 * 1024; // 50 KB: split files larger than this
const CHUNK_SIZE_BYTES = 30 * 1024;            // 30 KB per chunk
const EXTRACTION_DELAY_MS = 2_000;             // 2 s between API calls
const DEFAULT_MODEL = "anthropic/claude-sonnet-4-6";
const DEFAULT_DB_PATH = join(homedir(), ".engram", "conversations.sqlite");
const EXISTING_FACTS_LIMIT = 50;

// ---------------------------------------------------------------------------
// Agent inventory
// ---------------------------------------------------------------------------

interface AgentConfig {
  agentId: string;
  workspace: string;
  /** Glob patterns relative to workspace */
  paths: string[];
}

/**
 * Load agent configs from ~/.engram/migration-config.json if it exists,
 * otherwise fall back to env vars, otherwise return an empty list and ask
 * the user to configure.
 *
 * Config file format:
 * {
 *   "agents": [
 *     { "agentId": "main", "workspace": "/path/to/workspace", "paths": ["MEMORY.md", "memory/*.md"] },
 *     ...
 *   ]
 * }
 */
function loadAgentConfigs(): AgentConfig[] {
  const home = homedir();

  // 1. External config file (preferred — nothing leaks into source)
  const configPath = join(home, ".engram", "migration-config.json");
  if (existsSync(configPath)) {
    try {
      const raw = JSON.parse(readFileSync(configPath, "utf8"));
      if (Array.isArray(raw.agents) && raw.agents.length > 0) {
        return raw.agents as AgentConfig[];
      }
    } catch (err) {
      console.warn(`[migrate] Could not parse ${configPath}: ${String(err)}`);
    }
  }

  // 2. Environment variables for common agents
  const fromEnv: AgentConfig[] = [];
  const envMappings: Array<{ envVar: string; agentId: string; defaultPaths: string[] }> = [
    { envVar: "MEMENTO_WORKSPACE_MAIN",   agentId: "main",    defaultPaths: ["MEMORY.md", "memory/*.md"] },
    { envVar: "MEMENTO_WORKSPACE_DRJONES",agentId: "drjones", defaultPaths: ["MEMORY.md", "memory/*.md", "prescriptions/*.md", "medical_records/*.md"] },
  ];
  for (const { envVar, agentId, defaultPaths } of envMappings) {
    const ws = process.env[envVar];
    if (ws) {
      fromEnv.push({ agentId, workspace: ws, paths: defaultPaths });
    }
  }
  if (fromEnv.length > 0) return fromEnv;

  // 3. No config found — return empty list; parseArgs() will surface a helpful error
  return [];
}

let _defaultAgentsCache: AgentConfig[] | null = null;

function getDefaultAgents(): AgentConfig[] {
  if (_defaultAgentsCache !== null) return _defaultAgentsCache;
  _defaultAgentsCache = loadAgentConfigs();
  return _defaultAgentsCache;
}

// ---------------------------------------------------------------------------
// CLI parsing
// ---------------------------------------------------------------------------

interface CliOptions {
  agents: AgentConfig[];
  dryRun: boolean;
  force: boolean;
  model: string;
  dbPath: string;
}

function parseArgs(): CliOptions {
  const args = process.argv.slice(2);
  let agentFilter: string | null = null;
  let all = false;
  let dryRun = false;
  let force = false;
  let model = DEFAULT_MODEL;
  let dbPath = DEFAULT_DB_PATH;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--all") {
      all = true;
    } else if (arg === "--dry-run") {
      dryRun = true;
    } else if (arg === "--force") {
      force = true;
    } else if (arg === "--agent" && args[i + 1]) {
      agentFilter = args[++i];
    } else if (arg === "--model" && args[i + 1]) {
      model = args[++i];
    } else if (arg === "--db" && args[i + 1]) {
      dbPath = resolve(args[++i]);
    }
  }

  const defaultAgents = getDefaultAgents();

  if (defaultAgents.length === 0) {
    console.error(
      "\nNo agent configuration found. Please create ~/.engram/migration-config.json:\n" +
      JSON.stringify({
        agents: [
          { agentId: "main", workspace: join(homedir(), "your-workspace"), paths: ["MEMORY.md", "memory/*.md"] },
        ],
      }, null, 2) +
      "\n\nOr set MEMENTO_WORKSPACE_MAIN environment variable to your workspace path.\n",
    );
    process.exit(1);
  }

  if (!all && !agentFilter) {
    console.error(
      "Usage: migrate.ts --all | --agent <id> [--dry-run] [--force] [--model <model>] [--db <path>]\n" +
        `Valid agents: ${defaultAgents.map((a) => a.agentId).join(", ")}`,
    );
    process.exit(1);
  }

  let agents: AgentConfig[];
  if (all) {
    agents = defaultAgents;
  } else {
    const found = defaultAgents.find((a) => a.agentId === agentFilter);
    if (!found) {
      console.error(
        `Unknown agent: ${agentFilter}. Valid agents: ${defaultAgents.map((a) => a.agentId).join(", ")}`,
      );
      process.exit(1);
    }
    agents = [found];
  }

  return { agents, dryRun, force, model, dbPath };
}

// ---------------------------------------------------------------------------
// Simple glob expander (no deps — handles "dir/*.md" and "file.md")
// ---------------------------------------------------------------------------

function expandGlob(baseDir: string, pattern: string): string[] {
  const slashIdx = pattern.lastIndexOf("/");
  const dir = slashIdx === -1 ? baseDir : join(baseDir, pattern.slice(0, slashIdx));
  const filePattern = slashIdx === -1 ? pattern : pattern.slice(slashIdx + 1);

  if (!existsSync(dir)) return [];

  if (!filePattern.includes("*")) {
    // Literal filename
    const full = join(dir, filePattern);
    return existsSync(full) && statSync(full).isFile() ? [full] : [];
  }

  // Wildcard — convert glob to regex and match against dir entries
  const reStr = "^" + filePattern.replace(/\./g, "\\.").replace(/\*/g, ".*") + "$";
  const re = new RegExp(reStr);
  try {
    return readdirSync(dir)
      .filter((name) => re.test(name))
      .map((name) => join(dir, name))
      .filter((full) => statSync(full).isFile());
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Deterministic conversation ID from file path (UUID-shaped hex slice)
// ---------------------------------------------------------------------------

function makeConversationId(agentId: string, filePath: string, chunkIndex?: number): string {
  const key =
    chunkIndex !== undefined
      ? `migration:${agentId}:${filePath}:chunk:${chunkIndex}`
      : `migration:${agentId}:${filePath}`;
  const hex = createHash("sha256").update(key).digest("hex");
  // Format as UUID to satisfy any UUID validators downstream
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20, 32)}`;
}

// ---------------------------------------------------------------------------
// Text chunker — splits at newline boundaries
// ---------------------------------------------------------------------------

function chunkText(text: string, maxBytes: number): string[] {
  if (Buffer.byteLength(text, "utf8") <= maxBytes) return [text];

  const chunks: string[] = [];
  const lines = text.split("\n");
  let current = "";

  for (const line of lines) {
    const next = current ? current + "\n" + line : line;
    if (Buffer.byteLength(next, "utf8") > maxBytes && current) {
      chunks.push(current);
      current = line;
    } else {
      current = next;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

// ---------------------------------------------------------------------------
// Logger (stdout only)
// ---------------------------------------------------------------------------

const logger = {
  info: (...args: any[]) => console.log("[migrate]", ...args),
  warn: (...args: any[]) => console.warn("[migrate:WARN]", ...args),
  error: (...args: any[]) => console.error("[migrate:ERROR]", ...args),
  // Suppress debug noise from extractor/deduplicator
  debug: (_msg: string) => {},
};

function log(...args: any[]) {
  console.log("[migrate]", ...args);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

function isFileAlreadyExtracted(db: ConversationDB, agentId: string, filePath: string): boolean {
  // For small files, the ID has no chunk index. For chunked files, check chunk 0.
  // We check both to cover all cases regardless of which scheme was used last run.
  return (
    db.isExtracted(makeConversationId(agentId, filePath)) ||
    db.isExtracted(makeConversationId(agentId, filePath, 0))
  );
}

// ---------------------------------------------------------------------------
// Per-file processing
// ---------------------------------------------------------------------------

type FileResult = {
  skipped: boolean;
  reason?: string;
  chunksProcessed: number;
  factsExtracted: number;
  factsUpdated: number;
  factsDeduplicated: number;
  error?: string;
};

async function processFile(
  db: ConversationDB,
  agentId: string,
  filePath: string,
  model: string,
  dryRun: boolean,
  force: boolean,
): Promise<FileResult> {
  const name = basename(filePath);

  // Skip system files
  if (SYSTEM_FILES.has(name)) {
    log(`Skip [system file]: ${name}`);
    return { skipped: true, reason: "system file", chunksProcessed: 0, factsExtracted: 0, factsUpdated: 0, factsDeduplicated: 0 };
  }

  // Skip already-processed (unless --force)
  if (!force && isFileAlreadyExtracted(db, agentId, filePath)) {
    log(`Skip [already done]: ${name}`);
    return { skipped: true, reason: "already processed", chunksProcessed: 0, factsExtracted: 0, factsUpdated: 0, factsDeduplicated: 0 };
  }

  // Read file content
  let content: string;
  try {
    content = readFileSync(filePath, "utf8");
  } catch (err) {
    logger.warn(`Cannot read ${filePath}: ${String(err)}`);
    return { skipped: false, chunksProcessed: 0, factsExtracted: 0, factsUpdated: 0, factsDeduplicated: 0, error: String(err) };
  }

  if (!content.trim()) {
    log(`Skip [empty]: ${name}`);
    return { skipped: true, reason: "empty file", chunksProcessed: 0, factsExtracted: 0, factsUpdated: 0, factsDeduplicated: 0 };
  }

  const fileSizeKb = Math.round(Buffer.byteLength(content, "utf8") / 1024);
  const chunks = chunkText(content, CHUNK_SIZE_BYTES);
  const isLarge = Buffer.byteLength(content, "utf8") > FILE_CHUNK_THRESHOLD_BYTES;

  if (dryRun) {
    log(
      `[DRY RUN] Would process: ${name}` +
        (isLarge ? ` (${fileSizeKb}KB → ${chunks.length} chunks)` : ` (${fileSizeKb}KB)`),
    );
    return { skipped: false, chunksProcessed: chunks.length, factsExtracted: 0, factsUpdated: 0, factsDeduplicated: 0 };
  }

  log(`Processing: ${name} (${fileSizeKb}KB${chunks.length > 1 ? `, ${chunks.length} chunks` : ""})`);

  let totalExtracted = 0;
  let totalUpdated = 0;
  let totalDeduped = 0;
  let lastError: string | undefined;

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    const conversationId = chunks.length > 1
      ? makeConversationId(agentId, filePath, i)
      : makeConversationId(agentId, filePath);
    const chunkLabel = chunks.length > 1 ? ` [chunk ${i + 1}/${chunks.length}]` : "";

    const now = Date.now();
    const conversation: ConversationRow = {
      id: conversationId,
      agent_id: agentId,
      session_key: `migration:${agentId}:${filePath}`,
      channel: "migration",
      started_at: now,
      ended_at: now,
      // Large value so ExtractionTrigger's minTurns check is irrelevant if called
      turn_count: 999,
      raw_text: chunks.length > 1
        ? `[MEMORY FILE: ${name}${chunkLabel}]\n\n${chunk}`
        : `[MEMORY FILE: ${name}]\n\n${chunk}`,
      metadata: JSON.stringify({
        source: "migration",
        filePath,
        chunkIndex: i,
        totalChunks: chunks.length,
      }),
    };

    // Insert conversation row (idempotent — OR IGNORE)
    try {
      db.insertConversationWithMessages(conversation, []);
    } catch (err) {
      logger.warn(`DB insert failed for ${name}${chunkLabel}: ${String(err)}`);
    }

    // Fetch existing facts for dedup context
    const existingFacts = db.getRelevantFacts(agentId, EXISTING_FACTS_LIMIT);

    // Call extraction LLM
    log(`  Extracting${chunkLabel}...`);
    const extractionResult = await extractFacts(conversation, existingFacts, model, logger);

    if (extractionResult.error) {
      logger.warn(`  Extraction error${chunkLabel}: ${extractionResult.error}`);
      db.logExtraction(conversationId, {
        modelUsed: extractionResult.modelUsed,
        factsExtracted: 0,
        factsUpdated: 0,
        factsDeduplicated: 0,
        error: extractionResult.error,
      });
      lastError = extractionResult.error;
    } else if (extractionResult.facts.length === 0) {
      log(`  No facts extracted${chunkLabel}`);
      db.logExtraction(conversationId, {
        modelUsed: extractionResult.modelUsed,
        factsExtracted: 0,
        factsUpdated: 0,
        factsDeduplicated: 0,
        error: null,
      });
    } else {
      const dedup = await processExtractedFacts(
        extractionResult.facts,
        conversationId,
        agentId,
        db,
        null, // embeddingEngine — not available in batch migration
        logger,
      );
      totalExtracted += dedup.factsExtracted;
      totalUpdated += dedup.factsUpdated;
      totalDeduped += dedup.factsDeduplicated;

      db.logExtraction(conversationId, {
        modelUsed: extractionResult.modelUsed,
        factsExtracted: dedup.factsExtracted,
        factsUpdated: dedup.factsUpdated,
        factsDeduplicated: dedup.factsDeduplicated,
        error: null,
      });

      log(
        `  Done${chunkLabel}: ${dedup.factsExtracted} new, ` +
          `${dedup.factsUpdated} updated, ${dedup.factsDeduplicated} dupes`,
      );
    }

    // Delay between chunks to respect API rate limits
    if (i < chunks.length - 1) {
      await sleep(EXTRACTION_DELAY_MS);
    }
  }

  return {
    skipped: false,
    chunksProcessed: chunks.length,
    factsExtracted: totalExtracted,
    factsUpdated: totalUpdated,
    factsDeduplicated: totalDeduped,
    error: lastError,
  };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

export async function runMigration(): Promise<void> {
  const opts = parseArgs();

  // Credentials are resolved by the extractor from environment variables:
  //   ANTHROPIC_API_KEY | OPENAI_API_KEY | MISTRAL_API_KEY | MEMENTO_API_KEY
  // Set the appropriate variable before running this script.

  console.log("=".repeat(60));
  console.log("Memento Migration");
  console.log(`DB:     ${opts.dbPath}`);
  console.log(`Model:  ${opts.model}`);
  console.log(`Agents: ${opts.agents.map((a) => a.agentId).join(", ")}`);
  if (opts.dryRun) console.log("Mode:   DRY RUN (no writes)");
  if (opts.force) console.log("Force:  yes (reprocess already-done files)");
  console.log("=".repeat(60));

  const db = new ConversationDB(opts.dbPath);

  type AgentStats = {
    total: number;
    skipped: number;
    processed: number;
    factsExtracted: number;
    factsUpdated: number;
    factsDeduplicated: number;
    errors: number;
  };

  const summary: Record<string, AgentStats> = {};

  for (const agent of opts.agents) {
    console.log(`\n${"─".repeat(60)}`);
    console.log(`Agent: ${agent.agentId}  (${agent.workspace})`);
    console.log("─".repeat(60));

    if (!existsSync(agent.workspace)) {
      console.warn(`  Workspace not found — skipping: ${agent.workspace}`);
      continue;
    }

    // Expand all glob patterns, deduplicate
    const fileSet = new Set<string>();
    for (const pattern of agent.paths) {
      for (const f of expandGlob(agent.workspace, pattern)) {
        fileSet.add(f);
      }
    }
    const files = [...fileSet].sort();

    log(`${files.length} file(s) found`);

    const stats: AgentStats = {
      total: files.length,
      skipped: 0,
      processed: 0,
      factsExtracted: 0,
      factsUpdated: 0,
      factsDeduplicated: 0,
      errors: 0,
    };

    for (let i = 0; i < files.length; i++) {
      const filePath = files[i];
      const result = await processFile(
        db,
        agent.agentId,
        filePath,
        opts.model,
        opts.dryRun,
        opts.force,
      );

      if (result.skipped) {
        stats.skipped++;
      } else {
        stats.processed++;
        stats.factsExtracted += result.factsExtracted;
        stats.factsUpdated += result.factsUpdated;
        stats.factsDeduplicated += result.factsDeduplicated;
        if (result.error) stats.errors++;

        // Delay between files (not after the last one)
        if (i < files.length - 1) {
          await sleep(EXTRACTION_DELAY_MS);
        }
      }
    }

    summary[agent.agentId] = stats;

    console.log(`\n  Summary for ${agent.agentId}:`);
    console.log(`    Files found:     ${stats.total}`);
    console.log(`    Skipped:         ${stats.skipped}`);
    console.log(`    Processed:       ${stats.processed}`);
    if (!opts.dryRun) {
      console.log(`    Facts new:       ${stats.factsExtracted}`);
      console.log(`    Facts updated:   ${stats.factsUpdated}`);
      console.log(`    Facts deduped:   ${stats.factsDeduplicated}`);
      if (stats.errors > 0) {
        console.log(`    Errors:          ${stats.errors}`);
      }
    }
  }

  // Overall totals
  console.log(`\n${"=".repeat(60)}`);
  console.log("Migration complete!");
  if (opts.dryRun) {
    console.log("(DRY RUN — no changes written to DB)");
  } else {
    let totalNew = 0;
    let totalUp = 0;
    let totalDe = 0;
    for (const s of Object.values(summary)) {
      totalNew += s.factsExtracted;
      totalUp += s.factsUpdated;
      totalDe += s.factsDeduplicated;
    }
    console.log(`Total facts new:     ${totalNew}`);
    console.log(`Total facts updated: ${totalUp}`);
    console.log(`Total facts deduped: ${totalDe}`);
  }
  console.log("=".repeat(60));

  db.close();
}

// Run when invoked directly (npx tsx src/extraction/migrate.ts ...)
runMigration().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
