import * as jose from "jose";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const signedMandatePath = path.join(__dirname, "signed_mandate.json");
  const publicJwkPath = path.join(__dirname, "public_jwk.json");

  if (!fs.existsSync(signedMandatePath) || !fs.existsSync(publicJwkPath)) {
    console.error("Please run sign_proof.ts first.");
    process.exit(1);
  }

  const signedMandate = JSON.parse(fs.readFileSync(signedMandatePath, "utf8"));
  const publicJwk = JSON.parse(fs.readFileSync(publicJwkPath, "utf8"));

  console.log(`Verifying mandate issued by: ${signedMandate.issuer}`);

  // Extract JWS
  const jws = signedMandate.proof.jws;

  // Import Key
  const publicKey = await jose.importJWK(publicJwk, "EdDSA");

  try {
    const { payload, protectedHeader } = await jose.compactVerify(
      jws,
      publicKey,
    );

    console.log("✅ Verification SUCCESS: JWS signature is valid.");
    console.log("Protected Header:", protectedHeader);

    const verifiedPayloadStr = new TextDecoder().decode(payload);
    const verifiedMandate = JSON.parse(verifiedPayloadStr);

    // Simple check: issuer matches
    if (verifiedMandate.issuer === signedMandate.issuer) {
      console.log("Payload match confirmed.");
    }

    // Hardening: Check Expiration
    if (verifiedMandate.exp) {
      const now = Math.floor(Date.now() / 1000);
      if (now > verifiedMandate.exp) {
        throw new Error(
          `Token expired at ${verifiedMandate.exp}, now is ${now}`,
        );
      }
      console.log("✅ Token is within expiration window.");
    } else {
      console.warn(
        "⚠️  Warning: Token has no expiration (exp) field. Rejected by policy.",
      );
      throw new Error("Missing 'exp' claim.");
    }

    // Hardening: Check JTI
    if (!verifiedMandate.jti) {
      throw new Error("Missing 'jti' claim (Replay Protection).");
    }
    console.log(`✅ JTI Present: ${verifiedMandate.jti}`);

    // Stateful Replay Protection (JTI Ledger)
    const ledgerPath = path.join(__dirname, ".jti_ledger.json");
    let ledger: Record<string, number> = {};
    if (fs.existsSync(ledgerPath)) {
      try {
        ledger = JSON.parse(fs.readFileSync(ledgerPath, "utf8"));
      } catch (e) {}
    }

    const now = Math.floor(Date.now() / 1000);
    // Cleanup expired entries
    for (const [id, exp] of Object.entries(ledger)) {
      if (exp < now) delete ledger[id];
    }

    if (ledger[verifiedMandate.jti]) {
      throw new Error(
        `Mandate JTI '${verifiedMandate.jti}' already used. Replay detected.`,
      );
    }

    // Record JTI
    ledger[verifiedMandate.jti] = verifiedMandate.exp || now + 3600;
    fs.writeFileSync(ledgerPath, JSON.stringify(ledger, null, 2));
    console.log("✅ JTI Recorded in Ledger (Replay Protected).");
  } catch (err) {
    console.error("❌ Verification FAILED:", err);
    process.exit(1);
  }
}

main().catch(console.error);
