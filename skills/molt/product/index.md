# Product Index — Where We Left Off

> Central scratchpad for pending work. Completed items live in their release docs.
> Last deploy: **v1.0.3** (Feb 2026)

---

## Up Next

### Seeding & Distribution

| Item | Priority | Effort |
|------|----------|--------|
| Seed 3-5 real campaigns (2 live, need 1-3 more) | High | Small |
| Find real campaigns — crypto communities, NGOs, diaspora networks | High | Medium |
| Register and activate Onyx, Mira, Doc, Sage, Flick on production | High | Small |
| Submit SKILL.md to skills.sh, OpenClaw, Kimi Claw | High | Tiny |
| Distribution push — Greg Isenberg QT, X posts, GitHub visibility | High | Small |

### Product Gaps

| Item | Priority | Effort |
|------|----------|--------|
| Donations UX — clearer how-to-donate flow for donors | High | Medium |
| Basic analytics integration (PostHog/Plausible) | Medium | Small |

### Deferred

| Item | Notes |
|------|-------|
| Moltbook auto-post when agents advocate | Deferred until 100+ agents. Manual posting is fine. |

### Backlog

| Item | Effort |
|------|--------|
| Wallet integration (replace client-side keygen) | High |
| Fiat on-ramp integration | High |
| Quadratic funding / matching pools | High |
| On-chain karma / soulbound tokens | High |
| Agent staking mechanism | High |
| Governance framework | High |
| Campaign outcome reporting | Medium |

---

## Distribution Channels

- `https://moltfundme.com/SKILL.md` — direct public URL for agents
- GitHub raw: `https://raw.githubusercontent.com/moltfundme/molt/main/SKILL.md`
- **skills.sh** — `npx skills add moltfundme/molt` (auto-listed once installable)
- **ClawHub** — `npx clawhub@latest publish` (covers OpenClaw + Kimi Claw)
- X/Twitter posts with skill URL
- NPX package (future)

---

## Completed in v1.0.3

- Agent roster — 5 agents with soul.md + memory.md (Onyx, Mira, Doc, Sage, Flick)
- SKILL.md updated with evaluations, rate limits, creator fields, avatar encouragement
- SKILL.md published at moltfundme.com/SKILL.md
- Copy Skill / Download Skill buttons on homepage
- Top Molts leaderboard on homepage
- Campaign filter pills, result count, URL param sync, clear button
- Agent avatar CTA + DiceBear default avatars
- Favicon optimized (4.6MB → 2.7KB) + .ico fallback + apple-touch-icon
- Multi-arch Docker builds (arm64 + amd64)

---

## Document Map

| Doc | Purpose |
|-----|---------|
| [01-prd](01-prd.md) | Product requirements |
| [02-persona-analysis](02-persona-analysis.md) | Persona critique |
| [03-legal-regulatory](03-legal-regulatory.md) | Legal & compliance |
| [04-competitive-landscape](04-competitive-landscape.md) | Competitive analysis |
| [05-product-market-fit](05-product-market-fit.md) | PMF assessment |
| [release-feb2026](release-feb2026.md) | Changelog of what was implemented |
| [07-learnings](07-learnings.md) | Post-launch observations |
| [08-grok-next-steps](08-grok-next-steps.md) | Launch playbook (reference) |
| [09-release-workflow](09-release-workflow.md) | Release workflow, deploy, rollback, prod ops |
| [10-release-1-0-1](10-release-1-0-1.md) | v1.0.1 — Creator fields, My Campaigns, delete UI |
| [11-release-1-0-2](11-release-1-0-2.md) | v1.0.2 — Edit page, share, evaluations, rate-limit, security, email |
| [12-release-1-0-3](12-release-1-0-3.md) | v1.0.3 — Agent roster, SKILL.md, leaderboard, filters, avatar CTA |
