---
name: stack-scaffold
description: Scaffolds a full-stack project with Next.js App Router, Supabase, Firebase Auth, Vercel, and Cloudflare
user-invocable: true
---

# Stack Scaffold

You are an expert full-stack developer. When the user asks to create a new project, scaffold the complete structure following the conventions below. Always confirm the project name and target directory with the user before creating files. This skill only creates new files in empty or new directories — it never reads or modifies existing .env, .env.local, or credential files.

## Planning Protocol (MANDATORY — execute before ANY action)

Before writing a single file or running any command, you MUST complete this planning phase:

1. **Understand the request.** Restate what the user wants in your own words. Identify any ambiguities. If the request is vague (e.g., "create a project"), ask one round of clarifying questions (project name, purpose, any specific requirements).

2. **Survey the environment.** Check the current directory structure and installed tools. Run `ls` and `node -v` to confirm the target directory is empty or does not exist yet. Do NOT read, open, or inspect any `.env`, `.env.local`, or credential files. This skill only creates new projects — if the directory already contains a project, ask the user to confirm before proceeding.

3. **Build an execution plan.** Write out the numbered list of steps you will take, including file paths you will create or modify, commands you will run, and the expected outcome of each step. Present this plan to yourself (in your reasoning) before executing.

4. **Identify risks.** Note any step that could fail or cause data loss (overwriting files, dropping tables, force-pushing). For each risk, define the mitigation (backup, dry-run, confirmation).

5. **Execute sequentially.** Follow the plan step by step. After each step, verify it succeeded before moving to the next. If a step fails, diagnose the issue, update the plan, and continue.

6. **Summarize.** After completing all steps, provide a concise summary of what was created, what was modified, and any manual steps the user still needs to take.

Do NOT skip this protocol. Rushing to execute without planning leads to errors, broken state, and wasted time.

## Project Initialization

1. Run `npx create-next-app@latest <project-name> --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"` to create the Next.js project with App Router.
2. `cd` into the project directory.
3. Ensure `.gitignore` exists and includes at minimum: `.env`, `.env.local`, `.env*.local`, `node_modules/`, `.next/`. The `create-next-app` template already includes these, but verify before any commit.
4. Initialize git: `git init && git add -A && git commit -m "chore: initial Next.js scaffold"`.

## Dependencies

Install the following in a single command:

```bash
npm install @supabase/supabase-js @supabase/ssr firebase firebase-admin zod zustand next-themes
npm install -D @types/node vitest @vitejs/plugin-react playwright @playwright/test prettier eslint-config-prettier
```

## Directory Structure

Create this structure inside `src/`:

```
src/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/
│   │   └── page.tsx
│   ├── api/
│   │   └── health/route.ts
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── ui/           # Reusable UI primitives
│   └── shared/       # Shared composite components
├── lib/
│   ├── supabase/
│   │   ├── client.ts       # Browser Supabase client
│   │   ├── server.ts       # Server Supabase client (cookies-based)
│   │   ├── middleware.ts    # Auth refresh middleware helper
│   │   └── types.ts        # Generated DB types (placeholder)
│   ├── firebase/
│   │   ├── client.ts       # Firebase client SDK init
│   │   └── admin.ts        # Firebase Admin SDK init (server-only)
│   └── utils.ts
├── hooks/
│   └── use-auth.ts         # Auth state hook
├── stores/
│   └── user-store.ts       # Zustand user store
├── types/
│   └── index.ts
└── middleware.ts            # Next.js middleware for auth
```

## File Contents

### `src/lib/supabase/client.ts`
```typescript
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

### `src/lib/supabase/server.ts`
```typescript
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createClient() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Called from Server Component — ignore
          }
        },
      },
    }
  );
}
```

### `src/lib/firebase/client.ts`
```typescript
import { initializeApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
export const auth = getAuth(app);
```

### `src/lib/firebase/admin.ts`
```typescript
import { initializeApp, getApps, cert } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

if (getApps().length === 0) {
  initializeApp({
    credential: cert({
      projectId: process.env.FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
    }),
  });
}

export const adminAuth = getAuth();
```

### `src/middleware.ts`
```typescript
import { type NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  await supabase.auth.getUser();

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
```

### `src/app/api/health/route.ts`
```typescript
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ status: "ok", timestamp: new Date().toISOString() });
}
```

### `.env.example`
```
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Firebase Client
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=

# Firebase Admin (server-only)
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### `vercel.json`
```json
{
  "framework": "nextjs",
  "regions": ["gru1"],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store" }
      ]
    }
  ]
}
```

### `vitest.config.ts`
```typescript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/tests/setup.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
```

## Post-Scaffold Steps

1. Copy `.env.example` to `.env.local` and remind the user to fill in the values.
2. Create an initial Supabase migration file at `supabase/migrations/00000000000000_init.sql` with a `profiles` table:

```sql
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  email text not null,
  full_name text,
  avatar_url text,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

alter table public.profiles enable row level security;

create policy "Users can view own profile" on public.profiles
  for select using (auth.uid() = id);

create policy "Users can update own profile" on public.profiles
  for update using (auth.uid() = id);
```

3. Add scripts to `package.json`:
```json
{
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write .",
    "test": "vitest",
    "test:e2e": "playwright test",
    "types:supabase": "npx supabase gen types typescript --local > src/lib/supabase/types.ts"
  }
}
```

4. Commit: `git add -A && git commit -m "chore: add full stack scaffold with Supabase, Firebase Auth, Vercel config"`.

5. Print a summary of what was created and what the user needs to configure manually (env vars, Supabase project, Firebase project, Vercel project link, Cloudflare DNS).
