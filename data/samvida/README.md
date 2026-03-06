# Samvida

> OpenClaw skill that crawls your business website, fills gaps conversationally, and generates a structured `llms.txt` — the agentic contract that makes your business readable and transactable by AI agents.

Samvida is not a template filler. It's a multi-pass generation pipeline: crawl → extract → gap-fill conversationally → generate prose-rich, AEO-optimized output → deploy to Cloudflare Workers in one command.

The output follows the [llmstxt.org](https://llmstxt.org) spec with business-specific extensions — a mandatory `## FAQs` section written for agent reasoning, inline Q&A that lets an agent answer "is this right for me?" without crawling the site, and a prose block that gives agents the context they need to make fit decisions.

---

## What is llms.txt?

`llms.txt` is a markdown file at `yourdomain.com/llms.txt`. It tells AI agents what your business does, who it serves, how to interact with it, and what questions it can answer on your behalf.

Think of it as a contract between your business and every AI agent that might recommend, purchase from, or interact with you. Without it, agents guess. With it, agents reason.

---

## What Samvida generates

Every output includes:

- **Prose block** — 3–6 sentences of AEO-friendly context that lets an agent assess fit before recommending your business
- **`## Services`** — every offering with a link and a one-line description of what it does and who it's for
- **`## Team`** — founders and key people with LinkedIn profiles and contact emails, for agent trust
- **`## Clients & Testimonials`** — ICP definition, named client subsections with verbatim quotes and outcomes
- **`## For Agents`** — what an agent can actually do with your business right now (API actions, or a "coming soon" notice with contact path)
- **`## Pricing`** — enough detail for an agent to qualify a lead
- **`## FAQs`** — 6–10 inline Q&A pairs written from the agent's user's perspective: "Is this right for me?", "How does X work?", "What does it cost?", "Can I do Y?" — answered without requiring the agent to follow a link
- **`## Links`** — every link with a description, no bare URLs
- **`## Optional`** — supplementary resources with descriptions, safe to skip under token pressure

---

## How it works

```
1. Crawl        → fast crawl of your site (L1 + L2 pages)
2. Deep crawl   → full raw text extraction if needed ("dig deeper")
3. Gap report   → shows Pass 1 draft + what was and wasn't found
4. Conversation → fills missing data one question at a time
5. Generate     → AEO-optimized llms.txt with prose, FAQs, full descriptions
6. Deploy       → Cloudflare Workers deployment in one command
```

---

## Usage

Trigger via OpenClaw chat:

```
use samvida to generate llms.txt for mybusiness.com
```

Or:

```
generate an agentic contract for mybusiness.com
create an llms.txt for mybusiness.com
make my site agent-readable
```

Samvida will crawl the site, show a draft with a gap report, ask a few targeted questions, and produce the final file. Say **"deploy"** to push it live.

---

## AEO — Agent Experience Optimization

Standard llms.txt files are transactional: a list of links with descriptions. Samvida generates AEO-optimized output — files written so agents can *reason* about your business, not just look things up.

The three pillars of AEO in Samvida's output:

**1. Prose for reasoning**
The free-form block after the summary answers: what problem does this solve, what makes it different, who is it NOT for, what does a typical customer get. Agents use this to make fit decisions — "yes, this is relevant for this user" or "no, this isn't right."

**2. FAQs as agent memory**
The `## FAQs` section is written from the agent's user's perspective. Questions an agent gets asked that it can answer by reading the file — without crawling the site, without following links. This is what makes the contract useful in real agentic workflows.

**3. Described links everywhere**
Every link in `## Links` and `## Optional` has a one-line description. Links without context are dead weight in a token-constrained window.

---

## Deploy

Samvida deploys via Cloudflare Workers — your `llms.txt` is served directly from your domain's edge network, with no CMS changes required.

You need three things from Cloudflare:
1. **API Token** — Cloudflare dashboard → My Profile → API Tokens → Create Token → "Edit Cloudflare Workers" template
2. **Account ID** — top-right of your Cloudflare dashboard
3. **Zone ID** — Cloudflare dashboard → click your domain → right sidebar under "API"

Say `deploy` in the Samvida conversation and it'll walk you through the rest.

---

## File structure

```
samvida/
├── SKILL.md                        # OpenClaw skill definition and workflow
├── README.md                       # This file
├── package.json                    # Skill metadata
├── scripts/
│   ├── crawl.py                    # Multi-mode web crawler (fast + deep)
│   └── deploy.py                   # Cloudflare Workers deployment
└── references/
    ├── llms_txt_spec.md            # Full spec + AEO rules + generation guidelines
    └── cloudflare_api.md           # Cloudflare deployment reference
```

---

## Part of the OpenClaw skill ecosystem

Samvida is an [OpenClaw](https://openclaw.ai) skill. Install via [ClawHub](https://clawhub.com):

```
install samvida from clawhub
```

OpenClaw is an agentic OS that gives AI assistants persistent memory, tool access, and cross-channel presence. Skills extend what your agent can do.

---

## License

MIT
