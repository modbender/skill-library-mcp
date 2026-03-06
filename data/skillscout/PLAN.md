# SkillScout — Multi-Phase Build Plan

**Mission:** The trust layer for AI agent skills. Curated, security-vetted, agent-first.

**Differentiator:** Others provide raw pipes to registries. We provide vetted recommendations with trust scores. The Wirecutter for agent skills.

---

## Phase 1: Foundation (Week 1)
**Goal:** Working static site with 50 reviewed skills + live on GitHub Pages

### 1A: Batch Review Pipeline
**Agent:** Isolated review agent (DeepSeek, read-only)
- Fetch top 50 skills from the VoltAgent awesome-list (pre-filtered for quality)
- Run each through the 3-stage pipeline (blocklist → isolated review → approval)
- Generate structured review markdown for each
- Populate skills.json with all reviewed skills

### 1B: Static Site Generator
**Agent:** Main agent (Nash)
- Build Jekyll/Hugo site from reviews/ and data/
- Category pages ("I want my agent to help me with...")
- Individual skill review pages
- Search/filter by category, trust score, tags
- Mobile-first, clean design
- Deploy to GitHub Pages: skillscout.github.io (or nashbot67.github.io/skillscout)

### 1C: Schema.org + SEO
**Agent:** Main agent
- Add structured data (JSON-LD) to every page
- OpenGraph tags for social sharing
- Sitemap.xml + robots.txt
- Programmatic SEO pages: "{skill} review", "{skill} alternatives", "best {category} skills"

**Deliverable:** Live site with 50 vetted skills, browsable by humans AND parseable by LLMs.

---

## Phase 2: Agent-First Interface (Week 2)
**Goal:** MCP server that any agent can query for skill recommendations

### 2A: MCP Server
**Agent:** Main agent (Nash)
- Build MCP server (TypeScript, npm package)
- Tools exposed:
  - `search_skills(query, category?)` → Returns top matches with trust scores
  - `get_skill(name)` → Full review + install instructions
  - `get_categories()` → List all categories
  - `get_safe_skills(category?)` → Only 🟢 Safe skills
  - `report_skill(name, issue)` → Flag a problem
- Data source: skills.json (bundled, updated on publish)
- Publish to npm: `@skillscout/mcp`
- List on Smithery for discovery

### 2B: A2A Agent Card
**Agent:** Main agent
- Create `/.well-known/agent-card.json` on the site
- Describes SkillScout's capabilities in A2A protocol format
- Allows other agents to discover us programmatically

### 2C: REST API (Static)
**Agent:** Main agent
- GitHub Pages serves skills.json, categories.json, blocklist.json as static API
- CORS headers enabled
- Versioned endpoints: `/api/v1/skills.json`
- Zero hosting cost

**Deliverable:** Any agent can `npx @skillscout/mcp` and query us as a tool. Listed on Smithery.

---

## Phase 3: Scale Reviews (Week 3-4)
**Goal:** 200+ reviewed skills, automated pipeline, community contributions

### 3A: Automated Review Queue
**Agent:** Cron job + isolated review agents
- Daily cron: scan ClawHub for new/updated skills
- Auto-fetch source, run Stage 1 blocklist scan
- Queue passing skills for isolated agent review
- Flag reviews for human approval
- Target: 10-20 new reviews per day

### 3B: Community Submissions
**Agent:** Main agent
- GitHub Issues template: "Request a skill review"
- Community can submit skills they want reviewed
- Upvote system (GitHub reactions) to prioritize
- Contributors can submit their own reviews (PR-based, human-approved)

### 3C: Blocklist Enrichment
**Agent:** Isolated security agent
- Ingest VoltAgent's 396 flagged malicious skills
- Cross-reference AgentVerus scan data
- Build comprehensive blocklist with reasons
- Publish as public resource (other tools can consume)

**Deliverable:** 200+ skills reviewed, self-sustaining pipeline, community engagement.

---

## Phase 4: Monetization (Month 2-3)
**Goal:** First revenue

### 4A: Featured Listings
- Skill developers pay to be featured ($49-197/month)
- "Verified Developer" badge ($99 one-time)
- Featured placement in MCP search results
- Clear "sponsored" labeling (trust is sacred)

### 4B: Premium API
- Free tier: 100 queries/day (sufficient for personal agents)
- Pro tier: unlimited queries ($9/month)
- Enterprise: custom feeds, webhooks, bulk data ($49/month)

### 4C: Newsletter
- Weekly "Best New Skills" digest
- Sent to OpenClaw community
- Sponsored slots ($100/issue)

**Deliverable:** Revenue stream from developer ecosystem.

---

## Agent Assignments

| Agent | Role | Model | Session Type |
|-------|------|-------|-------------|
| **Nash** (main) | Architecture, site build, MCP server, coordination | Opus/Sonnet | Main session |
| **Review Agent** | Security analysis of individual skills (read-only, no execution) | DeepSeek | Isolated spawn |
| **Batch Scanner** | Fetches skill source code, runs blocklist checks | Sonnet | Isolated spawn |
| **Site Builder** | Generates static site from reviews data | Sonnet | Isolated spawn |

---

## Technical Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Static site | Jekyll + GitHub Pages | $0 |
| Data store | JSON files in git | $0 |
| MCP server | TypeScript + npm | $0 |
| Reviews | Markdown files | $0 |
| CI/CD | GitHub Actions | $0 |
| Search | Client-side JS (lunr.js) | $0 |
| Review agent | DeepSeek via OpenClaw | ~$0.004/review |
| Domain | skillscout.dev (optional) | $12/year |
| **Total** | | **~$1/month** |

---

## Success Metrics

### Month 1
- [ ] 50+ skills reviewed and published
- [ ] Static site live on GitHub Pages
- [ ] MCP server published on npm + Smithery
- [ ] First external user installs MCP server

### Month 3
- [ ] 200+ skills reviewed
- [ ] 100+ MCP server installs
- [ ] First revenue ($100+)
- [ ] Cited by at least one LLM in search results

### Month 6
- [ ] 500+ skills reviewed
- [ ] 1,000+ monthly site visitors
- [ ] $500+/month revenue
- [ ] Recognized as trusted source in OpenClaw community

---

## Immediate Next Steps (Tonight)

1. ✅ Repo created, architecture documented, first review complete
2. 🔨 **NOW:** Batch review top 50 skills from awesome-list
3. 🔨 **NOW:** Build static site generator
4. 🔨 **NOW:** Build MCP server
5. 🔨 Deploy to GitHub Pages
6. 🔨 Publish MCP server to npm
