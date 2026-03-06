# Caching — NextJS

## Cache Types

| Cache | Location | Purpose | Duration |
|-------|----------|---------|----------|
| Request Memoization | Server | Dedupe same fetch in render | Per request |
| Data Cache | Server | Persist fetch results | Indefinite (revalidate) |
| Full Route Cache | Server | Pre-rendered HTML/RSC | Build time |
| Router Cache | Client | RSC payloads | Session/time-based |

## Fetch Caching (Next.js 15)

```typescript
// No cache (default in Next.js 15)
const data = await fetch(url)

// Opt-in to cache
const data = await fetch(url, { cache: 'force-cache' })

// Time-based revalidation
const data = await fetch(url, { next: { revalidate: 60 } })

// Tagged for on-demand revalidation
const data = await fetch(url, { next: { tags: ['posts'] } })
```

## On-Demand Revalidation

```typescript
// In Server Action or Route Handler
import { revalidatePath, revalidateTag } from 'next/cache'

// Revalidate by path
export async function updatePost(id: string, data: any) {
  await db.post.update({ where: { id }, data })
  
  revalidatePath('/blog')           // Specific page
  revalidatePath('/blog/[slug]', 'page')  // Dynamic route
  revalidatePath('/blog', 'layout') // Layout and all pages
  revalidatePath('/', 'layout')     // Entire site
}

// Revalidate by tag
export async function createPost(data: any) {
  await db.post.create({ data })
  revalidateTag('posts')
}

// Route handler for webhook
export async function POST(request: Request) {
  const secret = request.headers.get('x-revalidate-secret')
  if (secret !== process.env.REVALIDATE_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 })
  }
  
  revalidateTag('posts')
  return Response.json({ revalidated: true })
}
```

## unstable_cache

```typescript
import { unstable_cache } from 'next/cache'

// Cache database queries
const getCachedUser = unstable_cache(
  async (id: string) => {
    return db.user.findUnique({ where: { id } })
  },
  ['user'],
  {
    tags: ['users'],
    revalidate: 60,
  }
)

// Usage
const user = await getCachedUser('123')

// Revalidate
revalidateTag('users')
```

## Route Segment Config

```typescript
// Force dynamic rendering (no cache)
export const dynamic = 'force-dynamic'

// Force static rendering
export const dynamic = 'force-static'

// Set revalidation time
export const revalidate = 60 // seconds

// Fetch cache behavior
export const fetchCache = 'force-cache'      // Cache all fetches
export const fetchCache = 'force-no-store'   // No cache

// Combined example
export const dynamic = 'force-dynamic'
export const revalidate = 0
```

## Router Cache (Client)

```typescript
// Automatic - Link prefetching
<Link href="/about">About</Link>

// Disable prefetch
<Link href="/about" prefetch={false}>About</Link>

// Manual invalidation
import { useRouter } from 'next/navigation'

function Component() {
  const router = useRouter()
  
  // Force refresh from server
  router.refresh()
}
```

## ISR (Incremental Static Regeneration)

```typescript
// Page-level revalidation
export const revalidate = 60 // seconds

// Or fetch-level
async function Page() {
  const data = await fetch(url, {
    next: { revalidate: 60 }
  })
}

// Shortest revalidate wins for the page
// fetch with 30s + fetch with 60s = page revalidates at 30s
```

## Static Generation with Dynamic Params

```typescript
// Generate static pages at build time
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map(post => ({ slug: post.slug }))
}

// Control behavior for unlisted params
export const dynamicParams = true   // Generate on-demand (default)
export const dynamicParams = false  // Return 404

// Force static even with dynamic data
export const dynamic = 'force-static'
```

## Cache Debugging

```typescript
// Log cache status
async function Page() {
  const res = await fetch(url)
  console.log('Cache:', res.headers.get('x-vercel-cache')) // On Vercel
  console.log('Age:', res.headers.get('age'))
}

// Development: caching is disabled by default
// Use `next build && next start` to test production caching

// Headers to check
// x-nextjs-cache: HIT | MISS | STALE
// x-vercel-cache: HIT | MISS | STALE | PRERENDER
```

## Common Patterns

### Cache with Dynamic User Data
```typescript
// Static page shell + dynamic user data
async function Page() {
  return (
    <>
      <StaticContent />
      <Suspense fallback={<Skeleton />}>
        <DynamicUserData />
      </Suspense>
    </>
  )
}

async function DynamicUserData() {
  const session = await auth()
  // Dynamic - not cached
  const userData = await getUserData(session.user.id)
  return <UserWidget data={userData} />
}
```

### Cache Everything Except Auth
```typescript
// Cache the page
export const revalidate = 3600 // 1 hour

async function Page() {
  const posts = await getCachedPosts() // Cached
  
  return (
    <>
      <PostList posts={posts} />
      {/* Auth-aware component - client-side */}
      <AuthActions />
    </>
  )
}

'use client'
function AuthActions() {
  const { data: session } = useSession()
  if (!session) return <LoginButton />
  return <CreatePostButton />
}
```

### Stale-While-Revalidate
```typescript
// Show stale content immediately, revalidate in background
export const revalidate = 60

async function Page() {
  // First request: generate and cache
  // Within 60s: serve from cache
  // After 60s: serve stale, regenerate in background
  const data = await fetch(url, {
    next: { revalidate: 60 }
  })
}
```
