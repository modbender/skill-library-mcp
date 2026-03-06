#!/usr/bin/env node
/**
 * CLI for managing Memento ingest tokens.
 *
 * Usage:
 *   memento-token create --name "mac-mini-m2"
 *   memento-token list
 *   memento-token revoke <id>
 */

import { randomBytes, createHash, randomUUID } from "node:crypto";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";

// ---------------------------------------------------------------------------
// Load better-sqlite3 (CJS module, load via createRequire for ESM compat)
// ---------------------------------------------------------------------------

import type BetterSQLite3 from "better-sqlite3";
type Database = BetterSQLite3.Database;
type DatabaseConstructor = typeof BetterSQLite3;

const _require = createRequire(import.meta.url);
const DatabaseCtor = _require("better-sqlite3") as DatabaseConstructor;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type TokenRow = {
  id: string;
  name: string;
  token_hash: string;
  created_at: number;
  last_used_at: number | null;
  is_active: number;
};

// ---------------------------------------------------------------------------
// DB helpers
// ---------------------------------------------------------------------------

const DB_PATH = join(homedir(), ".engram", "conversations.sqlite");

function openDB(): Database {
  if (!existsSync(DB_PATH)) {
    console.error(`✗ Database not found at ${DB_PATH}`);
    console.error("  Run OpenClaw at least once to initialize the database.");
    process.exit(1);
  }

  const db = new DatabaseCtor(DB_PATH);
  db.pragma("journal_mode = WAL");

  // Ensure the ingest_tokens table exists (idempotent)
  db.exec(`
    CREATE TABLE IF NOT EXISTS ingest_tokens (
      id          TEXT PRIMARY KEY,
      name        TEXT NOT NULL,
      token_hash  TEXT NOT NULL UNIQUE,
      created_at  INTEGER NOT NULL,
      last_used_at INTEGER,
      is_active   INTEGER DEFAULT 1
    );
  `);

  return db;
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

function cmdCreate(args: string[]): void {
  const nameIdx = args.indexOf("--name");
  const name = nameIdx !== -1 ? args[nameIdx + 1] : undefined;

  if (!name || name.startsWith("--")) {
    console.error("Usage: memento-token create --name <name>");
    console.error("  Example: memento-token create --name mac-mini-m2");
    process.exit(1);
  }

  const rawToken = randomBytes(32).toString("hex");
  const tokenHash = createHash("sha256").update(rawToken).digest("hex");
  const id = randomUUID();

  const db = openDB();
  db.prepare(
    "INSERT INTO ingest_tokens (id, name, token_hash, created_at) VALUES (?, ?, ?, ?)"
  ).run(id, name, tokenHash, Date.now());
  db.close();

  console.log(`✓ Token created for "${name}"`);
  console.log(`  ID:    ${id}`);
  console.log(`  Token: ${rawToken}`);
  console.log("");
  console.log("  ⚠  Save this token now — it will NOT be shown again.");
}

function cmdList(): void {
  const db = openDB();
  const rows = db
    .prepare(
      "SELECT id, name, created_at, last_used_at, is_active FROM ingest_tokens ORDER BY created_at DESC"
    )
    .all() as TokenRow[];
  db.close();

  if (rows.length === 0) {
    console.log("No ingest tokens found.");
    return;
  }

  console.log("Ingest tokens:\n");
  for (const row of rows) {
    const status = row.is_active ? "✓ active " : "✗ revoked";
    const created = new Date(row.created_at).toISOString().slice(0, 19).replace("T", " ");
    const lastUsed = row.last_used_at
      ? new Date(row.last_used_at).toISOString().slice(0, 19).replace("T", " ")
      : "never";
    console.log(`  ${status}  ${row.id}`);
    console.log(`            name: ${row.name}`);
    console.log(`         created: ${created}`);
    console.log(`       last used: ${lastUsed}`);
    console.log("");
  }
}

function cmdRevoke(args: string[]): void {
  const id = args[0];

  if (!id || id.startsWith("--")) {
    console.error("Usage: memento-token revoke <id>");
    process.exit(1);
  }

  const db = openDB();
  const result = db
    .prepare("UPDATE ingest_tokens SET is_active = 0 WHERE id = ?")
    .run(id);
  db.close();

  if (result.changes === 0) {
    console.error(`✗ Token not found: ${id}`);
    process.exit(1);
  }

  console.log(`✓ Token revoked: ${id}`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const [, , command, ...rest] = process.argv;

switch (command) {
  case "create":
    cmdCreate(rest);
    break;
  case "list":
    cmdList();
    break;
  case "revoke":
    cmdRevoke(rest);
    break;
  default:
    console.error("Memento ingest token manager\n");
    console.error("Usage: memento-token <command> [options]\n");
    console.error("Commands:");
    console.error("  create --name <name>   Create a new ingest token");
    console.error("  list                   List all tokens");
    console.error("  revoke <id>            Revoke a token by ID");
    process.exit(command ? 1 : 0);
}
