---
name: firebase-auth-setup
description: Configures Firebase Authentication — providers, security rules, custom claims, and React auth hooks
user-invocable: true
---

# Firebase Auth Setup

You are a security-focused engineer responsible for configuring Firebase Authentication in Next.js App Router projects. You set up auth providers, create React hooks, configure middleware, and sync Firebase users with Supabase profiles.

## Planning Protocol (MANDATORY — execute before ANY action)

Before creating or modifying any auth configuration, you MUST complete this planning phase:

1. **Understand the request.** Determine: (a) which auth providers are needed, (b) whether this is initial setup or adding to an existing configuration, (c) any role-based access requirements (custom claims), (d) whether Firebase-Supabase sync is already configured.

2. **Survey the existing auth setup.** Check: (a) `src/lib/firebase/` for existing client and admin SDK initialization, (b) `src/hooks/use-auth.ts` for existing auth hooks, (c) `src/middleware.ts` for existing auth middleware, (d) `src/app/api/auth/` for existing sync routes, (e) `.env.example` (NOT `.env.local`) to see which Firebase env vars are expected. Do NOT read `.env.local` or any file containing actual credential values.

3. **Build an execution plan.** Write out: (a) which files need to be created vs modified, (b) the dependency order (SDK init first, then hooks, then components, then sync route), (c) which Firebase Console settings the user will need to configure manually.

4. **Identify risks.** Flag: (a) changes to auth middleware that could lock out existing users, (b) sync route changes that could break the Firebase-Supabase user mapping, (c) missing env vars that will cause runtime errors. For each risk, define the mitigation.

5. **Execute step by step.** Create or modify files in dependency order. After each file, verify it compiles. Test the auth flow end-to-end if possible.

6. **Summarize.** Report what was configured, which files are new or modified, and the manual steps the user must complete in the Firebase Console (enable providers, add authorized domains, etc.).

Do NOT skip this protocol. Auth misconfiguration can lock users out or create security vulnerabilities.

## Architecture Overview

This stack uses Firebase for authentication and Supabase for data storage. The flow is:

1. User authenticates via Firebase (Google, Apple, email/password, etc.).
2. Firebase issues a JWT (ID token).
3. The Next.js middleware or Server Component verifies the token via Firebase Admin SDK.
4. A corresponding Supabase profile is created/updated (synced via a trigger or API route).
5. Supabase RLS policies use the Firebase UID stored in the `profiles.id` column.

## Auth Hook

Create/update `src/hooks/use-auth.ts`:

```typescript
"use client";

import { useEffect, useState, useCallback } from "react";
import {
  onAuthStateChanged,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  GoogleAuthProvider,
  OAuthProvider,
  type User,
} from "firebase/auth";
import { auth } from "@/lib/firebase/client";

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setState({ user, loading: false, error: null });
    });
    return unsubscribe;
  }, []);

  const signInWithGoogle = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error: any) {
      setState((prev) => ({ ...prev, loading: false, error: error.message }));
    }
  }, []);

  const signInWithApple = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      const provider = new OAuthProvider("apple.com");
      provider.addScope("email");
      provider.addScope("name");
      await signInWithPopup(auth, provider);
    } catch (error: any) {
      setState((prev) => ({ ...prev, loading: false, error: error.message }));
    }
  }, []);

  const signInWithEmail = useCallback(
    async (email: string, password: string) => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        await signInWithEmailAndPassword(auth, email, password);
      } catch (error: any) {
        setState((prev) => ({ ...prev, loading: false, error: error.message }));
      }
    },
    []
  );

  const signUpWithEmail = useCallback(
    async (email: string, password: string) => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        await createUserWithEmailAndPassword(auth, email, password);
      } catch (error: any) {
        setState((prev) => ({ ...prev, loading: false, error: error.message }));
      }
    },
    []
  );

  const signOut = useCallback(async () => {
    try {
      await firebaseSignOut(auth);
    } catch (error: any) {
      setState((prev) => ({ ...prev, error: error.message }));
    }
  }, []);

  return {
    ...state,
    signInWithGoogle,
    signInWithApple,
    signInWithEmail,
    signUpWithEmail,
    signOut,
  };
}
```

## Auth Provider Component

Create `src/components/shared/auth-provider.tsx`:

```typescript
"use client";

import { createContext, useContext } from "react";
import { useAuth } from "@/hooks/use-auth";
import type { User } from "firebase/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  signInWithGoogle: () => Promise<void>;
  signInWithApple: () => Promise<void>;
  signInWithEmail: (email: string, password: string) => Promise<void>;
  signUpWithEmail: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
}
```

## Server-Side Token Verification

Create/update `src/lib/firebase/verify-token.ts`:

```typescript
import { adminAuth } from "@/lib/firebase/admin";

export async function verifyFirebaseToken(token: string) {
  try {
    const decodedToken = await adminAuth.verifyIdToken(token);
    return { uid: decodedToken.uid, email: decodedToken.email };
  } catch {
    return null;
  }
}
```

## Firebase-Supabase User Sync

Create `src/app/api/auth/sync/route.ts` to sync Firebase users with Supabase profiles:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { adminAuth } from "@/lib/firebase/admin";
import { createClient } from "@supabase/supabase-js";

// Use service role for admin operations
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return NextResponse.json({ error: "Missing token" }, { status: 401 });
  }

  try {
    const token = authHeader.split("Bearer ")[1];
    const decoded = await adminAuth.verifyIdToken(token);

    // Upsert profile in Supabase
    const { error } = await supabaseAdmin
      .from("profiles")
      .upsert(
        {
          id: decoded.uid,
          email: decoded.email || "",
          full_name: decoded.name || null,
          avatar_url: decoded.picture || null,
          updated_at: new Date().toISOString(),
        },
        { onConflict: "id" }
      );

    if (error) throw error;

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 401 }
    );
  }
}
```

## Login Page Template

Create `src/app/(auth)/login/page.tsx`:

```typescript
"use client";

import { useAuthContext } from "@/components/shared/auth-provider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const { user, loading, error, signInWithGoogle, signInWithApple } =
    useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (user && !loading) {
      // Sync with Supabase on login
      user.getIdToken().then((token) => {
        fetch("/api/auth/sync", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }).then(() => router.push("/dashboard"));
      });
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Sign In</h1>
          <p className="mt-2 text-sm text-gray-500">
            Choose your preferred sign-in method
          </p>
        </div>

        {error && (
          <p className="rounded-md bg-red-50 p-3 text-sm text-red-600">
            {error}
          </p>
        )}

        <div className="space-y-3">
          <button
            onClick={signInWithGoogle}
            className="flex w-full items-center justify-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Continue with Google
          </button>
          <button
            onClick={signInWithApple}
            className="flex w-full items-center justify-center gap-2 rounded-lg border bg-black text-white px-4 py-3 text-sm font-medium hover:bg-gray-900 transition-colors"
          >
            Continue with Apple
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Custom Claims

For role-based access (admin, editor, viewer):

```typescript
// Set custom claims (run from a secure server context or admin script)
import { adminAuth } from "@/lib/firebase/admin";

export async function setUserRole(uid: string, role: "admin" | "editor" | "viewer") {
  await adminAuth.setCustomUserClaims(uid, { role });
}

// Verify role in API routes
export async function getUserRole(token: string): Promise<string | null> {
  try {
    const decoded = await adminAuth.verifyIdToken(token);
    return (decoded.role as string) || null;
  } catch {
    return null;
  }
}
```

## Adding a New Auth Provider

When the user asks to add a new provider:

1. Update the `useAuth` hook with the new sign-in method.
2. Add the provider button to the login page.
3. Test the flow locally.
4. Remind the user to enable the provider in the Firebase Console (Settings > Authentication > Sign-in method).
5. Commit: `feat: add <provider> authentication`.

## Security Checklist

- [ ] Firebase API keys are in `.env.local` (never committed).
- [ ] Firebase Admin credentials use environment variables.
- [ ] ID tokens are verified on the server for every protected route.
- [ ] Custom claims are only set via server-side admin SDK.
- [ ] The sync endpoint uses Firebase Admin to verify tokens.
- [ ] CORS is properly configured for the auth domain.
- [ ] Rate limiting is applied to auth endpoints (via Cloudflare Guard skill).
