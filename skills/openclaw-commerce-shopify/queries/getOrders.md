# Shopify Order & Draft Order Queries

This guide helps you generate accurate GraphQL queries for fetching order and draft order information from Shopify.

## Instructions for Query Generation

When a user requests order or draft order information, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all requested fields are available in the API

## Official Documentation

### Orders Query Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders

**What to learn from this documentation:**
- Available query arguments (`first`, `last`, `query`, `sortKey`, `reverse`, etc.)
- All available filters for the `query` argument
- Complete field structure and nested objects
- Pagination using `edges`, `cursor`, and `pageInfo`
- Examples of common query patterns

**Important sections to review:**
- Query filters: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#argument-query
  - *Review only when you need specific filter syntax or new filter types*
- Sort keys: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#argument-sortKey
  - *Review only when you need alternative sorting options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#return-fields
  - *Review only when you need to verify field availability or find new fields*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#examples
  - *Review only when you need sample query patterns for complex scenarios*

### Draft Orders Query Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrders

**What to learn from this documentation:**
- Available query arguments specific to draft orders
- Draft order-specific filters
- Draft order field structure
- Status values and their meanings

**Note**: *Review this documentation only when working specifically with draft orders, not regular orders*

### Single Order/Draft Order Queries
- **Order by ID**: https://shopify.dev/docs/api/admin-graphql/latest/queries/order
  - *Use only when you need to fetch a specific order by its ID instead of querying multiple orders*
- **Draft Order by ID**: https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrder
  - *Use only when you need to fetch a specific draft order by its ID instead of querying multiple draft orders*

### Specialized Order Queries (Use Only When Needed)
- **Orders Count**: https://shopify.dev/docs/api/admin-graphql/latest/queries/ordersCount
  - *Use only when you need to count orders without fetching order data*
- **Order Payment Status**: https://shopify.dev/docs/api/admin-graphql/latest/queries/orderPaymentStatus
  - *Use only when you need specific payment status information for orders*

### Specialized Draft Order Queries (Use Only When Needed)
- **Draft Order Tag**: https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrderTag
  - *Use only when you need to manage or retrieve draft order tags*
- **Draft Orders Count**: https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrdersCount
  - *Use only when you need to count draft orders without fetching draft order data*
- **Draft Order Available Delivery Options**: https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrderAvailableDeliveryOptions
  - *Use only when you need delivery/shipping options for specific draft orders*

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
   - **Use specific queries**: Prefer `order(id:)` over `orders()` when fetching single order
   - **Implement pagination**: Use cursor-based pagination for large datasets

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches too many orders with many fields
   query { orders(first: 250) { edges { node { id name email customer { ... } lineItems(first: 100) { ... } } } } }
   
   # ✅ LOW COST - Fetches reasonable amount with needed fields only
   query { orders(first: 10) { edges { node { id name createdAt } } } }
   ```

## Query Generation Rules

### Variable Placeholders

When generating queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$FIRST$` | Number of orders to fetch | 5 | `first: 10` |
| `$LAST$` | Number of recent orders | 5 | `last: 5` |
| `$ORDER_ID$` | Specific order ID | Ask user if not provided | `gid://shopify/Order/123456789` |
| `$DRAFT_ORDER_ID$` | Specific draft order ID | Ask user if not provided | `gid://shopify/DraftOrder/987654321` |
| `$QUERY_FILTERS$` | Search filters | Empty string if not needed | `status:open AND created_at:>=2024-01-01` |
| `$SORT_KEY$` | Sort order | `PROCESSED_AT` for orders | `CREATED_AT`, `TOTAL_PRICE` |

### Query Structure Template

```graphql
query {
  orders(
    first: $FIRST$
    query: "$QUERY_FILTERS$"
    sortKey: $SORT_KEY$
  ) {
    edges {
      cursor
      node {
        # Only include fields user requested
        id
        name
        # ... other requested fields
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Response Guidelines

When generating a query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will show your recent orders")
3. **Explain any limitations** in simple terms (e.g., "This shows up to 10 orders to keep things fast")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "pagination", "optimization", etc.

### Example Response Format

```
I'll help you get [business-friendly description of what user wants].

**Query:**
```graphql
query {
  orders(first: 10, query: "status:open") {
    edges {
      node {
        id
        name
        createdAt
      }
    }
  }
}
```

**What this shows:**
- Your first 10 open orders
- Order number and date for each order
- This keeps the response fast and easy to read

Would you like to:
- See more orders? (I can show up to 50 at a time)
- Add customer information? (like customer name and email)
- Filter by specific date range?
- Show only paid orders?
```

## Common Query Patterns

### Pattern 1: Fetch Recent Orders
```graphql
query {
  orders(first: 10, sortKey: CREATED_AT) {
    edges {
      node { id name createdAt }
    }
  }
}
```

### Pattern 2: Search Orders by Customer
```graphql
query {
  orders(first: 10, query: "customer_id:123456") {
    edges {
      node { id name customer { email } }
    }
  }
}
```

### Pattern 3: Get Specific Order Details
```graphql
query {
  order(id: "gid://shopify/Order/123456789") {
    id
    name
    createdAt
    totalPriceSet {
      shopMoney { amount currencyCode }
    }
  }
}
```

## Important Notes

- **Always check the documentation** before generating queries - field names and structures may change
- **Test queries** with small datasets first (use `first: 1-5`)
- **Monitor rate limits** - if user needs large datasets, suggest batching
- **Use cursor pagination** for fetching all orders, not increasing `first` value
- **Request only necessary fields** - each field adds to the cost
- **Validate filter syntax** - refer to documentation for correct filter format
- **Check field availability** - some fields require specific API versions or permissions

## Learning Resources

- **GraphQL Admin API Overview**: https://shopify.dev/docs/api/admin-graphql
  - *Review only when you need general GraphQL API understanding beyond orders*
- **API Rate Limits**: https://shopify.dev/docs/api/usage/rate-limits
  - *Review only when you encounter rate limiting issues or need optimization guidance*
- **Pagination Best Practices**: https://shopify.dev/docs/api/usage/pagination-graphql
  - *Review only when implementing pagination for large datasets*
- **Search Syntax**: https://shopify.dev/docs/api/usage/search-syntax
  - *Review only when building complex search filters or when filters aren't working*
- **API Versioning**: https://shopify.dev/docs/api/usage/versioning
  - *Review only when you encounter API compatibility issues or need specific version features*

## Troubleshooting

If a query fails or returns unexpected results:

1. **Verify field names** against current API documentation
2. **Check filter syntax** - ensure proper format (e.g., `status:open` not `status=open`)
3. **Validate ID format** - must be full GID (e.g., `gid://shopify/Order/123`)
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
