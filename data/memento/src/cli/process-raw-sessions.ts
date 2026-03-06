#!/usr/bin/env node
/**
 * CLI to process raw Claude session JSONL files from ~/.engram/raw-sessions/.
 * Extracts facts via LLM and saves them to the Memento DB.
 *
 * Usage:
 *   node dist/cli/process-raw-sessions.js [--dry-run] [--limit N] [--agent <id>]
 *
 * Options:
 *   --dry-run     Parse and show what would be extracted, don't save or move files.
 *   --limit N     Process only N files (useful for testing).
 *   --agent <id>  Which agent_id to attribute facts to (default: "main").
 */

import {
  readdirSync,
  readFileSync,
  mkdirSync,
  renameSync,
  existsSync,
} from "node:fs";
import { join, basename } from "node:path";
import { homedir } from "node:os";
import { randomUUID } from "node:crypto";
import { createRequire } from "node:module";
import { ConversationDB } from "../storage/db.js";
import { extractFacts } from "../extraction/extractor.js";
import { processExtractedFacts } from "../extraction/deduplicator.js";
import type { PluginLogger } from "../types.js";
import type { ConversationRow } from "../storage/schema.js";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const RAW_SESSIONS_DIR = join(homedir(), ".engram", "raw-sessions");
const PROCESSED_DIR = join(RAW_SESSIONS_DIR, ".processed");
const DB_PATH = join(homedir(), ".engram", "conversations.sqlite");
const DEFAULT_MODEL = "anthropic/claude-sonnet-4-6";

// ---------------------------------------------------------------------------
// Load better-sqlite3 for reading schema_meta (model config)
// ---------------------------------------------------------------------------

import type BetterSQLite3 from "better-sqlite3";
type Database = BetterSQLite3.Database;
type DatabaseConstructor = typeof BetterSQLite3;

const _require = createRequire(import.meta.url);
const DatabaseCtor = _require("better-sqlite3") as DatabaseConstructor;

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
// JSONL parsing types
// ---------------------------------------------------------------------------

type ContentBlock = {
  type?: string;
  text?: string;
};

type SessionLine = {
  type?: string;
  message?: {
    role?: string;
    content?: string | ContentBlock[];
  };
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractTextContent(content: string | ContentBlock[]): string {
  if (typeof content === "string") return content.trim();
  return content
    .filter((b) => b.type === "text" && typeof b.text === "string")
    .map((b) => (b.text as string).trim())
    .join("\n")
    .trim();
}

/**
 * Parse a raw Claude session JSONL file into a flat conversation string.
 * Returns the conversation text and message count.
 */
function parseSessionFile(
  filePath: string,
): { text: string; turnCount: number } {
  const raw = readFileSync(filePath, "utf-8");
  const lines = raw.split("\n");
  const parts: string[] = [];
  let turnCount = 0;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    let obj: SessionLine;
    try {
      obj = JSON.parse(trimmed) as SessionLine;
    } catch {
      logger.warn(`  Skipping malformed line in ${basename(filePath)}`);
      continue;
    }

    const type = obj?.type;
    if (type !== "user" && type !== "assistant") continue;

    const content = obj?.message?.content;
    if (content === undefined || content === null) continue;

    const text = extractTextContent(
      content as string | ContentBlock[],
    );
    if (!text) continue;

    const role = type === "user" ? "User" : "Assistant";
    parts.push(`[${role}]: ${text}`);
    turnCount++;
  }

  return { text: parts.join("\n\n"), turnCount };
}

/**
 * Try to read the extraction model from schema_meta table.
 * Falls back to DEFAULT_MODEL if not found or DB unavailable.
 */
function readExtractionModel(): string {
  if (!existsSync(DB_PATH)) return DEFAULT_MODEL;
  let db: Database | null = null;
  try {
    db = new DatabaseCtor(DB_PATH, { readonly: true });
    const row = db
      .prepare("SELECT value FROM schema_meta WHERE key = 'extractionModel'")
      .get() as { value: string } | undefined;
    return row?.value ?? DEFAULT_MODEL;
  } catch {
    return DEFAULT_MODEL;
  } finally {
    try { db?.close(); } catch { /* ignore */ }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  // Parse CLI args
  const args = process.argv.slice(2);
  const dryRun = args.includes("--dry-run");
  const limitIdx = args.indexOf("--limit");
  const limit = limitIdx !== -1 ? parseInt(args[limitIdx + 1]!, 10) : Infinity;
  const agentIdx = args.indexOf("--agent");
  const agentId = agentIdx !== -1 ? (args[agentIdx + 1] ?? "main") : "main";

  if (dryRun) {
    console.log("DRY RUN — no facts will be saved, no files will be moved.");
  }

  // Validate raw-sessions directory
  if (!existsSync(RAW_SESSIONS_DIR)) {
    console.error(`Raw sessions directory does not exist: ${RAW_SESSIONS_DIR}`);
    process.exit(1);
  }

  // Scan for JSONL files (skip .processed/ subdirectory)
  let files = readdirSync(RAW_SESSIONS_DIR)
    .filter((f) => f.endsWith(".jsonl"))
    .sort()
    .map((f) => join(RAW_SESSIONS_DIR, f));

  if (files.length === 0) {
    console.log(`No JSONL files found in ${RAW_SESSIONS_DIR}`);
    return;
  }

  const totalFiles = files.length;
  if (isFinite(limit) && limit < files.length) {
    files = files.slice(0, limit);
  }

  console.log(
    `Found ${totalFiles} JSONL file(s) in raw-sessions/. Processing ${files.length}...`,
  );

  // Read extraction model config
  const extractionModel = readExtractionModel();
  console.log(`Extraction model: ${extractionModel}`);
  console.log(`Agent ID: ${agentId}`);
  console.log("");

  // Open Memento DB
  const db = new ConversationDB(DB_PATH);

  // Ensure .processed dir exists
  if (!dryRun) {
    mkdirSync(PROCESSED_DIR, { recursive: true });
  }

  let totalExtracted = 0;
  let totalUpdated = 0;
  let totalDeduplicated = 0;
  let totalErrors = 0;
  let totalSkipped = 0;
  let processedCount = 0;

  for (let i = 0; i < files.length; i++) {
    const filePath = files[i]!;
    const fileName = basename(filePath);
    console.log(`Processing file ${i + 1}/${files.length}: ${fileName}...`);

    // Parse the raw session JSONL
    let sessionData: { text: string; turnCount: number };
    try {
      sessionData = parseSessionFile(filePath);
    } catch (err) {
      logger.error(`  Failed to read/parse ${fileName}: ${String(err)}`);
      totalErrors++;
      if (!dryRun) {
        renameSync(filePath, join(PROCESSED_DIR, fileName));
      }
      continue;
    }

    const { text, turnCount } = sessionData;

    // Skip files with fewer than 3 meaningful exchanges (< 6 message parts)
    if (turnCount < 6) {
      logger.warn(
        `  Skipping ${fileName} — only ${turnCount} message parts (min: 6)`,
      );
      totalSkipped++;
      if (!dryRun) {
        renameSync(filePath, join(PROCESSED_DIR, fileName));
      }
      continue;
    }

    // Truncate very large conversations to last 8000 chars
    const conversationText =
      text.length > 8000 ? text.slice(-8000) : text;

    if (dryRun) {
      console.log(
        `  → Would extract from ${turnCount} messages (${conversationText.length} chars)`,
      );
      console.log(
        `  Preview: ${conversationText.slice(0, 200).replace(/\n/g, " ")}...`,
      );
      totalSkipped++;
      continue;
    }

    // Build a synthetic ConversationRow for the extractor
    const now = Date.now();
    const conversationId = randomUUID();
    const convRow: ConversationRow = {
      id: conversationId,
      agent_id: agentId,
      session_key: `raw-session:${fileName}`,
      channel: "raw-ingest",
      started_at: now,
      ended_at: now,
      turn_count: Math.floor(turnCount / 2),
      raw_text: conversationText,
      metadata: null,
    };

    // Insert conversation row so FK references in fact_occurrences / extraction_log work
    db.insertConversationWithMessages(convRow, []);

    // Fetch existing facts for dedup context (pass up to 50)
    const existingFacts = db.getRelevantFacts(agentId, 50);

    // Call LLM extractor
    let extractionResult: Awaited<ReturnType<typeof extractFacts>>;
    try {
      extractionResult = await extractFacts(
        convRow,
        existingFacts,
        extractionModel,
        logger,
      );
    } catch (err) {
      logger.error(`  Extraction threw for ${fileName}: ${String(err)}`);
      totalErrors++;
      renameSync(filePath, join(PROCESSED_DIR, fileName));
      // Rate limit: pause before next call
      if (i < files.length - 1) await sleep(1000);
      continue;
    }

    if (extractionResult.error) {
      logger.error(
        `  Extraction failed for ${fileName}: ${extractionResult.error}`,
      );
      totalErrors++;
      renameSync(filePath, join(PROCESSED_DIR, fileName));
      if (i < files.length - 1) await sleep(1000);
      continue;
    }

    // Save extracted facts via deduplicator
    const dedup = await processExtractedFacts(
      extractionResult.facts,
      conversationId,
      agentId,
      db,
      null, // embeddingEngine — not available in CLI mode
      logger,
    );

    console.log(
      `  → extracted ${dedup.factsExtracted} new, ` +
        `${dedup.factsUpdated} updated, ` +
        `${dedup.factsDeduplicated} deduplicated`,
    );

    totalExtracted += dedup.factsExtracted;
    totalUpdated += dedup.factsUpdated;
    totalDeduplicated += dedup.factsDeduplicated;
    processedCount++;

    // Move processed file to .processed/
    renameSync(filePath, join(PROCESSED_DIR, fileName));

    // Rate limit: 1-second delay between LLM calls
    if (i < files.length - 1) {
      await sleep(1000);
    }
  }

  // Summary
  console.log("\n--- Summary ---");
  console.log(`Files processed:    ${processedCount}`);
  console.log(`Files skipped:      ${totalSkipped}`);
  console.log(`Errors:             ${totalErrors}`);
  console.log(`Facts extracted:    ${totalExtracted}`);
  console.log(`Facts updated:      ${totalUpdated}`);
  console.log(`Facts deduplicated: ${totalDeduplicated}`);
}

main().catch((err: unknown) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
