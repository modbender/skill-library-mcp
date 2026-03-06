# Clerk + Convex Integration

## Provider Setup

```tsx
// providers/convex-clerk-provider.tsx
"use client";

import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { ConvexProviderWithClerk } from "convex/react-clerk";
import { ConvexReactClient } from "convex/react";
import { ReactNode } from "react";

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function ConvexClerkProvider({ children }: { children: ReactNode }) {
  return (
    <ClerkProvider
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/dashboard"
      afterSignUpUrl="/dashboard"
    >
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}
```

## Root Layout

```tsx
// app/layout.tsx
import { ConvexClerkProvider } from "@/providers/convex-clerk-provider";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <ConvexClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ConvexClerkProvider>
  );
}
```

## User Sync Pattern (Webhook-free)

Sync Clerk user to Convex on first authenticated action:

```typescript
// convex/users.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const getOrCreateUser = mutation({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    // Check if user exists
    const existing = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();

    if (existing) return existing._id;

    // Create new user
    return await ctx.db.insert("users", {
      clerkId: identity.subject,
      email: identity.email!,
      name: identity.name ?? "",
      imageUrl: identity.pictureUrl ?? "",
      createdAt: Date.now(),
    });
  },
});

export const currentUser = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;

    return await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
  },
});
```

## Schema

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.string(),
    imageUrl: v.string(),
    createdAt: v.number(),
  })
    .index("by_clerk_id", ["clerkId"])
    .index("by_email", ["email"]),
});
```

## Client-Side User Sync

```tsx
// components/user-sync.tsx
"use client";

import { useUser } from "@clerk/nextjs";
import { useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useEffect } from "react";

export function UserSync({ children }: { children: React.ReactNode }) {
  const { isSignedIn, isLoaded } = useUser();
  const syncUser = useMutation(api.users.getOrCreateUser);

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      syncUser().catch(console.error);
    }
  }, [isLoaded, isSignedIn, syncUser]);

  return <>{children}</>;
}
```

## Protected Convex Queries

```typescript
// convex/documents.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];

    return await ctx.db
      .query("documents")
      .withIndex("by_owner", (q) => q.eq("ownerId", identity.subject))
      .collect();
  },
});

export const create = mutation({
  args: { title: v.string() },
  handler: async (ctx, { title }) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    return await ctx.db.insert("documents", {
      title,
      ownerId: identity.subject,
      createdAt: Date.now(),
    });
  },
});
```
