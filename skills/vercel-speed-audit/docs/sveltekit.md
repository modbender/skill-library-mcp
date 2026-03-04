# SvelteKit-Specific Vercel Optimizations

Optimizations that are specific to SvelteKit projects deployed on Vercel.

---

## adapter-vercel Configuration

The `@sveltejs/adapter-vercel` package controls how SvelteKit outputs are mapped to Vercel's infrastructure.

### Basic Setup

```javascript
// svelte.config.js
import adapter from '@sveltejs/adapter-vercel';

export default {
  kit: {
    adapter: adapter({
      // Runtime: 'nodejs22.x' recommended for latest features
      runtime: 'nodejs22.x',

      // Split routes into separate serverless functions
      // true = one function per route (better cold starts, more granular)
      // false = single function for all routes (simpler, shared cold starts)
      split: false,

      // Memory allocation (MB) — lower = cheaper, higher = faster
      memory: 1024,

      // Max execution duration (seconds)
      maxDuration: 10,

      // Regions — deploy functions close to your users/database
      regions: ['iad1'], // US East (default)

      // ISR configuration (see ISR section below)
      isr: false,
    })
  }
};
```

### Route-Level Configuration

Override adapter settings per-route using `+server.js` or `+page.server.js`:

```typescript
// src/routes/api/heavy-computation/+server.ts
export const config = {
  runtime: 'nodejs22.x',
  memory: 3008,      // More memory for heavy routes
  maxDuration: 30,    // Longer timeout
  regions: ['iad1'],
};
```

### Split vs Single Function

| Setting | Pros | Cons |
|---------|------|------|
| `split: false` (default) | Shared warm instances, simpler | One cold start affects all routes |
| `split: true` | Granular scaling, independent cold starts | More functions to manage, more cold starts initially |

**Recommendation:** Start with `split: false`. Switch to `split: true` if you have routes with very different resource needs (e.g., a heavy API endpoint vs lightweight pages).

---

## Prerendering

SvelteKit has first-class prerendering support. Every page that can be prerendered should be.

### Page-Level Prerendering

```typescript
// src/routes/about/+page.ts
export const prerender = true;
```

### Layout-Level Prerendering

Apply to all child routes:

```typescript
// src/routes/(marketing)/+layout.ts
export const prerender = true;
```

### Global Prerender Default

```typescript
// src/routes/+layout.ts
// Prerender everything by default, opt-out where needed
export const prerender = true;
```

Then opt out for dynamic routes:

```typescript
// src/routes/dashboard/+page.ts
export const prerender = false;
```

### Prerender Crawling

SvelteKit crawls your prerendered pages for links and prerenders those too. Configure in `svelte.config.js`:

```javascript
export default {
  kit: {
    prerender: {
      // Crawl links found in prerendered pages
      crawl: true,
      // Explicit entries to start crawling from
      entries: ['/', '/about', '/blog'],
      // Handle HTTP errors during prerendering
      handleHttpError: 'warn', // or 'fail'
    }
  }
};
```

### What to Prerender

✅ **Prerender these:**
- Marketing/landing pages
- Blog posts and documentation
- About, contact, terms, privacy pages
- Any page with content that only changes at build time

❌ **Don't prerender these:**
- User dashboards (personalized)
- Pages behind authentication
- Pages with real-time data
- Search results pages

---

## $env/static vs $env/dynamic

This is a subtle but important optimization for build and runtime performance.

### `$env/static/private` and `$env/static/public`

```typescript
// Inlined at BUILD TIME — becomes a literal string in the bundle
import { DATABASE_URL } from '$env/static/private';
import { PUBLIC_API_URL } from '$env/static/public';
```

- **Pros:** Zero runtime cost, enables dead-code elimination, smaller bundles
- **Cons:** Requires rebuild to change values
- **Use for:** API URLs, feature flags, app version, anything that changes only at deploy time

### `$env/dynamic/private` and `$env/dynamic/public`

```typescript
// Read at RUNTIME from process.env
import { env } from '$env/dynamic/private';
const dbUrl = env.DATABASE_URL;
```

- **Pros:** Can change without rebuilding (via Vercel env var UI)
- **Cons:** Runtime lookup on every request, can't tree-shake
- **Use for:** Secrets that rotate, values that might change between deploys

### Recommendation

Default to `$env/static/*`. Only use `$env/dynamic/*` when you genuinely need runtime flexibility. This reduces bundle size and improves cold start times.

---

## ISR Configuration

Incremental Static Regeneration in SvelteKit via adapter-vercel.

### Global ISR

```javascript
// svelte.config.js
export default {
  kit: {
    adapter: adapter({
      isr: {
        // Revalidate every 60 seconds
        expiration: 60,
        // Allow on-demand revalidation via deploy hooks
        bypassToken: process.env.ISR_BYPASS_TOKEN,
      }
    })
  }
};
```

### Per-Route ISR

```typescript
// src/routes/blog/[slug]/+page.server.ts
export const config = {
  isr: {
    expiration: 300, // Revalidate every 5 minutes
  }
};
```

### ISR with Dynamic Paths

```typescript
// src/routes/products/[id]/+page.server.ts
export const config = {
  isr: {
    expiration: 60,
    // Pre-generate these paths at build time
    // Others generated on first request
  }
};

// The load function still runs — ISR caches its output
export async function load({ params }) {
  const product = await fetchProduct(params.id);
  return { product };
}
```

### On-Demand Revalidation

Trigger revalidation for specific paths without waiting for expiration:

```bash
# Revalidate a specific path
curl "https://your-site.vercel.app/blog/my-post?x-prerender-revalidate=YOUR_BYPASS_TOKEN"
```

---

## Edge vs Serverless

SvelteKit on Vercel can run routes as either Edge Functions or Serverless Functions.

### Edge Functions

```typescript
// src/routes/api/fast/+server.ts
export const config = {
  runtime: 'edge',
};
```

**Pros:**
- ~0ms cold start
- Runs in all regions simultaneously
- Lower latency for global users

**Cons:**
- Limited Node.js API (no `fs`, limited `crypto`)
- 128KB code size limit (after bundling)
- Can't use most npm packages that rely on Node.js APIs
- Limited execution time

**Use for:** Simple API routes, redirects, A/B testing, auth middleware, lightweight transformations.

### Serverless Functions

```typescript
// src/routes/api/heavy/+server.ts
export const config = {
  runtime: 'nodejs22.x',
};
```

**Pros:**
- Full Node.js API
- Up to 250MB code size
- Can use any npm package
- Configurable memory (128MB–3008MB)

**Cons:**
- Cold starts (100ms–2s depending on bundle size)
- Runs in configured region(s) only

**Use for:** Database queries, heavy computation, file processing, anything requiring full Node.js.

### Recommendation for SvelteKit

- **Default to serverless** (`nodejs22.x`) — it's the most compatible
- **Use edge** selectively for latency-critical, lightweight routes
- **Don't use edge** for routes that import database clients, ORMs, or heavy libraries
- SvelteKit's `handle` hook in `hooks.server.ts` runs as the configured default runtime — keep it lightweight if using edge

---

## Build Output Optimization

### Minimize Server-Side Dependencies

SvelteKit bundles server-side code separately. Minimize what goes into the server bundle:

```typescript
// Use dynamic imports for heavy server-only dependencies
export async function load() {
  const { processImage } = await import('$lib/server/image-processor');
  return { image: await processImage() };
}
```

### Vite Configuration

```typescript
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  build: {
    // Increase chunk size warning limit if you've audited your bundles
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Group vendor libs that change infrequently
          // 'vendor': ['some-large-lib'],
        }
      }
    }
  }
});
```

### Dependency Optimization

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [sveltekit()],
  optimizeDeps: {
    // Pre-bundle these for faster dev AND faster prod builds
    include: ['lodash-es', 'date-fns'],
    // Exclude packages that cause issues with pre-bundling
    exclude: ['@sveltejs/kit'],
  }
});
```
