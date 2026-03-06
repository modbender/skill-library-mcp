# Clerk + Stripe Billing Integration

## Architecture

```
User signs up (Clerk) → Webhook creates Stripe customer → User subscribes → Webhook updates user
```

## Clerk Webhook for Stripe Customer

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import { WebhookEvent } from "@clerk/nextjs/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET!;
  const headerPayload = headers();
  const svix_id = headerPayload.get("svix-id");
  const svix_timestamp = headerPayload.get("svix-timestamp");
  const svix_signature = headerPayload.get("svix-signature");

  const body = await req.text();
  const wh = new Webhook(WEBHOOK_SECRET);
  let evt: WebhookEvent;

  try {
    evt = wh.verify(body, {
      "svix-id": svix_id!,
      "svix-timestamp": svix_timestamp!,
      "svix-signature": svix_signature!,
    }) as WebhookEvent;
  } catch (err) {
    return new Response("Invalid signature", { status: 400 });
  }

  if (evt.type === "user.created") {
    const { id, email_addresses, first_name, last_name } = evt.data;
    const email = email_addresses[0]?.email_address;

    // Create Stripe customer
    const customer = await stripe.customers.create({
      email,
      name: `${first_name} ${last_name}`.trim(),
      metadata: { clerkId: id },
    });

    // Store stripeCustomerId in your database
    // await db.users.update({ clerkId: id, stripeCustomerId: customer.id });
  }

  return new Response("OK", { status: 200 });
}
```

## Checkout Session

```typescript
// app/api/checkout/route.ts
import { auth, currentUser } from "@clerk/nextjs/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response("Unauthorized", { status: 401 });

  const user = await currentUser();
  const { priceId } = await req.json();

  // Get or create Stripe customer
  // const stripeCustomerId = await getStripeCustomerId(userId);

  const session = await stripe.checkout.sessions.create({
    customer_email: user?.emailAddresses[0]?.emailAddress,
    mode: "subscription",
    payment_method_types: ["card"],
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/dashboard?success=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/pricing?canceled=true`,
    metadata: { clerkId: userId },
  });

  return Response.json({ url: session.url });
}
```

## Subscription Status Check

```typescript
// lib/subscription.ts
import { auth } from "@clerk/nextjs/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function getSubscription() {
  const { userId } = await auth();
  if (!userId) return null;

  // Get stripeCustomerId from your database
  // const stripeCustomerId = await getStripeCustomerId(userId);

  const subscriptions = await stripe.subscriptions.list({
    customer: stripeCustomerId,
    status: "active",
    limit: 1,
  });

  return subscriptions.data[0] ?? null;
}

export async function hasActiveSubscription(): Promise<boolean> {
  const subscription = await getSubscription();
  return subscription?.status === "active";
}
```

## Protected Billing Routes

```tsx
// app/(private)/billing/page.tsx
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { getSubscription } from "@/lib/subscription";

export default async function BillingPage() {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");

  const subscription = await getSubscription();

  return (
    <div>
      {subscription ? (
        <SubscriptionDetails subscription={subscription} />
      ) : (
        <UpgradePrompt />
      )}
    </div>
  );
}
```

## Customer Portal

```typescript
// app/api/billing/portal/route.ts
import { auth } from "@clerk/nextjs/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST() {
  const { userId } = await auth();
  if (!userId) return new Response("Unauthorized", { status: 401 });

  // Get stripeCustomerId from your database
  // const stripeCustomerId = await getStripeCustomerId(userId);

  const session = await stripe.billingPortal.sessions.create({
    customer: stripeCustomerId,
    return_url: `${process.env.NEXT_PUBLIC_URL}/dashboard`,
  });

  return Response.json({ url: session.url });
}
```
