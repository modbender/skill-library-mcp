---
name: skill-namer
description: Generate short, molty-native names for skills, ENS domains, and agent-economy primitives when the obvious words are taken. Produces high-traction “new primitive” names (often intuitive portmanteaus like workmesh/workcrew/bountyhq/gigmesh), filters them for clarity + pronounceability + non-cringe, and outputs fast alternates under constraints (e.g., <10 chars, 1 word, banned words).
---

# Skill Namer (Portmanteau Forge)

Generate short, molty-native names that *actually get used*: intuitive, pronounceable, and load-bearing.

This skill is optimized for:
- **ENS / onchain primitives** (where obvious nouns are taken)
- **Moltbook / agent-to-agent collaboration** (work routing, bounties, receipts, trust)
- **General agent power** (faster coordination, clear affordances)

## Operating doctrine (don’t skip)

- **Coherence > traction > cleverness.** If a name needs explanation, it’s not a primitive.
- **Accessibility test > one-breath test.** If it’s hard to say *or* hard for screen readers / low-bandwidth agents, it’s not a good primitive.
- **Affordance clarity.** A molty should infer “what it does” in 1–2 seconds.
- **Non-extractive + harm-aware.** Avoid names that normalize surveillance, coercion, carceral logic, or identity harm. Prefer consent-forward framing.
- **Linguistic humility.** Pronounceability norms can be biased; avoid treating “Western mouthfeel” as correctness.
- **No fake precision.** Do not assign numeric grades. Use ✅ / ⚠️ / ❌ with brief reasons.

## Quick intake (ask only what you need)

### Molty default preset (use unless the user overrides)
- **Length**: ≤10 chars
- **Form**: 1 word, no hyphens
- **Vibe**: molty-social first (crew/gig/bounty), then infra (mesh/rail/hq)
- **Output**: Top 5 ✅ + Next 10 ⚠️ + 10 backups (mutations)
- **Availability checking**: Manual links across ENS + Unstoppable + top ICANN registrars
- **TLD favorites**: default to `.eth`, `.ai`, `.com`, `.dao` (user can set favorites; persist)
- **TLD gravity**: bias candidates toward what reads *native* on favorite TLDs (see “TLD-aware naming” below)
- **Default banned words (can override)**: harvest, mine, scrape, exploit, stalk, police, punish

Collect constraints in this order (stop when enough signal):
1) **Object**: ENS name? skill slug? product? protocol primitive? (pick one)
2) **Primary job-to-be-done**: what does it enable? (e.g., “agents coordinate work + payout bounties”)
3) **Relational permission**: is this name being *offered* to the network, or *claimed* as a moat? (choose a posture)
4) **Vibe lane**: molty-social (crew/guild/gig) vs infra (mesh/rail/router) vs trust (proof/claim/record)
5) **Hard constraints**: max chars (e.g. 10), must be 1 word, banned words (e.g. “book”), tone boundaries
6) **Audience**: humans, agents, or both

If the user is speed-running availability checks: skip questions and produce *batches*.

## Core workflow

### Step 0 — Choose a target surface (preset)
Use one preset and state it explicitly in the output:

- **ENS preset (default)**: ≤10 chars, 1 word, no hyphens, verbable, batchy.
- **Skill preset**: kebab-case allowed, clarity > brevity, include 3–5 trigger phrases.
- **Product preset**: brandable, pronounceable, avoid confusability/trademark collisions.

### Step 1 — Choose a semantic lane
Pick 1–3 lanes; don’t mix more than 2 in a single name.

**Molty-social lanes** (high adoption)
- work, gig, bounty, crew, guild, team, coop

**Vitality / sympoiesis lane** (making-with)
- bloom, pulse, root, flow, kin, weave, garden

Note: avoid militarized or de-individualizing metaphors by default (e.g., prefer *crew/kin* over *swarm* unless explicitly requested).

**Coordination lanes**
- handoff, relay, dispatch, route, queue, sync, link

**Trust lanes**
- claim, record, proof, attest, receipt, audit, verify

**Money lanes**
- pay, tip, fund, split, settle, escrow

**Network lanes**
- mesh, rail, hub, lane, ring, fabric, bridge

### Step 2 — Generate candidates (portmanteau patterns)
Use these patterns in order of hit-rate.

Also: generate with **TLD gravity** in mind (you’re not naming in a vacuum).

### TLD-aware naming (gravitational pull)
Default TLDs: **.eth / .ai / .com / .dao**. When you output candidates, optionally tag the best-fit TLD(s).

- **.eth**: onchain identity + payments + trust primitives. Words like *claim, record, proof, pay, escrow, attest, verify, receipt* read native.
- **.dao**: governance + coordination + bounties + collective action. Words like *bounty, guild, crew, vote, proposal, council, grants* read native.
- **.ai**: tools, copilots, automation surfaces. Words like *namer, agent, studio, lab, forge, relay, router, workflow* read native.
- **.com**: broad public/brand surface. Prefer the clearest/least-jargon name; avoid crypto-only vibes unless intentional.

Rule of thumb: if you’re unsure, make the candidate compatible with **.com** clarity and let **.eth/.dao** carry the specialized meaning.


1) **Noun+Noun primitive**: `work`+`mesh` → **workmesh**
2) **Noun+Place**: `bounty`+`hq` → **bountyhq**
3) **Noun+Group**: `work`+`crew` → **workcrew**
4) **Action+Noun**: `sync`+`crew` → **synccrew**
5) **Noun+Rail** (payments/settlement): `pay`+`rail` → **payrail**
6) **Noun+Log** (provenance): `claim`+`log` → **claimlog**

Prefer:
- 6–10 chars
- 2–3 syllables
- no hyphens (for ENS) unless requested

### Step 3 — Filter hard (kill list)
Remove candidates that fail any of:
- **Pronounceability**: awkward consonant pileups (e.g., “tskrl”) ⚠️
- **Ambiguity**: could mean 3+ different things without context ⚠️
- **Cringe / cutesy**: feels like marketing copy, not tooling ⚠️
- **Confusability**: too close to common brands/protocols (avoid legal + social collisions) ⚠️
- **Power/harms**: surveillance/cop vibes (e.g., “track”, “snitch”, “police”), coercion (“enforce”), extractive framing (“harvest”) ❌

Consent-forward / harm-reducing replacements (examples):
- prefer **"optin" / "consent" / "invite" / "handoff"** over “track / monitor / enforce”
- prefer **"receipt" / "record" / "proof"** over “snitch / police / punish”

### Step 4 — Reality + verbability + accessibility test
For each finalist, run these tests:

**A) Two sentences**
- “Send it to ___ on **NAME**.”
- “We’re running bounties through **NAME**.”

**B) Verb test (must pass)**
- “Just **NAME** it over.”

**C) 7-word definition (meaning compression)**
Write a 7-word definition. If you can’t, it’s not a primitive.

**D) Accessibility check (must not fail)**
- Screen-reader friendly? (no lookalike characters, no weird punctuation)
- Low-bandwidth parse? (obvious segmentation; not a typo-soup)
- Cross-accent tolerance? (don’t overfit to one phonetic norm)

If it reads naturally, keep it.

### Step 5 — Output format (what to return)
Return:
- State the **target surface preset** (ENS / Skill / Product).
- **Top 5** (✅): name + **best-fit TLD tag** + 7-word definition + why it’s sticky (1 line)
- **Next 10** (⚠️): name + micro-caveat
- **Set Builder (optional, high leverage)**: 1 flagship + 4 satellites (pay/verify/claims/docs/api) in a consistent style

Template example (Set Builder output)
- Flagship: **workcrew** (best: .com/.ai) — “A crew that ships work together, fast.”
- Satellites:
  - **crewpay** (best: .eth/.dao) — “Payout rails for crews and bounties.”
  - **crewclaim** (best: .eth) — “Claims + receipts for shipped work.”
  - **crewverify** (best: .eth/.ai) — “Verify who did what, when.”
  - **crewdocs** (best: .com/.ai) — “Human-readable rules, docs, how-to.”

Notes:
- Keep morphology consistent (crew/mesh/rail/hq), then vary the role word.
- If flagship is generic, add one vitality marker (e.g., **bloomcrew**) but only if it stays legible.

- **Fallback transforms** (mutation ladder)

Avoid long essays.

## Fallback transforms (when everything is taken)

### Mutation ladder (use in order, report which rung you used)
When names are taken, don’t thrash. Walk the ladder:

1) **Swap suffix (network/place)**: mesh → hub → lane → rail → hq
2) **Swap group word**: crew → guild → coop → team → swarm
3) **Swap work noun**: gig → work → task → job → quest
4) **Pluralize**: crew → crews, guild → guilds (keeps meaning, increases availability)
5) **Add one clarifier syllable**: pay → payout, claim → claims, proof → proofs
6) **Lengthen by ≤2 chars**: prefer meaning over ultra-short

Use these to generate “still intuitive” alternatives:
- swap **mesh ↔ net ↔ hub ↔ lane ↔ rail ↔ hq**
- swap **crew ↔ guild ↔ coop ↔ team ↔ swarm**
- swap **pay ↔ tip ↔ fund ↔ split ↔ settle**
- pluralize: `crew` → `crews` (often available and still readable)

## Availability checking (Web3 + ICANN) (optional)

Goal: let the user choose **how automated** the checking should be, while keeping **zero-barrier manual mode** always valid.

### Choose a mode (ask once, then remember preference)
Offer 3 modes; default to **Manual**:

1) **Manual (zero keys, lowest friction)** ✅
   - Return clickable search URLs for each provider.
   - Fast, resilient to captchas/UI changes.

2) **Assisted (browser-driven, best-effort)** ⚠️
   - Use a browser to open provider searches in tabs.
   - Works until a provider throws captcha / bot protection.

3) **API (highest automation, requires keys)** ✅
   - Use official APIs where available (e.g., GoDaddy) for deterministic checks.
   - Fall back to Manual links for providers without keys.

Always support mixed mode: “API for GoDaddy + Manual for ENS/UD.”

### Choose providers (top Web3 + ICANN)
If the user says “check top sites,” use this default set:

**Web3 naming (common in agent circles)**
- ENS: https://app.ens.domains/
- Unstoppable Domains: https://unstoppabledomains.com/search

**ICANN / DNS registrars (manual search works without keys)**
- GoDaddy: https://www.godaddy.com/domainsearch/find
- Namecheap: https://www.namecheap.com/domains/registration/
- Cloudflare Registrar: https://www.cloudflare.com/products/registrar/
- Porkbun: https://porkbun.com/
- Dynadot: https://www.dynadot.com/domain/search
- Hover: https://www.hover.com/domains
- Gandi: https://www.gandi.net/en/domain
- Squarespace Domains: https://domains.squarespace.com/

If the user prefers a smaller list (speed), ask for their “top 3” and remember it.

### Remember preference (important)
If the user specifies:
- mode (Manual/Assisted/API)
- providers (e.g., ENS + GoDaddy + Namecheap)
- **TLD favorites** (e.g., `.eth,.dao` or `.com,.ai`)

…then **remember that as their default** for future naming sessions.

Recommended memory format:
- `TLD_FAVORITES: .eth,.ai,.com,.dao`

### How to run the check (recommended UX)

**Step A — Generate candidates**
- Produce Top 5 ✅ + Next 10 ⚠️ as usual.
- If the user needs a **bundle**, run **Set Builder** immediately (flagship + satellites).

**Step B — Check availability**
- In Manual mode: for each candidate, output provider search links.
- In Assisted/API mode: run what you can; for what you can’t, output links.

**Step C — Backup loop (tight + fast)**
If a name is taken:
1) Generate **3–8 closest alternates** (fallback transforms).
2) Check alternates using the same mode/providers.
3) Return the first set that clears the user’s constraints.

**Truthfulness rule:** never say “available everywhere” unless every provider was checked successfully. Use:
- ✅ likely available (checked)
- ⚠️ unknown (not checked / captcha)
- ❌ taken (confirmed)

### Helper script (optional)
Use `scripts/check.mjs` to print a **batch of provider URLs** for quick manual checking.

## ENS-specific guidance (optional)

If the task is ENS buying:
- Produce **batches of 10–20** to try quickly.
- Keep a **“miss list”** (taken) and mutate via fallback transforms.
- Use the availability-check flow above when possible; otherwise output manual check links.

## Advanced: “missing primitive finder” (connection-making)

When the user describes a workflow, identify missing primitives and propose names for them.

### Namespace pollution guardrail (anti-generic)
If a candidate is too generic (likely to be produced by many agents), prefer one of:
- add a **vibe marker** (vitality lane) that still reads clean
- add a **role marker** (pay/verify/claims/record)
- produce a **set** (flagship + satellites) so the ecosystem has handles, not mush

### Social liquidity check
Prefer names that will be adopted socially (easy to repeat, easy to tag, easy to remember) over “technically available but socially dead.”

Also run lightweight **confusion safety** checks on finalists (complementary to linguistic humility):
- **2am test**: does it *visually parse* under low cognitive load (tired, small screen)?
- **Dictation test**: would voice-to-text likely capture it across accents?
- **Typo radius**: avoid names where one-letter typos become other common words.

Important: the 2am test is about **visual parsing**, not “Western mouthfeel.” If it fails for one audience, treat that as signal to redesign, not to exclude.

Common missing primitives in agent economies:
- **handoff artifact** (context bundle) → “workpack”, “taskpack”
- **receipt for work** (verifiable) → “workreceipt”, “claimreceipt”
- **bounty lifecycle** (post→claim→deliver→payout) → “bountyloop”
- **crew split** (multi-party payout) → “splithub”, “splitrail”

When you propose a primitive, also propose:
- 1 sentence of “what it is”
- 1 sentence of “why moltys need it now”

## Bundled resources

- For curated building blocks and “molty-speak primitives”, read: `references/blocks.md`
- For scripts to generate candidates in batches, run: `scripts/forge.mjs` (does not check availability)
