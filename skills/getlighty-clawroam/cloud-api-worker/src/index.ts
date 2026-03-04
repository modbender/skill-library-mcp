import { Hono } from "hono";

interface Env {
  DB: D1Database;
  STORAGE: R2Bucket;
  STRIPE_SECRET_KEY?: string;
  STRIPE_PRICE_ID?: string;
  JWT_SECRET: string;
}

const app = new Hono<{ Bindings: Env }>();
const MAX_VERSIONS = 10;

// ─── CORS ────────────────────────────────────────────────────

app.use("*", async (c, next) => {
  if (c.req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-ClawRoam-Signature, X-ClawRoam-Hash, X-ClawRoam-Timestamp",
        "Access-Control-Max-Age": "86400",
      },
    });
  }
  await next();
  c.res.headers.set("Access-Control-Allow-Origin", "*");
});

// ─── JWT helpers ─────────────────────────────────────────────

function b64url(data: string): string {
  return btoa(data).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function b64urlDecode(s: string): string {
  let b = s.replace(/-/g, "+").replace(/_/g, "/");
  while (b.length % 4) b += "=";
  return atob(b);
}

async function signJWT(payload: Record<string, unknown>, secret: string): Promise<string> {
  const header = b64url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const body = b64url(JSON.stringify(payload));
  const data = `${header}.${body}`;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(data));
  return `${data}.${b64url(String.fromCharCode(...new Uint8Array(sig)))}`;
}

async function verifyJWT(token: string, secret: string): Promise<{ vault_id: string; email: string } | null> {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["verify"]);
  const sig = Uint8Array.from(b64urlDecode(parts[2]), (c) => c.charCodeAt(0));
  const valid = await crypto.subtle.verify("HMAC", key, sig, new TextEncoder().encode(`${parts[0]}.${parts[1]}`));
  if (!valid) return null;
  const payload = JSON.parse(b64urlDecode(parts[1]));
  if (payload.exp && payload.exp < Date.now() / 1000) return null;
  return { vault_id: payload.vault_id, email: payload.email };
}

// ─── Ed25519 auth ────────────────────────────────────────────

function sshPubKeyToRaw(sshPubKey: string): Uint8Array {
  const parts = sshPubKey.trim().split(/\s+/);
  if (parts.length < 2 || parts[0] !== "ssh-ed25519") throw new Error("Not Ed25519");
  const keyData = Uint8Array.from(atob(parts[1]), (c) => c.charCodeAt(0));
  let offset = 0;
  const typeLen = new DataView(keyData.buffer).getUint32(offset);
  offset += 4 + typeLen;
  const pubLen = new DataView(keyData.buffer).getUint32(offset);
  offset += 4;
  return keyData.slice(offset, offset + pubLen);
}

async function importEd25519PubKey(rawPub: Uint8Array): Promise<CryptoKey> {
  const prefix = new Uint8Array([0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65, 0x70, 0x03, 0x21, 0x00]);
  const spki = new Uint8Array(prefix.length + rawPub.length);
  spki.set(prefix);
  spki.set(rawPub, prefix.length);
  return crypto.subtle.importKey("spki", spki, { name: "Ed25519" }, false, ["verify"]);
}

async function verifySignature(
  payload: string, signatureBase64: string,
  keys: { public_key: string; fingerprint: string; revoked_at: string | null }[]
): Promise<string | null> {
  const sigBytes = Uint8Array.from(atob(signatureBase64), (c) => c.charCodeAt(0));
  const data = new TextEncoder().encode(payload);
  for (const key of keys) {
    if (key.revoked_at) continue;
    try {
      const pubKey = await importEd25519PubKey(sshPubKeyToRaw(key.public_key));
      if (await crypto.subtle.verify("Ed25519", pubKey, sigBytes, data)) return key.fingerprint;
    } catch { continue; }
  }
  return null;
}

async function computeFingerprintAsync(sshPubKey: string): Promise<string> {
  const parts = sshPubKey.trim().split(/\s+/);
  const keyData = Uint8Array.from(atob(parts[1]), (c) => c.charCodeAt(0));
  const hash = await crypto.subtle.digest("SHA-256", keyData);
  return `SHA256:${btoa(String.fromCharCode(...new Uint8Array(hash))).replace(/=+$/, "")}`;
}

// ─── Dual auth (JWT or Ed25519) ──────────────────────────────

async function authenticateVault(
  db: D1Database, vaultId: string, signature: string | undefined, payload: string
): Promise<{ ok: true; fingerprint: string } | { ok: false; error: string }> {
  if (!signature) return { ok: false, error: "Missing signature" };
  const vault = await db.prepare("SELECT id FROM vaults WHERE id = ?").bind(vaultId).first();
  if (!vault) return { ok: false, error: "Vault not found" };
  const keys = await db.prepare("SELECT public_key, fingerprint, revoked_at FROM vault_keys WHERE vault_id = ? AND revoked_at IS NULL").bind(vaultId).all();
  if (!keys.results.length) return { ok: false, error: "No registered keys" };
  const fp = await verifySignature(payload, signature, keys.results as { public_key: string; fingerprint: string; revoked_at: string | null }[]);
  if (!fp) return { ok: false, error: "Invalid signature" };
  return { ok: true, fingerprint: fp };
}

async function auth(
  db: D1Database, jwtSecret: string, vaultId: string,
  req: { header: (n: string) => string | undefined }, sigPayload: string
): Promise<{ ok: true; fingerprint: string } | { ok: false; error: string }> {
  const bearer = req.header("Authorization");
  if (bearer?.startsWith("Bearer ")) {
    const claims = await verifyJWT(bearer.slice(7), jwtSecret);
    if (!claims) return { ok: false, error: "Invalid token" };
    if (claims.vault_id !== vaultId) return { ok: false, error: "Token vault mismatch" };
    return { ok: true, fingerprint: "dashboard" };
  }
  return authenticateVault(db, vaultId, req.header("X-ClawRoam-Signature"), sigPayload);
}

// ─── Tar/gzip utilities ──────────────────────────────────────

async function decompressGzip(compressed: ArrayBuffer): Promise<Uint8Array> {
  const ds = new DecompressionStream("gzip");
  const writer = ds.writable.getWriter();
  writer.write(compressed);
  writer.close();
  const reader = ds.readable.getReader();
  const chunks: Uint8Array[] = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  const total = chunks.reduce((s, c) => s + c.length, 0);
  const result = new Uint8Array(total);
  let off = 0;
  for (const ch of chunks) { result.set(ch, off); off += ch.length; }
  return result;
}

async function compressGzip(data: Uint8Array): Promise<ArrayBuffer> {
  const cs = new CompressionStream("gzip");
  const writer = cs.writable.getWriter();
  writer.write(data);
  writer.close();
  const reader = cs.readable.getReader();
  const chunks: Uint8Array[] = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  const total = chunks.reduce((s, c) => s + c.length, 0);
  const result = new Uint8Array(total);
  let off = 0;
  for (const ch of chunks) { result.set(ch, off); off += ch.length; }
  return result.buffer;
}

interface TarEntry { name: string; size: number; data: Uint8Array; }

function parseTar(buf: Uint8Array): TarEntry[] {
  const entries: TarEntry[] = [];
  const dec = new TextDecoder();
  let off = 0;
  while (off + 512 <= buf.length) {
    const header = buf.slice(off, off + 512);
    if (header.every((b) => b === 0)) break;
    let name = dec.decode(header.slice(0, 100)).replace(/\0/g, "");
    const sizeStr = dec.decode(header.slice(124, 136)).replace(/\0/g, "").trim();
    const size = parseInt(sizeStr, 8) || 0;
    const type = header[156];
    const prefix = dec.decode(header.slice(345, 500)).replace(/\0/g, "");
    if (prefix) name = prefix + "/" + name;
    name = name.replace(/^\.\//, "");
    off += 512;
    const data = buf.slice(off, off + size);
    off += Math.ceil(size / 512) * 512;
    if (type === 0 || type === 48) entries.push({ name, size, data });
  }
  return entries;
}

function buildTar(entries: TarEntry[]): Uint8Array {
  const enc = new TextEncoder();
  const blocks: Uint8Array[] = [];
  for (const entry of entries) {
    const h = new Uint8Array(512);
    h.set(enc.encode(entry.name).slice(0, 100), 0);
    h.set(enc.encode("0000644\0"), 100);
    h.set(enc.encode("0000000\0"), 108);
    h.set(enc.encode("0000000\0"), 116);
    h.set(enc.encode(entry.size.toString(8).padStart(11, "0") + "\0"), 124);
    h.set(enc.encode(Math.floor(Date.now() / 1000).toString(8).padStart(11, "0") + "\0"), 136);
    h.set(enc.encode("        "), 148);
    h[156] = 48;
    h.set(enc.encode("ustar\0"), 257);
    h.set(enc.encode("00"), 263);
    let cksum = 0;
    for (let i = 0; i < 512; i++) cksum += h[i];
    h.set(enc.encode(cksum.toString(8).padStart(6, "0") + "\0 "), 148);
    blocks.push(h);
    blocks.push(entry.data);
    const pad = 512 - (entry.data.length % 512);
    if (pad < 512) blocks.push(new Uint8Array(pad));
  }
  blocks.push(new Uint8Array(1024));
  const total = blocks.reduce((s, b) => s + b.length, 0);
  const result = new Uint8Array(total);
  let off = 0;
  for (const b of blocks) { result.set(b, off); off += b.length; }
  return result;
}

function categorizeFile(path: string): string {
  if (path.startsWith("identity/")) return "identity";
  if (path.startsWith("knowledge/")) return "knowledge";
  if (/^(config\.yaml|requirements\.yaml|manifest\.json)$/.test(path)) return "config";
  if (path.includes("skills")) return "skills";
  return "other";
}

// ─── Health ──────────────────────────────────────────────────

app.get("/v1/health", (c) => c.json({ status: "ok", version: "3.0.0" }));

// ─── Dashboard auth ──────────────────────────────────────────

app.post("/v1/dashboard/auth", async (c) => {
  const { email, vault_id } = await c.req.json<{ email: string; vault_id: string }>();
  if (!email || !vault_id) return c.json({ error: "email and vault_id required" }, 400);
  const vault = await c.env.DB.prepare("SELECT id, email FROM vaults WHERE id = ? AND email = ?").bind(vault_id, email).first<{ id: string; email: string }>();
  if (!vault) return c.json({ error: "Invalid credentials" }, 401);
  const now = Math.floor(Date.now() / 1000);
  const token = await signJWT({ vault_id, email, iat: now, exp: now + 86400 }, c.env.JWT_SECRET);
  return c.json({ token, vault_id, email, expires_in: 86400 });
});

// ─── Signup ──────────────────────────────────────────────────

app.post("/v1/signup", async (c) => {
  const body = await c.req.json<{ email: string; public_key: string; hostname?: string; os?: string; instance_id?: string }>();
  if (!body.email) return c.json({ error: "email required" }, 400);
  const db = c.env.DB;
  const existing = await db.prepare("SELECT id FROM vaults WHERE email = ?").bind(body.email).first<{ id: string }>();
  if (existing) {
    if (body.public_key) {
      const fp = await computeFingerprintAsync(body.public_key);
      const dup = await db.prepare("SELECT id FROM vault_keys WHERE vault_id = ? AND fingerprint = ? AND revoked_at IS NULL").bind(existing.id, fp).first();
      if (!dup) await db.prepare("INSERT INTO vault_keys (id, vault_id, public_key, fingerprint, hostname, instance_id) VALUES (?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), existing.id, body.public_key, fp, body.hostname || "", body.instance_id || "").run();
    }
    return c.json({ vault_id: existing.id, status: "existing" });
  }
  const vaultId = crypto.randomUUID();
  await db.prepare("INSERT INTO vaults (id, email) VALUES (?, ?)").bind(vaultId, body.email).run();
  let fingerprint = "";
  if (body.public_key) {
    fingerprint = await computeFingerprintAsync(body.public_key);
    await db.prepare("INSERT INTO vault_keys (id, vault_id, public_key, fingerprint, hostname, instance_id) VALUES (?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), vaultId, body.public_key, fingerprint, body.hostname || "", body.instance_id || "").run();
  }
  return c.json({ vault_id: vaultId, fingerprint, status: "created" }, 201);
});

// ─── Legacy push/pull (backward compat) ─────────────────────

app.put("/v1/vaults/:id/sync", async (c) => {
  const vaultId = c.req.param("id");
  const archiveHash = c.req.header("X-ClawRoam-Hash") || "";
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, archiveHash);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const body = await c.req.arrayBuffer();
  if (!body.byteLength) return c.json({ error: "Empty body" }, 400);
  const hashBuf = await crypto.subtle.digest("SHA-256", body);
  const actualHash = [...new Uint8Array(hashBuf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  if (archiveHash && actualHash !== archiveHash) return c.json({ error: "Hash mismatch" }, 400);
  const versionId = crypto.randomUUID();
  const s3Key = `vaults/${vaultId}/${versionId}.tar.gz`;
  await c.env.STORAGE.put(s3Key, body, { httpMetadata: { contentType: "application/gzip" } });
  await c.env.DB.prepare("INSERT INTO vault_versions (id, vault_id, s3_key, size_bytes, hash_sha256, pushed_by) VALUES (?, ?, ?, ?, ?, ?)").bind(versionId, vaultId, s3Key, body.byteLength, actualHash, a.fingerprint).run();
  const old = await c.env.DB.prepare("SELECT id, s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = 'default' ORDER BY created_at DESC LIMIT -1 OFFSET ?").bind(vaultId, MAX_VERSIONS).all<{ id: string; s3_key: string }>();
  for (const v of old.results) { await c.env.STORAGE.delete(v.s3_key); await c.env.DB.prepare("DELETE FROM vault_versions WHERE id = ?").bind(v.id).run(); }
  return c.json({ status: "ok", version_id: versionId, size_bytes: body.byteLength }, 201);
});

app.get("/v1/vaults/:id/sync", async (c) => {
  const vaultId = c.req.param("id");
  const ts = c.req.header("X-ClawRoam-Timestamp") || "";
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `pull:${vaultId}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const latest = await c.env.DB.prepare("SELECT s3_key, hash_sha256, id FROM vault_versions WHERE vault_id = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId).first<{ s3_key: string; hash_sha256: string; id: string }>();
  if (!latest) return c.json({ error: "No vault data" }, 404);
  const obj = await c.env.STORAGE.get(latest.s3_key);
  if (!obj) return c.json({ error: "Archive not found" }, 404);
  return new Response(obj.body, { headers: { "Content-Type": "application/gzip", "X-ClawRoam-Hash": latest.hash_sha256, "X-ClawRoam-Version": latest.id } });
});

// ─── Usage ───────────────────────────────────────────────────

app.get("/v1/vaults/:id/usage", async (c) => {
  const vaultId = c.req.param("id");
  const ts = c.req.header("X-ClawRoam-Timestamp") || "";
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `usage:${vaultId}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const latest = await c.env.DB.prepare("SELECT size_bytes FROM vault_versions WHERE vault_id = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId).first<{ size_bytes: number }>();
  const sizeBytes = latest?.size_bytes ?? 0;
  const usedMb = sizeBytes / 1048576;
  const billableMb = Math.max(0, usedMb - 50);
  const keyCount = await c.env.DB.prepare("SELECT COUNT(*) as c FROM vault_keys WHERE vault_id = ? AND revoked_at IS NULL").bind(vaultId).first<{ c: number }>();
  const verCount = await c.env.DB.prepare("SELECT COUNT(*) as c FROM vault_versions WHERE vault_id = ?").bind(vaultId).first<{ c: number }>();
  return c.json({ used_bytes: sizeBytes, used_mb: Math.round(usedMb * 100) / 100, free_mb: 50, billable_mb: Math.round(billableMb * 100) / 100, monthly_cost: Math.round(billableMb * 0.005 * 100) / 100, instance_count: keyCount?.c ?? 0, version_count: verCount?.c ?? 0 });
});

// ─── Profile push ────────────────────────────────────────────

app.put("/v1/vaults/:id/profiles/:profile/sync", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const archiveHash = c.req.header("X-ClawRoam-Hash") || "";
  if (!/^[a-zA-Z0-9_.-]{1,64}$/.test(profileName)) return c.json({ error: "Invalid profile name" }, 400);
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, archiveHash);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const body = await c.req.arrayBuffer();
  if (!body.byteLength) return c.json({ error: "Empty body" }, 400);
  const hashBuf = await crypto.subtle.digest("SHA-256", body);
  const actualHash = [...new Uint8Array(hashBuf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  if (archiveHash && actualHash !== archiveHash) return c.json({ error: "Hash mismatch" }, 400);
  const versionId = crypto.randomUUID();
  const s3Key = `vaults/${vaultId}/profiles/${profileName}/${versionId}.tar.gz`;
  await c.env.STORAGE.put(s3Key, body, { httpMetadata: { contentType: "application/gzip" } });
  await c.env.DB.prepare("INSERT INTO vault_versions (id, vault_id, s3_key, size_bytes, hash_sha256, pushed_by, profile_name) VALUES (?, ?, ?, ?, ?, ?, ?)").bind(versionId, vaultId, s3Key, body.byteLength, actualHash, a.fingerprint, profileName).run();
  const old = await c.env.DB.prepare("SELECT id, s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT -1 OFFSET ?").bind(vaultId, profileName, MAX_VERSIONS).all<{ id: string; s3_key: string }>();
  for (const v of old.results) { await c.env.STORAGE.delete(v.s3_key); await c.env.DB.prepare("DELETE FROM vault_versions WHERE id = ?").bind(v.id).run(); }
  return c.json({ status: "ok", version_id: versionId, profile: profileName, size_bytes: body.byteLength }, 201);
});

// ─── Profile pull ────────────────────────────────────────────

app.get("/v1/vaults/:id/profiles/:profile/sync", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const ts = c.req.header("X-ClawRoam-Timestamp") || "";
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `pull:${vaultId}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const latest = await c.env.DB.prepare("SELECT s3_key, hash_sha256, id FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId, profileName).first<{ s3_key: string; hash_sha256: string; id: string }>();
  if (!latest) return c.json({ error: "No data for profile" }, 404);
  const obj = await c.env.STORAGE.get(latest.s3_key);
  if (!obj) return c.json({ error: "Archive not found" }, 404);
  return new Response(obj.body, { headers: { "Content-Type": "application/gzip", "X-ClawRoam-Hash": latest.hash_sha256, "X-ClawRoam-Version": latest.id, "X-ClawRoam-Profile": profileName } });
});

// ─── List profiles ───────────────────────────────────────────

app.get("/v1/vaults/:id/profiles", async (c) => {
  const vaultId = c.req.param("id");
  const ts = c.req.header("X-ClawRoam-Timestamp") || "";
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `list-profiles:${vaultId}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const profiles = await c.env.DB.prepare(`
    SELECT profile_name, MAX(created_at) as last_push,
      (SELECT size_bytes FROM vault_versions v2 WHERE v2.vault_id = ? AND v2.profile_name = vault_versions.profile_name ORDER BY v2.created_at DESC LIMIT 1) as size_bytes
    FROM vault_versions WHERE vault_id = ? GROUP BY profile_name ORDER BY last_push DESC
  `).bind(vaultId, vaultId).all<{ profile_name: string; last_push: string; size_bytes: number }>();
  return c.json({ profiles: profiles.results.map((p) => ({ name: p.profile_name, last_push: p.last_push, size_mb: Math.round((p.size_bytes || 0) / 1048576 * 100) / 100 })) });
});

// ─── Profile file listing ────────────────────────────────────

app.get("/v1/vaults/:id/profiles/:profile/files", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `list-files:${vaultId}:${profileName}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const latest = await c.env.DB.prepare("SELECT s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId, profileName).first<{ s3_key: string }>();
  if (!latest) return c.json({ error: "No data for profile" }, 404);
  const obj = await c.env.STORAGE.get(latest.s3_key);
  if (!obj) return c.json({ error: "Archive not found" }, 404);
  const tarData = await decompressGzip(await obj.arrayBuffer());
  const entries = parseTar(tarData);
  const files = entries
    .filter((e) => !e.name.startsWith(".git/") && !e.name.startsWith(".git") && e.name !== ".gitignore" && !e.name.startsWith("sync.log"))
    .map((e) => ({ path: e.name, size: e.size, category: categorizeFile(e.name) }));
  return c.json({ profile: profileName, files });
});

// ─── Profile file read ───────────────────────────────────────

app.get("/v1/vaults/:id/profiles/:profile/file/*", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const filepath = c.req.path.split(`/profiles/${profileName}/file/`)[1];
  if (!filepath) return c.json({ error: "filepath required" }, 400);
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `read-file:${vaultId}:${profileName}:${filepath}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const latest = await c.env.DB.prepare("SELECT s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId, profileName).first<{ s3_key: string }>();
  if (!latest) return c.json({ error: "No data" }, 404);
  const obj = await c.env.STORAGE.get(latest.s3_key);
  if (!obj) return c.json({ error: "Archive not found" }, 404);
  const entries = parseTar(await decompressGzip(await obj.arrayBuffer()));
  const entry = entries.find((e) => e.name === filepath || e.name === "./" + filepath);
  if (!entry) return c.json({ error: "File not found" }, 404);
  return c.json({ path: filepath, content: new TextDecoder().decode(entry.data), size: entry.size });
});

// ─── Copy file between profiles ──────────────────────────────

app.post("/v1/vaults/:id/copy-file", async (c) => {
  const vaultId = c.req.param("id");
  const { source_profile, target_profile, filepath } = await c.req.json<{ source_profile: string; target_profile: string; filepath: string }>();
  if (!source_profile || !target_profile || !filepath) return c.json({ error: "source_profile, target_profile, filepath required" }, 400);
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `copy-file:${vaultId}:${source_profile}:${target_profile}:${filepath}`);
  if (!a.ok) return c.json({ error: a.error }, 401);

  // Get source file
  const srcVer = await c.env.DB.prepare("SELECT s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId, source_profile).first<{ s3_key: string }>();
  if (!srcVer) return c.json({ error: "Source not found" }, 404);
  const srcObj = await c.env.STORAGE.get(srcVer.s3_key);
  if (!srcObj) return c.json({ error: "Source archive not found" }, 404);
  const srcEntries = parseTar(await decompressGzip(await srcObj.arrayBuffer()));
  const srcFile = srcEntries.find((e) => e.name === filepath);
  if (!srcFile) return c.json({ error: "File not found in source" }, 404);

  // Get target archive
  const tgtVer = await c.env.DB.prepare("SELECT s3_key FROM vault_versions WHERE vault_id = ? AND profile_name = ? ORDER BY created_at DESC LIMIT 1").bind(vaultId, target_profile).first<{ s3_key: string }>();
  if (!tgtVer) return c.json({ error: "Target not found" }, 404);
  const tgtObj = await c.env.STORAGE.get(tgtVer.s3_key);
  if (!tgtObj) return c.json({ error: "Target archive not found" }, 404);
  const tgtEntries = parseTar(await decompressGzip(await tgtObj.arrayBuffer()));

  // Replace or add
  const idx = tgtEntries.findIndex((e) => e.name === filepath);
  if (idx >= 0) tgtEntries[idx] = { ...srcFile };
  else tgtEntries.push({ ...srcFile });

  // Re-pack and upload
  const newTar = buildTar(tgtEntries);
  const compressed = await compressGzip(newTar);
  const versionId = crypto.randomUUID();
  const s3Key = `vaults/${vaultId}/profiles/${target_profile}/${versionId}.tar.gz`;
  const hashBuf = await crypto.subtle.digest("SHA-256", compressed);
  const hash = [...new Uint8Array(hashBuf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  await c.env.STORAGE.put(s3Key, compressed, { httpMetadata: { contentType: "application/gzip" } });
  await c.env.DB.prepare("INSERT INTO vault_versions (id, vault_id, s3_key, size_bytes, hash_sha256, pushed_by, profile_name) VALUES (?, ?, ?, ?, ?, ?, ?)").bind(versionId, vaultId, s3Key, compressed.byteLength, hash, "dashboard", target_profile).run();

  return c.json({ status: "ok", filepath, source_profile, target_profile, version_id: versionId });
});

// ─── Register key ────────────────────────────────────────────

app.post("/v1/vaults/:id/keys", async (c) => {
  const vaultId = c.req.param("id");
  const body = await c.req.json<{ public_key: string; hostname?: string; instance_id?: string }>();
  if (!body.public_key) return c.json({ error: "public_key required" }, 400);
  const fp = await computeFingerprintAsync(body.public_key);
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `register:${vaultId}:${fp}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const existing = await c.env.DB.prepare("SELECT id FROM vault_keys WHERE vault_id = ? AND fingerprint = ? AND revoked_at IS NULL").bind(vaultId, fp).first();
  if (existing) return c.json({ fingerprint: fp, status: "already_registered" });
  await c.env.DB.prepare("INSERT INTO vault_keys (id, vault_id, public_key, fingerprint, hostname, instance_id) VALUES (?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), vaultId, body.public_key, fp, body.hostname || "", body.instance_id || "").run();
  return c.json({ fingerprint: fp, status: "registered" }, 201);
});

// ─── Revoke key ──────────────────────────────────────────────

app.delete("/v1/vaults/:id/keys/:fp", async (c) => {
  const vaultId = c.req.param("id");
  const fp = decodeURIComponent(c.req.param("fp"));
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `revoke:${vaultId}:${fp}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  if (a.fingerprint === fp) return c.json({ error: "Cannot revoke the signing key" }, 400);
  const res = await c.env.DB.prepare("UPDATE vault_keys SET revoked_at = datetime('now') WHERE vault_id = ? AND fingerprint = ? AND revoked_at IS NULL").bind(vaultId, fp).run();
  if (!res.meta.changes) return c.json({ error: "Key not found" }, 404);
  return c.json({ status: "revoked", fingerprint: fp });
});

// ─── Sync rules — get ────────────────────────────────────────

app.get("/v1/vaults/:id/profiles/:profile/sync-rules", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const ts = c.req.header("X-ClawRoam-Timestamp") || String(Math.floor(Date.now() / 1000));
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `sync-rules:${vaultId}:${profileName}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const rows = await c.env.DB.prepare(
    "SELECT path FROM sync_rules WHERE vault_id = ? AND profile_name = ? ORDER BY path"
  ).bind(vaultId, profileName).all<{ path: string }>();
  return c.json({ excluded: rows.results.map(r => r.path) });
});

// ─── Sync rules — update ─────────────────────────────────────

app.put("/v1/vaults/:id/profiles/:profile/sync-rules", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const ts = c.req.header("X-ClawRoam-Timestamp") || String(Math.floor(Date.now() / 1000));
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `sync-rules:${vaultId}:${profileName}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const body = await c.req.json<{ excluded: string[] }>();
  if (!Array.isArray(body.excluded)) return c.json({ error: "excluded must be an array" }, 400);
  const paths = body.excluded.filter(p => typeof p === "string" && p.length > 0 && p.length < 512);
  await c.env.DB.prepare(
    "DELETE FROM sync_rules WHERE vault_id = ? AND profile_name = ?"
  ).bind(vaultId, profileName).run();
  for (const path of paths) {
    await c.env.DB.prepare(
      "INSERT OR IGNORE INTO sync_rules (id, vault_id, profile_name, path) VALUES (?, ?, ?, ?)"
    ).bind(crypto.randomUUID(), vaultId, profileName, path).run();
  }
  return c.json({ status: "ok", excluded_count: paths.length });
});

export default app;
