# Schema Examples by Industry

## SaaS / Technology

### Homepage — Organization + WebSite

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "name": "Vercel",
      "url": "https://vercel.com",
      "logo": "https://assets.vercel.com/image/upload/v1662130559/front/vercel-logo.svg",
      "description": "Cloud platform for frontend developers and serverless deployment",
      "sameAs": [
        "https://twitter.com/vercel",
        "https://github.com/vercel",
        "https://linkedin.com/company/vercel"
      ],
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "sales",
        "email": "sales@vercel.com"
      }
    },
    {
      "@type": "WebSite",
      "name": "Vercel",
      "url": "https://vercel.com",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://vercel.com/docs/search?query={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  ]
}
```

### Pricing Page — Product + FAQ

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Product",
      "name": "Vercel Pro Plan",
      "description": "Team collaboration with advanced features and priority support",
      "brand": {
        "@type": "Brand",
        "name": "Vercel"
      },
      "offers": {
        "@type": "Offer",
        "price": "20.00",
        "priceCurrency": "USD",
        "priceValidUntil": "2024-12-31",
        "availability": "https://schema.org/InStock",
        "description": "Per user, per month"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What's included in the Pro plan?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Pro includes team collaboration, priority support, 1TB bandwidth, and unlimited personal projects."
          }
        }
      ]
    }
  ]
}
```

### Documentation — Article + Breadcrumb

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "TechArticle",
      "headline": "Getting Started with Next.js",
      "description": "Learn how to build your first Next.js application",
      "author": {
        "@type": "Organization",
        "name": "Vercel"
      },
      "publisher": {
        "@type": "Organization",
        "name": "Vercel",
        "logo": {
          "@type": "ImageObject",
          "url": "https://assets.vercel.com/logo.png"
        }
      },
      "datePublished": "2024-01-15",
      "dateModified": "2024-02-01",
      "dependencies": "Node.js 18.17 or later"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Docs",
          "item": "https://nextjs.org/docs"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Getting Started",
          "item": "https://nextjs.org/docs/getting-started"
        }
      ]
    }
  ]
}
```

---

## E-commerce

### Product Page — Complete Product Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Sony WH-1000XM5 Wireless Headphones",
  "image": [
    "https://example.com/images/headphones-1x1.jpg",
    "https://example.com/images/headphones-4x3.jpg",
    "https://example.com/images/headphones-16x9.jpg"
  ],
  "description": "Industry-leading noise canceling with 30-hour battery life and crystal clear hands-free calling",
  "sku": "WH1000XM5/B",
  "mpn": "WH1000XM5",
  "gtin13": "4548736132345",
  "brand": {
    "@type": "Brand",
    "name": "Sony"
  },
  "color": "Black",
  "material": "Plastic, Synthetic Leather",
  "weight": {
    "@type": "QuantitativeValue",
    "value": "250",
    "unitCode": "g"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.6",
    "reviewCount": "2847",
    "bestRating": "5",
    "worstRating": "1"
  },
  "review": [
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "John D."
      },
      "datePublished": "2024-01-10",
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5"
      },
      "reviewBody": "Best noise canceling I've ever experienced. Battery lasts forever."
    }
  ],
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/sony-wh1000xm5",
    "price": "379.99",
    "priceCurrency": "USD",
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Electronics Store"
    },
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": "0",
        "currency": "USD"
      },
      "deliveryTime": {
        "@type": "ShippingDeliveryTime",
        "handlingTime": {
          "@type": "QuantitativeValue",
          "minValue": "0",
          "maxValue": "1",
          "unitCode": "d"
        },
        "transitTime": {
          "@type": "QuantitativeValue",
          "minValue": "1",
          "maxValue": "5",
          "unitCode": "d"
        }
      }
    }
  }
}
```

### Category Page — ItemList

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Product",
        "name": "Sony WH-1000XM5",
        "url": "https://example.com/products/sony-wh1000xm5"
      }
    },
    {
      "@type": "ListItem",
      "position": 2,
      "item": {
        "@type": "Product",
        "name": "Bose QuietComfort Ultra",
        "url": "https://example.com/products/bose-qc-ultra"
      }
    }
  ]
}
```

---

## Publishing / Media

### News Article

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "SpaceX Successfully Launches Starship Test Flight",
  "description": "The most powerful rocket ever built reaches space for the first time",
  "image": [
    "https://example.com/images/spacex-launch-16x9.jpg",
    "https://example.com/images/spacex-launch-4x3.jpg",
    "https://example.com/images/spacex-launch-1x1.jpg"
  ],
  "datePublished": "2024-03-14T09:00:00-05:00",
  "dateModified": "2024-03-14T11:30:00-05:00",
  "author": [
    {
      "@type": "Person",
      "name": "Sarah Johnson",
      "url": "https://example.com/authors/sarah-johnson"
    }
  ],
  "publisher": {
    "@type": "Organization",
    "name": "Tech News Daily",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "dateline": "Cape Canaveral, FL"
}
```

### Blog Post — With Author Bios

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "10 Advanced TypeScript Patterns for React Developers",
  "description": "Learn advanced TypeScript techniques to improve your React code quality",
  "image": "https://example.com/images/typescript-react.jpg",
  "datePublished": "2024-02-20",
  "dateModified": "2024-02-22",
  "author": {
    "@type": "Person",
    "name": "Alex Chen",
    "url": "https://example.com/authors/alex-chen",
    "jobTitle": "Senior Frontend Engineer",
    "worksFor": {
      "@type": "Organization",
      "name": "TechCorp"
    }
  },
  "publisher": {
    "@type": "Organization",
    "name": "DevBlog",
    "logo": "https://example.com/logo.png"
  },
  "articleBody": "TypeScript has become the standard...",
  "wordCount": 2500,
  "articleSection": "JavaScript",
  "keywords": ["TypeScript", "React", "JavaScript", "Frontend"]
}
```

---

## Local Business

### Restaurant

```json
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "name": "The Golden Spoon",
  "image": [
    "https://example.com/restaurant-exterior.jpg",
    "https://example.com/dining-room.jpg"
  ],
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "San Francisco",
    "addressRegion": "CA",
    "postalCode": "94102",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "37.7749",
    "longitude": "-122.4194"
  },
  "telephone": "+1-415-555-0123",
  "url": "https://goldenspoon.example.com",
  "menu": "https://goldenspoon.example.com/menu",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"],
      "opens": "11:30",
      "closes": "22:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Friday", "Saturday"],
      "opens": "11:30",
      "closes": "23:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": "Sunday",
      "opens": "10:00",
      "closes": "21:00"
    }
  ],
  "priceRange": "$$",
  "servesCuisine": ["Italian", "Mediterranean"],
  "acceptsReservations": "True"
}
```

### Medical Practice

```json
{
  "@context": "https://schema.org",
  "@type": "Dentist",
  "name": "Bright Smile Dental",
  "description": "Family dental practice offering comprehensive care",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "456 Oak Avenue",
    "addressLocality": "Oakland",
    "addressRegion": "CA",
    "postalCode": "94610"
  },
  "telephone": "+1-510-555-0199",
  "openingHours": ["Mo-Fr 08:00-17:00", "Sa 09:00-14:00"],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "127"
  }
}
```

---

## Education

### Online Course

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "Advanced React Patterns",
  "description": "Master advanced React patterns including compound components, render props, and custom hooks",
  "provider": {
    "@type": "Organization",
    "name": "Frontend Masters",
    "sameAs": "https://frontendmasters.com"
  },
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "duration": "PT8H",
    "instructor": {
      "@type": "Person",
      "name": "Ryan Florence"
    }
  },
  "offers": {
    "@type": "Offer",
    "price": "39",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
```

---

## Events

### Conference/Event

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "React Conference 2024",
  "startDate": "2024-05-15T09:00:00-07:00",
  "endDate": "2024-05-17T18:00:00-07:00",
  "eventAttendanceMode": "https://schema.org/MixedEventAttendanceMode",
  "eventStatus": "https://schema.org/EventScheduled",
  "location": [
    {
      "@type": "VirtualLocation",
      "url": "https://reactconf.com/live"
    },
    {
      "@type": "Place",
      "name": "Moscone Center",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "747 Howard Street",
        "addressLocality": "San Francisco",
        "addressRegion": "CA",
        "postalCode": "94103"
      }
    }
  ],
  "image": "https://reactconf.com/images/og-image.jpg",
  "description": "The biggest React conference of the year featuring keynotes from the React core team",
  "offers": {
    "@type": "Offer",
    "url": "https://reactconf.com/tickets",
    "price": "899",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "validFrom": "2024-01-01T00:00:00-07:00"
  },
  "performer": {
    "@type": "PerformingGroup",
    "name": "React Core Team"
  },
  "organizer": {
    "@type": "Organization",
    "name": "React Events LLC",
    "url": "https://reactconf.com"
  }
}
```

---

## Video Content

### YouTube Video

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "How to Build a Full-Stack App with Next.js",
  "description": "Complete tutorial on building a production-ready app",
  "thumbnailUrl": [
    "https://i.ytimg.com/vi/ABC123/maxresdefault.jpg",
    "https://i.ytimg.com/vi/ABC123/sddefault.jpg"
  ],
  "uploadDate": "2024-01-15",
  "duration": "PT45M30S",
  "contentUrl": "https://www.youtube.com/watch?v=ABC123",
  "embedUrl": "https://www.youtube.com/embed/ABC123",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": 152000
  },
  "author": {
    "@type": "Person",
    "name": "Fireship"
  }
}
```