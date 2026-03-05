---
name: cold-outreach-hunter
description: Meta-skill for orchestrating Apollo API, LinkedIn API, YC Cold Outreach, and MachFive Cold Email into a complete B2B cold outreach pipeline. Use when the user wants end-to-end lead sourcing, enrichment, personalized copy strategy, and generation-ready outreach sequences with strict quality and safety gates.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"dart","requires":{"bins":["python3","npx"],"env":["MATON_API_KEY","MACHFIVE_API_KEY"],"config":[]},"note":"Requires local installation of apollo-api, linkedin-api, yc-cold-outreach, and cold-email."}}
---

# Purpose

Run a full B2B cold outreach workflow from ICP definition to sequence-ready output.

Primary objective:
- Identify high-fit leads.
- Enrich context for personalization.
- Produce concise, non-salesy, high-response outreach sequences.
- Return execution-ready assets for external sending/scheduling systems.

This is an orchestration skill. It coordinates upstream skills; it does not replace them.

# Required Installed Skills

- `apollo-api` (inspected latest: `1.0.5`)
- `linkedin-api` (inspected latest: `1.0.2`)
- `yc-cold-outreach` (inspected latest: `1.0.1`)
- `cold-email` (MachFive Cold Email, inspected latest: `1.0.5`)

Install/update with ClawHub:

```bash
npx -y clawhub@latest install apollo-api
npx -y clawhub@latest install linkedin-api
npx -y clawhub@latest install yc-cold-outreach
npx -y clawhub@latest install cold-email
npx -y clawhub@latest update --all
```

Verify availability:

```bash
npx -y clawhub@latest list
```

If any required skill is missing, stop and report exact install commands.

# Required Credentials

- `MATON_API_KEY` for `apollo-api` and `linkedin-api` (Maton gateway)
- `MACHFIVE_API_KEY` for `cold-email`

Preflight checks:

```bash
echo "$MATON_API_KEY" | wc -c
echo "$MACHFIVE_API_KEY" | wc -c
```

If either key is missing or empty, stop before lead processing.

# Job Context Template

Collect these inputs before execution:

- `offer`: what is being sold (example: design service)
- `icp_title`: target role (example: `CMO`)
- `icp_industry`: target industry (example: `SaaS`)
- `icp_location`: target location (example: `Berlin`)
- `lead_count_target` (example: `50`)
- `campaign_goal`: reply, meeting, referral, audit request, etc.
- `proof_points`: case studies, metrics, social proof
- `tone_constraints`: plain-English, short, non-salesy
- `machfive_campaign` (campaign ID or campaign name to resolve)
- `execution_mode`: `draft-only` or `generation-ready`

Do not start writing copy until these are explicit.

# Tool Responsibilities

## Apollo API (`apollo-api`)

Use for lead discovery and basic enrichment.

Operationally relevant behavior from inspected skill:
- Search people: `POST /apollo/v1/mixed_people/api_search`
- Search filters include:
  - `q_person_title`
  - `person_locations`
  - `q_organization_name`
  - `q_keywords`
- Enrich person by email or LinkedIn URL:
  - `POST /apollo/v1/people/match`
- Supports pagination via `page` and `per_page`.
- Uses Maton gateway and optional `Maton-Connection` header.

Primary output of this stage:
- initial lead list with role/company/email/linkedin_url (when available)

## LinkedIn API (`linkedin-api`)

Use for LinkedIn-side context where accessible through provided endpoints.

Operationally relevant behavior from inspected skill:
- Authenticated profile/user info endpoints (for connected account context).
- Content/posting APIs (`ugcPosts`) and organization post/stat APIs.
- Requires `MATON_API_KEY` and LinkedIn protocol headers.

Important boundary:
- The inspected skill is not a generic scraper for arbitrary third-party personal profiles and recent personal posts.
- If a workflow requires deep per-lead personal-post enrichment, mark that as additional-tool-required.

## YC Cold Outreach (`yc-cold-outreach`)

Use as writing strategy/critique framework, not as a transport API.

Core principles to enforce:
- single goal per email
- human tone
- deep personalization (not just token replacement)
- brevity/mobile readability
- credibility and proof
- reader-centric language
- clear CTA

## MachFive Cold Email (`cold-email`)

Use for sequence generation from prepared lead records.

Operationally relevant behavior from inspected skill:
- Campaign required (`campaign_id` mandatory for generate endpoints).
- Single lead sync generation (`/generate`) can take minutes; use long timeout.
- Batch async generation (`/generate-batch`) returns `list_id`; poll list status; export when complete.
- Lead `email` is required.
- Supports structured sequence output with subject/body per step.

# Canonical Workflow

## Stage 1: Build lead universe (Apollo)

1. Query Apollo for ICP-constrained leads (example: CMO + SaaS + Berlin).
2. Page until `lead_count_target` or quality threshold is reached.
3. Normalize each lead record to required fields.
4. Drop records without email if `generation-ready` mode is requested (MachFive requires email).

Recommended normalized lead schema:

```json
{
  "lead_id": "apollo-or-derived-id",
  "name": "Anna Example",
  "title": "Chief Marketing Officer",
  "company": "Startup GmbH",
  "location": "Berlin",
  "email": "anna@startup.com",
  "linkedin_url": "https://linkedin.com/in/...",
  "source": "apollo-api"
}
```

## Stage 2: Enrich personalization context

1. Attempt LinkedIn/API enrichment within supported endpoints.
2. If direct personal-post signal is unavailable, keep the context slot explicit as `not_available`.
3. Optionally enrich from Apollo fields (company, role, keywords, domain context) to avoid fake personalization.

Personalization object per lead:

```json
{
  "icebreaker": "not_available_or_verified_fact",
  "pain_hypothesis": "Likely CRO bottleneck in paid landing pages",
  "proof_hook": "Helped X improve conversion by Y%",
  "confidence": 0.0
}
```

Hard rule:
- Never invent a post, interest, or quote.

## Stage 3: Message strategy (YC framework)

For each lead, create a strategy brief before generating copy:

- Problem: what specific pain this role likely has
- Solution: what your offer solves
- Proof: one concrete metric/client signal
- CTA: one low-friction next step

Apply YC constraints:
- one ask
- short/mobile-first
- human language
- personalization grounded in verifiable context

## Stage 4: Sequence generation (MachFive)

1. Resolve campaign ID first (`GET /api/v1/campaigns`) if not provided.
2. Submit leads with required email field.
3. Prefer batch for many leads; poll until completion.
4. Export JSON result and map sequences back to lead IDs.

Required generation payload hygiene:
- include `name`, `title`, `company`, `email`
- include `linkedin_url` and `company_website` when available
- set `email_count` intentionally (usually 3)
- use approved CTA set aligned with campaign goal

## Stage 5: QA and decision gate

Before declaring output ready, validate each sequence:

- personalization factuality check
- YC rubric check (human, concise, one CTA)
- token insertion sanity (name/company/title correct)
- prohibited claims check (no fabricated proof)

Any failed sequence must be flagged `needs_revision`.

## Stage 6: Scheduling and send handoff

This meta-skill outputs send-ready recommendations, not direct send automation.

If user asks for timing optimization (for example Tuesday 10:00), return it as a scheduling recommendation field and handoff plan.

Example handoff object:

```json
{
  "lead_id": "...",
  "sequence_status": "approved",
  "suggested_send_time_local": "Tuesday 10:00",
  "timezone": "Europe/Berlin",
  "send_system": "external",
  "notes": "Timing is recommendation-only; execution tool must schedule/send."
}
```

# Causal Chain (Scenario Mapping)

For the scenario "sell design services to startup marketing leaders":

1. Apollo returns target leads (example target: 50 CMOs in Berlin SaaS).
2. LinkedIn/API enrichment attempts to add usable context per lead.
3. YC framework converts lead context into a concise Problem → Solution → Proof → CTA angle.
4. MachFive generates multi-step sequences with validated variables.
5. Agent outputs:
   - approved sequences
   - quality score per lead
   - scheduling recommendation (example: Tuesday 10:00 local)

# Output Contract

Always return these sections:

- `LeadSummary`
  - requested vs qualified lead count
  - rejection reasons (missing email, poor fit, duplicate)

- `EnrichmentSummary`
  - fields successfully enriched
  - unavailable fields and why

- `SequencePackage`
  - one object per lead with subjects/bodies by step
  - QA status (`approved` or `needs_revision`)

- `ExecutionPlan`
  - send-time recommendation
  - required external sender/scheduler
  - blockers (missing campaign, missing API key, missing email)

# Guardrails

- Never fabricate personalization facts.
- Never claim a lead posted something unless sourced and verifiable.
- Do not proceed to MachFive generation without campaign ID resolution.
- Do not mark sequence `approved` when CTA is unclear or multiple asks exist.
- Keep language non-manipulative and compliant with outreach policies.

# Failure Handling

- Missing `MATON_API_KEY`: stop Apollo/LinkedIn stages.
- Missing `MACHFIVE_API_KEY`: stop generation stage and return draft-only strategy.
- Missing campaign ID: list campaigns and request explicit selection.
- Batch timeout/partial output: continue via list status + export recovery flow.
- Insufficient lead quality: return reduced high-quality set instead of forcing volume.

# Known Limits from Inspected Upstream Skills

- `linkedin-api` inspected capability set is not equivalent to unrestricted scraping of arbitrary personal lead activity.
- `cold-email` generates sequences but does not itself guarantee outbound send scheduling/execution.
- `apollo-api` provides search/enrichment primitives; email deliverability validation beyond provider fields may require extra tooling.

Treat these as explicit constraints in planning and reporting.
