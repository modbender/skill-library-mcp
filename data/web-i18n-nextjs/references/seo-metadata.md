# SEO Metadata Reference

## `generateMetadata()` Pattern

Every page and layout that serves user-facing content must export `generateMetadata`.

```typescript
// src/app/[lang]/some-page/page.tsx
import { type Metadata } from 'next'
import { getDictionary } from '../dictionaries'
import { generateAlternatesMetadata } from '@/lib/i18n/seo'
import { type Locale } from '@/lib/i18n/locales'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang: string }>
}): Promise<Metadata> {
  const { lang } = await params
  const locale = lang as Locale
  const dict = await getDictionary(locale)
  const meta = dict?.somePage?.metadata || {}

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://MyApp.com'
  const pathname = `/${lang}/some-page`
  const alternates = generateAlternatesMetadata(locale, pathname, baseUrl, true)

  const title = meta.title || 'Default Title'
  const description = meta.description || 'Default description'

  return {
    metadataBase: new URL(baseUrl),
    title,
    description,
    keywords: meta.keywords || [],
    alternates,             // ← hreflang for all 19 locales
    openGraph: {
      title: meta.ogTitle || title,
      description: meta.ogDescription || description,
      url: `${baseUrl}/${lang}/some-page`,
      locale: lang === 'zh-CN' ? 'zh_CN' : lang.replace('-', '_'),
      alternateLocale: locales
        .filter((l) => l !== lang)
        .map((l) => (l === 'zh-CN' ? 'zh_CN' : l.replace('-', '_'))),
      type: 'website',
      images: [{ url: '/images/og-image.webp', width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: meta.ogTitle || title,
      description: meta.ogDescription || description,
      images: ['/images/og-image.webp'],
    },
  }
}
```

## `generateAlternatesMetadata()` — `src/lib/i18n/seo.ts`

```typescript
export function generateAlternatesMetadata(
  currentLang: Locale,
  pathname: string,
  baseUrl: string,
  useDefaultLocaleAsRoot: boolean = true
) {
  const pathWithoutLang = getPathnameWithoutLang(pathname)
  const languages = generateHreflangUrls(currentLang, pathWithoutLang, baseUrl, useDefaultLocaleAsRoot)

  const canonical =
    currentLang === defaultLocale && useDefaultLocaleAsRoot
      ? pathWithoutLang
      : `/${currentLang}${pathWithoutLang}`

  return { canonical, languages }
}

export function generateHreflangUrls(
  currentLang: Locale,
  pathname: string,   // path WITHOUT locale prefix
  baseUrl: string,
  useDefaultLocaleAsRoot: boolean = true
): Record<string, string> {
  const urls: Record<string, string> = {}

  for (const locale of locales) {
    urls[locale] =
      locale === defaultLocale && useDefaultLocaleAsRoot
        ? `${baseUrl}${pathname}`
        : `${baseUrl}/${locale}${pathname}`
  }

  // x-default → default locale
  urls['x-default'] = useDefaultLocaleAsRoot
    ? `${baseUrl}${pathname}`
    : `${baseUrl}/${defaultLocale}${pathname}`

  return urls
}
```

**Output (Next.js converts to `<link rel="alternate" hreflang="...">`):**
```html
<link rel="alternate" hreflang="en"      href="https://MyApp.com/some-page"/>
<link rel="alternate" hreflang="es"      href="https://MyApp.com/es/some-page"/>
<link rel="alternate" hreflang="ar"      href="https://MyApp.com/ar/some-page"/>
<link rel="alternate" hreflang="zh-CN"   href="https://MyApp.com/zh-CN/some-page"/>
<!-- ... all 19 locales ... -->
<link rel="alternate" hreflang="x-default" href="https://MyApp.com/some-page"/>
```

## Dictionary Keys for Metadata

In each locale's JSON, the `metadata` block should contain:

```json
{
  "somePage": {
    "metadata": {
      "title": "Page Title — Site Name",
      "description": "Localized meta description (140–160 chars).",
      "keywords": ["keyword 1", "keyword 2"],
      "ogTitle": "OG title (can differ from meta title)",
      "ogDescription": "OG description for social sharing."
    }
  }
}
```

Translations must be written in the target language — not machine-translated copies of English.

## Blog / Dynamic Pages

For pages with dynamic data (blog post, template detail), merge static dictionary strings with dynamic content:

```typescript
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang, slug } = await params
  const locale = lang as Locale
  const dict = await getDictionary(locale)
  const blogPost = await getBlogPost(slug)

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://MyApp.com'
  const pathname = `/${lang}/blog/${blogPost.slug}`
  const alternates = generateAlternatesMetadata(locale, pathname, baseUrl, true)

  return {
    title: `${blogPost.title} | Blog`,
    description: blogPost.excerpt || dict?.blog?.metadata?.description,
    alternates,
    openGraph: {
      type: 'article',
      publishedTime: blogPost.publishedAt.toISOString(),
      locale: lang === 'zh-CN' ? 'zh_CN' : lang.replace('-', '_'),
      images: [{ url: blogPost.featuredImage, width: 1200, height: 630 }],
    },
  }
}
```

## Canonical URL Rules

| Locale         | Canonical URL                        |
|----------------|--------------------------------------|
| `en` (default) | `https://MyApp.com/some-page`      |
| `es`           | `https://MyApp.com/es/some-page`   |
| `zh-CN`        | `https://MyApp.com/zh-CN/some-page`|
| `x-default`    | `https://MyApp.com/some-page`      |

English canonical has **no** `/en` prefix. This is enforced by `useDefaultLocaleAsRoot: true`.
