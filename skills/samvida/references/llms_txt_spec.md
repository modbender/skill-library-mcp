# llms.txt Specification & Examples

## What is llms.txt?

`llms.txt` is a markdown file placed at `https://yourdomain.com/llms.txt`. It gives LLMs and AI agents a structured, concise overview of a business — who they are, what they offer, and how agents can interact with them.

It is intentionally:
- **Short** — agents read it in constrained contexts
- **Structured** — machine-parseable with named links
- **Honest** — no made-up info, no marketing fluff

---

## Canonical Format (from llmstxt.org)

```
# Title

> One-line summary (blockquote)

Optional free-form markdown (bullet points, short paragraphs)

## Section Name
- [Link Title](url): Optional description

## Another Section
- [Link Title](url): Description
```

### Rules:
1. **H1** (`#`) — business name, exactly one
2. **Blockquote** (`>`) — one sentence summary, right after H1
3. **H2 sections** (`##`) — each section groups related named links
4. **Named links** — every bullet is `- [Title](url): description`. This is not optional.
5. **`## Optional` section** — agents may skip this under token pressure. Put supplementary links here.
6. No tables. No images. No HTML. Pure markdown.

---

## Our Business llms.txt Structure

For businesses (not docs sites), we use this section order:

```
# BusinessName

> One sentence. What they do, who they serve.

2-3 sentences of context (what makes them unique, who they're for)

## Services
## Team
## Clients & Testimonials
## For Agents
## Pricing
## API
## Links
## Optional
```

---

## Section Definitions

### `## Services`
What the business offers. Each service is a named link to a relevant page.
```
## Services
- [Service Name](url): What it does, who it's for
```

### `## Team`
Founders and key people. Builds agent trust in who is behind the business.
```
## Team
- [Founder Name](linkedin-or-profile-url): Role. One-line bio. email@domain.com
```
- Include email if available — agents use this to initiate contact
- LinkedIn profile URL preferred if no personal page
- If team not found publicly: populate from user conversation or omit with a note

### `## Clients & Testimonials`
Social proof. Agents use this to judge fit and credibility. Use subsections for individual clients when detail is available.

```
## Clients & Testimonials

- ICP: [Description of ideal customer profile]
- ICP roles: [Job titles of typical buyers]

### [Client / Company Name]
> "[Verbatim or lightly cleaned quote from their testimonial]" — Name, Role, Company

Problem: [What they were struggling with before]
Outcome: [What changed after using the product]

### [Another Client]
> "[Quote]" — Name, Role

Outcome: [Key result]
```

Rules:
- ICP bullets always come first
- Use `###` subsections for each named client where you have a quote or case study detail
- Quote must be real — verbatim or lightly cleaned from public page. Never invented.
- Problem/Outcome lines are optional — include only if the testimonial or case study gives enough detail
- If you only have a name + one-liner quote (no detail), a single bullet is fine — no need to force a subsection
- If no clients found at all: ask user or omit section entirely

### `## For Agents`
The most important section for agentic commerce. What can an agent actually DO?

**If API/integration info available:**
```
## For Agents
- [Action Name](api-endpoint-url): What this does. Input/output description.
- [Another Action](url): Description
```

**If no API info available:**
```
## For Agents
> ⚠️ Full agentic transaction support is coming in a future version.
- [Contact for agent partnerships](mailto:email): Reach out to discuss integration
```

Never omit this section. If info is missing, say so — don't silently skip it.

### `## Pricing`
```
## Pricing
- [Pricing page](url): Summary — e.g. "per-seat, starts at $X/mo"
```
If unknown: link to pricing page with no summary, or omit if no pricing page exists.

### `## API`
```
## API
- [API Docs](url): REST/GraphQL, base URL, brief description of what's available
```
Document the endpoint URL only. No auth details, no secrets. Agent reads the docs for auth.

### `## Links`
```
## Links
- [Homepage](url)
- [Sign up](url)
- [Contact](mailto:email)
- [Blog](url)
```

### `## Optional`
Supplementary links agents can skip under token pressure.
```
## Optional
- [FAQs](url): Common questions
- [Case studies](url): Detailed customer stories
- [Status page](url): Uptime and incidents
```

---

## Full Example — Agent-Ready Business

```markdown
# utkrusht.ai

> Technical hiring assessment platform for software companies. Screens engineers via real on-the-job tasks in live environments — not MCQs, not Leetcode.

Assessments are ~30 mins, video-recorded with AI analysis. 70% of assessments are taken mid-workday. Aimed at engineering teams and recruiters who need accurate signal fast.

## Services
- [Technical Assessment](https://utkrusht.ai): Real on-the-job coding tasks with video recording, AI scoring, and rubric insights
- [SmartRank](https://utkrusht.ai): Natural language candidate filtering — e.g. "startup background + BFSI sector"
- [Candidate Rubrics](https://utkrusht.ai): AI-generated insights from resume, socials, intent signals, salary alignment

## Team
- [Naman Muley](https://linkedin.com/in/namanmuley): Founder & CEO. Building the future of technical hiring. naman@utkrusht.ai

## Clients & Testimonials

- ICP: Custom software development companies and software product startups hiring 2–50 engineers/year
- ICP roles: CEOs, CTOs, Founders, VP Engineering, Head of Technology

### Wybrid
> "Their assessment tests helped us find candidates with the required technical skills and their detailed analysis improved our time spent on interviewing significantly. We now realise how much time we used to waste on screening." — Jaydeep Roman, VP of Products

Outcome: Significant reduction in interview time; higher-quality candidate shortlist.

### Cital
> "We shortlisted 3 strong candidates in just a week, and every single one of them could build robust code!" — Harshal Bhakta, Co-founder

Problem: Relying on recruitment agencies took 2–3 months and still produced weak candidates.
Outcome: 3 strong candidates shortlisted in one week.

## For Agents
> ⚠️ Full agentic transaction support is coming in a future version.
- [Contact for agent partnerships](mailto:api@utkrusht.ai): Reach out to discuss programmatic integration

## Pricing
- [Pricing](https://utkrusht.ai/pricing): Per-candidate assessment model. No credit card required to start.

## API
- [API Docs](https://api.utkrusht.ai/docs): REST API available. Contact for access.

## Links
- [Homepage](https://utkrusht.ai)
- [Sign up](https://utkrusht.ai/signup)
- [Contact](mailto:hello@utkrusht.ai)

## Optional
- [FAQs](https://utkrusht.ai/#faqs): Assessment methodology, candidate experience, platform comparisons
```

---

## Common Mistakes to Avoid

| ❌ Wrong | ✅ Right |
|---------|---------|
| `- Service name: description` (no link) | `- [Service name](url): description` |
| Inventing pricing or team members | Use `[UNKNOWN]` placeholder, ask user |
| Omitting `## For Agents` | Always include it, even if just a "coming soon" notice |
| Long paragraphs in sections | Named links only — keep it scannable |
| Auth tokens or API keys in API section | URL only — agent reads the docs for auth |
| Making up testimonials | Only use what's publicly available or user-provided |

---

## `## Compliance`

Certifications, standards, and regulatory adherence that agents and their users care about when evaluating vendor trust.

```
## Compliance
- [SOC 2 Type II](url): Certified. Annual audit by [Auditor]. Valid through [date].
- [ISO 27001](url): Certified. Information security management.
- [GDPR](url): Compliant. Data processing agreements available on request.
- [HIPAA](url): Compliant. BAA available for healthcare customers.
```

Rules:
- Include only verified, publicly mentioned certifications — never invent
- If a cert page/PDF is linked on the site, use that URL
- If no URL but cert is mentioned in text, use the homepage or trust page as fallback
- Omit section entirely if no compliance info found and user doesn't provide any
- Signal to agents: compliance = trust signal for regulated industry purchases

---

## `## Reviews`

Third-party ratings and professional recognition. Agents use this to assess credibility without crawling review sites.

```
## Reviews
- [G2 — 4.8/5 (120 reviews)](url): Rated top in [category] by verified users
- [ProductHunt — #1 Product of the Day](url): Launched [date], featured by PH community
- [Trustpilot — 4.6/5](url): Excellent rating from [N] verified customer reviews
- [Gartner Peer Insights — 4.5/5](url): Recognized in [Magic Quadrant / Peer Insights category]
- [Capterra — 4.7/5](url): Top-rated in [software category]
```

Rules:
- Only include real, publicly visible ratings — never invent scores
- Link directly to the product's review page (not the review platform homepage)
- Include the score and review count where available
- Awards and recognitions (e.g. "Forbes 30 Under 30", "YC W23") go here too
- Omit section if no third-party reviews found and user doesn't provide any
