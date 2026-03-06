# Backend Integration — `@selfxyz/core`

```bash
npm install @selfxyz/core
```

## SelfBackendVerifier

```typescript
import {
  SelfBackendVerifier,
  DefaultConfigStore,
  ATTESTATION_ID,
} from "@selfxyz/core";

const verifier = new SelfBackendVerifier(
  "my-app-scope",                    // scope — must match frontend
  "https://api.example.com/verify",  // endpoint — must match frontend
  false,                             // false = mainnet, true = staging/mock passports
  null,                              // allowedIds (null = all document types)
  new DefaultConfigStore({           // disclosures — must match frontend exactly
    minimumAge: 18,
    excludedCountries: ["IRN", "PRK"],
    ofac: true,
    nationality: true,
    name: true,
  })
);
```

## Verification

```typescript
// app/api/verify/route.ts
export async function POST(req: Request) {
  const { proof, publicSignals } = await req.json();

  const result = await verifier.verify(proof, publicSignals);

  if (!result.isValid) {
    return Response.json({ error: "Verification failed" }, { status: 400 });
  }

  // result.credentialSubject contains disclosed attributes
  const { nationality, name, dateOfBirth, gender } = result.credentialSubject ?? {};

  // result.isValidDetails has per-check breakdown
  const { isMinimumAgeValid, isOfacValid } = result.isValidDetails;

  return Response.json({ verified: true, nationality });
}
```

## Verification Result Schema

```typescript
{
  isValid: boolean,
  isValidDetails: {
    isValid: boolean,
    isMinimumAgeValid: boolean,
    isOfacValid: boolean,
  },
  credentialSubject: {
    nationality?: string,    // 3-letter country code
    name?: string,
    dateOfBirth?: string,
    gender?: string,
    issuingState?: string,
    idNumber?: string,
    expiryDate?: string,
  },
  // Nullifier for Sybil resistance
  nullifier?: string,
}
```

## Config Stores

For advanced use cases with multiple verification configurations.

### DefaultConfigStore

Same config for all requests (most common).

```typescript
import { SelfBackendVerifier, DefaultConfigStore } from "@selfxyz/core";

const verifier = new SelfBackendVerifier(
  "scope", "endpoint", false, null,
  new DefaultConfigStore({ minimumAge: 18, ofac: true })
);
```

### InMemoryConfigStore

Dynamic configs keyed by a custom function — useful when different users or flows need different verification requirements.

```typescript
import { InMemoryConfigStore } from "@selfxyz/core";

const configStore = new InMemoryConfigStore(
  (actionId: string) => `config-${actionId}` // key generation function
);

// Register configs
configStore.set("config-premium", { minimumAge: 21, ofac: true });
configStore.set("config-basic", { minimumAge: 18 });
```

### Custom Config Store

Implement `IConfigStorage` for database-backed configs.

```typescript
import { IConfigStorage } from "@selfxyz/core";

class DatabaseConfigStore implements IConfigStorage {
  async getConfig(id: string) { /* fetch from DB */ }
  async setConfig(id: string, config: any): Promise<boolean> { /* save, return true if replaced */ }
  async getActionId(userIdentifier: string, data: any): Promise<string> { /* compute action ID */ }
}
```

## Attestation IDs

```typescript
import { ATTESTATION_ID } from "@selfxyz/core";

// ATTESTATION_ID.PASSPORT = 1
// ATTESTATION_ID.BIOMETRIC_ID_CARD = 2
```

When configuring which document types to accept:

```typescript
const allowedIds = new Map<number, boolean>();
allowedIds.set(ATTESTATION_ID.PASSPORT, true);
allowedIds.set(ATTESTATION_ID.BIOMETRIC_ID_CARD, true);
```

## Local Development

The Self app sends proofs directly to your `endpoint`. For local dev, expose your server:

```bash
ngrok http 3000
# Use the ngrok URL as endpoint in both frontend and backend
```
