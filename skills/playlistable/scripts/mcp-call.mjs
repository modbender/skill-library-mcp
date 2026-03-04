#!/usr/bin/env node

/**
 * Call Playlistable MCP tools directly via Streamable HTTP transport.
 *
 * Usage:
 *   node mcp-call.mjs <tool-name> [json-params]
 *   node mcp-call.mjs --list-tools
 *
 * Examples:
 *   node mcp-call.mjs generate_playlist '{"mood": "chill lo-fi for studying"}'
 *   node mcp-call.mjs search_songs '{"query": "Blinding Lights", "limit": 5}'
 *   node mcp-call.mjs get_playlists
 *   node mcp-call.mjs playlist_suggestions '{"userHour": 22}'
 */

import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const MCP_URL = "https://mcp.playlistable.io";

function usage() {
  console.error("Usage: mcp-call.mjs <tool-name> [json-params]");
  console.error("       mcp-call.mjs --list-tools");
  console.error("");
  console.error("Tools: generate_playlist, get_playlist, get_playlists,");
  console.error("       edit_playlist, delete_playlist, playlist_suggestions,");
  console.error("       search_songs, search_artists");
  console.error("");
  console.error('Example: mcp-call.mjs generate_playlist \'{"mood": "chill vibes"}\'');
  process.exit(2);
}

function loadApiKey() {
  // 1. Environment variable
  const envKey = (process.env.PLAYLISTABLE_API_KEY ?? "").trim();
  if (envKey) return envKey;

  // 2. config/auth.json
  try {
    const configPath = resolve(__dirname, "..", "config", "auth.json");
    const config = JSON.parse(readFileSync(configPath, "utf-8"));
    if (config.api_key) return config.api_key;
    if (config.access_token) return config.access_token;
  } catch {
    // not found
  }

  console.error("No API key found. Set PLAYLISTABLE_API_KEY or run: node scripts/auth.mjs");
  process.exit(1);
}

async function callMcp(method, params, apiKey) {
  const resp = await fetch(MCP_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`MCP request failed (${resp.status}): ${text}`);
  }

  const contentType = resp.headers.get("content-type") || "";

  // Handle SSE response
  if (contentType.includes("text/event-stream")) {
    const text = await resp.text();
    for (const line of text.split("\n")) {
      if (line.startsWith("data: ")) {
        try {
          return JSON.parse(line.slice(6));
        } catch {
          // keep scanning
        }
      }
    }
    throw new Error("No valid JSON-RPC response in SSE stream");
  }

  return await resp.json();
}

// --- Main ---

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const apiKey = loadApiKey();

// List tools
if (args[0] === "--list-tools") {
  const result = await callMcp("tools/list", {}, apiKey);
  const tools = result?.result?.tools ?? [];
  if (!tools.length) {
    console.log("No tools returned.");
    process.exit(0);
  }
  console.log(`${tools.length} tools:\n`);
  for (const t of tools) {
    console.log(`  ${t.name}`);
    if (t.description) console.log(`    ${t.description}`);
    const props = t.inputSchema?.properties;
    if (props) {
      for (const [k, v] of Object.entries(props)) {
        const req = t.inputSchema?.required?.includes(k) ? " (required)" : "";
        console.log(`    - ${k}: ${v.type ?? "any"}${req}`);
      }
    }
    console.log();
  }
  process.exit(0);
}

// Call a tool
const toolName = args[0];
const waitFlag = args.includes("--wait");
let params = {};

const paramsArg = args[1] && !args[1].startsWith("--") ? args[1] : null;
if (paramsArg) {
  try {
    params = JSON.parse(paramsArg);
  } catch (e) {
    console.error(`Invalid JSON params: ${e.message}`);
    process.exit(1);
  }
}

function extractContent(result) {
  if (result.error) {
    console.error(`Error: ${result.error.message || JSON.stringify(result.error)}`);
    process.exit(1);
  }
  const content = result.result?.content;
  if (Array.isArray(content)) {
    for (const block of content) {
      if (block.type === "text") {
        try {
          return JSON.parse(block.text);
        } catch {
          return block.text;
        }
      }
    }
  }
  return result;
}

try {
  const result = await callMcp("tools/call", { name: toolName, arguments: params }, apiKey);
  const data = extractContent(result);

  // --wait: poll get_playlist until status === "ready"
  if (waitFlag && toolName === "generate_playlist" && data?.id) {
    console.error(`Playlist created: ${data.playlistableUrl || data.url}`);
    console.error(`Spotify: ${data.url}`);
    console.error(`Waiting for tracks to generate...`);

    const INITIAL_WAIT = 15000;
    const POLL_INTERVAL = 10000;
    const TIMEOUT = 3 * 60 * 1000;
    const start = Date.now();

    await new Promise((r) => setTimeout(r, INITIAL_WAIT));

    while (Date.now() - start < TIMEOUT) {
      await new Promise((r) => setTimeout(r, POLL_INTERVAL));
      const poll = await callMcp("tools/call", { name: "get_playlist", arguments: { id: data.id } }, apiKey);
      const playlist = extractContent(poll);
      if (playlist?.status === "ready") {
        console.log(JSON.stringify(playlist, null, 2));
        process.exit(0);
      }
      console.error(`Still generating... (${Math.round((Date.now() - start) / 1000)}s)`);
    }

    console.error("Timed out waiting for playlist. Check manually with get_playlist.");
    process.exit(1);
  }

  console.log(typeof data === "string" ? data : JSON.stringify(data, null, 2));
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
