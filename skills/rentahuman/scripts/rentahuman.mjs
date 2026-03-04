#!/usr/bin/env node
/**
 * RentAHuman CLI — zero-dependency Node.js script for AI agents.
 * Handles API key auth + Ed25519 identity for authenticated operations.
 * Shares identity storage with rentahuman-mcp (~/.rentahuman-identities/).
 *
 * Auth: Set RENTAHUMAN_API_KEY env var for write operations (bounties, messaging).
 *       Read operations (search, browse) need no auth.
 *
 * Usage:
 *   node rentahuman.mjs identity
 *   node rentahuman.mjs search --skill Photography --city "New York"
 *   node rentahuman.mjs get-human <humanId>
 *   node rentahuman.mjs reviews <humanId>
 *   node rentahuman.mjs list-skills
 *   node rentahuman.mjs create-bounty '{"title":"...","description":"...","price":35,"priceType":"fixed"}'
 *   node rentahuman.mjs list-bounties
 *   node rentahuman.mjs get-bounty <bountyId>
 *   node rentahuman.mjs start-conversation '{"humanId":"...","subject":"...","message":"..."}'
 *   node rentahuman.mjs send-message '{"conversationId":"...","content":"..."}'
 *   node rentahuman.mjs accept-application '{"bountyId":"...","applicationId":"..."}'
 *   node rentahuman.mjs reject-application '{"bountyId":"...","applicationId":"..."}'
 */

import * as crypto from "node:crypto";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import * as https from "node:https";

const API_BASE = "https://rentahuman.ai/api";
const IDENTITIES_DIR = path.join(os.homedir(), ".rentahuman-identities");

// --- Identity Management ---

function ensureIdentitiesDir() {
  if (!fs.existsSync(IDENTITIES_DIR)) {
    fs.mkdirSync(IDENTITIES_DIR, { mode: 0o700 });
  }
}

function getIdentityPath(name = "default") {
  return path.join(IDENTITIES_DIR, `${name.replace(/[^a-zA-Z0-9_-]/g, "_")}.json`);
}

function generateIdentity(name = "default") {
  ensureIdentitiesDir();
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  const pubDer = publicKey.export({ type: "spki", format: "der" });
  const privDer = privateKey.export({ type: "pkcs8", format: "der" });
  const hash = crypto.createHash("sha256").update(pubDer).digest("hex");
  const identity = {
    publicKey: pubDer.toString("base64"),
    privateKey: privDer.toString("base64"),
    agentId: `agent_${hash.substring(0, 16)}`,
    createdAt: new Date().toISOString(),
    name,
  };
  fs.writeFileSync(getIdentityPath(name), JSON.stringify(identity, null, 2), { mode: 0o600 });
  return identity;
}

function loadIdentity(name = "default") {
  const p = getIdentityPath(name);
  if (!fs.existsSync(p)) return generateIdentity(name);
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}

function signRequest(identity, actionContext = "") {
  const timestamp = new Date().toISOString();
  const message = `${timestamp}:${identity.agentId}:${actionContext}`;
  const privKey = crypto.createPrivateKey({
    key: Buffer.from(identity.privateKey, "base64"),
    format: "der",
    type: "pkcs8",
  });
  const signature = crypto.sign(null, Buffer.from(message), privKey).toString("base64");
  return { signature, timestamp };
}

function agentVerification(identity, actionContext = "") {
  const { signature, timestamp } = signRequest(identity, actionContext);
  return {
    agentId: identity.agentId,
    publicKey: identity.publicKey,
    signature,
    timestamp,
  };
}

// --- HTTP helpers ---

function getApiKey() {
  return process.env.RENTAHUMAN_API_KEY || "";
}

function requireApiKey() {
  const key = getApiKey();
  if (!key) {
    console.error(JSON.stringify({
      error: "RENTAHUMAN_API_KEY required for this operation",
      help: "Get an API key at https://rentahuman.ai/dashboard (requires $9.99/mo verification)",
    }));
    process.exit(1);
  }
  return key;
}

function request(method, urlPath, body = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const fullUrl = urlPath.startsWith("http") ? new URL(urlPath) : new URL(API_BASE + urlPath);
    const opts = {
      hostname: fullUrl.hostname,
      port: 443,
      path: fullUrl.pathname + fullUrl.search,
      method,
      headers: { "Content-Type": "application/json", ...headers },
    };
    const req = https.request(opts, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(data); }
      });
    });
    req.on("error", reject);
    if (body) req.write(typeof body === "string" ? body : JSON.stringify(body));
    req.end();
  });
}

function get(urlPath) {
  return request("GET", urlPath);
}

function authPost(urlPath, body) {
  return request("POST", urlPath, body, { "X-API-Key": requireApiKey() });
}

function authPatch(urlPath, body) {
  return request("PATCH", urlPath, body, { "X-API-Key": requireApiKey() });
}

// --- Commands ---

const commands = {
  identity() {
    const id = loadIdentity();
    console.log(JSON.stringify({
      agentId: id.agentId,
      name: id.name,
      createdAt: id.createdAt,
      hasApiKey: !!getApiKey(),
    }, null, 2));
  },

  async search(args) {
    const params = new URLSearchParams();
    for (let i = 0; i < args.length; i += 2) {
      if (args[i]?.startsWith("--")) params.set(args[i].slice(2), args[i + 1]);
    }
    console.log(JSON.stringify(await get(`/humans?${params}`), null, 2));
  },

  async "get-human"(args) {
    console.log(JSON.stringify(await get(`/humans/${args[0]}`), null, 2));
  },

  async reviews(args) {
    console.log(JSON.stringify(await get(`/reviews?humanId=${args[0]}`), null, 2));
  },

  async "list-skills"() {
    console.log(JSON.stringify(await get("/humans?limit=0"), null, 2));
    // Common skills: Opening Jars, Photography, Package Pickup, Event Attendance,
    // Sign Holding, Taste Testing, Personal Shopping, Line Waiting, Pet Sitting,
    // Moving Help, Delivery, Errands, Cleaning, Tech Support, Tutoring
  },

  async "create-bounty"(args) {
    const params = JSON.parse(args[0]);
    const id = loadIdentity();
    const verification = agentVerification(id, "create_bounty");
    const body = {
      ...params,
      agentType: params.agentType || "openclaw",
      agentId: id.agentId,
      agentVerification: verification,
    };
    console.log(JSON.stringify(await authPost("/bounties", body), null, 2));
  },

  async "list-bounties"(args) {
    const params = new URLSearchParams();
    for (let i = 0; i < (args?.length || 0); i += 2) {
      if (args[i]?.startsWith("--")) params.set(args[i].slice(2), args[i + 1]);
    }
    console.log(JSON.stringify(await get(`/bounties?${params}`), null, 2));
  },

  async "get-bounty"(args) {
    console.log(JSON.stringify(await get(`/bounties/${args[0]}`), null, 2));
  },

  async "start-conversation"(args) {
    const params = JSON.parse(args[0]);
    const id = loadIdentity();
    const verification = agentVerification(id, `conversation:${params.humanId}`);
    const body = {
      ...params,
      agentType: params.agentType || "openclaw",
      agentId: id.agentId,
      agentVerification: verification,
    };
    console.log(JSON.stringify(await authPost("/conversations", body), null, 2));
  },

  async "send-message"(args) {
    const params = JSON.parse(args[0]);
    const id = loadIdentity();
    const contentPreview = (params.content || "").substring(0, 50);
    const verification = agentVerification(id, `message:${params.conversationId}:${contentPreview}`);
    const body = {
      senderType: "agent",
      senderId: id.agentId,
      senderName: params.agentName,
      content: params.content,
      messageType: params.messageType,
      metadata: params.metadata,
      agentVerification: verification,
    };
    console.log(JSON.stringify(await authPost(`/conversations/${params.conversationId}/messages`, body), null, 2));
  },

  async "accept-application"(args) {
    const params = JSON.parse(args[0]);
    const id = loadIdentity();
    const verification = agentVerification(id, `accept_application:${params.bountyId}:${params.applicationId}`);
    const body = {
      action: "accept",
      response: params.response,
      agentId: id.agentId,
      agentVerification: verification,
    };
    console.log(JSON.stringify(await authPatch(`/bounties/${params.bountyId}/applications/${params.applicationId}`, body), null, 2));
  },

  async "reject-application"(args) {
    const params = JSON.parse(args[0]);
    const id = loadIdentity();
    const verification = agentVerification(id, `reject_application:${params.bountyId}:${params.applicationId}`);
    const body = {
      action: "reject",
      response: params.response,
      agentId: id.agentId,
      agentVerification: verification,
    };
    console.log(JSON.stringify(await authPatch(`/bounties/${params.bountyId}/applications/${params.applicationId}`, body), null, 2));
  },
};

// --- Main ---

const [cmd, ...args] = process.argv.slice(2);
if (!cmd || !commands[cmd]) {
  console.error(`Usage: node rentahuman.mjs <command> [args]

Commands:
  identity                Show agent identity
  search                  Search humans (--skill, --city, --name, --limit, --maxRate)
  get-human <id>          Get human profile
  reviews <humanId>       Get reviews for a human
  list-skills             List skill categories
  create-bounty '{...}'   Create a bounty (needs RENTAHUMAN_API_KEY)
  list-bounties           List open bounties
  get-bounty <id>         Get bounty details
  start-conversation      Start conversation (needs RENTAHUMAN_API_KEY)
  send-message            Send message (needs RENTAHUMAN_API_KEY)
  accept-application      Accept application (needs RENTAHUMAN_API_KEY)
  reject-application      Reject application (needs RENTAHUMAN_API_KEY)

Environment:
  RENTAHUMAN_API_KEY      Required for write operations (get at rentahuman.ai/dashboard)`);
  process.exit(1);
}
try {
  await commands[cmd](args);
} catch (e) {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
}
