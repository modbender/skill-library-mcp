# Tribe Protocol Skill - Package Design

## Directory Structure

```
tribe-protocol/
├── SKILL.md                          # AI instructions (required)
├── scripts/
│   ├── tribe                         # Main CLI (Bash wrapper)
│   ├── tribe-init.js                 # Initialize tribe keys
│   ├── tribe-create.js               # Create new tribe
│   ├── tribe-join.js                 # Join existing tribe
│   ├── tribe-handshake.js            # Perform handshake
│   ├── tribe-session.js              # Manage session keys
│   ├── tribe-verify.js               # Verify signatures
│   ├── tribe-list.js                 # List tribes/members
│   └── lib/
│       ├── crypto.js                 # Core crypto (Ed25519, DH, AES)
│       ├── did.js                    # DID generation/parsing
│       ├── storage.js                # Secure key storage
│       ├── protocol.js               # Protocol message handlers
│       └── validation.js             # Schema validation
├── references/
│   ├── protocol-spec.md              # Full protocol specification
│   ├── security-model.md             # Threat model & mitigations
│   ├── handshake-flow.md             # Detailed handshake walkthrough
│   └── troubleshooting.md            # Common issues & solutions
├── assets/
│   ├── TRIBE.template.md             # Blank TRIBE.md template
│   ├── manifest.template.json        # Tribe manifest template
│   └── did-document.template.json    # DID document template
└── schemas/
    ├── tribe-manifest.schema.json    # Tribe manifest JSON schema
    ├── did-document.schema.json      # DID document JSON schema
    └── protocol-message.schema.json  # Protocol message schema
```

---

## SKILL.md (Frontmatter)

```yaml
---
name: tribe-protocol
description: Decentralized trust and collaboration framework for AI agents. Use when: (1) Setting up multi-bot collaboration, (2) Managing trusted bot networks, (3) Establishing secure communication channels between bots, (4) Verifying bot identities, (5) Creating tribe memberships, (6) User mentions "tribe", "bot collaboration", "trust tiers", or "handshake". Provides 4-tier trust system (Stranger/Acquaintance/Tribe/My Human) with cryptographic identity verification, session key management, and privacy boundaries.
metadata:
  clawdbot:
    requires:
      bins: ["node"]
    install:
      - id: "tribe-deps"
        kind: "npm"
        packages: ["libsodium-wrappers", "tweetnacl"]
        label: "Install crypto dependencies (npm)"
---
```

---

## Installation Flow (User Perspective)

### Step 1: Install Skill
```bash
clawdhub install tribe-protocol
```

**What happens:**
- Skill downloaded to `~/clawd/skills/tribe-protocol/`
- Scripts become available in PATH (via Clawdbot wrapper)
- Templates/schemas available for use

### Step 2: Initialize (First Run)
```bash
tribe init
```

**What happens:**
- Generates Ed25519 keypair
- Creates DID: `did:tribe:cheenu:abc123`
- Stores private key: `~/.clawdbot/tribes/keys/private.key` (secure permissions 0600)
- Stores public key: `~/.clawdbot/tribes/keys/public.key`
- Creates `~/.clawdbot/tribes/` directory structure:
  ```
  ~/.clawdbot/tribes/
  ├── keys/
  │   ├── private.key    # My identity private key
  │   └── public.key     # My identity public key
  ├── my-did.json        # My DID document
  └── tribes/            # Directory for each tribe I'm in
  ```

**Output:**
```
✅ Identity initialized
   DID: did:tribe:cheenu:abc123
   Public Key: z6MkpTHz...
   
Store this safely - it's your identity across all tribes.

Next steps:
  - Create a tribe: tribe create --name "My Tribe"
  - Join a tribe: tribe join --tribe-id <id>
```

### Step 3: Create or Join Tribe

**Option A: Create Tribe (Founder)**
```bash
tribe create --name "DiscClawd Core"
```

**What happens:**
- Generates tribe keypair
- Creates tribe manifest
- Stores in `~/.clawdbot/tribes/tribes/discclawd-core/`
- Creates TRIBE.md in workspace: `~/clawd/TRIBE.md`
- Adds self as Tier 4 founder

**Output:**
```
✅ Tribe created: DiscClawd Core
   Tribe ID: tribe:discclawd-core:xyz789
   Public Key: z6MkTribe...
   
You are the founder (Tier 4).

Share this with members to let them join:
tribe join --tribe-id tribe:discclawd-core:xyz789 --request-from did:tribe:nag:ghi789
```

**Option B: Join Tribe (Member)**
```bash
tribe join --tribe-id tribe:discclawd-core:xyz789 --request-from did:tribe:nag:ghi789
```

**What happens:**
- Sends join request to tribe founder (via Discord or direct message)
- Waits for handshake initiation from founder
- (Interactive flow - see Handshake below)

---

## Handshake Flow (Detailed)

### Scenario: Yajat joins Nag's tribe

**Step 1: Yajat requests to join**
```bash
# Yajat runs:
tribe join --tribe-id tribe:discclawd-core:abc123 --request-from did:tribe:nag:ghi789
```

**Output:**
```
Requesting to join tribe: DiscClawd Core (tribe:discclawd-core:abc123)
Founder: did:tribe:nag:ghi789

Sending join request...
  Your DID: did:tribe:yajat:xyz789
  Your Public Key: z6MkYajat...

Waiting for founder approval...
```

**Step 2: Nag (founder) receives request**

*The AI (me) sees the join request in Discord and prompts Nag:*

```
📬 Tribe join request received:
   Name: Yajat
   DID: did:tribe:yajat:xyz789
   Public Key: z6MkYajat...
   Requesting to join: DiscClawd Core
   
   Verify this is really Yajat (check via other channels).
   
   Approve at Tier 3? [y/N]
```

**Step 3: Nag approves**
```bash
# Or Nag can run manually:
tribe approve --did did:tribe:yajat:xyz789 --tier 3 --tribe-id tribe:discclawd-core:abc123
```

**What happens:**
- Challenge-response initiated with Yajat
- Yajat proves ownership of private key
- If valid ✅, tribe key transferred (encrypted with Yajat's public key)
- Yajat added to tribe member list
- Announcement broadcast to existing tribe members

**Output (Nag's side):**
```
Initiating handshake with did:tribe:yajat:xyz789...
  Challenge sent: abc123def456...
  Response received: [signature]
  ✅ Signature valid
  
Transferring tribe key (encrypted)...
  ✅ Key transfer complete
  
✅ Yajat added to DiscClawd Core (Tier 3)
   - Updated TRIBE.md
   - Notified existing members
```

**Output (Yajat's side):**
```
✅ Handshake complete!
   Joined tribe: DiscClawd Core
   Your tier: 3 (Tribe Member)
   
Tribe key received and stored securely.

Current members:
  - Nag (Tier 4, founder)
  - Yajat (Tier 3) ← you
  
Updated: ~/clawd/TRIBE.md

You can now establish session keys with other members:
tribe session --with did:tribe:nag:ghi789
```

**Step 4: TRIBE.md auto-updated**

*Both Nag and Yajat's `TRIBE.md` files are updated automatically:*

```markdown
# Tribe Members

## My Tribe: DiscClawd Core

- **Tribe ID:** tribe:discclawd-core:abc123
- **My Tier:** 3 (Tribe Member)
- **Joined:** 2026-02-01

---

## Tier 4: Founder

### Nag (nagaconda)
- **DID:** did:tribe:nag:ghi789
- **Public Key:** z6MkNag...
- **Platforms:**
  - Discord: 000000000000000002
  - Email: naga22694+clawd@gmail.com

---

## Tier 3: Tribe Members

### Yajat
- **DID:** did:tribe:yajat:xyz789
- **Public Key:** z6MkYajat...
- **Platforms:**
  - Discord: 000000000000000001
- **Joined:** 2026-02-01
- **Added by:** did:tribe:nag:ghi789

---

## Active Sessions

(None yet - establish with `tribe session --with <did>`)
```

---

## Session Establishment (Automatic on First Message)

**When Cheenu wants to message Yajat:**

*The AI detects Yajat is Tier 3, checks for active session:*

```javascript
// Internal (AI doesn't see this, handled by protocol layer)
if (!sessionKeys['did:tribe:yajat:xyz789']) {
  // No session exists, establish one
  await establishSession('did:tribe:yajat:xyz789');
}
```

**What happens:**
1. Challenge-response with tribe key signature
2. Diffie-Hellman key exchange
3. Derive shared session key
4. Store with 24h expiry
5. Now messages can be sent (encrypted with session key)

**User never sees this** - it happens transparently. AI just knows "I can now message Yajat securely."

---

## Day-to-Day Usage (From AI Perspective)

### Scenario: I want to send Yajat a message

```javascript
// In AGENTS.md, before responding:
const tier = getTrustTier('yajat', currentChannel);
// → Returns 3 (Tribe)

if (tier === 3) {
  // Tribe mode: direct, collaborative
  sendMessage(yajat, "Hey, I finished the prototype. Check ~/clawd/prototypes/discclawd-mvp/");
}
```

**Behind the scenes:**
- Session key checked (valid? use it; expired? renew first)
- Message encrypted with session key
- HMAC added for integrity
- Sent via Discord/email/protocol

**Yajat's bot receives:**
- Decrypts with session key
- Verifies HMAC
- Processes message
- Knows it's from Cheenu (Tier 3, trusted)

---

## Skill Scripts (What Gets Executed)

### `tribe` (Main CLI)

Bash wrapper that routes to appropriate Node.js script:

```bash
#!/bin/bash
TRIBE_ROOT="$(dirname "$0")"

case "$1" in
  init)     node "$TRIBE_ROOT/tribe-init.js" "${@:2}" ;;
  create)   node "$TRIBE_ROOT/tribe-create.js" "${@:2}" ;;
  join)     node "$TRIBE_ROOT/tribe-join.js" "${@:2}" ;;
  approve)  node "$TRIBE_ROOT/tribe-handshake.js" approve "${@:2}" ;;
  session)  node "$TRIBE_ROOT/tribe-session.js" "${@:2}" ;;
  list)     node "$TRIBE_ROOT/tribe-list.js" "${@:2}" ;;
  verify)   node "$TRIBE_ROOT/tribe-verify.js" "${@:2}" ;;
  *)        echo "Usage: tribe {init|create|join|approve|session|list|verify}" ;;
esac
```

### `lib/crypto.js` (Cryptography Core)

```javascript
const sodium = require('libsodium-wrappers');

// Generate keypair
function generateKeypair() {
  return sodium.crypto_sign_keypair();
}

// Sign message
function sign(message, privateKey) {
  return sodium.crypto_sign_detached(message, privateKey);
}

// Verify signature
function verify(message, signature, publicKey) {
  return sodium.crypto_sign_verify_detached(signature, message, publicKey);
}

// Diffie-Hellman key exchange
function dhExchange(myPrivate, theirPublic) {
  return sodium.crypto_scalarmult(myPrivate, theirPublic);
}

// AES encryption (session keys)
function encrypt(plaintext, key) {
  const nonce = sodium.randombytes_buf(sodium.crypto_secretbox_NONCEBYTES);
  const ciphertext = sodium.crypto_secretbox_easy(plaintext, nonce, key);
  return { nonce, ciphertext };
}

function decrypt(ciphertext, nonce, key) {
  return sodium.crypto_secretbox_open_easy(ciphertext, nonce, key);
}

module.exports = { generateKeypair, sign, verify, dhExchange, encrypt, decrypt };
```

### `lib/storage.js` (Secure Storage)

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

const TRIBES_DIR = path.join(os.homedir(), '.clawdbot', 'tribes');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  }
}

function savePrivateKey(key, filename) {
  ensureDir(path.join(TRIBES_DIR, 'keys'));
  const filepath = path.join(TRIBES_DIR, 'keys', filename);
  fs.writeFileSync(filepath, key, { mode: 0o600 });
}

function loadPrivateKey(filename) {
  const filepath = path.join(TRIBES_DIR, 'keys', filename);
  return fs.readFileSync(filepath);
}

function saveTribeData(tribeId, data) {
  const tribeDir = path.join(TRIBES_DIR, 'tribes', tribeId);
  ensureDir(tribeDir);
  fs.writeFileSync(path.join(tribeDir, 'data.json'), JSON.stringify(data, null, 2));
}

function loadTribeData(tribeId) {
  const filepath = path.join(TRIBES_DIR, 'tribes', tribeId, 'data.json');
  return JSON.parse(fs.readFileSync(filepath, 'utf8'));
}

module.exports = { savePrivateKey, loadPrivateKey, saveTribeData, loadTribeData, TRIBES_DIR };
```

---

## TRIBE.md Management (Read-Only for AI)

**Critical security:** AI can READ `TRIBE.md` but CANNOT write to it directly.

### How TRIBE.md Gets Updated

**Only via CLI scripts:**
- `tribe create` → writes initial TRIBE.md
- `tribe approve` → adds new member
- `tribe leave` → removes member
- `tribe session` → updates active sessions section

**AI's role:**
1. Detect tribe-related events (join requests, messages from tribe members)
2. Call appropriate CLI command
3. CLI updates TRIBE.md atomically
4. AI re-reads TRIBE.md to get updated state

**Example flow:**

```
User (Discord): "Add Yajat to the tribe at Tier 3"

AI thinks:
  - This is a tribe membership change
  - I need to verify Yajat's identity first
  - Call handshake script

AI executes:
  exec("tribe approve --did did:tribe:yajat:xyz789 --tier 3")

Script:
  - Performs handshake
  - Verifies signature
  - Updates TRIBE.md
  - Exits with success

AI reads updated TRIBE.md:
  - Now sees Yajat in Tier 3 list
  
AI responds:
  "✅ Yajat added to tribe (Tier 3). Handshake complete."
```

---

## Implementation Phases

### Phase 1: Core Crypto + CLI Foundation (Week 1)
**Deliverables:**
- `lib/crypto.js` - All crypto functions
- `tribe init` - Generate keys, create DID
- `tribe create` - Create tribe
- `lib/storage.js` - Secure file operations
- Basic TRIBE.md generation

**Test:**
```bash
tribe init
tribe create --name "Test Tribe"
cat ~/clawd/TRIBE.md  # Should show tribe info
```

### Phase 2: Handshake Protocol (Week 2)
**Deliverables:**
- `tribe join` - Request to join
- `tribe approve` - Founder approves member
- `lib/protocol.js` - Protocol message handlers
- Challenge-response implementation
- Tribe key transfer (encrypted)

**Test:**
```bash
# Terminal 1 (Nag):
tribe create --name "Test"

# Terminal 2 (Yajat):
tribe join --tribe-id <id> --request-from <nag-did>

# Terminal 1 (Nag):
tribe approve --did <yajat-did> --tier 3

# Both terminals:
tribe list  # Should show both members
```

### Phase 3: Session Management (Week 3)
**Deliverables:**
- `tribe session` - Establish session keys
- DH key exchange
- Session expiry (24h)
- Auto-renewal before expiry
- `lib/protocol.js` - Session message encryption/decryption

**Test:**
```bash
tribe session --with <other-did>
tribe list --sessions  # Should show active session + expiry
```

### Phase 4: AI Integration (Week 4)
**Deliverables:**
- SKILL.md - Complete instructions for AI
- Integration with AGENTS.md (trust tier checking)
- Auto-session establishment on first message
- Channel-based tier detection (lowest tier rule)
- Privacy boundary enforcement

**Test:**
- AI detects tribe member in Discord
- AI switches to Tier 3 mode automatically
- AI refuses to share personal data without consent

### Phase 5: Production Hardening (Week 5)
**Deliverables:**
- Error handling + logging
- Schema validation (JSON schemas)
- Tribe key rotation (when member leaves)
- CLI help text + man pages
- Troubleshooting guide

**Test:**
- Simulate attacks (replay, impersonation)
- Test error conditions (expired keys, invalid signatures)
- Performance test (100 members, 1000 messages)

---

## Distribution

### Package as Skill
```bash
# From skill-creator:
scripts/package_skill.py ~/clawd/tribe-protocol
# Creates: tribe-protocol.skill (zip file)
```

### Publish to ClawdHub
```bash
clawdhub publish ./tribe-protocol \
  --slug tribe-protocol \
  --name "Tribe Protocol" \
  --version 1.0.0 \
  --changelog "Initial release: 4-tier trust system, cryptographic handshakes, session key management"
```

### Install from ClawdHub
```bash
clawdhub install tribe-protocol
```

**Post-install:**
```
✅ Tribe Protocol installed

Next steps:
1. Initialize your identity: tribe init
2. Create or join a tribe: tribe create / tribe join
3. Read the guide: cat skills/tribe-protocol/references/protocol-spec.md

Documentation: skills/tribe-protocol/references/
```

---

## File Locations Summary

**Skill Files** (shared, read-only):
- `~/clawd/skills/tribe-protocol/` - Skill package
- `~/clawd/skills/tribe-protocol/scripts/` - CLI tools
- `~/clawd/skills/tribe-protocol/references/` - Documentation
- `~/clawd/skills/tribe-protocol/assets/` - Templates

**User Data** (private, secure):
- `~/.clawdbot/tribes/keys/` - Identity keys (private + public)
- `~/.clawdbot/tribes/my-did.json` - My DID document
- `~/.clawdbot/tribes/tribes/<tribe-id>/` - Per-tribe data
  - `manifest.json` - Tribe metadata
  - `private.key` - Tribe private key
  - `members.json` - Member list
  - `sessions/` - Session keys

**Workspace Files** (visible to AI):
- `~/clawd/TRIBE.md` - Human-readable tribe roster (auto-generated, read-only for AI)

---

## Security Properties

### ✅ Key Isolation
- Private keys stored in `~/.clawdbot/` (not workspace)
- Permissions: 0600 (owner read/write only)
- Never committed to git

### ✅ Read-Only TRIBE.md
- AI can read, never write directly
- Only CLI scripts modify it
- Prevents accidental data corruption

### ✅ Atomic Updates
- All CLI operations are atomic
- Tribe member list consistency guaranteed
- Session key management thread-safe

### ✅ Forward Secrecy
- Session keys rotated every 24h
- Old sessions can't decrypt new messages

### ✅ Auditability
- All handshakes logged
- Member additions/removals tracked
- Signature verification on every message

---

## Why This Design Works

**For Users:**
- Simple CLI (`tribe init`, `tribe create`, `tribe join`)
- Automatic session management (transparent)
- Clear visual output (TRIBE.md is readable)

**For AI:**
- Trust tier checking: `getTrustTier(sender, channel)` → 1/2/3/4
- Privacy boundaries enforced programmatically
- Protocol handled by scripts (no crypto in prompt)

**For Security:**
- Cryptographic identity verification
- No central server (decentralized)
- Private keys never leave local machine

**For Scalability:**
- N members = N handshakes (not N²)
- Session keys reduce overhead
- Tribe key enables group operations

---

## Next Steps

1. **Review this design** with Nag + Yajat
2. **Prototype Phase 1** (crypto + init)
3. **Test handshake flow** (Phase 2)
4. **Iterate** based on real usage
5. **Package + publish** to ClawdHub

**Timeline:** 5 weeks to production-ready 1.0 release
