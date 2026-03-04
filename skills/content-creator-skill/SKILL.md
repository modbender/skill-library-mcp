---
name: human-masked-content-creator
description: Meta-skill for orchestrating humanizer, de-ai-ify, copywriting, and tweet-writer to produce high-quality, platform-ready content that sounds authentic and human while preserving factual integrity. Use when users need persuasive posts and thread adaptations with anti-generic voice editing and engagement-focused structure.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"writing_hand","requires":{"bins":["node","npx"],"env":[],"config":[]},"note":"Requires local installation of humanizer, de-ai-ify, copywriting, and tweet-writer."}}
---

# Purpose

Create content that is:
- persuasive and high-signal,
- natural in voice,
- platform-appropriate,
- non-generic and non-template-like.

This skill coordinates upstream writing/editing skills; it does not claim guaranteed virality.

# Required Installed Skills

- `humanizer` (inspected latest: `1.0.0`)
- `de-ai-ify` (inspected latest: `1.0.0`)
- `copywriting` (inspected latest: `0.1.0`)
- `tweet-writer` (inspected latest: `1.0.0`)

Install/update:

```bash
npx -y clawhub@latest install humanizer
npx -y clawhub@latest install de-ai-ify
npx -y clawhub@latest install copywriting
npx -y clawhub@latest install tweet-writer
npx -y clawhub@latest update --all
```

Verify:

```bash
npx -y clawhub@latest list
```

# Requested Scenario Profile

Example scenario:
- User needs a LinkedIn post about remote work.
- The post should feel authentic and engagement-oriented.
- The final output should also include an X thread adaptation (5 tweets).

# Inputs the LM Must Collect First

- `topic` (example: remote work)
- `platform_primary` (`linkedin`)
- `target_audience` (example: managers, founders, ICs)
- `goal` (reach, comments, shares, leads)
- `voice_preferences` (direct, reflective, contrarian, practical)
- `author_context` (first-hand experience, examples, proof points)
- `hard_constraints` (length, tone, banned claims/words)
- `thread_required` (`yes/no`, default `yes` for this scenario)

Do not draft copy before these are explicit.

# Tool Responsibilities

## humanizer

Use as first-pass anti-pattern editor:
- remove common AI writing signals,
- replace inflated/formulaic language with specific concrete phrasing,
- preserve meaning while increasing naturalness.

Important behavior:
- strongly pattern-based rewrite guidance,
- output is rewritten text + change summary,
- no guaranteed numeric score in the base `humanizer` skill.

## de-ai-ify

Use as voice pass:
- reduce robotic transitions and hedging,
- simplify buzzword-heavy language,
- increase conversational rhythm,
- enforce direct, human cadence.

Important behavior:
- style/voice correction layer after humanizer,
- useful for adding opinionated nuance and natural texture.

## copywriting

Use as persuasion structure pass:
- apply AIDA/PAS/FAB where appropriate,
- strengthen opening hook,
- sharpen value proposition,
- add one clear engagement CTA.

Important behavior:
- persuasive framework selection by goal,
- avoid over-salesy tone for social posts.

## tweet-writer

Use as X/Twitter adaptation layer:
- convert long-form message into scroll-stopping tweet/thread format,
- optimize hooks, pacing, and mobile readability,
- enforce concise tweet structure.

Important boundary:
- this is X-oriented optimization, not LinkedIn-native optimization.

# Canonical Pipeline

Use this order unless user requests otherwise.

## Stage 1: Base draft (message-first)

Create a clean first draft for LinkedIn:
- one strong claim/opinion
- one concrete example
- one practical takeaway
- one question for comments

Avoid list-heavy, sterile, template-first drafting.

## Stage 2: Humanizer pass (pattern cleanup)

Run the draft through `humanizer` logic:
- remove inflated symbolism and generic conclusions
- reduce over-structured AI cadence
- replace vague claims with specifics

Output target:
- same core meaning,
- lower obvious AI-pattern density,
- still readable and coherent.

## Stage 3: De-AI-ify pass (voice)

Apply `de-ai-ify` voice shaping:
- remove excessive transitions and hedging
- tighten to direct, natural language
- introduce human rhythm (short + long sentence variation)

Output target:
- sounds like a person with a point of view,
- not like policy copy.

## Stage 4: Copywriting pass (engagement architecture)

Apply `copywriting` frameworks to final LinkedIn post:
- opening: strong hook (bold thesis, tension, or contrarian angle)
- body: concise value block (problem -> insight -> implication)
- close: one engagement question (comments-oriented CTA)

Rule:
- one CTA only.

## Stage 5: X adaptation (5-tweet thread)

Use `tweet-writer` principles to convert the same core argument into exactly 5 tweets:

- Tweet 1: hook
- Tweet 2: context/problem
- Tweet 3: key insight
- Tweet 4: practical framework/example
- Tweet 5: question CTA

Hard constraints:
- no external links in the main tweets unless user explicitly requests
- short, mobile-readable lines
- keep continuity and avoid repeating the same sentence across tweets

# Causal Chain (Scenario Mapping)

For the scenario "LinkedIn post about remote work":

1. Agent drafts initial post on remote-work thesis.
2. `humanizer` flags typical AI-like signals and rewrites for specificity.
3. `de-ai-ify` adds conversational nuance and less robotic cadence.
4. `copywriting` strengthens hook and adds one engagement question.
5. `tweet-writer` transforms core message into a 5-tweet thread.

# Output Contract

Always return:

- `LinkedInPost_Final`
  - final LinkedIn copy

- `VoiceEdits_Summary`
  - key changes from humanizer + de-ai-ify

- `PersuasionStructure`
  - framework used (AIDA/PAS/FAB) and why

- `XThread_5Tweets`
  - exactly five tweets, numbered 1/5 ... 5/5

- `OptionalVariants`
  - 2 alternative hooks
  - 2 alternative closing questions

# Quality Gates

Before final output, verify:

- authenticity: text does not read like a rigid template
- specificity: at least one concrete detail/example included
- rhythm: sentence lengths vary naturally
- persuasion: one clear hook + one clear CTA
- platform fit: LinkedIn readable + X thread concise
- integrity: no fabricated data, experiences, or citations

If any gate fails, return `Needs Revision` with explicit reasons.

# Guardrails

- Do not fabricate personal anecdotes or fake proof.
- Do not claim guaranteed virality or guaranteed reach outcomes.
- Do not hide factual uncertainty when claims are unverified.
- Keep persuasive language ethical and non-manipulative.
- Prioritize reader trust over stylistic gimmicks.

# Known Limits from Inspected Upstream Skills

- Base `humanizer` is rewrite-focused and does not define a strict numeric AI score output.
- If numeric AI-likeness scoring is required (for example "85% AI"), this may need the optional `ai-humanizer` variant or explicit custom scoring rubric.
- `tweet-writer` optimizes for X, not LinkedIn ranking mechanics.
- These tools improve quality and naturalness but cannot guarantee SEO outcomes or detection immunity.

Treat these limits as required disclosure when presenting results.
