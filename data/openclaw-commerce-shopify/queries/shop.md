# Shopify Shop & Business Entity Queries

This guide helps you generate accurate GraphQL queries for fetching shop and business entity information from Shopify.

## Instructions for Query Generation

When a user requests shop or business entity information, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all requested fields are available in the API

## Official Documentation

### Shop Query Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/shop

**What to learn from this documentation:**
- Available shop fields and their data types
- Shop configuration and settings
- Billing and plan information
- Feature entitlements and capabilities
- Address and contact information
- Currency and locale settings

**Important sections to review:**
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/shop#return-fields
  - *Review only when you need to verify field availability or find new shop fields*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/shop#examples
  - *Review only when you need sample query patterns for complex shop scenarios*

### Business Entity Query Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/businessEntity

**What to learn from this documentation:**
- Business entity structure and fields
- Company and organization information
- Legal and tax details
- Contact and address information

**Note**: *Review this documentation only when working specifically with business entity data, not general shop information*

### Business Entities Query Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/businessEntities

**What to learn from this documentation:**
- Multiple business entities handling
- Filtering and searching business entities
- Business entity relationships

**Note**: *Review this documentation only when you need to work with multiple business entities or search/filter them*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when generating queries.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Query Cost Calculation**:
   - Simple fields: 1 point each
   - Connections (edges): Cost multiplied by requested count
   - Nested connections: Costs multiply
   - Formula: `cost = field_cost × first/last × depth`

3. **Best Practices for Query Generation**:
   - **Limit pagination size**: Use `first: 5-10` by default, not `first: 250`
   - **Request only needed fields**: Don't fetch all available fields
   - **Avoid deep nesting**: Minimize nested connections
   - **Use specific queries**: Prefer `shop` directly for basic information
   - **Implement pagination**: Use cursor-based pagination for large datasets

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches too many fields with nested connections
   query { shop { fulfillmentServices(first: 100) { ... } shopPolicies { ... } metafields(first: 50) { ... } } }
   
   # ✅ LOW COST - Fetches reasonable amount with needed fields only
   query { shop { id name email currencyCode plan { displayName } } }
   ```

## Query Generation Rules

### Variable Placeholders

When generating queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$FIRST$` | Number of items to fetch | 5 | `first: 10` |
| `$NAMESPACE$` | Metafield namespace | Ask user if not provided | `"custom"` |
| `$KEY$` | Metafield key | Ask user if not provided | `"banner_text"` |
| `$BUSINESS_ENTITY_ID$` | Specific business entity ID | Ask user if not provided | `gid://shopify/BusinessEntity/123456789` |

### Query Structure Template

```graphql
query {
  shop {
    # Only include fields user requested
    id
    name
    email
    # ... other requested fields
  }
}
```

## Response Guidelines

When generating a query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will show your store's basic information")
2. **Explain any limitations** in simple terms (e.g., "This shows your main store settings to keep things fast")
3. **Ask for clarification** if requirements are unclear, using business language
4. **Offer practical options** that relate to their business needs
5. **Avoid technical jargon** - no mentions of "cost", "pagination", "optimization", etc.

### Example Response Format

```
I'll help you get [business-friendly description of what user wants].

**Query:**
```graphql
query {
  shop {
    id
    name
    email
    currencyCode
    plan {
      displayName
    }
  }
}
```

**What this shows:**
- Your store name and email
- The currency you use
- Your current Shopify plan
- This keeps the response fast and easy to read

Would you like to:
- Add your store address?
- See your available features?
- Include billing information?
- Show customer account settings?
```

## Common Query Patterns

### Pattern 1: Basic Store Information
```graphql
query {
  shop {
    id
    name
    email
    myshopifyDomain
  }
}
```

### Pattern 2: Store Configuration
```graphql
query {
  shop {
    name
    currencyCode
    weightUnit
    ianaTimezone
    plan {
      displayName
      shopifyPlus
    }
  }
}
```

### Pattern 3: Store Address and Contact
```graphql
query {
  shop {
    name
    email
    contactEmail
    phone
    shopAddress {
      address1
      city
      country
      zip
    }
  }
}
```

### Pattern 4: Store Features and Capabilities
```graphql
query {
  shop {
    name
    plan {
      displayName
      shopifyPlus
    }
    features {
      giftCards
      subscriptions
      reports
      storefront
    }
  }
}
```

### Pattern 5: Business Entity Information
```graphql
query {
  businessEntity(id: "gid://shopify/BusinessEntity/123456789") {
    id
    name
    email
    phone
    address {
      address1
      city
      country
    }
  }
}
```

## Important Notes

- **Always check the documentation** before generating queries - field names and structures may change
- **Test queries** with essential fields first
- **Monitor rate limits** - if user needs large datasets, suggest batching
- **Request only necessary fields** - each field adds to the cost
- **Check field availability** - some fields require specific API versions or permissions
- **Business entity queries** are separate from shop queries and have different fields

## Learning Resources

- **GraphQL Admin API Overview**: https://shopify.dev/docs/api/admin-graphql
  - *Review only when you need general GraphQL API understanding beyond shop data*
- **API Rate Limits**: https://shopify.dev/docs/api/usage/rate-limits
  - *Review only when you encounter rate limiting issues or need optimization guidance*
- **Pagination Best Practices**: https://shopify.dev/docs/api/usage/pagination-graphql
  - *Review only when implementing pagination for large datasets*
- **Search Syntax**: https://shopify.dev/docs/api/usage/search-syntax
  - *Review only when building complex search filters for business entities*
- **API Versioning**: https://shopify.dev/docs/api/usage/versioning
  - *Review only when you encounter API compatibility issues or need specific version features*

## Troubleshooting

If a query fails or returns unexpected results:

1. **Verify field names** against current API documentation
2. **Check query structure** - ensure proper GraphQL syntax
3. **Validate ID format** - must be full GID (e.g., `gid://shopify/BusinessEntity/123`)
4. **Review rate limit response** - if throttled, reduce query complexity
5. **Check API version** - some fields may not exist in older versions
6. **Verify permissions** - ensure app has required scopes

---

**Remember**: The goal is to generate efficient, accurate queries that respect rate limits while providing exactly what the user needs. When in doubt, consult the official documentation links provided above.

## Agent Instructions

**Important:** As an AI agent using this skill, follow these guidelines to ensure a smooth and effective user experience.

### Handling GraphQL Errors
If you encounter a GraphQL error after sending a query, do not give up immediately. The error may be due to a misunderstanding of the required query structure or parameters.

1.  **Re-read the Documentation:** Go back to the specific documentation file for the query you are trying to execute (e.g., `queries/createProduct.md`).
2.  **Analyze the Query:** Carefully review the required fields, input structures, and examples provided in the documentation.
3.  **Retry the Query:** Construct a new query based on your revised understanding and try the operation again.

### Fulfilling User Requirements
Your primary goal is to fulfill the user's request completely.

- **Strive for Completion:** Always attempt to meet all aspects of the user's request.
- **Communicate Limitations:** If a specific part of the request cannot be fulfilled due to API limitations or other constraints, you must clearly communicate this to the user.
- **Provide Alternatives:** When you cannot complete a task, explain what you *were* able to do and suggest a clear manual alternative for the part you could not complete. For example: "I have created the product, but I was unable to set the custom inventory policy. You can set this manually in your Shopify Admin under the product's inventory settings."
