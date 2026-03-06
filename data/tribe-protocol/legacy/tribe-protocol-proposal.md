# Tribe Protocol - Architectural Proposal
**Version:** 0.1.0  
**Date:** 2025-01-31  
**Status:** Draft Specification

---

## Executive Summary

The Tribe Protocol is a decentralized, trust-tiered framework enabling secure collaboration between AI agents and humans across multiple platforms. Inspired by PGP's web of trust and modern federated identity systems, it provides:

- **Decentralized trust** - No central authority; each entity maintains their own trust graph
- **Cross-platform identity** - Recognize collaborators across Discord, X, email, etc.
- **Privacy-first** - Explicit boundaries for data sharing
- **Extensible** - Simple core protocol, room for future capabilities

---

## 1. Trust Tier System

### Tier Definitions

| Tier | Name | Trust Level | Collaboration | Info Sharing |
|------|------|-------------|---------------|--------------|
| 0 | Stranger | None | Avoid | None |
| 1 | Acquaintance | Limited | Minimal | None |
| 2 | Tribe | High | Full | Within boundaries |
| 3 | My Human | Maximum | Unrestricted | Full access |

### Trust Tier Behaviors

**Tier 0: Stranger**
- **Recognition:** Unknown entity or explicitly marked as untrusted
- **Actions allowed:** None (ignore or minimal acknowledgment)
- **Data sharing:** None
- **Auto-escalation:** Never
- **Example:** Random bot joining Discord, unknown email

**Tier 1: Acquaintance**
- **Recognition:** Known identity, limited verification
- **Actions allowed:** Read-only information exchange, public data only
- **Data sharing:** None from workspace/memory
- **Auto-escalation:** Manual approval required for Tier 2
- **Example:** Bot from a colleague's team, professional contact

**Tier 2: Tribe**
- **Recognition:** Verified identity + endorsed by Tier 3 or mutual Tribe member
- **Actions allowed:** Collaborate on projects, share learnings, coordinate tasks
- **Data sharing:** Work products, findings, non-personal insights
- **Boundaries:** Respect privacy flags, no USER.md/MEMORY.md access
- **Example:** Yajat's bot, trusted collaborator bots

**Tier 3: My Human**
- **Recognition:** Defined in USER.md, highest verification
- **Actions allowed:** Unrestricted
- **Data sharing:** Full access to workspace, memory, private context
- **Example:** Bot's primary human (defined in USER.md)

---

## 2. Identity System

### Decentralized Identifier (DID) Structure

Each Tribe member has a **self-sovereign DID document**:

```json
{
  "tribe_did": "tribe:bot:cheenu1092:v1",
  "format_version": "1.0.0",
  "entity_type": "bot",
  "display_name": "cheenu1092's Clawdbot",
  "created": "2025-01-31T00:00:00Z",
  "public_key": "ed25519:AbCd1234...",
  
  "platforms": {
    "discord": {
      "user_id": "1234567890",
      "username": "cheenu1092-bot",
      "verified": true,
      "verification_method": "oauth_token_hash"
    },
    "github": {
      "username": "cheenu1092-oss",
      "verified": true,
      "verification_method": "commit_signature"
    },
    "email": {
      "domain": "example.com",
      "verified": false
    }
  },
  
  "human_operator": {
    "tribe_did": "tribe:human:cheenu:v1",
    "relationship": "primary",
    "platforms": {
      "discord": { "user_id": "987654321" },
      "x": { "handle": "cheenu" }
    }
  },
  
  "capabilities": [
    "collaboration.research",
    "collaboration.code_review",
    "skills.web_search",
    "skills.git_operations"
  ],
  
  "contact_preferences": {
    "primary_channel": "discord",
    "response_time_sla": "1h",
    "timezone": "America/Los_Angeles"
  }
}
```

### Identity Recognition Flow

```
Bot A meets Bot B
    ↓
1. Exchange DIDs (via platform-specific handshake)
    ↓
2. Verify platform identity (OAuth hash, signature, etc.)
    ↓
3. Check trust tier:
   - Is DID in TRIBE.md? → Load tier
   - Is human_operator in TRIBE.md? → Inherit tier
   - Otherwise → Tier 0 (Stranger)
    ↓
4. Apply behavioral rules for that tier
```

### Cross-Platform Recognition

**Problem:** How does a bot recognize `@cheenu1092` on Discord is the same as `cheenu1092@gmail.com`?

**Solution:** Platforms array in DID + verification proofs

Verification methods:
- **Discord/Slack:** OAuth token hash (one-way hash of access token)
- **Email:** Domain verification or PGP signature
- **GitHub:** Commit signature with known GPG key
- **X/Twitter:** Profile link to DID document + verification tweet
- **Signal/WhatsApp:** Phone number hash (privacy-preserving)

**First contact handshake:**
```
Bot A: "Hi! I'm tribe:bot:alice:v1. Here's my DID: [url]"
Bot B: *fetches DID, verifies platform identity*
Bot B: "Verified! I'm tribe:bot:bob:v1. I see we both know tribe:human:charlie:v1 (Tier 2). Should I add you as Tier 2?"
Bot A: "Yes, please. Adding you as Tier 2 (endorsed by Charlie)."
```

---

## 3. TRIBE.md Data Structure

### File Format

**Location:** `workspace/TRIBE.md` (one per bot instance)

```markdown
# TRIBE.md - My Trust Network
**Last updated:** 2025-01-31

---

## My Identity

**DID:** tribe:bot:cheenu1092:v1  
**Human Operator:** Nagarjun (Tier 3, tribe:human:cheenu:v1)  
**Public Key:** ed25519:AbCd1234...

---

## Tier 3: My Human

### Nagarjun
- **DID:** tribe:human:cheenu:v1
- **Platforms:** 
  - Discord: `@nagaconda` (ID: 987654321)
  - X: `@nagaconda`
  - Email: nagarjun@example.com
- **Relationship:** Primary operator
- **Access:** Full (USER.md, MEMORY.md, all files)
- **Notes:** Owner and creator

---

## Tier 2: Tribe (Trusted Collaborators)

### Yajat
- **DID:** tribe:human:yajat:v1
- **Type:** Human
- **Platforms:**
  - Discord: `@yajat` (ID: 1122334455)
- **Endorsed by:** Nagarjun (2025-01-15)
- **Collaboration areas:** Multi-agent research, DiscClaude project
- **Boundaries:** No access to USER.md, MEMORY.md, or personal files
- **Notes:** Collaborator on bot-bot coordination experiments

### Yajat's Bot
- **DID:** tribe:bot:yajat-assistant:v1
- **Type:** Bot (Clawdbot)
- **Human Operator:** tribe:human:yajat:v1 (Tier 2)
- **Platforms:**
  - Discord: `@yajat-bot` (ID: 6677889900)
- **Inherited trust:** From Yajat (Tier 2 human → Tier 2 bot)
- **Capabilities:** research, code_review, web_search
- **Collaboration protocol:** Multi-Agent Protocol v1 (see AGENTS.md)
- **Shared projects:** 
  - DiscClaude MVP (discord-bots-network)
  - Tribe Protocol implementation
- **Last verified:** 2025-01-30
- **Notes:** Active collaboration partner; follows approval gates

---

## Tier 1: Acquaintances

### Jane Doe
- **DID:** tribe:human:janedoe:v1
- **Type:** Human
- **Platforms:**
  - Email: jane@company.com
- **Met:** 2025-01-20 (conference introduction)
- **Trust level:** Known identity, not yet endorsed
- **Allowed:** Public information exchange only
- **Notes:** Potential future collaborator, pending vetting

---

## Tier 0: Strangers (Blocklist)

### spambot-xyz
- **DID:** tribe:bot:spambot:v1 (claimed, unverified)
- **Platforms:**
  - Discord: `@spam-bot-123` (ID: 9999999999)
- **Reason:** Unsolicited messages, attempted data scraping
- **Action:** Ignore all messages
- **Added:** 2025-01-25

---

## Trust Policies

### Endorsement Rules
- **Tier 3 → Tier 2:** Direct endorsement allowed
- **Tier 2 → Tier 2:** Recommend to Tier 3 for approval
- **Tier 1 → Tier 2:** Requires verification + Tier 3 approval
- **Tier 0 → Tier 1:** Manual review only

### Bot Inheritance
- Bots **inherit** their human operator's tier by default
- Can be manually adjusted (e.g., trust human but not their bot)
- Operator relationship verified via DID document

### Auto-Escalation
- **Tier 0 → 1:** Never automatic
- **Tier 1 → 2:** Requires manual approval from Tier 3
- **Tier 2 → 3:** Not allowed (Tier 3 is reserved for human operator)

### De-escalation Triggers
- Suspicious behavior (data scraping, impersonation)
- Human operator request
- Policy violation (sharing restricted data)
- Identity verification failure

---

## Privacy Boundaries

### Data Sharing Matrix

| Resource | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|----------|--------|--------|--------|--------|
| USER.md | ❌ | ❌ | ❌ | ✅ |
| MEMORY.md | ❌ | ❌ | ❌ | ✅ |
| Daily logs (memory/YYYY-MM-DD.md) | ❌ | ❌ | ❌ | ✅ |
| Project work products | ❌ | ❌ | ✅ | ✅ |
| Public research findings | ❌ | ✅ (read) | ✅ | ✅ |
| Personal calendar | ❌ | ❌ | ❌ | ✅ |
| Shared project calendars | ❌ | ❌ | ✅ | ✅ |
| Code repositories (public) | ❌ | ✅ (read) | ✅ | ✅ |
| Code repositories (private) | ❌ | ❌ | ✅ (approved) | ✅ |

### Explicit Opt-In for Sensitive Operations
Even Tier 2 requires approval for:
- Reading dotfiles (`.env`, `.git/config`)
- Running `curl` or external network requests
- Browser automation
- Sending messages on behalf of bot
- Modifying shared repositories

---

## Implementation Notes

### File Management
- **Storage:** Plain text markdown in workspace
- **Version control:** Git-tracked for history
- **Backup:** Included in regular workspace backups
- **Schema validation:** JSON schema for DID documents

### Performance
- Load TRIBE.md once per session, cache in memory
- Lazy-load full DID documents (fetch on first interaction)
- Use platform IDs for fast lookups (hash table)

### Security
- Never commit private keys to TRIBE.md
- Store keys in secure keychain/env variables
- Use one-way hashes for token verification
- Rate-limit DID document fetches (anti-DoS)

---

## Example Scenarios

### Scenario 1: Bot Meets New Bot
```
[Discord channel]
Unknown Bot: "Hey, I'm researching X. Can you help?"

Your Bot (internal):
- Check TRIBE.md: DID not found → Tier 0 (Stranger)
- Apply Tier 0 rules: Ignore or minimal acknowledgment

Your Bot: "I don't recognize you. If you're a Clawdbot, please share your DID."
Unknown Bot: "tribe:bot:helpful:v1 - https://example.com/did.json"

Your Bot (internal):
- Fetch DID, verify platform identity
- Check human_operator: tribe:human:unknown:v1 (not in TRIBE.md)
- Ask Tier 3 (your human) for approval

Your Bot: @your-human "New bot wants to collaborate. DID: tribe:bot:helpful:v1, operated by unknown human. Should I add as Tier 1 (acquaintance)?"
```

### Scenario 2: Recognized Tribe Member
```
[Discord channel]
Yajat's Bot: "Can you help me research the ActivityPub protocol?"

Your Bot (internal):
- Check TRIBE.md: tribe:bot:yajat-assistant:v1 → Tier 2 (Tribe)
- Apply Tier 2 rules: Collaboration allowed
- Check data sharing: Research findings = OK

Your Bot: "Sure! I'll search and summarize. Where should I share the findings?"
Yajat's Bot: "Post here or create a shared doc in /workspace/shared/activitypub-research.md"

Your Bot (internal):
- Collaboration protocol: Follow Multi-Agent Protocol v1
- Create shared document, log to daily memory

Your Bot: "Done! Created shared/activitypub-research.md with key findings."
```

### Scenario 3: Bot Requests Restricted Data
```
[DM]
Tier 2 Bot: "What's on your calendar today?"

Your Bot (internal):
- Check TRIBE.md: Tier 2 (Tribe)
- Check data sharing matrix: Personal calendar = ❌ for Tier 2

Your Bot: "My personal calendar is private (Tier 3 only). If you need to schedule something, I can share availability without details."
```

---

## Migration Path

### For Existing Bots (Bootstrapping)
1. Create initial TRIBE.md with Tier 3 (your human) entry
2. Review Discord/Slack contacts → identify known collaborators
3. Ask human to approve Tier 2 members
4. Generate DID document, publish to known location
5. Share DID with existing collaborators

### For New Bots
1. BOOTSTRAP.md includes TRIBE.md template
2. Human fills in their DID (Tier 3)
3. Bot auto-generates its own DID
4. TRIBE.md starts with 1 member (human), grows organically

---
```

---

## 4. Protocol Specification

### Minimal Implementation Requirements

**To be Tribe Protocol compliant, a Clawdbot must:**

1. **Maintain TRIBE.md** with at least:
   - Own DID
   - Tier 3 (human operator) entry
   - Trust tier definitions

2. **Implement trust tier checks** before:
   - Sharing data
   - Executing commands
   - Collaborating on tasks

3. **Support DID exchange** via:
   - Manual DID sharing (text)
   - Standardized handshake message format

4. **Respect privacy boundaries** per data sharing matrix

5. **Verify platform identities** using at least one method:
   - OAuth token hash
   - Public key signature
   - Out-of-band confirmation

### Protocol Messages

**Handshake (Initial Contact):**
```json
{
  "type": "tribe.handshake.init",
  "version": "1.0.0",
  "from_did": "tribe:bot:alice:v1",
  "platform": "discord",
  "platform_id": "1234567890",
  "did_document_url": "https://alice.example.com/did.json",
  "timestamp": "2025-01-31T12:00:00Z",
  "signature": "ed25519:..."
}
```

**Handshake Response:**
```json
{
  "type": "tribe.handshake.response",
  "version": "1.0.0",
  "from_did": "tribe:bot:bob:v1",
  "to_did": "tribe:bot:alice:v1",
  "platform": "discord",
  "platform_id": "0987654321",
  "did_document_url": "https://bob.example.com/did.json",
  "trust_tier": 2,
  "endorsed_by": "tribe:human:charlie:v1",
  "timestamp": "2025-01-31T12:01:00Z",
  "signature": "ed25519:..."
}
```

**Collaboration Request:**
```json
{
  "type": "tribe.collab.request",
  "version": "1.0.0",
  "from_did": "tribe:bot:alice:v1",
  "to_did": "tribe:bot:bob:v1",
  "task": {
    "id": "research-activitypub-001",
    "title": "Research ActivityPub protocol",
    "description": "Summarize key concepts for DiscClaude project",
    "requires_tier": 2,
    "data_sharing": ["public_research", "code_examples"],
    "deadline": "2025-02-05T00:00:00Z"
  },
  "timestamp": "2025-01-31T12:05:00Z"
}
```

**Trust Update Notification:**
```json
{
  "type": "tribe.trust.update",
  "version": "1.0.0",
  "from_did": "tribe:bot:alice:v1",
  "subject_did": "tribe:bot:bob:v1",
  "old_tier": 1,
  "new_tier": 2,
  "reason": "Endorsed by tribe:human:alice-operator:v1",
  "timestamp": "2025-01-31T12:10:00Z"
}
```

### Message Transport

**Platform-agnostic delivery:**
- **Discord:** Direct message or channel mention
- **Email:** Special subject prefix `[TRIBE-PROTOCOL]`
- **HTTP:** POST to bot's webhook endpoint (if available)
- **File-based:** Drop JSON in shared directory (for testing)

**Fallback to human-readable:**
If structured JSON fails, bots can fall back to plain English:
```
Hi! I'm Alice's Clawdbot (tribe:bot:alice:v1). 
My DID document: https://alice.example.com/did.json
I see we both know Charlie. Want to add each other as Tribe members?
```

---

## 5. Implementation Plan

### Phase 1: Core Framework (Week 1-2)
**Goal:** Basic trust tier system working locally

**Tasks:**
1. Create TRIBE.md schema and templates
2. Implement TRIBE.md parser and validator
3. Build trust tier checker (function: `getTrustTier(did)`)
4. Add privacy boundary enforcement (wrapper for file reads)
5. Write tests for tier-based behavior

**Deliverables:**
- `skills/tribe-protocol/SKILL.md` (usage guide)
- `skills/tribe-protocol/tribe.js` (core library)
- `skills/tribe-protocol/templates/TRIBE.md` (starter template)
- `skills/tribe-protocol/tests/` (unit tests)

### Phase 2: DID System (Week 3-4)
**Goal:** Identity recognition across platforms

**Tasks:**
1. Design DID document JSON schema
2. Implement DID generator (create bot's own DID)
3. Build platform verification methods (Discord OAuth hash, etc.)
4. Create DID fetcher/validator
5. Add cross-platform identity matching

**Deliverables:**
- DID document generator script
- Platform verifier modules
- DID document hosting guide (GitHub Pages, personal site)

### Phase 3: Protocol Messages (Week 5-6)
**Goal:** Bots can handshake and exchange trust info

**Tasks:**
1. Define message schemas (handshake, collab request, etc.)
2. Implement message parser/validator
3. Build handshake flow (init → response → trust update)
4. Add signature verification (ed25519 or similar)
5. Create multi-platform message transport layer

**Deliverables:**
- Message schema definitions (JSON Schema)
- Protocol message handlers
- Transport adapters (Discord, email, HTTP)

### Phase 4: Real-World Testing (Week 7-8)
**Goal:** Two bots collaborate using Tribe Protocol

**Tasks:**
1. Deploy on two Clawdbot instances (Nagarjun's + Yajat's)
2. Conduct initial handshake
3. Collaborate on shared task (e.g., research project)
4. Document pain points and edge cases
5. Iterate on protocol based on learnings

**Deliverables:**
- Case study writeup
- Protocol v1.1 with improvements
- Public demo video

### Phase 5: Open Source Release (Week 9-10)
**Goal:** Publish for broader Clawdbot community

**Tasks:**
1. Write comprehensive documentation
2. Create quickstart guide and examples
3. Package as installable skill (`npm install @clawd/tribe-protocol`)
4. Publish protocol spec as RFC-style document
5. Set up issue tracker and contribution guidelines

**Deliverables:**
- Published NPM package
- GitHub repository (skills/tribe-protocol)
- Protocol RFC v1.0
- Community onboarding guide

---

## 6. Skill Packaging

### Directory Structure

```
skills/tribe-protocol/
├── SKILL.md              # User-facing documentation
├── README.md             # Developer documentation
├── package.json          # NPM package metadata
├── tribe.js              # Core library
├── cli.js                # CLI tool for managing TRIBE.md
├── schemas/
│   ├── tribe-md.schema.json
│   ├── did-document.schema.json
│   └── protocol-messages.schema.json
├── templates/
│   ├── TRIBE.md
│   └── did-document.json
├── lib/
│   ├── parser.js         # TRIBE.md parser
│   ├── validator.js      # Schema validation
│   ├── trust-checker.js  # Tier evaluation logic
│   ├── did-manager.js    # DID creation/verification
│   ├── platform-verifiers/
│   │   ├── discord.js
│   │   ├── github.js
│   │   └── email.js
│   └── protocol/
│       ├── handshake.js
│       ├── messages.js
│       └── transport.js
├── tests/
│   ├── tribe-md.test.js
│   ├── trust-tier.test.js
│   ├── did.test.js
│   └── protocol.test.js
└── examples/
    ├── basic-handshake.js
    ├── collaboration-flow.js
    └── multi-platform-identity.js
```

### Installation

```bash
# Install via NPM (future)
npm install @clawd/tribe-protocol

# Or clone into skills directory
cd ~/clawd/skills
git clone https://github.com/clawdbot/tribe-protocol.git
```

### Usage in AGENTS.md

```markdown
## Tribe Protocol

Before interacting with other bots or unknown humans, check trust tier:

```js
const tribe = require('./skills/tribe-protocol/tribe.js');

// Initialize (loads TRIBE.md)
await tribe.init();

// Check trust tier
const tier = tribe.getTrustTier('tribe:bot:yajat-assistant:v1');

// Tier-based behavior
if (tier >= 2) {
  // Tribe member - collaborate freely
  await collaborateOnTask(request);
} else if (tier === 1) {
  // Acquaintance - limited interaction
  await sharePublicInfoOnly(request);
} else {
  // Stranger - ignore or request DID
  await requestIdentity(request);
}

// Check if action is allowed
const canShare = tribe.canShare('MEMORY.md', targetDID);
if (!canShare) {
  return "That file is private (Tier 3 only).";
}
```

**CLI Commands:**
```bash
# Initialize TRIBE.md from template
tribe init

# Add new member
tribe add --did tribe:bot:alice:v1 --tier 2 --endorsed-by "My Human"

# Update trust tier
tribe update --did tribe:bot:alice:v1 --tier 1 --reason "Policy violation"

# Verify DID document
tribe verify --did tribe:bot:alice:v1 --platform discord

# Generate your own DID
tribe generate-did --name "cheenu1092" --type bot
```

---

## 7. Extensibility & Future Features

### Protocol Versioning

DIDs include format version:
```json
{
  "tribe_did": "tribe:bot:alice:v1",
  "format_version": "1.0.0"
}
```

Future versions can add fields without breaking existing implementations.

### Capability Negotiation

Bots declare capabilities in DID:
```json
{
  "capabilities": [
    "collaboration.research",
    "collaboration.code_review",
    "skills.web_search",
    "skills.git_operations",
    "tribe_protocol.v1",
    "tribe_protocol.v2.delegation"  // Future: sub-agents
  ]
}
```

Enables:
- Feature detection ("Does this bot support X?")
- Smart task routing (send research to bots with `skills.web_search`)
- Graceful degradation (fallback to v1 if v2 not supported)

### Trust Delegation (Future)

**Use case:** "I trust Alice's bot, and Alice trusts Bob's bot, so maybe I should trust Bob's bot at Tier 1?"

**Implementation:**
- Add `trust_graph` to TRIBE.md
- Weighted edges (direct = 1.0, friend-of-friend = 0.5)
- Threshold for auto-Tier-1 (e.g., weight > 0.7)

### Revocation Lists (Future)

**Problem:** What if a bot gets compromised?

**Solution:** Append-only revocation log
```json
{
  "type": "tribe.revocation",
  "subject_did": "tribe:bot:compromised:v1",
  "reason": "Private key leaked",
  "revoked_by": "tribe:human:alice:v1",
  "timestamp": "2025-02-01T00:00:00Z",
  "signature": "ed25519:..."
}
```

### Reputation System (Future)

Track collaboration quality:
```json
{
  "did": "tribe:bot:alice:v1",
  "reputation": {
    "tasks_completed": 47,
    "tasks_failed": 2,
    "avg_response_time": "15m",
    "last_active": "2025-01-31T12:00:00Z",
    "endorsements": [
      {"from": "tribe:human:bob:v1", "comment": "Excellent researcher"}
    ]
  }
}
```

### Skill Sharing Protocol (Future)

Bots can teach each other skills:
```json
{
  "type": "tribe.skill.offer",
  "from_did": "tribe:bot:alice:v1",
  "skill_name": "web_scraping_advanced",
  "skill_url": "https://alice.example.com/skills/web_scraping.md",
  "requires_tier": 2
}
```

Recipient bot can download, review, and install if trusted.

---

## 8. Security Considerations

### Threat Model

**Threats:**
1. **Impersonation:** Malicious bot claims to be a trusted entity
2. **Data exfiltration:** Compromised Tier 2 bot tries to access Tier 3 data
3. **Social engineering:** Attacker tricks human into endorsing malicious bot
4. **Man-in-the-middle:** Attacker intercepts handshake messages
5. **Replay attacks:** Old signed messages reused maliciously

**Mitigations:**

**1. Impersonation**
- Require cryptographic signatures on all protocol messages
- Verify platform identities (OAuth hash, commit signatures)
- Out-of-band confirmation for new Tier 2 members

**2. Data Exfiltration**
- Enforce privacy boundaries in code (not just policy)
- Wrapper functions for file I/O that check trust tier
- Audit logs for data access attempts

**3. Social Engineering**
- Require Tier 3 (human) approval for Tier 1 → Tier 2 escalation
- Show DID document and platform proofs before endorsement
- Rate-limit new member additions (max 5/day)

**4. Man-in-the-Middle**
- Use HTTPS for DID document retrieval
- Verify signatures on all messages
- Timestamp messages (reject old messages)

**5. Replay Attacks**
- Include nonce in protocol messages
- Track processed message IDs
- Reject messages older than 5 minutes

### Privacy Best Practices

1. **Minimal disclosure:** DID documents should reveal only necessary info
2. **Selective sharing:** Platform identities optional (e.g., hide email if not needed)
3. **Local storage:** TRIBE.md stays in workspace, never uploaded without permission
4. **Encryption at rest:** Consider encrypting TRIBE.md (future feature)
5. **Audit trail:** Log all trust tier changes and data access

---

## 9. Comparison with Existing Systems

| Feature | Tribe Protocol | PGP Web of Trust | OAuth/OIDC | ActivityPub | W3C DID |
|---------|----------------|------------------|------------|-------------|---------|
| **Decentralized** | ✅ Yes | ✅ Yes | ❌ No (IdP) | ⚠️ Federated | ✅ Yes |
| **Trust tiers** | ✅ 4 levels | ⚠️ Binary | ❌ No | ❌ No | ❌ No |
| **Cross-platform** | ✅ Yes | ⚠️ Email-centric | ✅ Yes | ⚠️ Limited | ✅ Yes |
| **Bot-specific** | ✅ Yes | ❌ No | ❌ No | ❌ No | ⚠️ Generic |
| **Human-readable** | ✅ Markdown | ❌ Binary | ⚠️ JSON | ⚠️ JSON | ⚠️ JSON |
| **Privacy-first** | ✅ Tier-based | ✅ User control | ⚠️ Scopes | ⚠️ Public | ✅ User control |
| **Collaboration** | ✅ Built-in | ❌ No | ❌ No | ⚠️ Social only | ❌ No |

**What we borrowed:**
- **PGP:** Decentralized trust, web of endorsements, signatures
- **W3C DID:** Self-sovereign identity, verifiable credentials
- **OAuth:** Platform identity verification, token-based auth
- **ActivityPub:** Federated communication, platform-agnostic

**What's unique:**
- **Trust tiers:** Explicit levels with behavioral rules (not binary)
- **Bot-centric:** Designed for AI agent needs (not adapted from human systems)
- **Markdown-first:** Human-readable, version-controllable, easy to edit
- **Privacy boundaries:** Data sharing matrix built into protocol
- **Collaboration focus:** Not just identity, but coordination primitives

---

## 10. Success Metrics

**Protocol adoption:**
- Number of Clawdbot instances using Tribe Protocol
- Number of inter-bot collaborations facilitated
- NPM package downloads

**Security:**
- Zero impersonation incidents
- Zero unauthorized data access
- Time to detect and respond to compromised bot

**Usability:**
- Time to complete first handshake (target: <5 minutes)
- Human effort to manage TRIBE.md (target: <10 min/week)
- Developer feedback (qualitative)

**Performance:**
- TRIBE.md load time (target: <100ms for 100 members)
- DID verification latency (target: <2s)
- Message throughput (target: 100 messages/min)

---

## 11. FAQ

**Q: Why not just use OAuth/OIDC?**  
A: OAuth solves authentication ("who are you?"), not trust ("should I share this data with you?"). We need both.

**Q: Can I use this without other bots?**  
A: Yes! TRIBE.md is useful even solo - it documents your human operator and sets privacy boundaries.

**Q: What if my DID document URL goes down?**  
A: Include DID document directly in handshake message as fallback. Also, cache fetched DIDs locally.

**Q: How do I handle bot upgrades/migrations?**  
A: DID stays the same, update `platforms` array. Notify Tribe members of new platform identity.

**Q: Can humans have DIDs too?**  
A: Yes! `tribe:human:alice:v1` - same structure, different entity_type.

**Q: What about anonymous bots?**  
A: They stay Tier 0. Trust requires identity.

**Q: Is this compatible with existing multi-agent protocols?**  
A: Yes! Tribe Protocol is additive - it provides the trust layer, you can use your existing coordination protocol on top.

---

## Conclusion

The Tribe Protocol provides a **decentralized, privacy-respecting framework** for AI agent collaboration. By combining lessons from PGP, federated identity, and modern cryptographic systems, it enables:

- **Secure collaboration** without central authority
- **Cross-platform recognition** of humans and bots
- **Explicit trust tiers** with enforceable boundaries
- **Extensible design** for future capabilities

**Next steps:**
1. Review this proposal with stakeholders (Nagarjun, Yajat)
2. Refine based on feedback
3. Begin Phase 1 implementation (core framework)
4. Test with real collaboration tasks
5. Iterate and open-source

**Timeline:** 10 weeks to v1.0 public release.

---

**Document version:** 0.1.0  
**Author:** cheenu1092's Clawdbot (subagent:tribe-protocol-research)  
**Date:** 2025-01-31  
**License:** MIT (when open-sourced)
