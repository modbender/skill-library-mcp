---
name: afrexai-react-production
description: Complete methodology for building production-grade React applications with architecture decisions, component design, state management, performance optimization, testing, and deployment.
---

# React Production Engineering

Complete methodology for building production-grade React applications. Covers architecture decisions, component design, state management, performance optimization, testing, and deployment — not just API reference, but engineering methodology with decision frameworks, templates, and scoring systems.

## Phase 1: Architecture Assessment

### Quick Health Check (score /16)
- [ ] Component tree depth < 6 levels (+2)
- [ ] No prop drilling past 2 levels (+2)
- [ ] Bundle size < 200KB gzipped (+2)
- [ ] LCP < 2.5s on 4G (+2)
- [ ] Test coverage > 70% on business logic (+2)
- [ ] Zero `any` types in production code (+2)
- [ ] No direct DOM manipulation (+2)
- [ ] Consistent error boundaries (+2)

### Architecture Brief

```yaml
project:
  name: ""
  type: "" # spa | ssr | hybrid | static
  framework: "" # next | remix | vite-spa | astro
  scale: "" # small (<20 routes) | medium (20-100) | large (100+)
  team_size: "" # solo | small (2-5) | medium (6-15) | large (15+)
current_state:
  react_version: "" # 18 | 19
  typescript: true
  router: "" # react-router | next-app | tanstack-router
  state_management: "" # useState | zustand | jotai | redux | tanstack-query
  styling: "" # tailwind | css-modules | styled-components | vanilla-extract
  testing: "" # vitest | jest | playwright | cypress
  ci_cd: "" # github-actions | gitlab-ci | vercel
pain_points: []
goals: []
```

### Framework Selection Decision Matrix

| Factor | Vite SPA | Next.js | Remix | Astro |
|--------|----------|---------|-------|-------|
| SEO needed | ❌ | ✅ Best | ✅ Good | ✅ Best |
| Dashboard/app | ✅ Best | ✅ Good | ✅ Good | ❌ |
| Content-heavy | ❌ | ✅ Good | ✅ Good | ✅ Best |
| Team familiarity | ✅ Simple | ⚠️ Learning curve | ⚠️ Web standards | ⚠️ Islands |
| Deployment | Anywhere | Vercel optimal | Anywhere | Anywhere |
| Bundle size | You control | Framework overhead | Smaller | Minimal JS |

**Decision rules:**
1. Dashboard/internal tool with no SEO → Vite SPA
2. Marketing + app hybrid → Next.js
3. Content-first with some interactivity → Astro
4. Web-standards-first, nested layouts → Remix
5. Default for most SaaS products → Next.js

---

## Phase 2: Project Structure & Conventions

### Recommended Feature-Based Structure

```
src/
├── app/                    # Routes/pages (framework-specific)
├── features/               # Feature modules (THE core pattern)
│   ├── auth/
│   │   ├── components/     # Feature-specific components
│   │   ├── hooks/          # Feature-specific hooks
│   │   ├── api/            # API calls & types
│   │   ├── utils/          # Feature utilities
│   │   ├── types.ts        # Feature types
│   │   └── index.ts        # Public API (barrel export)
│   ├── dashboard/
│   └── settings/
├── shared/                 # Cross-feature shared code
│   ├── components/         # Generic UI components
│   │   ├── ui/             # Primitives (Button, Input, Card)
│   │   └── layout/         # Layout components
│   ├── hooks/              # Generic hooks
│   ├── lib/                # Utilities, constants
│   └── types/              # Global types
├── providers/              # Context providers
└── styles/                 # Global styles
```

### 7 Structure Rules
1. **Feature isolation** — features/ never import from other features directly; use shared/ or events
2. **Barrel exports** — every feature has index.ts that defines its public API
3. **Colocation** — tests, stories, and styles live next to their component
4. **Max file size** — 300 lines. If bigger, split
5. **Max component size** — 50 lines of JSX. If bigger, extract
6. **No circular deps** — enforce with eslint-plugin-import
7. **Types colocated** — feature types in feature, shared types in shared/types

### Naming Conventions

```
Components:     PascalCase.tsx       (UserProfile.tsx)
Hooks:          useCamelCase.ts      (useAuth.ts)
Utilities:      camelCase.ts         (formatCurrency.ts)
Types:          PascalCase.ts        (User.ts) or types.ts
Constants:      SCREAMING_SNAKE.ts   (API_ENDPOINTS.ts)
Test files:     *.test.tsx           (UserProfile.test.tsx)
Story files:    *.stories.tsx        (Button.stories.tsx)
```

---

## Phase 3: Component Design Patterns

### Component Anatomy Template

```tsx
// 1. Imports (grouped: react → third-party → internal → types → styles)
import { useState, useCallback, memo } from 'react'
import { clsx } from 'clsx'
import { Button } from '@/shared/components/ui'
import type { User } from '../types'

// 2. Types (exported for reuse)
export interface UserCardProps {
  user: User
  onEdit?: (id: string) => void
  variant?: 'compact' | 'full'
  className?: string
}

// 3. Component (named export, not default)
export const UserCard = memo(function UserCard({
  user,
  onEdit,
  variant = 'full',
  className,
}: UserCardProps) {
  // 4. Hooks first
  const [isExpanded, setIsExpanded] = useState(false)

  // 5. Derived state (no useEffect for derived!)
  const displayName = `${user.firstName} ${user.lastName}`

  // 6. Handlers (useCallback for passed-down refs)
  const handleEdit = useCallback(() => {
    onEdit?.(user.id)
  }, [onEdit, user.id])

  // 7. Early returns for edge cases
  if (!user) return null

  // 8. JSX (max 50 lines)
  return (
    <div className={clsx('rounded-lg border p-4', className)}>
      <h3>{displayName}</h3>
      {variant === 'full' && <p>{user.bio}</p>}
      {onEdit && <Button onClick={handleEdit}>Edit</Button>}
    </div>
  )
})
```

### Component Composition Patterns

**1. Compound Components (for related UI groups)**
```tsx
// Usage: <Tabs><Tabs.List><Tabs.Tab>A</Tabs.Tab></Tabs.List><Tabs.Panel>...</Tabs.Panel></Tabs>
const TabsContext = createContext<TabsContextType | null>(null)

export function Tabs({ children, defaultValue }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue)
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  )
}
Tabs.List = TabsList
Tabs.Tab = TabsTab
Tabs.Panel = TabsPanel
```

**2. Render Props (for flexible rendering logic)**
```tsx
export function DataList<T>({ items, renderItem, renderEmpty }: DataListProps<T>) {
  if (items.length === 0) return renderEmpty?.() ?? <EmptyState />
  return <ul>{items.map((item, i) => <li key={i}>{renderItem(item)}</li>)}</ul>
}
```

**3. Higher-Order Components (for cross-cutting concerns — use sparingly)**
```tsx
export function withAuth<P>(Component: ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { user, isLoading } = useAuth()
    if (isLoading) return <Spinner />
    if (!user) return <Navigate to="/login" />
    return <Component {...props} />
  }
}
```

### 10 Component Rules
1. **One component per file** — always
2. **Named exports** — never default exports (refactoring safety)
3. **Props interface** — always explicit, always exported
4. **No business logic in components** — extract to hooks
5. **No inline styles** — use Tailwind classes or CSS modules
6. **No string refs** — useRef only
7. **No index as key** — use stable identifiers
8. **Memo strategically** — not everywhere, only for expensive renders
9. **Children over props** — prefer composition over configuration
10. **Accessible by default** — semantic HTML, ARIA when needed

---

## Phase 4: State Management Decision Framework

### State Type Decision Tree

```
Is it server data (from API)?
├─ YES → TanStack Query (or SWR) — NEVER Redux/Zustand for server state
│
└─ NO → Is it shared across features?
    ├─ YES → Is it complex with many actions?
    │   ├─ YES → Zustand (or Redux Toolkit if team knows it)
    │   └─ NO → Jotai (atomic) or Zustand (simple store)
    │
    └─ NO → Is it shared within a feature?
        ├─ YES → Context + useReducer (or Zustand feature store)
        └─ NO → useState / useReducer (component-local)
```

### State Management Comparison

| Tool | Best For | Bundle | Learning | Team Size |
|------|----------|--------|----------|-----------|
| useState | Component-local | 0 KB | None | Any |
| useReducer | Complex local state | 0 KB | Low | Any |
| Context | Feature-scoped, low-frequency | 0 KB | Low | Any |
| Zustand | Global client state | 1.1 KB | Low | Any |
| Jotai | Atomic derived state | 3.4 KB | Medium | Small-Med |
| TanStack Query | Server state | 12 KB | Medium | Any |
| Redux Toolkit | Complex global + middleware | 11 KB | High | Large |

### Server State with TanStack Query

```tsx
// api/users.ts — query key factory pattern
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: Filters) => [...userKeys.lists(), filters] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
}

// hooks/useUsers.ts
export function useUsers(filters: Filters) {
  return useQuery({
    queryKey: userKeys.list(filters),
    queryFn: () => fetchUsers(filters),
    staleTime: 5 * 60 * 1000, // 5 min
    placeholderData: keepPreviousData,
  })
}

export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: updateUser,
    onMutate: async (newUser) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: userKeys.detail(newUser.id) })
      const previous = queryClient.getQueryData(userKeys.detail(newUser.id))
      queryClient.setQueryData(userKeys.detail(newUser.id), newUser)
      return { previous }
    },
    onError: (err, newUser, context) => {
      queryClient.setQueryData(userKeys.detail(newUser.id), context?.previous)
    },
    onSettled: (data, err, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
    },
  })
}
```

### Client State with Zustand

```tsx
// stores/useUIStore.ts — thin, focused stores
interface UIStore {
  sidebarOpen: boolean
  theme: 'light' | 'dark' | 'system'
  toggleSidebar: () => void
  setTheme: (theme: UIStore['theme']) => void
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'system',
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setTheme: (theme) => set({ theme }),
    }),
    { name: 'ui-preferences' }
  )
)

// Usage: const theme = useUIStore((s) => s.theme) — always use selectors!
```

### 5 State Management Rules
1. **Server state ≠ client state** — never mix them in the same store
2. **Smallest scope possible** — useState > Context > Zustand > Redux
3. **No useEffect for derived state** — use useMemo or compute inline
4. **Selectors always** — `useStore(s => s.field)` not `useStore()`
5. **URL is state** — search params, filters, pagination → URL, not React state

---

## Phase 5: Hooks Engineering

### Custom Hook Template

```tsx
// hooks/useDebounce.ts
export function useDebounce<T>(value: T, delayMs: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])

  return debouncedValue
}
```

### Essential Custom Hooks Library

| Hook | Purpose | When to Use |
|------|---------|-------------|
| `useDebounce` | Debounce value changes | Search inputs, resize |
| `useMediaQuery` | Responsive breakpoints | Conditional rendering |
| `useLocalStorage` | Persistent local state | Preferences, drafts |
| `useIntersection` | Viewport detection | Lazy load, infinite scroll |
| `usePrevious` | Track previous value | Animations, comparisons |
| `useClickOutside` | Detect outside clicks | Dropdowns, modals |
| `useEventListener` | Safe event binding | Keyboard, scroll, resize |
| `useToggle` | Boolean state toggle | Modals, accordions |

### Hook Rules (beyond React's rules)
1. **One concern per hook** — `useUserSearch` not `useEverything`
2. **Return tuple or object** — tuple for 1-2 values, object for 3+
3. **Accept options object** — `useDebounce(value, { delay: 300 })` scales better
4. **Handle cleanup** — every subscription/timer needs cleanup in useEffect return
5. **No hooks in conditions** — extract conditional logic into the hook body
6. **Test hooks independently** — use `renderHook` from testing-library

---

## Phase 6: TypeScript Integration

### Strict Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Essential Type Patterns

```tsx
// 1. Discriminated unions for state machines
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error }

// 2. Polymorphic components
type ButtonProps<C extends ElementType = 'button'> = {
  as?: C
  variant?: 'primary' | 'secondary'
} & ComponentPropsWithoutRef<C>

export function Button<C extends ElementType = 'button'>({
  as,
  variant = 'primary',
  ...props
}: ButtonProps<C>) {
  const Component = as || 'button'
  return <Component {...props} />
}

// 3. Branded types for IDs
type UserId = string & { __brand: 'UserId' }
type PostId = string & { __brand: 'PostId' }

// 4. Zod for runtime validation
const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  role: z.enum(['admin', 'user', 'viewer']),
})
type User = z.infer<typeof userSchema>
```

### 5 TypeScript Rules
1. **Zero `any`** — use `unknown` and narrow, or generics
2. **Zod at boundaries** — validate all external data (API, forms, URL params)
3. **Discriminated unions over optional fields** — `{ status: 'success'; data: T }` not `{ data?: T; error?: Error }`
4. **Branded types for IDs** — prevent `userId` being passed where `postId` expected
5. **Satisfies over as** — `config satisfies Config` preserves inference; `as Config` lies

---

## Phase 7: Performance Optimization

### Performance Budget

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | < 1.8s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Interaction to Next Paint | < 200ms | Lighthouse |
| Cumulative Layout Shift | < 0.1 | Lighthouse |
| Bundle size (gzipped) | < 200 KB | webpack-bundle-analyzer |
| JS execution (main thread) | < 3s | Chrome DevTools |

### Optimization Priority Stack

| Priority | Technique | Impact | Effort |
|----------|-----------|--------|--------|
| P0 | Code splitting (route-based) | 🔴 High | Low |
| P0 | Image optimization (next/image, srcset) | 🔴 High | Low |
| P1 | Tree shaking (named imports) | 🟡 Medium | Low |
| P1 | Virtualization for long lists | 🟡 Medium | Medium |
| P1 | Debounce expensive operations | 🟡 Medium | Low |
| P2 | React.memo on expensive components | 🟢 Low-Med | Low |
| P2 | useMemo/useCallback for expensive calculations | 🟢 Low-Med | Low |
| P3 | Web Workers for heavy computation | 🟢 Low | High |

### Code Splitting Patterns

```tsx
// 1. Route-based (automatic with Next.js, manual with React Router)
const Dashboard = lazy(() => import('./features/dashboard'))
const Settings = lazy(() => import('./features/settings'))

// 2. Component-based (heavy components)
const Chart = lazy(() => import('./components/Chart'))
const MarkdownEditor = lazy(() =>
  import('./components/MarkdownEditor').then(m => ({ default: m.MarkdownEditor }))
)

// 3. Library-based (heavy third-party)
const { PDFViewer } = await import('@react-pdf/renderer')
```

### React Compiler (React 19+)
```tsx
// With React Compiler enabled, manual memo/useMemo/useCallback become unnecessary
// The compiler auto-memoizes. Remove manual optimizations:
// ❌ const memoized = useMemo(() => expensiveCalc(data), [data])
// ✅ const memoized = expensiveCalc(data)  // compiler handles it

// Enable in babel config:
// plugins: [['babel-plugin-react-compiler', {}]]
```

### Rendering Performance Rules
1. **Never create components inside components** — define at module level
2. **Never create objects/arrays in JSX** — `style={{ color: 'red' }}` rerenders always
3. **Children as props prevent rerender** — `<Layout><ExpensiveChild /></Layout>`
4. **Key must be stable and unique** — not index, not `Math.random()`
5. **Avoid context value churn** — memoize provider value or split contexts
6. **Profile before optimizing** — React DevTools Profiler, not guesswork

---

## Phase 8: Error Handling & Resilience

### Error Boundary Architecture

```tsx
// Three levels of error boundaries:
// 1. App-level (catches everything, shows full-page error)
// 2. Feature-level (isolates feature failures)
// 3. Component-level (for risky widgets — charts, third-party)

// Modern error boundary with react-error-boundary
import { ErrorBoundary, FallbackProps } from 'react-error-boundary'

function FeatureErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert" className="rounded-lg border-red-200 bg-red-50 p-4">
      <h3>Something went wrong</h3>
      <pre className="text-sm text-red-600">{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  )
}

// Usage:
<ErrorBoundary FallbackComponent={FeatureErrorFallback} onReset={() => queryClient.clear()}>
  <DashboardFeature />
</ErrorBoundary>
```

### Error Handling Checklist
- [ ] App-level error boundary wrapping entire app
- [ ] Feature-level boundaries for each major feature
- [ ] API errors handled in TanStack Query's `onError` / error states
- [ ] Form validation errors shown inline (not alerts)
- [ ] 404 page for unknown routes
- [ ] Offline detection and graceful degradation
- [ ] Error reporting to monitoring (Sentry, etc.)
- [ ] User-friendly error messages (no stack traces in production)

---

## Phase 9: Forms & Validation

### Form Library Decision

| Library | Best For | Bundle | Renders |
|---------|----------|--------|---------|
| React Hook Form | Most forms | 9 KB | Minimal (uncontrolled) |
| Formik | Simple forms | 13 KB | Every keystroke |
| TanStack Form | Type-safe complex | 5 KB | Controlled |
| Native | 1-2 field forms | 0 KB | You control |

**Default recommendation: React Hook Form + Zod**

### Form Pattern

```tsx
const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
  role: z.enum(['admin', 'user']),
})
type FormData = z.infer<typeof schema>

export function LoginForm({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '', role: 'user' },
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" {...form.register('email')} aria-invalid={!!form.formState.errors.email} />
      {form.formState.errors.email && (
        <p role="alert">{form.formState.errors.email.message}</p>
      )}
      {/* ... more fields */}
      <button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  )
}
```

---

## Phase 10: Testing Strategy

### Test Pyramid for React

| Level | Tool | Coverage Target | What to Test |
|-------|------|-----------------|-------------|
| Unit | Vitest | 80% business logic | Hooks, utilities, reducers |
| Component | Testing Library | Key user flows | Rendering, interactions, a11y |
| Integration | Testing Library | Feature flows | Multi-component workflows |
| E2E | Playwright | Critical paths | Auth, checkout, core flows |
| Visual | Chromatic/Percy | UI components | Regression detection |

### Testing Patterns

```tsx
// Component test (Testing Library philosophy: test behavior, not implementation)
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('UserCard', () => {
  it('calls onEdit when edit button clicked', async () => {
    const user = userEvent.setup()
    const onEdit = vi.fn()
    render(<UserCard user={mockUser} onEdit={onEdit} />)

    await user.click(screen.getByRole('button', { name: /edit/i }))
    expect(onEdit).toHaveBeenCalledWith(mockUser.id)
  })

  it('does not render edit button when onEdit not provided', () => {
    render(<UserCard user={mockUser} />)
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
  })
})
```

### 7 Testing Rules
1. **Test behavior, not implementation** — never test state directly or useEffect
2. **Use accessible queries** — `getByRole` > `getByTestId` > `getByText`
3. **User events over fireEvent** — `userEvent.click` simulates real interaction
4. **One assertion per concept** — not one per test, but focused assertions
5. **Mock at boundaries** — API calls, not internal functions
6. **No snapshot tests** — they break on every change and test nothing meaningful
7. **Arrange-Act-Assert** — clear structure in every test

---

## Phase 11: Accessibility (a11y)

### 10-Point Accessibility Checklist
1. **Semantic HTML** — `<button>` not `<div onClick>`, `<nav>` not `<div class="nav">`
2. **Keyboard navigation** — every interactive element reachable via Tab, operable via Enter/Space
3. **Focus management** — visible focus indicator, logical tab order, focus trap in modals
4. **Alt text** — every `<img>` has descriptive alt (or `alt=""` if decorative)
5. **Color contrast** — 4.5:1 for normal text, 3:1 for large text (WCAG AA)
6. **ARIA labels** — `aria-label` for icon-only buttons, `aria-describedby` for hints
7. **Live regions** — `aria-live="polite"` for dynamic content (toasts, form errors)
8. **Reduced motion** — respect `prefers-reduced-motion` for animations
9. **Screen reader testing** — test with VoiceOver (Mac) or NVDA (Windows)
10. **Automated scanning** — axe-core in CI (`vitest-axe` or `@axe-core/playwright`)

---

## Phase 12: Production Deployment Checklist

### Mandatory (P0)
- [ ] TypeScript strict mode, zero errors
- [ ] All tests passing
- [ ] Bundle analyzed, no unexpected large dependencies
- [ ] Error boundaries at app and feature level
- [ ] Environment variables validated at build time
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] SEO meta tags (title, description, OG tags)
- [ ] Analytics/error monitoring integrated
- [ ] Performance budget met (LCP < 2.5s)

### Recommended (P1)
- [ ] Storybook for component library
- [ ] Visual regression tests
- [ ] a11y automated checks in CI
- [ ] Feature flags for risky features
- [ ] Preview deployments for PRs
- [ ] Bundle size CI check (fail if +10%)

### Recommended Stack (2025+)

| Layer | Recommendation | Alternative |
|-------|---------------|-------------|
| Framework | Next.js 15 | Remix, Vite SPA |
| Language | TypeScript (strict) | — |
| Styling | Tailwind CSS v4 | CSS Modules |
| Components | shadcn/ui | Radix, Headless UI |
| State (server) | TanStack Query v5 | SWR |
| State (client) | Zustand | Jotai |
| Forms | React Hook Form + Zod | TanStack Form |
| Testing | Vitest + Testing Library | Jest |
| E2E | Playwright | Cypress |
| Linting | Biome | ESLint + Prettier |
| Auth | Auth.js (NextAuth) | Clerk, Lucia |
| Database | Drizzle ORM | Prisma |
| Deployment | Vercel | Cloudflare, Fly.io |
| Monitoring | Sentry | Datadog |

---

## Quality Scoring (0-100)

| Dimension | Weight | What to Score |
|-----------|--------|--------------|
| Architecture | 20% | Structure, separation, patterns |
| Type safety | 15% | Strict TS, zero any, Zod boundaries |
| Performance | 15% | Core Web Vitals, bundle size |
| Testing | 15% | Coverage, quality, pyramid |
| Accessibility | 10% | WCAG AA, keyboard, screen reader |
| State management | 10% | Right tool, no prop drilling |
| Error handling | 10% | Boundaries, user-friendly, monitoring |
| Developer experience | 5% | Linting, formatting, CI speed |

**Grading:** 90+ World-class | 75-89 Production-ready | 60-74 Needs work | <60 Tech debt crisis

---

## 10 Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | useEffect for derived state | Compute inline or useMemo |
| 2 | Prop drilling 5+ levels deep | Context, Zustand, or composition |
| 3 | Fetching in useEffect | TanStack Query or framework loaders |
| 4 | Default exports everywhere | Named exports for refactoring safety |
| 5 | Testing implementation details | Test behavior with Testing Library |
| 6 | Giant components (500+ lines) | Extract hooks and sub-components |
| 7 | No error boundaries | Add at app, feature, and widget level |
| 8 | Redux for server state | TanStack Query for API data |
| 9 | Ignoring a11y until the end | Build accessible from day 1 |
| 10 | No TypeScript strict mode | Enable strict, fix all errors |

---

## Natural Language Commands

- "Set up a new React project" → Phase 1-2 architecture + structure
- "Review my component" → Phase 3 rules + quality scoring
- "Help me choose state management" → Phase 4 decision tree
- "Optimize performance" → Phase 7 priority stack + profiling
- "Add error handling" → Phase 8 error boundary architecture
- "Build a form" → Phase 9 React Hook Form + Zod pattern
- "Write tests for this component" → Phase 10 testing patterns
- "Check accessibility" → Phase 11 checklist
- "Prepare for production" → Phase 12 deployment checklist
- "Audit my React app" → Full quality scoring across all phases
- "Migrate from class components" → Modern patterns + hooks
- "Upgrade to React 19" → Compiler, Server Components, Actions

---

## ⚡ Level Up Your React Development

This skill gives you the methodology. For industry-specific implementation patterns, grab an **AfrexAI Context Pack** ($47):

- **SaaS Context Pack** — SaaS-specific React patterns, billing UI, dashboard architecture
- **Fintech Context Pack** — Financial UI patterns, real-time data, compliance
- **Healthcare Context Pack** — HIPAA-compliant UI, patient data handling

👉 **Browse all 10 packs:** https://afrexai-cto.github.io/context-packs/

### 🔗 More Free Skills by AfrexAI
- `afrexai-nextjs-production` — Next.js production engineering
- `afrexai-vibe-coding` — AI-assisted development methodology
- `afrexai-technical-seo` — SEO for React SPAs and SSR
- `afrexai-test-automation-engineering` — Complete testing strategy
- `afrexai-ui-design-system` — Design system architecture
