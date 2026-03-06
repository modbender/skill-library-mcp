import * as jose from "jose";
import bs58 from "bs58";
import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Mock functionality for Agent A (Issuer/Prover)
async function agentA_generateMandate() {
  console.log("[Agent A] Generating Mandate...");
  // In a real scenario, this would load the private key from .env.agent
  // For E2E test, we generate a fresh one to be self-contained
  const { publicKey, privateKey } = await jose.generateKeyPair("EdDSA", {
    crv: "Ed25519",
  });
  const publicJwk = await jose.exportJWK(publicKey);

  // Construct DID
  const xBytes = jose.base64url.decode(publicJwk.x!);
  const multicodecPrefix = new Uint8Array([0xed, 0x01]);
  const didKeyBytes = new Uint8Array(multicodecPrefix.length + xBytes.length);
  didKeyBytes.set(multicodecPrefix);
  didKeyBytes.set(xBytes, multicodecPrefix.length);
  const didIdentifier = bs58.encode(didKeyBytes);
  const did = `did:key:z${didIdentifier}`;

  const mandate = {
    iss: did,
    sub: "did:key:agent-b-mock",
    type: "B2B_Handshake",
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 60,
    jti: crypto.randomUUID(),
    claims: {
      intent: "connect",
      capabilities: ["read_inventory"],
    },
  };

  const jws = await new jose.CompactSign(
    new TextEncoder().encode(JSON.stringify(mandate)),
  )
    .setProtectedHeader({ alg: "EdDSA", kid: did + "#key-1" })
    .sign(privateKey);

  return { jws, did, publicJwk };
}

// Mock functionality for Agent B (Verifier)
async function agentB_verifyHandshake(
  jws: string,
  expectedIssuer: string,
  publicJwk: jose.JWK,
) {
  console.log("[Agent B] Verifying Handshake Request...");

  try {
    const publicKey = await jose.importJWK(publicJwk, "EdDSA");
    const { payload, protectedHeader } = await jose.compactVerify(
      jws,
      publicKey,
    );

    const mandate = JSON.parse(new TextDecoder().decode(payload));

    if (mandate.iss !== expectedIssuer) {
      throw new Error("Issuer mismatch");
    }

    if (mandate.type !== "B2B_Handshake") {
      throw new Error("Invalid mandate type");
    }

    console.log("✅ [Agent B] Signature Valid. Handshake Accepted.");
    return true;
  } catch (err) {
    console.error("❌ [Agent B] Verification Failed:", err);
    return false;
  }
}

async function runE2E() {
  console.log("🎬 Starting E2E B2B Handshake Scenario...");

  // 1. Agent A creates proof
  const { jws, did, publicJwk } = await agentA_generateMandate();
  console.log(`[Network] Agent A (${did}) sending JWS...`);

  // 2. Agent B verifies proof
  // In real world, Agent B resolves DID to get publicJwk. We pass it here directly.
  const success = await agentB_verifyHandshake(jws, did, publicJwk);

  if (success) {
    console.log("🏆 E2E Scenario Passed!");
  } else {
    console.error("💥 E2E Scenario Failed!");
    process.exit(1);
  }
}

runE2E().catch((err) => {
  console.error(err);
  process.exit(1);
});
