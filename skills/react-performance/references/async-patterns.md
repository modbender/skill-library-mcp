# Async Patterns — Eliminating Waterfalls

## Promise.all() for Independent Operations (CRITICAL)

When async operations have no interdependencies, execute them concurrently.

```typescript
// BAD — sequential, 3 round trips
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()

// GOOD — parallel, 1 round trip
const [user, posts, comments] = await Promise.all([
  fetchUser(), fetchPosts(), fetchComments(),
])
```

## Defer Await Until Needed (HIGH)

Move `await` into branches where actually used.

```typescript
// BAD — blocks both branches
async function handleRequest(userId: string, skip: boolean) {
  const userData = await fetchUserData(userId)
  if (skip) return { skipped: true }
  return processUserData(userData)
}

// GOOD — only blocks when needed
async function handleRequest(userId: string, skip: boolean) {
  if (skip) return { skipped: true }
  const userData = await fetchUserData(userId)
  return processUserData(userData)
}
```

Also applies to early-return patterns: check cheapest conditions first before
expensive async operations.

## Strategic Suspense Boundaries (HIGH)

Use Suspense to stream content — show layout immediately while data loads.

```tsx
// BAD — entire page blocked by fetch
async function Page() {
  const data = await fetchData()
  return (
    <div>
      <Sidebar /><Header /><DataDisplay data={data} /><Footer />
    </div>
  )
}

// GOOD — layout renders immediately, data streams in
function Page() {
  return (
    <div>
      <Sidebar />
      <Header />
      <Suspense fallback={<Skeleton />}>
        <DataDisplay />
      </Suspense>
      <Footer />
    </div>
  )
}

async function DataDisplay() {
  const data = await fetchData()
  return <div>{data.content}</div>
}
```

**Share promises across components:**

```tsx
function Page() {
  const dataPromise = fetchData()   // Start, don't await
  return (
    <Suspense fallback={<Skeleton />}>
      <DataDisplay dataPromise={dataPromise} />
      <DataSummary dataPromise={dataPromise} />  {/* Same promise */}
    </Suspense>
  )
}

function DataDisplay({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise)
  return <div>{data.content}</div>
}
```

**When NOT to use Suspense:**
- Critical data needed for layout decisions
- SEO-critical above-the-fold content
- Small/fast queries where overhead isn't worth it
