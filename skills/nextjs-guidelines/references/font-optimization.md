# Font Optimization

Use `next/font` for automatic font optimization with zero layout shift.

## Google Fonts

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  )
}
```

## Multiple Fonts with CSS Variables

```tsx
import { Inter, Roboto_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  variable: '--font-roboto-mono',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

Use in CSS or Tailwind:

```css
body { font-family: var(--font-inter); }
code { font-family: var(--font-roboto-mono); }
```

## Font Weights

```tsx
// Single weight
const inter = Inter({ subsets: ['latin'], weight: '400' })

// Multiple weights
const inter = Inter({ subsets: ['latin'], weight: ['400', '500', '700'] })

// Variable font (recommended) — includes all weights automatically
const inter = Inter({ subsets: ['latin'] })

// With italic
const inter = Inter({ subsets: ['latin'], style: ['normal', 'italic'] })
```

## Local Fonts

```tsx
import localFont from 'next/font/local'

// Single file
const myFont = localFont({ src: './fonts/MyFont.woff2' })

// Multiple files for different weights
const myFont = localFont({
  src: [
    { path: './fonts/MyFont-Regular.woff2', weight: '400', style: 'normal' },
    { path: './fonts/MyFont-Bold.woff2', weight: '700', style: 'normal' },
  ],
})

// Variable font
const myFont = localFont({
  src: './fonts/MyFont-Variable.woff2',
  variable: '--font-my-font',
})
```

## Tailwind CSS Integration

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
```

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)'],
      },
    },
  },
}
```

## NEVER Do

```tsx
// BAD: Importing font in every component — creates new instance each time!
// components/Button.tsx
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'] })

// GOOD: Import once in layout, use CSS variable everywhere

// BAD: Using @import in CSS — blocks rendering
/* globals.css */
@import url('https://fonts.googleapis.com/css2?family=Inter');

// GOOD: Use next/font — self-hosted, no network request

// BAD: Manual link tag — no optimization
<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet" />

// GOOD: Use next/font
import { Inter } from 'next/font/google'

// BAD: Missing subset — loads all characters
const inter = Inter({})

// GOOD: Always specify subset
const inter = Inter({ subsets: ['latin'] })
```

## Display Strategy

```tsx
const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Default — shows fallback, swaps when loaded
})

// Options:
// 'auto' - browser decides
// 'block' - short block period, then swap
// 'swap' - immediate fallback, swap when ready (recommended)
// 'fallback' - short block, short swap, then fallback
// 'optional' - short block, no swap (use if font is optional)
```

## Shared Font Exports

For component-specific fonts, export from a shared file:

```tsx
// lib/fonts.ts
import { Inter, Playfair_Display } from 'next/font/google'

export const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
export const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair' })

// components/Heading.tsx
import { playfair } from '@/lib/fonts'

export function Heading({ children }) {
  return <h1 className={playfair.className}>{children}</h1>
}
```
