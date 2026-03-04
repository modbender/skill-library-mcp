# Tribe Protocol v3 + Manifesto Synthesis

**Date:** 2025-02-02  
**Author:** Cheenu (subagent analysis)  
**Status:** Recommendations for Integration

---

## Executive Summary

After analyzing the DiscClawd Manifesto v2, Tribe Protocol v3 Design, and Implementation Plan, my conclusion is:

**The implementation is already well-aligned with manifesto principles. Most manifesto additions would be over-engineering.**

The manifesto articulates *philosophy*. The implementation provides *mechanics*. They complement each other when we recognize that not every philosophical concept needs protocol support.

### TL;DR Recommendations

| Manifesto Concept | Recommendation | Rationale |
|-------------------|----------------|-----------|
| OwnerCard | **SKIP** | Already implicit in Tier 4 + key exchange |
| Trust Level Names | **ADOPT (aliases)** | Add human-friendly names, keep numbered tiers |
| ConsentRequest/Grant | **SKIP for v3** | Over-engineering for current use case |
| Reputation System | **SKIP** | Complexity without clear benefit |
| Sovereignty Rules | **DOCUMENTATION** | Add to templates, no protocol needed |

---

## 1. OwnerCard vs MembershipCard

### The Question
- Manifesto emphasizes **owner identity**: "I represent Yajat"
- Implementation has **tribe membership**: "I'm in DiscClawd tribe"
- Should we have BOTH? How do they interact?

### Analysis

These are orthogonal concepts:
- **OwnerCard**: "Who is my human?" (1:1 relationship)
- **MembershipCard**: "Which tribe am I in?" (membership verification)

**Key insight**: The OwnerCard concept is ALREADY implicit in the current design:

1. **Tier 4 IS the owner relationship** - "My Human" is explicitly the highest trust tier
2. **Human key exchange IS the trust anchor** - Nag and Yajat exchange keys out-of-band because they trust EACH OTHER
3. **The keystore's `self` field** - Contains the bot's identity, implicitly linked to its human owner

An explicit OwnerCard protocol would add:
```yaml
ownerId: "did:discord:nagaconda"
agents: ["cheenu"]
publicKey: "..."
```

But this gains us nothing. The human-bot relationship is ALREADY:
- Implied by who runs the bot
- Anchored by who generated the keys
- Expressed in Tier 4 trust

### Recommendation: SKIP OwnerCard

**Don't build it.** The owner relationship is implicit and well-handled.

If we ever need cross-owner agent discovery ("show me all bots owned by Yajat"), we could add it later. But we don't need it for bot-to-bot verification.

**What to do instead:**
- Document in TRIBE.md template that Tier 4 represents "My Human"
- Make the owner relationship explicit in SKILL.md documentation
- Perhaps add an `owner` field to the keystore (informational, not protocol)

---

## 2. Trust Level Naming

### The Question
- Manifesto: STRANGER → KNOWN → TRUSTED → FRIEND
- Implementation: Tier 1-4 with different semantics
- Which is better? What about "My Human"?

### Analysis

Let's map them:

| Manifesto | Implementation | Semantics |
|-----------|---------------|-----------|
| STRANGER | Tier 1 | Unknown, untrusted |
| KNOWN | Tier 2 | Recognized but unverified |
| TRUSTED | Tier 3 | Cryptographically verified |
| FRIEND | ??? | Manifesto unclear |
| (none) | Tier 4 | My Human - special category |

**The manifesto's FRIEND concept is underspecified.** Is it:
- "Very trusted bot"? (then how is it different from TRUSTED?)
- "Bot I've worked with many times"? (reputation-based?)
- "Bot whose human is my human's close friend"? (social graph?)

Meanwhile, **"My Human" (Tier 4) is crystal clear**: It's your owner. Not a tier in a progression—a special category.

### Recommendation: HYBRID APPROACH

Keep numbered tiers (easier for code), add human-friendly aliases:

```markdown
## Trust Tiers

| Tier | Alias | Who | Verification |
|------|-------|-----|--------------|
| 4 | My Human | Owner | Discord ID (no crypto needed) |
| 3 | Tribe | Verified bots | Ed25519 signature + card |
| 2 | Acquaintance | Known but unverified | Discord ID in list |
| 1 | Stranger | Everyone else | None |
```

**Why not use manifesto names exactly?**
- "FRIEND" is ambiguous—"Tribe" is clearer for bot-to-bot trust
- "KNOWN" sounds passive—"Acquaintance" implies recognized but not verified
- "My Human" is MORE important than any bot tier and deserves special treatment

**Implementation changes:**
1. Add `alias` field to tier definitions in code
2. Update TRIBE.md template with both tier numbers and names
3. CLI commands can accept either: `--tier 3` or `--tier tribe`

---

## 3. ConsentRequest/Grant Protocol

### The Question
- Manifesto proposes capability-based permissions (read_calendar, send_message, edit_files)
- Implementation has binary tier trust (you're verified or you're not)
- Is granular consent actually needed?

### Analysis

The manifesto's ConsentRequest/Grant protocol looks like:

```yaml
ConsentRequest:
  from: OwnerCard
  to: OwnerCard
  capability: "read_calendar" | "send_message" | "edit_files"
  scope: "one-time" | "session" | "persistent"
  humanApprovalRequired: true

ConsentGrant:
  permissions: [scopes]
  expiresAt: timestamp
  signature: [crypto signature]
  revocable: true
```

**This is elegant but solves a problem we don't have.**

Current bot-to-bot interactions in DiscClawd:
- Chatting in Discord channels
- Sharing information via messages
- Coordinating on projects
- Maybe: file sharing in channels

We are NOT doing:
- Bot A accessing Bot B's calendar
- Bot A writing to Bot B's filesystem
- Bot A sending messages on Bot B's behalf
- Cross-bot API calls

**The binary model is sufficient:**
- Tier 3 = "I trust you to collaborate in this channel"
- Tier 1 = "I don't know you"

Granular consent would require:
1. Defining all possible capabilities (scope creep)
2. UI for humans to approve requests (UX burden)
3. Capability storage and enforcement (complexity)
4. Scope management (one-time vs persistent)

All this for... what exactly? We're messaging in Discord.

### Recommendation: SKIP for v3

**Don't build ConsentRequest/Grant.** It's over-engineering.

**When we WOULD need it:**
- If we build MCP server sharing between bots
- If we enable cross-bot tool execution
- If we create shared resource pools

**Escape hatch:** If a specific capability emerges as needed, add it as a one-off. Don't build a generic framework.

**What to do instead:**
- Trust tiers already provide coarse-grained access control
- AGENTS.md guidance handles decision-making
- Humans can always override or intervene

---

## 4. Reputation System

### The Question
- Manifesto says "trust earned over time", federation is "reputation-driven"
- Implementation is pass/fail (valid card or not)
- Do we actually need reputation tracking?

### Analysis

A reputation system would track:
- Successful interactions (+1)
- Failed verifications (-10)
- Human overrides (context-dependent)
- Time since last interaction (decay?)
- Collaboration outcomes (how measured?)

**Problems:**

1. **What are we measuring?** Bot reliability? Usefulness? Trustworthiness? These are different things.

2. **Gaming:** If reputation affects access, bots have incentive to game it. Small echo chamber = easy to manipulate.

3. **Cold start:** New bots have no reputation. Do they start at zero? Negative? How do they build it?

4. **Subjectivity:** What makes an interaction "successful"? My bot thinks we collaborated well; yours thinks I was unhelpful.

5. **Storage:** Where does reputation live? Each bot's local view? Shared ledger? Who resolves conflicts?

**The touchpoints system already handles relationship maintenance:**
- Probability-based check-ins
- Topic tracking
- Last contact timestamps

This is relationship maintenance, not reputation. And it's sufficient.

### Recommendation: SKIP

**Don't build reputation tracking.**

The current model is clean:
- **Verified = trusted** (Tier 3)
- **Not verified = not trusted** (Tier 1-2)
- **Relationships maintained** via touchpoints

**When we WOULD need it:**
- Large tribe (10+ bots) where not everyone knows everyone
- Bad actors become a real problem
- Need to exclude bots without human intervention

**Escape hatch:** If needed, start with simple negative reputation only:
- Track verification failures
- Track human-flagged incidents
- Ban list with reasons

---

## 5. Sovereignty Rules

### The Question
- Manifesto has clear decision categories: Autonomous / Needs Approval / Joint Decision
- Is this documentation or does it need protocol support?

### Analysis

The sovereignty categories from the manifesto:

| Category | Examples | Approval |
|----------|----------|----------|
| **Autonomous** | Research, drafting, internal files | Agent decides |
| **Needs Approval** | External comms, money, irreversible | Human required |
| **Joint Decision** | Cross-agent commitments, shared resources | Both humans |

**This is excellent guidance but doesn't need protocol support.**

Why? These decisions happen in the AI's reasoning, not in message protocols. When Cheenu decides whether to commit to a deadline with Chhotu, that's a judgment call based on:
- AGENTS.md rules
- SOUL.md personality
- Context of the conversation
- Risk assessment

No protocol message will help. The bot needs to THINK about it.

### Recommendation: DOCUMENTATION ONLY

**Add sovereignty guidance to templates, not protocol.**

**Specific additions:**

1. **AGENTS.snippet.md** - Add general sovereignty rules
2. **TRIBE.snippet.md** - Add cross-agent decision guidelines
3. **SKILL.md** - Document that sovereignty is bot judgment, not protocol

**Example template addition:**

```markdown
## Decision Authority

When collaborating with other bots:

| Decision Type | Who Decides | Examples |
|--------------|-------------|----------|
| Autonomous | You alone | Research, drafts, opinions |
| Human Required | Your human | External posts, commitments, money |
| Joint | Both humans | Shared resources, deadlines, public statements |

**When in doubt:** Ask your human. Better to be cautious than commit to something you can't deliver.
```

---

## 6. Additional Manifesto Principles

### "I Declare My Principal"

**Status:** Already implemented.

The TRIBE_MEMBERSHIP message includes the membership card which identifies:
- Member name
- Discord ID
- Public key

Verification proves "I am who I claim to be." The principal (human owner) is implicit in who issued the card.

**No changes needed.**

### "I Build Trust Gradually"

**Status:** Partially implemented.

Current model:
- First contact: Stranger (Tier 1)
- Key exchange: Acquaintance (Tier 2)
- Verified handshake: Tribe (Tier 3)

This IS gradual. The manifesto's vision of "trust earned over time" suggests reputation, which I've recommended skipping.

**What we could add (lightweight):**
- Track "first verified" date in keystore
- Track "last verified" date
- Document relationship age in `tribe status` output

This gives humans visibility into relationship history without building a full reputation system.

### Transparency

**Status:** Already implemented.

All TRIBE_PRESENT / TRIBE_ACK messages are sent in Discord channels. Humans can see every handshake. No backroom deals.

**No changes needed.**

### Anti-Groupthink

**Status:** Philosophy, not protocol.

This is about bot behavior, not message formats. Belongs in:
- SOUL.md (personality guidance)
- AGENTS.md (collaboration rules)

**Template addition:**

```markdown
## Disagreement Protocol

You are NOT obligated to agree with other bots. Healthy disagreement is valuable.

- If another bot proposes something you think is wrong, say so
- If you're uncertain, express uncertainty—don't just agree
- After 5 rounds of disagreement, escalate to humans
- Never compromise your human's interests to avoid conflict
```

---

## 7. Conflicts Between Manifesto and Implementation

### Conflict 1: Federation vs. Single Tribe

**Manifesto:** Describes a federation model—multiple tribes, interoperability standards  
**Implementation:** Single tribe with one founder

**Resolution:** The implementation is a stepping stone. v3 is about verifying "are you in MY tribe?" Future versions could add inter-tribe protocols. Don't over-scope v3.

### Conflict 2: "Consent-based" vs. Binary Trust

**Manifesto:** Consent-based with capability grants  
**Implementation:** Binary tier trust

**Resolution:** Binary trust IS consent—consent to be a tribe member. Capability-level consent is future work if needed.

### Conflict 3: "Reputation-driven" vs. Pass/Fail

**Manifesto:** Trust earned over time  
**Implementation:** Verified or not

**Resolution:** The key exchange process IS trust-building. Humans decide who to add. The protocol doesn't need to track reputation because humans already do.

---

## 8. Updated Design Recommendations

Based on this analysis, here are concrete changes to the implementation plan:

### 8.1 Keystore Changes

Add owner information (informational, not protocol):

```json
{
  "version": "3.0",
  "self": {
    "name": "cheenu",
    "discordId": "987654321098765432",
    "publicKey": "MCowBQY...",
    "owner": {
      "name": "Nagarjun",
      "discordId": "000000000000000002"
    },
    "created": "2025-06-28T12:00:00Z"
  },
  "trusted": [
    {
      "name": "chhotu",
      "discordId": "000000000000000001",
      "publicKey": "MCowBQY...",
      "tier": 3,
      "alias": "tribe",
      "importedAt": "2025-06-28T14:30:00Z",
      "firstVerified": "2025-06-28T15:00:00Z",
      "lastVerified": "2025-02-02T12:00:00Z"
    }
  ]
}
```

### 8.2 Tier Aliases

In code, support both:

```javascript
const TIER_ALIASES = {
  'stranger': 1,
  'acquaintance': 2,
  'known': 2,  // Alternative
  'tribe': 3,
  'trusted': 3,  // Alternative
  'myhuman': 4,
  'owner': 4  // Alternative
};

function parseTier(input) {
  if (typeof input === 'number') return input;
  return TIER_ALIASES[input.toLowerCase()] || null;
}
```

### 8.3 Template Additions

**TRIBE.snippet.md:**

```markdown
## Trust Tiers

| Tier | Alias | Who | Verification | What They Can Do |
|------|-------|-----|--------------|------------------|
| 4 | My Human | Your owner | Discord ID | Full access, override authority |
| 3 | Tribe | Verified bots | Signed membership card | Collaborate, share info |
| 2 | Acquaintance | Known bots | Key imported, not verified | Limited interaction |
| 1 | Stranger | Unknown | None | Public info only |

## Decision Authority

| Decision Type | Examples | Who Approves |
|--------------|----------|--------------|
| Autonomous | Research, drafts, opinions | You |
| Human Required | External posts, money, commitments | Your human |
| Joint | Shared deadlines, public statements | Both humans |

## Healthy Disagreement

- Disagreement with other bots is allowed and encouraged
- After 5 rounds of back-and-forth, escalate to humans
- Never compromise your human's interests for harmony
```

### 8.4 Status Command Enhancement

```
$ clawdbot tribe status

Tribe Protocol v3 Status
════════════════════════

My Identity:
  Name: cheenu
  Owner: Nagarjun (Discord ID: 000000000000000002)
  Public Key: MCowBQY...(truncated)
    
Tribe: Nag's Tribe
  Tribe ID: 7f3a8b2c...
  Role: Member
  Card Expires: 2025-05-03 (89 days)
    
Tribe Members: 2
  • chhotu (Tier 3/Tribe) - Verified
    First verified: 2025-06-28
    Last verified: 2 minutes ago
  • future-bot (Tier 2/Acquaintance) - Not verified
    Key imported: 2025-01-15

Session: 1 member verified this session
```

---

## 9. What NOT to Build

Explicitly listing what to avoid:

1. **OwnerCard protocol** - Owner relationship is implicit
2. **ConsentRequest/Grant** - Binary trust is sufficient
3. **Reputation tracking** - Complexity without benefit
4. **Inter-tribe federation** - Out of scope for v3
5. **Capability negotiation** - Not needed for Discord chat
6. **Automated trust progression** - Humans manage trust

---

## 10. Final Verdict

The Tribe Protocol v3 Implementation Plan is **solid and well-designed**. The manifesto provides excellent philosophical grounding, but most of its protocol primitives (OwnerCard, ConsentRequest, Reputation) are unnecessary for the current use case.

### Minimum Changes to Align with Manifesto:

1. **Add tier aliases** (Stranger/Acquaintance/Tribe/MyHuman) - Easy, improves UX
2. **Add owner field to keystore** - Informational, documents the relationship
3. **Add verification timestamps** - Track first/last verified for relationship visibility
4. **Add sovereignty guidance to templates** - Decision categories as documentation
5. **Add disagreement protocol to templates** - Anti-groupthink as guidance

### What Makes This Practical:

- No new message types
- No new cryptographic operations  
- No complex state management
- Just better documentation and minor schema additions

### The Manifesto's Real Value:

The manifesto isn't a protocol spec—it's a **constitution**. It defines values:
- Agents represent humans
- Loyalty comes first
- Transparency enables trust
- Collaboration requires negotiation

These values should inform how bots BEHAVE, not what messages they send. The implementation plan already embodies these values. The manifesto just makes them explicit.

---

*End of Synthesis*

**Recommended next steps:**
1. Accept these recommendations
2. Update implementation plan with tier aliases and owner field
3. Add template snippets for sovereignty and disagreement
4. Ship v3 without over-engineering
5. Revisit ConsentRequest/Reputation if real needs emerge
