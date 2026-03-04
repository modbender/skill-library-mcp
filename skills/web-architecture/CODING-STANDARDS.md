# Coding Standards

> Next.js 16 + React 19 + Convex + TypeScript

---

## Table of Contents

1. [TypeScript Standards](#1-typescript-standards)
2. [React/Next.js Patterns](#2-reactnextjs-patterns)
3. [File Organization](#3-file-organization)
4. [Convex Patterns](#4-convex-patterns)
5. [Component Standards](#5-component-standards)
6. [Error Handling](#6-error-handling)
7. [Testing Standards](#7-testing-standards)
8. [Git Conventions](#8-git-conventions)

---

## 1. TypeScript Standards

### Strict Mode Configuration

We use strict TypeScript. The `tsconfig.json` must include:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### Type vs Interface Conventions

| Use | When |
|-----|------|
| `interface` | Object shapes, component props, extendable contracts |
| `type` | Unions, intersections, mapped types, primitives |

```typescript
// ✅ Interface for props and object shapes
interface UserProps {
  id: string;
  name: string;
  email: string;
}

// ✅ Type for unions and computed types
type Status = "pending" | "active" | "archived";
type UserWithStatus = UserProps & { status: Status };

// ✅ Interface for extension
interface AdminProps extends UserProps {
  permissions: string[];
}
```

### Generic Patterns

```typescript
// ✅ Constrained generics with meaningful names
function getProperty<TObj, TKey extends keyof TObj>(
  obj: TObj,
  key: TKey
): TObj[TKey] {
  return obj[key];
}

// ✅ Default generic types
interface ApiResponse<TData = unknown> {
  data: TData;
  error: string | null;
  status: number;
}

// ✅ Generic React components
interface ListProps<TItem> {
  items: TItem[];
  renderItem: (item: TItem, index: number) => React.ReactNode;
  keyExtractor: (item: TItem) => string;
}

function List<TItem>({ items, renderItem, keyExtractor }: ListProps<TItem>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}
```

### Utility Types Usage

```typescript
// ✅ Prefer built-in utility types
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type ReadonlyUser = Readonly<User>;
type UserName = Pick<User, "firstName" | "lastName">;
type UserWithoutId = Omit<User, "id">;

// ✅ Record for dictionaries
type UserMap = Record<string, User>;

// ✅ Extract and Exclude for union manipulation
type ActiveStatus = Extract<Status, "active" | "pending">;
type InactiveStatus = Exclude<Status, "active">;

// ✅ ReturnType and Parameters for function types
type FetchUserReturn = ReturnType<typeof fetchUser>;
type FetchUserParams = Parameters<typeof fetchUser>;
```

### Zod Schema Patterns

```typescript
import { z } from "zod";

// ✅ Define schemas in lib/validations/
// File: lib/validations/user.ts

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email("Invalid email address"),
  name: z.string().min(2, "Name must be at least 2 characters"),
  role: z.enum(["user", "admin", "moderator"]),
  createdAt: z.date(),
});

// ✅ Infer types from schemas
export type User = z.infer<typeof userSchema>;

// ✅ Create partial/pick schemas for forms
export const createUserSchema = userSchema.omit({ id: true, createdAt: true });
export type CreateUserInput = z.infer<typeof createUserSchema>;

export const updateUserSchema = userSchema.partial().required({ id: true });
export type UpdateUserInput = z.infer<typeof updateUserSchema>;

// ✅ Reusable field schemas
export const emailSchema = z.string().email("Invalid email");
export const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .regex(/[A-Z]/, "Password must contain an uppercase letter")
  .regex(/[0-9]/, "Password must contain a number");

// ✅ Use with react-hook-form
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

function CreateUserForm() {
  const form = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: "",
      name: "",
      role: "user",
    },
  });
  // ...
}
```

---

## 2. React/Next.js Patterns

### Server vs Client Component Decisions

```
┌─────────────────────────────────────────────────────────────────┐
│                     DECISION TREE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Does it need browser APIs, state, or effects?                  │
│     ├── YES → Client Component ("use client")                   │
│     └── NO  → Does it fetch data?                               │
│                  ├── YES → Server Component (default)           │
│                  └── NO  → Does it render user-specific data?   │
│                               ├── YES → Consider both           │
│                               └── NO  → Server Component        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

| Server Components (Default) | Client Components ("use client") |
|-----------------------------|----------------------------------|
| Data fetching | useState, useEffect, useRef |
| Database access | Event handlers (onClick, onChange) |
| Sensitive operations | Browser APIs (localStorage, etc.) |
| Large dependencies | Real-time subscriptions |
| Static content | Interactive UI |

```typescript
// ✅ Server Component (default) - app/users/page.tsx
import { api } from "@/convex/_generated/api";
import { fetchQuery } from "convex/nextjs";

export default async function UsersPage() {
  const users = await fetchQuery(api.users.list);
  return <UserList users={users} />;
}

// ✅ Client Component - components/users/user-form.tsx
"use client";

import { useState } from "react";
import { useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";

export function UserForm() {
  const [name, setName] = useState("");
  const createUser = useMutation(api.users.create);
  // ...
}
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | kebab-case | `user-avatar.tsx` |
| Pages | kebab-case folders | `app/user-profile/page.tsx` |
| Utilities | kebab-case | `format-date.ts` |
| Hooks | camelCase with `use` prefix | `use-user.ts` |
| Types | kebab-case | `user-types.ts` |
| Constants | SCREAMING_SNAKE_CASE | `API_ENDPOINTS` |
| Convex functions | camelCase | `users.ts` |

### Component Structure (Co-location)

```
components/
├── ui/                          # shadcn/ui primitives
│   ├── button.tsx
│   ├── input.tsx
│   └── dialog.tsx
├── users/                       # Feature: Users
│   ├── user-avatar.tsx
│   ├── user-card.tsx
│   ├── user-form.tsx
│   ├── user-list.tsx
│   └── index.ts                 # Barrel export
├── auth/                        # Feature: Auth
│   ├── sign-in-form.tsx
│   ├── sign-up-form.tsx
│   └── index.ts
└── layout/                      # Layout components
    ├── header.tsx
    ├── footer.tsx
    ├── sidebar.tsx
    └── index.ts
```

### Custom Hooks Patterns

```typescript
// ✅ Location: hooks/use-user.ts or components/users/use-user.ts

import { useQuery, useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useCallback, useMemo } from "react";

// ✅ Encapsulate related Convex operations
export function useUser(userId: string) {
  const user = useQuery(api.users.get, { id: userId });
  const updateUser = useMutation(api.users.update);
  const deleteUser = useMutation(api.users.delete);

  const isLoading = user === undefined;

  const handleUpdate = useCallback(
    async (data: Partial<User>) => {
      await updateUser({ id: userId, ...data });
    },
    [updateUser, userId]
  );

  const handleDelete = useCallback(async () => {
    await deleteUser({ id: userId });
  }, [deleteUser, userId]);

  return {
    user,
    isLoading,
    updateUser: handleUpdate,
    deleteUser: handleDelete,
  };
}

// ✅ Hooks for complex state logic
export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => setValue((v) => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return [value, { toggle, setTrue, setFalse }] as const;
}

// ✅ Hooks for side effects
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

### State Management Approaches

```
┌─────────────────────────────────────────────────────────────────┐
│                     STATE LOCATION                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Server State (Convex)                                          │
│  └── useQuery, useMutation, useAction                           │
│      └── Real-time, persistent, shared                          │
│                                                                  │
│  URL State (Next.js)                                            │
│  └── useSearchParams, usePathname                               │
│      └── Filters, pagination, tabs                              │
│                                                                  │
│  Form State (react-hook-form)                                   │
│  └── useForm with Zod resolver                                  │
│      └── Validation, submission                                 │
│                                                                  │
│  UI State (React)                                               │
│  └── useState, useReducer                                       │
│      └── Modals, dropdowns, local toggles                       │
│                                                                  │
│  Shared UI State (Context)                                      │
│  └── Only when prop drilling becomes painful                    │
│      └── Theme, sidebar state, toasts                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Fetching Patterns (Convex)

```typescript
// ✅ Server Component fetching
import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";

export default async function Page() {
  const data = await fetchQuery(api.posts.list);
  return <PostList initialPosts={data} />;
}

// ✅ Client Component real-time subscription
"use client";

import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export function PostList({ initialPosts }: { initialPosts: Post[] }) {
  // Real-time updates, falls back to initialPosts while loading
  const posts = useQuery(api.posts.list) ?? initialPosts;
  return <>{posts.map((post) => <PostCard key={post._id} post={post} />)}</>;
}

// ✅ Conditional queries
const user = useQuery(
  api.users.get,
  userId ? { id: userId } : "skip"
);

// ✅ Mutations with optimistic updates
const createPost = useMutation(api.posts.create);

async function handleSubmit(data: CreatePostInput) {
  try {
    await createPost(data);
    toast.success("Post created");
  } catch (error) {
    toast.error("Failed to create post");
  }
}
```

### Layout Composition Pattern

**Don't rely on nested `layout.tsx` files for page chrome.** Use a composable Layout component instead.

❌ **Anti-pattern:**
```typescript
// app/(dashboard)/layout.tsx
// Complex conditionals bleeding into every child page
export default function Layout({ children }) {
  const isDeveloperSection = /* complex check */;
  return (
    <div className={isDeveloperSection ? "grid-with-sidebar" : "full-width"}>
      {children}
    </div>
  );
}
```

✅ **Correct pattern:**

```typescript
// components/layout/layout.tsx
import { cn } from "@/lib/utils";
import Navbar from "./navbar";
import Footer from "./footer";

export type LayoutStyle = "default" | "full" | "canvas" | "dashboard";

interface LayoutProps {
  children: React.ReactNode;
  style?: LayoutStyle;
  sidebar?: boolean;
  className?: string;
}

export function Layout({
  children,
  style = "default",
  sidebar = false,
  className,
}: LayoutProps) {
  switch (style) {
    case "dashboard":
      return (
        <div className={cn("flex flex-col min-h-dvh", className)}>
          <Navbar />
          <div className="flex flex-1">
            {sidebar && <Sidebar />}
            <main className="flex-1">{children}</main>
          </div>
        </div>
      );
    case "canvas":
      // No navbar, no footer — for onboarding, auth, custom flows
      return (
        <div className={cn("flex flex-col min-h-dvh", className)}>
          {children}
        </div>
      );
    case "full":
      return (
        <div className={cn("flex flex-col min-h-dvh", className)}>
          <Navbar sticky={false} />
          {children}
          <Footer />
        </div>
      );
    case "default":
    default:
      return (
        <div className={cn("flex flex-col min-h-dvh", className)}>
          <Navbar sticky={true} />
          {children}
          <Footer />
        </div>
      );
  }
}
```

```typescript
// Usage in pages — explicit control per-page
import { Layout } from "@/components/layout";

export default function DeveloperDashboard() {
  return (
    <Layout style="dashboard" sidebar>
      {/* page content */}
    </Layout>
  );
}

export default function OnboardingPage() {
  return (
    <Layout style="canvas">
      {/* full control, no inherited chrome */}
    </Layout>
  );
}
```

**Why:** Parent `layout.tsx` cascades whether you want it or not. Composition gives per-page control without conditional gymnastics.

---

### Provider Composition Pattern

**Don't nest providers directly in layout.tsx.** Use a `/providers` folder with a single composed export.

❌ **Anti-pattern:**
```typescript
// app/layout.tsx — messy nesting
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ClerkProvider>
          <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
            <ThemeProvider>
              <PostHogProvider>
                <TooltipProvider>
                  {children}
                  <Toaster />
                </TooltipProvider>
              </PostHogProvider>
            </ThemeProvider>
          </ConvexProviderWithClerk>
        </ClerkProvider>
      </body>
    </html>
  );
}
```

✅ **Correct pattern:**

```
providers/
├── index.tsx         # Composed export
├── convex.tsx        # Convex + Clerk
├── posthog.tsx       # Analytics
└── theme.tsx         # Theme provider
```

```typescript
// providers/convex.tsx
"use client";

import { ConvexReactClient } from "convex/react";
import { ConvexProviderWithClerk } from "convex/react-clerk";
import { ClerkProvider, useAuth } from "@clerk/nextjs";

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function ConvexClientProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}>
      <ConvexProviderWithClerk useAuth={useAuth} client={convex}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}
```

```typescript
// providers/index.tsx
import { ConvexClientProvider } from "@/providers/convex";
import { PostHogProvider } from "@/providers/posthog";
import { ThemeProvider } from "@/providers/theme";
import { Toaster } from "@/components/ui/sonner";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ConvexClientProvider>
      <PostHogProvider>
        <ThemeProvider>
          {children}
          <Toaster />
        </ThemeProvider>
      </PostHogProvider>
    </ConvexClientProvider>
  );
}
```

```typescript
// app/layout.tsx — clean
import Providers from "@/providers";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

**Why:** Modular providers are easier to add, remove, and debug. Each provider file owns its configuration. Root layout stays clean.

---

## 3. File Organization

```
.
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group (no layout nesting)
│   │   ├── sign-in/
│   │   │   └── [[...sign-in]]/
│   │   │       └── page.tsx
│   │   └── sign-up/
│   │       └── [[...sign-up]]/
│   │           └── page.tsx
│   ├── (dashboard)/              # Protected routes
│   │   ├── layout.tsx            # Dashboard layout with sidebar
│   │   ├── page.tsx              # Dashboard home
│   │   ├── settings/
│   │   │   └── page.tsx
│   │   └── [projectId]/          # Dynamic routes
│   │       └── page.tsx
│   ├── (marketing)/              # Public marketing pages
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Landing page
│   │   ├── pricing/
│   │   └── about/
│   ├── api/                      # API routes
│   │   ├── webhooks/
│   │   │   ├── clerk/
│   │   │   │   └── route.ts
│   │   │   └── stripe/
│   │   │       └── route.ts
│   │   └── trpc/
│   │       └── [trpc]/
│   │           └── route.ts
│   ├── layout.tsx                # Root layout
│   ├── globals.css
│   └── not-found.tsx
│
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── users/                    # Feature: Users
│   │   ├── user-avatar.tsx
│   │   ├── user-card.tsx
│   │   └── index.ts
│   ├── projects/                 # Feature: Projects
│   │   ├── project-card.tsx
│   │   ├── project-form.tsx
│   │   └── index.ts
│   ├── layout/                   # Layout components
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── index.ts
│   └── providers/                # Context providers
│       ├── convex-provider.tsx
│       ├── theme-provider.tsx
│       └── index.ts
│
├── lib/
│   ├── utils.ts                  # cn() and general utilities
│   ├── constants.ts              # App-wide constants
│   ├── validations/              # Zod schemas
│   │   ├── user.ts
│   │   ├── project.ts
│   │   └── index.ts
│   └── hooks/                    # Shared hooks (not feature-specific)
│       ├── use-debounce.ts
│       ├── use-local-storage.ts
│       └── index.ts
│
├── convex/
│   ├── _generated/               # Auto-generated (gitignored)
│   ├── schema.ts                 # Database schema
│   ├── users.ts                  # User queries/mutations
│   ├── projects.ts               # Project queries/mutations
│   ├── http.ts                   # HTTP endpoints
│   └── lib/                      # Shared Convex utilities
│       ├── auth.ts               # Auth helpers
│       └── utils.ts
│
├── types/
│   ├── index.ts                  # Shared TypeScript types
│   └── globals.d.ts              # Global type declarations
│
├── public/
│   ├── images/
│   └── fonts/
│
└── config/
    ├── site.ts                   # Site metadata
    └── navigation.ts             # Navigation config
```

### Import Order

```typescript
// 1. React/Next.js
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

// 2. External packages
import { useQuery, useMutation } from "convex/react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// 3. Internal aliases (@/)
import { api } from "@/convex/_generated/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { userSchema } from "@/lib/validations/user";

// 4. Relative imports
import { UserAvatar } from "./user-avatar";
import type { UserProps } from "./types";
```

---

## 4. Convex Patterns

### Query vs Mutation Organization

```typescript
// convex/users.ts

import { v } from "convex/values";
import { query, mutation, internalMutation } from "./_generated/server";
import { getCurrentUser } from "./lib/auth";

// ═══════════════════════════════════════════════════════════════
// QUERIES
// ═══════════════════════════════════════════════════════════════

export const get = query({
  args: { id: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const getByEmail = query({
  args: { email: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.email))
      .unique();
  },
});

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("users").order("desc").collect();
  },
});

// ═══════════════════════════════════════════════════════════════
// MUTATIONS
// ═══════════════════════════════════════════════════════════════

export const create = mutation({
  args: {
    email: v.string(),
    name: v.string(),
    clerkId: v.string(),
  },
  handler: async (ctx, args) => {
    // Check for existing user
    const existing = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", args.clerkId))
      .unique();

    if (existing) {
      throw new Error("User already exists");
    }

    return await ctx.db.insert("users", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const update = mutation({
  args: {
    id: v.id("users"),
    name: v.optional(v.string()),
    email: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    await ctx.db.patch(id, updates);
  },
});

export const remove = mutation({
  args: { id: v.id("users") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// ═══════════════════════════════════════════════════════════════
// INTERNAL MUTATIONS (called by other Convex functions only)
// ═══════════════════════════════════════════════════════════════

export const internal_updateLastLogin = internalMutation({
  args: { id: v.id("users") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { lastLoginAt: Date.now() });
  },
});
```

### Pagination Patterns

```typescript
// convex/posts.ts

import { v } from "convex/values";
import { query } from "./_generated/server";
import { paginationOptsValidator } from "convex/server";

export const listPaginated = query({
  args: {
    paginationOpts: paginationOptsValidator,
    authorId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    let q = ctx.db.query("posts").order("desc");

    if (args.authorId) {
      q = ctx.db
        .query("posts")
        .withIndex("by_author", (q) => q.eq("authorId", args.authorId))
        .order("desc");
    }

    return await q.paginate(args.paginationOpts);
  },
});

// Client usage
"use client";

import { usePaginatedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export function PostList() {
  const { results, status, loadMore } = usePaginatedQuery(
    api.posts.listPaginated,
    { authorId: undefined },
    { initialNumItems: 10 }
  );

  return (
    <div>
      {results.map((post) => (
        <PostCard key={post._id} post={post} />
      ))}

      {status === "CanLoadMore" && (
        <Button onClick={() => loadMore(10)}>Load More</Button>
      )}

      {status === "LoadingMore" && <Spinner />}
    </div>
  );
}
```

### Real-time Subscription Patterns

```typescript
// ✅ Basic subscription
const posts = useQuery(api.posts.list);

// ✅ Conditional subscription (skip when no userId)
const user = useQuery(
  api.users.get,
  userId ? { id: userId } : "skip"
);

// ✅ Subscription with loading state
function UserProfile({ userId }: { userId: string }) {
  const user = useQuery(api.users.get, { id: userId });

  if (user === undefined) {
    return <Skeleton />;
  }

  if (user === null) {
    return <NotFound />;
  }

  return <ProfileCard user={user} />;
}

// ✅ Multiple subscriptions
function Dashboard() {
  const user = useQuery(api.users.getCurrent);
  const projects = useQuery(api.projects.listByUser, 
    user ? { userId: user._id } : "skip"
  );
  const notifications = useQuery(api.notifications.listUnread,
    user ? { userId: user._id } : "skip"
  );

  // All update in real-time automatically
}
```

### Error Handling in Convex

```typescript
// convex/lib/errors.ts

export class ConvexError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = "ConvexError";
  }
}

export const Errors = {
  NOT_FOUND: (resource: string) =>
    new ConvexError(`${resource} not found`, "NOT_FOUND", 404),
  UNAUTHORIZED: () =>
    new ConvexError("Unauthorized", "UNAUTHORIZED", 401),
  FORBIDDEN: () =>
    new ConvexError("Forbidden", "FORBIDDEN", 403),
  VALIDATION: (message: string) =>
    new ConvexError(message, "VALIDATION_ERROR", 400),
} as const;

// Usage in mutations
export const update = mutation({
  args: { id: v.id("posts"), title: v.string() },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) {
      throw Errors.UNAUTHORIZED();
    }

    const post = await ctx.db.get(args.id);
    if (!post) {
      throw Errors.NOT_FOUND("Post");
    }

    if (post.authorId !== user._id) {
      throw Errors.FORBIDDEN();
    }

    await ctx.db.patch(args.id, { title: args.title });
  },
});

// Client-side handling
const updatePost = useMutation(api.posts.update);

async function handleUpdate(data: UpdatePostInput) {
  try {
    await updatePost(data);
    toast.success("Post updated");
  } catch (error) {
    if (error instanceof Error) {
      toast.error(error.message);
    }
  }
}
```

---

## 5. Component Standards

### Props Interface Naming

```typescript
// ✅ Component props: {ComponentName}Props
interface ButtonProps {
  variant?: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

// ✅ For extending HTML elements
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
}

// ✅ For extending other components
interface IconButtonProps extends ButtonProps {
  icon: React.ReactNode;
}
```

### Default Props

```typescript
// ✅ Use default parameters (not defaultProps)
interface CardProps {
  title: string;
  variant?: "default" | "outlined";
  padding?: "none" | "sm" | "md" | "lg";
}

function Card({
  title,
  variant = "default",
  padding = "md",
}: CardProps) {
  return (
    <div className={cn(variantStyles[variant], paddingStyles[padding])}>
      <h3>{title}</h3>
    </div>
  );
}

// ✅ With destructuring and rest props
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

function Button({
  variant = "primary",
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant }), className)}
      {...props}
    >
      {children}
    </button>
  );
}
```

### Forwarding Refs

```typescript
import { forwardRef } from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && <label className="text-sm font-medium">{label}</label>}
        <input
          ref={ref}
          className={cn(
            "flex h-10 w-full rounded-md border px-3 py-2",
            error && "border-red-500",
            className
          )}
          {...props}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export { Input };
```

### Composition Patterns

```typescript
// ✅ Compound components pattern
import { createContext, useContext } from "react";

interface CardContextValue {
  variant: "default" | "outlined";
}

const CardContext = createContext<CardContextValue | null>(null);

function useCard() {
  const context = useContext(CardContext);
  if (!context) {
    throw new Error("Card components must be used within a Card");
  }
  return context;
}

interface CardProps {
  variant?: "default" | "outlined";
  children: React.ReactNode;
}

function Card({ variant = "default", children }: CardProps) {
  return (
    <CardContext.Provider value={{ variant }}>
      <div className={cn(cardVariants({ variant }))}>{children}</div>
    </CardContext.Provider>
  );
}

function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="p-4 border-b">{children}</div>;
}

function CardContent({ children }: { children: React.ReactNode }) {
  return <div className="p-4">{children}</div>;
}

function CardFooter({ children }: { children: React.ReactNode }) {
  return <div className="p-4 border-t">{children}</div>;
}

// Attach sub-components
Card.Header = CardHeader;
Card.Content = CardContent;
Card.Footer = CardFooter;

export { Card };

// Usage
<Card variant="outlined">
  <Card.Header>Title</Card.Header>
  <Card.Content>Body content</Card.Content>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

```typescript
// ✅ Render props pattern (when needed)
interface DataLoaderProps<T> {
  query: () => T | undefined;
  loading: React.ReactNode;
  error?: React.ReactNode;
  children: (data: T) => React.ReactNode;
}

function DataLoader<T>({
  query,
  loading,
  error,
  children,
}: DataLoaderProps<T>) {
  const data = query();

  if (data === undefined) {
    return <>{loading}</>;
  }

  if (data === null && error) {
    return <>{error}</>;
  }

  return <>{children(data as T)}</>;
}

// Usage
<DataLoader
  query={() => useQuery(api.users.get, { id })}
  loading={<Skeleton />}
  error={<NotFound />}
>
  {(user) => <UserProfile user={user} />}
</DataLoader>
```

```typescript
// ✅ Slot pattern (using Radix Slot)
import { Slot } from "@radix-ui/react-slot";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

function Button({ asChild, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return <Comp {...props} />;
}

// Usage - renders as <a> with button styles
<Button asChild>
  <a href="/home">Go Home</a>
</Button>
```

---

## 6. Error Handling

### Try/Catch Patterns

```typescript
// ✅ Async function error handling
async function handleSubmit(data: FormData) {
  try {
    await createUser(data);
    toast.success("User created successfully");
    router.push("/users");
  } catch (error) {
    if (error instanceof ConvexError) {
      // Known error types
      switch (error.code) {
        case "VALIDATION_ERROR":
          toast.error(error.message);
          break;
        case "UNAUTHORIZED":
          router.push("/sign-in");
          break;
        default:
          toast.error("An error occurred");
      }
    } else {
      // Unknown errors - log to Sentry
      Sentry.captureException(error);
      toast.error("Something went wrong. Please try again.");
    }
  }
}

// ✅ Query error handling
function UserProfile({ userId }: { userId: string }) {
  const user = useQuery(api.users.get, { id: userId });

  // undefined = loading
  if (user === undefined) {
    return <ProfileSkeleton />;
  }

  // null = not found
  if (user === null) {
    return <NotFound message="User not found" />;
  }

  return <Profile user={user} />;
}
```

### Error Boundaries

```typescript
// components/error-boundary.tsx
"use client";

import { Component, type ReactNode } from "react";
import * as Sentry from "@sentry/nextjs";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    Sentry.captureException(error, { extra: { errorInfo } });
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex flex-col items-center justify-center p-8">
            <h2 className="text-xl font-semibold">Something went wrong</h2>
            <p className="text-muted-foreground mt-2">
              We've been notified and are working on a fix.
            </p>
            <Button
              className="mt-4"
              onClick={() => this.setState({ hasError: false })}
            >
              Try again
            </Button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}

// app/error.tsx (Next.js error boundary)
"use client";

import { useEffect } from "react";
import * as Sentry from "@sentry/nextjs";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <Button onClick={reset} className="mt-4">
        Try again
      </Button>
    </div>
  );
}
```

### Toast Notifications

```typescript
// lib/toast.ts
import { toast as sonnerToast } from "sonner";

export const toast = {
  success: (message: string) => {
    sonnerToast.success(message);
  },
  error: (message: string) => {
    sonnerToast.error(message);
  },
  warning: (message: string) => {
    sonnerToast.warning(message);
  },
  info: (message: string) => {
    sonnerToast.info(message);
  },
  promise: <T>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: string;
      error: string;
    }
  ) => {
    return sonnerToast.promise(promise, messages);
  },
};

// Usage
import { toast } from "@/lib/toast";

async function handleDelete() {
  toast.promise(deleteUser(userId), {
    loading: "Deleting user...",
    success: "User deleted",
    error: "Failed to delete user",
  });
}
```

### Sentry Integration

```typescript
// sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration(),
  ],
  // Filter out noisy errors
  ignoreErrors: [
    "ResizeObserver loop limit exceeded",
    "Non-Error promise rejection",
  ],
});

// Manual error capture
try {
  riskyOperation();
} catch (error) {
  Sentry.captureException(error, {
    tags: { feature: "checkout" },
    extra: { userId, cartItems },
  });
}

// Add user context
Sentry.setUser({
  id: user.id,
  email: user.email,
});
```

---

## 7. Testing Standards

### Unit Test Patterns

```typescript
// __tests__/lib/utils.test.ts
import { describe, it, expect } from "vitest";
import { cn, formatDate, formatCurrency } from "@/lib/utils";

describe("cn", () => {
  it("merges class names correctly", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", true && "visible")).toBe(
      "base visible"
    );
  });

  it("resolves Tailwind conflicts", () => {
    expect(cn("px-4", "px-6")).toBe("px-6");
  });
});

describe("formatDate", () => {
  it("formats dates correctly", () => {
    const date = new Date("2024-01-15");
    expect(formatDate(date)).toBe("January 15, 2024");
  });

  it("handles invalid dates", () => {
    expect(formatDate(null)).toBe("");
  });
});
```

```typescript
// __tests__/components/button.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders children correctly", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByText("Disabled")).toBeDisabled();
  });

  it("applies variant classes correctly", () => {
    render(<Button variant="destructive">Delete</Button>);
    expect(screen.getByText("Delete")).toHaveClass("bg-destructive");
  });
});
```

### Integration Test Patterns

```typescript
// __tests__/features/auth/sign-in.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { SignInForm } from "@/components/auth/sign-in-form";

// Mock Clerk
vi.mock("@clerk/nextjs", () => ({
  useSignIn: () => ({
    signIn: {
      create: vi.fn().mockResolvedValue({ status: "complete" }),
    },
    isLoaded: true,
  }),
}));

describe("SignInForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("submits form with valid credentials", async () => {
    const user = userEvent.setup();
    render(<SignInForm />);

    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.queryByText(/invalid/i)).not.toBeInTheDocument();
    });
  });

  it("shows validation errors for empty fields", async () => {
    const user = userEvent.setup();
    render(<SignInForm />);

    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });
  });
});
```

```typescript
// __tests__/convex/users.test.ts
import { convexTest } from "convex-test";
import { describe, it, expect, beforeEach } from "vitest";
import { api } from "@/convex/_generated/api";
import schema from "@/convex/schema";

describe("users", () => {
  const t = convexTest(schema);

  beforeEach(async () => {
    // Reset database state
  });

  it("creates a user", async () => {
    const userId = await t.mutation(api.users.create, {
      email: "test@example.com",
      name: "Test User",
      clerkId: "clerk_123",
    });

    expect(userId).toBeDefined();

    const user = await t.query(api.users.get, { id: userId });
    expect(user?.email).toBe("test@example.com");
  });

  it("prevents duplicate emails", async () => {
    await t.mutation(api.users.create, {
      email: "test@example.com",
      name: "User 1",
      clerkId: "clerk_1",
    });

    await expect(
      t.mutation(api.users.create, {
        email: "test@example.com",
        name: "User 2",
        clerkId: "clerk_2",
      })
    ).rejects.toThrow();
  });
});
```

### E2E Considerations

```typescript
// e2e/auth.spec.ts (Playwright)
import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("user can sign in", async ({ page }) => {
    await page.goto("/sign-in");

    await page.fill('input[name="email"]', "test@example.com");
    await page.fill('input[name="password"]', "password123");
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("h1")).toContainText("Dashboard");
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.goto("/sign-in");

    await page.fill('input[name="email"]', "wrong@example.com");
    await page.fill('input[name="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    await expect(page.locator(".error-message")).toBeVisible();
  });
});

// e2e/fixtures.ts
import { test as base } from "@playwright/test";

type Fixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Set up auth state
    await page.goto("/sign-in");
    await page.fill('input[name="email"]', process.env.TEST_USER_EMAIL!);
    await page.fill('input[name="password"]', process.env.TEST_USER_PASSWORD!);
    await page.click('button[type="submit"]');
    await page.waitForURL("/dashboard");

    await use(page);
  },
});
```

---

## 8. Git Conventions

### Commit Message Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

#### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, semicolons, etc. |
| `refactor` | Code change that neither fixes nor adds |
| `perf` | Performance improvement |
| `test` | Adding tests |
| `chore` | Maintenance, deps, config |
| `ci` | CI/CD changes |

#### Examples

```bash
feat(auth): add OAuth2 Google sign-in

fix(api): handle null response from Stripe webhook

docs(readme): update installation instructions

refactor(users): extract validation logic to shared util

chore(deps): upgrade Next.js to 16.1

feat(dashboard): add project analytics chart

Closes #123
```

### Branch Naming

```
<type>/<ticket-id>-<short-description>
```

#### Examples

```
feat/UC-123-oauth-google
fix/UC-456-webhook-null-handling
refactor/UC-789-user-validation
chore/deps-nextjs-16
hotfix/prod-login-crash
```

#### Branch Types

| Prefix | Purpose |
|--------|---------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `refactor/` | Code refactoring |
| `chore/` | Maintenance tasks |
| `hotfix/` | Production emergency fixes |
| `docs/` | Documentation updates |
| `test/` | Test additions/updates |

### PR Templates

```markdown
<!-- .github/pull_request_template.md -->

## Summary

<!-- Brief description of changes -->

## Type of Change

- [ ] 🚀 Feature
- [ ] 🐛 Bug fix
- [ ] 📝 Documentation
- [ ] 🔧 Refactor
- [ ] ✅ Tests
- [ ] 🔒 Security

## Related Issues

<!-- Link issues: Closes #123, Fixes #456 -->

## Changes Made

- 
- 
- 

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots

<!-- If applicable -->

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No console.logs or debug code
- [ ] TypeScript types are correct
```

### Graphite Workflow

```bash
# Create feature branch from trunk
gt create feat/UC-123-new-feature

# Make changes and commit
git add -A
gt modify -m "feat(scope): description"

# Submit PR
gt submit

# After review, merge
gt merge

# Sync with trunk
gt sync
```

---

## Quick Reference

### File Naming Cheat Sheet

```
components/users/user-avatar.tsx    # Component
lib/hooks/use-user.ts               # Hook
lib/utils/format-date.ts            # Utility
lib/validations/user.ts             # Zod schema
convex/users.ts                     # Convex functions
types/user.ts                       # Types
```

### Import Template

```typescript
// React/Next
import { useState } from "react";
import { useRouter } from "next/navigation";

// External
import { useQuery } from "convex/react";
import { z } from "zod";

// Internal (@/)
import { api } from "@/convex/_generated/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Relative
import { UserCard } from "./user-card";
```

### Component Template

```typescript
"use client";

import { forwardRef } from "react";
import { cn } from "@/lib/utils";

interface ComponentProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outlined";
}

const Component = forwardRef<HTMLDivElement, ComponentProps>(
  ({ variant = "default", className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(variants[variant], className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Component.displayName = "Component";

export { Component };
export type { ComponentProps };
```

---

*Last updated: 2026-02-07*
