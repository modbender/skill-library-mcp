# Bundle Size Optimization

## Avoid Barrel File Imports (CRITICAL)

Import directly from source files. Barrel files re-export thousands of modules.

```tsx
// BAD — loads 1,583 modules, 200-800ms import cost
import { Check, X, Menu } from 'lucide-react'
import { Button, TextField } from '@mui/material'

// GOOD — loads only what you need
import Check from 'lucide-react/dist/esm/icons/check'
import X from 'lucide-react/dist/esm/icons/x'
import Button from '@mui/material/Button'
```

**Next.js 13.5+ auto-optimization:**

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@mui/material']
  }
}
```

Commonly affected: `lucide-react`, `@mui/material`, `@mui/icons-material`,
`@tabler/icons-react`, `react-icons`, `@radix-ui/react-*`, `lodash`, `date-fns`.

Benefits: 15-70% faster dev boot, 28% faster builds, 40% faster cold starts.

## Dynamic Imports for Heavy Components (CRITICAL)

Use `next/dynamic` to lazy-load components not needed on initial render.

```tsx
import dynamic from 'next/dynamic'

const MonacoEditor = dynamic(
  () => import('./monaco-editor').then((m) => m.MonacoEditor),
  { ssr: false }
)
```

## Defer Non-Critical Third-Party Libraries (MEDIUM)

Analytics, logging, error tracking don't block interaction — load after hydration.

```tsx
const Analytics = dynamic(
  () => import('@vercel/analytics/react').then((m) => m.Analytics),
  { ssr: false }
)
```

## Conditional Module Loading (HIGH)

Load large data/modules only when a feature is activated.

```tsx
useEffect(() => {
  if (enabled && !frames && typeof window !== 'undefined') {
    import('./animation-frames.js')
      .then((mod) => setFrames(mod.frames))
      .catch(() => setEnabled(false))
  }
}, [enabled, frames, setEnabled])
```

The `typeof window !== 'undefined'` check prevents bundling for SSR.

## Preload on User Intent (MEDIUM)

Preload heavy bundles on hover/focus before they're needed.

```tsx
function EditorButton({ onClick }: { onClick: () => void }) {
  const preload = () => {
    if (typeof window !== 'undefined') void import('./monaco-editor')
  }
  return (
    <button onMouseEnter={preload} onFocus={preload} onClick={onClick}>
      Open Editor
    </button>
  )
}
```

Also works with feature flags:

```tsx
useEffect(() => {
  if (flags.editorEnabled && typeof window !== 'undefined') {
    void import('./monaco-editor').then((mod) => mod.init())
  }
}, [flags.editorEnabled])
```
