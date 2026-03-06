# Framework-Agnostic Vercel Optimizations

Optimizations that apply to any project deployed on Vercel, regardless of framework.

---

## Build Cache Mechanics

Vercel caches `node_modules` and framework-specific build caches between deployments.

### How It Works

1. **Dependency cache:** `node_modules` is cached based on lockfile hash (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`)
2. **Build cache:** Framework build outputs (`.next/cache`, `.svelte-kit`, `.nuxt`) are cached between deploys
3. **Cache scope:** Caches are per-project, per-branch (production branch has its own cache)
4. **Cache invalidation:** Changing the lockfile invalidates the dependency cache; some framework caches auto-invalidate on config changes

### Optimizing Cache Hit Rate

- **Pin dependency versions** — avoid `^` ranges that cause unnecessary lockfile churn
- **Use `pnpm`** — faster installs and better deduplication than npm
- **Don't `npm ci --force`** — this invalidates the entire cache
- **Keep lockfiles stable** — separate dependency update PRs from feature work

### Cache Debugging

In Vercel build logs, look for:
- `"Cache found"` → cache hit, fast install
- `"Cache not found"` → full install, slower
- `"Cache expired"` → forced invalidation

### Force Cache Clear

If builds are broken due to stale cache:
- Redeploy with "Clear Cache and Deploy" option in the Vercel dashboard
- Or use: `vercel --force`

---

## Machine Tiers & Pricing

Vercel offers different build machine tiers with varying performance.

### Available Tiers

| Tier | vCPUs | RAM | Speed | Availability |
|------|-------|-----|-------|-------------|
| **Standard** | 4 vCPU | 8 GB | Baseline | All plans |
| **Turbo** | 16 vCPU | 32 GB | 50-70% faster | Pro & Enterprise |

### Cost Implications

- **Hobby:** Standard only, 6,000 build minutes/month
- **Pro ($20/user/month):**
  - Standard: included in base plan
  - Turbo: consumes build minutes at 2x rate (1 wall-minute = 2 build-minutes)
  - Base: 24,000 build minutes/month
  - Additional: $10 per 1,000 minutes
- **Enterprise:** Custom pricing, typically includes Turbo

### When Turbo Doesn't Help

Turbo machines won't help if your build bottleneck is:
- Network I/O (fetching data from external APIs during build)
- Vercel's internal deploy step (uploading artifacts)
- Queue wait time (need concurrent builds instead)

### Recommendation

Always enable Turbo on Pro/Enterprise. The 2x minute multiplier is almost always worth the 50-70% wall-clock speedup. A 3-minute build at 2x rate = 6 build-minutes but only 1.5 minutes of waiting.

---

## Concurrent Builds

### Default Behavior

- **Hobby:** 1 concurrent build
- **Pro:** 1 concurrent build (upgradeable)
- **Enterprise:** Custom

### Adding Concurrent Builds

- Pro plan: $50/additional slot/month
- Each slot allows one more simultaneous build across all team projects

### How Queuing Works

When all build slots are busy:
1. New builds enter a FIFO queue
2. Production builds can be prioritized (see setting below)
3. Queued builds show "Queued" status in dashboard
4. There's no timeout — builds wait indefinitely

### Cancellation Strategy

Reduce queue pressure by canceling redundant builds:

```json
// vercel.json
{
  "autoCancel": true
}
```

This cancels in-progress preview builds when a new commit is pushed to the same branch. Production builds are never auto-canceled.

---

## Preview Deploy Management

Preview deploys (one per PR/branch) can consume significant build resources.

### Reducing Preview Deploy Overhead

1. **Auto-cancel redundant previews** — enable in `vercel.json` (see above)
2. **Ignored Build Step** — skip builds for non-code changes
3. **Limit preview branches** — use Vercel's Git configuration to only build specific branches:
   ```json
   // vercel.json
   {
     "git": {
       "deploymentEnabled": {
         "main": true,
         "staging": true,
         "feature/*": true,
         "docs/*": false
       }
     }
   }
   ```
4. **Comment-triggered deploys** — use GitHub Actions to only deploy previews when requested (via `/deploy` comment)

### Preview Protection

Password-protect previews to prevent unauthorized access without blocking builds:

```json
// vercel.json
{
  "deploymentProtection": {
    "preview": "standard_protection"
  }
}
```

---

## Edge Config

Vercel Edge Config is a global, low-latency key-value data store.

### What It Is

- Ultra-fast reads (~1ms) from the edge
- Ideal for feature flags, A/B test configs, redirect maps, maintenance mode toggles
- Changes propagate globally in ~seconds (no redeploy needed)

### Why It Matters for Speed

- **No redeploy for config changes** — toggle features without building
- **No function invocation** — Edge Config reads don't count as function calls
- **Sub-millisecond reads** — faster than hitting a database or API

### Setup

```bash
# Install the SDK
npm install @vercel/edge-config

# Create an Edge Config in dashboard: Storage → Edge Config → Create
```

### Usage

```typescript
import { get } from '@vercel/edge-config';

// In any server-side code or middleware
const isMaintenanceMode = await get('maintenance_mode');
const featureFlags = await get('feature_flags');
```

### Use Cases for Build Speed

- **Feature flags** — deploy code behind flags, enable later without redeploy
- **Redirect maps** — update redirects without rebuilding
- **Kill switches** — disable features instantly during incidents
- **Gradual rollouts** — percentage-based feature rollouts without any builds

---

## Environment Variables Best Practices

### Build-Time vs Runtime

| Type | When Resolved | Example |
|------|--------------|---------|
| Build-time | During `vercel build` | `NEXT_PUBLIC_*`, `$env/static/*` |
| Runtime | On each request | `process.env.*`, `$env/dynamic/*` |

### Recommendations

- Use build-time env vars for anything that doesn't change between deploys (API URLs, public keys, feature flags)
- Use runtime env vars only for secrets that rotate or values that need to change without rebuilding
- Build-time vars enable dead-code elimination and smaller bundles

### Vercel-Specific

```bash
# Set env var for all environments
vercel env add MY_VAR production preview development

# IMPORTANT: Use printf, not echo (echo adds trailing newline)
printf 'my-value' | vercel env add MY_VAR production
```

---

## Output File Tracing

Vercel uses NFT (Node File Trace) to determine which files each serverless function needs. Smaller traces = faster deploys.

### How to Optimize

1. **Avoid dynamic requires** — `require(variable)` forces inclusion of everything in the directory
2. **Use specific imports** — `import { specific } from 'package/specific'` instead of `import package from 'package'`
3. **External packages** — for Next.js, use `outputFileTracingExcludes` to exclude unnecessary files:
   ```javascript
   // next.config.js
   module.exports = {
     outputFileTracingExcludes: {
       '/api/*': ['./node_modules/@swc/**'],
     },
   };
   ```

### Debugging Trace Size

Check `.vercel/output/functions/` after building locally with `vercel build` to see function sizes.

---

## Monorepo Optimization

### Turborepo Integration

If using a monorepo with Turborepo:

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".svelte-kit/**", ".next/**", "dist/**"]
    }
  }
}
```

Vercel detects Turborepo and uses Remote Caching automatically on Pro/Enterprise plans.

### Root Directory Configuration

Set the correct root directory for your app in Vercel project settings:
- Project Settings → General → Root Directory
- This ensures Vercel only installs and builds the relevant workspace

### Ignored Build Step for Monorepos

Use `npx turbo-ignore` as your ignored build step — it checks if the current app or its dependencies changed:

```json
// vercel.json (in the app directory)
{
  "ignoreCommand": "npx turbo-ignore"
}
```
