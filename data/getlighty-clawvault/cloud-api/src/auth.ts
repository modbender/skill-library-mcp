import crypto from "node:crypto";
import type { VaultKey } from "./types.js";

/**
 * Convert an SSH Ed25519 public key to a PEM-formatted public key
 * that Node.js crypto can use for verification.
 *
 * SSH format: "ssh-ed25519 AAAAC3Nz... comment"
 * We need to extract the raw 32-byte Ed25519 key and wrap it in PKCS8/SPKI DER.
 */
function sshPubKeyToPem(sshPubKey: string): crypto.KeyObject {
  const parts = sshPubKey.trim().split(/\s+/);
  if (parts.length < 2 || parts[0] !== "ssh-ed25519") {
    throw new Error("Not an Ed25519 SSH public key");
  }

  const keyData = Buffer.from(parts[1], "base64");

  // SSH wire format: uint32 length + "ssh-ed25519" + uint32 length + 32-byte key
  // Parse it properly
  let offset = 0;
  const typeLen = keyData.readUInt32BE(offset);
  offset += 4;
  const keyType = keyData.subarray(offset, offset + typeLen).toString();
  offset += typeLen;

  if (keyType !== "ssh-ed25519") {
    throw new Error(`Unexpected key type: ${keyType}`);
  }

  const pubLen = keyData.readUInt32BE(offset);
  offset += 4;
  const rawPub = keyData.subarray(offset, offset + pubLen);

  if (rawPub.length !== 32) {
    throw new Error(`Expected 32-byte Ed25519 key, got ${rawPub.length}`);
  }

  // Wrap in Ed25519 SPKI DER format
  // The SPKI wrapper for Ed25519 is: 302a300506032b6570032100 + 32 bytes
  const spkiPrefix = Buffer.from("302a300506032b6570032100", "hex");
  const spkiDer = Buffer.concat([spkiPrefix, rawPub]);

  return crypto.createPublicKey({
    key: spkiDer,
    format: "der",
    type: "spki",
  });
}

/**
 * Verify an Ed25519 signature against a payload using registered SSH public keys.
 * Returns the fingerprint of the key that matched, or null if none did.
 *
 * The client signs with: echo -n "$payload" | openssl pkeyutl -sign -inkey privkey -rawin | base64
 */
export function verifySignature(
  payload: string,
  signatureBase64: string,
  keys: VaultKey[]
): string | null {
  const signature = Buffer.from(signatureBase64, "base64");
  const data = Buffer.from(payload, "utf-8");

  for (const key of keys) {
    if (key.revoked_at) continue;

    try {
      const pubKey = sshPubKeyToPem(key.public_key);
      const valid = crypto.verify(null, data, pubKey, signature);
      if (valid) return key.fingerprint;
    } catch {
      // Key parsing failed, try next
      continue;
    }
  }

  return null;
}

/**
 * Compute the SSH fingerprint of a public key (SHA256:...).
 */
export function computeFingerprint(sshPubKey: string): string {
  const parts = sshPubKey.trim().split(/\s+/);
  if (parts.length < 2) throw new Error("Invalid SSH public key");
  const keyData = Buffer.from(parts[1], "base64");
  const hash = crypto.createHash("sha256").update(keyData).digest("base64");
  // Remove trailing '=' padding to match ssh-keygen output
  return `SHA256:${hash.replace(/=+$/, "")}`;
}
