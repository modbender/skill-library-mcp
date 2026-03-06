#!/usr/bin/env node
/**
 * Backfill Embeddings
 *
 * Generates and stores BGE-M3 embeddings for all facts that don't have one yet.
 * Run this after installing the embedding model to populate the vector index.
 *
 * Usage:
 *   npx tsx src/storage/backfill-embeddings.ts [--db <path>] [--batch <size>] [--dry-run]
 *
 * Options:
 *   --db <path>     Path to the conversations.sqlite file
 *                    Default: ~/.engram/conversations.sqlite
 *   --batch <size>  Number of facts to embed per batch (default: 50)
 *   --dry-run       Show what would be done without actually embedding
 *
 * The script embeds fact content + summary for best retrieval quality.
 */

import { join } from "node:path";
import { homedir } from "node:os";
import { existsSync } from "node:fs";
import { ConversationDB } from "./db.js";
import { EmbeddingEngine } from "./embeddings.js";

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);

function getArg(name: string): string | undefined {
  const idx = args.indexOf(`--${name}`);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : undefined;
}

const dryRun = args.includes("--dry-run");
const batchSize = parseInt(getArg("batch") ?? "50", 10);

// Find the database
const defaultDbPaths = [
  join(homedir(), ".engram", "conversations.sqlite"),
  
];
const dbPath =
  getArg("db") ?? defaultDbPaths.find((p) => existsSync(p));

if (!dbPath || !existsSync(dbPath)) {
  console.error("❌ Database not found. Use --db <path> to specify location.");
  console.error("   Searched:", defaultDbPaths.join(", "));
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Logger
// ---------------------------------------------------------------------------

const logger = {
  info: (...args: any[]) => console.log("[memento]", ...args),
  warn: (...args: any[]) => console.warn("[memento]", ...args),
  error: (...args: any[]) => console.error("[memento:error]", ...args),
  debug: (...args: any[]) => {
    if (process.env.DEBUG) console.log("[memento:debug]", ...args);
  },
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  console.log("🧠 Memento — Embedding Backfill");
  console.log(`   Database: ${dbPath}`);
  console.log(`   Batch size: ${batchSize}`);
  console.log(`   Dry run: ${dryRun}`);
  console.log("");

  const db = new ConversationDB(dbPath!);
  const stats = db.countFactsMissingEmbeddings();

  console.log(
    `   Total active facts: ${stats.total}`,
  );
  console.log(
    `   Already embedded: ${stats.withEmbedding}`,
  );
  console.log(
    `   Need embedding: ${stats.withoutEmbedding}`,
  );
  console.log("");

  if (stats.withoutEmbedding === 0) {
    console.log("✅ All facts already have embeddings. Nothing to do.");
    db.close();
    return;
  }

  if (dryRun) {
    console.log("🔍 Dry run — would embed", stats.withoutEmbedding, "facts.");
    db.close();
    return;
  }

  // Initialize embedding engine
  const engine = new EmbeddingEngine(undefined, logger);
  console.log("⏳ Loading embedding model...");
  const testEmb = await engine.embed("test");
  if (!testEmb) {
    console.error("❌ Failed to initialize embedding engine.");
    console.error(
      "   Download the model: curl -L -o ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf " +
        '"https://huggingface.co/gpustack/bge-m3-GGUF/resolve/main/bge-m3-Q8_0.gguf"',
    );
    db.close();
    process.exit(1);
  }
  console.log(`✅ Model loaded (${engine.embeddingDimensions} dimensions)`);
  console.log("");

  // Process in batches
  let embedded = 0;
  let failed = 0;

  while (true) {
    const batch = db.getFactsMissingEmbeddings(batchSize);
    if (batch.length === 0) break;

    const texts = batch.map(
      (f) =>
        `${f.summary ? f.summary + ". " : ""}${f.content}`.slice(0, 2000),
    );

    const embeddings = await engine.embedBatch(texts, (done, total) => {
      process.stdout.write(
        `\r   Embedding batch: ${done}/${total} (total: ${embedded + done}/${stats.withoutEmbedding})`,
      );
    });
    console.log(""); // newline after progress

    const updates: { factId: string; embedding: number[] }[] = [];
    for (let i = 0; i < batch.length; i++) {
      const emb = embeddings[i];
      if (emb) {
        updates.push({ factId: batch[i].id, embedding: emb });
        embedded++;
      } else {
        failed++;
      }
    }

    if (updates.length > 0) {
      db.setFactEmbeddingsBatch(updates);
    }

    console.log(
      `   Batch done: ${updates.length} embedded, ${batch.length - updates.length} failed`,
    );
  }

  console.log("");
  console.log("🎉 Backfill complete!");
  console.log(`   Embedded: ${embedded}`);
  if (failed > 0) console.log(`   Failed: ${failed}`);

  // Verify
  const finalStats = db.countFactsMissingEmbeddings();
  console.log(
    `   Coverage: ${finalStats.withEmbedding}/${finalStats.total} facts have embeddings`,
  );

  await engine.dispose();
  db.close();
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
