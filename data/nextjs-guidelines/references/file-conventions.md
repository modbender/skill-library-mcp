# File Conventions

Next.js App Router uses file-based routing with special file conventions.

## Project Structure

```
app/
├── layout.tsx          # Root layout (required)
├── page.tsx            # Home page (/)
├── loading.tsx         # Loading UI (Suspense fallback)
├── error.tsx           # Error UI (must be 'use client')
├── not-found.tsx       # 404 UI
├── global-error.tsx    # Global error UI (for root layout errors)
├── route.ts            # API endpoint
├── template.tsx        # Re-rendered layout (remounts on navigation)
├── default.tsx         # Parallel route fallback
├── opengraph-image.tsx # OG image generation
├── blog/
│   ├── page.tsx        # /blog
│   └── [slug]/
│       └── page.tsx    # /blog/:slug
└── (group)/            # Route group (no URL impact)
    └── page.tsx
```

## Special Files

| File | Purpose |
|------|---------|
| `page.tsx` | UI for a route segment |
| `layout.tsx` | Shared UI for segment and children |
| `loading.tsx` | Loading UI (automatic Suspense boundary) |
| `error.tsx` | Error UI (automatic Error boundary) |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint |
| `template.tsx` | Like layout but re-renders on navigation |
| `default.tsx` | Fallback for parallel routes |

## Route Segments

```
app/
├── blog/               # Static segment: /blog
├── [slug]/             # Dynamic segment: /:slug
├── [...slug]/          # Catch-all: /a/b/c
├── [[...slug]]/        # Optional catch-all: / or /a/b/c
├── (marketing)/        # Route group (ignored in URL)
└── _components/        # Private folder (excluded from routing)
```

## Parallel Routes

Enable multiple independent sections with separate loading states:

```
app/
├── @analytics/
│   ├── page.tsx
│   └── default.tsx     # Required fallback
├── @sidebar/
│   ├── page.tsx
│   └── default.tsx     # Required fallback
└── layout.tsx          # Receives { analytics, sidebar } as props
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  analytics,
  sidebar,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  sidebar: React.ReactNode
}) {
  return (
    <div className="flex">
      <aside>{sidebar}</aside>
      <main>{children}</main>
      <aside>{analytics}</aside>
    </div>
  )
}
```

## Intercepting Routes

Enable modal overlays on soft navigation:

```
app/
├── feed/
│   └── page.tsx
├── @modal/
│   ├── (.)photo/[id]/  # Intercepts /photo/[id] from /feed
│   │   └── page.tsx
│   └── default.tsx
└── photo/[id]/
    └── page.tsx        # Full page (direct navigation/refresh)
```

Conventions:
- `(.)` - same level
- `(..)` - one level up
- `(..)(..)` - two levels up
- `(...)` - from root

## Middleware / Proxy

### Next.js 14-15: `middleware.ts`

```tsx
// middleware.ts (root of project)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Auth, redirects, rewrites, i18n, etc.
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}
```

### Next.js 16+: `proxy.ts`

Renamed for clarity — same capabilities, different names:

```tsx
// proxy.ts (root of project)
export function proxy(request: NextRequest) {
  return NextResponse.next()
}

export const proxyConfig = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}
```

| Version | File | Export | Config |
|---------|------|--------|--------|
| v14-15 | `middleware.ts` | `middleware()` | `config` |
| v16+ | `proxy.ts` | `proxy()` | `proxyConfig` |

**Migration**: Run `npx @next/codemod@latest upgrade` to auto-rename.
