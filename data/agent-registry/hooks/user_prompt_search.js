#!/usr/bin/env bun
"use strict";

/**
 * UserPromptSubmit Hook for Agent Registry
 *
 * Automatically searches the agent registry when the user submits a prompt.
 * If high-confidence agent matches are found, injects them as additionalContext
 * so Claude can load relevant agents without manual search.
 *
 * Receives JSON on stdin: {"prompt": "...", "session_id": "...", ...}
 * Outputs JSON on stdout: {"additionalContext": "..."} or nothing
 *
 * Runs on Bun (Claude Code's runtime) — no Python dependency. Imports the
 * shared BM25 search engine from lib/search.js.
 */

const fs = require("fs");
const path = require("path");
const { searchAgents } = require("../lib/search");

// Configuration
const MIN_WORDS = 3;
const SCORE_THRESHOLD = 0.5;
const TOP_K = 3;

// ============================================================================
// Hook Entry Point
// ============================================================================

function main() {
  let raw;
  try {
    raw = fs.readFileSync(0, "utf8"); // fd 0 = stdin
  } catch {
    process.exit(0);
  }

  let data;
  try {
    data = JSON.parse(raw);
  } catch {
    process.exit(0);
  }

  const prompt = (data.prompt || "").trim();

  // Skip slash commands and short prompts
  if (!prompt || prompt.startsWith("/") || prompt.split(/\s+/).length < MIN_WORDS) {
    process.exit(0);
  }

  // Load registry directly — silent fail for hooks
  const registryPath = path.join(path.resolve(__dirname, ".."), "references", "registry.json");

  let registry;
  try {
    registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
  } catch {
    process.exit(0);
  }

  // Search and filter to high-confidence matches
  const results = searchAgents(prompt, registry, TOP_K).filter(
    (r) => r.score >= SCORE_THRESHOLD
  );

  if (results.length === 0) {
    process.exit(0);
  }

  // Format and output additionalContext
  const lines = ["Agent Registry found relevant agents for this task:", ""];
  for (const r of results) {
    lines.push(`  - ${r.name} (score: ${r.score.toFixed(2)}): ${r.summary}`);
  }
  lines.push("");
  lines.push("To load an agent: bun bin/get.js <agent-name>");

  console.log(JSON.stringify({ additionalContext: lines.join("\n") }));
}

main();
