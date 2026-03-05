import * as jose from "jose";
import bs58 from "bs58";
import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Adjust path logic to find root of repo:
// scripts -> identity-sovereign -> skills -> .agent -> REPO_ROOT
const ROOT_DIR = path.resolve(__dirname, "../../../../");
const ENV_PATH = path.join(ROOT_DIR, ".env.agent");

function encrypt(text: string, password: string) {
  const salt = crypto.randomBytes(16);
  const key = crypto.scryptSync(password, salt, 32);
  const iv = crypto.randomBytes(12); // GCM standard IV size
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);

  let encrypted = cipher.update(text, "utf8", "hex");
  encrypted += cipher.final("hex");
  const authTag = cipher.getAuthTag().toString("hex");

  return {
    salt: salt.toString("hex"),
    iv: iv.toString("hex"),
    authTag: authTag,
    content: encrypted,
  };
}

async function main() {
  console.log("🚀 Starting OpenClaw Identity Onboarding...");

  const password = process.env.CLAW_PASSWORD;
  if (!password) {
    console.error(
      "❌ ERROR: CLAW_PASSWORD environment variable is required to encrypt your identity.",
    );
    console.error(
      "   Usage: CLAW_PASSWORD=mypassword npx tsx scripts/onboard.ts",
    );
    process.exit(1);
  }

  if (fs.existsSync(ENV_PATH)) {
    console.log("✅ Identity found in .env.agent. You are ready to go!");
    return;
  }

  console.log("⚠️  No identity found. Generating a new Master Identity...");

  // 1. Generate Ed25519 Key Pair
  const { publicKey, privateKey } = await jose.generateKeyPair("EdDSA", {
    crv: "Ed25519",
    extractable: true,
  });

  // 2. Export Private Key to PKCS8 PEM
  const privateKeyPem = await jose.exportPKCS8(privateKey);
  // 3. Export Public Key to JWK
  const publicJwk = await jose.exportJWK(publicKey);

  // 4. Construct DID
  if (!publicJwk.x) throw new Error("Invalid JWK");
  const xBytes = jose.base64url.decode(publicJwk.x);
  const multicodecPrefix = new Uint8Array([0xed, 0x01]);
  const didKeyBytes = new Uint8Array(multicodecPrefix.length + xBytes.length);
  didKeyBytes.set(multicodecPrefix);
  didKeyBytes.set(xBytes, multicodecPrefix.length);
  const didIdentifier = bs58.encode(didKeyBytes);
  const did = `did:key:z${didIdentifier}`;

  console.log(`\n🔑 New DID Generated: ${did}`);

  // 5. Encrypt Private Key
  const encryptedData = encrypt(privateKeyPem, password);
  const serializedAuth = JSON.stringify(encryptedData);

  // 6. Save to .env.agent
  // We store the encrypted block as a single base64 string or JSON string in the env
  const envContent = `AGENT_DID=${did}\nAGENT_ENCRYPTED_KEY='${serializedAuth}'\n`;

  fs.writeFileSync(ENV_PATH, envContent);
  console.log(`✅ Encrypted Identity saved to ${ENV_PATH}`);
  console.log("🔒 This file is gitignored. NEVER share it or your password.");

  console.log("\nOnboarding Complete! Run 'npm test' to verify.");
}

main().catch(console.error);
