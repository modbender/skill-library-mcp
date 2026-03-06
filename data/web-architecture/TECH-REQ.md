# HustleStack - Technical Requirements

> Comprehensive technical specification for the HustleStack career development platform.

---

## 1. Stack Overview

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | Next.js | 16+ | Full-stack React framework with App Router |
| **Runtime** | React | 19+ | UI library with concurrent features |
| **Compiler** | React Compiler | experimental | Automatic memoization and optimization |
| **Database** | Convex | latest | Real-time reactive database |
| **Authentication** | Clerk | latest | Auth with billing/subscriptions |
| **Payments** | Stripe | latest | Payment processing |
| **Email** | Resend | latest | Transactional email |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **UI Components** | shadcn/ui | latest | Accessible component primitives |
| **Icons** | react-icons (Phosphor) | latest | Lightweight icon library |
| **Analytics** | PostHog | latest | Product analytics |
| **Error Tracking** | Sentry | latest | Error monitoring |
| **Hosting** | Vercel | - | Edge deployment |
| **Package Manager** | Bun | 1.3+ | Fast JS runtime & package manager |

---

## 2. Technology Configuration

### 2.1 Next.js 16+

**Purpose**: Full-stack React framework with App Router, Server Components, and edge runtime support.

**Configuration** (`next.config.ts`):
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
    ppr: true, // Partial Pre-rendering
  },
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'img.clerk.com' },
      { protocol: 'https', hostname: '*.convex.cloud' },
    ],
  },
  // Turbopack for development
  turbopack: {},
};

export default nextConfig;
```

**Requirements**:
- App Router architecture (no Pages Router)
- Server Components by default
- Client Components only when necessary (`'use client'`)
- Route Groups for layout organization
- Parallel and Intercepting routes for modals
- Metadata API for SEO

---

### 2.2 React 19+

**Purpose**: UI library with concurrent rendering, Server Components, and improved hooks.

**Key Features to Use**:
- Server Components (default)
- `use` hook for promises and context
- `useOptimistic` for optimistic updates
- `useFormStatus` for form states
- `useActionState` for server actions
- Actions with `useTransition`

**Requirements**:
- Strict Mode enabled
- No legacy lifecycle methods
- Functional components only

---

### 2.3 React Compiler (Experimental)

**Purpose**: Automatic memoization eliminating need for manual `useMemo`, `useCallback`, `React.memo`.

**Configuration** (`babel.config.js` or via Next.js):
```javascript
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      target: '19',
    }],
  ],
};
```

**Requirements**:
- Remove existing manual memoization
- Follow React Compiler rules (no rule-breaking patterns)
- Enable eslint-plugin-react-compiler

---

### 2.4 Tailwind CSS v4

**Purpose**: Utility-first CSS framework with native CSS variables and improved performance.

**Configuration** (`app/globals.css`):
```css
@import "tailwindcss";
@import "tw-animate-css";

@theme {
  /* HustleStack Brand Colors */
  --color-primary: oklch(0.65 0.19 250);
  --color-primary-foreground: oklch(0.98 0.01 250);
  --color-secondary: oklch(0.55 0.15 160);
  --color-accent: oklch(0.75 0.18 45);
  
  /* Semantic Colors */
  --color-background: oklch(0.99 0.005 250);
  --color-foreground: oklch(0.15 0.01 250);
  --color-muted: oklch(0.95 0.01 250);
  --color-muted-foreground: oklch(0.45 0.02 250);
  
  /* Status Colors */
  --color-success: oklch(0.65 0.18 145);
  --color-warning: oklch(0.75 0.16 65);
  --color-error: oklch(0.60 0.20 25);
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  /* Fonts */
  --font-sans: 'Inter Variable', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono Variable', monospace;
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground antialiased;
  }
}
```

**Requirements**:
- Use CSS-first configuration (no tailwind.config.js)
- OKLCH color space for all colors
- CSS variables for theming
- Dark mode via `@media (prefers-color-scheme: dark)` or class strategy

---

### 2.5 Clerk (Authentication + Billing)

**Purpose**: Complete authentication solution with built-in billing/subscriptions support.

**Configuration**:
```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
  '/pricing',
  '/about',
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

**Billing Setup**:
```typescript
// Clerk Billing with Stripe
import { auth } from '@clerk/nextjs/server';

export async function getSubscriptionStatus() {
  const { userId, orgId } = await auth();
  // Use Clerk's billing features
}
```

**Requirements**:
- Clerk Core 2 SDK
- Billing add-on enabled
- Multi-tenant support for teams
- OAuth providers: Google, LinkedIn, GitHub
- Webhook handling for subscription events

---

### 2.6 Convex (Real-time Database)

**Purpose**: Reactive database with real-time sync, TypeScript-first schema, and serverless functions.

**Schema** (`convex/schema.ts`):
```typescript
import { defineSchema, defineTable } from 'convex/server';
import { v } from 'convex/values';

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.string(),
    imageUrl: v.optional(v.string()),
    tier: v.union(v.literal('free'), v.literal('pro'), v.literal('premium')),
    stripeCustomerId: v.optional(v.string()),
    createdAt: v.number(),
  })
    .index('by_clerk_id', ['clerkId'])
    .index('by_email', ['email']),
  
  profiles: defineTable({
    userId: v.id('users'),
    headline: v.optional(v.string()),
    bio: v.optional(v.string()),
    skills: v.array(v.string()),
    experience: v.array(v.object({
      title: v.string(),
      company: v.string(),
      startDate: v.string(),
      endDate: v.optional(v.string()),
      current: v.boolean(),
    })),
    goals: v.array(v.string()),
    valueScore: v.optional(v.number()),
  }).index('by_user', ['userId']),
  
  roadmaps: defineTable({
    userId: v.id('users'),
    title: v.string(),
    milestones: v.array(v.object({
      id: v.string(),
      title: v.string(),
      completed: v.boolean(),
      dueDate: v.optional(v.string()),
    })),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index('by_user', ['userId']),
});
```

**Client Setup**:
```typescript
// convex/convex.ts
'use client';

import { ConvexProvider, ConvexReactClient } from 'convex/react';
import { ConvexProviderWithClerk } from 'convex/react-clerk';
import { ClerkProvider, useAuth } from '@clerk/nextjs';

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}
```

**Requirements**:
- TypeScript-first schema definitions
- Optimistic updates for UX
- Real-time subscriptions for live data
- Server-side queries for initial page loads
- Proper indexing for all query patterns

---

### 2.7 Stripe (Payments)

**Purpose**: Payment processing for subscriptions and one-time purchases.

**Integration with Clerk**:
Clerk Billing handles the primary Stripe integration. Direct Stripe SDK used for:
- Webhook handling
- Custom checkout flows
- Refund processing
- Invoice management

**Webhook Handler**:
```typescript
// app/api/webhooks/stripe/route.ts
import { headers } from 'next/headers';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const body = await req.text();
  const sig = (await headers()).get('stripe-signature')!;
  
  const event = stripe.webhooks.constructEvent(
    body,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET!
  );
  
  switch (event.type) {
    case 'customer.subscription.updated':
    case 'customer.subscription.deleted':
      // Sync with Convex
      break;
    case 'invoice.payment_failed':
      // Handle failed payment
      break;
  }
  
  return Response.json({ received: true });
}
```

**Requirements**:
- Stripe SDK v14+
- Webhook signature verification
- Idempotent event handling
- Subscription lifecycle management
- PCI DSS compliance (Stripe handles card data)

---

### 2.8 Resend (Email)

**Purpose**: Transactional email for notifications, onboarding, and marketing.

**Configuration**:
```typescript
// lib/email.ts
import { Resend } from 'resend';

export const resend = new Resend(process.env.RESEND_API_KEY);

// Email templates as React components
import { WelcomeEmail } from '@/emails/welcome';

export async function sendWelcomeEmail(email: string, name: string) {
  await resend.emails.send({
    from: 'HustleStack <hello@hustlestack>',
    to: email,
    subject: 'Welcome to HustleStack - Your potential is hustlestackped!',
    react: WelcomeEmail({ name }),
  });
}
```

**Email Types**:
- Welcome / Onboarding sequence
- Value assessment results
- Roadmap reminders
- Milestone achievements
- Mentor session confirmations
- Weekly progress digests
- Subscription updates

**Requirements**:
- React Email for templates
- Domain verification (hustlestack)
- Unsubscribe handling
- Email preferences in user settings
- Bounce/complaint handling

---

### 2.9 Icons (react-icons + Phosphor Light)

**Purpose**: Lightweight, consistent iconography.

**Usage**:
```typescript
// ALWAYS use Light weight only
import { PiRocketLight, PiUserLight, PiChartLineUpLight } from 'react-icons/pi';

// Never use other weights
// ❌ PiRocket, PiRocketBold, PiRocketFill, PiRocketDuotone
// ✅ PiRocketLight
```

**Icon Categories**:
- Navigation: `PiHouseLight`, `PiUserLight`, `PiGearLight`
- Actions: `PiPlusLight`, `PiPencilLight`, `PiTrashLight`
- Career: `PiBriefcaseLight`, `PiGraduationCapLight`, `PiTrophyLight`
- Status: `PiCheckCircleLight`, `PiWarningLight`, `PiInfoLight`

**Requirements**:
- ONLY Phosphor Light weight (`PiXxxLight`)
- Tree-shaking enabled (import specific icons)
- Consistent sizing via className

---

### 2.10 shadcn/ui Components

**Purpose**: Accessible, customizable component primitives built on Radix UI.

**Installation**:
```bash
bunx shadcn@latest init
bunx shadcn@latest add button card dialog form input
```

**Required Components**:
- `Button` - Primary actions
- `Card` - Content containers
- `Dialog` - Modals
- `Form` - React Hook Form integration
- `Input` - Text inputs
- `Select` - Dropdowns
- `Tabs` - Tab navigation
- `Toast` - Notifications
- `Avatar` - User images
- `Badge` - Status indicators
- `Progress` - Progress bars
- `Skeleton` - Loading states
- `Sheet` - Side panels
- `Command` - Command palette

**Requirements**:
- Tailwind CSS v4 compatible
- ARIA compliant
- Keyboard navigation
- Focus management

---

### 2.11 PostHog (Analytics)

**Purpose**: Product analytics, feature flags, session replay.

**Configuration**:
```typescript
// app/providers.tsx
'use client';

import posthog from 'posthog-js';
import { PostHogProvider } from 'posthog-js/react';

if (typeof window !== 'undefined') {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
    person_profiles: 'identified_only',
    capture_pageview: false, // Manual with App Router
  });
}

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}
```

**Event Tracking**:
```typescript
import { usePostHog } from 'posthog-js/react';

function ValueAssessment() {
  const posthog = usePostHog();
  
  const handleComplete = (score: number) => {
    posthog.capture('value_assessment_completed', {
      score,
      tier: user.tier,
    });
  };
}
```

**Requirements**:
- EU hosting for GDPR compliance
- Session replay enabled
- Feature flags for A/B testing
- User identification via Clerk ID
- Custom events for key actions

---

### 2.12 Sentry (Error Tracking)

**Purpose**: Error monitoring, performance tracking, and alerting.

**Configuration**:
```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
});
```

**Requirements**:
- Source maps uploaded on build
- User context from Clerk
- Performance monitoring enabled
- Release tracking
- Alert rules for critical errors

---

## 3. Environment Variables

### Required Variables

```bash
# .env.local

# ─────────────────────────────────────────────────────────────
# Core Application
# ─────────────────────────────────────────────────────────────
NEXT_PUBLIC_APP_URL=http://localhost:3000

# ─────────────────────────────────────────────────────────────
# Convex
# ─────────────────────────────────────────────────────────────
CONVEX_DEPLOYMENT=dev:hustlestack-us
NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud

# ─────────────────────────────────────────────────────────────
# Clerk Authentication
# ─────────────────────────────────────────────────────────────
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
CLERK_WEBHOOK_SECRET=whsec_xxx

# Sign-in/up redirect URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# ─────────────────────────────────────────────────────────────
# Stripe
# ─────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# Price IDs
STRIPE_PRO_MONTHLY_PRICE_ID=price_xxx
STRIPE_PRO_YEARLY_PRICE_ID=price_xxx
STRIPE_PREMIUM_MONTHLY_PRICE_ID=price_xxx
STRIPE_PREMIUM_YEARLY_PRICE_ID=price_xxx

# ─────────────────────────────────────────────────────────────
# Resend
# ─────────────────────────────────────────────────────────────
RESEND_API_KEY=re_xxx

# ─────────────────────────────────────────────────────────────
# PostHog
# ─────────────────────────────────────────────────────────────
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://eu.posthog.com

# ─────────────────────────────────────────────────────────────
# Sentry
# ─────────────────────────────────────────────────────────────
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_AUTH_TOKEN=sntrys_xxx
SENTRY_ORG=hustlestack
SENTRY_PROJECT=hustlestack-us
```

### Environment Variable Validation

```typescript
// lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  // Convex
  NEXT_PUBLIC_CONVEX_URL: z.string().url(),
  
  // Clerk
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: z.string().startsWith('pk_'),
  CLERK_SECRET_KEY: z.string().startsWith('sk_'),
  
  // Stripe
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  STRIPE_WEBHOOK_SECRET: z.string().startsWith('whsec_'),
  
  // Resend
  RESEND_API_KEY: z.string().startsWith('re_'),
  
  // PostHog
  NEXT_PUBLIC_POSTHOG_KEY: z.string().startsWith('phc_'),
  
  // Sentry
  NEXT_PUBLIC_SENTRY_DSN: z.string().url(),
});

export const env = envSchema.parse(process.env);
```

---

## 4. Development Setup

### Prerequisites

- **Bun** v1.3.1+ (package manager & runtime)
- **Node.js** 22+ (for tooling compatibility)
- **Git** with SSH key configured
- **VS Code** with recommended extensions

### Initial Setup

```bash
# Clone repository
git clone git@github.com:hustlestack-us/hustlestack.git
cd hustlestack

# Install dependencies
bun install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your credentials

# Set up Convex
bunx convex dev

# Run development server (separate terminal)
bun run dev

# Open http://localhost:3000
```

### VS Code Extensions (Required)

```json
// .vscode/extensions.json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "prisma.prisma",
    "ms-vscode.vscode-typescript-next",
    "unifiedjs.vscode-mdx",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

### Scripts

```json
// package.json scripts
{
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "next lint && tsc --noEmit",
    "format": "prettier --write .",
    "test": "vitest",
    "test:e2e": "playwright test",
    "convex:dev": "convex dev",
    "convex:deploy": "convex deploy",
    "db:push": "convex deploy",
    "email:dev": "email dev --port 3001"
  }
}
```

---

## 5. Build & Deployment

### Build Process

```bash
# Production build
bun run build

# Build outputs:
# - .next/static: Static assets (cached forever)
# - .next/server: Server components and API routes
# - .vercel/output: Vercel deployment artifact
```

### Vercel Configuration

```json
// vercel.json
{
  "framework": "nextjs",
  "buildCommand": "bun run build",
  "installCommand": "bun install",
  "regions": ["iad1"],
  "crons": [
    {
      "path": "/api/cron/weekly-digest",
      "schedule": "0 9 * * 1"
    }
  ]
}
```

### Deployment Checklist

1. **Environment Variables**: All production keys configured in Vercel
2. **Convex**: Production deployment active (`convex deploy`)
3. **Clerk**: Production instance with correct URLs
4. **Stripe**: Live mode webhooks configured
5. **Resend**: Domain verified
6. **PostHog**: Production project
7. **Sentry**: Release tracking enabled

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      
      - run: bun install --frozen-lockfile
      
      - run: bun run lint
      
      - run: bun run test
      
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## 6. Performance Requirements

### Core Web Vitals Targets

| Metric | Target | Maximum |
|--------|--------|---------|
| **LCP** (Largest Contentful Paint) | < 1.5s | < 2.5s |
| **INP** (Interaction to Next Paint) | < 100ms | < 200ms |
| **CLS** (Cumulative Layout Shift) | < 0.05 | < 0.1 |
| **FCP** (First Contentful Paint) | < 1.0s | < 1.8s |
| **TTFB** (Time to First Byte) | < 200ms | < 500ms |

### Performance Strategies

```typescript
// 1. Server Components (default)
// Render on server, zero JS for static content
export default async function Dashboard() {
  const data = await fetchData();
  return <DashboardView data={data} />;
}

// 2. Streaming with Suspense
import { Suspense } from 'react';

export default function Page() {
  return (
    <>
      <Header /> {/* Instant */}
      <Suspense fallback={<ProfileSkeleton />}>
        <Profile /> {/* Streams when ready */}
      </Suspense>
    </>
  );
}

// 3. Optimistic Updates
import { useOptimistic } from 'react';

function TodoList({ todos }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, newTodo]
  );
}

// 4. Image Optimization
import Image from 'next/image';

<Image
  src={user.avatar}
  alt={user.name}
  width={48}
  height={48}
  priority={isAboveFold}
/>
```

### Bundle Size Limits

| Chunk | Target | Maximum |
|-------|--------|---------|
| Initial JS | < 100KB | < 150KB |
| Per-route JS | < 50KB | < 100KB |
| Total CSS | < 30KB | < 50KB |
| Third-party | < 75KB | < 100KB |

### Monitoring

- **Vercel Analytics**: Real-user Core Web Vitals
- **Sentry Performance**: Transaction tracing
- **PostHog**: Feature performance correlation

---

## 7. Security Requirements

### Authentication & Authorization

```typescript
// Server-side auth check
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function ProtectedPage() {
  const { userId } = await auth();
  if (!userId) redirect('/sign-in');
  // ...
}

// API route protection
import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  // ...
}
```

### Data Validation

```typescript
// Zod schemas for all inputs
import { z } from 'zod';

export const profileSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  bio: z.string().max(500).optional(),
  skills: z.array(z.string()).max(20),
});

// Convex validators
import { v } from 'convex/values';

export const updateProfile = mutation({
  args: {
    name: v.string(),
    bio: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Validated args
  },
});
```

### Security Headers

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
];
```

### Rate Limiting

```typescript
// API rate limiting via Vercel Edge Config or Upstash
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
});

export async function POST(req: Request) {
  const ip = req.headers.get('x-forwarded-for') ?? 'unknown';
  const { success } = await ratelimit.limit(ip);
  
  if (!success) {
    return Response.json({ error: 'Too many requests' }, { status: 429 });
  }
  // ...
}
```

### Compliance Requirements

- **GDPR**: EU user data handling, consent, data export/deletion
- **CCPA**: California privacy rights
- **SOC 2**: Via Clerk, Convex, Stripe compliance
- **PCI DSS**: Stripe handles payment card data

---

## 8. Testing Requirements

### Testing Stack

| Type | Tool | Coverage Target |
|------|------|-----------------|
| Unit | Vitest | 80% |
| Integration | Vitest + Testing Library | 70% |
| E2E | Playwright | Critical paths |
| Visual | Playwright screenshots | Key pages |

### Unit Testing

```typescript
// lib/__tests__/value-calculator.test.ts
import { describe, it, expect } from 'vitest';
import { calculateValueScore } from '../value-calculator';

describe('calculateValueScore', () => {
  it('returns correct score for junior developer', () => {
    const score = calculateValueScore({
      yearsExperience: 2,
      skills: ['React', 'TypeScript'],
      education: 'bachelors',
    });
    expect(score).toBeGreaterThan(50);
    expect(score).toBeLessThan(75);
  });
});
```

### Component Testing

```typescript
// components/__tests__/value-card.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ValueCard } from '../value-card';

describe('ValueCard', () => {
  it('displays the value score', () => {
    render(<ValueCard score={85} />);
    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText('Your Value Score')).toBeInTheDocument();
  });
});
```

### E2E Testing

```typescript
// e2e/onboarding.spec.ts
import { test, expect } from '@playwright/test';

test('complete onboarding flow', async ({ page }) => {
  await page.goto('/sign-up');
  
  // Sign up with Clerk test credentials
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('button[type="submit"]');
  
  // Complete onboarding
  await expect(page).toHaveURL('/onboarding');
  await page.fill('[name="headline"]', 'Software Engineer');
  await page.click('text=Continue');
  
  // Verify dashboard
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('h1')).toContainText('Welcome');
});
```

### Convex Testing

```typescript
// convex/__tests__/users.test.ts
import { convexTest } from 'convex-test';
import { describe, it, expect } from 'vitest';
import schema from '../schema';
import { api } from '../_generated/api';

describe('users', () => {
  it('creates a user correctly', async () => {
    const t = convexTest(schema);
    
    const userId = await t.mutation(api.users.create, {
      clerkId: 'user_123',
      email: 'test@example.com',
      name: 'Test User',
    });
    
    const user = await t.query(api.users.get, { id: userId });
    expect(user?.email).toBe('test@example.com');
  });
});
```

### CI Testing

```yaml
# Run on all PRs
- run: bun run test
- run: bun run test:e2e
- run: bun run lint
- run: tsc --noEmit
```

---

## Appendix: Project Structure

```
hustlestack/
├── app/
│   ├── (auth)/
│   │   ├── sign-in/[[...sign-in]]/
│   │   └── sign-up/[[...sign-up]]/
│   ├── (marketing)/
│   │   ├── page.tsx              # Landing page
│   │   ├── pricing/
│   │   └── about/
│   ├── (app)/
│   │   ├── dashboard/
│   │   ├── profile/
│   │   ├── roadmap/
│   │   ├── mentors/
│   │   └── settings/
│   ├── api/
│   │   └── webhooks/
│   │       ├── clerk/
│   │       └── stripe/
│   ├── layout.tsx
│   ├── globals.css
│   └── providers.tsx
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── forms/
│   ├── cards/
│   └── layouts/
├── convex/
│   ├── schema.ts
│   ├── users.ts
│   ├── profiles.ts
│   ├── roadmaps.ts
│   └── _generated/
├── lib/
│   ├── env.ts
│   ├── utils.ts
│   └── email.ts
├── emails/
│   ├── welcome.tsx
│   └── weekly-digest.tsx
├── public/
├── e2e/
└── types/
```

---

*Last updated: 2026-02-07*
*Version: 1.0.0*
