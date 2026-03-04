# Stack & Tooling — Frontend

## Recommended Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Framework | Next.js 14+ | RSC, file routing, Vercel deploy |
| Language | TypeScript | Catch errors early, better DX |
| Styling | Tailwind CSS | Utility-first, design tokens built-in |
| Components | shadcn/ui | Accessible, customizable, not a dependency |
| Animation | Framer Motion | Declarative, performant |
| Forms | React Hook Form + Zod | Type-safe validation |
| State | Zustand or Jotai | Simple, no boilerplate |

## Project Structure

```
src/
├── app/                 # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   └── [feature]/
├── components/
│   ├── ui/              # shadcn/ui components
│   └── [feature]/
├── lib/
│   ├── utils.ts         # cn(), formatters
│   └── api.ts
├── hooks/
├── styles/
│   └── globals.css
└── config/
    └── site.ts
```

## Essential Utils

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## shadcn/ui Setup

```bash
npx shadcn@latest init
npx shadcn@latest add button card dialog
```

Most used: Button, Card, Dialog, Accordion, Tabs, Sheet, NavigationMenu.
