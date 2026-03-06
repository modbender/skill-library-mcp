import * as jose from "jose";
import * as crypto from "crypto";
import bs58 from "bs58";

// Helper to generate salt
const generateSalt = () => {
  return crypto.randomBytes(16).toString("base64url");
};

// Helper to create a disclosure
// Disclosure format: [salt, key, value]
const createDisclosure = (key: string, value: any) => {
  const salt = generateSalt();
  return [salt, key, value];
};

// Helper to hash a disclosure
// Hash(canonical_json(disclosure))
const hashDisclosure = (disclosure: any[]) => {
  const disclosureJson = JSON.stringify(disclosure);
  const hash = crypto.createHash("sha256").update(disclosureJson).digest();
  return hash.toString("base64url"); // generic SD-JWT uses base64url usually
};

async function main() {
  console.log("--- Generating SD-JWT ---");

  // 1. Identity Setup (Issuer)
  const { publicKey, privateKey } = await jose.generateKeyPair("EdDSA", {
    crv: "Ed25519",
  });

  // 2. Define Claims
  const sensitiveClaims = {
    given_name: "Agent",
    family_name: "Smith",
    email: "agent.smith@matrix.com",
    age_over_18: true,
    credit_score_tier: "A+",
  };

  // 3. Create Disclosures & Hashes
  const disclosures: string[] = [];
  const hashes: string[] = [];

  const sdClaims: Record<string, any> = {
    _sd: [],
  };

  for (const [key, value] of Object.entries(sensitiveClaims)) {
    const disclosure = createDisclosure(key, value);
    const disclosureStr = JSON.stringify(disclosure);
    const disclosureB64 = Buffer.from(disclosureStr).toString("base64url");

    disclosures.push(disclosureB64);

    const hash = hashDisclosure(disclosure);
    hashes.push(hash);
    sdClaims._sd.push(hash);
  }

  // 4. Create the JWT Payload
  const payload = {
    iss: "did:key:issuer",
    sub: "did:key:subject",
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600,
    ...sdClaims,
  };

  console.log(
    "JWT Payload (with hidden claims):",
    JSON.stringify(payload, null, 2),
  );

  // 5. Sign the JWT
  const jwt = await new jose.SignJWT(payload)
    .setProtectedHeader({ alg: "EdDSA" })
    .sign(privateKey);

  // 6. Append Disclosures (The SD-JWT Format utils)
  // Format: <JWT>~<Disclosure1>~<Disclosure2>~...~<KeyBindingJWT>
  const sdJwt = `${jwt}~${disclosures.join("~")}~`;

  console.log("\nComplete SD-JWT:");
  console.log(sdJwt);

  console.log("\n--- Verifying & Selective Disclosure ---");
  console.log(
    "Scenario: Presenting ONLY 'age_over_18' and 'credit_score_tier' to a vendor.",
  );

  // 7. Client Selects Disclosures to Reveal
  // The client parses the SD-JWT, finds the hashes for the claims they want to reveal,
  // and filters the disclosure strings that match those hashes.

  const targetClaims = ["age_over_18", "credit_score_tier"];

  // Simulating the "Holder" logic filtering disclosures
  const revealedDisclosures = disclosures.filter((d) => {
    const decoded = JSON.parse(Buffer.from(d, "base64url").toString());
    // decoded is [salt, key, value]
    return targetClaims.includes(decoded[1]);
  });

  // 8. Presentation
  // Format: <JWT>~<RevealedDisclosure1>~<RevealedDisclosure2>~
  const presentationSdJwt = `${jwt}~${revealedDisclosures.join("~")}~`;

  console.log("\nPresentation SD-JWT (Redacted):");
  console.log(presentationSdJwt);

  // 9. Verifier Logic
  // a. Split token
  const parts = presentationSdJwt.split("~");
  const receivedJwt = parts[0];
  const receivedDisclosures = parts.slice(1, -1); // remove last empty

  // b. Verify Signature of JWT
  const { payload: verifiedPayload } = await jose.jwtVerify(
    receivedJwt,
    publicKey,
  );
  console.log("\n✅ Base JWT Signature Verified.");

  // c. Verify Disclosures
  const recoveredClaims: Record<string, any> = {};

  const _sd = (verifiedPayload as any)._sd || [];

  console.log("\nVerifying Disclosures:");
  for (const d of receivedDisclosures) {
    const decodedJson = Buffer.from(d, "base64url").toString();
    const decoded = JSON.parse(decodedJson); // [salt, key, value]

    // Re-hash check
    const hash = hashDisclosure(decoded);

    if (_sd.includes(hash)) {
      console.log(`  ✅ Verified Claim: "${decoded[1]}" = ${decoded[2]}`);
      recoveredClaims[decoded[1]] = decoded[2];
    } else {
      console.error(`  ❌ Hash mismatch for disclosure: ${decodedJson}`);
    }
  }

  console.log("\nRecovered Claims View:");
  console.log(JSON.stringify(recoveredClaims, null, 2));

  if (!recoveredClaims["email"]) {
    console.log("  (Note: 'email' was successfully hidden)");
  }
}

main().catch(console.error);
