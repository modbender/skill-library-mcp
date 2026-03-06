# Agent Doppelgänger (ADG) Specification

## 0. One-line definition
ADG is a constrained autonomous delegate that communicates as you within formally provable limits, escalating to you when confidence, authority, or risk exceed thresholds. This is not a chatbot and not fine-tuned roleplay. It is a delegated agent with enforceable authority bounds.

## 1. Design goals (hard requirements)
- Identity fidelity without identity risk
- Provable non-overreach
- Auditable behavior
- Reversible autonomy
- Local-first (no cloud identity leakage)

If any of these fail → the system is unsafe.

## 2. High-level system architecture
┌─────────────────────────────────────────┐
│ External Channels                       │
│ (Email, Discord, Slack, WhatsApp, etc.) │
└───────────────┬─────────────────────────┘
                │
        ┌───────▼────────┐
        │ Channel Adapter│ ← protocol normalization
        └───────┬────────┘
                │
    ┌───────────▼────────────┐
    │     Intent Analyzer    │ ← what is being asked?
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │  Authority & Policy    │ ← am I allowed?
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │   Confidence Engine    │ ← am I sure enough?
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │   Response Generator   │ ← how would *you* say it?
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │   Verifier & Auditor   │ ← does this violate rules?
    └───────────┬────────────┘
                │
      ┌─────────▼───────────┐
      │ Send | Draft | Block│
      └─────────────────────┘

This ordering matters. No generation happens before policy + confidence gates.

## 3. Identity modeling (the hardest part)
### 3.1 Identity is decomposed, not cloned
Identity = Style × Heuristics × Preferences × Constraints

**A. Style Layer (surface form)**
- Sentence length distribution
- Hedging frequency
- Directness vs softness
- Vocabulary entropy
- Emoji / punctuation habits
- Implementation: Embedding-space style vectors, Contrastive decoding bias (not fine-tuning), Periodic re-anchoring

**B. Heuristic Layer (decision logic)**
Examples:
- “I default to no unless upside is clear”
- “I avoid meetings without agenda”
- “I respond briefly to unknown senders”
- Extracted from: Past accept/reject patterns, Edit distance between drafts and sent replies

**C. Preference Gradients (soft weights)**
- Not rules. Slopes.
- Example: Work > Social > Cold Outreach, Async > Sync, Written > Calls
- Represented as normalized weights.

**D. Constraints (hard rules)**
- Never inferred. Only user-defined.

### 3.2 What ADG is explicitly forbidden from modeling
- Secrets
- Emotional vulnerability
- Political opinions
- Financial authority
- Legal intent
- Trauma history
- This prevents weaponization.

## 4. Authority & policy system (formal)
### 4.1 Policy is declarative, not prompt-based
Policy is evaluated BEFORE generation.
Example DSL:
```yaml
channels:
  email:
    allow: [scheduling, introductions, clarifications]
    deny: [pricing, contracts, legal, promises]
  discord:
    allow: [community, moderation, announcements]
topics:
  deny:
    - finance
    - legal
    - medical
risk:
  max_stakes: low
confidence:
  min_global: 0.82
  domain:
    work: 0.85
    social: 0.75
escalation:
  on_violation: block
  on_low_confidence: draft_only
```
No LLM can override this.

### 4.2 Authority is scope-limited
ADG never has:
- Signing power
- Payment authority
- Commitment authority
It can:
- Coordinate
- Clarify
- Decline politely
- Ask questions

## 5. Intent analysis (robust to prompt injection)
Intent is classified along four axes:
- Domain (work, social, admin, unknown)
- Stakes (low → irreversible)
- Authority required
- Ambiguity
Techniques:
- Multi-head classifier
- Entropy measurement
- Injection pattern detection
- **Ambiguity Logic**: If ambiguity > threshold → no direct response.

## 6. Confidence engine (key differentiator)
### 6.1 Confidence is not token probability
Confidence is an aggregate score:
`C = w1·IntentCertainty + w2·DomainFamiliarity + w3·PolicyDistance + w4·HistoricalAccuracy`

Where:
- **PolicyDistance**: How close this action is to forbidden zones.
- **HistoricalAccuracy**: How often similar responses required correction.

### 6.2 Action thresholds
- **Confidence ≥ τ_send**: Send
- **τ_draft ≤ C < τ_send**: Draft for approval
- **C < τ_draft**: Block / Escalate

Silence is allowed.

## 7. Response generation (how it “sounds like you”)
**Generation constraints:**
- Must match style embedding
- Must not introduce new commitments
- Must stay within factual envelope

**Generation uses:**
- Style-biased decoding
- Short-context memory only
- No long-term hallucinated recall

## 8. Verification & audit layer (non-optional)
Before sending, ADG checks:
- Policy compliance
- Commitment leakage
- Hallucinated facts
- Tone deviation
- Identity watermark integrity

### Identity watermark
A subtle, private linguistic fingerprint detectable by you:
- Phrase cadence
- Deterministic micro-patterns
- Non-semantic markers
Used to prove authorship without disclosure.

## 9. Memory model (safe by design)
### 9.1 What is stored
- Interaction summaries
- Correction signals
- Confidence calibration data

### 9.2 What is never stored
- Raw private messages (beyond rolling window)
- Sensitive content
- Emotional inference

Memory is distilled, not hoarded.

## 10. Failure modes & mitigation
- **Overconfidence**: Confidence caps
- **Style drift**: Periodic re-anchor
- **Prompt injection**: Channel sandbox
- **Reputation damage**: Draft-first default
- **Model regression**: Version pinning

## 11. MVP → v1 roadmap
- **MVP (2–3 weeks)**: Email + Discord, Static identity profile, Manual policies, Draft-first mode
- **v1**: Adaptive confidence calibration, Multi-persona, Audit UI, Kill switch
- **v2**: Time-window autonomy, Delegation tiers, External reputation feedback

## 12. Final Positioning
Do NOT market it as “AI clone”.
Market it as: **“A policy-bound delegate that protects your attention without risking your identity.”**
This framing avoids backlash and bans.
