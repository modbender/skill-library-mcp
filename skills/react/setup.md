# React Setup

First-time setup for the React skill.

## Step 1: Create Workspace

```bash
mkdir -p ~/react
```

## Step 2: Initialize Memory

Copy the template to your memory file:

```bash
cp memory-template.md ~/react/memory.md
```

## Step 3: Verify Setup

The skill is ready when `~/react/memory.md` exists.

## Project Structure

For new React projects, use this structure:

```
src/
├── app/                 # Routes (Next.js App Router)
├── features/            # Feature modules
│   └── [feature]/
│       ├── components/  # Feature components
│       ├── hooks/       # Feature hooks
│       ├── api/         # API calls + types
│       └── index.ts     # Public exports
├── shared/              # Cross-feature code
│   ├── components/ui/   # Primitives (Button, Input)
│   └── hooks/           # Shared hooks
└── providers/           # Context providers
```

## Recommended Stack

| Layer | Tool | Why |
|-------|------|-----|
| Framework | Next.js 15 | SSR, App Router, Server Actions |
| Styling | Tailwind CSS | Utility-first, fast |
| Components | shadcn/ui | Accessible, customizable |
| Server state | TanStack Query | Caching, sync, devtools |
| Client state | Zustand | Simple, tiny, selectors |
| Forms | React Hook Form + Zod | Validation, performance |
| Testing | Vitest + Testing Library | Fast, user-centric |

## TypeScript Config

Enable strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

## Common Commands

```bash
# Next.js
npx create-next-app@latest my-app --typescript --tailwind --app

# Vite (SPA)
npm create vite@latest my-app -- --template react-ts

# Add shadcn/ui
npx shadcn@latest init

# Add TanStack Query
npm install @tanstack/react-query

# Add Zustand
npm install zustand

# Add React Hook Form + Zod
npm install react-hook-form zod @hookform/resolvers
```
