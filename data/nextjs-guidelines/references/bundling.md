# Bundling

Fix common bundling issues with third-party packages.

## Server-Incompatible Packages

Some packages use browser APIs (`window`, `document`, `localStorage`) and fail in Server Components.

### Error Signs

```
ReferenceError: window is not defined
ReferenceError: document is not defined
ReferenceError: localStorage is not defined
Module not found: Can't resolve 'fs'
```

### Solution 1: Dynamic Import with SSR Disabled

For packages that only work on client:

```tsx
// BAD: Fails — package uses window
import SomeChart from 'some-chart-library'

export default function Page() {
  return <SomeChart />
}

// GOOD: Dynamic import with ssr: false
import dynamic from 'next/dynamic'

const SomeChart = dynamic(() => import('some-chart-library'), {
  ssr: false,
  loading: () => <ChartSkeleton />,
})

export default function Page() {
  return <SomeChart />
}
```

### Solution 2: Server External Packages

For packages that should run on server but have bundling issues:

```js
// next.config.js
module.exports = {
  serverExternalPackages: ['problematic-package'],
}
```

Use for:
- Native bindings (sharp, bcrypt, canvas)
- Packages that don't bundle well (some ORMs)
- Packages with circular dependencies

### Solution 3: Client Component Wrapper

```tsx
// components/ChartWrapper.tsx
'use client'

import { Chart } from 'chart-library'

export function ChartWrapper(props) {
  return <Chart {...props} />
}

// app/page.tsx (server component)
import { ChartWrapper } from '@/components/ChartWrapper'

export default function Page() {
  return <ChartWrapper data={data} />
}
```

## Common Problematic Packages

| Package | Issue | Solution |
|---------|-------|----------|
| `sharp` | Native bindings | `serverExternalPackages: ['sharp']` |
| `bcrypt` | Native bindings | `serverExternalPackages: ['bcrypt']` or use `bcryptjs` |
| `canvas` | Native bindings | `serverExternalPackages: ['canvas']` |
| `recharts` | Uses window | `dynamic(() => import('recharts'), { ssr: false })` |
| `react-quill` | Uses document | `dynamic(() => import('react-quill'), { ssr: false })` |
| `mapbox-gl` | Uses window | `dynamic(() => import('mapbox-gl'), { ssr: false })` |
| `monaco-editor` | Uses window | `dynamic(() => import('@monaco-editor/react'), { ssr: false })` |
| `lottie-web` | Uses document | `dynamic(() => import('lottie-react'), { ssr: false })` |

## CSS Imports

Import CSS files — Next.js handles bundling and optimization:

```tsx
// BAD: Manual link tag
<link rel="stylesheet" href="/styles.css" />

// GOOD: Import CSS
import './styles.css'

// GOOD: CSS Modules
import styles from './Button.module.css'
```

## ESM/CommonJS Issues

### Error Signs

```
SyntaxError: Cannot use import statement outside a module
Error: require() of ES Module
Module not found: ESM packages need to be imported
```

### Solution: Transpile Package

```js
// next.config.js
module.exports = {
  transpilePackages: ['some-esm-package', 'another-package'],
}
```

## Polyfills

Next.js includes common polyfills automatically. Don't load redundant ones:

```tsx
// BAD: Redundant polyfills
<script src="https://polyfill.io/v3/polyfill.min.js?features=fetch,Promise,Array.from" />

// GOOD: Next.js includes these automatically — no script needed
```

Already included: `Array.from`, `Object.assign`, `Promise`, `fetch`, `Map`, `Set`, `Symbol`, `URLSearchParams`, and 50+ others.

## Bundle Analysis

Analyze bundle size with the built-in analyzer (Next.js 16.1+):

```bash
next experimental-analyze
```

Save output for comparison:

```bash
next experimental-analyze --output
# Output saved to .next/diagnostics/analyze
```

## Turbopack Migration

Turbopack is the default bundler in Next.js 15+. If you have custom webpack config:

```js
// next.config.js
module.exports = {
  // GOOD: Works with Turbopack
  serverExternalPackages: ['package'],
  transpilePackages: ['package'],

  // BAD: Webpack-only — migrate away from this
  webpack: (config) => {
    // custom webpack config
  },
}
```
