# Data Fetching — NextJS

## Server Components (Recommended)

```typescript
// Direct fetch in Server Component
async function Page() {
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()
  return <div>{json.title}</div>
}

// With database
async function Page() {
  const posts = await db.post.findMany()
  return <PostList posts={posts} />
}
```

## Parallel Data Fetching

```typescript
// ✅ Good - parallel fetches
async function Dashboard() {
  // Start both fetches simultaneously
  const [user, posts, comments] = await Promise.all([
    getUser(),
    getPosts(),
    getComments(),
  ])
  
  return (
    <>
      <UserCard user={user} />
      <PostList posts={posts} />
      <CommentList comments={comments} />
    </>
  )
}

// ❌ Bad - sequential waterfall
async function Dashboard() {
  const user = await getUser()      // waits
  const posts = await getPosts()    // then waits
  const comments = await getComments() // then waits
  // Total time = sum of all fetches
}
```

## Streaming with Suspense

```typescript
import { Suspense } from 'react'

export default function Page() {
  return (
    <main>
      {/* Shows immediately */}
      <h1>Dashboard</h1>
      
      {/* Streams when ready */}
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile />
      </Suspense>
      
      {/* Independent stream */}
      <Suspense fallback={<PostsSkeleton />}>
        <RecentPosts />
      </Suspense>
    </main>
  )
}

// Each component fetches its own data
async function UserProfile() {
  const user = await getUser() // 200ms
  return <div>{user.name}</div>
}

async function RecentPosts() {
  const posts = await getPosts() // 500ms
  return <PostList posts={posts} />
}
// User shows at 200ms, Posts at 500ms
```

## Loading UI

```typescript
// app/dashboard/loading.tsx
// Automatically wraps page in Suspense

export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded" />
      <div className="mt-4 space-y-3">
        <div className="h-4 bg-gray-200 rounded" />
        <div className="h-4 bg-gray-200 rounded" />
      </div>
    </div>
  )
}
```

## Error Handling

```typescript
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

## Fetch Options

```typescript
// Cached (default in Next.js 14, opt-in in 15)
fetch(url, { cache: 'force-cache' })

// No cache
fetch(url, { cache: 'no-store' })

// Time-based revalidation (ISR)
fetch(url, { next: { revalidate: 60 } }) // seconds

// Tag-based revalidation
fetch(url, { next: { tags: ['posts'] } })

// Revalidate by tag (Server Action)
import { revalidateTag } from 'next/cache'
revalidateTag('posts')
```

## Request Deduplication

```typescript
// Same fetch in multiple components = 1 request
async function Layout({ children }) {
  const user = await getUser() // Request 1
  return <>{children}</>
}

async function Page() {
  const user = await getUser() // Deduped, uses Request 1
  return <div>{user.name}</div>
}

// Works for fetch() with same URL and options
// Also works with React cache()
import { cache } from 'react'

export const getUser = cache(async () => {
  const res = await fetch('/api/user')
  return res.json()
})
```

## Client-Side Fetching (When Needed)

```typescript
'use client'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function UserPosts() {
  const { data, error, isLoading } = useSWR('/api/posts', fetcher)
  
  if (isLoading) return <Skeleton />
  if (error) return <Error />
  return <PostList posts={data} />
}

// With React Query
'use client'
import { useQuery } from '@tanstack/react-query'

export function UserPosts() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['posts'],
    queryFn: () => fetch('/api/posts').then(r => r.json()),
  })
  
  if (isLoading) return <Skeleton />
  if (error) return <Error />
  return <PostList posts={data} />
}
```

## Preloading Data

```typescript
import { preload } from 'react-dom'

// Preload in parent, use in child
export default function Page() {
  preload('/api/user', { as: 'fetch' })
  return <UserProfile />
}

// With custom function
import { unstable_preload as preload } from 'next/cache'

export const preloadUser = (id: string) => {
  void getUser(id)
}

// Parent preloads
export default function Layout({ children }) {
  preloadUser('123')
  return <>{children}</>
}
```

## Search Params

```typescript
// Server Component - use searchParams prop
export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; page?: string }>
}) {
  const { q, page } = await searchParams
  const results = await search(q, parseInt(page || '1'))
  return <Results data={results} />
}

// Client Component - use useSearchParams
'use client'
import { useSearchParams, useRouter } from 'next/navigation'

export function SearchInput() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const q = searchParams.get('q') || ''
  
  function handleSearch(term: string) {
    const params = new URLSearchParams(searchParams)
    if (term) {
      params.set('q', term)
    } else {
      params.delete('q')
    }
    router.push(`?${params.toString()}`)
  }
  
  return <input defaultValue={q} onChange={e => handleSearch(e.target.value)} />
}
```

## Patterns

### Fetch on Server, Hydrate on Client
```typescript
// Fetch on server
async function Page() {
  const initialData = await getPosts()
  return <PostsClient initialData={initialData} />
}

// Hydrate on client for real-time updates
'use client'
function PostsClient({ initialData }) {
  const { data } = useSWR('/api/posts', fetcher, {
    fallbackData: initialData,
  })
  return <PostList posts={data} />
}
```

### Infinite Scroll
```typescript
'use client'
import useSWRInfinite from 'swr/infinite'

const getKey = (pageIndex: number, previousPageData: any) => {
  if (previousPageData && !previousPageData.length) return null
  return `/api/posts?page=${pageIndex + 1}`
}

export function InfiniteList() {
  const { data, size, setSize, isLoading } = useSWRInfinite(getKey, fetcher)
  
  const posts = data ? data.flat() : []
  const isLoadingMore = isLoading || (size > 0 && data && typeof data[size - 1] === 'undefined')
  const isEmpty = data?.[0]?.length === 0
  const isReachingEnd = isEmpty || (data && data[data.length - 1]?.length < 10)
  
  return (
    <>
      {posts.map(post => <Post key={post.id} post={post} />)}
      <button
        disabled={isLoadingMore || isReachingEnd}
        onClick={() => setSize(size + 1)}
      >
        {isLoadingMore ? 'Loading...' : isReachingEnd ? 'No more' : 'Load more'}
      </button>
    </>
  )
}
```
