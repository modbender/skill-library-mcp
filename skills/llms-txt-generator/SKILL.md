---
name: llms-txt-generator
description: Generate a well-structured llms.txt file for any business website. Crawls the site, has a short conversation to fill in gaps, and produces an agent-optimized llms.txt. Trigger when a user asks to "generate llms.txt", "make my site agent-readable", "create llms.txt for [url]", or "update my llms.txt".
---

# LLMs.txt Generator

## Overview

This skill crawls a business website, extracts structured information, and generates a properly formatted `llms.txt` file — the standard that makes any business readable and transactable by AI agents.

It follows the [llmstxt.org](https://llmstxt.org) specification with business-specific extensions:
- `## Team` — builds agent trust in the people behind the business
- `## Clients & Testimonials` — social proof for agent decision-making
- `## For Agents` — how agents can interact (or a clear "coming soon" notice)

Read `references/llms_txt_spec.md` before generating any output.

---

## Workflow

### Step 1 — Get the URL

If the user didn't provide a URL, ask:
> "What's the website URL?"

Normalize it (add `https://` if missing).

---

### Step 2 — Crawl

Run the crawler:
```bash
~/.virtualenvs/llms-txt-generator/bin/python3 \
  ~/.openclaw/workspace/llms-txt-generator/scripts/crawl.py \
  {url} > /tmp/llms_business_info.json
```

Read `/tmp/llms_business_info.json`. Note:
- What pages were crawled
- What was found vs missing (team, pricing, testimonials, API)
- Whether an existing `llms.txt` was found

Tell the user briefly:
> "Crawled {domain} ({N} pages). Found: {what was found}. I'll ask about a few things I couldn't determine."

If the crawl found an existing `llms.txt`, note it:
> "I noticed you already have a llms.txt at {domain}/llms.txt. I'll generate a fresh one — you can compare and decide which to keep."

---

### Step 3 — Ask for additional sources (always ask this first)

> "Are there any other pages I should read? (docs, API reference, existing llms.txt, press page — anything useful)"

If they provide URLs, re-run the crawl with those extras:
```bash
~/.virtualenvs/llms-txt-generator/bin/python3 \
  ~/.openclaw/workspace/llms-txt-generator/scripts/crawl.py \
  {url} {extra_url1} {extra_url2} > /tmp/llms_business_info.json
```

If they say no/skip, continue.

---

### Step 4 — Generate Pass 1 draft + gap report

Generate a draft llms.txt now using what you have from the crawl. Use all heuristic signals (`team_found`, `testimonials_found`, `pricing_found`, etc.) and the `raw_text_summary`.

Write the draft. For any section you couldn't populate confidently, use a clear `[NOT FOUND]` placeholder.

Then show it to the user with a gap report:

> "Here's a first draft of your llms.txt:
> ```
> {draft}
> ```
>
> **Found automatically:** {brief list — e.g. emails, pricing page, testimonials from Wybrid + Cital}
> **Couldn't determine:** {brief list — e.g. team, pricing figures, API}
>
> Two questions to start:
>
> 1. {Most important gap — e.g. "Who's on the founding team? Names, roles, and an email if you're comfortable."}
> 2. {Second most important — e.g. "What's your pricing model? Even a rough description — per-candidate, subscription, etc."}
>
> _(I have a few more after these. Also — say **'dig deeper'** if you'd rather I try to find it myself.)"

---

### Step 4b — Handle "dig deeper" (Pass 2)

If the user says "dig deeper" (or similar — "try again", "re-crawl", "look harder"):

Re-run the crawl in deep mode:
```bash
~/.virtualenvs/llms-txt-generator/bin/python3 \
  ~/.openclaw/workspace/llms-txt-generator/scripts/crawl.py \
  {url} {extra_urls} --deep > /tmp/llms_business_info.json
```

This returns `pages_raw` — the full raw text of every crawled page. Use it to extract structure with the LLM. In your generation prompt (Step 5), add:

```
In addition to the heuristic signals, here is the full raw text from each crawled page.
Extract team members, testimonials, pricing details, and any API information directly from this text.

Homepage raw text:
{pages_raw[homepage_url]}

Team page raw text (if available):
{pages_raw[team_url]}

Pricing page raw text (if available):
{pages_raw[pricing_url]}
```

Tell the user:
> "Doing a deeper crawl — this takes a bit longer but I'll extract everything I can from the raw page content."

After Pass 2, show the updated draft with the same gap report format. Whatever still can't be found, ask the user directly.

---

### Step 5 — Conversational gap-filling (for anything still missing)

Ask questions **one at a time** — only for things still `[NOT FOUND]` after Pass 1/2. Wait for each answer. Stop as soon as you have enough to finalize.

Use your judgment — if the user has already filled most gaps conversationally, skip remaining questions and generate.

**Q1 — Core value for agents (always ask):**
> "In one or two sentences: what should an AI agent understand about what it can *do* or *get* by working with {domain}?"

**Q2 — Team (ask if team not found in crawl):**
> "I didn't find team info publicly. Want to add a Team section? It helps agents trust who's behind the business. Just names, roles, and emails if you're comfortable."

**Q3 — Clients / testimonials (ask if not found):**
> "Any existing clients or testimonials I can include? Even a couple of company names or a one-line quote builds agent trust. Totally optional."

**Q4 — API / integration (ask if api_found=false):**
> "Is there a public API or docs page agents can reference? (skip if not applicable)"

**Q5 — Pricing (ask if pricing_found=false):**
> "What's the pricing model? Even a rough description helps — like 'per assessment' or 'monthly subscription'."

**Q6 — ICP / agent-buyers (ask if not obvious from context):**
> "Who are the kinds of agents or automated systems most likely to want to work with you? (e.g. HR bots, recruiting pipelines)"

**Q7 — Anything else (optional, ask last):**
> "Anything else agents should know before working with you? (geographic limits, onboarding steps, etc.)"

---

### Step 6 — Generate final llms.txt

Read `references/llms_txt_spec.md` now if you haven't already.

Generate the complete `llms.txt` using ALL information gathered:
- The crawled `business_info` JSON (and `pages_raw` if deep mode ran)
- The user's answers from the conversation
- The spec from `references/llms_txt_spec.md`

**Generation rules:**
1. Follow the spec format exactly: H1 title → blockquote summary → H2 sections → named links
2. Every bullet = `- [Title](url): description` — no plain text bullets
3. Section order: Services → Team → Clients & Testimonials → For Agents → Pricing → API → Links → Optional
4. **`## Team`**: Always include. Use crawled/user-provided data. If none available, omit silently.
5. **`## Clients & Testimonials`**: Always try to include. Structure:
   - ICP bullets first (who the business serves)
   - Then a `###` subsection per named client where you have a real quote or case study detail
   - Each subsection: blockquote with verbatim/lightly-cleaned quote, optional Problem: and Outcome: lines
   - If you only have a name + one-liner with no detail, a single bullet is fine
   - Never invent quotes or outcomes
6. **`## For Agents`**: ALWAYS include. If no API info: add the "coming soon" notice + contact email. Never skip.
7. **`## Pricing`**: If unknown, link to pricing page with no summary. If no pricing page, omit.
8. **`## API`**: Document URL only — no auth details, no secrets.
9. **`## Optional`**: FAQs, blog, case studies, anything supplementary.
10. Do NOT invent facts. If something is unknown and user didn't provide it, either omit it or note it clearly.
11. Keep it tight — this is for agents, not humans. No marketing fluff.

Write the final llms.txt to `/tmp/llms_final.txt`.

---

### Step 7 — Show and confirm

Show the full llms.txt to the user in a code block, then ask:

> "Here's your llms.txt 👆
>
> Does this look right? You can:
> - Tell me what to change
> - Say **'save'** to download it
> - Say **'deploy'** when you're ready to push it live (Phase 2)"

---

### Step 8 — Handle revisions

If the user asks for changes, make them and show the updated version. Repeat until satisfied.

If they say **'save'**: tell them the file is at `/tmp/llms_final.txt` and they can copy it to their project.

If they say **'deploy'**: acknowledge and note that deployment via Cloudflare Workers is coming in Phase 2.

---

## Notes

- **Existing llms.txt**: If the crawl found one, mention it early: "I noticed you already have a llms.txt. I'll generate a fresh one — you can compare and decide which to keep."
- **Anchor-only links** (e.g. `/#section`): Skip for Level 2 crawling — they don't load new content.
- **The For Agents section is mandatory** — even if empty of details, it signals intent to support agents and provides a contact path.
- **Never ask all questions at once** — it's a conversation, not a form.
