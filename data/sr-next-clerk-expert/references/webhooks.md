# Clerk Webhooks

## Setup

1. Go to Clerk Dashboard → Webhooks
2. Add endpoint: `https://your-app.com/api/webhooks/clerk`
3. Select events: `user.created`, `user.updated`, `user.deleted`
4. Copy signing secret to `CLERK_WEBHOOK_SECRET`

## Webhook Handler

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import { WebhookEvent } from "@clerk/nextjs/server";

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;

  if (!WEBHOOK_SECRET) {
    throw new Error("Missing CLERK_WEBHOOK_SECRET");
  }

  const headerPayload = headers();
  const svix_id = headerPayload.get("svix-id");
  const svix_timestamp = headerPayload.get("svix-timestamp");
  const svix_signature = headerPayload.get("svix-signature");

  if (!svix_id || !svix_timestamp || !svix_signature) {
    return new Response("Missing svix headers", { status: 400 });
  }

  const body = await req.text();
  const wh = new Webhook(WEBHOOK_SECRET);

  let evt: WebhookEvent;

  try {
    evt = wh.verify(body, {
      "svix-id": svix_id,
      "svix-timestamp": svix_timestamp,
      "svix-signature": svix_signature,
    }) as WebhookEvent;
  } catch (err) {
    console.error("Webhook verification failed:", err);
    return new Response("Invalid signature", { status: 400 });
  }

  const eventType = evt.type;

  switch (eventType) {
    case "user.created":
      await handleUserCreated(evt.data);
      break;
    case "user.updated":
      await handleUserUpdated(evt.data);
      break;
    case "user.deleted":
      await handleUserDeleted(evt.data);
      break;
  }

  return new Response("OK", { status: 200 });
}

async function handleUserCreated(data: any) {
  const { id, email_addresses, first_name, last_name, image_url } = data;
  const email = email_addresses[0]?.email_address;

  // Create user in your database
  // await db.users.create({
  //   clerkId: id,
  //   email,
  //   name: `${first_name ?? ""} ${last_name ?? ""}`.trim(),
  //   imageUrl: image_url,
  // });
}

async function handleUserUpdated(data: any) {
  const { id, email_addresses, first_name, last_name, image_url } = data;
  const email = email_addresses[0]?.email_address;

  // Update user in your database
  // await db.users.update({
  //   where: { clerkId: id },
  //   data: {
  //     email,
  //     name: `${first_name ?? ""} ${last_name ?? ""}`.trim(),
  //     imageUrl: image_url,
  //   },
  // });
}

async function handleUserDeleted(data: any) {
  const { id } = data;

  // Delete or soft-delete user
  // await db.users.delete({ where: { clerkId: id } });
}
```

## Convex Webhook Handler

```typescript
// convex/http.ts
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { Webhook } from "svix";
import { internal } from "./_generated/api";

const http = httpRouter();

http.route({
  path: "/webhooks/clerk",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const secret = process.env.CLERK_WEBHOOK_SECRET!;
    const svixId = request.headers.get("svix-id")!;
    const svixTimestamp = request.headers.get("svix-timestamp")!;
    const svixSignature = request.headers.get("svix-signature")!;

    const body = await request.text();
    const wh = new Webhook(secret);

    let evt: any;
    try {
      evt = wh.verify(body, {
        "svix-id": svixId,
        "svix-timestamp": svixTimestamp,
        "svix-signature": svixSignature,
      });
    } catch {
      return new Response("Invalid signature", { status: 400 });
    }

    switch (evt.type) {
      case "user.created":
        await ctx.runMutation(internal.users.createFromWebhook, {
          clerkId: evt.data.id,
          email: evt.data.email_addresses[0]?.email_address,
          name: `${evt.data.first_name ?? ""} ${evt.data.last_name ?? ""}`.trim(),
          imageUrl: evt.data.image_url,
        });
        break;
    }

    return new Response("OK", { status: 200 });
  }),
});

export default http;
```

## Testing Webhooks Locally

```bash
# Install ngrok
brew install ngrok

# Expose local server
ngrok http 3000

# Use ngrok URL in Clerk Dashboard webhook config
# https://abc123.ngrok.io/api/webhooks/clerk
```

## Required Dependencies

```bash
bun add svix
```
