import { Hono } from "hono";
import { serve } from "@hono/node-server";
import crypto from "node:crypto";
import * as db from "./db.js";
import * as storage from "./storage.js";
import * as billing from "./billing.js";
import { verifySignature, computeFingerprint } from "./auth.js";
import type { SignupRequest, RegisterKeyRequest } from "./types.js";

const app = new Hono();

const MAX_VERSIONS = 10;

// ─── Middleware: auth for vault routes ───────────────────────

async function authenticateVault(
  vaultId: string,
  signature: string | undefined,
  payload: string
): Promise<{ ok: true; fingerprint: string } | { ok: false; error: string }> {
  if (!signature) {
    return { ok: false, error: "Missing X-ClawVault-Signature header" };
  }

  const vault = await db.getVault(vaultId);
  if (!vault) {
    return { ok: false, error: "Vault not found" };
  }

  const keys = await db.getActiveKeys(vaultId);
  if (keys.length === 0) {
    return { ok: false, error: "No registered keys" };
  }

  const fingerprint = verifySignature(payload, signature, keys);
  if (!fingerprint) {
    return { ok: false, error: "Invalid signature" };
  }

  return { ok: true, fingerprint };
}

// ─── Health ──────────────────────────────────────────────────

app.get("/v1/health", (c) => {
  return c.json({ status: "ok", version: "1.0.0" });
});

// ─── Signup ──────────────────────────────────────────────────

app.post("/v1/signup", async (c) => {
  const body: SignupRequest = await c.req.json();

  if (!body.email || !body.public_key) {
    return c.json({ error: "email and public_key required" }, 400);
  }

  // Check if already registered
  const existing = await db.getVaultByEmail(body.email);
  if (existing) {
    return c.json({ vault_id: existing.id, status: "existing" });
  }

  // Create vault
  const vault = await db.createVault(body.email);

  // Register key
  const fingerprint = computeFingerprint(body.public_key);
  await db.addKey(
    vault.id,
    body.public_key,
    fingerprint,
    body.hostname || "",
    body.instance_id || ""
  );

  // Create Stripe customer
  const customerId = await billing.createCustomer(body.email, vault.id);
  if (customerId) {
    await db.updateVaultStripe(vault.id, customerId, null);
  }

  return c.json(
    {
      vault_id: vault.id,
      fingerprint,
      status: "created",
    },
    201
  );
});

// ─── Push (upload vault archive) ─────────────────────────────

app.put("/v1/vaults/:id/sync", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const archiveHash = c.req.header("X-ClawVault-Hash") || "";

  const auth = await authenticateVault(vaultId, signature, archiveHash);
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  // Read the archive body
  const body = await c.req.arrayBuffer();
  const data = new Uint8Array(body);

  if (data.length === 0) {
    return c.json({ error: "Empty body" }, 400);
  }

  // Verify hash matches
  const actualHash = crypto
    .createHash("sha256")
    .update(data)
    .digest("hex");
  if (archiveHash && actualHash !== archiveHash) {
    return c.json({ error: "Hash mismatch" }, 400);
  }

  // Generate version ID and upload
  const versionId = crypto.randomUUID();
  const s3Key = await storage.uploadArchive(vaultId, versionId, data);

  // Record in DB
  await db.addVersion(vaultId, s3Key, data.length, actualHash, auth.fingerprint);

  // Prune old versions
  const old = await db.getOldVersions(vaultId, MAX_VERSIONS);
  for (const v of old) {
    await storage.deleteArchive(v.s3_key);
    await db.deleteVersion(v.id);
  }

  // Handle billing
  const vault = await db.getVault(vaultId);
  if (vault?.stripe_customer_id) {
    if (!vault.stripe_subscription_id && data.length > 50 * 1024 * 1024) {
      const subId = await billing.ensureSubscription(
        vault.stripe_customer_id,
        data.length
      );
      if (subId) await db.updateVaultStripe(vaultId, vault.stripe_customer_id, subId);
    }
    if (vault.stripe_subscription_id) {
      await billing.reportUsage(vault.stripe_subscription_id, data.length);
    }
  }

  return c.json({
    status: "ok",
    version_id: versionId,
    size_bytes: data.length,
  }, 201);
});

// ─── Pull (download vault archive) ──────────────────────────

app.get("/v1/vaults/:id/sync", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const timestamp = c.req.header("X-ClawVault-Timestamp") || "";

  const auth = await authenticateVault(
    vaultId,
    signature,
    `pull:${vaultId}:${timestamp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const latest = await db.getLatestVersion(vaultId);
  if (!latest) {
    return c.json({ error: "No vault data" }, 404);
  }

  const data = await storage.downloadArchive(latest.s3_key);
  if (!data) {
    return c.json({ error: "Archive not found in storage" }, 404);
  }

  return new Response(Buffer.from(data), {
    headers: {
      "Content-Type": "application/gzip",
      "X-ClawVault-Hash": latest.hash_sha256,
      "X-ClawVault-Version": latest.id,
    },
  });
});

// ─── Usage ───────────────────────────────────────────────────

app.get("/v1/vaults/:id/usage", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const timestamp = c.req.header("X-ClawVault-Timestamp") || "";

  const auth = await authenticateVault(
    vaultId,
    signature,
    `usage:${vaultId}:${timestamp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const latest = await db.getLatestVersion(vaultId);
  const sizeBytes = latest?.size_bytes ?? 0;
  const instanceCount = await db.getKeyCount(vaultId);
  const versionCount = await db.getVersionCount(vaultId);

  return c.json({
    ...billing.computeBilling(sizeBytes),
    instance_count: instanceCount,
    version_count: versionCount,
  });
});

// ─── Register key ────────────────────────────────────────────

app.post("/v1/vaults/:id/keys", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const body: RegisterKeyRequest = await c.req.json();

  if (!body.public_key) {
    return c.json({ error: "public_key required" }, 400);
  }

  // Auth: the request must be signed by an existing key
  const newFingerprint = computeFingerprint(body.public_key);
  const auth = await authenticateVault(
    vaultId,
    signature,
    `register:${vaultId}:${newFingerprint}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  // Check for duplicate
  const existing = await db.getActiveKeys(vaultId);
  if (existing.some((k) => k.fingerprint === newFingerprint)) {
    return c.json({ fingerprint: newFingerprint, status: "already_registered" });
  }

  await db.addKey(
    vaultId,
    body.public_key,
    newFingerprint,
    body.hostname || "",
    body.instance_id || ""
  );

  return c.json({ fingerprint: newFingerprint, status: "registered" }, 201);
});

// ─── Revoke key ──────────────────────────────────────────────

app.delete("/v1/vaults/:id/keys/:fp", async (c) => {
  const vaultId = c.req.param("id");
  const fp = decodeURIComponent(c.req.param("fp"));
  const signature = c.req.header("X-ClawVault-Signature");

  const auth = await authenticateVault(
    vaultId,
    signature,
    `revoke:${vaultId}:${fp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  // Don't allow revoking the key that's signing this request
  if (auth.fingerprint === fp) {
    return c.json({ error: "Cannot revoke the key used to sign this request" }, 400);
  }

  const revoked = await db.revokeKey(vaultId, fp);
  if (!revoked) {
    return c.json({ error: "Key not found or already revoked" }, 404);
  }

  return c.json({ status: "revoked", fingerprint: fp });
});

// ─── Start ───────────────────────────────────────────────────

const port = parseInt(process.env.PORT || "3000", 10);

await db.migrate();
console.log(`ClawVault Cloud API listening on :${port}`);
serve({ fetch: app.fetch, port });
