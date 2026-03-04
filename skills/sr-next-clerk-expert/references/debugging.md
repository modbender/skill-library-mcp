# Clerk Debugging Guide

## Error: MIDDLEWARE_INVOCATION_FAILED (500)

**Symptoms:**
- Site returns 500 error
- Vercel logs show `MIDDLEWARE_INVOCATION_FAILED`
- Error mentions "secret key invalid"

**Causes:**
1. Missing `CLERK_SECRET_KEY` env var on Vercel
2. Wrong key (typo, `1` vs `l`, `x` vs `X`)
3. Key from wrong Clerk app/environment

**Fix:**
```bash
# 1. Go to Clerk Dashboard → API Keys
# 2. Click "Reveal Secret Key"
# 3. Click the COPY BUTTON (don't manually select)
# 4. Add to Vercel
vercel env add CLERK_SECRET_KEY production
# 5. Paste exactly
# 6. Redeploy
vercel --prod
```

---

## Error: Handshake Redirect Loop

**Symptoms:**
- URL contains `?__clerk_handshake=...`
- Page keeps redirecting
- Works when signed in, breaks when signed out

**Cause:** `auth()` called on a public page

**Fix:**
```tsx
// ❌ WRONG
export default async function HomePage() {
  const { userId } = await auth();
  // ...
}

// ✅ CORRECT
export default function HomePage() {
  return (
    <ClerkLoaded>
      <SignedIn>{/* authenticated content */}</SignedIn>
      <SignedOut>{/* public content */}</SignedOut>
    </ClerkLoaded>
  );
}
```

---

## Error: Infinite Redirect After Sign-In

**Symptoms:**
- Sign in succeeds but redirects back to sign-in
- Browser shows redirect loop error

**Causes:**
1. `afterSignInUrl` points to protected route that redirects back
2. Missing user in database (Convex integration)
3. Middleware blocking the redirect target

**Fix:**
```tsx
// Ensure afterSignInUrl goes to an accessible page
<ClerkProvider afterSignInUrl="/dashboard">

// Ensure /dashboard layout doesn't redirect signed-in users
// app/(private)/layout.tsx
export default async function Layout({ children }) {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");  // Only redirect if NOT signed in
  return <>{children}</>;
}
```

---

## Error: Flash of Unauthenticated Content

**Symptoms:**
- Sign-in button briefly shows for authenticated users
- Content flickers on page load

**Cause:** Missing `<ClerkLoaded>` wrapper

**Fix:**
```tsx
// ❌ WRONG
<SignedIn>
  <UserButton />
</SignedIn>

// ✅ CORRECT
<ClerkLoading>
  <Skeleton className="w-8 h-8 rounded-full" />
</ClerkLoading>
<ClerkLoaded>
  <SignedIn>
    <UserButton />
  </SignedIn>
</ClerkLoaded>
```

---

## Error: "Client created with undefined deployment address"

**Symptoms:**
- Build fails with Convex error
- Works locally but not on Vercel

**Cause:** Missing Convex env vars on Vercel

**Fix:**
```bash
vercel env add CONVEX_DEPLOYMENT production
vercel env add NEXT_PUBLIC_CONVEX_URL production
vercel --prod
```

---

## Debug Mode

⚠️ **LOCAL DEVELOPMENT ONLY** — Never enable in production!

Debug mode logs sensitive handshake tokens that could be exploited.

```typescript
// FOR LOCAL DEV ONLY - REMOVE BEFORE DEPLOYING
export default clerkMiddleware(
  async (auth, request) => {
    if (process.env.NODE_ENV === 'development') {
      console.log("Auth request:", request.url);
    }
    // ... your logic
  },
  { debug: process.env.NODE_ENV === 'development' }
);
```

**Before deploying:**
1. Remove `{ debug: true }`
2. Remove any `console.log` that logs request URLs
3. These can expose `?__clerk_handshake=` tokens in logs

---

## Verification Steps

1. **Test as anonymous user:**
   - Open incognito window
   - Visit homepage → should load without redirect
   - Visit `/dashboard` → should redirect to sign-in

2. **Test sign-in flow:**
   - Sign in → should redirect to dashboard
   - Refresh dashboard → should stay on dashboard
   - Click sign out → should redirect to homepage

3. **Check console:**
   - No Clerk errors
   - No hydration mismatches
   - No 401/403 errors in Network tab

4. **Check Clerk dashboard:**
   - Sessions tab shows activity
   - No errors in Logs tab
