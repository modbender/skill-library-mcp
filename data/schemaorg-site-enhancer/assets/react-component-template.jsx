'use client';

import React from 'react';

/**
 * JsonLd Component for Next.js / React
 *
 * Usage:
 *   <JsonLd data={{
 *     "@context": "https://schema.org",
 *     "@type": "Organization",
 *     "name": "Your Company",
 *     "url": "https://example.com"
 *   }} />
 *
 * Renders: <script type="application/ld+json">...</script>
 */
export function JsonLd({ data }: { data: Record<string, any> }) {
  const jsonLd = JSON.stringify(data);
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: jsonLd }}
    />
  );
}

/**
 * Pre-built component for Organization schema
 */
export function OrganizationJsonLd({
  name,
  url,
  logo,
  sameAs,
  contactPoint,
}: {
  name: string;
  url: string;
  logo?: string;
  sameAs?: string[];
  contactPoint?: Array<{
    '@type': string;
    telephone?: string;
    contactType?: string;
    email?: string;
  }>;
}) {
  const data: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name,
    url,
  };
  if (logo) data.logo = logo;
  if (sameAs) data.sameAs = sameAs;
  if (contactPoint) data.contactPoint = contactPoint;
  return <JsonLd data={data} />;
}

/**
 * Pre-built component for Article/BlogPosting
 */
export function ArticleJsonLd({
  headline,
  url,
  author,
  datePublished,
  dateModified,
  image,
  publisher,
  description,
}: {
  headline: string;
  url: string;
  author: { name: string; url?: string } | { name: string };
  datePublished: string;
  dateModified?: string;
  image?: string;
  description?: string;
  publisher?: {
    name: string;
    url?: string;
    logo?: string;
  };
}) {
  const authorObj = typeof author === 'string' ? { name: author } : author;
  const data: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline,
    author: authorObj,
    datePublished,
    url,
  };
  if (dateModified) data.dateModified = dateModified;
  if (image) data.image = image;
  if (description) data.description = description;
  if (publisher) {
    data.publisher = { '@type': 'Organization', ...publisher };
  }
  return <JsonLd data={data} />;
}

/**
 * Pre-built component for Product
 */
export function ProductJsonLd({
  name,
  description,
  brand,
  price,
  currency = 'USD',
  availability,
  sku,
  image,
  url,
  rating,
  reviewCount,
}: {
  name: string;
  description: string;
  brand: string;
  price: number;
  currency?: string;
  availability: 'https://schema.org/InStock' | 'https://schema.org/OutOfStock' | 'https://schema.org/PreOrder';
  sku?: string;
  image?: string;
  url?: string;
  rating?: number;
  reviewCount?: number;
}) {
  const data: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name,
    description,
    brand: { '@type': 'Brand', name: brand },
    offers: {
      '@type': 'Offer',
      price,
      priceCurrency: currency,
      availability,
    },
  };
  if (sku) data.sku = sku;
  if (image) data.image = image;
  if (url) data.url = url;
  if (rating !== undefined && reviewCount) {
    data.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: rating,
      reviewCount,
    };
  }
  return <JsonLd data={data} />;
}

/**
 * Pre-built component for FAQPage
 */
export function FaqPageJsonLd({
  questions,
}: {
  questions: Array<{ question: string; answer: string }>;
}) {
  const data: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: questions.map(q => ({
      '@type': 'Question',
      name: q.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: q.answer,
      },
    })),
  };
  return <JsonLd data={data} />;
}

/**
 * Pre-built component for BreadcrumbList
 */
export function BreadcrumbJsonLd({
  items,
}: {
  items: Array<{ name: string; url: string }>;
}) {
  const data: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
  return <JsonLd data={data} />;
}

/**
 * Pre-built component for WebSite with SearchAction
 */
export function WebSiteJsonLd({
  name,
  url,
  searchUrl,
}: {
  name: string;
  url: string;
  searchUrl: string; // with {search_term_string} placeholder, e.g., "https://example.com/search?q={search_term_string}"
}) {
  const data = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name,
    url,
    potentialAction: {
      '@type': 'SearchAction',
      target: searchUrl,
      'query-input': 'required name=search_term_string',
    },
  };
  return <JsonLd data={data} />;
}

/**
 * Example: Using multiple schema types on one page
 *
 * export default function Page() {
 *   return (
 *     <>
 *       <OrganizationJsonLd name="MyCo" url="https://myco.com" />
 *       <WebSiteJsonLd name="MyCo Docs" url="https://docs.myco.com" searchUrl="https://docs.myco.com/search?q={search_term_string}" />
 *       <ArticleJsonLd ... />
 *     </>
 *   );
 * }
 *
 * All components render <script type="application/ld+json"> in the page.
 */