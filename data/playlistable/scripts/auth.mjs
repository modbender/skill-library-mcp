#!/usr/bin/env node

/**
 * Authenticate with Playlistable MCP via Spotify OAuth.
 *
 * Usage:
 *   node auth.mjs
 *
 * Starts a local HTTP server, opens browser for Spotify login,
 * catches the OAuth redirect, exchanges the code for an API key,
 * and saves it to config/auth.json — fully automatic.
 */

import { randomBytes, createHash } from "crypto";
import { createServer } from "http";
import { existsSync, mkdirSync, writeFileSync, readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { exec } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_DIR = resolve(__dirname, "..", "config");
const CONFIG_PATH = resolve(CONFIG_DIR, "auth.json");
const MCP_URL = "https://mcp.playlistable.io";

// Check if already authenticated
if (existsSync(CONFIG_PATH)) {
  try {
    const existing = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
    if (existing.api_key) {
      console.log("Already authenticated.");
      console.log(`API key: ${existing.api_key.slice(0, 12)}...${existing.api_key.slice(-6)}`);
      console.log(`\nTo re-authenticate, delete ${CONFIG_PATH} and run again.`);
      process.exit(0);
    }
  } catch {
    // corrupt file, proceed with auth
  }
}

// PKCE: generate code_verifier and code_challenge (S256)
const codeVerifier = randomBytes(32).toString("base64url");
const codeChallenge = createHash("sha256")
  .update(codeVerifier)
  .digest("base64")
  .replace(/\+/g, "-")
  .replace(/\//g, "_")
  .replace(/=+$/, "");

const sessionId = randomBytes(16).toString("hex");

// 1. Start a local HTTP server to catch the OAuth redirect
const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost`);

  if (!url.pathname.startsWith("/callback")) {
    res.writeHead(404);
    res.end("Not found");
    return;
  }

  const code = url.searchParams.get("code");

  if (!code) {
    const error = url.searchParams.get("error") || "unknown";
    res.writeHead(400, { "Content-Type": "text/html" });
    res.end(`<h1>Auth failed</h1><p>${error}</p>`);
    console.error(`\nAuth failed: ${error}`);
    server.close();
    process.exit(1);
  }

  // 3. Exchange code for API key
  try {
    const tokenResp = await fetch(`${MCP_URL}/oauth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        redirect_uri: redirectUri,
        code_verifier: codeVerifier,
      }).toString(),
    });

    if (!tokenResp.ok) {
      const err = await tokenResp.text().catch(() => "");
      throw new Error(`Token exchange failed (${tokenResp.status}): ${err}`);
    }

    const { access_token } = await tokenResp.json();

    // Save to config
    if (!existsSync(CONFIG_DIR)) {
      mkdirSync(CONFIG_DIR, { recursive: true });
    }
    writeFileSync(
      CONFIG_PATH,
      JSON.stringify({ api_key: access_token, created_at: new Date().toISOString() }, null, 2)
    );

    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(`<!DOCTYPE html><html><body style="font-family:system-ui;text-align:center;padding:60px">
      <h1>Connected!</h1><p>API key saved. You can close this window.</p>
    </body></html>`);

    console.log("\nAuthentication successful!");
    console.log(`API key saved to: ${CONFIG_PATH}`);
    console.log(`\nYou can now use: node scripts/mcp-call.mjs <tool> [params]`);
  } catch (err) {
    res.writeHead(500, { "Content-Type": "text/html" });
    res.end(`<h1>Error</h1><p>${err.message}</p>`);
    console.error(`\nToken exchange error: ${err.message}`);
  }

  server.close();
  process.exit(0);
});

// Listen on a random available port
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const port = server.address().port;
const redirectUri = `http://localhost:${port}/callback`;

// 2. Register a dynamic OAuth client with our local redirect URI
const registerResp = await fetch(`${MCP_URL}/register`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    client_name: "OpenClaw CLI",
    redirect_uris: [redirectUri],
    token_endpoint_auth_method: "none",
    grant_types: ["authorization_code"],
    response_types: ["code"],
  }),
});

if (!registerResp.ok) {
  console.error(`Client registration failed (${registerResp.status})`);
  server.close();
  process.exit(1);
}

const { client_id } = await registerResp.json();

// Build authorize URL with PKCE
const authUrl = new URL(`${MCP_URL}/authorize`);
authUrl.searchParams.set("session_id", sessionId);
authUrl.searchParams.set("client_id", client_id);
authUrl.searchParams.set("redirect_uri", redirectUri);
authUrl.searchParams.set("response_type", "code");
authUrl.searchParams.set("code_challenge", codeChallenge);
authUrl.searchParams.set("code_challenge_method", "S256");

console.log("Opening browser for Spotify authorization...");
console.log(`\nIf the browser doesn't open, visit:\n${authUrl.toString()}\n`);
console.log(`Listening on http://localhost:${port} for callback...`);

// Open browser
const openCmd =
  process.platform === "darwin" ? "open" : process.platform === "win32" ? "start" : "xdg-open";
exec(`${openCmd} "${authUrl.toString()}"`);

// Timeout after 5 minutes
setTimeout(() => {
  console.error("\nAuthentication timed out after 5 minutes.");
  server.close();
  process.exit(1);
}, 5 * 60 * 1000);
