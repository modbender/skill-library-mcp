# Common Schema Markup Templates

## Article
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": {"@type": "Person", "name": "Author Name"},
  "datePublished": "2026-01-01",
  "dateModified": "2026-01-15",
  "publisher": {"@type": "Organization", "name": "Company"},
  "description": "Article summary"
}
```

## FAQPage
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is X?",
      "acceptedAnswer": {"@type": "Answer", "text": "X is..."}
    }
  ]
}
```

## HowTo
```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to do X",
  "step": [
    {"@type": "HowToStep", "name": "Step 1", "text": "Do this first"},
    {"@type": "HowToStep", "name": "Step 2", "text": "Then do this"}
  ]
}
```

## LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Business Name",
  "address": {"@type": "PostalAddress", "streetAddress": "123 Main St", "addressLocality": "City", "addressRegion": "ST", "postalCode": "12345"},
  "telephone": "+1-555-555-5555",
  "openingHours": "Mo-Fr 09:00-17:00"
}
```

## Product
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "offers": {"@type": "Offer", "price": "49.99", "priceCurrency": "USD", "availability": "https://schema.org/InStock"}
}
```
