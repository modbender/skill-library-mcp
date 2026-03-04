# Schema Types Quick Reference

This document provides quick parameters for generating each supported schema type using `generate_jsonld.py`.

## Organization

```python
generate_organization(
    name="Company Name",
    url="https://example.com",
    logo="https://example.com/logo.png",        # optional
    same_as=["https://twitter.com/handle"]      # optional, list of social/profile URLs
)
```

**Required:** `name`, `url`  
**Common optional:** `logo`, `sameAs`, `contactPoint`, `address`

---

## Person

```python
generate_person(
    name="Full Name",
    url="https://example.com/about",            # optional
    job_title="Senior Developer",               # optional
    same_as=["https://linkedin.com/in/..."]    # optional
)
```

**Required:** `name`  
**Common optional:** `url`, `jobTitle`, `sameAs`, `knowsAbout` (skills)

---

## WebSite

```python
generate_website(
    name="Site Name",
    url="https://example.com",
    search_action_url="https://example.com/search"  # optional, adds SearchAction
)
```

**Required:** `name`, `url`  
**Optional:** `potentialAction` (SearchAction for searchable sites)

---

## WebPage

```python
generate_webpage(
    title="Page Title",
    url="https://example.com/page",
    description="Brief description",             # optional
    date_published="2025-02-20T10:00:00Z",     # optional, ISO 8601
    date_modified="2025-02-20T12:00:00Z"      # optional
)
```

**Required:** `name` (title), `url`  
**Optional:** `description`, `datePublished`, `dateModified`

---

## Article / BlogPosting

```python
generate_article(
    headline="Article Headline",
    url="https://example.com/article",
    author={"@type": "Person", "name": "Author Name"},
    date_published="2025-02-20T10:00:00Z",
    image="https://example.com/image.jpg",      # optional
    publisher={"@type": "Organization", "name": "Pub", "url": "..."},  # optional
    description="Article summary..."            # optional
)

generate_blog_posting(
    headline="Blog Title",
    url="https://example.com/blog/post",
    author_name="Jane Doe",
    date_published="2025-02-20T10:00:00Z"
)
```

**Required (Article):** `headline`, `author`, `datePublished`, `url`  
**Note:** BlogPosting is a subtype of Article; usage same but @type differs.

---

## Product

```python
generate_product(
    name="Product Name",
    description="Detailed description...",
    brand="Brand Name" or {"@type": "Brand", "name": "..."},
    price=49.99,
    currency="USD",
    availability="https://schema.org/InStock",  # or OutOfStock, PreOrder, etc.
    sku="SKU123",                              # optional
    image="https://example.com/product.jpg",   # optional
    url="https://example.com/product"          # optional
)
```

**Required:** `name`, `description`, `brand`, `offers` (price, priceCurrency, availability)  
**Common optional:** `sku`, `image`, `url`, `aggregateRating`

---

## Event

```python
generate_event(
    name="Event Name",
    start_date="2025-03-15T19:00:00Z",
    end_date="2025-03-15T21:00:00Z",           # optional
    location={"@type": "Place", "name": "Venue", "address": "123 Main St"},
    organizer={"@type": "Organization", "name": "Org", "url": "..."},
    description="What it's about...",
    event_status="https://schema.org/EventScheduled",  # optional
    image="https://example.com/event.jpg"      # optional
)
```

**Required:** `name`, `startDate`  
**Common optional:** `endDate`, `location`, `organizer`, `description`, `eventStatus`

---

## FAQPage

```python
generate_faq([
    ("What is your return policy?", "We accept returns within 30 days."),
    ("How long does shipping take?", "3-5 business days."),
])
```

**Required:** List of (question, answer) tuples  
**Output:** `FAQPage` with `mainEntity` array of `Question` objects

---

## Recipe

```python
generate_recipe(
    name="Chocolate Chip Cookies",
    url="https://example.com/recipe",
    author="Chef Name",
    date_published="2025-02-20",
    description="Delicious homemade cookies",
    prep_time="PT30M",              # optional, ISO 8601 duration
    cook_time="PT15M",              # optional
    total_time="PT45M",             # optional
    ingredients=["1 cup flour", "2 eggs", "..."],
    instructions=[{"@type": "HowToStep", "text": "Preheat oven..."}, ...],
    image="https://example.com/recipe.jpg"  # optional
)
```

**Required:** `name`, `author`, `datePublished`  
**Optional:** `prepTime`, `cookTime`, `totalTime`, `recipeIngredient`, `recipeInstructions`, `image`

---

## HowTo

```python
generate_how_to(
    name="How to Tie a Tie",
    url="https://example.com/how-to",
    step_list=[
        {"@type": "HowToStep", "name": "Step 1", "text": "Place tie around neck..."},
        {"@type": "HowToStep", "name": "Step 2", "text": "Cross wide end over narrow..."}
    ],
    total_time="PT5M",               # optional
    estimated_cost="$20",            # optional
    supply=["Tie"],                  # optional
    tool=["Mirror"]                  # optional
)
```

**Required:** `name`, `url`, `step`  
**Optional:** `totalTime`, `estimatedCost`, `supply`, `tool`

---

## Notes

- All date/time fields should be ISO 8601 (e.g., `"2025-02-20T10:00:00Z"`)
- Duration fields (prepTime, totalTime, etc.) use ISO 8601 duration format: `"PT30M"` (30 minutes), `"PT1H30M"` (1 hour 30 min)
- For more property options, see [schema.org](https://schema.org/) directly.