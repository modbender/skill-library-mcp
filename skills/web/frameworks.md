# Framework Patterns and Traps

## React

- **State updates are async** — `setState(x)` doesn't immediately change state; use callback form for derived state
- **Keys must be stable** — Don't use array index as key if list reorders; causes bugs with forms/animations
- **useEffect dependencies** — Missing deps cause stale closures; ESLint exhaustive-deps catches these
- **useEffect cleanup** — Return cleanup function for subscriptions/timers; prevents memory leaks
- **Conditional hooks** — Hooks can't be in conditions/loops; breaks React's hook order tracking
- **Context rerenders** — Every consumer rerenders when context value changes; memoize or split contexts

## Next.js (App Router)

- **Server vs Client Components** — Default is server; add `"use client"` for hooks, browser APIs, events
- **`fetch` in Server Components** — Automatically deduped and cached; use `{cache: 'no-store'}` for fresh
- **Middleware runs on edge** — No Node APIs; limited to Web APIs and edge-compatible packages
- **Route handlers** — Export `GET`, `POST` functions from `route.ts`; not `page.tsx`
- **`revalidatePath`/`revalidateTag`** — Call after mutations to bust cache; ISR invalidation
- **Parallel routes** — Use `@folder` convention for loading multiple routes in same layout
- **`NEXT_PUBLIC_` prefix** — Required for env vars in client code; others are server-only

## General SPA

- **Hydration mismatch** — Server and client must render identically on first pass; use `useEffect` for client-only
- **Bundle size** — Tree-shaking needs ES modules; named imports from lodash don't tree-shake without lodash-es
- **Code splitting** — Use `lazy()` or `next/dynamic` for below-fold components; improves LCP
- **SSR data fetching** — Fetch on server to avoid waterfalls; don't fetch in useEffect for initial data
