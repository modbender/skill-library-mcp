import { Hono } from "hono";

interface Env {
  DB: D1Database;
  STORAGE: R2Bucket;
  STRIPE_SECRET_KEY?: string;
  STRIPE_PRICE_ID?: string;
}

const app = new Hono<{ Bindings: Env }>();

const MAX_VERSIONS = 10;

// ─── Auth: Ed25519 signature verification ────────────────────

function sshPubKeyToRaw(sshPubKey: string): Uint8Array {
  const parts = sshPubKey.trim().split(/\s+/);
  if (parts.length < 2 || parts[0] !== "ssh-ed25519") {
    throw new Error("Not an Ed25519 SSH public key");
  }
  const keyData = Uint8Array.from(atob(parts[1]), (c) => c.charCodeAt(0));
  // SSH wire: uint32 len + "ssh-ed25519" + uint32 len + 32-byte key
  let offset = 0;
  const typeLen = new DataView(keyData.buffer).getUint32(offset);
  offset += 4 + typeLen;
  const pubLen = new DataView(keyData.buffer).getUint32(offset);
  offset += 4;
  return keyData.slice(offset, offset + pubLen);
}

async function importEd25519PubKey(rawPub: Uint8Array): Promise<CryptoKey> {
  // SPKI wrapper for Ed25519: 302a300506032b6570032100 + 32 bytes
  const prefix = new Uint8Array([
    0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65, 0x70, 0x03, 0x21, 0x00,
  ]);
  const spki = new Uint8Array(prefix.length + rawPub.length);
  spki.set(prefix);
  spki.set(rawPub, prefix.length);
  return crypto.subtle.importKey("spki", spki, { name: "Ed25519" }, false, [
    "verify",
  ]);
}

async function verifySignature(
  payload: string,
  signatureBase64: string,
  keys: { public_key: string; fingerprint: string; revoked_at: string | null }[]
): Promise<string | null> {
  const sigBytes = Uint8Array.from(atob(signatureBase64), (c) =>
    c.charCodeAt(0)
  );
  const data = new TextEncoder().encode(payload);

  for (const key of keys) {
    if (key.revoked_at) continue;
    try {
      const rawPub = sshPubKeyToRaw(key.public_key);
      const pubKey = await importEd25519PubKey(rawPub);
      const valid = await crypto.subtle.verify("Ed25519", pubKey, sigBytes, data);
      if (valid) return key.fingerprint;
    } catch {
      continue;
    }
  }
  return null;
}

function computeFingerprint(sshPubKey: string): string {
  const parts = sshPubKey.trim().split(/\s+/);
  if (parts.length < 2) throw new Error("Invalid SSH public key");
  const keyData = Uint8Array.from(atob(parts[1]), (c) => c.charCodeAt(0));
  // SHA256 fingerprint
  // We'll compute it and return in the response
  return "pending"; // Computed async below
}

async function computeFingerprintAsync(sshPubKey: string): Promise<string> {
  const parts = sshPubKey.trim().split(/\s+/);
  const keyData = Uint8Array.from(atob(parts[1]), (c) => c.charCodeAt(0));
  const hash = await crypto.subtle.digest("SHA-256", keyData);
  const b64 = btoa(String.fromCharCode(...new Uint8Array(hash)));
  return `SHA256:${b64.replace(/=+$/, "")}`;
}

async function authenticateVault(
  db: D1Database,
  vaultId: string,
  signature: string | undefined,
  payload: string
): Promise<{ ok: true; fingerprint: string } | { ok: false; error: string }> {
  if (!signature) return { ok: false, error: "Missing X-ClawVault-Signature" };

  const vault = await db
    .prepare("SELECT id FROM vaults WHERE id = ?")
    .bind(vaultId)
    .first();
  if (!vault) return { ok: false, error: "Vault not found" };

  const keys = await db
    .prepare(
      "SELECT public_key, fingerprint, revoked_at FROM vault_keys WHERE vault_id = ? AND revoked_at IS NULL"
    )
    .bind(vaultId)
    .all();
  if (!keys.results.length)
    return { ok: false, error: "No registered keys" };

  const fp = await verifySignature(
    payload,
    signature,
    keys.results as { public_key: string; fingerprint: string; revoked_at: string | null }[]
  );
  if (!fp) return { ok: false, error: "Invalid signature" };
  return { ok: true, fingerprint: fp };
}

// ─── Health ──────────────────────────────────────────────────

app.get("/v1/health", (c) => c.json({ status: "ok", version: "1.0.0" }));


// ─── Signup ──────────────────────────────────────────────────

app.post("/v1/signup", async (c) => {
  const body = await c.req.json<{
    email: string;
    public_key: string;
    hostname?: string;
    os?: string;
    instance_id?: string;
  }>();

  if (!body.email) return c.json({ error: "email required" }, 400);

  const db = c.env.DB;

  // Check existing
  const existing = await db
    .prepare("SELECT id FROM vaults WHERE email = ?")
    .bind(body.email)
    .first<{ id: string }>();
  if (existing) {
    // Register new key if provided and not already registered
    if (body.public_key) {
      const fp = await computeFingerprintAsync(body.public_key);
      const dup = await db
        .prepare("SELECT id FROM vault_keys WHERE vault_id = ? AND fingerprint = ? AND revoked_at IS NULL")
        .bind(existing.id, fp)
        .first();
      if (!dup) {
        await db
          .prepare("INSERT INTO vault_keys (id, vault_id, public_key, fingerprint, hostname, instance_id) VALUES (?, ?, ?, ?, ?, ?)")
          .bind(crypto.randomUUID(), existing.id, body.public_key, fp, body.hostname || "", body.instance_id || "")
          .run();
      }
    }
    return c.json({ vault_id: existing.id, status: "existing" });
  }

  // Create vault
  const vaultId = crypto.randomUUID();
  await db
    .prepare("INSERT INTO vaults (id, email) VALUES (?, ?)")
    .bind(vaultId, body.email)
    .run();

  // Register key if provided
  let fingerprint = "";
  if (body.public_key) {
    fingerprint = await computeFingerprintAsync(body.public_key);
    await db
      .prepare(
        "INSERT INTO vault_keys (id, vault_id, public_key, fingerprint, hostname, instance_id) VALUES (?, ?, ?, ?, ?, ?)"
      )
      .bind(
        crypto.randomUUID(),
        vaultId,
        body.public_key,
        fingerprint,
        body.hostname || "",
        body.instance_id || ""
      )
      .run();
  }

  return c.json({ vault_id: vaultId, fingerprint, status: "created" }, 201);
});

// ─── Push ────────────────────────────────────────────────────

app.put("/v1/vaults/:id/sync", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const archiveHash = c.req.header("X-ClawVault-Hash") || "";

  const auth = await authenticateVault(c.env.DB, vaultId, signature, archiveHash);
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const body = await c.req.arrayBuffer();
  if (!body.byteLength) return c.json({ error: "Empty body" }, 400);

  // Verify hash
  const hashBuf = await crypto.subtle.digest("SHA-256", body);
  const actualHash = [...new Uint8Array(hashBuf)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  if (archiveHash && actualHash !== archiveHash)
    return c.json({ error: "Hash mismatch" }, 400);

  const versionId = crypto.randomUUID();
  const s3Key = `vaults/${vaultId}/${versionId}.tar.gz`;

  // Upload to R2
  await c.env.STORAGE.put(s3Key, body, {
    httpMetadata: { contentType: "application/gzip" },
  });

  // Record in DB
  await c.env.DB
    .prepare(
      "INSERT INTO vault_versions (id, vault_id, s3_key, size_bytes, hash_sha256, pushed_by) VALUES (?, ?, ?, ?, ?, ?)"
    )
    .bind(versionId, vaultId, s3Key, body.byteLength, actualHash, auth.fingerprint)
    .run();

  // Prune old versions
  const old = await c.env.DB
    .prepare(
      "SELECT id, s3_key FROM vault_versions WHERE vault_id = ? ORDER BY created_at DESC LIMIT -1 OFFSET ?"
    )
    .bind(vaultId, MAX_VERSIONS)
    .all<{ id: string; s3_key: string }>();

  for (const v of old.results) {
    await c.env.STORAGE.delete(v.s3_key);
    await c.env.DB.prepare("DELETE FROM vault_versions WHERE id = ?").bind(v.id).run();
  }

  return c.json({ status: "ok", version_id: versionId, size_bytes: body.byteLength }, 201);
});

// ─── Pull ────────────────────────────────────────────────────

app.get("/v1/vaults/:id/sync", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const timestamp = c.req.header("X-ClawVault-Timestamp") || "";

  const auth = await authenticateVault(
    c.env.DB, vaultId, signature, `pull:${vaultId}:${timestamp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const latest = await c.env.DB
    .prepare(
      "SELECT s3_key, hash_sha256, id FROM vault_versions WHERE vault_id = ? ORDER BY created_at DESC LIMIT 1"
    )
    .bind(vaultId)
    .first<{ s3_key: string; hash_sha256: string; id: string }>();

  if (!latest) return c.json({ error: "No vault data" }, 404);

  const obj = await c.env.STORAGE.get(latest.s3_key);
  if (!obj) return c.json({ error: "Archive not found" }, 404);

  return new Response(obj.body, {
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
    c.env.DB, vaultId, signature, `usage:${vaultId}:${timestamp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const latest = await c.env.DB
    .prepare(
      "SELECT size_bytes FROM vault_versions WHERE vault_id = ? ORDER BY created_at DESC LIMIT 1"
    )
    .bind(vaultId)
    .first<{ size_bytes: number }>();

  const sizeBytes = latest?.size_bytes ?? 0;
  const usedMb = sizeBytes / (1024 * 1024);
  const billableMb = Math.max(0, usedMb - 50);

  const keyCount = await c.env.DB
    .prepare("SELECT COUNT(*) as c FROM vault_keys WHERE vault_id = ? AND revoked_at IS NULL")
    .bind(vaultId)
    .first<{ c: number }>();

  const verCount = await c.env.DB
    .prepare("SELECT COUNT(*) as c FROM vault_versions WHERE vault_id = ?")
    .bind(vaultId)
    .first<{ c: number }>();

  return c.json({
    used_bytes: sizeBytes,
    used_mb: Math.round(usedMb * 100) / 100,
    free_mb: 50,
    billable_mb: Math.round(billableMb * 100) / 100,
    monthly_cost: Math.round(billableMb * 0.005 * 100) / 100,
    instance_count: keyCount?.c ?? 0,
    version_count: verCount?.c ?? 0,
  });
});

// ─── Profile Push ────────────────────────────────────────────

app.put("/v1/vaults/:id/profiles/:profile/sync", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const signature = c.req.header("X-ClawVault-Signature");
  const archiveHash = c.req.header("X-ClawVault-Hash") || "";

  if (!/^[a-zA-Z0-9_.-]{1,64}$/.test(profileName))
    return c.json({ error: "Invalid profile name" }, 400);

  const auth = await authenticateVault(c.env.DB, vaultId, signature, archiveHash);
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const body = await c.req.arrayBuffer();
  if (!body.byteLength) return c.json({ error: "Empty body" }, 400);

  const hashBuf = await crypto.subtle.digest("SHA-256", body);
  const actualHash = [...new Uint8Array(hashBuf)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  if (archiveHash && actualHash !== archiveHash)
    return c.json({ error: "Hash mismatch" }, 400);

  const versionId = crypto.randomUUID();
  const s3Key = `vaults/${vaultId}/profiles/${profileName}/${versionId}.tar.gz`;

  await c.env.STORAGE.put(s3Key, body, {
    httpMetadata: { contentType: "application/gzip" },
  });

  await c.env.DB
    .prepare(
      "INSERT INTO vault_versions (id, vault_id, s3_key, size_bytes, hash_sha256, pushed_by, profile_name) VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
    .bind(versionId, vaultId, s3Key, body.byteLength, actualHash, auth.fingerprint, profileName)
    .run();

  // Prune old versions for this profile only
  const old = await c.env.DB
    .prepare(
      "SELECT id, s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT -1 OFFSET ?"
    )
    .bind(vaultId, profileName, MAX_VERSIONS)
    .all<{ id: string; s3_key: string }>();

  for (const v of old.results) {
    await c.env.STORAGE.delete(v.s3_key);
    await c.env.DB.prepare("DELETE FROM vault_versions WHERE id = ?").bind(v.id).run();
  }

  return c.json({ status: "ok", version_id: versionId, profile: profileName, size_bytes: body.byteLength }, 201);
});

// ─── Profile Pull ────────────────────────────────────────────

app.get("/v1/vaults/:id/profiles/:profile/sync", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const signature = c.req.header("X-ClawVault-Signature");
  const timestamp = c.req.header("X-ClawVault-Timestamp") || "";

  const auth = await authenticateVault(
    c.env.DB, vaultId, signature, `pull:${vaultId}:${timestamp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const latest = await c.env.DB
    .prepare(
      "SELECT s3_key, hash_sha256, id FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT 1"
    )
    .bind(vaultId, profileName)
    .first<{ s3_key: string; hash_sha256: string; id: string }>();

  if (!latest) return c.json({ error: "No data for profile" }, 404);

  const obj = await c.env.STORAGE.get(latest.s3_key);
  if (!obj) return c.json({ error: "Archive not found" }, 404);

  return new Response(obj.body, {
    headers: {
      "Content-Type": "application/gzip",
      "X-ClawVault-Hash": latest.hash_sha256,
      "X-ClawVault-Version": latest.id,
      "X-ClawVault-Profile": profileName,
    },
  });
});

// ─── List Profiles ───────────────────────────────────────────

app.get("/v1/vaults/:id/profiles", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const timestamp = c.req.header("X-ClawVault-Timestamp") || "";

  const auth = await authenticateVault(
    c.env.DB, vaultId, signature, `list-profiles:${vaultId}:${timestamp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  const profiles = await c.env.DB
    .prepare(`
      SELECT profile_name,
             MAX(created_at) as last_push,
             (SELECT size_bytes FROM vault_versions v2
              WHERE v2.vault_id = ? AND v2.profile_name = vault_versions.profile_name
              ORDER BY v2.created_at DESC LIMIT 1) as size_bytes
      FROM vault_versions
      WHERE vault_id = ?
      GROUP BY profile_name
      ORDER BY last_push DESC
    `)
    .bind(vaultId, vaultId)
    .all<{ profile_name: string; last_push: string; size_bytes: number }>();

  return c.json({
    profiles: profiles.results.map((p) => ({
      name: p.profile_name,
      last_push: p.last_push,
      size_mb: Math.round((p.size_bytes || 0) / 1048576 * 100) / 100,
    })),
  });
});

// ─── Register key ────────────────────────────────────────────

app.post("/v1/vaults/:id/keys", async (c) => {
  const vaultId = c.req.param("id");
  const signature = c.req.header("X-ClawVault-Signature");
  const body = await c.req.json<{
    public_key: string;
    hostname?: string;
    instance_id?: string;
  }>();

  if (!body.public_key) return c.json({ error: "public_key required" }, 400);

  const fp = await computeFingerprintAsync(body.public_key);

  const auth = await authenticateVault(
    c.env.DB, vaultId, signature, `register:${vaultId}:${fp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  // Check duplicate
  const existing = await c.env.DB
    .prepare(
      "SELECT id FROM vault_keys WHERE vault_id = ? AND fingerprint = ? AND revoked_at IS NULL"
    )
    .bind(vaultId, fp)
    .first();
  if (existing) return c.json({ fingerprint: fp, status: "already_registered" });

  await c.env.DB
    .prepare(
      "INSERT INTO vault_keys (id, vault_id, public_key, fingerprint, hostname, instance_id) VALUES (?, ?, ?, ?, ?, ?)"
    )
    .bind(crypto.randomUUID(), vaultId, body.public_key, fp, body.hostname || "", body.instance_id || "")
    .run();

  return c.json({ fingerprint: fp, status: "registered" }, 201);
});

// ─── Revoke key ──────────────────────────────────────────────

app.delete("/v1/vaults/:id/keys/:fp", async (c) => {
  const vaultId = c.req.param("id");
  const fp = decodeURIComponent(c.req.param("fp"));
  const signature = c.req.header("X-ClawVault-Signature");

  const auth = await authenticateVault(
    c.env.DB, vaultId, signature, `revoke:${vaultId}:${fp}`
  );
  if (!auth.ok) return c.json({ error: auth.error }, 401);

  if (auth.fingerprint === fp)
    return c.json({ error: "Cannot revoke the signing key" }, 400);

  const res = await c.env.DB
    .prepare(
      "UPDATE vault_keys SET revoked_at = datetime('now') WHERE vault_id = ? AND fingerprint = ? AND revoked_at IS NULL"
    )
    .bind(vaultId, fp)
    .run();

  if (!res.meta.changes) return c.json({ error: "Key not found" }, 404);
  return c.json({ status: "revoked", fingerprint: fp });
});

export default app;
