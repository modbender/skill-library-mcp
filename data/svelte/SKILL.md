---
name: Svelte
description: Avoid common Svelte mistakes — reactivity triggers, store subscriptions, and SvelteKit SSR gotchas.
metadata: {"clawdbot":{"emoji":"🔥","requires":{"bins":["node"]},"os":["linux","darwin","win32"]}}
---

## Reactivity Triggers
- Assignment triggers reactivity — `arr = arr` after push, or use `arr = [...arr, item]`
- Array methods don't trigger — `arr.push()` needs reassignment: `arr = arr`
- Object mutation same issue — `obj.key = val; obj = obj` or spread: `obj = {...obj, key: val}`
- `$:` reactive statements run on dependency change — but only top-level assignments tracked

## Reactive Statements
- `$:` runs when dependencies change — list all dependencies used
- `$: { }` block for multiple statements — all run together
- `$:` order matters — later statements can depend on earlier
- Avoid side effects in `$:` — prefer derived values, use `onMount` for effects

## Stores
- `$store` auto-subscribes in component — automatic unsubscribe on destroy
- Manual subscribe needs unsubscribe — `const unsub = store.subscribe(v => ...); onDestroy(unsub)`
- `writable` for read/write — `readable` for external data sources
- `derived` for computed values — `derived(store, $s => $s * 2)`

## Component Lifecycle
- `onMount` runs after first render — return cleanup function
- No access to DOM before `onMount` — `document` etc. not available in SSR
- `beforeUpdate` / `afterUpdate` for DOM sync — rarely needed
- `tick()` to wait for DOM update — `await tick()` after state change

## Props
- `export let propName` to declare — required by default
- `export let propName = default` for optional — default value if not passed
- Props are reactive — component re-renders on change
- `$$props` and `$$restProps` for pass-through — but explicit props preferred

## Events
- `createEventDispatcher` for custom events — `dispatch('eventName', data)`
- `on:eventName` to listen — `on:click`, `on:customEvent`
- `on:click|preventDefault` modifiers — `|stopPropagation`, `|once`
- Event forwarding: `on:click` without handler — forwards to parent

## SvelteKit
- `+page.svelte` for pages — `+page.server.ts` for server-only load
- `load` function for data fetching — runs on server and client navigation
- `$app/stores` for page, navigating, etc. — `$page.params`, `$page.url`
- `form` actions for mutations — progressive enhancement, works without JS

## SSR Gotchas
- `browser` from `$app/environment` — check before using window/document
- `onMount` only runs client-side — safe for browser APIs
- Stores initialized on server shared between requests — use context for request-specific
- `fetch` in load is special — relative URLs work, credentials handled

## Svelte 5 Runes
- `$state()` replaces `let` for reactivity — `let count = $state(0)`
- `$derived` replaces `$:` for computed — `let doubled = $derived(count * 2)`
- `$effect` for side effects — replaces `$:` with side effects
- Runes are opt-in per file — can mix with Svelte 4 syntax

## Common Mistakes
- Destructuring props loses reactivity — `let { prop } = $props()` in Svelte 5, or don't destructure in 4
- Store value vs store — `$store` for value, `store` for subscribe/set
- Transition on conditional — `{#if show}<div transition:fade>` not on wrapper
- Key block for re-render — `{#key value}...{/key}` destroys and recreates
