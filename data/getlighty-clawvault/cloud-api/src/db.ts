import pg from "pg";
import type { Vault, VaultKey, VaultVersion } from "./types.js";

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl:
    process.env.NODE_ENV === "production"
      ? { rejectUnauthorized: false }
      : undefined,
});

// ─── Migrations ──────────────────────────────────────────────

export async function migrate() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS vaults (
      id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      email           TEXT UNIQUE NOT NULL,
      stripe_customer_id    TEXT,
      stripe_subscription_id TEXT,
      created_at      TIMESTAMPTZ DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS vault_keys (
      id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      vault_id        UUID NOT NULL REFERENCES vaults(id),
      public_key      TEXT NOT NULL,
      fingerprint     TEXT NOT NULL,
      hostname        TEXT NOT NULL DEFAULT '',
      instance_id     TEXT NOT NULL DEFAULT '',
      registered_at   TIMESTAMPTZ DEFAULT now(),
      revoked_at      TIMESTAMPTZ
    );

    CREATE TABLE IF NOT EXISTS vault_versions (
      id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      vault_id        UUID NOT NULL REFERENCES vaults(id),
      s3_key          TEXT NOT NULL,
      size_bytes      BIGINT NOT NULL DEFAULT 0,
      hash_sha256     TEXT NOT NULL,
      pushed_by       TEXT NOT NULL DEFAULT '',
      created_at      TIMESTAMPTZ DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_vault_keys_vault ON vault_keys(vault_id);
    CREATE INDEX IF NOT EXISTS idx_vault_versions_vault ON vault_versions(vault_id);
  `);
}

// ─── Vaults ──────────────────────────────────────────────────

export async function createVault(email: string): Promise<Vault> {
  const res = await pool.query(
    `INSERT INTO vaults (email) VALUES ($1) RETURNING *`,
    [email]
  );
  return res.rows[0];
}

export async function getVault(id: string): Promise<Vault | null> {
  const res = await pool.query(`SELECT * FROM vaults WHERE id = $1`, [id]);
  return res.rows[0] ?? null;
}

export async function getVaultByEmail(email: string): Promise<Vault | null> {
  const res = await pool.query(`SELECT * FROM vaults WHERE email = $1`, [
    email,
  ]);
  return res.rows[0] ?? null;
}

export async function updateVaultStripe(
  id: string,
  customerId: string,
  subscriptionId: string | null
) {
  await pool.query(
    `UPDATE vaults SET stripe_customer_id = $2, stripe_subscription_id = $3 WHERE id = $1`,
    [id, customerId, subscriptionId]
  );
}

// ─── Keys ────────────────────────────────────────────────────

export async function addKey(
  vaultId: string,
  publicKey: string,
  fingerprint: string,
  hostname: string,
  instanceId: string
): Promise<VaultKey> {
  const res = await pool.query(
    `INSERT INTO vault_keys (vault_id, public_key, fingerprint, hostname, instance_id)
     VALUES ($1, $2, $3, $4, $5) RETURNING *`,
    [vaultId, publicKey, fingerprint, hostname, instanceId]
  );
  return res.rows[0];
}

export async function getActiveKeys(vaultId: string): Promise<VaultKey[]> {
  const res = await pool.query(
    `SELECT * FROM vault_keys WHERE vault_id = $1 AND revoked_at IS NULL`,
    [vaultId]
  );
  return res.rows;
}

export async function revokeKey(
  vaultId: string,
  fingerprint: string
): Promise<boolean> {
  const res = await pool.query(
    `UPDATE vault_keys SET revoked_at = now()
     WHERE vault_id = $1 AND fingerprint = $2 AND revoked_at IS NULL`,
    [vaultId, fingerprint]
  );
  return (res.rowCount ?? 0) > 0;
}

// ─── Versions ────────────────────────────────────────────────

export async function addVersion(
  vaultId: string,
  s3Key: string,
  sizeBytes: number,
  hashSha256: string,
  pushedBy: string
): Promise<VaultVersion> {
  const res = await pool.query(
    `INSERT INTO vault_versions (vault_id, s3_key, size_bytes, hash_sha256, pushed_by)
     VALUES ($1, $2, $3, $4, $5) RETURNING *`,
    [vaultId, s3Key, sizeBytes, hashSha256, pushedBy]
  );
  return res.rows[0];
}

export async function getLatestVersion(
  vaultId: string
): Promise<VaultVersion | null> {
  const res = await pool.query(
    `SELECT * FROM vault_versions WHERE vault_id = $1 ORDER BY created_at DESC LIMIT 1`,
    [vaultId]
  );
  return res.rows[0] ?? null;
}

export async function getVersionCount(vaultId: string): Promise<number> {
  const res = await pool.query(
    `SELECT COUNT(*) as count FROM vault_versions WHERE vault_id = $1`,
    [vaultId]
  );
  return parseInt(res.rows[0].count, 10);
}

export async function getOldVersions(
  vaultId: string,
  keepCount: number
): Promise<VaultVersion[]> {
  const res = await pool.query(
    `SELECT * FROM vault_versions WHERE vault_id = $1
     ORDER BY created_at DESC OFFSET $2`,
    [vaultId, keepCount]
  );
  return res.rows;
}

export async function deleteVersion(id: string) {
  await pool.query(`DELETE FROM vault_versions WHERE id = $1`, [id]);
}

export async function getKeyCount(vaultId: string): Promise<number> {
  const res = await pool.query(
    `SELECT COUNT(*) as count FROM vault_keys WHERE vault_id = $1 AND revoked_at IS NULL`,
    [vaultId]
  );
  return parseInt(res.rows[0].count, 10);
}
