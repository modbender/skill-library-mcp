# Routing & Middleware Reference

## URL Pattern

English (default locale) has no prefix — all others use `/<locale>`:

```
/              → English home
/products      → English products
/es            → Spanish home
/es/products   → Spanish products
/ar/products   → Arabic products
/zh-CN/blog    → Simplified Chinese blog
```

Redirect rule: `/en/*` → `/*` (middleware enforces clean English URLs)

## Middleware (`src/middleware.ts`)

```typescript
import { match } from '@formatjs/intl-localematcher'
import Negotiator from 'negotiator'
import { NextRequest, NextResponse } from 'next/server'
import { defaultLocale, locales, type Locale } from '@/lib/i18n/locales'

function getLocale(request: NextRequest): string {
  const acceptLang = request.headers.get('accept-language') ?? undefined
  const headers = { 'accept-language': acceptLang || defaultLocale }
  const languages = new Negotiator({ headers }).languages()
  return match(languages, locales, defaultLocale)
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip non-page paths
  if (
    pathname.startsWith('/api/') ||
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/admin') ||
    pathname === '/sitemap.xml' ||
    pathname === '/robots.txt'
  ) {
    return NextResponse.next()
  }

  // Redirect /en/* → /* to keep URLs clean
  if (pathname.startsWith(`/${defaultLocale}/`) || pathname === `/${defaultLocale}`) {
    const clean = pathname === `/${defaultLocale}` ? '/' : pathname.replace(`/${defaultLocale}`, '')
    const url = request.nextUrl.clone()
    url.pathname = clean
    return NextResponse.redirect(url)
  }

  // If pathname already has a supported locale prefix, pass through
  const hasLocale = locales.some(
    (l) => pathname.startsWith(`/${l}/`) || pathname === `/${l}`
  )
  if (hasLocale) return NextResponse.next()

  // No locale prefix → rewrite internally to default locale folder
  const rewrite = pathname === '/' ? `/${defaultLocale}` : `/${defaultLocale}${pathname}`
  const url = request.nextUrl.clone()
  url.pathname = rewrite
  return NextResponse.rewrite(url)
}

export const config = {
  matcher: ['/((?!_next|favicon.ico|images|fonts|icons).*)'],
}
```

## `useLocale()` Hook

Priority order: URL param → pathname segment → localStorage → default locale.

```typescript
// src/hooks/use-locale.ts
export function useLocale(): Locale {
  const params = useParams()
  const pathname = usePathname()
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => setHydrated(true), [])

  return useMemo(() => {
    // 1. URL params (e.g., [lang] segment)
    if (params?.lang && locales.includes(params.lang as Locale)) {
      return params.lang as Locale
    }
    // 2. Pathname prefix
    const first = pathname?.split('/').filter(Boolean)[0]
    if (first && locales.includes(first as Locale)) return first as Locale
    // 3. localStorage
    if (hydrated) {
      const stored = localStorage.getItem('locale') as Locale
      if (stored && locales.includes(stored)) return stored
    }
    return defaultLocale
  }, [params, pathname, hydrated])
}
```

## Path Utilities (`src/lib/i18n/utils.ts`)

```typescript
// Add locale prefix (no prefix for default locale)
export function getLocalizedPath(path: string, locale?: Locale): string {
  const target = locale ?? getStoredLocale()
  const clean = path.startsWith('/') ? path : `/${path}`
  return target === defaultLocale ? clean : `/${target}${clean}`
}

// Strip locale prefix from any path
export function removeLocalePrefix(path: string): string {
  const segments = path.split('/').filter(Boolean)
  if (segments.length > 0 && locales.includes(segments[0] as Locale)) {
    return '/' + segments.slice(1).join('/') || '/'
  }
  return path || '/'
}

// Locale persistence
export function storeLocale(locale: Locale): void {
  if (typeof window === 'undefined') return
  locale === defaultLocale
    ? localStorage.removeItem('locale')
    : localStorage.setItem('locale', locale)
}
```

## `LocalizedLink` Component

Wrap `<Link>` to automatically apply locale prefix:

```typescript
// src/components/ui/localized-link.tsx
'use client'
export function LocalizedLink({ href, children, ...props }: LocalizedLinkProps) {
  const locale = useLocale()
  const clean = removeLocalePrefix(href)
  const localizedHref = getLocalizedPath(clean, locale)
  return <Link href={localizedHref} {...props}>{children}</Link>
}
```

Usage:
```tsx
// Renders /products (en) or /es/products (es) automatically
<LocalizedLink href="/products">Products</LocalizedLink>
```

## Language Switcher

```typescript
// src/components/ui/language-switcher.tsx
const languageNames: Record<Locale, string> = {
  en: 'English', es: 'Español', ar: 'العربية',
  ja: '日本語', 'zh-CN': '简体中文', 'zh-TW': '繁體中文',
  // ... all 19
}

function switchLanguage(locale: Locale) {
  storeLocale(locale)
  const clean = removeLocalePrefix(pathname || '/')
  const newPath = locale === defaultLocale ? clean : `/${locale}${clean === '/' ? '' : clean}`
  router.push(newPath)
}
```

## HTML `lang` Attribute

Set server-side in layout, update client-side for SPA navigation:

```typescript
// src/app/[lang]/layout.tsx
export default async function RootLayout({ children, params }) {
  const { lang } = await params
  return (
    <html lang={lang}>
      <body>
        <LangSetter />  {/* Updates document.documentElement.lang on client */}
        {children}
      </body>
    </html>
  )
}
```

```typescript
// src/components/ui/lang-setter.tsx
'use client'
export function LangSetter() {
  const params = useParams()
  useEffect(() => {
    const lang = (params?.lang as Locale) || defaultLocale
    document.documentElement.setAttribute('lang', lang)
  }, [params?.lang])
  return null
}
```

## RTL Support

Arabic (`ar`) requires RTL layout. Detect in layout:

```typescript
const isRtl = lang === 'ar'
return <html lang={lang} dir={isRtl ? 'rtl' : 'ltr'}>
```
