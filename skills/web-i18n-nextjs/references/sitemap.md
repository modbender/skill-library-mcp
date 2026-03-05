# Multi-Language Sitemap Reference

## Core Principle

In an i18n site, **every URL has multiple language versions**. The sitemap must:
1. List every URL once (using the canonical/default locale URL as `<loc>`)
2. Attach `<xhtml:link rel="alternate">` entries for **all locale variants** of that URL, including `x-default`

This tells search engines that these URLs are the same page in different languages, not duplicate content.

---

## URL Structure

With default locale = `en` and no `/en` prefix for English:

| Page      | English (default)          | Spanish                      | Japanese                     |
|-----------|----------------------------|------------------------------|------------------------------|
| Home      | `https://example.com/`     | `https://example.com/es/`    | `https://example.com/ja/`    |
| Products  | `https://example.com/products` | `https://example.com/es/products` | `https://example.com/ja/products` |
| Blog post | `https://example.com/blog/my-post` | `https://example.com/es/blog/my-post` | `https://example.com/ja/blog/my-post` |

The `<loc>` in the sitemap uses the **English (default) URL**. All locale versions are listed in `<xhtml:link>` alternates.

---

## XML Structure per URL Entry

```xml
<url>
  <!-- Canonical URL (default locale, no language prefix) -->
  <loc>https://example.com/products</loc>

  <!-- Alternate for every supported locale -->
  <xhtml:link rel="alternate" hreflang="en"    href="https://example.com/products"/>
  <xhtml:link rel="alternate" hreflang="es"    href="https://example.com/es/products"/>
  <xhtml:link rel="alternate" hreflang="fr"    href="https://example.com/fr/products"/>
  <xhtml:link rel="alternate" hreflang="de"    href="https://example.com/de/products"/>
  <xhtml:link rel="alternate" hreflang="ja"    href="https://example.com/ja/products"/>
  <xhtml:link rel="alternate" hreflang="zh-CN" href="https://example.com/zh-CN/products"/>
  <!-- ... one entry per locale ... -->

  <!-- x-default points to the default locale URL -->
  <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/products"/>

  <lastmod>2025-01-15</lastmod>
  <changefreq>weekly</changefreq>
  <priority>0.8</priority>
</url>
```

**Rules:**
- `<loc>` = canonical URL (always the default locale / clean URL)
- Every locale gets exactly one `<xhtml:link>` alternate
- `x-default` typically points to the same URL as the default locale
- All URLs within one `<url>` block must reference each other (Google requirement: alternates must be consistent across all language pages)

---

## Full Sitemap Document Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- Home page -->
  <url>
    <loc>https://example.com/</loc>
    <xhtml:link rel="alternate" hreflang="en"       href="https://example.com/"/>
    <xhtml:link rel="alternate" hreflang="es"       href="https://example.com/es/"/>
    <xhtml:link rel="alternate" hreflang="fr"       href="https://example.com/fr/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/"/>
    <lastmod>2025-01-15</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>

  <!-- Static page -->
  <url>
    <loc>https://example.com/about</loc>
    <xhtml:link rel="alternate" hreflang="en"       href="https://example.com/about"/>
    <xhtml:link rel="alternate" hreflang="es"       href="https://example.com/es/about"/>
    <xhtml:link rel="alternate" hreflang="fr"       href="https://example.com/fr/about"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/about"/>
    <lastmod>2025-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>

  <!-- Dynamic page (e.g. blog post) -->
  <url>
    <loc>https://example.com/blog/my-post-slug</loc>
    <xhtml:link rel="alternate" hreflang="en"       href="https://example.com/blog/my-post-slug"/>
    <xhtml:link rel="alternate" hreflang="es"       href="https://example.com/es/blog/my-post-slug"/>
    <xhtml:link rel="alternate" hreflang="fr"       href="https://example.com/fr/blog/my-post-slug"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/blog/my-post-slug"/>
    <lastmod>2025-01-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>

</urlset>
```

---

## What to Include vs. Exclude

**Include:**
- All public-facing pages (home, feature pages, pricing, about, contact)
- Dynamic content pages (blog posts, product detail pages, etc.)
- Each page listed **once** using the default-locale URL as `<loc>`

**Exclude:**
- Admin / internal routes (`/admin`, `/dashboard`, etc.)
- API routes (`/api/...`)
- Auth pages (`/login`, `/signup`) — optional, low SEO value
- Pages behind authentication
- Duplicate or near-duplicate pages (`/en/...` redirect targets)

---

## Implementation Approaches

### Option 1: Next.js built-in `sitemap.ts` (recommended for App Router)

```typescript
// src/app/sitemap.ts
import { MetadataRoute } from 'next'
import { locales, defaultLocale } from '@/lib/i18n/locales'

const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://example.com'

function buildAlternates(path: string) {
  const languages: Record<string, string> = {}
  for (const locale of locales) {
    languages[locale] = locale === defaultLocale
      ? `${baseUrl}${path}`
      : `${baseUrl}/${locale}${path}`
  }
  languages['x-default'] = `${baseUrl}${path}`
  return { languages }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Static pages
  const staticPages = ['/', '/about', '/pricing', '/blog'].map((path) => ({
    url: `${baseUrl}${path}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: path === '/' ? 1.0 : 0.7,
    alternates: buildAlternates(path),
  }))

  // Dynamic pages (e.g. blog posts from DB/CMS)
  const posts = await fetchBlogPosts()
  const dynamicPages = posts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: 0.6,
    alternates: buildAlternates(`/blog/${post.slug}`),
  }))

  return [...staticPages, ...dynamicPages]
}
```

Next.js automatically outputs `<xhtml:link>` tags when `alternates.languages` is provided.

### Option 2: Custom script (non-App Router or more control needed)

Generate `public/sitemap.xml` with a Node.js script that:
1. Collects all paths (static list + dynamic from DB/CMS/API)
2. For each path, expands to all locale URLs
3. Writes the XML with the structure shown above

---

## Hreflang Language Code Rules

| Locale         | `hreflang` value |
|----------------|------------------|
| English        | `en`             |
| Spanish        | `es`             |
| French         | `fr`             |
| Simplified Chinese | `zh-CN`      |
| Traditional Chinese | `zh-TW`     |
| Portuguese (Brazil) | `pt-BR`    |
| Portuguese (Portugal) | `pt-PT`  |
| Default fallback | `x-default`    |

- Use IETF language tags: `language` or `language-REGION`
- `x-default` is required — point it to the default locale URL
- Must be consistent: every locale page must list all the same alternates

---

## Keeping Locales in Sync

The sitemap's locale list must always match the app's `locales` array in `src/lib/i18n/locales.ts`. When adding or removing a locale, update both in the same commit.
