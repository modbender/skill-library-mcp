# Structured JSON-LD Data Reference

Always include translated strings and the `inLanguage` field in structured data.
Render via `<Script>` (layout) or `<script>` (page component).

## Table of Contents
- [WebApplication Schema (Homepage / App Landing)](#webapplication-schema)
- [BlogPosting Schema](#blogposting-schema)
- [FAQ Schema with Translations](#faq-schema)
- [BreadcrumbList Schema](#breadcrumblist-schema)
- [How-To Schema](#how-to-schema)

---

## WebApplication Schema

For the main product/homepage layout:

```tsx
// src/app/[lang]/layout.tsx
import Script from 'next/script'

const dict = await getDictionary(locale)
const structured = dict?.home?.structuredData || {}

const webAppSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: structured.name || 'MyApp',
  description: structured.description || 'AI-powered presentation generator',
  url: `${baseUrl}/${locale === defaultLocale ? '' : locale}`,
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web Browser',
  inLanguage: locale,
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
    description: structured.offerDescription || 'Free plan available',
  },
  featureList: structured.featureList || ['AI slide generation', 'Templates'],
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.7',
    reviewCount: '1500',
  },
  creator: {
    '@type': 'Organization',
    name: 'MyApp',
    url: 'https://MyApp.com',
  },
}

return (
  <>
    <Script
      id="webapplication-schema"
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppSchema) }}
    />
    {children}
  </>
)
```

**Dictionary keys needed:**
```json
{
  "home": {
    "structuredData": {
      "name": "MyApp",
      "description": "...",
      "offerDescription": "Free plan available",
      "featureList": ["AI slide generation", "Templates", "Export to PPTX"]
    }
  }
}
```

---

## BlogPosting Schema

```tsx
// src/app/[lang]/blog/[slug]/page.tsx
const blogSchema = {
  '@context': 'https://schema.org',
  '@type': 'BlogPosting',
  headline: blogPost.title,
  description: blogPost.excerpt,
  image: blogPost.featuredImage,
  datePublished: blogPost.publishedAt.toISOString(),
  dateModified: blogPost.updatedAt.toISOString(),
  inLanguage: locale,           // ← required: marks language version
  url: `${baseUrl}/${locale === defaultLocale ? '' : locale + '/'}blog/${blogPost.slug}`,
  author: {
    '@type': 'Organization',
    name: 'App Team',
    url: 'https://MyApp.com',
  },
  publisher: {
    '@type': 'Organization',
    name: 'MyApp',
    logo: {
      '@type': 'ImageObject',
      url: `${baseUrl}/images/logo.svg`,
    },
  },
  mainEntityOfPage: {
    '@type': 'WebPage',
    '@id': blogUrl,
  },
  wordCount: blogPost.wordCount,
  timeRequired: `PT${Math.ceil(blogPost.wordCount / 200)}M`,
}

return (
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{ __html: JSON.stringify(blogSchema) }}
  />
)
```

---

## FAQ Schema

Useful for feature pages, help pages, landing pages.

```tsx
const dict = await getDictionary(locale)
const faqs = dict?.featurePage?.faq?.items || []

const faqSchema = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  inLanguage: locale,
  mainEntity: faqs.map((faq: { question: string; answer: string }) => ({
    '@type': 'Question',
    name: faq.question,
    acceptedAnswer: {
      '@type': 'Answer',
      text: faq.answer,
    },
  })),
}
```

**Dictionary keys needed:**
```json
{
  "featurePage": {
    "faq": {
      "items": [
        {
          "question": "How does the AI generate slides?",
          "answer": "Our AI analyzes your input and creates structured slides..."
        }
      ]
    }
  }
}
```

---

## BreadcrumbList Schema

```tsx
const dict = await getDictionary(locale)
const breadcrumb = dict?.blog?.breadcrumb || {}

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    {
      '@type': 'ListItem',
      position: 1,
      name: breadcrumb.home || 'Home',
      item: `${baseUrl}${getLocalizedPath('/', locale)}`,
    },
    {
      '@type': 'ListItem',
      position: 2,
      name: breadcrumb.blog || 'Blog',
      item: `${baseUrl}${getLocalizedPath('/blog', locale)}`,
    },
    {
      '@type': 'ListItem',
      position: 3,
      name: blogPost.title,
      item: `${baseUrl}${getLocalizedPath(`/blog/${blogPost.slug}`, locale)}`,
    },
  ],
}
```

---

## How-To Schema

For tutorial/guide pages:

```tsx
const steps = dict?.howToPage?.steps || []

const howToSchema = {
  '@context': 'https://schema.org',
  '@type': 'HowTo',
  name: dict?.howToPage?.title || 'How to create slides',
  inLanguage: locale,
  description: dict?.howToPage?.description || '',
  step: steps.map((step: { name: string; text: string }, i: number) => ({
    '@type': 'HowToStep',
    position: i + 1,
    name: step.name,
    text: step.text,
  })),
}
```

---

## Script Placement

- **`<Script>` from `next/script`** — use in layouts (avoids hydration issues)
- **`<script>`** — use in page components for content-level schemas (BlogPosting, FAQ)
- Place before `</body>` or within the JSX return of Server Components
- Use unique `id` props when using `<Script>` to prevent duplicates
