# Frontend Integration — `@selfxyz/qrcode`

```bash
npm install @selfxyz/qrcode
```

## SelfAppBuilder

Builder pattern that produces a `SelfApp` config object.

```typescript
import { SelfAppBuilder } from "@selfxyz/qrcode";

const selfApp = new SelfAppBuilder({
  appName: "My App",                         // display name in Self app
  scope: "my-app-scope",                     // unique scope string
  endpoint: "https://api.example.com/verify", // backend URL or contract address
  endpointType: "https",                     // "https" | "https-staging" | "celo" | "celo-staging"
  userId: "0xabc...",                        // user identifier
  userIdType: "hex",                         // "hex" | "uuid"
  logoBase64: "data:image/png;base64,...",    // optional app logo
  userDefinedData: "tier:premium",           // optional arbitrary string passed through to backend/contract
  deeplinkCallback: "https://myapp.com/cb",  // optional callback URL for deep link flow
  disclosures: {
    minimumAge: 18,                          // minimum age (number or false)
    excludedCountries: ["IRN", "PRK"],       // ISO 3-letter codes, max 40
    ofac: true,                              // OFAC sanctions screening
    nationality: true,                       // disclose nationality
    gender: true,                            // disclose gender
    name: true,                              // disclose full name
    dateOfBirth: true,                       // disclose exact DOB
    issuingState: true,                      // disclose issuing country
    idNumber: true,                          // disclose passport/ID number
    expiryDate: true,                        // disclose document expiry
  },
}).build();
```

**`endpointType` values:**
- `"https"` — Off-chain, production (real passports)
- `"https-staging"` — Off-chain, testnet (mock passports)
- `"celo"` — On-chain, Celo mainnet
- `"celo-staging"` — On-chain, Celo Sepolia testnet

## SelfQRcodeWrapper

React component that renders the QR code and handles the verification flow.

```tsx
<SelfQRcodeWrapper
  selfApp={selfApp}          // SelfApp config from builder
  onSuccess={(result) => {}}  // called on successful verification
  onError={(error) => {}}     // called on failure
  type="websocket"            // connection type
  darkMode={false}            // UI theme
/>
```

## Deep Linking (Mobile)

For mobile users, bypass QR scanning by linking directly into the Self app.

```tsx
import { SelfAppBuilder, getUniversalLink } from "@selfxyz/qrcode";

const selfApp = new SelfAppBuilder({
  appName: "My App",
  scope: "my-scope",
  endpoint: "https://api.example.com/verify",
  endpointType: "https",
  userId: userAddress,
  userIdType: "hex",
  deeplinkCallback: "https://myapp.com/callback",
  disclosures: { minimumAge: 18 },
}).build();

const deepLink = getUniversalLink(selfApp);

// Render conditionally
function VerifyButton() {
  const isMobile = /iPhone|Android/i.test(navigator.userAgent);

  if (isMobile) {
    return <a href={deepLink}>Verify with Self</a>;
  }
  return <SelfQRcodeWrapper selfApp={selfApp} onSuccess={handleSuccess} />;
}
```

**Deep link callback flow:**
1. User taps link → Self app opens
2. User scans passport, generates proof
3. Self app sends proof to `endpoint`
4. Self app redirects user to `deeplinkCallback` URL

## Disclosure Options Reference

All disclosure fields are optional. Set to `true` to request disclosure, `false` or omit to skip.

| Field | Type | Notes |
|-------|------|-------|
| `minimumAge` | `number \| false` | Age threshold check |
| `excludedCountries` | `string[]` | ISO 3-letter, max 40 |
| `ofac` | `boolean` | US sanctions list check |
| `nationality` | `boolean` | Returns 3-letter country code |
| `gender` | `boolean` | As on document |
| `name` | `boolean` | Full name from document |
| `dateOfBirth` | `boolean` | Exact date |
| `issuingState` | `boolean` | Document issuing country |
| `idNumber` | `boolean` | Passport/ID number |
| `expiryDate` | `boolean` | Document expiry date |
