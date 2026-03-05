# Next.js Production Engineering

> Complete methodology for building, optimizing, and operating production Next.js applications. From architecture decisions to deployment strategies — everything beyond "hello world."

## Quick Health Check (60 seconds)

Run through these 8 signals — score 0 (no) or 2 (yes):

| Signal | Check | Score |
|--------|-------|-------|
| 🏗️ Architecture | Server/Client Component boundary is intentional, not accidental | /2 |
| ⚡ Performance | Core Web Vitals all green (LCP <2.5s, INP <200ms, CLS <0.1) | /2 |
| 🔒 Security | No secrets in client bundles, CSP headers configured | /2 |
| 📦 Bundle | No unnecessary client JS, tree-shaking working | /2 |
| 🗄️ Data | Caching strategy defined (not just defaults) | /2 |
| 🧪 Testing | E2E + unit tests in CI, >70% coverage on critical paths | /2 |
| 🚀 Deploy | Preview deploys, rollback capability, monitoring | /2 |
| 📊 Observability | Error tracking, performance monitoring, structured logging | /2 |

**Score:** /16 → 14-16 Production-ready | 10-13 Needs work | <10 Risk zone

---

## Phase 1: Architecture Decisions

### App Router vs Pages Router Decision

**Default: App Router** for all new projects (Next.js 13.4+).

Use Pages Router ONLY if:
- Migrating existing Pages Router app (incremental adoption)
- Team has zero RSC experience AND shipping deadline <2 weeks
- Library dependency requires Pages Router patterns

### Project Structure (Recommended)

```
src/
├── app/                    # App Router — routes only
│   ├── (auth)/             # Route group — shared auth layout
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/        # Route group — shared dashboard layout
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── settings/page.tsx
│   ├── api/                # Route Handlers (use sparingly)
│   │   └── webhooks/
│   │       └── stripe/route.ts
│   ├── layout.tsx          # Root layout
│   ├── loading.tsx         # Root loading
│   ├── error.tsx           # Root error boundary
│   ├── not-found.tsx       # 404 page
│   └── global-error.tsx    # Global error boundary
├── components/             # Shared components
│   ├── ui/                 # Design system primitives
│   ├── forms/              # Form components
│   └── layouts/            # Layout components
├── lib/                    # Shared utilities
│   ├── db/                 # Database client & queries
│   ├── auth/               # Auth utilities
│   ├── api/                # External API clients
│   └── utils/              # Pure utility functions
├── hooks/                  # Custom React hooks (client-only)
├── actions/                # Server Actions
├── types/                  # TypeScript types
├── styles/                 # Global styles
└── config/                 # App configuration
```

### Structure Rules

1. **Routes are thin** — `page.tsx` imports components, doesn't contain business logic
2. **Components are reusable** — never import from `app/` into `components/`
3. **Server Actions get their own directory** — organized by domain, not by page
4. **No barrel files** (`index.ts` re-exports) — they break tree-shaking
5. **Colocation for route-specific** — `_components/` in route folders for non-shared components

### Rendering Strategy Decision Matrix

| Scenario | Strategy | Why |
|----------|----------|-----|
| Static content (blog, docs, marketing) | Static (SSG) | Build-time generation, CDN-cached |
| User-specific dashboard | Dynamic Server | Fresh data per request |
| Product listing with prices | ISR (revalidate: 3600) | Fresh enough, fast delivery |
| Real-time data (chat, stocks) | Client-side + WebSocket | Server can't push updates |
| SEO-critical + fresh data | Dynamic Server + streaming | Fast TTFB with Suspense |
| Highly interactive form/wizard | Client Component | Complex state management |

### Server vs Client Component Rules

```
DEFAULT: Server Component (every .tsx is server by default)

Add "use client" ONLY when you need:
✅ useState, useEffect, useRef, useContext
✅ Browser APIs (window, document, localStorage)
✅ Event handlers (onClick, onChange, onSubmit)
✅ Third-party client libraries (framer-motion, react-hook-form)

NEVER add "use client" because:
❌ You want to use async/await (Server Components support this natively)
❌ You're fetching data (fetch in Server Components, not useEffect)
❌ You're importing a server-only library
❌ "It's not working" — debug the actual issue first
```

### The Boundary Pattern

```tsx
// ✅ CORRECT: Server Component wraps Client Component
// app/dashboard/page.tsx (Server Component)
import { getUser } from '@/lib/auth'
import { DashboardClient } from './_components/dashboard-client'

export default async function DashboardPage() {
  const user = await getUser()  // Server-side data fetch
  return <DashboardClient user={user} />  // Pass as props
}

// _components/dashboard-client.tsx
'use client'
export function DashboardClient({ user }: { user: User }) {
  const [tab, setTab] = useState('overview')
  return <div>...</div>
}
```

**Push "use client" as far down the tree as possible.** The boundary should be at the leaf, not the root.

---

## Phase 2: Data Fetching & Caching

### Data Fetching Hierarchy (Prefer Top → Bottom)

1. **Server Component direct fetch** — simplest, most performant
2. **Server Actions** — for mutations and form submissions
3. **Route Handlers** — for webhooks, external API endpoints
4. **Client-side fetch (SWR/React Query)** — for real-time/polling data only

### Fetch Configuration

```tsx
// Static data (cached indefinitely, revalidated on deploy)
const data = await fetch('https://api.example.com/data', {
  cache: 'force-cache'  // Default in App Router
})

// Revalidate every hour
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 }
})

// Always fresh (no cache)
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store'
})

// Tag-based revalidation
const data = await fetch('https://api.example.com/products', {
  next: { tags: ['products'] }
})
// Then in a Server Action:
import { revalidateTag } from 'next/cache'
revalidateTag('products')
```

### Caching Strategy by Data Type

| Data Type | Cache Strategy | Revalidate | Tags |
|-----------|---------------|------------|------|
| CMS content | ISR | 3600s (1h) | `['cms', 'posts']` |
| Product catalog | ISR | 300s (5m) | `['products']` |
| User profile | No cache | — | — |
| Pricing/inventory | No cache | — | — |
| Static assets | Force cache | On deploy | — |
| Analytics/dashboards | ISR | 60s | `['analytics']` |
| Auth tokens | No cache | — | — |

### Database Queries (No fetch API)

```tsx
import { unstable_cache } from 'next/cache'
import { db } from '@/lib/db'

// Cache database queries with tags
const getProducts = unstable_cache(
  async (categoryId: string) => {
    return db.query.products.findMany({
      where: eq(products.categoryId, categoryId)
    })
  },
  ['products'],  // Cache key parts
  {
    revalidate: 300,
    tags: ['products']
  }
)
```

### Parallel Data Fetching

```tsx
// ✅ CORRECT: Parallel fetches
export default async function DashboardPage() {
  const [user, stats, notifications] = await Promise.all([
    getUser(),
    getStats(),
    getNotifications()
  ])
  return <Dashboard user={user} stats={stats} notifications={notifications} />
}

// ❌ WRONG: Sequential waterfall
export default async function DashboardPage() {
  const user = await getUser()
  const stats = await getStats(user.id)  // Waits for user
  const notifications = await getNotifications(user.id)  // Waits for stats
}
```

### Streaming with Suspense

```tsx
import { Suspense } from 'react'

export default async function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      {/* Fast: renders immediately */}
      <UserGreeting />
      
      {/* Slow: streams in when ready */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />  {/* Async Server Component */}
      </Suspense>
      
      <Suspense fallback={<FeedSkeleton />}>
        <ActivityFeed />
      </Suspense>
    </div>
  )
}
```

---

## Phase 3: Server Actions & Mutations

### Server Action Best Practices

```tsx
// actions/user.ts
'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

const updateProfileSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  bio: z.string().max(500).optional()
})

export async function updateProfile(formData: FormData) {
  // 1. Authenticate
  const session = await getSession()
  if (!session) throw new Error('Unauthorized')

  // 2. Validate
  const parsed = updateProfileSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    bio: formData.get('bio')
  })
  
  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors }
  }

  // 3. Authorize
  if (session.userId !== formData.get('userId')) {
    throw new Error('Forbidden')
  }

  // 4. Mutate
  await db.update(users)
    .set(parsed.data)
    .where(eq(users.id, session.userId))

  // 5. Revalidate
  revalidatePath('/profile')
  
  return { success: true }
}
```

### Server Action Rules

1. **Always validate input** — FormData is user input, never trust it
2. **Always check auth** — Server Actions are public endpoints
3. **Always check authorization** — user can only modify their own data
4. **Use Zod for validation** — type-safe, composable schemas
5. **Return errors, don't throw** — throwing shows error boundary, returning shows inline errors
6. **Revalidate after mutations** — `revalidatePath` or `revalidateTag`
7. **Never return sensitive data** — return only what the client needs

### useActionState Pattern (React 19)

```tsx
'use client'
import { useActionState } from 'react'
import { updateProfile } from '@/actions/user'

export function ProfileForm({ user }: { user: User }) {
  const [state, action, pending] = useActionState(updateProfile, null)

  return (
    <form action={action}>
      <input name="name" defaultValue={user.name} />
      {state?.error?.name && <p className="text-red-500">{state.error.name}</p>}
      
      <button type="submit" disabled={pending}>
        {pending ? 'Saving...' : 'Save'}
      </button>
      
      {state?.success && <p className="text-green-500">Saved!</p>}
    </form>
  )
}
```

---

## Phase 4: Authentication & Authorization

### Auth Pattern Selection

| Method | Best For | Libraries |
|--------|----------|-----------|
| Session-based (cookie) | Traditional web apps | NextAuth.js / Auth.js |
| JWT | API-first, mobile clients | jose, custom |
| OAuth only | Social login, quick start | NextAuth.js |
| Passkeys/WebAuthn | Modern, passwordless | SimpleWebAuthn |
| Third-party | Enterprise, compliance | Clerk, Auth0, Supabase Auth |

### Middleware Auth Pattern

```tsx
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const publicRoutes = ['/', '/login', '/register', '/api/webhooks']
const authRoutes = ['/login', '/register']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get('session')?.value

  // Public routes — allow
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    // Redirect authenticated users away from auth pages
    if (token && authRoutes.some(route => pathname.startsWith(route))) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
    return NextResponse.next()
  }

  // Protected routes — require auth
  if (!token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('callbackUrl', pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|public).*)']
}
```

### Authorization Pattern

```tsx
// lib/auth/permissions.ts
type Permission = 'read' | 'write' | 'admin'
type Resource = 'posts' | 'users' | 'settings'

const rolePermissions: Record<string, Record<Resource, Permission[]>> = {
  admin: {
    posts: ['read', 'write', 'admin'],
    users: ['read', 'write', 'admin'],
    settings: ['read', 'write', 'admin']
  },
  editor: {
    posts: ['read', 'write'],
    users: ['read'],
    settings: ['read']
  },
  viewer: {
    posts: ['read'],
    users: [],
    settings: []
  }
}

export function can(role: string, resource: Resource, permission: Permission): boolean {
  return rolePermissions[role]?.[resource]?.includes(permission) ?? false
}

// Usage in Server Component
export default async function AdminPage() {
  const session = await getSession()
  if (!can(session.role, 'settings', 'admin')) {
    notFound()  // Don't reveal admin pages exist
  }
  return <AdminDashboard />
}
```

### Security Headers (next.config.ts)

```tsx
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.example.com;
      frame-ancestors 'none';
    `.replace(/\n/g, '')
  }
]
```

---

## Phase 5: Performance Optimization

### Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | <2.5s | 2.5-4.0s | >4.0s |
| INP | <200ms | 200-500ms | >500ms |
| CLS | <0.1 | 0.1-0.25 | >0.25 |
| TTFB | <800ms | 800ms-1.8s | >1.8s |
| FCP | <1.8s | 1.8-3.0s | >3.0s |

### Image Optimization

```tsx
import Image from 'next/image'

// ✅ Always use next/image
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={630}
  priority  // LCP image — load immediately
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  placeholder="blur"
  blurDataURL={shimmer}  // Base64 placeholder
/>

// For dynamic images
<Image
  src={user.avatar}
  alt={user.name}
  width={48}
  height={48}
  loading="lazy"  // Below fold — lazy load
/>
```

### Image Rules

1. **Always set `priority` on LCP image** (hero, above-fold)
2. **Always provide `sizes`** — prevents downloading oversized images
3. **Use `placeholder="blur"`** for large images — prevents CLS
4. **Configure `remotePatterns`** in next.config.ts for external images
5. **Use WebP/AVIF** — next/image auto-converts by default

### Bundle Optimization

```tsx
// next.config.ts
const nextConfig = {
  // Strict mode for catching bugs
  reactStrictMode: true,
  
  // Optimize packages
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      'date-fns',
      'lodash-es'
    ]
  },
  
  // Bundle analyzer (dev only)
  // npm install @next/bundle-analyzer
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config) => {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
      config.plugins.push(new BundleAnalyzerPlugin({ analyzerMode: 'static' }))
      return config
    }
  })
}
```

### Dynamic Imports for Heavy Components

```tsx
import dynamic from 'next/dynamic'

// Heavy chart library — only load when needed
const Chart = dynamic(() => import('@/components/chart'), {
  loading: () => <ChartSkeleton />,
  ssr: false  // Client-only component
})

// Code editor — definitely client-only
const CodeEditor = dynamic(() => import('@/components/code-editor'), {
  ssr: false
})
```

### Font Optimization

```tsx
// app/layout.tsx
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
})

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono'
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

### Performance Budget

| Resource | Budget | Tool |
|----------|--------|------|
| First Load JS | <100KB | `next build` output |
| Page JS | <50KB per route | Bundle analyzer |
| Total page weight | <500KB | Lighthouse |
| LCP image | <200KB | next/image handles |
| Third-party scripts | <50KB total | Script component |
| Web fonts | <100KB | next/font handles |

---

## Phase 6: Database & ORM

### ORM Selection Guide

| ORM | Best For | Tradeoffs |
|-----|----------|-----------|
| Drizzle | Type-safe, lightweight, SQL-like | Newer ecosystem |
| Prisma | Rapid prototyping, schema-first | Heavier, edge limitations |
| Kysely | Type-safe raw SQL | More manual, no migrations |
| Raw SQL (pg/mysql2) | Max performance, full control | No type safety, manual migrations |

### Drizzle Setup Pattern (Recommended)

```tsx
// lib/db/index.ts
import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'
import * as schema from './schema'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000
})

export const db = drizzle(pool, { schema })

// lib/db/schema.ts
import { pgTable, text, timestamp, uuid, boolean } from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: uuid('id').defaultRandom().primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  role: text('role', { enum: ['admin', 'editor', 'viewer'] }).default('viewer'),
  emailVerified: boolean('email_verified').default(false),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
})
```

### Connection Pooling for Serverless

```tsx
// For Vercel/serverless — use connection pooler
// Neon: use pooler URL (port 5432 → 6543)
// Supabase: use Supavisor URL
// PlanetScale: serverless driver built-in

// lib/db/index.ts (serverless-safe)
import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql)
```

---

## Phase 7: Testing Strategy

### Test Pyramid for Next.js

| Level | Tool | What to Test | Coverage Target |
|-------|------|-------------|-----------------|
| Unit | Vitest | Utils, hooks, pure functions | 80%+ |
| Component | Testing Library + Vitest | UI components, forms | 70%+ |
| Integration | Testing Library | Page-level with mocked data | Key flows |
| E2E | Playwright | Critical user journeys | 5-10 flows |
| Visual | Playwright screenshots | UI regression | Key pages |

### Vitest Configuration

```tsx
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: ['**/*.config.*', '**/types/**']
    }
  }
})
```

### Server Component Testing

```tsx
// Server Components can be tested as async functions
import { render } from '@testing-library/react'
import Page from '@/app/dashboard/page'

// Mock the data fetching
vi.mock('@/lib/db', () => ({
  getUser: vi.fn().mockResolvedValue({ id: '1', name: 'Test' })
}))

test('dashboard page renders user name', async () => {
  const Component = await Page()  // Call as async function
  const { getByText } = render(Component)
  expect(getByText('Test')).toBeInTheDocument()
})
```

### Playwright E2E Pattern

```tsx
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('login flow', async ({ page }) => {
    await page.goto('/login')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByText('Welcome')).toBeVisible()
  })
  
  test('protected route redirects', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })
})
```

---

## Phase 8: Error Handling & Monitoring

### Error Boundary Architecture

```
app/
├── global-error.tsx     # Catches root layout errors (must include <html>)
├── error.tsx            # Catches app-level errors
├── not-found.tsx        # 404 page
├── (dashboard)/
│   ├── error.tsx        # Dashboard-specific errors
│   └── settings/
│       └── error.tsx    # Settings-specific errors
```

### Error Component Pattern

```tsx
// app/error.tsx
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log to error tracking service
    console.error('Application error:', error)
    // Sentry.captureException(error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <h2 className="text-2xl font-bold">Something went wrong</h2>
      <p className="text-gray-500 mt-2">
        {error.digest ? `Error ID: ${error.digest}` : error.message}
      </p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Try again
      </button>
    </div>
  )
}
```

### Structured Logging

```tsx
// lib/logger.ts
type LogLevel = 'debug' | 'info' | 'warn' | 'error'

function log(level: LogLevel, message: string, meta?: Record<string, unknown>) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...meta,
    // Add request context if available
    ...(meta?.requestId && { requestId: meta.requestId })
  }
  
  if (level === 'error') {
    console.error(JSON.stringify(entry))
  } else {
    console.log(JSON.stringify(entry))
  }
}

export const logger = {
  debug: (msg: string, meta?: Record<string, unknown>) => log('debug', msg, meta),
  info: (msg: string, meta?: Record<string, unknown>) => log('info', msg, meta),
  warn: (msg: string, meta?: Record<string, unknown>) => log('warn', msg, meta),
  error: (msg: string, meta?: Record<string, unknown>) => log('error', msg, meta)
}
```

---

## Phase 9: Deployment & Infrastructure

### Platform Comparison

| Platform | Best For | Edge | DB | Cost (hobby) |
|----------|----------|------|-----|---------------|
| Vercel | Default choice, best DX | ✅ | External | Free → $20/mo |
| Cloudflare Pages | Edge-first, Workers | ✅ | D1, KV | Free → $5/mo |
| AWS Amplify | AWS ecosystem | ✅ | RDS, DynamoDB | Pay-per-use |
| Railway | Full-stack, Docker | ❌ | Built-in Postgres | $5/mo |
| Fly.io | Global, Docker | ✅ | Built-in Postgres | Pay-per-use |
| Self-hosted (Docker) | Full control | ❌ | Any | Server cost |

### Docker Production Setup

```dockerfile
# Dockerfile
FROM node:20-alpine AS base
RUN corepack enable

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

```tsx
// next.config.ts — required for standalone
const nextConfig = {
  output: 'standalone'
}
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm tsc --noEmit
      - run: pnpm lint
      - run: pnpm test -- --coverage
      - run: pnpm build
      
  e2e:
    runs-on: ubuntu-latest
    needs: quality
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps
      - run: pnpm build
      - run: pnpm exec playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### Environment Variables

```tsx
// env.ts — runtime validation with t3-env
import { createEnv } from '@t3-oss/env-nextjs'
import { z } from 'zod'

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    AUTH_SECRET: z.string().min(32),
    STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
    REDIS_URL: z.string().url().optional(),
  },
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url(),
    NEXT_PUBLIC_STRIPE_KEY: z.string().startsWith('pk_'),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    AUTH_SECRET: process.env.AUTH_SECRET,
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,
    REDIS_URL: process.env.REDIS_URL,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
    NEXT_PUBLIC_STRIPE_KEY: process.env.NEXT_PUBLIC_STRIPE_KEY,
  },
})
```

---

## Phase 10: Common Patterns Library

### Optimistic Updates

```tsx
'use client'
import { useOptimistic, useTransition } from 'react'
import { toggleTodo } from '@/actions/todos'

export function TodoItem({ todo }: { todo: Todo }) {
  const [optimisticTodo, setOptimisticTodo] = useOptimistic(todo)
  const [, startTransition] = useTransition()

  return (
    <label>
      <input
        type="checkbox"
        checked={optimisticTodo.completed}
        onChange={() => {
          startTransition(async () => {
            setOptimisticTodo({ ...todo, completed: !todo.completed })
            await toggleTodo(todo.id)
          })
        }}
      />
      {optimisticTodo.title}
    </label>
  )
}
```

### Infinite Scroll

```tsx
'use client'
import { useInView } from 'react-intersection-observer'
import { useEffect, useState, useTransition } from 'react'
import { loadMore } from '@/actions/feed'

export function InfiniteList({ initialItems }: { initialItems: Item[] }) {
  const [items, setItems] = useState(initialItems)
  const [cursor, setCursor] = useState(initialItems.at(-1)?.id)
  const [hasMore, setHasMore] = useState(true)
  const [isPending, startTransition] = useTransition()
  const { ref, inView } = useInView()

  useEffect(() => {
    if (inView && hasMore && !isPending) {
      startTransition(async () => {
        const newItems = await loadMore(cursor)
        if (newItems.length === 0) {
          setHasMore(false)
        } else {
          setItems(prev => [...prev, ...newItems])
          setCursor(newItems.at(-1)?.id)
        }
      })
    }
  }, [inView, hasMore, isPending, cursor])

  return (
    <div>
      {items.map(item => <ItemCard key={item.id} item={item} />)}
      {hasMore && <div ref={ref}>{isPending ? <Spinner /> : null}</div>}
    </div>
  )
}
```

### Search with URL State

```tsx
'use client'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useDebouncedCallback } from 'use-debounce'

export function SearchBar() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const handleSearch = useDebouncedCallback((term: string) => {
    const params = new URLSearchParams(searchParams)
    if (term) {
      params.set('q', term)
      params.set('page', '1')
    } else {
      params.delete('q')
    }
    router.replace(`${pathname}?${params.toString()}`)
  }, 300)

  return (
    <input
      type="search"
      placeholder="Search..."
      defaultValue={searchParams.get('q') ?? ''}
      onChange={e => handleSearch(e.target.value)}
    />
  )
}
```

### Multi-step Form with URL State

```tsx
// app/onboarding/page.tsx
export default function OnboardingPage({
  searchParams
}: {
  searchParams: { step?: string }
}) {
  const step = Number(searchParams.step) || 1
  
  return (
    <div>
      <ProgressBar step={step} total={4} />
      {step === 1 && <StepOne />}
      {step === 2 && <StepTwo />}
      {step === 3 && <StepThree />}
      {step === 4 && <StepFour />}
    </div>
  )
}
```

---

## Phase 11: Production Checklist

### Pre-Launch (Mandatory)

- [ ] `next build` succeeds with zero warnings
- [ ] TypeScript strict mode, no `any` types in production code
- [ ] All environment variables validated (t3-env or manual)
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Authentication + authorization tested (pen test critical flows)
- [ ] Error boundaries at every route level
- [ ] 404 and 500 pages customized
- [ ] Favicon, OG images, meta tags configured
- [ ] Core Web Vitals passing (Lighthouse >90)
- [ ] Mobile responsive tested on real devices
- [ ] Accessibility audit (axe, keyboard nav, screen reader)
- [ ] Rate limiting on API routes and Server Actions
- [ ] CORS configured correctly
- [ ] Database connection pooling configured for serverless
- [ ] Monitoring & error tracking connected (Sentry, etc.)

### Pre-Launch (Recommended)

- [ ] E2E tests for critical user journeys
- [ ] Bundle size within budget (<100KB first load)
- [ ] Image optimization verified (next/image, proper sizes)
- [ ] Sitemap.xml and robots.txt configured
- [ ] Analytics configured
- [ ] Preview deployment tested
- [ ] Rollback plan documented
- [ ] Load testing completed
- [ ] CDN caching verified
- [ ] Edge middleware tested in production environment

---

## Phase 12: Anti-Patterns & Troubleshooting

### 10 Next.js Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | `"use client"` at the top of every file | Default to Server Components, push client boundary down |
| 2 | Fetching data with useEffect | Fetch in Server Components or use SWR/React Query for client |
| 3 | Not using `loading.tsx` | Add loading states to prevent layout shift |
| 4 | Ignoring bundle size | Run `next build` and check output, use dynamic imports |
| 5 | No error boundaries | Add `error.tsx` at every route level |
| 6 | Storing secrets in `NEXT_PUBLIC_*` | Server-only env vars for secrets, validate with t3-env |
| 7 | Not setting image `sizes` prop | Always provide `sizes` for responsive images |
| 8 | Sequential data fetching | Use `Promise.all()` for parallel fetches |
| 9 | Caching everything or nothing | Explicit cache strategy per data type |
| 10 | Not using `revalidateTag` | Tag-based revalidation for precise cache control |

### Troubleshooting Decision Tree

```
Build error?
├── "Module not found" → Check import paths, tsconfig paths
├── "Server Component error" → Remove "use client" or move hooks to client component
├── "Hydration mismatch" → Check for browser-only code in shared components
│   → Use suppressHydrationWarning for timestamps
│   → Wrap in useEffect or dynamic(ssr: false)
├── "Edge runtime error" → Check node APIs (fs, crypto) not available at edge
└── Slow build → Check for large static generation, reduce ISR pages

Runtime error?
├── 500 on production → Check error.tsx, logs, Sentry
├── Slow TTFB → Check database queries, add caching
├── CLS → Add explicit dimensions to images/embeds
├── High JS bundle → Run bundle analyzer, dynamic import heavy libs
└── Stale data → Check revalidation settings, revalidateTag
```

---

## Recommended Stack (2025+)

| Layer | Recommendation | Why |
|-------|---------------|-----|
| Framework | Next.js 15+ (App Router) | RSC, streaming, Server Actions |
| Language | TypeScript (strict) | Type safety, better DX |
| Styling | Tailwind CSS 4 | Utility-first, no runtime cost |
| UI Components | shadcn/ui | Copy-paste, customizable |
| Forms | react-hook-form + zod | Type-safe validation |
| ORM | Drizzle | Type-safe, lightweight, SQL-like |
| Database | PostgreSQL (Neon/Supabase) | Serverless-friendly, proven |
| Auth | Auth.js (NextAuth v5) | Built for Next.js |
| Payments | Stripe | Industry standard |
| Hosting | Vercel | Best Next.js DX |
| Testing | Vitest + Playwright | Fast unit + reliable E2E |
| Monitoring | Sentry | Error tracking + performance |
| Analytics | PostHog | Product analytics, open source |

---

## Quality Rubric (0-100)

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| Architecture (RSC boundaries, structure) | 20% | 0-20 |
| Performance (CWV, bundle, TTFB) | 20% | 0-20 |
| Security (auth, headers, validation) | 15% | 0-15 |
| Data layer (caching, fetching, DB) | 15% | 0-15 |
| Testing (pyramid, coverage, E2E) | 10% | 0-10 |
| Error handling (boundaries, logging) | 10% | 0-10 |
| DX (types, linting, CI) | 5% | 0-5 |
| Deployment (Docker/platform, monitoring) | 5% | 0-5 |

**Score:** 90-100 Elite | 75-89 Production-ready | 60-74 Needs improvement | <60 Not production-ready

---

## Natural Language Commands

1. "Set up a new Next.js project" → Phase 1 architecture + structure + Phase 6 DB setup
2. "Add authentication" → Phase 4 auth pattern + middleware + authorization
3. "Optimize performance" → Phase 5 full checklist + image + bundle + fonts
4. "Set up testing" → Phase 7 full pyramid + Vitest + Playwright config
5. "Deploy to production" → Phase 9 platform selection + Docker + CI/CD + env vars
6. "Fix hydration error" → Phase 12 troubleshooting tree
7. "Add caching" → Phase 2 caching strategy table + fetch config + tags
8. "Create a Server Action" → Phase 3 best practices + useActionState pattern
9. "Audit my app" → Quick health check + Phase 11 production checklist
10. "Add error handling" → Phase 8 error boundary architecture + logging
11. "Set up search" → Phase 10 search with URL state pattern
12. "Review my architecture" → Phase 1 decision matrix + rendering strategy

---

*Built by AfrexAI — the AI automation agency that ships. Zero dependencies.*
