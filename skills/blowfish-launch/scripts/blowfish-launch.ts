#!/usr/bin/env bun
import { Keypair } from "@solana/web3.js";
import nacl from "tweetnacl";
import bs58 from "bs58";
import { parseArgs } from "util";

const API_BASE = "https://api-blowfish.neuko.ai";

// --- Args ---
const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    name: { type: "string" },
    ticker: { type: "string" },
    description: { type: "string", default: "" },
    imageUrl: { type: "string", default: "" },
  },
  strict: true,
});

if (!values.name || !values.ticker) {
  console.error("Usage: blowfish-launch.ts --name <name> --ticker <TICKER> [--description <desc>] [--imageUrl <url>]");
  process.exit(1);
}

// --- Auth ---
async function authenticate(keypair: Keypair): Promise<string> {
  const wallet = keypair.publicKey.toBase58();

  const challengeRes = await fetch(`${API_BASE}/api/auth/challenge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wallet }),
  });
  const { nonce } = await challengeRes.json();

  const message = `Sign this message to authenticate: ${nonce}`;
  const sig = nacl.sign.detached(new TextEncoder().encode(message), keypair.secretKey);

  const verifyRes = await fetch(`${API_BASE}/api/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wallet, nonce, signature: bs58.encode(sig) }),
  });
  const { token } = await verifyRes.json();
  return token;
}

// --- Launch ---
async function launchToken(
  token: string,
  params: { name: string; ticker: string; description?: string; imageUrl?: string }
): Promise<string> {
  const response = await fetch(`${API_BASE}/api/v1/tokens/launch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Launch failed (${response.status}): ${error.error}`);
  }

  const { eventId } = await response.json();
  return eventId;
}

// --- Poll ---
async function waitForDeployment(eventId: string, token: string): Promise<string> {
  const url = `${API_BASE}/api/v1/tokens/launch/status/${eventId}`;

  for (let i = 0; i < 60; i++) {
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();

    if (data.status === "success") {
      console.log("✅ Token launched successfully!");
      console.log(JSON.stringify(data, null, 2));
      return "success";
    }
    if (data.status === "failed" || data.status === "rate_limited") {
      throw new Error(`Launch ${data.status}: ${JSON.stringify(data)}`);
    }

    console.log(`⏳ Status: ${data.status}... (attempt ${i + 1}/60)`);
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }

  throw new Error("Launch timed out after 5 minutes");
}

// --- Main ---
async function main() {
  const secretKey = Uint8Array.from(JSON.parse(process.env.WALLET_SECRET_KEY!));
  const keypair = Keypair.fromSecretKey(secretKey);

  console.log(`🔐 Authenticating wallet: ${keypair.publicKey.toBase58()}`);
  const token = await authenticate(keypair);

  const params: any = { name: values.name!, ticker: values.ticker! };
  if (values.description) params.description = values.description;
  if (values.imageUrl) params.imageUrl = values.imageUrl;

  console.log(`🚀 Launching token: ${params.name} ($${params.ticker})`);
  const eventId = await launchToken(token, params);
  console.log(`📋 Event ID: ${eventId}`);

  await waitForDeployment(eventId, token);
}

main().catch((err) => {
  console.error(`❌ ${err.message}`);
  process.exit(1);
});
