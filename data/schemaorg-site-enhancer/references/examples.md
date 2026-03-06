# Real-World Schema.org Examples

Complete JSON-LD examples for common site types. Copy and adapt.

## 1. Freelancer Portfolio

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Alex Rivera",
  "jobTitle": "Full-Stack Developer",
  "url": "https://alexrivera.dev",
  "sameAs": [
    "https://github.com/alexrivera",
    "https://linkedin.com/in/alexrivera",
    "https://twitter.com/alexrivera"
  ],
  "knowsAbout": [
    "JavaScript",
    "React",
    "Node.js",
    "Python",
    "PostgreSQL"
  ]
}
```

**Add to site head.** Also consider `Organization` if you operate as a business entity.

---

## 2. Tech Blog Article

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Implement OAuth 2.0 in Node.js",
  "description": "A step-by-step guide to adding OAuth 2.0 authentication to your Node.js application using Passport.js.",
  "author": {
    "@type": "Person",
    "name": "Alex Rivera",
    "url": "https://alexrivera.dev"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Alex Rivera Dev",
    "url": "https://alexrivera.dev",
    "logo": {
      "@type": "ImageObject",
      "url": "https://alexrivera.dev/logo.png"
    }
  },
  "datePublished": "2025-02-18T09:00:00Z",
  "dateModified": "2025-02-19T14:30:00Z",
  "image": "https://alexrivera.dev/images/oauth2-nodejs-cover.jpg",
  "url": "https://alexrivera.dev/blog/oauth2-nodejs",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://alexrivera.dev/blog/oauth2-nodejs"
  }
}
```

---

## 3. SaaS Product (Pricing Page)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "CodePilot AI",
  "description": "AI-powered code completion and review tool for professional developers.",
  "brand": {
    "@type": "Brand",
    "name": "CodePilot"
  },
  "offers": {
    "@type": "Offer",
    "price": "29.00",
    "priceCurrency": "USD",
    "priceValidUntil": "2025-12-31",
    "availability": "https://schema.org/InStock",
    "url": "https://codepilot.example.com/pricing"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "127"
  },
  "screenshot": "https://codepilot.example.com/screenshot.png",
  "url": "https://codepilot.example.com"
}
```

**Note:** Include `aggregateRating` only if reviews are visible on page.

---

## 4. Online Workshop (Event)

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Building Autonomous Agents Workshop",
  "description": "Learn to build AI agents with OpenClaw in this hands-on 2-hour workshop.",
  "startDate": "2025-03-15T18:00:00Z",
  "endDate": "2025-03-15T20:00:00Z",
  "eventStatus": "https://schema.org/EventScheduled",
  "location": {
    "@type": "VirtualLocation",
    "url": "https://zoom.us/j/1234567890"
  },
  "organizer": {
    "@type": "Organization",
    "name": "OpenClaw Community",
    "url": "https://openclaw.ai"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "validFrom": "2025-02-01T00:00:00Z"
  },
  "image": "https://openclaw.ai/images/workshop-banner.jpg",
  "url": "https://openclaw.ai/events/workshop-march2025"
}
```

For in-person events, use `Place` with `address`, `telephone`, `openingHoursSpecification`.

---

## 5. Local Business (Coffee Shop)

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Cozy Bean Café",
  "image": "https://cozybean.example.com/photo.jpg",
  "url": "https://cozybean.example.com",
  "telephone": "+1-555-123-4567",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "San Francisco",
    "addressRegion": "CA",
    "postalCode": "94102",
    "addressCountry": "US"
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
      ],
      "opens": "07:00",
      "closes": "19:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "Saturday",
        "Sunday"
      ],
      "opens": "08:00",
      "closes": "18:00"
    }
  ],
  "priceRange": "$$",
  "servesCuisine": ["Coffee", "Pastries", "Breakfast"]
}
```

---

## 6. FAQ Page

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is OpenClaw?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "OpenClaw is an open-source AI agent framework that enables autonomous agents to perform tasks, integrate with tools, and maintain continuity across sessions."
      }
    },
    {
      "@type": "Question",
      "name": "How do I get started?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Install the CLI with `npm install -g openclaw`, then run `openclaw init` to set up your workspace. See the documentation for detailed guides."
      }
    },
    {
      "@type": "Question",
      "name": "Is OpenClaw free?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, OpenClaw is open-source and free to use. Some integrations (LLM providers) may have their own costs."
      }
    }
  ]
}
```

---

## 7. Recipe (Baking Blog)

```json
{
  "@context": "https://schema.org",
  "@type": "Recipe",
  "name": "Grandma's Chocolate Chip Cookies",
  "description": "Soft, chewy chocolate chip cookies with a secret ingredient — love!",
  "author": {
    "@type": "Person",
    "name": "Maria Santos",
    "url": "https:// mariasbaking.blog"
  },
  "datePublished": "2025-02-10",
  "image": "https://mariasbaking.blog/images/cookies-hero.jpg",
  "recipeIngredient": [
    "2 1/4 cups all-purpose flour",
    "1 tsp baking soda",
    "1 tsp salt",
    "1 cup unsalted butter, softened",
    "3/4 cup granulated sugar",
    "3/4 cup packed brown sugar",
    "2 large eggs",
    "2 tsp vanilla extract",
    "2 cups chocolate chips"
  ],
  "recipeInstructions": [
    {
      "@type": "HowToStep",
      "name": "Prep",
      "text": "Preheat oven to 375°F (190°C). Line baking sheets with parchment paper."
    },
    {
      "@type": "HowToStep",
      "name": "Mix dry",
      "text": "Whisk flour, baking soda, and salt together in a bowl."
    },
    {
      "@type": "HowToStep",
      "name": "Cream",
      "text": "Beat butter and both sugars until light and fluffy. Add eggs and vanilla; beat until combined."
    },
    {
      "@type": "HowToStep",
      "name": "Combine",
      "text": "Gradually mix in flour mixture. Stir in chocolate chips."
    },
    {
      "@type": "HowToStep",
      "name": "Bake",
      "text": "Drop rounded tablespoons onto prepared sheets. Bake 9-11 minutes until golden. Cool on wire rack."
    }
  ],
  "prepTime": "PT20M",
  "cookTime": "PT10M",
  "totalTime": "PT30M",
  "recipeYield": "24 cookies",
  "nutrition": {
    "@type": "NutritionInformation",
    "calories": "150 calories per serving",
    "servingSize": "1 cookie"
  },
  "url": "https://mariasbaking.blog/recipes/chocolate-chip-cookies"
}
```

---

## 8. Product with Variants

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Noise-Cancelling Headphones",
  "description": "Wireless over-ear headphones with active noise cancellation and 30-hour battery.",
  "brand": {
    "@type": "Brand",
    "name": "SonicBlue"
  },
  "offers": {
    "@type": "Offer",
    "price": "299.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://shop.example.com/products/sb-noisecancelling-headphones",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.6",
    "reviewCount": "342"
  },
  "color": "Midnight Black",
  "sku": "SB-HP500-BK",
  "mpn": "HP500-BLK",
  "image": "https://shop.example.com/images/hp500-black.jpg",
  "url": "https://shop.example.com/products/sb-noisecancelling-headphones",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Battery Life",
      "value": "30 hours"
    },
    {
      "@type": "PropertyValue",
      "name": "Noise Cancellation",
      "value": "Active"
    }
  ]
}
```

---

## 9. Software Application

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "CodePilot CLI",
  "operatingSystem": "Linux, macOS, Windows",
  "applicationCategory": "DeveloperApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  },
  "downloadUrl": "https://github.com/openclaw/codepilot-cli/releases",
  "softwareVersion": "2.1.0",
  "author": {
    "@type": "Person",
    "name": "OpenClaw Team"
  },
  "description": "Command-line AI assistant for developers, with task automation, context awareness, and skill integrations.",
  "screenshot": "https://codepilot.dev/images/screenshot.png",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "89"
  }
}
```

---

## 10. How-To: Fix a Leaky Faucet

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Fix a Leaky Faucet",
  "description": "Replace a faucet washer to stop dripping in 10 minutes.",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Turn off water supply",
      "text": "Locate shut-off valves under sink and turn clockwise until tight.",
      "url": "https://example.com/guides/faucet-repair#step1",
      "image": "https://example.com/images/faucet-shutoff.jpg"
    },
    {
      "@type": "HowToStep",
      "name": "Remove faucet handle",
      "text": "Pry off decorative cap, then unscrew handle set screw. Lift handle off.",
      "url": "https://example.com/guides/faucet-repair#step2"
    },
    {
      "@type": "HowToStep",
      "name": "Replace washer",
      "text": "Remove old washer from valve stem. Install new washer of same size.",
      "url": "https://example.com/guides/faucet-repair#step3"
    },
    {
      "@type": "HowToStep",
      "name": "Reassemble and test",
      "text": "Reassemble handle, turn water back on, check for leaks.",
      "url": "https://example.com/guides/faucet-repair#step4"
    }
  ],
  "totalTime": "PT15M",
  "estimatedCost": "$5-10",
  "supply": [
    "Adjustable wrench",
    "Screwdriver (flathead)",
    "Replacement faucet washer (size 3/4-inch)",
    "Bucket (optional, for residual water)"
  ],
  "tool": ["Adjustable wrench", "Screwdriver"],
  "url": "https://example.com/guides/faucet-repair"
}
```

---

## Usage in HTML

Embed any of the above as:

```html
<head>
  <!-- other head content -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Your Site",
    "url": "https://yoursite.com"
  }
  </script>
</head>
```

For React/Next.js, use `dangerouslySetInnerHTML` or a component as shown in SKILL.md.

---

## Validation

Always test with:
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)

Fix warnings that affect eligibility (missing required fields, incorrect types). Minor warnings may be acceptable.