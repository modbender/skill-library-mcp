# Authentication — NextJS

## Auth.js / NextAuth.js Setup

### Installation
```bash
npm install next-auth@beta
```

### Configuration
```typescript
// auth.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID,
      clientSecret: process.env.AUTH_GITHUB_SECRET,
    }),
    Google({
      clientId: process.env.AUTH_GOOGLE_ID,
      clientSecret: process.env.AUTH_GOOGLE_SECRET,
    }),
    Credentials({
      credentials: {
        email: { label: 'Email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const user = await getUserByEmail(credentials.email)
        if (!user || !verifyPassword(credentials.password, user.password)) {
          return null
        }
        return { id: user.id, email: user.email, name: user.name }
      },
    }),
  ],
  callbacks: {
    authorized({ auth, request }) {
      const isLoggedIn = !!auth?.user
      const isProtected = request.nextUrl.pathname.startsWith('/dashboard')
      if (isProtected && !isLoggedIn) {
        return false // Redirect to login
      }
      return true
    },
    jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    session({ session, token }) {
      session.user.id = token.id as string
      return session
    },
  },
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
})
```

### Route Handler
```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'
export const { GET, POST } = handlers
```

## Middleware Protection

```typescript
// middleware.ts
import { auth } from '@/auth'

export default auth((req) => {
  const isLoggedIn = !!req.auth
  const isAuthPage = req.nextUrl.pathname.startsWith('/login')
  const isProtected = req.nextUrl.pathname.startsWith('/dashboard')
  
  // Redirect logged-in users away from auth pages
  if (isAuthPage && isLoggedIn) {
    return Response.redirect(new URL('/dashboard', req.url))
  }
  
  // Redirect unauthenticated users to login
  if (isProtected && !isLoggedIn) {
    const callbackUrl = encodeURIComponent(req.nextUrl.pathname)
    return Response.redirect(new URL(`/login?callbackUrl=${callbackUrl}`, req.url))
  }
})

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register'],
}
```

## Server Components

```typescript
// Get session in Server Component
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await auth()
  
  if (!session) {
    redirect('/login')
  }
  
  return (
    <div>
      <h1>Welcome, {session.user?.name}</h1>
      <p>Email: {session.user?.email}</p>
    </div>
  )
}
```

## Client Components

```typescript
// app/providers.tsx
'use client'
import { SessionProvider } from 'next-auth/react'

export function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>
}

// app/layout.tsx
import { Providers } from './providers'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

// components/user-nav.tsx
'use client'
import { useSession, signIn, signOut } from 'next-auth/react'

export function UserNav() {
  const { data: session, status } = useSession()
  
  if (status === 'loading') {
    return <div>Loading...</div>
  }
  
  if (!session) {
    return <button onClick={() => signIn()}>Sign In</button>
  }
  
  return (
    <div>
      <span>{session.user?.name}</span>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  )
}
```

## Sign In/Out Forms

```typescript
// components/login-form.tsx
'use client'
import { signIn } from 'next-auth/react'
import { useSearchParams } from 'next/navigation'

export function LoginForm() {
  const searchParams = useSearchParams()
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard'
  
  return (
    <div>
      <button onClick={() => signIn('github', { callbackUrl })}>
        Sign in with GitHub
      </button>
      <button onClick={() => signIn('google', { callbackUrl })}>
        Sign in with Google
      </button>
      
      {/* Credentials form */}
      <form action={async (formData) => {
        await signIn('credentials', {
          email: formData.get('email'),
          password: formData.get('password'),
          callbackUrl,
        })
      }}>
        <input name="email" type="email" required />
        <input name="password" type="password" required />
        <button type="submit">Sign In</button>
      </form>
    </div>
  )
}
```

## Database Adapter (Prisma)

```typescript
// auth.ts with Prisma adapter
import { PrismaAdapter } from '@auth/prisma-adapter'
import { prisma } from '@/lib/prisma'

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [...],
  session: {
    strategy: 'jwt', // or 'database' for database sessions
  },
})
```

## Role-Based Access

```typescript
// Extend types
declare module 'next-auth' {
  interface User {
    role: 'admin' | 'user'
  }
  interface Session {
    user: User & { id: string }
  }
}

// Check role in Server Component
export default async function AdminPage() {
  const session = await auth()
  
  if (session?.user?.role !== 'admin') {
    redirect('/unauthorized')
  }
  
  return <AdminDashboard />
}

// Check role in middleware
export default auth((req) => {
  if (req.nextUrl.pathname.startsWith('/admin')) {
    if (req.auth?.user?.role !== 'admin') {
      return Response.redirect(new URL('/unauthorized', req.url))
    }
  }
})
```

## Common Patterns

### Protected API Route
```typescript
// app/api/protected/route.ts
import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export async function GET() {
  const session = await auth()
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  return NextResponse.json({ data: 'Protected data' })
}
```

### Protected Server Action
```typescript
'use server'
import { auth } from '@/auth'

export async function updateProfile(formData: FormData) {
  const session = await auth()
  
  if (!session?.user?.id) {
    throw new Error('Unauthorized')
  }
  
  await db.user.update({
    where: { id: session.user.id },
    data: { name: formData.get('name') },
  })
}
```
