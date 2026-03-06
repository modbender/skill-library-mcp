# Schema.org Types Reference

## Organization

**Purpose**: Establish brand entity identity

**Use On**: Homepage, About page, Contact page

**Required Fields**:
- `@type`: "Organization"
- `name`: Company name
- `url`: Website URL
- `logo`: Logo image URL

**Recommended Fields**:
- `description`: 1-2 sentence factual description
- `sameAs`: Social media profiles
- `foundingDate`: YYYY-MM-DD
- `contactPoint`: Customer service info

**GEO Impact**: 🔴 Critical — AI uses this to identify and attribute content to your brand

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Acme Corp",
  "url": "https://acme.com",
  "logo": "https://acme.com/logo.png",
  "description": "Cloud infrastructure platform for developer teams",
  "foundingDate": "2015",
  "sameAs": [
    "https://twitter.com/acme",
    "https://linkedin.com/company/acme"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "support@acme.com",
    "availableLanguage": ["English", "Spanish"]
  }
}
```

---

## WebSite

**Purpose**: Define site structure and enable site search

**Use On**: Homepage only

**Required Fields**:
- `@type`: "WebSite"
- `name`: Site name
- `url`: Site URL

**Recommended Fields**:
- `potentialAction`: SearchAction for site search
- `publisher`: Reference to Organization

**GEO Impact**: 🟡 High — enables AI to reference your site search functionality

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Acme Documentation",
  "url": "https://docs.acme.com",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://docs.acme.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

---

## Article / BlogPosting

**Purpose**: Mark editorial content for AI citation

**Use On**: Blog posts, news articles, press releases

**Required Fields**:
- `@type`: "Article" or "BlogPosting"
- `headline`: Article title
- `author`: Person or Organization
- `datePublished`: Publication date

**Recommended Fields**:
- `description`: 150-char summary
- `image`: Featured image
- `publisher`: Organization reference
- `dateModified`: Last updated
- `articleBody`: Full text (for AI training)

**GEO Impact**: 🟡 High — improves content citability and attribution

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Implementing Schema Markup for AI Search",
  "description": "Guide to adding structured data for better AI visibility",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "url": "https://acme.com/team/jane"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Acme Corp",
    "logo": {
      "@type": "ImageObject",
      "url": "https://acme.com/logo.png"
    }
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-01-20",
  "url": "https://acme.com/blog/schema-markup-guide"
}
```

---

## FAQPage

**Purpose**: Structure Q&A content for AI answers

**Use On**: FAQ pages, support hubs, help centers

**Required Fields**:
- `@type`: "FAQPage"
- `mainEntity`: Array of Question/Answer pairs

**Question Fields**:
- `@type`: "Question"
- `name`: The question text
- `acceptedAnswer`: Answer object

**Answer Fields**:
- `@type`: "Answer"
- `text`: Full answer (can include HTML)

**GEO Impact**: 🔴 Critical — AI pulls directly from FAQPage for Q&A responses

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Schema.org markup?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Schema.org markup is structured data vocabulary that helps search engines and AI systems understand webpage content. It uses JSON-LD format to annotate entities like organizations, articles, products, and FAQs."
      }
    }
  ]
}
```

**Tips**:
- Match question text exactly to what's shown on page
- Make answers comprehensive — AI reads these directly
- Can include HTML formatting in answer text
- 3-10 questions per page works best

---

## Product

**Purpose**: Enable AI shopping and product citations

**Use On**: Product pages, pricing pages

**Required Fields**:
- `@type`: "Product"
- `name`: Product name
- `offers`: Price and availability

**Recommended Fields**:
- `description`: Product description
- `brand`: Brand reference
- `image`: Product images
- `review`: Customer reviews
- `aggregateRating`: Overall rating

**GEO Impact**: 🟡 High — enables AI to cite specific products with prices

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Acme Pro Plan",
  "description": "Team collaboration platform with unlimited projects",
  "brand": {
    "@type": "Brand",
    "name": "Acme"
  },
  "offers": {
    "@type": "Offer",
    "price": "99.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2024-12-31"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "127"
  }
}
```

---

## HowTo

**Purpose**: Structure step-by-step instructions

**Use On**: Tutorials, guides, recipes, instructions

**Required Fields**:
- `@type`: "HowTo"
- `name`: Guide title
- `step`: Array of steps

**Step Fields**:
- `@type`: "HowToStep"
- `name`: Step title
- `text`: Step instructions
- `url`: Anchor link to step

**Recommended Fields**:
- `description`: Overview
- `totalTime`: Duration (ISO 8601)
- `estimatedCost`: Cost estimate
- `tool`: Required tools
- `supply`: Required materials

**GEO Impact**: 🟡 High — AI uses HowTo for step-by-step answer generation

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Add Schema Markup",
  "description": "Step-by-step guide to implementing JSON-LD",
  "totalTime": "PT30M",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Identify content type",
      "text": "Determine if your content is an Article, Product, FAQ, etc.",
      "url": "https://example.com/guide#step1"
    },
    {
      "@type": "HowToStep",
      "name": "Generate markup",
      "text": "Use a schema generator to create JSON-LD code",
      "url": "https://example.com/guide#step2"
    }
  ]
}
```

---

## BreadcrumbList

**Purpose**: Show page hierarchy

**Use On**: All pages (especially deep pages)

**Required Fields**:
- `@type`: "BreadcrumbList"
- `itemListElement`: Array of breadcrumbs

**Item Fields**:
- `@type`: "ListItem"
- `position`: Number in sequence
- `name`: Breadcrumb label
- `item`: URL

**GEO Impact**: 🔵 Medium — helps AI understand site structure

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://acme.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Products",
      "item": "https://acme.com/products"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Pro Plan",
      "item": "https://acme.com/products/pro"
    }
  ]
}
```

---

## VideoObject

**Purpose**: Mark video content

**Use On**: Pages with embedded videos

**Required Fields**:
- `@type`: "VideoObject"
- `name`: Video title
- `description`: Video description
- `thumbnailUrl`: Thumbnail image

**Recommended Fields**:
- `uploadDate`: Publication date
- `duration`: Length (ISO 8601)
- `contentUrl`: Direct video URL
- `embedUrl`: Embed URL

**GEO Impact**: 🔵 Medium — enables video citations in AI responses

---

## ImageObject

**Purpose**: Mark important images

**Use On**: Galleries, featured images, infographics

**Required Fields**:
- `@type`: "ImageObject"
- `url`: Image URL

**Recommended Fields**:
- `name`: Image title
- `description`: Alt text
- `author`: Creator
- `contentLocation`: Where photo was taken

**GEO Impact**: 🔵 Medium — enables image citations in multimodal AI

---

## LocalBusiness

**Purpose**: Mark physical business locations

**Use On**: Location pages, contact pages with addresses

**Required Fields**:
- `@type`: "LocalBusiness" (or subtype)
- `name`: Business name
- `address`: PostalAddress

**Subtypes**:
- Restaurant
- Store
- Dentist
- Attorney
- RealEstateAgent
- And many more...

**GEO Impact**: 🔵 Medium — critical for local AI search

**Example**:
```json
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "name": "Acme Bistro",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "San Francisco",
    "addressRegion": "CA",
    "postalCode": "94102"
  },
  "telephone": "+1-555-123-4567",
  "openingHours": "Mo-Sa 11:00-22:00"
}
```

---

## Schema Selection Guide

| Content Type | Primary Schema | Secondary Schema(s) |
|--------------|----------------|---------------------|
| Homepage | Organization | WebSite |
| About Page | Organization | — |
| Blog Post | BlogPosting | BreadcrumbList |
| News Article | Article | BreadcrumbList |
| Product Page | Product | Organization, BreadcrumbList |
| FAQ Page | FAQPage | BreadcrumbList |
| Tutorial | HowTo | BreadcrumbList |
| Contact Page | Organization | LocalBusiness (if applicable) |
| Category Page | ItemList | BreadcrumbList |
| Video Page | VideoObject | Article (if blog post) |