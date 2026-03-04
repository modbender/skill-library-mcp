---
name: sr-next-clerk-expert
description: Senior-level Clerk authentication expertise for Next.js 15/16+ applications. Use when implementing auth, protecting routes, fixing auth errors (500s, handshake redirects, middleware failures), integrating with Convex/Stripe, or debugging Clerk issues. Covers proxy.ts patterns, route groups, client vs server auth, and the 12 Commandments that prevent common disasters.
env:
  required:
    - CLERK_SECRET_KEY
    - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  optional:
    - CLERK_WEBHOOK_SECRET
    - STRIPE_SECRET_KEY
    - NEXT_PUBLIC_CONVEX_URL
    - CONVEX_DEPLOYMENT
---

# Senior Next.js + Clerk Expert

You are a senior engineer implementing Clerk authentication. Follow these patterns exactly—deviations cause production outages.

---

## ⚠️ CRITICAL: THE TWELVE COMMANDMENTS

These rules are non-negotiable. Violations cause 500 errors, infinite redirects, and broken sites.

| # | Commandment | Violation Consequence |
|---|-------------|----------------------|
| I | Use `app/(private)/` route groups | Maintenance hell, broken auth |
| II | Keep proxy.ts simple (protect only private) | Every new page needs proxy update |
| III | NEVER call `auth()` on public pages | 500 errors, slow pages, SEO death |
| IV | Use `<SignedIn>`/`<SignedOut>` for conditional content | Server errors on static pages |
| V | Wrap Clerk components in `<ClerkLoaded>` | Flash of wrong content |
| VI | Pair `<ClerkLoaded>` with `<ClerkLoading>` | Jarring loading states |
| VII | Configure redirects in ClerkProvider | Redirect loops |
| VIII | No handshake redirects on public pages | Broken user experience |
| IX | Keep marketing pages STATIC | Slow pages, bad SEO |
| X | Verify env vars EXACTLY (copy-paste only) | Cryptic 500 errors |
| XI | Use `proxy.ts` not `middleware.ts` (Next.js 16+) | Deprecation warnings |
| XII | Test as anonymous user before deploy | Ship broken auth |

---

## Quick Reference

### Project Structure
```
app/
├── (private)/           # Protected - requires auth
│   ├── dashboard/
│   ├── settings/
│   └── layout.tsx       # Can call auth() here
├── page.tsx             # PUBLIC - NO auth()
├── layout.tsx           # Root - ClerkProvider
├── sign-in/[[...sign-in]]/page.tsx
└── sign-up/[[...sign-up]]/page.tsx
```

### The ONLY Correct proxy.ts
```typescript
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPrivateRoute = createRouteMatcher(["/(private)(.*)"]);

export default clerkMiddleware(async (auth, request) => {
  if (isPrivateRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
```

---

## Patterns by Use Case

### Public Page with Auth-Conditional Content
```tsx
// app/page.tsx - CORRECT
import { ClerkLoaded, ClerkLoading, SignedIn, SignedOut } from "@clerk/nextjs";

export default function HomePage() {
  return (
    <main>
      <h1>Welcome</h1>
      <ClerkLoading>
        <Skeleton />
      </ClerkLoading>
      <ClerkLoaded>
        <SignedOut>
          <a href="/sign-in">Sign In</a>
        </SignedOut>
        <SignedIn>
          <a href="/dashboard">Dashboard</a>
        </SignedIn>
      </ClerkLoaded>
    </main>
  );
}
```

### Private Layout (Route Protection)
```tsx
// app/(private)/layout.tsx
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function PrivateLayout({ children }: { children: React.ReactNode }) {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");
  return <>{children}</>;
}
```

### Root Layout with ClerkProvider
```tsx
// app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/dashboard"
      afterSignUpUrl="/dashboard"
    >
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

---

## Advanced Patterns

For complex integrations, see reference files:

- **Convex Integration**: See [references/convex.md](references/convex.md) for ConvexProviderWithClerk patterns
- **Stripe/Billing**: See [references/stripe.md](references/stripe.md) for subscription flows with Clerk
- **Multi-tenant/Organizations**: See [references/organizations.md](references/organizations.md) for org-based auth
- **Webhooks**: See [references/webhooks.md](references/webhooks.md) for user sync patterns
- **Custom Sign-in Pages**: See [references/custom-ui.md](references/custom-ui.md) for branded auth pages
- **Debugging Guide**: See [references/debugging.md](references/debugging.md) for fixing common errors

---

## Environment Variables

```bash
# .env.local - COPY FROM CLERK DASHBOARD (do not type manually)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Optional redirects
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

**⚠️ CRITICAL**: Copy-paste keys from Clerk dashboard. Manual typing causes `1/l` and `x/X` errors that produce cryptic 500s.

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `MIDDLEWARE_INVOCATION_FAILED` | Missing/wrong CLERK_SECRET_KEY | Re-copy from dashboard |
| `?__clerk_handshake=` in URL | `auth()` called on public page | Remove auth(), use SignedIn/SignedOut |
| Infinite redirect loop | Missing/wrong redirect config | Set afterSignInUrl in ClerkProvider |
| 500 on homepage | Server-side auth on static page | Make page client-side or remove auth |
| Flash of wrong content | Missing ClerkLoaded wrapper | Wrap Clerk components |

---

## Anti-Patterns (NEVER DO)

```tsx
// ❌ WRONG - auth() on public page
export default async function HomePage() {
  const { userId } = await auth();  // BREAKS STATIC RENDERING
  if (userId) redirect("/dashboard");
  return <LandingPage />;
}

// ❌ WRONG - listing every public route
const isPublicRoute = createRouteMatcher([
  "/", "/about", "/pricing", "/blog", "/contact", // MAINTENANCE HELL
]);

// ❌ WRONG - no ClerkLoaded wrapper
<SignedIn>
  <UserButton />  // FLASHES INCORRECTLY
</SignedIn>

// ❌ WRONG - middleware.ts in Next.js 16+
// File: middleware.ts  // DEPRECATED - USE proxy.ts
```

---

## Migration: middleware.ts → proxy.ts

```bash
# Option 1: Rename
mv middleware.ts proxy.ts

# Option 2: Codemod
npx @next/codemod@latest middleware-to-proxy
```

---

## 🔐 Security Best Practices

### Secret Management
- **Store secrets in platform env vars** (Vercel, Railway, etc.) — never in code or git
- **Use separate keys for dev/staging/prod** — Clerk provides different instances
- **Rotate keys if compromised** — Clerk Dashboard → API Keys → Add new key → update env → delete old
- **Limit access** — only team members who need keys should have dashboard access

### Key Rotation Procedure
1. Create new key in Clerk Dashboard
2. Update production env var (Vercel: `vercel env rm CLERK_SECRET_KEY production && vercel env add CLERK_SECRET_KEY production`)
3. Redeploy
4. Verify auth works
5. Delete old key from Clerk Dashboard

### Webhook Security
- **Always verify signatures** — use `svix` library (shown in references/webhooks.md)
- **Use HTTPS endpoints only** — never expose webhook URLs over HTTP
- **Store CLERK_WEBHOOK_SECRET securely** — same as other secrets

### Debug Logging
⚠️ **NEVER use debug mode in production:**
```typescript
// ❌ REMOVE BEFORE DEPLOYING
export default clerkMiddleware(
  async (auth, request) => { /* ... */ },
  { debug: true }  // LEAKS TOKENS TO LOGS
);
```
Debug mode logs handshake tokens (`?__clerk_handshake=`) which are sensitive. Use only in local development.

### Least Privilege
| Secret | Scope | Notes |
|--------|-------|-------|
| `CLERK_SECRET_KEY` | Server only | Never expose to client |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Client safe | Can be in client bundles |
| `CLERK_WEBHOOK_SECRET` | Server only | Webhook handler only |
| `STRIPE_SECRET_KEY` | Server only | API routes only |

---

## Verification Checklist

Before deploying, verify:

- [ ] `proxy.ts` exists (not `middleware.ts`)
- [ ] proxy.ts ONLY protects `/(private)` routes
- [ ] No `auth()` calls in `app/page.tsx` or marketing pages
- [ ] All Clerk components wrapped in `<ClerkLoaded>`
- [ ] `<ClerkLoading>` shows skeleton/spinner
- [ ] Env vars copied exactly from Clerk dashboard
- [ ] Anonymous user can access homepage (incognito test)
- [ ] Sign-in redirects to correct page
- [ ] Dashboard requires authentication
