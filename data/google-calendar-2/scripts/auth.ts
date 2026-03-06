/**
 * Google Calendar OAuth 2.0 — Desktop/Native App flow with PKCE
 *
 * Supports multiple accounts via --account <alias>.
 *
 * Usage:
 *   bun run auth.ts login [--account work]     # Start OAuth flow
 *   bun run auth.ts status [--account work]     # Check if authenticated
 *   bun run auth.ts refresh [--account work]    # Force-refresh the access token
 *   bun run auth.ts revoke [--account work]     # Revoke tokens and delete stored credentials
 *   bun run auth.ts token [--account work]      # Print current access token (refreshes if expired)
 *   bun run auth.ts accounts                    # List all authenticated accounts
 */

import * as crypto from "node:crypto";
import * as fs from "node:fs";
import * as http from "node:http";
import * as path from "node:path";
import * as url from "node:url";

// ─── Config ──────────────────────────────────────────────────────────────────

const SCOPES = [
  "https://www.googleapis.com/auth/calendar",
  "https://www.googleapis.com/auth/calendar.events",
];

const AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth";
const TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token";
const REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke";

const DEFAULT_ACCOUNT = "default";

const CREDENTIALS_DIR = path.join(
  process.env.HOME ?? "~",
  ".config",
  "google-calendar-skill"
);
const CLIENT_CREDENTIALS_PATH = path.join(CREDENTIALS_DIR, "client.json");
const TOKENS_DIR = path.join(CREDENTIALS_DIR, "tokens");

// Skill config lives in skill root (parent of scripts/ when run from scripts/)
function skillConfigPath(): string {
  return path.join(process.cwd(), "..", "config.json");
}

// ─── Types ───────────────────────────────────────────────────────────────────

interface ClientCredentials {
  client_id: string;
  client_secret?: string;
}

interface StoredTokens {
  access_token: string;
  refresh_token: string;
  expires_at: number; // epoch ms
  scope: string;
  token_type: string;
  email?: string; // Google account email, detected after login
}

// ─── PKCE helpers ────────────────────────────────────────────────────────────

function generateCodeVerifier(): string {
  return crypto.randomBytes(64).toString("base64url").slice(0, 128);
}

function generateCodeChallenge(verifier: string): string {
  return crypto.createHash("sha256").update(verifier).digest("base64url");
}

// ─── Credential helpers ─────────────────────────────────────────────────────

function ensureDir(dir: string) {
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
}

function tokenPath(account: string): string {
  return path.join(TOKENS_DIR, `${account}.json`);
}

function loadClientCredentials(): ClientCredentials {
  if (!fs.existsSync(CLIENT_CREDENTIALS_PATH)) {
    console.error(
      `\n✗ Client credentials not found at ${CLIENT_CREDENTIALS_PATH}\n` +
        `\nCreate the file with your OAuth client_id (and optionally client_secret):\n\n` +
        `  mkdir -p ${CREDENTIALS_DIR}\n` +
        `  cat > ${CLIENT_CREDENTIALS_PATH} << 'EOF'\n` +
        `  {\n` +
        `    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",\n` +
        `    "client_secret": "YOUR_CLIENT_SECRET"\n` +
        `  }\n` +
        `  EOF\n` +
        `  chmod 600 ${CLIENT_CREDENTIALS_PATH}\n`
    );
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(CLIENT_CREDENTIALS_PATH, "utf-8"));
}

function loadTokens(account: string): StoredTokens | null {
  const p = tokenPath(account);
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(fs.readFileSync(p, "utf-8"));
  } catch {
    return null;
  }
}

function saveTokens(account: string, tokens: StoredTokens) {
  ensureDir(TOKENS_DIR);
  fs.writeFileSync(tokenPath(account), JSON.stringify(tokens, null, 2), {
    mode: 0o600,
  });
}

function deleteTokens(account: string) {
  const p = tokenPath(account);
  if (fs.existsSync(p)) fs.unlinkSync(p);
}

// ─── Backward compat: migrate old single token.json → tokens/default.json ──

function migrateOldTokenFile() {
  const oldPath = path.join(CREDENTIALS_DIR, "token.json");
  const newPath = tokenPath(DEFAULT_ACCOUNT);
  if (fs.existsSync(oldPath) && !fs.existsSync(newPath)) {
    ensureDir(TOKENS_DIR);
    fs.renameSync(oldPath, newPath);
  }
}

// ─── Token exchange & refresh ────────────────────────────────────────────────

async function exchangeCode(
  code: string,
  codeVerifier: string,
  redirectUri: string,
  client: ClientCredentials,
  account: string
): Promise<StoredTokens> {
  const body = new URLSearchParams({
    code,
    client_id: client.client_id,
    redirect_uri: redirectUri,
    grant_type: "authorization_code",
    code_verifier: codeVerifier,
  });
  if (client.client_secret) {
    body.set("client_secret", client.client_secret);
  }

  const res = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Token exchange failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  const tokens: StoredTokens = {
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    expires_at: Date.now() + data.expires_in * 1000,
    scope: data.scope,
    token_type: data.token_type,
  };
  saveTokens(account, tokens);
  return tokens;
}

async function refreshAccessToken(
  client: ClientCredentials,
  refreshToken: string,
  account: string
): Promise<StoredTokens> {
  const body = new URLSearchParams({
    client_id: client.client_id,
    grant_type: "refresh_token",
    refresh_token: refreshToken,
  });
  if (client.client_secret) {
    body.set("client_secret", client.client_secret);
  }

  const res = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Token refresh failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  const tokens: StoredTokens = {
    access_token: data.access_token,
    refresh_token: data.refresh_token ?? refreshToken,
    expires_at: Date.now() + data.expires_in * 1000,
    scope: data.scope,
    token_type: data.token_type,
  };
  saveTokens(account, tokens);
  return tokens;
}

// ─── Fetch authenticated email via Calendar API ─────────────────────────────

async function fetchEmail(accessToken: string): Promise<string | null> {
  try {
    const res = await fetch(
      "https://www.googleapis.com/calendar/v3/calendars/primary",
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!res.ok) return null;
    const data = await res.json();
    return data.id ?? null; // primary calendar ID is the user's email
  } catch {
    return null;
  }
}

// ─── Public: get a valid access token (auto-refreshes) ───────────────────────

export async function getAccessToken(
  account: string = DEFAULT_ACCOUNT
): Promise<string> {
  migrateOldTokenFile();
  const client = loadClientCredentials();
  const tokens = loadTokens(account);

  if (!tokens) {
    console.error(
      `✗ Account '${account}' not authenticated. Run: bun run auth.ts login --account ${account}`
    );
    process.exit(1);
  }

  // Refresh if within 5 min of expiry
  if (Date.now() > tokens.expires_at - 5 * 60 * 1000) {
    const refreshed = await refreshAccessToken(
      client,
      tokens.refresh_token,
      account
    );
    return refreshed.access_token;
  }

  return tokens.access_token;
}

// ─── OAuth login flow ────────────────────────────────────────────────────────

async function login(account: string) {
  const client = loadClientCredentials();
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);

  // Start a loopback HTTP server on a random port
  const server = http.createServer();
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  const redirectUri = `http://127.0.0.1:${port}`;

  // Build the authorization URL
  const authUrl = new URL(AUTH_ENDPOINT);
  authUrl.searchParams.set("client_id", client.client_id);
  authUrl.searchParams.set("redirect_uri", redirectUri);
  authUrl.searchParams.set("response_type", "code");
  authUrl.searchParams.set("scope", SCOPES.join(" "));
  authUrl.searchParams.set("code_challenge", codeChallenge);
  authUrl.searchParams.set("code_challenge_method", "S256");
  authUrl.searchParams.set("access_type", "offline");
  authUrl.searchParams.set("prompt", "consent");

  const label =
    account === DEFAULT_ACCOUNT ? "" : ` (account: ${account})`;
  console.log(`\n▸ Opening browser for Google authorization${label}...`);
  console.log(`  If it doesn't open, visit:\n  ${authUrl.toString()}\n`);

  // Try to open the browser
  try {
    const open = (await import("open")).default;
    await open(authUrl.toString());
  } catch {
    // Browser open failed — user can copy the URL above
  }

  // Wait for the redirect callback
  const code = await new Promise<string>((resolve, reject) => {
    const timeout = setTimeout(() => {
      server.close();
      reject(new Error("Timed out waiting for authorization (5 minutes)."));
    }, 5 * 60 * 1000);

    server.on("request", (req, res) => {
      const parsed = url.parse(req.url ?? "", true);
      const authCode = parsed.query.code as string | undefined;
      const error = parsed.query.error as string | undefined;

      if (error) {
        res.writeHead(400, { "Content-Type": "text/html" });
        res.end(
          `<html><body><h2>Authorization denied</h2><p>${error}</p><p>You can close this tab.</p></body></html>`
        );
        clearTimeout(timeout);
        server.close();
        reject(new Error(`Authorization denied: ${error}`));
        return;
      }

      if (authCode) {
        res.writeHead(200, { "Content-Type": "text/html" });
        res.end(
          `<html><body><h2>Authorization successful!</h2><p>You can close this tab and return to your terminal.</p></body></html>`
        );
        clearTimeout(timeout);
        server.close();
        resolve(authCode);
        return;
      }

      // Favicon or other requests — ignore
      res.writeHead(204);
      res.end();
    });
  });

  console.log("▸ Exchanging authorization code for tokens...");
  const tokens = await exchangeCode(
    code,
    codeVerifier,
    redirectUri,
    client,
    account
  );

  // Detect the authenticated email
  const email = await fetchEmail(tokens.access_token);
  if (email) {
    tokens.email = email;
    saveTokens(account, tokens);
  }

  console.log(
    `✓ Authenticated! Tokens saved to ${tokenPath(account)}`
  );
  console.log(`  Account: ${account}`);
  if (email) console.log(`  Email: ${email}`);
  console.log(`  Scopes: ${tokens.scope}`);
}

// ─── Status ──────────────────────────────────────────────────────────────────

function status(account: string) {
  migrateOldTokenFile();
  const clientOk = fs.existsSync(CLIENT_CREDENTIALS_PATH);
  const tokens = loadTokens(account);

  console.log(`\n── Google Calendar Auth Status (${account}) ──\n`);
  console.log(
    `  Client credentials: ${clientOk ? "✓ Found" : "✗ Missing"}`
  );
  console.log(`    Path: ${CLIENT_CREDENTIALS_PATH}\n`);

  if (!tokens) {
    console.log("  Tokens: ✗ Not authenticated");
    console.log(
      `    Run: bun run auth.ts login${account !== DEFAULT_ACCOUNT ? ` --account ${account}` : ""}\n`
    );
    return;
  }

  const expired = Date.now() > tokens.expires_at;
  const expiresIn = Math.round((tokens.expires_at - Date.now()) / 1000);

  console.log(`  Tokens: ✓ Found`);
  console.log(`    Path: ${tokenPath(account)}`);
  if (tokens.email) console.log(`    Email: ${tokens.email}`);
  console.log(
    `    Access token: ${expired ? "✗ Expired" : `✓ Valid (${expiresIn}s remaining)`}`
  );
  console.log(`    Refresh token: ✓ Present`);
  console.log(`    Scopes: ${tokens.scope}\n`);
}

// ─── List accounts ───────────────────────────────────────────────────────────

function listAccounts() {
  migrateOldTokenFile();
  ensureDir(TOKENS_DIR);

  const files = fs.readdirSync(TOKENS_DIR).filter((f) => f.endsWith(".json"));

  if (files.length === 0) {
    console.log("\n  No authenticated accounts.\n");
    return;
  }

  console.log(`\n── Authenticated Accounts ──\n`);
  for (const file of files) {
    const account = file.replace(/\.json$/, "");
    const tokens = loadTokens(account);
    if (!tokens) continue;

    const expired = Date.now() > tokens.expires_at;
    const tokenStatus = expired ? "✗ expired" : "✓ valid";
    const emailLabel = tokens.email ? ` (${tokens.email})` : "";
    console.log(`  • ${account}${emailLabel} — access token: ${tokenStatus}`);
  }
  console.log();
}

// ─── Skill config (config.json in skill root) ─────────────────────────────────

interface SkillConfig {
  accounts?: Record<string, { purpose?: string }>;
}

function readSkillConfig(): SkillConfig {
  const p = skillConfigPath();
  if (!fs.existsSync(p)) return {};
  try {
    return JSON.parse(fs.readFileSync(p, "utf-8"));
  } catch {
    return {};
  }
}

function writeSkillConfig(config: SkillConfig) {
  const p = skillConfigPath();
  const dir = path.dirname(p);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(p, JSON.stringify(config, null, 2));
}

// ─── Label (rename) an account ───────────────────────────────────────────────

function labelAccount(
  currentName: string,
  newName: string,
  description?: string
) {
  migrateOldTokenFile();
  const currentPath = tokenPath(currentName);
  const newPath = tokenPath(newName);

  if (!fs.existsSync(currentPath)) {
    console.error(
      `✗ Account '${currentName}' not found. Run 'bun run auth.ts accounts' to see available accounts.`
    );
    process.exit(1);
  }

  if (fs.existsSync(newPath)) {
    console.error(
      `✗ Account '${newName}' already exists. Choose a different name or revoke it first.`
    );
    process.exit(1);
  }

  fs.renameSync(currentPath, newPath);
  console.log(`✓ Renamed account '${currentName}' → '${newName}'`);

  // Update config.json in skill root so agent knows about this account
  const config = readSkillConfig();
  config.accounts = config.accounts ?? {};
  config.accounts[newName] = { purpose: description ?? "" };
  writeSkillConfig(config);
  console.log("  Updated skill config.json");
}

// ─── Refresh ─────────────────────────────────────────────────────────────────

async function forceRefresh(account: string) {
  migrateOldTokenFile();
  const client = loadClientCredentials();
  const tokens = loadTokens(account);
  if (!tokens) {
    console.error(
      `✗ Account '${account}' not authenticated. Run: bun run auth.ts login --account ${account}`
    );
    process.exit(1);
  }
  const refreshed = await refreshAccessToken(
    client,
    tokens.refresh_token,
    account
  );
  console.log(`✓ Token refreshed (${account}).`);
  console.log(
    `  Expires in ${Math.round((refreshed.expires_at - Date.now()) / 1000)}s`
  );
}

// ─── Revoke ──────────────────────────────────────────────────────────────────

async function revoke(account: string) {
  migrateOldTokenFile();
  const tokens = loadTokens(account);
  if (!tokens) {
    console.log(`▸ No tokens to revoke for account '${account}'.`);
    return;
  }

  const res = await fetch(
    `${REVOKE_ENDPOINT}?token=${tokens.refresh_token}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }
  );

  if (res.ok) {
    deleteTokens(account);
    console.log(`✓ Tokens revoked and deleted (${account}).`);
  } else {
    const text = await res.text();
    console.error(`✗ Revocation failed (${res.status}): ${text}`);
    console.log("▸ Deleting local tokens anyway.");
    deleteTokens(account);
  }
}

// ─── Print token ─────────────────────────────────────────────────────────────

async function printToken(account: string) {
  const token = await getAccessToken(account);
  console.log(token);
}

// ─── CLI helpers ─────────────────────────────────────────────────────────────

function getAccountFromArgs(args: string[]): string {
  const idx = args.indexOf("--account");
  if (idx === -1 || idx + 1 >= args.length) return DEFAULT_ACCOUNT;
  return args[idx + 1];
}

// ─── CLI dispatch (only when run directly) ──────────────────────────────────

const isMain =
  process.argv[1] &&
  (process.argv[1].endsWith("auth.ts") ||
    process.argv[1].endsWith("auth"));

if (isMain) {
  const cliArgs = process.argv.slice(2);
  const command = cliArgs[0] ?? "status";
  const account = getAccountFromArgs(cliArgs);

  switch (command) {
    case "login":
      login(account).catch((e) => {
        console.error("✗ Login failed:", e.message);
        process.exit(1);
      });
      break;
    case "status":
      status(account);
      break;
    case "accounts":
      listAccounts();
      break;
    case "label": {
      // Positional args after "label": newName, then optional description (not --account value)
      const positionals = cliArgs.slice(1).filter((a, i, arr) => {
        if (a.startsWith("--")) return false;
        if (i > 0 && arr[i - 1] === "--account") return false;
        return true;
      });
      const newName = positionals[0];
      const description = positionals[1];
      if (!newName) {
        console.error(
          "Usage: bun run auth.ts label <new-name> [description] [--account <current-name>]"
        );
        process.exit(1);
      }
      labelAccount(account, newName, description);
      break;
    }
    case "refresh":
      forceRefresh(account).catch((e) => {
        console.error("✗ Refresh failed:", e.message);
        process.exit(1);
      });
      break;
    case "revoke":
      revoke(account).catch((e) => {
        console.error("✗ Revoke failed:", e.message);
        process.exit(1);
      });
      break;
    case "token":
      printToken(account).catch((e) => {
        console.error("✗ Failed to get token:", e.message);
        process.exit(1);
      });
      break;
    default:
      console.log(
        "Usage: bun run auth.ts <command> [--account <alias>]\n\n" +
          "Commands:\n" +
          "  login                  Start OAuth flow (opens browser)\n" +
          "  status                 Check authentication status\n" +
          "  accounts               List all authenticated accounts\n" +
          "  label <new-name> [desc]  Rename an account; optional desc → config purpose (default: renames 'default')\n" +
          "  refresh                Force-refresh the access token\n" +
          "  revoke                 Revoke tokens and delete credentials\n" +
          "  token                  Print a valid access token\n"
      );
      process.exit(1);
  }
}
