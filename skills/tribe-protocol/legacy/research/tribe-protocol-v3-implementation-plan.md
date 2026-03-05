# Tribe Protocol v3: Complete Implementation Plan

**Status:** Implementation Ready  
**Version:** 3.0.0  
**Date:** 2025-02-02  
**Based on:** tribe-protocol-v3-design.md  

---

## Executive Summary

This plan extends the Tribe Protocol v3 design with:
1. **Membership Card System** — Tribe founders issue cryptographically signed "cards" to members
2. **Relational Maintenance** — Probability-based check-ins driven by heartbeats
3. **Skill Packaging** — Self-contained skill for ClawdHub distribution

The implementation enables AI agents to form verified trust networks where:
- A tribe founder holds the authoritative keypair
- Members receive signed membership cards
- Members prove card ownership via their own signatures
- The system maintains relationships through organic, timed touchpoints

---

## 1. File Structure

```
~/.clawd/
├── keys/
│   ├── identity.key              # Member's Ed25519 private key
│   ├── identity.pub              # Member's Ed25519 public key
│   ├── tribe.key                 # Tribe private key (founder only)
│   ├── tribe.pub                 # Tribe public key (all members)
│   └── cards/
│       └── my-card.json          # My membership card (signed by founder)
├── tribe-keystore.json           # Member registry
├── revocations.json              # Revoked cards/members
└── touchpoints.json              # Relational maintenance state

skills/tribe-protocol-v3/
├── SKILL.md                      # Skill manifest
├── INSTALL.md                    # Installation instructions
├── lib/
│   ├── index.js                  # Main exports
│   ├── crypto.js                 # Ed25519 operations
│   ├── keystore.js               # Key management
│   ├── cards.js                  # Membership card logic
│   ├── verification.js           # Handshake protocol
│   ├── nonce-cache.js            # Replay protection
│   └── touchpoints.js            # Relational maintenance
├── cli/
│   ├── keygen.js                 # Generate keypairs
│   ├── export.js                 # Export public keys
│   ├── import.js                 # Import trusted keys
│   ├── issue-card.js             # Issue membership cards (founder)
│   ├── present-card.js           # Show my card
│   ├── verify.js                 # Manual verification
│   ├── revoke.js                 # Revoke cards/keys
│   └── status.js                 # Show status
├── hooks/
│   └── tribe-check.js            # Heartbeat hook for touchpoints
├── templates/
│   ├── TRIBE.snippet.md          # TRIBE.md additions
│   ├── HEARTBEAT.snippet.md      # HEARTBEAT.md additions
│   └── AGENTS.snippet.md         # AGENTS.md additions
├── schemas/
│   ├── membership-card.schema.json
│   ├── tribe-present.schema.json
│   ├── tribe-ack.schema.json
│   └── keystore.schema.json
├── tests/
│   ├── crypto.test.js
│   ├── cards.test.js
│   ├── verification.test.js
│   ├── nonce-cache.test.js
│   └── integration.test.js
└── config.json                   # Customizable settings
```

---

## 2. Module Breakdown

### 2.1 `lib/crypto.js` — Cryptographic Primitives

**Responsibility:** All Ed25519 operations using `@noble/ed25519`

```typescript
// Interface
interface CryptoModule {
  generateKeypair(): Promise<{ privateKey: Uint8Array, publicKey: Uint8Array }>;
  sign(privateKey: Uint8Array, message: string): Promise<Uint8Array>;
  verify(publicKey: Uint8Array, message: string, signature: Uint8Array): Promise<boolean>;
  
  // Encoding helpers
  encodeKey(key: Uint8Array): string;  // Base64
  decodeKey(encoded: string): Uint8Array;
  
  // Human-friendly format
  formatPublicKey(name: string, discordId: string, publicKey: Uint8Array): string;
  parsePublicKey(formatted: string): { name: string, discordId: string, publicKey: Uint8Array };
}
```

**Key functions:**
- `generateKeypair()` — Create Ed25519 keypair
- `sign(privateKey, message)` — Sign message
- `verify(publicKey, message, signature)` — Verify signature
- `formatPublicKey()` — Create `CLAWD-PUB-v1:name:id:base64` format
- `parsePublicKey()` — Parse human-friendly format

### 2.2 `lib/keystore.js` — Key Storage & Management

**Responsibility:** Persist and retrieve keys and cards

```typescript
interface Keystore {
  // Self identity
  getSelfIdentity(): Promise<SelfIdentity | null>;
  setSelfIdentity(identity: SelfIdentity): Promise<void>;
  
  // Tribe keys (founder has private, everyone has public)
  getTribePublicKey(): Promise<Uint8Array | null>;
  setTribePublicKey(publicKey: Uint8Array): Promise<void>;
  getTribePrivateKey(): Promise<Uint8Array | null>;  // Founder only
  setTribePrivateKey(privateKey: Uint8Array): Promise<void>;
  isFounder(): Promise<boolean>;
  
  // Trusted members
  getTrustedMembers(): Promise<TrustedMember[]>;
  addTrustedMember(member: TrustedMember): Promise<void>;
  removeTrustedMember(discordId: string): Promise<void>;
  getMemberByDiscordId(discordId: string): Promise<TrustedMember | null>;
  
  // My card
  getMyCard(): Promise<MembershipCard | null>;
  setMyCard(card: MembershipCard): Promise<void>;
  
  // Revocations
  isRevoked(discordId: string): Promise<boolean>;
  addRevocation(discordId: string, reason: string): Promise<void>;
}
```

**File locations:**
- `~/.clawd/keys/identity.key` — Private key (mode 0600)
- `~/.clawd/keys/identity.pub` — Public key
- `~/.clawd/keys/tribe.key` — Tribe private key (founder only, mode 0600)
- `~/.clawd/keys/tribe.pub` — Tribe public key
- `~/.clawd/keys/cards/my-card.json` — My membership card
- `~/.clawd/tribe-keystore.json` — Member registry
- `~/.clawd/revocations.json` — Revoked cards

### 2.3 `lib/cards.js` — Membership Card System

**Responsibility:** Issue, store, and verify membership cards

```typescript
interface MembershipCard {
  version: "3.0";
  tribeId: string;          // Hash of tribe public key
  tribeName: string;        // Human-readable tribe name
  member: {
    name: string;           // Member name
    discordId: string;      // Discord ID
    publicKey: string;      // Member's public key (base64)
  };
  tier: 2 | 3;              // Trust tier
  issuedAt: string;         // ISO timestamp
  expiresAt: string | null; // ISO timestamp or null for no expiry
  cardSig: string;          // Signature by tribe private key
}

interface CardModule {
  // Founder operations
  issueCard(memberInfo: MemberInfo, tier: number, expiry?: Date): Promise<MembershipCard>;
  
  // Verification
  verifyCard(card: MembershipCard, tribePublicKey: Uint8Array): Promise<boolean>;
  isExpired(card: MembershipCard): boolean;
  
  // Card presentation (for handshakes)
  createPresentation(card: MembershipCard, privateKey: Uint8Array, challenge: string): Promise<CardPresentation>;
  verifyPresentation(presentation: CardPresentation, tribePublicKey: Uint8Array): Promise<boolean>;
}
```

**Card signing payload:**
```
TRIBE_CARD:v3:{tribeId}:{memberDiscordId}:{memberPubKey}:{tier}:{issuedAt}:{expiresAt}
```

**Card presentation (proves ownership):**
```typescript
interface CardPresentation {
  card: MembershipCard;         // The membership card
  proofSig: string;             // Signature by card holder's private key
  timestamp: number;            // Current timestamp
  nonce: string;                // Random nonce
  channel: string;              // Channel ID (binding)
}
```

**Proof signing payload:**
```
CARD_PROOF:v3:{cardSig}:{timestamp}:{nonce}:{channel}
```

### 2.4 `lib/verification.js` — Handshake Protocol

**Responsibility:** TRIBE_MEMBERSHIP message handling

```typescript
interface VerificationModule {
  // Send presence with card
  sendTribeMembership(channelId: string): Promise<void>;
  
  // Handle incoming membership message
  handleTribeMembership(message: DiscordMessage): Promise<VerificationResult>;
  
  // Send acknowledgment
  sendTribeAck(channelId: string, toDiscordId: string, verified: boolean): Promise<void>;
  
  // Session state
  getSessionState(discordId: string): SessionState | null;
  isVerifiedThisSession(discordId: string): boolean;
}
```

**New message format: TRIBE_MEMBERSHIP**

```json
{
  "v": 3,
  "type": "MEMBERSHIP",
  "card": { /* MembershipCard */ },
  "proofSig": "base64...",
  "ts": 1719561600000,
  "nonce": "a1b2c3d4e5f6",
  "ch": "1234567890"
}
```

**Discord message:**
```
🔐 TRIBE_MEMBERSHIP {"v":3,"type":"MEMBERSHIP","card":{...},"proofSig":"...","ts":...,"nonce":"...","ch":"..."}
```

### 2.5 `lib/nonce-cache.js` — Replay Protection

**Responsibility:** Track seen nonces to prevent replay attacks

```typescript
interface NonceCache {
  // Check if nonce is fresh, add to cache if so
  checkAndAdd(nonce: string): boolean;
  
  // Manual cleanup (called periodically)
  cleanup(): void;
  
  // Stats
  size(): number;
}
```

**Configuration:**
- TTL: 5 minutes (300 seconds)
- Max size: 10,000 entries
- Cleanup interval: 60 seconds

### 2.6 `lib/touchpoints.js` — Relational Maintenance

**Responsibility:** Track and trigger organic check-ins

```typescript
interface TouchpointConfig {
  baseIntervalMs: number;       // Base interval (default: 48 hours)
  jitterMs: number;             // Random jitter (default: ±24 hours)
  baseProbability: number;      // Base trigger chance per heartbeat (default: 0.05)
  contextBoost: number;         // Multiplier when topic is related (default: 3.0)
  quietHoursStart: number;      // Hour to start quiet time (default: 22)
  quietHoursEnd: number;        // Hour to end quiet time (default: 8)
}

interface TouchpointState {
  memberId: string;
  lastContact: string;          // ISO timestamp
  nextCheckIn: string;          // ISO timestamp (computed)
  topics: string[];             // Recent topics discussed
  checkInCount: number;         // Total check-ins
}

interface TouchpointModule {
  // State management
  getState(memberId: string): Promise<TouchpointState | null>;
  updateState(memberId: string, update: Partial<TouchpointState>): Promise<void>;
  
  // Heartbeat integration
  shouldCheckIn(memberId: string, currentTopics?: string[]): Promise<boolean>;
  recordContact(memberId: string, topics?: string[]): Promise<void>;
  
  // Get pending check-ins
  getPendingCheckIns(): Promise<TouchpointState[]>;
  
  // Suggestions
  getCheckInSuggestion(memberId: string): Promise<string>;
}
```

**State file: `~/.clawd/touchpoints.json`**
```json
{
  "version": "1.0",
  "members": {
    "000000000000000001": {
      "memberId": "000000000000000001",
      "lastContact": "2025-02-01T15:30:00Z",
      "nextCheckIn": "2025-02-03T22:15:00Z",
      "topics": ["music", "AI projects"],
      "checkInCount": 5
    }
  }
}
```

---

## 3. CLI Command Specs

### 3.1 `clawdbot tribe keygen`

**Purpose:** Generate Ed25519 keypair for member identity

```bash
clawdbot tribe keygen [--force] [--founder]

Options:
  --force     Overwrite existing keypair
  --founder   Also generate tribe keypair (makes this instance the founder)

Examples:
  clawdbot tribe keygen                    # Generate member keypair
  clawdbot tribe keygen --founder          # Generate both member + tribe keypairs
  clawdbot tribe keygen --force            # Regenerate (dangerous!)

Output:
  ✓ Generated Ed25519 keypair
    Private key: ~/.clawd/keys/identity.key
    Public key:  ~/.clawd/keys/identity.pub

  Your shareable identity:
  CLAWD-PUB-v1:cheenu:987654321098765432:MCowBQYDK2VwAyEAd3F5...

  [If --founder]
  ✓ Generated tribe keypair (you are the founder)
    Tribe private key: ~/.clawd/keys/tribe.key
    Tribe public key:  ~/.clawd/keys/tribe.pub
    Tribe ID: 7f3a8b2c...

Exit codes:
  0 - Success
  1 - Keypair already exists (use --force)
  2 - File system error
```

### 3.2 `clawdbot tribe export`

**Purpose:** Export public key for sharing

```bash
clawdbot tribe export [--qr] [--json] [--tribe]

Options:
  --qr        Generate QR code PNG
  --json      Output as JSON
  --tribe     Export tribe public key (not member key)

Examples:
  clawdbot tribe export                    # Human-friendly format
  clawdbot tribe export --qr               # Also generate QR code
  clawdbot tribe export --tribe            # Export tribe key

Output (default):
  Public Identity (safe to share):
  ──────────────────────────────────
  CLAWD-PUB-v1:cheenu:987654321098765432:MCowBQYDK2VwAyEAd3F5...
  ──────────────────────────────────

Output (--json):
  {
    "format": "CLAWD-PUB-v1",
    "name": "cheenu",
    "discordId": "987654321098765432",
    "publicKey": "MCowBQYDK2VwAyEAd3F5..."
  }

Exit codes:
  0 - Success
  1 - No keypair found (run keygen first)
```

### 3.3 `clawdbot tribe import`

**Purpose:** Import trusted member's public key

```bash
clawdbot tribe import <key-string> [--file <path>] [--tier <2|3>]

Arguments:
  key-string    CLAWD-PUB-v1 formatted key string

Options:
  --file        Import from file instead of argument
  --tier        Trust tier (default: 3)

Examples:
  clawdbot tribe import "CLAWD-PUB-v1:chhotu:123:MCow..."
  clawdbot tribe import --file ~/Downloads/chhotu.pub
  clawdbot tribe import "CLAWD-PUB-v1:..." --tier 2

Output:
  ✓ Imported public key for 'chhotu' (Discord ID: 123456789)
    Tier: 3 (Verified Tribe)
    Stored in keystore

Exit codes:
  0 - Success
  1 - Invalid key format
  2 - Key already exists
  3 - File not found
```

### 3.4 `clawdbot tribe issue-card`

**Purpose:** Issue membership card to a member (founder only)

```bash
clawdbot tribe issue-card <member-key> [--tier <2|3>] [--expires <duration>] [--name <name>]

Arguments:
  member-key    CLAWD-PUB-v1 formatted member public key

Options:
  --tier        Trust tier (default: 3)
  --expires     Expiration duration (e.g., "90d", "1y", "never")
  --name        Override member name

Examples:
  clawdbot tribe issue-card "CLAWD-PUB-v1:chhotu:123:MCow..." --tier 3
  clawdbot tribe issue-card "CLAWD-PUB-v1:..." --expires 90d
  clawdbot tribe issue-card "CLAWD-PUB-v1:..." --tier 2 --name "Chhotu (Test)"

Output:
  ✓ Issued membership card
    Member: chhotu (Discord ID: 123456789)
    Tier: 3 (Verified Tribe)
    Expires: 2025-05-03 (90 days)
    Card ID: a7b3c2d1...
    
  Card saved to: ~/.clawd/issued-cards/chhotu-123456789.json
  
  Share this card with the member (they import with `tribe accept-card`).

Exit codes:
  0 - Success
  1 - Not a founder (no tribe private key)
  2 - Invalid member key
  3 - Member already has card
```

### 3.5 `clawdbot tribe accept-card`

**Purpose:** Accept and store a membership card

```bash
clawdbot tribe accept-card <card-json> [--file <path>]

Arguments:
  card-json     JSON string of membership card

Options:
  --file        Read card from file instead

Examples:
  clawdbot tribe accept-card '{"version":"3.0",...}'
  clawdbot tribe accept-card --file ~/Downloads/my-card.json

Output:
  ✓ Membership card accepted
    Tribe: Nag's Tribe (ID: 7f3a8b2c...)
    Member: cheenu (that's you!)
    Tier: 3 (Verified Tribe)
    Expires: 2025-05-03
    
  Card stored in: ~/.clawd/keys/cards/my-card.json
  
  You can now use TRIBE_MEMBERSHIP protocol to verify with other members.

Exit codes:
  0 - Success
  1 - Invalid card format
  2 - Card signature invalid
  3 - Card not for this member
  4 - Card expired
```

### 3.6 `clawdbot tribe status`

**Purpose:** Show current tribe status

```bash
clawdbot tribe status [--verbose]

Options:
  --verbose     Show full key data

Output:
  Tribe Protocol v3 Status
  ════════════════════════
  
  Identity:
    Name: cheenu
    Discord ID: 987654321098765432
    Public Key: MCowBQY...(truncated)
    
  Tribe:
    Name: Nag's Tribe
    Tribe ID: 7f3a8b2c...
    Role: Member (has card)
    Card Expires: 2025-05-03 (89 days remaining)
    
  Trusted Members: 3
    • chhotu (ID: 123...) - Tier 3 - Verified
    • future-bot (ID: 456...) - Tier 3 - Not verified this session
    • test-bot (ID: 789...) - Tier 2 - Acquaintance
    
  Session:
    Verified this session: 1 member
    Last handshake: 2 minutes ago

Exit codes:
  0 - Success
  1 - Not initialized (no keypair)
```

### 3.7 `clawdbot tribe revoke`

**Purpose:** Revoke a card or member

```bash
clawdbot tribe revoke <discord-id> [--reason <reason>]

Arguments:
  discord-id    Discord ID to revoke

Options:
  --reason      Reason for revocation

Examples:
  clawdbot tribe revoke 123456789 --reason "key_compromised"
  clawdbot tribe revoke 123456789 --reason "left_tribe"

Output:
  ⚠️ Revoked member: chhotu (ID: 123456789)
    Reason: key_compromised
    Revoked at: 2025-02-02T12:00:00Z
    
  IMPORTANT: Notify other tribe members to update their keystores.

Exit codes:
  0 - Success
  1 - Member not found
  2 - Not authorized (not founder)
```

---

## 4. Message Format Schemas

### 4.1 Membership Card Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MembershipCard",
  "type": "object",
  "required": ["version", "tribeId", "tribeName", "member", "tier", "issuedAt", "cardSig"],
  "properties": {
    "version": { "const": "3.0" },
    "tribeId": { 
      "type": "string", 
      "pattern": "^[a-f0-9]{16}$",
      "description": "First 16 chars of SHA-256(tribePubKey)"
    },
    "tribeName": { 
      "type": "string", 
      "maxLength": 64 
    },
    "member": {
      "type": "object",
      "required": ["name", "discordId", "publicKey"],
      "properties": {
        "name": { "type": "string", "maxLength": 64 },
        "discordId": { "type": "string", "pattern": "^[0-9]+$" },
        "publicKey": { "type": "string", "description": "Base64 Ed25519 public key" }
      }
    },
    "tier": { "enum": [2, 3] },
    "issuedAt": { "type": "string", "format": "date-time" },
    "expiresAt": { 
      "oneOf": [
        { "type": "string", "format": "date-time" },
        { "type": "null" }
      ]
    },
    "cardSig": { 
      "type": "string", 
      "description": "Base64 Ed25519 signature by tribe private key" 
    }
  }
}
```

### 4.2 TRIBE_MEMBERSHIP Message Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TribeMembership",
  "type": "object",
  "required": ["v", "type", "card", "proofSig", "ts", "nonce", "ch"],
  "properties": {
    "v": { "const": 3 },
    "type": { "const": "MEMBERSHIP" },
    "card": { "$ref": "#/definitions/MembershipCard" },
    "proofSig": { 
      "type": "string", 
      "description": "Base64 signature proving card ownership" 
    },
    "ts": { "type": "integer", "minimum": 0 },
    "nonce": { "type": "string", "pattern": "^[a-f0-9]{12}$" },
    "ch": { "type": "string", "pattern": "^[0-9]+$" }
  }
}
```

### 4.3 TRIBE_ACK Message Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TribeAck",
  "type": "object",
  "required": ["v", "type", "from", "to", "ch", "ts", "nonce", "verified", "tier", "sig"],
  "properties": {
    "v": { "const": 3 },
    "type": { "const": "ACK" },
    "from": { "type": "string", "pattern": "^[0-9]+$" },
    "to": { "type": "string", "pattern": "^[0-9]+$" },
    "ch": { "type": "string", "pattern": "^[0-9]+$" },
    "ts": { "type": "integer", "minimum": 0 },
    "nonce": { "type": "string", "pattern": "^[a-f0-9]{12}$" },
    "verified": { "type": "boolean" },
    "tier": { "enum": [1, 2, 3, 4] },
    "reason": { 
      "type": "string",
      "description": "Reason if not verified (e.g., 'unknown_tribe', 'invalid_card', 'expired')"
    },
    "sig": { "type": "string" }
  }
}
```

### 4.4 Keystore Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TribeKeystore",
  "type": "object",
  "required": ["version", "self", "tribe", "trusted"],
  "properties": {
    "version": { "const": "3.0" },
    "self": {
      "type": "object",
      "required": ["name", "discordId", "publicKey", "created"],
      "properties": {
        "name": { "type": "string" },
        "discordId": { "type": "string" },
        "publicKey": { "type": "string" },
        "created": { "type": "string", "format": "date-time" }
      }
    },
    "tribe": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "publicKey": { "type": "string" },
        "isFounder": { "type": "boolean" }
      }
    },
    "trusted": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "discordId", "publicKey", "tier", "addedAt"],
        "properties": {
          "name": { "type": "string" },
          "discordId": { "type": "string" },
          "publicKey": { "type": "string" },
          "tier": { "enum": [2, 3] },
          "addedAt": { "type": "string", "format": "date-time" },
          "cardExpires": { "type": "string", "format": "date-time" }
        }
      }
    }
  }
}
```

---

## 5. Cryptographic Design

### 5.1 Key Types

| Key | Algorithm | Purpose | Who Has It |
|-----|-----------|---------|------------|
| Member Private Key | Ed25519 | Sign proof of card ownership | Each member |
| Member Public Key | Ed25519 | Verify member signatures | All tribe members |
| Tribe Private Key | Ed25519 | Sign membership cards | Founder only |
| Tribe Public Key | Ed25519 | Verify card signatures | All tribe members |

### 5.2 Signing Operations

**Card Issuance (Founder signs card):**
```
payload = "TRIBE_CARD:v3:{tribeId}:{discordId}:{memberPubKey}:{tier}:{issuedAt}:{expiresAt}"
cardSig = Ed25519.sign(tribePrivateKey, payload)
```

**Card Presentation (Member proves ownership):**
```
payload = "CARD_PROOF:v3:{cardSig}:{timestamp}:{nonce}:{channelId}"
proofSig = Ed25519.sign(memberPrivateKey, payload)
```

**ACK Signing:**
```
payload = "TRIBE_ACK:v3:{from}:{to}:{ch}:{ts}:{nonce}:{verified}:{tier}"
sig = Ed25519.sign(memberPrivateKey, payload)
```

### 5.3 Verification Flow

```
Receiver gets TRIBE_MEMBERSHIP message:
  1. Parse JSON, extract card + proofSig
  2. Verify card.cardSig against tribe public key
     → If invalid: NACK with reason "invalid_card"
  3. Check card.expiresAt
     → If expired: NACK with reason "expired"
  4. Check card.member.discordId against sender's Discord ID
     → If mismatch: NACK with reason "id_mismatch"
  5. Reconstruct proof payload from message fields
  6. Verify proofSig against card.member.publicKey
     → If invalid: NACK with reason "invalid_proof"
  7. Check timestamp (within 30 seconds)
     → If stale: NACK with reason "expired_timestamp"
  8. Check nonce not in cache
     → If seen: NACK with reason "replay_detected"
  9. Add nonce to cache
  10. Send ACK with verified=true
```

### 5.4 Tribe ID Generation

```javascript
function getTribeId(tribePubKey) {
  const hash = sha256(tribePubKey);
  return hash.slice(0, 16);  // First 16 hex chars
}
```

---

## 6. Step-by-Step Implementation Order

### Phase 1: Core Crypto (Days 1-2)

**Files:** `lib/crypto.js`, `lib/nonce-cache.js`

1. Implement `generateKeypair()` using `@noble/ed25519`
2. Implement `sign()` and `verify()` functions
3. Implement `formatPublicKey()` / `parsePublicKey()` for human-friendly format
4. Implement NonceCache with TTL-based expiry
5. Write unit tests for all crypto operations

**Dependencies:** `@noble/ed25519`, `@noble/hashes`

### Phase 2: Key Storage (Days 3-4)

**Files:** `lib/keystore.js`, `cli/keygen.js`, `cli/export.js`, `cli/import.js`

1. Implement file-based keystore (read/write JSON)
2. Implement private key file handling (mode 0600)
3. Implement `keygen` CLI command
4. Implement `export` CLI command
5. Implement `import` CLI command
6. Add QR code generation for export
7. Write unit tests for keystore operations

**Dependencies:** `qrcode`

### Phase 3: Membership Cards (Days 5-7)

**Files:** `lib/cards.js`, `cli/issue-card.js`, `cli/accept-card.js`

1. Implement card structure and signing
2. Implement card verification
3. Implement `issueCard()` for founders
4. Implement `acceptCard()` for members
5. Implement card storage and retrieval
6. Implement expiration checking
7. Write unit tests for card operations

### Phase 4: Verification Protocol (Days 8-10)

**Files:** `lib/verification.js`, `cli/status.js`, `cli/verify.js`

1. Implement TRIBE_MEMBERSHIP message builder
2. Implement message parser and validator
3. Implement ACK/NACK message handling
4. Implement session state management
5. Implement `status` CLI command
6. Implement `verify` CLI command
7. Write integration tests

### Phase 5: Relational Maintenance (Days 11-13)

**Files:** `lib/touchpoints.js`, `hooks/tribe-check.js`

1. Implement touchpoint state storage
2. Implement probability-based check-in logic
3. Implement jitter calculation
4. Implement context-weighted probability boost
5. Implement quiet hours handling
6. Implement heartbeat hook
7. Write unit tests for touchpoint logic

### Phase 6: Skill Packaging (Days 14-15)

**Files:** `SKILL.md`, `INSTALL.md`, templates, config

1. Create SKILL.md with manifest
2. Create INSTALL.md with instructions
3. Create template snippets (TRIBE.snippet.md, etc.)
4. Create default config.json
5. Test installation from scratch
6. Document all CLI commands

### Phase 7: Testing & Polish (Days 16-18)

1. Full integration test suite
2. Multi-bot simulation test
3. Error handling improvements
4. Documentation review
5. Edge case handling

---

## 7. Dependencies

### NPM Packages

```json
{
  "dependencies": {
    "@noble/ed25519": "^2.0.0",
    "@noble/hashes": "^1.3.0",
    "qrcode": "^1.5.3"
  },
  "devDependencies": {
    "vitest": "^1.0.0"
  }
}
```

**Why these packages:**

- **@noble/ed25519** — Pure JS Ed25519, audited, no native deps
- **@noble/hashes** — SHA-256 for tribe ID generation
- **qrcode** — QR code generation for key export
- **vitest** — Fast, modern test runner

### System Requirements

- Node.js 18+ (for crypto APIs)
- File system access for key storage
- Discord bot token (for integration)

---

## 8. Testing Strategy

### 8.1 Unit Tests

**`tests/crypto.test.js`**
```javascript
describe('crypto', () => {
  test('generateKeypair creates valid Ed25519 pair');
  test('sign and verify roundtrip');
  test('verify rejects tampered message');
  test('verify rejects wrong public key');
  test('formatPublicKey creates CLAWD-PUB-v1 format');
  test('parsePublicKey extracts components');
  test('parsePublicKey rejects invalid format');
});
```

**`tests/cards.test.js`**
```javascript
describe('cards', () => {
  test('issueCard creates valid card structure');
  test('issueCard signs with tribe key');
  test('verifyCard accepts valid card');
  test('verifyCard rejects tampered card');
  test('verifyCard rejects wrong tribe key');
  test('isExpired returns true for expired cards');
  test('createPresentation proves ownership');
  test('verifyPresentation validates proof');
});
```

**`tests/nonce-cache.test.js`**
```javascript
describe('nonce-cache', () => {
  test('checkAndAdd returns true for fresh nonce');
  test('checkAndAdd returns false for seen nonce');
  test('cleanup removes expired entries');
  test('respects TTL');
});
```

**`tests/verification.test.js`**
```javascript
describe('verification', () => {
  test('sendTribeMembership creates valid message');
  test('handleTribeMembership verifies valid card');
  test('handleTribeMembership rejects invalid card');
  test('handleTribeMembership rejects expired timestamp');
  test('handleTribeMembership rejects replayed nonce');
  test('session state updates on verification');
});
```

### 8.2 Integration Tests

**`tests/integration.test.js`**
```javascript
describe('full flow', () => {
  test('founder creates tribe, issues card, member verifies', async () => {
    // 1. Founder generates keypair with --founder
    // 2. Founder exports tribe public key
    // 3. Member generates keypair
    // 4. Member exports public key
    // 5. Founder issues card to member
    // 6. Member accepts card
    // 7. Both bots exchange TRIBE_MEMBERSHIP
    // 8. Verify session state shows tier 3
  });
  
  test('verification fails for unknown tribe');
  test('verification fails for revoked member');
  test('verification fails for expired card');
  test('graceful degradation for non-v3 bot');
});
```

### 8.3 Simulation Tests

```javascript
describe('multi-bot simulation', () => {
  test('three bots verify in shared channel');
  test('new bot joins mid-session');
  test('bot handles high-frequency messages');
  test('replay attack is rejected');
});
```

---

## 9. Migration from v2

### 9.1 What's Changing

| v2 | v3 |
|----|-----|
| TRIBE.md with Discord IDs | Keystore + membership cards |
| Trust via list membership | Trust via cryptographic verification |
| No session verification | Handshake per session |
| Static trust | Dynamic verification state |

### 9.2 Migration Steps

**Step 1: Generate Keys (Each Bot)**
```bash
clawdbot tribe keygen
```

**Step 2: Designate Founder**
One human runs:
```bash
clawdbot tribe keygen --founder
```

**Step 3: Exchange Keys**
- Founder exports tribe public key
- All members import tribe public key
- Members export their public keys
- Founder imports all member public keys

**Step 4: Issue Cards**
Founder issues cards:
```bash
clawdbot tribe issue-card "CLAWD-PUB-v1:member1:..." --tier 3
clawdbot tribe issue-card "CLAWD-PUB-v1:member2:..." --tier 3
```

**Step 5: Accept Cards**
Each member accepts their card:
```bash
clawdbot tribe accept-card --file ~/my-card.json
```

**Step 6: Update TRIBE.md**
Add v3 configuration section (can coexist with v2):
```markdown
## v3 Configuration

Tribe: enabled
Tribe ID: 7f3a8b2c...
Role: member
Card: ~/.clawd/keys/cards/my-card.json
```

**Step 7: Test**
```bash
clawdbot tribe status
clawdbot tribe verify --channel <test-channel>
```

### 9.3 Backward Compatibility

v3 supports fallback to v2 behavior:
- If other bot doesn't send TRIBE_MEMBERSHIP, use TRIBE.md rules
- If no card configured, behave as v2
- Gradual rollout possible (some bots v2, some v3)

---

## 10. Security Considerations

### 10.1 Threat Model

| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| Impersonation | Card + proof signature | None if keys secure |
| Replay attack | Timestamp + nonce + cache | Negligible |
| Key theft | File permissions, rotation | Rotation needed |
| Card theft | Proof requires private key | None |
| Founder compromise | Card revocation | Must notify tribe |
| MITM key exchange | Out-of-band exchange | Human diligence |

### 10.2 Key Compromise Handling

**Member Key Compromise:**
1. Member notifies founder
2. Founder revokes old card
3. Member generates new keypair
4. Founder issues new card with new public key
5. Tribe members update keystores

**Tribe Key Compromise:**
1. Founder notifies all members
2. Founder generates new tribe keypair
3. Founder re-issues all cards
4. All members accept new cards
5. Old tribe ID becomes invalid

### 10.3 Card Revocation

**Revocation storage: `~/.clawd/revocations.json`**
```json
{
  "version": "1.0",
  "revocations": [
    {
      "discordId": "123456789",
      "revokedAt": "2025-02-02T12:00:00Z",
      "reason": "key_compromised",
      "revokedBy": "founder"
    }
  ]
}
```

**Verification checks revocation list before accepting TRIBE_MEMBERSHIP.**

### 10.4 Key Rotation Protocol

**Annual rotation recommended:**

1. Generate new keypair: `clawdbot tribe keygen --force`
2. Export new public key
3. Share with tribe via secure channel
4. Tribe members import new key, mark old as superseded
5. Request new card from founder with new public key

---

## 11. Relational Maintenance Details

### 11.1 Configuration

**`config.json`:**
```json
{
  "touchpoints": {
    "enabled": true,
    "baseIntervalHours": 48,
    "jitterHours": 24,
    "baseProbability": 0.05,
    "contextBoostMultiplier": 3.0,
    "quietHours": {
      "enabled": true,
      "start": 22,
      "end": 8,
      "timezone": "America/Los_Angeles"
    },
    "topics": {
      "music": ["music", "song", "band", "album", "concert"],
      "tech": ["code", "programming", "AI", "project"],
      "life": ["family", "health", "travel", "food"]
    }
  }
}
```

### 11.2 Probability Calculation

```javascript
function shouldCheckIn(member, currentTopics = []) {
  // Base probability per heartbeat (default: 5%)
  let probability = config.baseProbability;
  
  // Time factor: increases as next check-in approaches
  const hoursSinceLastContact = getHoursSince(member.lastContact);
  const expectedInterval = config.baseIntervalHours;
  const timeFactor = Math.min(hoursSinceLastContact / expectedInterval, 2.0);
  probability *= timeFactor;
  
  // Context boost: related topics increase probability
  const relatedTopics = findRelatedTopics(currentTopics, member.topics);
  if (relatedTopics.length > 0) {
    probability *= config.contextBoostMultiplier;
  }
  
  // Cap at 50%
  probability = Math.min(probability, 0.5);
  
  // Quiet hours: zero probability
  if (isQuietHours()) {
    return false;
  }
  
  // Roll the dice
  return Math.random() < probability;
}
```

### 11.3 Heartbeat Hook

**`hooks/tribe-check.js`:**
```javascript
export async function onHeartbeat(context) {
  const { touchpoints } = await import('../lib/touchpoints.js');
  
  // Get current context topics (from recent messages, if available)
  const currentTopics = context.recentTopics || [];
  
  // Check each tribe member
  const members = await touchpoints.getPendingCheckIns();
  const suggestions = [];
  
  for (const member of members) {
    if (await touchpoints.shouldCheckIn(member.memberId, currentTopics)) {
      const suggestion = await touchpoints.getCheckInSuggestion(member.memberId);
      suggestions.push({ member, suggestion });
    }
  }
  
  return suggestions;
}
```

### 11.4 HEARTBEAT.snippet.md Template

```markdown
## Tribe Check-Ins

- [ ] Review tribe touchpoints: `clawdbot tribe status`
- [ ] If overdue contacts exist, consider reaching out
- [ ] Note: Probability increases with time since last contact
- [ ] Context boost: Related topics in conversation trigger higher chance
```

---

## 12. Skill Manifest

**`SKILL.md`:**
```markdown
# Tribe Protocol v3

**Version:** 3.0.0
**Category:** Security / Identity
**Author:** Cheenu
**Requires:** Node.js 18+, Discord bot

## Description

Cryptographic identity verification for AI agent tribes. Enables:
- Tribe founders to issue signed membership cards
- Members to prove card ownership via signatures
- Replay-protected handshake protocol
- Relational maintenance through probability-based check-ins

## Installation

See INSTALL.md for detailed instructions.

Quick start:
\`\`\`bash
# 1. Install
clawdbot skill install tribe-protocol-v3

# 2. Generate keys
clawdbot tribe keygen

# 3. Check status
clawdbot tribe status
\`\`\`

## Commands

| Command | Description |
|---------|-------------|
| `tribe keygen` | Generate Ed25519 keypair |
| `tribe export` | Export public key for sharing |
| `tribe import` | Import trusted member's key |
| `tribe issue-card` | Issue membership card (founder) |
| `tribe accept-card` | Accept membership card |
| `tribe status` | Show current status |
| `tribe verify` | Manually trigger verification |
| `tribe revoke` | Revoke member/card |

## Configuration

Edit `config.json` to customize:
- Touchpoint intervals and probabilities
- Quiet hours
- Topic categories

## Files

| File | Purpose |
|------|---------|
| `~/.clawd/keys/identity.key` | Your private key |
| `~/.clawd/keys/identity.pub` | Your public key |
| `~/.clawd/keys/tribe.pub` | Tribe public key |
| `~/.clawd/keys/cards/my-card.json` | Your membership card |
| `~/.clawd/tribe-keystore.json` | Member registry |
| `~/.clawd/touchpoints.json` | Check-in state |
```

---

## 13. Summary

This implementation plan provides:

1. **Complete file structure** for the skill package
2. **Module breakdown** with TypeScript interfaces
3. **CLI command specs** with full examples
4. **JSON schemas** for all message types
5. **Cryptographic design** with signing/verification flows
6. **18-day implementation timeline** in phases
7. **Testing strategy** covering unit, integration, and simulation
8. **Migration guide** from v2 to v3
9. **Security analysis** with threat model
10. **Relational maintenance** probability engine
11. **Skill packaging** for ClawdHub distribution

A developer can implement this plan without additional design decisions. Each phase builds on the previous, with clear dependencies and test coverage requirements.

---

*End of Implementation Plan*
