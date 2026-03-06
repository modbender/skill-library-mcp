---
name: self-xyz
description: "Integrate Self (self.xyz) — a privacy-first identity protocol using zero-knowledge proofs to verify passports and ID cards. Use when the user mentions Self protocol, Self identity, self.xyz, passport verification, zero-knowledge identity verification, SelfAppBuilder, SelfBackendVerifier, SelfVerificationRoot, or wants to add privacy-preserving KYC, age verification, nationality checks, OFAC screening, or Sybil resistance using real-world identity documents. Covers frontend QR code integration, backend proof verification, and on-chain smart contract verification on Celo."
---

# Self Protocol Integration

Self lets users prove identity attributes (age, nationality, humanity) from passports/ID cards using zero-knowledge proofs — no personal data exposed. Users scan their document's NFC chip in the Self mobile app and share a zk proof with your app.

## Quick Start (Next.js Off-Chain)

### 1. Install

```bash
npm install @selfxyz/qrcode @selfxyz/core
```

### 2. Frontend — QR Code Component

```tsx
"use client";
import { SelfQRcodeWrapper, SelfAppBuilder } from "@selfxyz/qrcode";

export default function VerifyIdentity({ userId }: { userId: string }) {
  const selfApp = new SelfAppBuilder({
    appName: "My App",
    scope: "my-app-scope",
    endpoint: "https://yourapp.com/api/verify",
    endpointType: "https",
    userId,
    userIdType: "hex",
    disclosures: {
      minimumAge: 18,
    },
  }).build();

  return (
    <SelfQRcodeWrapper
      selfApp={selfApp}
      onSuccess={() => console.log("Verified")}
      type="websocket"
      darkMode={false}
    />
  );
}
```

### 3. Backend — Verification Endpoint

```ts
// app/api/verify/route.ts
import { SelfBackendVerifier, DefaultConfigStore } from "@selfxyz/core";

export async function POST(req: Request) {
  const { proof, publicSignals } = await req.json();

  const verifier = new SelfBackendVerifier(
    "my-app-scope",                    // must match frontend scope
    "https://yourapp.com/api/verify",  // must match frontend endpoint
    true,                              // true = accept mock passports (dev only)
    null,                              // allowedIds (null = all)
    new DefaultConfigStore({           // must match frontend disclosures
      minimumAge: 18,
    })
  );

  const result = await verifier.verify(proof, publicSignals);

  return Response.json({
    verified: result.isValid,
    nationality: result.credentialSubject?.nationality,
  });
}
```

## Integration Patterns

| Pattern | When to Use | `endpoint` | `endpointType` |
|---------|------------|------------|----------------|
| **Off-chain** (backend) | Web apps, APIs, most cases | Your API URL | `"https"` or `"https-staging"` |
| **On-chain** (contract) | DeFi, token gating, airdrops | Contract address (lowercase) | `"celo"` or `"celo-staging"` |
| **Deep linking** | Mobile-first flows | Your API URL | `"https"` |

- **Off-chain**: Fastest to implement. Proof sent to your backend, verified server-side.
- **On-chain**: Proof verified by Celo smart contract. Inherit `SelfVerificationRoot`. Use for trustless/permissionless scenarios.
- **Deep linking**: For mobile users — opens Self app directly instead of QR scan. See `references/frontend.md`.

## Critical Gotchas

1. **Config matching is mandatory** — Frontend `disclosures` must EXACTLY match backend/contract verification config. Mismatched age thresholds, country lists, or OFAC settings cause silent failures.

2. **Contract addresses must be lowercase** — Non-checksum format in frontend `endpoint`. Use `.toLowerCase()`.

3. **Country codes are ISO 3-letter** — e.g., `"USA"`, `"IRN"`, `"PRK"`. Max 40 countries in exclusion lists.

4. **Mock passports = testnet only** — Set `mockPassport: true` in backend / use `"celo-staging"` endpoint type. Real passports require mainnet. To create a mock passport: open Self app, tap the Passport button **5 times**. Mock testing requires OFAC disabled.

5. **Version requirement** — `@selfxyz/core` >= 1.1.0-beta.1.

6. **Attestation IDs** — `1` = Passport, `2` = Biometric ID Card. Must explicitly allow via `allowedIds` map.

7. **Scope uniqueness** — On-chain, scope is Poseidon-hashed with contract address, preventing cross-contract proof replay.

8. **Endpoint must be publicly accessible** — Self app sends proof directly to your endpoint. Use ngrok for local development.

9. **Common errors**: `ScopeMismatch` = scope/address mismatch or non-lowercase address. `Invalid 'to' Address` = wrong `endpointType` (celo vs https). `InvalidIdentityCommitmentRoot` = real passport on testnet (use mainnet). `Invalid Config ID` = mock passport on mainnet (use testnet).

## Deployed Contracts (Celo)

| Network | Address |
|---------|---------|
| **Mainnet** Hub V2 | `0xe57F4773bd9c9d8b6Cd70431117d353298B9f5BF` |
| **Sepolia** Hub V2 | `0x16ECBA51e18a4a7e61fdC417f0d47AFEeDfbed74` |
| **Sepolia Staging** Hub V2 | `0x68c931C9a534D37aa78094877F46fE46a49F1A51` |

## References

Load these for deeper integration details:

- **`references/frontend.md`** — `SelfAppBuilder` full config, `SelfQRcodeWrapper` props, deep linking with `getUniversalLink`, disclosure options
- **`references/backend.md`** — `SelfBackendVerifier` constructor details, `DefaultConfigStore` vs `InMemoryConfigStore`, verification result schema, dynamic configs
- **`references/contracts.md`** — `SelfVerificationRoot` inheritance pattern, Hub V2 interaction, `setVerificationConfigV2`, `customVerificationHook`, `getConfigId`, `userDefinedData` patterns
