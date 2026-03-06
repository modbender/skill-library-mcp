---
name: Nuxt
description: Build Vue 3 SSR/SSG applications with proper data fetching, hydration, and server patterns.
metadata: {"clawdbot":{"emoji":"💚","requires":{"bins":["node"]},"os":["linux","darwin","win32"]}}
---

# Nuxt 3 Patterns

## Data Fetching
- `useFetch` deduplicates and caches requests during SSR — use it in components, not `$fetch` which fetches twice (server + client)
- `$fetch` is for event handlers and server routes only — in `<script setup>` it causes hydration mismatches
- `useFetch` runs on server during SSR — check `process.server` if you need client-only data
- Add `key` option to `useFetch` when URL params change but path stays same — without it, cache returns stale data
- `useLazyFetch` doesn't block navigation — use for non-critical data, but handle the pending state

## Hydration Traps
- `Date.now()` or `Math.random()` in templates cause hydration mismatches — compute once in setup or use `<ClientOnly>`
- Browser-only APIs (localStorage, window) crash SSR — wrap in `onMounted` or `process.client` check
- Conditional rendering based on client-only state mismatches — use `<ClientOnly>` component with fallback
- `v-if` with async data shows flash of wrong content — use `v-show` or skeleton states instead

## Auto-imports
- Components in `components/` auto-import with folder-based naming — `components/UI/Button.vue` becomes `<UIButton>`
- Composables in `composables/` must be named `use*` for auto-import — `utils.ts` exports won't auto-import
- Server utils in `server/utils/` auto-import in server routes only — not available in client code
- Disable auto-imports per-file with `// @ts-nocheck` or explicitly import to avoid naming collisions

## Server Routes
- Files in `server/api/` become API routes — `server/api/users.get.ts` handles GET /api/users
- Method suffix (`.get.ts`, `.post.ts`) is required for method-specific handlers — without it, handles all methods
- `getQuery(event)` for query params, `readBody(event)` for POST body — don't access `event.req` directly
- Return value is auto-serialized to JSON — throw `createError({ statusCode: 404 })` for errors

## State Management
- `useState` is SSR-safe and persists across navigation — regular `ref()` resets on each page
- `useState` key must be unique app-wide — collisions silently share state between components
- Pinia stores need `storeToRefs()` to keep reactivity when destructuring — without it, values lose reactivity
- Don't initialize state with browser APIs in `useState` default — it runs on server too

## Middleware
- Global middleware in `middleware/` with `.global.ts` suffix runs on every route — order is alphabetical
- Route middleware defined in `definePageMeta` runs after global — use for auth checks on specific pages
- `navigateTo()` in middleware must be returned — forgetting `return` continues to the original route
- Server middleware in `server/middleware/` runs on all server requests including API routes

## Configuration
- `runtimeConfig` for server secrets, `runtimeConfig.public` for client-safe values — env vars override with `NUXT_` prefix
- `app.config.ts` for build-time config that doesn't need env vars — it's bundled into the app
- `nuxt.config.ts` changes require restart — `app.config.ts` changes hot-reload

## SEO and Meta
- `useSeoMeta` for standard meta tags — type-safe and handles og:/twitter: prefixes automatically
- `useHead` for custom tags, scripts, and links — more flexible but no type safety for meta names
- Meta in `definePageMeta` is static — use `useSeoMeta` in setup for dynamic values
- `titleTemplate` in `nuxt.config` for consistent titles — `%s - My Site` pattern

## Plugins
- Plugins run before app creation — use `nuxtApp.hook('app:created')` for post-creation logic
- `provide` in plugins makes values available via `useNuxtApp()` — but composables are cleaner
- Plugin order: numbered prefixes (`01.plugin.ts`) run first, then alphabetical — dependencies need explicit ordering
- Client-only plugins: `.client.ts` suffix — server-only: `.server.ts` suffix

## Build and Deploy
- `nuxt generate` creates static files — but API routes won't work without a server
- `nuxt build` creates server bundle — deploy the `.output` directory
- ISR with `routeRules`: `'/blog/**': { isr: 3600 }` — caches pages for 1 hour
- Prerender specific routes: `routeRules: { '/about': { prerender: true } }` — builds static HTML at build time
