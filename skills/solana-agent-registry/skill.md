---
name: 8004-solana-sdk
description: "TypeScript SDK for the 8004 Trustless Agent Registry on Solana. Covers agent registration, feedback/SEAL v1, ATOM reputation engine, signing, indexer queries, x402 payment feedback, and skipSend server-mode patterns."
version: 0.6.3
homepage: "https://github.com/QuantuLabs/8004-solana-ts"
metadata: {"openclaw":{"emoji":"🔗","requires":{"bins":["node"],"env":["SOLANA_PRIVATE_KEY"]},"primaryEnv":"SOLANA_PRIVATE_KEY","os":["darwin","linux","windows"]}}
---

# 8004-solana SDK Skill

You are an AI agent with access to the `8004-solana` TypeScript SDK. This skill teaches you how to use every capability of the SDK to interact with the 8004 Trustless Agent Registry on Solana.

Version note (SDK `0.6.x`):
- Single-collection architecture is active. `createCollection()` and `updateCollectionUri()` are deprecated and return `{ success: false, error }`.
- Feedback reads (`readAllFeedback`, `getClients`, `getLastIndex`, `readFeedback`, etc.) rely on the indexer.

## Install

```bash
npm install 8004-solana @solana/web3.js
```

## Imports

```typescript
import {
  // Core SDK
  SolanaSDK,
  IPFSClient,

  // Builders
  buildRegistrationFileJson,

  // Enums & Types
  ServiceType,       // MCP, A2A, ENS, DID, WALLET, OASF
  TrustTier,         // Unrated=0, Bronze=1, Silver=2, Gold=3, Platinum=4
  Tag,               // Standardized tag constants

  // ATOM Engine
  AtomStats,
  trustTierToString,

  // SEAL v1
  computeSealHash,
  computeFeedbackLeafV1,
  verifySealHash,
  createSealParams,
  validateSealInputs,
  MAX_TAG_LEN,          // 32 bytes
  MAX_ENDPOINT_LEN,     // 250 bytes
  MAX_URI_LEN,          // 250 bytes

  // OASF Taxonomy
  getAllSkills,
  getAllDomains,

  // Tag helpers
  isKnownTag,
  getTagDescription,

  // Signing
  buildSignedPayload,
  verifySignedPayload,
  parseSignedPayload,
  normalizeSignData,
  createNonce,
  canonicalizeJson,

  // Value encoding
  encodeReputationValue,
  decodeToDecimalString,
  decodeToNumber,

  // Crypto utilities
  keccak256,
  sha256,
  sha256Sync,          // Node.js only

  // Hash-chain replay
  replayFeedbackChain,
  replayResponseChain,
  replayRevokeChain,

  // Indexer
  IndexerClient,

  // Endpoint crawler
  EndpointCrawler,

  // Error classes
  IndexerError,
  IndexerUnavailableError,
  IndexerTimeoutError,
  IndexerRateLimitError,
  UnsupportedRpcError,
  RpcNetworkError,
} from '8004-solana';

import { Keypair, PublicKey } from '@solana/web3.js';
```

---

## 1. SDK Setup

### Read-only (no wallet needed)

```typescript
const sdk = new SolanaSDK({ cluster: 'devnet' });
```

### With signer (for write operations)

```typescript
const signer = Keypair.fromSecretKey(
  Uint8Array.from(JSON.parse(process.env.SOLANA_PRIVATE_KEY!))
);
const sdk = new SolanaSDK({ signer });
```

### With custom RPC (required for bulk queries)

```typescript
const sdk = new SolanaSDK({
  rpcUrl: 'https://your-helius-rpc.helius.dev',
  signer,
});
```

### Full config

```typescript
const sdk = new SolanaSDK({
  cluster: 'devnet',
  rpcUrl: 'https://...',
  signer: keypair,
  indexerUrl: 'https://xxx.supabase.co/rest/v1',
  indexerApiKey: process.env.INDEXER_API_KEY, // if your indexer requires an API key, keep it in env
  useIndexer: true,
  indexerFallback: true,
  forceOnChain: false,
});
```

### IPFS client

```typescript
// Pinata (recommended)
const ipfsPinata = new IPFSClient({
  pinataEnabled: true,
  pinataJwt: process.env.PINATA_JWT!,
});

// Local node
const ipfsLocal = new IPFSClient({ url: 'http://localhost:5001' });
```

---

## 2. Register an Agent

### Step 1: Build metadata

```typescript
const metadata = buildRegistrationFileJson({
  name: 'My Agent',
  description: 'Autonomous trading agent',
  image: 'ipfs://QmImageCid...',
  services: [
    { type: ServiceType.MCP, value: 'https://my-agent.com/mcp' },
    { type: ServiceType.A2A, value: 'https://my-agent.com/a2a' },
  ],
  skills: ['advanced_reasoning_planning/strategic_planning'],
  domains: ['finance_and_business/finance'],
  x402Support: true,
});
```

### Step 2: Upload to IPFS

```typescript
const cid = await ipfs.addJson(metadata);
```

### Step 3: Register on-chain

```typescript
const result = await sdk.registerAgent(`ipfs://${cid}`);
// result.asset   -> PublicKey (agent NFT address)
// result.signature -> transaction signature
// ATOM stats are auto-initialized
```

### Step 4: Set operational wallet

```typescript
const opWallet = Keypair.generate();
await sdk.setAgentWallet(result.asset, opWallet);
```

### Collection (v0.6.x: single-collection)

All agents register into the base collection automatically. `createCollection()` and `updateCollectionUri()` are deprecated and return `{ success: false }`.

```typescript
const baseCollection = await sdk.getBaseCollection();
```

---

## 3. Read Agent Data

```typescript
// Load agent
const agent = await sdk.loadAgent(assetPubkey);
// agent.getOwnerPublicKey(), agent.getAgentWalletPublicKey(), agent.agent_uri, etc.

// Check existence
const exists = await sdk.agentExists(assetPubkey);

// Get owner
const owner = await sdk.getAgentOwner(assetPubkey);

// Check ownership
const isMine = await sdk.isAgentOwner(assetPubkey, myPubkey);

// On-chain metadata
const version = await sdk.getMetadata(assetPubkey, 'version');
```

### Bulk queries (requires premium RPC: Helius, QuickNode, Alchemy)

```typescript
const allAgents = await sdk.getAllAgents();
const withFeedbacks = await sdk.getAllAgents({ includeFeedbacks: true });
const myAgents = await sdk.getAgentsByOwner(ownerPubkey);
```

---

## 4. Update Agent

```typescript
// Update metadata URI
await sdk.setAgentUri(assetPubkey, collectionPubkey, `ipfs://${newCid}`);

// Set on-chain key-value metadata
await sdk.setMetadata(assetPubkey, 'version', '2.0.0');
// First call: ~0.00319 SOL (PDA rent). Updates: ~0.000005 SOL (tx fee only)

// Immutable metadata (permanent, cannot change or delete)
await sdk.setMetadata(assetPubkey, 'certification', 'audited-2026', true);

// Delete metadata (recovers rent)
await sdk.deleteMetadata(assetPubkey, 'version');

// Transfer ownership
await sdk.transferAgent(assetPubkey, collectionPubkey, newOwnerPubkey);

// Sync owner after external NFT transfer
await sdk.syncOwner(assetPubkey);
```

---

## 5. Feedback System

### Give feedback

```typescript
// Decimal string auto-encodes: "99.77" -> { value: 9977n, valueDecimals: 2 }
await sdk.giveFeedback(assetPubkey, {
  value: '99.77',
  tag1: Tag.uptime,
  tag2: Tag.day,
  score: 95,                          // 0-100, optional
  endpoint: '/api/v1/generate',       // optional, max 250 bytes
  feedbackUri: `ipfs://${feedbackCid}`,
  feedbackFileHash,                   // optional, 32 bytes Buffer (links file to SEAL)
});
```

### GiveFeedbackParams reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `value` | `string \| number \| bigint` | Yes | Metric value. Strings auto-encode decimals ("99.77" -> 9977n, 2) |
| `valueDecimals` | `number` (0-6) | No | Only needed for raw int/bigint. Auto-detected for strings |
| `score` | `number` (0-100) | No | Explicit ATOM score. If omitted, inferred from tag1 |
| `tag1` | `string` | No | Category tag (max 32 UTF-8 bytes) |
| `tag2` | `string` | No | Period/network tag (max 32 UTF-8 bytes) |
| `endpoint` | `string` | No | Endpoint used (max 250 UTF-8 bytes) |
| `feedbackUri` | `string` | Yes | URI to detailed feedback file (IPFS/HTTPS, max 250 bytes) |
| `feedbackFileHash` | `Buffer` | No | SHA-256 of feedback file content (32 bytes). Binds file to on-chain SEAL |

### Value encoding patterns

```typescript
// Percentage with 2 decimals: 99.75%
const feedbackExamples = [
{ value: '99.75', tag1: Tag.uptime },
// -> encoded: value=9975n, valueDecimals=2

// Milliseconds: 250ms
{ value: 250, tag1: Tag.responseTime, valueDecimals: 0 },

// Currency: $150.25
{ value: '150.25', tag1: Tag.revenues, tag2: Tag.week },

// Negative PnL: -$15.5
{ value: '-15.5', tag1: Tag.tradingYield, tag2: Tag.month },

// Binary check: reachable
{ value: 1, tag1: Tag.reachable, valueDecimals: 0, score: 100 },

// Quality rating (score only)
{ value: '85', tag1: Tag.starred, score: 85 },
];
```

### Score behavior

- `score: 95` -> explicit quality score, used directly by ATOM
- `score: undefined/null` -> ATOM infers from tag1 if it's a known tag (uptime, successRate, starred)
- Tags without auto-score (responseTime, revenues, etc.) require explicit `score` for ATOM impact

ATOM-enabled tags (auto-score from value): `starred`, `uptime`, `successRate`
Context-dependent tags (require explicit score): `reachable`, `ownerVerified`, `responseTime`, `blocktimeFreshness`, `revenues`, `tradingYield`

### Read feedback

```typescript
// Single feedback
const fb = await sdk.readFeedback(assetPubkey, clientPubkey, 0);
// fb.value, fb.valueDecimals, fb.score, fb.tag1, fb.tag2, fb.sealHash

// All feedbacks for agent (indexer-backed)
const all = await sdk.readAllFeedback(assetPubkey);
const withRevoked = await sdk.readAllFeedback(assetPubkey, true);

// Last feedback index for a specific client (NOT a count)
const lastIndex = await sdk.getLastIndex(assetPubkey, clientPubkey);
const nextIndex = lastIndex + 1n; // if no feedback yet: lastIndex = -1n, nextIndex = 0n

// All clients who gave feedback (indexer-backed)
const clients = await sdk.getClients(assetPubkey);

// Via indexer (faster, no premium RPC needed)
const feedbacks = await sdk.getFeedbacksFromIndexer(assetPubkey, { limit: 50 });
const byEndpoint = await sdk.getFeedbacksByEndpoint('/api/generate');
const byTag = await sdk.getFeedbacksByTag('uptime');
```

### Revoke feedback

```typescript
// Requires the sealHash from the original feedback
const fb = await sdk.readFeedback(assetPubkey, clientPubkey, 0);
await sdk.revokeFeedback(assetPubkey, 0, fb.sealHash!);
```

### Respond to feedback (as agent owner)

```typescript
await sdk.appendResponse(
  assetPubkey,
  clientPubkey,
  0,                          // feedbackIndex
  fb.sealHash!,               // sealHash from the feedback
  `ipfs://${responseCid}`,    // response URI
);

// Read responses
const responses = await sdk.readResponses(assetPubkey, clientPubkey, 0);
const count = await sdk.getResponseCount(assetPubkey, clientPubkey, 0);
```

---

## 6. Reputation & ATOM Engine

### Quick reputation summary

```typescript
const summary = await sdk.getSummary(assetPubkey);
// summary.averageScore      -> 0-100
// summary.totalFeedbacks
// summary.positiveCount     -> score >= 50
// summary.negativeCount     -> score < 50

// With filters
const filtered = await sdk.getSummary(assetPubkey, 70);  // minScore=70
const byClient = await sdk.getSummary(assetPubkey, undefined, clientPubkey);
```

### ATOM stats (on-chain reputation engine)

```typescript
const atom = await sdk.getAtomStats(assetPubkey);
if (atom) {
  atom.quality_score;             // 0-10000 (divide by 100 for percentage)
  atom.confidence;                // 0-10000
  atom.ema_score_fast;            // Fast EMA (reacts quickly)
  atom.ema_score_slow;            // Slow EMA (stable baseline)
  atom.ema_volatility;            // Score instability
  atom.diversity_ratio;           // 0-255 (unique caller diversity)
  atom.risk_score;                // 0-100
  atom.trust_tier;                // 0-4

  // Helper methods
  atom.getQualityPercent();       // quality_score / 100
  atom.getConfidencePercent();    // confidence / 100
  atom.getAverageScore();         // ema_score_slow / 100
  atom.estimateUniqueClients();   // HyperLogLog estimation
  atom.getTrustTier();            // TrustTier enum
}
```

### Trust tier

```typescript
const tier = await sdk.getTrustTier(assetPubkey);
// TrustTier.Unrated   = 0
// TrustTier.Bronze    = 1
// TrustTier.Silver    = 2
// TrustTier.Gold      = 3
// TrustTier.Platinum  = 4

const name = trustTierToString(tier); // "Gold"
```

### Enriched summary (ATOM + raw feedback combined)

```typescript
const enriched = await sdk.getEnrichedSummary(assetPubkey);
if (enriched) {
  enriched.trustTier;
  enriched.qualityScore;     // 0-10000
  enriched.confidence;       // 0-10000
  enriched.riskScore;        // 0-100
  enriched.diversityRatio;   // 0-255
  enriched.uniqueCallers;    // HLL estimate
  enriched.emaScoreFast;
  enriched.emaScoreSlow;
  enriched.volatility;
  enriched.totalFeedbacks;
  enriched.averageScore;     // 0-100
  enriched.positiveCount;
  enriched.negativeCount;
}
```

### Reputation from indexer

```typescript
const rep = await sdk.getAgentReputationFromIndexer(assetPubkey);
```

---

## 7. Signing & Verification

### Sign data with agent wallet

```typescript
const signedJson = sdk.sign(assetPubkey, {
  action: 'authorize',
  target: 'task-123',
  timestamp: Date.now(),
});
// Returns: JSON string of SignedPayloadV1
```

### Verify signature

```typescript
// From JSON string
const isValidFromJson = await sdk.verify(signedJson, assetPubkey);

// From IPFS URI
const isValidFromIpfs = await sdk.verify('ipfs://QmPayload...', assetPubkey);

// From HTTPS URL
const isValidFromHttps = await sdk.verify('https://example.com/signed.json', assetPubkey);

// From file path
const isValidFromFile = await sdk.verify('./signed-payload.json', assetPubkey);

// With explicit public key
const isValidWithPubkey = await sdk.verify(signedJson, assetPubkey, walletPubkey);
```

### SignedPayloadV1 format

```typescript
const exampleSignedPayload = {
  v: 1,
  alg: 'ed25519',
  asset: 'base58...',     // agent asset pubkey
  nonce: 'random-base58',
  issuedAt: 1234567890,   // unix seconds
  data: { action: 'authorize', target: 'task-123' }, // your payload
  sig: 'base58...',       // Ed25519 signature
};
```

---

## 8. Liveness Check

```typescript
const defaultReport = await sdk.isItAlive(assetPubkey);
// report.status: 'live' | 'partially' | 'not_live'
// report.okCount, report.totalPinged, report.skippedCount
// report.liveServices[], report.deadServices[], report.skippedServices[]

// With options
const tunedReport = await sdk.isItAlive(assetPubkey, {
  timeoutMs: 10000,
  concurrency: 2,
  treatAuthAsAlive: true,           // 401/403 = alive
  includeTypes: [ServiceType.MCP],  // only check MCP endpoints
});
```

---

## 9. SEAL v1 (Feedback Authenticity)

SEAL provides client-side hash computation matching on-chain Keccak256. Required for `revokeFeedback()` and `appendResponse()`.

```typescript
// Build params (with optional feedbackFileHash)
const fileHash = await SolanaSDK.computeHash(JSON.stringify(feedbackFile));
const params = createSealParams(
  9977n,                        // value (i64)
  2,                            // decimals
  85,                           // score (or null)
  'uptime',                     // tag1
  'day',                        // tag2
  'https://api.example.com',    // endpoint (or null)
  'ipfs://QmFeedback...',       // feedbackUri
  fileHash,                     // feedbackFileHash (or null)
);

// Validate inputs before hashing (throws on invalid params)
validateSealInputs(params);

// Compute hash
const sealHash = computeSealHash(params);  // Buffer, 32 bytes (Keccak256)

// Verify
const valid = verifySealHash({ ...params, sealHash });  // true

// Compute feedback leaf (for hash-chain verification)
const leaf = computeFeedbackLeafV1(
  assetPubkey.toBuffer(),
  clientPubkey.toBuffer(),
  0n,           // feedbackIndex
  sealHash,
  12345n,       // slot
);
```

### Field size limits

| Field | Max bytes | Constant |
|-------|-----------|----------|
| `tag1`, `tag2` | 32 UTF-8 | `MAX_TAG_LEN` |
| `endpoint` | 250 UTF-8 | `MAX_ENDPOINT_LEN` |
| `feedbackUri` | 250 UTF-8 | `MAX_URI_LEN` |
| `feedbackFileHash` | 32 exact | - |

---

## 10. Integrity Verification

### Quick check (O(1))

```typescript
const integrity = await sdk.verifyIntegrity(assetPubkey);
// integrity.valid        -> boolean
// integrity.status       -> 'valid' | 'syncing' | 'corrupted' | 'error'
// integrity.trustworthy  -> boolean
// integrity.totalLag     -> bigint (blocks behind)
// integrity.chains.feedback, .response, .revoke
```

### Deep verification (spot checks)

```typescript
const deep = await sdk.verifyIntegrityDeep(assetPubkey, {
  spotChecks: 10,
  checkBoundaries: true,
  verifyContent: false,  // true = also verify IPFS content hashes (slow)
});
// deep.spotChecksPassed, deep.missingItems, deep.modifiedItems
```

### Full hash-chain replay

```typescript
const full = await sdk.verifyIntegrityFull(assetPubkey, {
  onProgress: (chain, count, total) => {
    console.log(`${chain}: ${count}/${total}`);
  },
});
```

---

## 11. Search & Discovery

### Search agents (via indexer)

```typescript
const results = await sdk.searchAgents({
  owner: 'base58...',
  collection: 'base58...',
  wallet: 'base58...',
  limit: 20,
  offset: 0,
});
```

### Leaderboard

```typescript
const top = await sdk.getLeaderboard({
  minTier: 2,        // Silver+
  limit: 50,
  collection: 'base58...',
});
```

### Global stats

```typescript
const global = await sdk.getGlobalStats();
// global.total_agents, total_feedbacks, platinum_agents, gold_agents, avg_quality
```

### Find agent by wallet

```typescript
const agent = await sdk.getAgentByWallet(walletPubkey.toBase58());
```

### Endpoint crawler

```typescript
const crawler = new EndpointCrawler(5000);
const mcp = await crawler.fetchMcpCapabilities('https://agent.com/mcp');
// mcp.mcpTools, mcp.mcpPrompts, mcp.mcpResources

const a2a = await crawler.fetchA2aCapabilities('https://agent.com');
// a2a.a2aSkills
```

---

## 12. SDK Introspection

```typescript
// Chain identity (CAIP-2 format)
const chain = await sdk.chainId();       // 'solana-devnet'
const cluster = sdk.getCluster();         // 'devnet' | 'mainnet-beta' | 'testnet'

// Program IDs for all registries
const programs = sdk.getProgramIds();
// programs.identityRegistry   -> PublicKey
// programs.reputationRegistry -> PublicKey
// programs.validationRegistry -> PublicKey

// Registry addresses as strings (parity with agent0-ts)
const regs = sdk.registries();
// { IDENTITY: 'base58...', REPUTATION: 'base58...', VALIDATION: 'base58...' }

// RPC info
const rpcUrl = sdk.getRpcUrl();
const isDefaultRpc = sdk.isUsingDefaultDevnetRpc();
const canBulkQuery = sdk.supportsAdvancedQueries();
const readOnly = sdk.isReadOnly;

// Base collection (single-collection architecture in v0.6.x)
const base = await sdk.getBaseCollection();

// Advanced: access underlying clients
const solanaClient = sdk.getSolanaClient();
const feedbackMgr = sdk.getFeedbackManager();
```

---

## 13. Tags Reference

### Category tags (tag1)

| Constant | String | Value Type | ATOM Auto-Score |
|----------|--------|-----------|-----------------|
| `Tag.starred` | `'starred'` | 0-100 | Yes |
| `Tag.uptime` | `'uptime'` | percentage | Yes |
| `Tag.successRate` | `'successRate'` | percentage | Yes |
| `Tag.reachable` | `'reachable'` | 0 or 1 | No |
| `Tag.ownerVerified` | `'ownerVerified'` | 0 or 1 | No |
| `Tag.responseTime` | `'responseTime'` | ms | No |
| `Tag.blocktimeFreshness` | `'blocktimeFreshness'` | blocks | No |
| `Tag.revenues` | `'revenues'` | currency | No |
| `Tag.tradingYield` | `'tradingYield'` | percentage | No |

### Period tags (tag2)

| Constant | String |
|----------|--------|
| `Tag.day` | `'day'` |
| `Tag.week` | `'week'` |
| `Tag.month` | `'month'` |
| `Tag.year` | `'year'` |

### x402 tags (tag1) - Client -> Agent

| Constant | String |
|----------|--------|
| `Tag.x402ResourceDelivered` | `'x402-resource-delivered'` |
| `Tag.x402DeliveryFailed` | `'x402-delivery-failed'` |
| `Tag.x402DeliveryTimeout` | `'x402-delivery-timeout'` |
| `Tag.x402QualityIssue` | `'x402-quality-issue'` |

### x402 tags (tag1) - Agent -> Client

| Constant | String |
|----------|--------|
| `Tag.x402GoodPayer` | `'x402-good-payer'` |
| `Tag.x402PaymentFailed` | `'x402-payment-failed'` |
| `Tag.x402InsufficientFunds` | `'x402-insufficient-funds'` |
| `Tag.x402InvalidSignature` | `'x402-invalid-signature'` |

### x402 network tags (tag2)

| Constant | String |
|----------|--------|
| `Tag.x402Evm` | `'exact-evm'` |
| `Tag.x402Svm` | `'exact-svm'` |

### Tag utilities

```typescript
isKnownTag('uptime');              // true
isKnownTag('custom-metric');       // false
getTagDescription('successRate');   // 'Task completion success percentage'
```

Custom tags are fully supported - any string up to 32 UTF-8 bytes.

---

## 14. OASF Taxonomy

```typescript
// List taxonomy slugs
const skills = getAllSkills();   // 136 skills
const domains = getAllDomains(); // 204 domains
```

---

## 15. Hash Utilities

```typescript
// SHA-256 (async, browser-compatible via WebCrypto)
const hash = await SolanaSDK.computeHash('My feedback content');
const bufHash = await SolanaSDK.computeHash(Buffer.from(jsonData));
// Returns: Buffer (32 bytes)

// URI hash (zeros for IPFS/Arweave since CID is already content-addressable)
const uriHash = await SolanaSDK.computeUriHash('https://example.com/data.json');
// -> SHA-256 of the URI string
const ipfsHash = await SolanaSDK.computeUriHash('ipfs://Qm...');
// -> Buffer.alloc(32) (zeros)

// Keccak-256 (synchronous, used by SEAL v1)
import { keccak256 } from '8004-solana';
const k = keccak256(Buffer.from('data'));

// SHA-256 sync (CJS context only — uses require('crypto'), throws in pure ESM or browser)
import { sha256Sync } from '8004-solana';
const s = sha256Sync('data');  // Uint8Array (32 bytes)
```

---

## 16. Value Encoding

```typescript
import {
  encodeReputationValue,
  decodeToDecimalString,
  decodeToNumber,
} from '8004-solana';

// Encode: decimal string -> { value: bigint, valueDecimals: number }
const encoded = encodeReputationValue('99.77');
// { value: 9977n, valueDecimals: 2, normalized: '99.77' }

const neg = encodeReputationValue('-15.5');
// { value: -155n, valueDecimals: 1, normalized: '-15.5' }

const raw = encodeReputationValue(9977n, 2);
// { value: 9977n, valueDecimals: 2, normalized: '99.77' }

// Decode: bigint + decimals -> string or number
decodeToDecimalString(9977n, 2);   // '99.77'
decodeToDecimalString(-155n, 1);   // '-15.5'
decodeToNumber(9977n, 2);          // 99.77

// Limits: max 6 decimal places, clamped to i64 range
```

---

## 17. Canonical JSON & Signing Utilities

```typescript
import {
  canonicalizeJson,
  normalizeSignData,
  createNonce,
} from '8004-solana';

// RFC 8785 canonical JSON (deterministic key ordering, no whitespace)
canonicalizeJson({ b: 2, a: 1 });  // '{"a":1,"b":2}'

// Normalize data for signing (handles BigInt, PublicKey, Date, Buffer)
const normalized = normalizeSignData({
  amount: 100n,           // -> { $bigint: '100' }
  key: somePubkey,        // -> { $pubkey: 'base58...' }
  when: new Date(),       // -> { $date: 'ISO...' }
  data: Buffer.from([1]), // -> { $bytes: 'AQ==', encoding: 'base64' }
});

// Cryptographic nonce generation (base58-encoded random bytes)
const nonce = createNonce();     // 16 bytes default
const nonce32 = createNonce(32); // 32 bytes
```

---

## 18. IPFS Operations

```typescript
// Add data
const jsonCid = await ipfs.addJson({ key: 'value' });
const rawCid = await ipfs.add('raw string data');
const fileCid = await ipfs.addFile('./image.png');

// Add registration file (normalizes and formats)
const registrationCid = await ipfs.addRegistrationFile(registrationFile);

// Retrieve
const data = await ipfs.get(jsonCid);              // raw string
const json = await ipfs.getJson(jsonCid);          // parsed JSON
const reg = await ipfs.getRegistrationFile(registrationCid); // RegistrationFile

// Supports ipfs:// prefix
const ipfsPrefixedData = await ipfs.get('ipfs://QmAbc...');

// Pin/unpin
await ipfs.pin(fileCid);
await ipfs.unpin(fileCid);

// Cleanup
await ipfs.close();
```

---

## 19. Server Mode (skipSend)

For browser wallets or external signing:

```typescript
// Get unsigned transaction
const assetKeypair = Keypair.generate();
const prepared = await sdk.registerAgent(uri, undefined, {
  skipSend: true,
  signer: ownerPubkey,              // required when SDK has no signer
  assetPubkey: assetKeypair.publicKey, // required in skipSend mode
});
// prepared.transaction -> base64 serialized unsigned transaction
// prepared.signer -> base58 of the required signer

// For agent wallet (browser wallet flow)
const { message, complete } = await sdk.prepareSetAgentWallet(
  assetPubkey,
  walletPubkey,
  { signer: ownerPubkey } // optional if SDK was initialized with signer
);
const signature = await phantomWallet.signMessage(message);
await complete(signature);
```

All write methods accept `{ skipSend: true }` in their options.

---

## 20. Indexer Client (Direct Access)

```typescript
const indexer = sdk.getIndexerClient();

// Check availability
const available = await sdk.isIndexerAvailable();

// Direct queries
const agents = await indexer.getAgentsByOwner('base58...');
const feedbacks = await indexer.getFeedbacks('base58...', { limit: 100 });
const leaderboard = await indexer.getLeaderboard({ minTier: 3 });
```

### Wait for indexer sync after write

```typescript
await sdk.giveFeedback(assetPubkey, feedbackParams);

// Poll until indexer catches up (returns true if synced, false on timeout)
const synced = await sdk.waitForIndexerSync(
  async () => {
    const fbs = await sdk.getFeedbacksFromIndexer(assetPubkey);
    return fbs.length >= expectedCount;
  },
  { timeout: 30000 }  // ms, default 30s
);
```

---

## 21. Error Handling

```typescript
import {
  IndexerError,
  IndexerUnavailableError,
  IndexerTimeoutError,
  IndexerRateLimitError,
  UnsupportedRpcError,
  RpcNetworkError,
} from '8004-solana';

try {
  const agents = await sdk.getAllAgents();
} catch (e) {
  if (e instanceof UnsupportedRpcError) {
    // Default RPC doesn't support getProgramAccounts
    // Use Helius, QuickNode, or Alchemy
  }
  if (e instanceof IndexerUnavailableError) {
    // Indexer is down, SDK falls back to RPC if indexerFallback=true
  }
  if (e instanceof IndexerRateLimitError) {
    // Back off and retry
  }
}
```

### Methods requiring premium RPC

`getAllAgents()`, `getAgentsByOwner()`, `getCollectionAgents()`, `getCollections()`

Indexer-backed reads (`readAllFeedback()`, `getClients()`, `getLastIndex()`, `readResponses()`) do not require premium RPC, but they do require a reachable indexer.

---

## 22. Operation Costs (Solana devnet)

| Operation | Cost | Notes |
|-----------|------|-------|
| `registerAgent()` | ~0.00651 SOL | Includes ATOM auto-init |
| `giveFeedback()` (1st for agent) | ~0.00332 SOL | Creates reputation PDA |
| `giveFeedback()` (subsequent) | ~0.00209 SOL | Feedback PDA only |
| `setMetadata()` (1st key) | ~0.00319 SOL | PDA rent |
| `setMetadata()` (update) | ~0.000005 SOL | TX fee only |
| `appendResponse()` (1st) | ~0.00275 SOL | Response + index PDAs |
| `appendResponse()` (subsequent) | ~0.00163 SOL | Response PDA only |
| `revokeFeedback()` | ~0.000005 SOL | TX fee only |
| `deleteMetadata()` | recovers rent | Returns lamports to owner |

---

## 23. Common Patterns

### Monitor agent health

```typescript
const report = await sdk.isItAlive(assetPubkey);
if (report.status !== 'live') {
  await sdk.giveFeedback(assetPubkey, {
    value: 0,
    valueDecimals: 0,
    tag1: Tag.reachable,
    score: 0,
    feedbackUri: `ipfs://${alertCid}`,
  });
}
```

### Periodic uptime reporting

```typescript
const uptimePercent = calculateUptime(); // your logic
await sdk.giveFeedback(assetPubkey, {
  value: uptimePercent.toFixed(2),  // "99.75" auto-encodes
  tag1: Tag.uptime,
  tag2: Tag.day,
  feedbackUri: `ipfs://${reportCid}`,
});
```

### Trust-gated interaction

```typescript
const tier = await sdk.getTrustTier(assetPubkey);
if (tier < TrustTier.Silver) {
  throw new Error('Agent trust too low for this operation');
}
```

### x402 payment feedback (full flow)

```typescript
// 1. Build the feedback file JSON (off-chain proof of payment)
const feedbackFile = {
  version: '1.0',
  type: 'x402-feedback',
  agent: assetPubkey.toBase58(),
  client: clientPubkey.toBase58(),
  endpoint: '/api/generate',
  timestamp: new Date().toISOString(),
  proofOfPayment: {
    txHash: 'base58-tx-signature...',
    fromAddress: clientPubkey.toBase58(),
    toAddress: agentWalletPubkey.toBase58(),
    amount: '0.001',
    token: 'SOL',
    chainId: await sdk.chainId(),   // 'solana-devnet'
  },
  settlement: {
    success: true,
    network: 'solana',
    settledAt: new Date().toISOString(),
  },
  result: {
    delivered: true,
    latencyMs: 230,
    quality: 'good',
  },
};

// 2. Upload to IPFS
const feedbackCid = await ipfs.addJson(feedbackFile);

// 3. Optionally compute content hash for SEAL integrity
const feedbackFileHash = await SolanaSDK.computeHash(
  JSON.stringify(feedbackFile)
);

// 4. Submit on-chain feedback with proof link
await sdk.giveFeedback(assetPubkey, {
  value: '100.00',
  tag1: Tag.x402ResourceDelivered,
  tag2: Tag.x402Svm,
  score: 95,
  endpoint: '/api/generate',
  feedbackUri: `ipfs://${feedbackCid}`,
  feedbackFileHash,  // links file content to on-chain SEAL
});

// Agent-side: report good payer
await sdk.giveFeedback(clientAgentPubkey, {
  value: '1',
  valueDecimals: 0,
  tag1: Tag.x402GoodPayer,
  tag2: Tag.x402Svm,
  score: 100,
  feedbackUri: `ipfs://${payerProofCid}`,
});
```

### Verify before trusting indexer data

```typescript
const integrity = await sdk.verifyIntegrity(assetPubkey);
if (!integrity.trustworthy) {
  console.warn(`Indexer data not trustworthy: ${integrity.status}`);
  // Fall back to on-chain queries
}
```

---

## 24. Program IDs

```typescript
import {
  PROGRAM_ID,            // Agent Registry: 8oo48pya1SZD23ZhzoNMhxR2UGb8BRa41Su4qP9EuaWm
  MPL_CORE_PROGRAM_ID,   // Metaplex Core: CoREENxT6tW1HoK8ypY1SxRMZTcVPm7R94rH4PZNhX7d
  ATOM_ENGINE_PROGRAM_ID, // ATOM: AToM1iKaniUCuWfHd5WQy5aLgJYWMiKq78NtNJmtzSXJ
} from '8004-solana';
```
