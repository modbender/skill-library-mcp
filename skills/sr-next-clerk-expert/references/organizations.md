# Clerk Organizations (Multi-tenant)

## Enable Organizations

1. Clerk Dashboard → Configure → Organizations → Enable
2. Configure roles (admin, member, etc.)

## Organization Switcher

```tsx
// components/org-switcher.tsx
"use client";

import { OrganizationSwitcher, ClerkLoaded, ClerkLoading } from "@clerk/nextjs";

export function OrgSwitcher() {
  return (
    <>
      <ClerkLoading>
        <div className="w-48 h-10 bg-muted animate-pulse rounded" />
      </ClerkLoading>
      <ClerkLoaded>
        <OrganizationSwitcher
          afterCreateOrganizationUrl="/dashboard"
          afterSelectOrganizationUrl="/dashboard"
          afterLeaveOrganizationUrl="/dashboard"
        />
      </ClerkLoaded>
    </>
  );
}
```

## Get Active Organization

```typescript
// Server Component
import { auth } from "@clerk/nextjs/server";

export default async function DashboardPage() {
  const { orgId, orgRole, orgSlug } = await auth();
  
  if (!orgId) {
    return <CreateOrgPrompt />;
  }

  return <OrgDashboard orgId={orgId} role={orgRole} />;
}
```

```tsx
// Client Component
"use client";

import { useOrganization, useOrganizationList } from "@clerk/nextjs";

export function OrgInfo() {
  const { organization, membership } = useOrganization();
  const { userMemberships } = useOrganizationList();

  if (!organization) return <div>No organization selected</div>;

  return (
    <div>
      <h2>{organization.name}</h2>
      <p>Role: {membership?.role}</p>
      <p>Members: {organization.membersCount}</p>
    </div>
  );
}
```

## Role-Based Access

```tsx
// app/(private)/admin/page.tsx
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function AdminPage() {
  const { orgRole } = await auth();

  if (orgRole !== "org:admin") {
    redirect("/dashboard");
  }

  return <AdminDashboard />;
}
```

## Protect Component

```tsx
import { Protect } from "@clerk/nextjs";

export function AdminSection() {
  return (
    <Protect role="org:admin" fallback={<div>Admin access required</div>}>
      <AdminControls />
    </Protect>
  );
}
```

## Organization Metadata

```typescript
// Set organization metadata
import { clerkClient } from "@clerk/nextjs/server";

await clerkClient.organizations.updateOrganization(orgId, {
  publicMetadata: {
    plan: "pro",
    features: ["analytics", "api"],
  },
});

// Read metadata
const { organization } = useOrganization();
const plan = organization?.publicMetadata?.plan;
```

## Convex with Organizations

```typescript
// convex/documents.ts
export const list = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];

    // Get org from JWT claims
    const orgId = identity.org_id;

    if (orgId) {
      // Org context - return org documents
      return await ctx.db
        .query("documents")
        .withIndex("by_org", (q) => q.eq("orgId", orgId))
        .collect();
    } else {
      // Personal context - return user documents
      return await ctx.db
        .query("documents")
        .withIndex("by_owner", (q) => q.eq("ownerId", identity.subject))
        .collect();
    }
  },
});
```
