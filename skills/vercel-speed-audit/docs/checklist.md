# Vercel Speed Optimization — Detailed Checklist

---

## 1. Turbo Build Machines

**What:** Vercel offers upgraded build infrastructure with more CPU and RAM. Turbo machines use higher-spec hardware that dramatically reduces build times.

**Why it matters:** Build time is the single biggest contributor to deploy latency. A 50-70% reduction means a 3-minute build drops to ~1 minute.

**How to check:**
- Go to Project → Settings → General → Build & Development Settings
- Check "Build Machine" setting — if it says "Standard", you're leaving speed on the table
- Compare recent build times in the Deployments tab

**How to implement:**
1. Project Settings → General → Build Machine → select **Turbo**
2. No code changes required
3. Monitor the next few builds to confirm improvement

**Expected impact:** 50-70% faster builds. This is the single highest-ROI change.

**Cost:** Turbo is included on Pro plans. On Enterprise, check your contract. Turbo builds consume more "build minutes" per wall-clock minute (typically 2x multiplier on usage).

---

## 2. On-Demand Concurrent Builds

**What:** By default, Vercel queues builds — only one runs at a time per project. Concurrent builds let multiple deployments build simultaneously.

**Why it matters:** In active development with multiple PRs, builds stack up. A 3-build queue means the last PR waits 9+ minutes before its deploy even starts.

**How to check:**
- Look at the Deployments tab — if you see "Queued" status on deployments, you're being bottlenecked
- Settings → General → check concurrent build limits

**How to implement:**
1. Go to Team Settings → Billing → look for Concurrent Builds add-on
2. On Pro: purchase additional concurrent build slots ($50/slot/month)
3. On Enterprise: request increase from your account team

**Expected impact:** Eliminates queue wait times entirely. Doesn't make individual builds faster, but dramatically improves throughput during active development.

**Cost:** $50/additional concurrent build slot/month on Pro.

---

## 3. Prerender Static Pages

**What:** Mark pages that don't need server-side rendering as static/prerendered. They become static HTML files instead of serverless functions.

**Why it matters:**
- Fewer serverless functions = faster builds (less to bundle/deploy)
- Static pages serve from CDN edge = instant TTFB
- No cold starts for prerendered pages
- Reduced function count keeps you under limits

**How to check:**
- Review your routes — any page that shows the same content for all users is a candidate
- Check your build output for function count vs static file count
- Look for pages that fetch data at build time only (docs, marketing, blog posts)

**How to implement:**
- Framework-specific (see `sveltekit.md` for SvelteKit)
- General principle: add `export const prerender = true` or equivalent
- For pages with dynamic data that changes infrequently, use ISR instead (item #9)

**Expected impact:** Each prerendered page = one fewer serverless function. For content-heavy sites, this can reduce function count by 50-90%.

---

## 4. Ignored Build Step

**What:** Configure Vercel to skip builds entirely when changes don't affect the project. Uses a script or folder-based check to decide whether to build.

**Why it matters:** In monorepos or when non-code files change (README, docs, CI configs), running a full build wastes time and build minutes.

**How to check:**
- Look at recent deployments — how many were triggered by changes that didn't affect the app?
- Check if you're in a monorepo with other projects

**How to implement:**
1. Project Settings → Git → Ignored Build Step
2. Options:
   - **Folder-based:** Use Vercel's built-in `git diff` — only builds if files in specified folders changed
   - **Custom script:** Write a bash script that exits `0` to skip or `1` to build
   ```bash
   #!/bin/bash
   # .vercel/ignore-build.sh
   # Skip build if only docs changed
   git diff HEAD^ HEAD --quiet -- src/ package.json svelte.config.js
   ```
3. Or use the `vercel.json` `ignoreCommand`:
   ```json
   {
     "ignoreCommand": "git diff HEAD^ HEAD --quiet -- src/ static/ package.json"
   }
   ```

**Expected impact:** Eliminates unnecessary builds entirely. In monorepos, can skip 30-60% of triggered builds.

---

## 5. Prioritize Production Builds

**What:** Configure Vercel to prioritize production (main branch) builds over preview deployments.

**Why it matters:** When the build queue is busy, you want production deploys to jump the line. A hotfix shouldn't wait behind 5 preview deploys.

**How to check:**
- Team Settings → check if production prioritization is enabled
- Look at deployment history — are production deploys getting queued behind previews?

**How to implement:**
1. Team Settings → General → Enable "Prioritize Production Builds"
2. This is a team-level setting, not per-project
3. On Pro plan, this is available by default

**Expected impact:** Production deploys go to the front of the queue. Combined with concurrent builds (#2), production deploys should never wait.

---

## 6. Eliminate Barrel Files

**What:** Barrel files are `index.ts` files that re-export from multiple modules (`export * from './Button'`). Bundlers must parse the entire barrel to resolve any single import.

**Why it matters:** Barrel files defeat tree-shaking and force the bundler to load entire module graphs. Importing one util from a barrel file can pull in hundreds of modules during build analysis.

**How to check:**
- Search for `index.ts` or `index.js` files that only contain re-exports
- Look for import patterns like `import { something } from '@/components'` (importing from a directory index)
- Run a build with `--debug` or timing output to identify slow modules

**How to implement:**
1. Replace barrel imports with direct imports:
   ```typescript
   // Before (barrel)
   import { Button, Input, Modal } from '@/components'

   // After (direct)
   import { Button } from '@/components/Button'
   import { Input } from '@/components/Input'
   import { Modal } from '@/components/Modal'
   ```
2. Delete barrel `index.ts` files or convert them to explicit named exports
3. Use ESLint rule `no-barrel-files` or similar to prevent reintroduction
4. For libraries you don't control, check if they offer deep import paths

**Expected impact:** 10-30% build speedup depending on how many barrel files exist. Largest impact in projects with big component libraries.

---

## 7. Audit & Trim Dependencies

**What:** Review `node_modules` for unnecessary, duplicate, or oversized packages. Remove what you don't need, replace heavy packages with lighter alternatives.

**Why it matters:**
- Install time is part of every build (often 30-60 seconds)
- Large `node_modules` = more to cache/restore
- Unused dependencies still get installed and can slow bundling
- Duplicate packages (different versions of same lib) waste time

**How to check:**
```bash
# Check total node_modules size
du -sh node_modules

# Find largest packages
du -sh node_modules/* | sort -rh | head -20

# Check for duplicates
npx depcheck        # Find unused dependencies
npx npm-check       # Interactive update/remove
```

**How to implement:**
1. Run `npx depcheck` and remove unused packages
2. Check for lighter alternatives:
   - `moment` → `date-fns` or `dayjs`
   - `lodash` → `lodash-es` (tree-shakeable) or native methods
   - `axios` → native `fetch`
3. Pin dependencies to avoid unnecessary resolution
4. Use `pnpm` for faster installs and deduplication (if not already)

**Expected impact:** 10-40% faster install step. Varies wildly by project.

---

## 8. GitHub Actions + `--prebuilt` Deploy Pattern

**What:** Build your project in GitHub Actions (where you control caching and parallelism) then deploy the pre-built output to Vercel using `vercel deploy --prebuilt`.

**Why it matters:**
- Full control over build caching (GitHub Actions cache is more flexible)
- Can run tests, linting, and build in parallel
- Build on faster/custom runners if needed
- Avoid Vercel's build queue entirely — you're deploying already-built output
- Can use CI cache across branches (Vercel cache is per-branch)

**How to check:**
- Are you currently using Vercel's built-in Git integration for builds?
- Do your builds have a significant install/cache-restore step?
- Do you need custom CI steps before deploying?

**How to implement:**
See [docs/github-actions-prebuilt.md](github-actions-prebuilt.md) for the full guide with workflow YAML.

**Expected impact:** 30-60% faster end-to-end deploy time when combined with aggressive caching. Biggest wins in monorepos and projects with expensive test suites.

---

## 9. ISR for Cacheable Dynamic Pages

**What:** Incremental Static Regeneration (ISR) lets you serve cached responses for dynamic pages, regenerating them in the background after a configured interval.

**Why it matters:**
- Pages that change infrequently (product pages, user profiles, dashboards) don't need to render on every request
- ISR gives you the speed of static with the freshness of dynamic
- Reduces serverless function invocations = lower cost and fewer cold starts

**How to check:**
- Review your routes — which dynamic pages could tolerate 60s/5min/1hr staleness?
- Check your serverless function invocation count in Vercel dashboard
- Look for pages where users wouldn't notice a 60-second delay in content updates

**How to implement:**
- Framework-specific (see `sveltekit.md` for SvelteKit ISR config)
- General principle: add ISR config to route handlers with an appropriate revalidation interval
- Start conservative (60s) and increase as you gain confidence

**Expected impact:** 80-95% reduction in function invocations for ISR-enabled routes. Dramatic improvement in TTFB for cached responses.

---

## 10. Instant Rollback

**What:** Vercel's Instant Rollback lets you revert to a previous deployment in seconds, without triggering a new build.

**Why it matters:**
- Bad deploy? Rollback in <1 second instead of waiting 2-5 minutes for a revert build
- No build queue, no build time — it's literally re-pointing the production alias
- Critical for incidents where every second of downtime matters

**How to check:**
- Ensure your team knows this feature exists (it's often forgotten in incident response)
- Test it once on a non-critical deploy to build muscle memory
- Verify your previous deployments are still available (Vercel retains them)

**How to implement:**
1. Go to Deployments → find the last known-good deployment
2. Click the three-dot menu → "Promote to Production"
3. Or use CLI: `vercel promote <deployment-url>`
4. The rollback is instant — no build, no wait

**Best practices:**
- Document the rollback procedure in your incident response runbook
- Set up Vercel deployment protection rules so only certain team members can promote
- Consider automating rollback triggers (e.g., if error rate spikes post-deploy)

**Expected impact:** Recovery time drops from minutes to seconds. Not a build speed optimization per se, but eliminates the need for emergency rebuilds.
