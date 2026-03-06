# Server Component Performance

## Minimize Serialization at RSC Boundaries (HIGH)

The server/client boundary serializes all props. Only pass fields the client uses.

```tsx
// BAD — serializes all 50 fields
async function Page() {
  const user = await fetchUser()
  return <Profile user={user} />
}

'use client'
function Profile({ user }: { user: User }) {
  return <div>{user.name}</div>     // Uses 1 field
}

// GOOD — serializes only 1 field
async function Page() {
  const user = await fetchUser()
  return <Profile name={user.name} />
}
```

## Parallel Data Fetching with Composition (CRITICAL)

RSC execute sequentially within a tree. Restructure to parallelize.

```tsx
// BAD — Sidebar waits for Page's fetch
export default async function Page() {
  const header = await fetchHeader()
  return <div><div>{header}</div><Sidebar /></div>
}

// GOOD — both fetch simultaneously as sibling async components
async function Header() {
  const data = await fetchHeader()
  return <div>{data}</div>
}
async function Sidebar() {
  const items = await fetchSidebarItems()
  return <nav>{items.map(renderItem)}</nav>
}
export default function Page() {
  return <div><Header /><Sidebar /></div>
}
```

## Per-Request Deduplication with React.cache() (MEDIUM)

Deduplicate server-side operations within a single request.

```typescript
import { cache } from 'react'

export const getCurrentUser = cache(async () => {
  const session = await auth()
  if (!session?.user?.id) return null
  return await db.user.findUnique({ where: { id: session.user.id } })
})
```

**Avoid inline objects as arguments** — `React.cache()` uses `Object.is`:

```typescript
// BAD — always cache miss (new object each call)
const getUser = cache(async (params: { uid: number }) => { ... })
getUser({ uid: 1 })
getUser({ uid: 1 })    // Miss — different reference

// GOOD — cache hit (primitive value)
const getUser = cache(async (uid: number) => { ... })
getUser(1)
getUser(1)              // Hit — same value
```

Next.js auto-deduplicates `fetch` calls, but `React.cache()` is needed for
database queries, auth checks, heavy computations, and file system operations.

## Non-Blocking Operations with after() (MEDIUM)

Use Next.js `after()` for work that should run after the response.

```tsx
import { after } from 'next/server'

export async function POST(request: Request) {
  await updateDatabase(request)

  after(async () => {
    const userAgent = (await headers()).get('user-agent') || 'unknown'
    logUserAction({ userAgent })
  })

  return Response.json({ status: 'success' })
}
```

Use for analytics, audit logging, notifications, cache invalidation, cleanup.

## Avoid Duplicate Serialization in RSC Props (LOW)

RSC serialization deduplicates by reference, not value. Transformations create
new references that duplicate data.

```tsx
// BAD — duplicates the array
<ClientList usernames={usernames} usernamesOrdered={usernames.toSorted()} />

// GOOD — send once, transform in client
<ClientList usernames={usernames} />

// Client-side:
const sorted = useMemo(() => [...usernames].sort(), [usernames])
```

Operations that break deduplication: `.toSorted()`, `.filter()`, `.map()`,
`.slice()`, `[...arr]`, `{...obj}`, `structuredClone()`.
