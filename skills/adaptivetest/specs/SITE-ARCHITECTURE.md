# AdaptiveTest Skill -- Site Architecture Spec

> **Route, configuration, and integration changes for the `/developers` page.**
> **Target repo:** `adaptivetest-marketing`

---

## New Route

| Route | Page Title | Description |
|-------|-----------|-------------|
| `/developers` | Developers - AdaptiveTest | API landing page for developers and OpenClaw users |

---

## File Tree (new and modified files only)

```
adaptivetest-marketing/
├── src/
│   ├── app/
│   │   ├── developers/
│   │   │   └── page.tsx              # NEW: /developers landing page
│   │   └── layout.tsx                # MODIFY: add "Developers" to nav links array
│   └── components/
│       ├── CodeBlock.tsx              # NEW: terminal-style code display
│       ├── StepCard.tsx               # NEW: numbered step component
│       ├── FAQAccordion.tsx           # NEW: expandable Q&A component
│       ├── PricingCard.tsx            # NEW or REUSE if exists
│       ├── Navbar.tsx                 # MODIFY: add "Developers" nav link
│       └── Footer.tsx                 # MODIFY: add "Developers" footer link
```

---

## Navbar Update

Add "Developers" to the navigation links array. Position it after existing links, before any CTA buttons.

```tsx
// In the nav links array (exact format depends on existing implementation)
{ label: "Developers", href: "/developers" }
```

Style: matches existing nav links (`text-gray-600 hover:text-indigo-600 transition`).
Mobile menu: include in the same position.

---

## Footer Update

Add "Developers" link to the appropriate column (Product or Resources).

```tsx
{ label: "Developers", href: "/developers" }
```

---

## SEO Metadata

```tsx
// src/app/developers/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Developers - AdaptiveTest",
  description:
    "Add adaptive testing to any application. IRT/CAT engine, AI question generation, and learning recommendations. One API key, six capabilities.",
  openGraph: {
    title: "Developers - AdaptiveTest",
    description:
      "Production-grade adaptive testing API for education and training applications.",
    url: "https://adaptivetest.io/developers",
    siteName: "AdaptiveTest",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Developers - AdaptiveTest",
    description:
      "Production-grade adaptive testing API for education and training applications.",
  },
};
```

---

## Stripe Checkout Integration

The "Start Free Trial" and "Subscribe" buttons redirect to Stripe Checkout (hosted).

```tsx
// Button onClick handler
const handleCheckout = async () => {
  // Option A: Direct redirect to Stripe Checkout URL
  // (requires creating a Stripe Checkout Session server-side first)
  const response = await fetch("/api/create-checkout-session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ price_id: STRIPE_PRICE_ID_PRO }),
  });
  const { url } = await response.json();
  window.location.href = url;
};
```

**Option A (recommended): API route on marketing site**

Create a minimal Next.js API route that creates a Stripe Checkout session and redirects:

```
src/app/api/create-checkout-session/route.ts  # NEW
```

```tsx
import Stripe from "stripe";
import { NextResponse } from "next/server";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(request: Request) {
  const { price_id } = await request.json();

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    payment_method_types: ["card"],
    line_items: [{ price: price_id, quantity: 1 }],
    subscription_data: { trial_period_days: 7 },
    success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/developers?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/developers`,
    metadata: { product: "adaptivetest-skill", tier: "pro" },
  });

  return NextResponse.json({ url: session.url });
}
```

**Option B (simpler): Stripe Payment Link**

Use a pre-configured Stripe Payment Link (no server-side code needed):
```tsx
<a href="https://buy.stripe.com/<payment-link-id>">Start Free Trial</a>
```

**Decision: Option A (API route).** Required for passing `session_id` back to the success page for API key retrieval.

---

## Success Page Behavior

When the user returns from Stripe Checkout with `?session_id=`, the page should:

1. Detect `session_id` query parameter
2. Call `GET /api/keys/from-session?session_id=<id>` on the AdaptiveTest platform
3. Display the API key in a prominent, copy-able code block
4. Show a "Key shown once -- copy it now" warning
5. Show next steps: install the OpenClaw skill, configure the env var

```tsx
// src/app/developers/page.tsx
"use client";
import { useSearchParams } from "next/navigation";

// If session_id is present, show the API key retrieval UI
// Otherwise, show the normal landing page
```

This means the page needs a client component wrapper (or a client-side section) for the success state. The rest of the page can remain server-rendered.

---

## Environment Variables (new, on adaptivetest-marketing Vercel)

```
- [ ] STRIPE_SECRET_KEY -- for creating Checkout sessions (if using Option A)
- [ ] NEXT_PUBLIC_SITE_URL -- e.g., https://adaptivetest.io
- [ ] NEXT_PUBLIC_STRIPE_PRICE_ID_PRO -- Stripe price ID for the Pro tier
- [ ] NEXT_PUBLIC_ADAPTIVETEST_API_URL -- for the success page key retrieval
```

---

## CSP / Security Headers

**No CSP changes needed** if using Stripe Checkout redirect (hosted). The redirect goes to `checkout.stripe.com` which is a full page navigation, not an iframe or XHR.

If using Option A (API route), the `STRIPE_SECRET_KEY` is server-side only and never exposed to the client.

---

## Sitemap Update

Add to existing `sitemap.xml` or `sitemap.ts`:

```tsx
{
  url: "https://adaptivetest.io/developers",
  lastModified: new Date(),
  changeFrequency: "monthly",
  priority: 0.8,
}
```

---

## robots.txt

No changes needed. `/developers` should be indexable (not blocked).
