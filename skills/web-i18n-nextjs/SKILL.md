---
name: i18n-nextjs
description: >
  Internationalization (i18n) guide for Next.js / Node.js web applications using the App Router.
  Covers translation file structure, locale routing, SEO metadata per locale, hreflang, structured
  JSON-LD data, UI component translations, and multi-language sitemap generation.
  Use when the user asks to: add i18n support, add a new language, translate a page or component,
  add SEO metadata for multiple locales, implement hreflang, update the sitemap for new locales,
  or follow i18n best practices in a Next.js project.
---

# i18n for Next.js — Implementation Guide

## Core Principles

- All user-facing features **must** implement i18n — no hardcoded strings in components.
- Translations must be **natural and idiomatic** — never use scripts or machine translation; treat quality the same as English copywriting.
- SEO metadata, JSON-LD structured data, and sitemaps must all be locale-aware.
- Default locale (English) uses **clean URLs** with no prefix (`/products`); other locales use a prefix (`/es/products`).

## Supported Locales

Locale list lives in `src/lib/i18n/locales.ts`. Keep the sitemap script's `locales` array in sync with this file.

```typescript
export const locales = ['en', 'es', 'fr', 'de', 'ja', 'zh-CN', /* ... add as needed */]
export const defaultLocale = 'en'
export type Locale = typeof locales[number]
```

## Directory Structure

```
src/app/[lang]/
├── dictionaries/       ← One JSON file per locale
│   ├── en.json
│   ├── es.json
│   └── ...
├── dictionaries.ts     ← getDictionary(locale) server helper
├── layout.tsx          ← Root layout: generateMetadata + hreflang + JSON-LD
└── <page>/
    └── page.tsx        ← generateMetadata + page content
```

## Translation Files

See **[references/translation-files.md](references/translation-files.md)** for:
- JSON key hierarchy conventions (`page.section.key`)
- Server-side `getDictionary()` usage
- Client-side `useDictionary()` hook usage
- Template variable pattern (`{count}` substitution)
- Fallback pattern for missing keys

## Routing & Middleware

See **[references/routing.md](references/routing.md)** for:
- `src/middleware.ts` — locale detection, redirect `/en/*` → `/*`, rewrite for default locale
- `LocalizedLink` component — automatically prefixes non-default locales
- `useLocale()` hook — reads locale from URL params → pathname → localStorage → default
- `getLocalizedPath()` / `removeLocalePrefix()` utilities

## SEO Metadata

See **[references/seo-metadata.md](references/seo-metadata.md)** for:
- `generateMetadata()` pattern in layout/page files
- `generateAlternatesMetadata()` from `src/lib/i18n/seo.ts`
- Full hreflang `alternates.languages` output (all locales + `x-default`)
- OpenGraph `locale` / `alternateLocale` fields
- `html lang` attribute and `LangSetter` client component

## Structured JSON-LD Data

See **[references/structured-data.md](references/structured-data.md)** for:
- WebApplication schema with translated `featureList`, `description`
- BlogPosting schema with `inLanguage` field
- FAQ schema with translated `acceptedAnswer`
- BreadcrumbList schema with localized URLs
- Rendering via `<Script>` or `<script>` tags

## Multi-language Sitemap

See **[references/sitemap.md](references/sitemap.md)** for:
- Sitemap structure: one `<url>` entry per page with `<xhtml:link>` alternates for every locale
- `<loc>` uses the default-locale (clean) URL; `x-default` also points there
- Full XML example with static and dynamic pages
- Next.js App Router `sitemap.ts` implementation pattern
- What to include vs. exclude (admin/API routes excluded)
- Hreflang language code format rules

## Quick Checklist — Adding a New Feature with i18n

1. **Add translation keys** to all locale JSON files in `src/app/[lang]/dictionaries/`
   - Add English first, then translate to all other languages naturally
2. **Server components**: `const dict = await getDictionary(locale)` → `dict?.page?.section?.key || 'fallback'`
3. **Client components**: `const dict = useDictionary()` → same fallback pattern
4. **Add `generateMetadata()`** to the page file, calling `generateAlternatesMetadata()`
5. **Add JSON-LD** structured data script tag with translated fields and `inLanguage`
6. **Update sitemap** if the page is new: add it to the sitemap source (see [references/sitemap.md](references/sitemap.md))
7. **Use `<LocalizedLink>`** for internal links and `getLocalizedPath()` for programmatic navigation

## Quick Checklist — Adding a New Locale

1. Add locale code to `locales` array in `src/lib/i18n/locales.ts`
2. Add locale entry to `dictionaries/` as `<code>.json` (full translation of `en.json`)
3. Add entry in `src/app/[lang]/dictionaries.ts` import map
4. Add display name in `LanguageSwitcher` `languageNames` map
5. Sync the sitemap locale list with the app's `locales` array
6. Regenerate / redeploy the sitemap
