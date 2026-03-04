# Routing — NextJS

## File-Based Routing

```
app/
├── page.tsx                    # /
├── about/
│   └── page.tsx               # /about
├── blog/
│   ├── page.tsx               # /blog
│   └── [slug]/
│       └── page.tsx           # /blog/hello-world
└── [...catchAll]/
    └── page.tsx               # /anything/else/here
```

## Special Files

| File | Purpose |
|------|---------|
| `page.tsx` | Unique UI for route, makes route accessible |
| `layout.tsx` | Shared UI, wraps pages and nested layouts |
| `loading.tsx` | Loading UI (Suspense boundary) |
| `error.tsx` | Error UI (Error boundary) |
| `not-found.tsx` | 404 UI for route |
| `template.tsx` | Like layout but re-mounts on navigation |
| `default.tsx` | Fallback for parallel routes |
| `route.tsx` | API endpoint |

## Dynamic Routes

```typescript
// app/blog/[slug]/page.tsx
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  return <h1>Post: {slug}</h1>
}

// Generate static params
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}

// Control dynamic behavior
export const dynamicParams = true  // Allow unlisted params (default)
export const dynamicParams = false // 404 for unlisted params
```

## Catch-All Routes

```typescript
// app/shop/[...categories]/page.tsx
// Matches: /shop/clothes, /shop/clothes/tops, /shop/clothes/tops/shirts

export default async function Page({
  params,
}: {
  params: Promise<{ categories: string[] }>
}) {
  const { categories } = await params
  // categories = ['clothes', 'tops', 'shirts']
  return <h1>{categories.join(' > ')}</h1>
}

// Optional catch-all: [[...categories]]
// Also matches: /shop (categories = undefined)
```

## Route Groups

```
app/
├── (marketing)/          # Group - no URL impact
│   ├── page.tsx         # /
│   ├── about/page.tsx   # /about
│   └── layout.tsx       # Marketing layout
├── (shop)/
│   ├── products/page.tsx # /products
│   └── layout.tsx       # Shop layout
└── layout.tsx           # Root layout
```

## Parallel Routes

```
app/
├── @analytics/
│   ├── page.tsx
│   └── default.tsx      # Fallback when no match
├── @team/
│   ├── page.tsx
│   └── default.tsx
├── layout.tsx           # Receives slots as props
└── page.tsx
```

```typescript
// app/layout.tsx
export default function Layout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <>
      {children}
      <aside>
        {analytics}
        {team}
      </aside>
    </>
  )
}
```

## Intercepting Routes

| Convention | Matches |
|------------|---------|
| `(.)folder` | Same level |
| `(..)folder` | One level up |
| `(..)(..)folder` | Two levels up |
| `(...)folder` | From root |

```
app/
├── feed/
│   └── page.tsx
├── photo/[id]/
│   └── page.tsx          # Full page /photo/123
└── @modal/
    └── (.)photo/[id]/
        └── page.tsx      # Intercepts as modal
```

## Navigation

```typescript
// Link component - client-side navigation
import Link from 'next/link'

<Link href="/about">About</Link>
<Link href={`/blog/${post.slug}`}>Read More</Link>
<Link href="/dashboard" prefetch={false}>Dashboard</Link>

// useRouter - programmatic navigation (Client Component)
'use client'
import { useRouter } from 'next/navigation'

function Component() {
  const router = useRouter()
  
  router.push('/dashboard')        // Navigate
  router.replace('/login')         // Replace history
  router.refresh()                 // Refresh server components
  router.prefetch('/about')        // Prefetch route
  router.back()                    // Go back
  router.forward()                 // Go forward
}

// redirect - Server Component/Action
import { redirect } from 'next/navigation'

export default async function Page() {
  const session = await getSession()
  if (!session) redirect('/login')
  return <Dashboard />
}

// permanentRedirect - 308 redirect
import { permanentRedirect } from 'next/navigation'
permanentRedirect('/new-url')
```

## Route Configuration

```typescript
// Per-route configuration
export const dynamic = 'auto' // default
export const dynamic = 'force-dynamic' // always dynamic
export const dynamic = 'force-static' // always static
export const dynamic = 'error' // error if dynamic

export const revalidate = false // no revalidation (default for static)
export const revalidate = 0 // always revalidate
export const revalidate = 60 // revalidate every 60 seconds

export const fetchCache = 'auto' // default
export const fetchCache = 'default-cache' // cache unless opt-out
export const fetchCache = 'default-no-store' // no cache unless opt-in
export const fetchCache = 'force-cache' // cache all
export const fetchCache = 'force-no-store' // no cache
export const fetchCache = 'only-cache' // error on no-cache
export const fetchCache = 'only-no-store' // error on cache

export const runtime = 'nodejs' // default
export const runtime = 'edge' // edge runtime

export const preferredRegion = 'auto' // default
export const preferredRegion = 'iad1' // specific region
export const preferredRegion = ['iad1', 'sfo1'] // multiple regions

export const maxDuration = 5 // max execution time in seconds
```

## Active Link

```typescript
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function NavLinks() {
  const pathname = usePathname()
  
  const links = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/blog', label: 'Blog' },
  ]
  
  return (
    <nav>
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={pathname === link.href ? 'active' : ''}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  )
}
```
