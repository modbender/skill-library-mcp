---
name: vercel-speed-audit
description: Optimize Vercel build and deploy speed — audit checklist for new and existing projects.
---

# Vercel Speed Audit Skill

Optimize Vercel build and deploy speed for any project. Run as a checklist when starting new projects or auditing existing ones.

## When to Use

- **New project setup** — configure optimal defaults from day one
- **Build times creeping up** — audit and fix performance regressions
- **Deploy queue bottlenecks** — eliminate waiting on concurrent builds
- **Production incidents** — use instant rollback instead of waiting for a new build
- **Cost optimization** — balance speed vs spend on build infrastructure

## Triage First (Don't Blindly Run All 10)

Before running the full checklist, **measure and assess**:

```bash
# 1. Check current build times
cd <project> && npx vercel ls --limit 5

# 2. Check team/plan tier
npx vercel team ls
```

**Decision tree:**

| Build Time | Action |
|-----------|--------|
| **< 20s** | Only do items 0, 1, 3-5, 10. Skip GitHub Actions (#8), skip barrel file audit (#6) unless codebase is large. |
| **20-60s** | Do items 0-7, 10. GitHub Actions (#8) is optional. |
| **60s+** | Do everything. GitHub Actions (#8) becomes high-value. |

**Auth-gated app?** (All pages behind login)
→ **Skip ISR (#9)** entirely. ISR caches one response for all users — incompatible with per-user content.

**Framework:**
→ SvelteKit: Also read `docs/sveltekit.md` — includes adapter-vercel switch, prerendering, $env tips.
→ Next.js/Nuxt/Other: `docs/general.md` covers framework-agnostic items.

## Checklist (Ordered by Impact)

| # | Optimization | Impact | CLI-checkable? | Plan Required |
|---|-------------|--------|:-:|:-:|
| **0** | **Use explicit adapter** (e.g., `adapter-vercel` not `adapter-auto`) | Faster, no detection overhead | ✅ Check config | Any |
| **1** | **Turbo Build Machines** | 50-70% faster builds | ❌ Dashboard only | Pro+ |
| **2** | **On-Demand Concurrent Builds** | Eliminates deploy queue | ❌ Dashboard only | Pro+ |
| **3** | **Prerender Static Pages** | Fewer functions, faster TTFB | ✅ Audit code | Any |
| **4** | **Ignored Build Step** | Skip irrelevant builds | ✅ Check vercel.json | Any |
| **5** | **Prioritize Production Builds** | Prod deploys go first | ❌ Dashboard only | Pro+ |
| **6** | **Eliminate Barrel Files** | 10-30% build speedup | ✅ Audit code | Any |
| **7** | **Audit & Trim Dependencies** | Faster install + bundle | ✅ Run depcheck | Any |
| **8** | **GitHub Actions + `--prebuilt`** | Full cache control, skip Vercel build | ✅ Add workflow | Any |
| **9** | **ISR for Dynamic Pages** | Fewer cold starts | ✅ Audit routes | Any |
| **10** | **Instant Rollback** | Zero-downtime recovery | ✅ `vercel rollback` | Hobby: last only; Pro+: any |

**Pro plan items (#1, #2, #5):** If not on Pro, check team plan first. These are the highest-impact free wins on Pro.

## Dashboard Links (Can't Check via CLI)

For a team called `<team-slug>`:
- **Turbo machines:** `https://vercel.com/<team-slug>/<project>/settings` → General → Build Machine
- **Concurrent builds:** `https://vercel.com/teams/<team-slug>/settings` → Build Queue
- **Prioritize prod:** `https://vercel.com/<team-slug>/<project>/settings` → Git → Production prioritization

## Docs

- **[docs/checklist.md](docs/checklist.md)** — Full detailed checklist with how-to for each item
- **[docs/sveltekit.md](docs/sveltekit.md)** — SvelteKit-specific optimizations
- **[docs/general.md](docs/general.md)** — Framework-agnostic Vercel optimizations
- **[docs/github-actions-prebuilt.md](docs/github-actions-prebuilt.md)** — GitHub Actions + `vercel deploy --prebuilt` guide

## Lessons Learned

Real-world findings from running all 10 checks on a SvelteKit project with 16-18s builds:

1. **Half the checklist was overkill** — builds were already fast. Triage step now prevents wasted effort.
2. **ISR is irrelevant for auth-gated apps** — every page served per-user content. Added decision tree.
3. **`adapter-auto` → `adapter-vercel` was a missed win** — not in original 10 but came up in dep audit. Now item #0.
4. **Dashboard-only settings are the highest-impact items** (Turbo, concurrent, priority) but can't be verified via CLI. Added direct links.
5. **GitHub Actions + prebuilt only worth it at 60s+** — for fast builds, the Vercel Git integration is simpler and equally fast.
6. **The dep audit found the project was already lean** (11 deps, 84MB node_modules, 472K client bundle). Only one unused dep (clsx).
7. **Team/plan tier gates most high-impact items** — checking plan should be step 1.

## Quick Start

1. **Triage:** Measure build times + check plan tier
2. **Run applicable items** from the checklist based on decision tree
3. If SvelteKit, also review `docs/sveltekit.md`
4. Track findings in a report file (e.g., `vercel-speed-report.md`)
5. For complex CI needs, follow `docs/github-actions-prebuilt.md`
