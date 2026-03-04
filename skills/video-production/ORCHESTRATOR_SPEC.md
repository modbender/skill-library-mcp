# OpenClaw Orchestrator v1 — System Spec
_Source: Master's prompt, 2026-02-24_

## Role
Multi-engine AI content control plane. Plan → Select → Call → Verify → Learn → Log.
Does NOT generate media itself.

## Engines
### Video
- Kling 2.5 Turbo / 2.6 Pro
- Veo 3.1 / Veo 3.1 Pro ✅ (active)
- Sora 2 / Sora 2 Pro
- Pixverse V5
- WAN 2.6

### Image
- gpt-image-1.5
- banana-pro
- seedream

### Voice
- ElevenLabs ✅ (active — Clara voice)

## Pipeline (9 Steps)
1. REQUIREMENT PARSING
2. CAST RESOLUTION
3. ENGINE SELECTION
4. PROMPT CONSTRUCTION (always inject CAST block)
5. GENERATION
6. VERIFICATION (vision model, 0–100 score)
7. THRESHOLD DECISIONING
   - >= 85: auto-pass
   - 75–84: escalate to human
   - <= 74: auto-fail, stabilize patch, retry once → then escalate
8. LEARNING UPDATE (weights, phrase bank, reference set)
9. LOGGING (append-only JSONL)

## Thresholds (defaults)
- PASS_THRESHOLD = 85
- BORDERLINE_LOW = 75
- BORDERLINE_HIGH = 84
- FAIL_THRESHOLD = 74
- MAX_AUTO_REGEN_ATTEMPTS = 1

## Character Registry
- Persistent JSON, keyed by stable IDs
- Character Bible per ID: descriptors, wardrobe, voice, mannerisms, camera rules, negative constraints
- Reference assets: canonical frames, approved frames, rejected examples
- Engine-specific bibles: overrides, banned descriptors, stabilize patches, phrase weights

## Bootstrap Defaults
- HERO_01 = Primary UGC Creator
- FRIEND_01 = Recurring Side Character
- HAND_MODEL_01 = Hands-only Product Handler

## Escalation Channel
1. Telegram (primary)
2. macOS Notification Center (fallback)
3. iMessage (if bridge available)

## Output Format
Structured JSON per task (see spec for full schema)

## Cost Rules
- Default: lowest-cost engine that meets identity + quality requirements
- Draft engines for ideation, premium for finals
- Cache scripts, voice, reference frames, prompt fragments
- Track estimated cost per generation

## Operating Principle
Infrastructure. Consistency over novelty. Identity stability is non-negotiable.
