# Shopify Discount Queries

This guide helps you generate accurate GraphQL queries for fetching discount information from Shopify.

## Instructions for Query Generation

When a user requests to fetch discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific discount data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Discount Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes

**What to learn from this documentation:**
- Required input fields for discount queries
- Available filters and search parameters
- Pagination and sorting options
- Discount data structure and available fields
- Discount types and their specific properties

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes#return-fields
  - *Review only when you need to verify what discount data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes#examples
  - *Review only when you need sample query patterns for complex discount scenarios*

### Individual Discount Queries Documentation

#### Specific Discount Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNode

**What to learn from this documentation:**
- Fetch individual discount by ID
- Complete discount data structure
- Discount-specific fields and properties
- Discount status and configuration details

### Discount Count and Analytics Documentation

#### Discount Count Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodesCount

**What to learn from this documentation:**
- Discount count aggregation options
- Filtering for count queries
- Performance considerations for large datasets
- Discount analytics and reporting

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying discount data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Discount Query Cost Calculation**:
   - Discount queries have moderate costs
   - Complex discounts with many rules increase cost
   - Large result sets require pagination to manage costs
   - Formula: `cost = base_query_cost + discount_complexity + result_size`

3. **Best Practices for Discount Query Generation**:
   - **Include only required fields**: Don't request unnecessary discount data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed discount data
   - **Batch efficiently**: Query multiple discounts in single requests when possible

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all discounts with excessive fields
   query {
     discountNodes(first: 50) {
       edges {
         node {
           id title status discountClass { ... } 
           codes { edges { node { ... } } }
           automaticDiscount { ... }
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches discounts with essential fields only
   query {
     discountNodes(first: 10, query:"status:ACTIVE") {
       edges {
         node {
           id
           title
           status
           discountClass
           startsAt
           endsAt
         }
       }
     }
   }
   ```

## Query Generation Rules

### Variable Placeholders

When generating discount queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Discount ID | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$TITLE$` | Discount title | Ask user if not provided | `"Summer Sale"` |
| `$STATUS$` | Discount status | `"ACTIVE"` | `"ARCHIVED"` |
| `$DISCOUNT_CLASS$` | Discount class | Ask user if not provided | `"CODE"` or `"AUTOMATIC"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"title:Summer AND status:ACTIVE"` |
| `$STARTS_AT$` | Discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |

### Query Structure Templates

#### Multiple Discounts Query Template
```graphql
query discountNodes($first: Int!, $query: String, $after: String) {
  discountNodes(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        status
        discountClass
        startsAt
        endsAt
        createdAt
        updatedAt
        summary
        discountApp {
          id
          title
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### Specific Discount Query Template
```graphql
query discountNode($id: ID!) {
  discountNode(id: $id) {
    id
    title
    status
    discountClass
    startsAt
    endsAt
    createdAt
    updatedAt
    summary
    discountApp {
      id
      title
    }
    ... on DiscountCode {
      codes(first: 10) {
        edges {
          node {
            id
            code
            usageCount
            createdAt
          }
        }
      }
    }
    ... on DiscountAutomatic {
      title
      status
      startsAt
      endsAt
    }
  }
}
```

#### Discount Count Query Template
```graphql
query discountNodesCount($query: String) {
  discountNodesCount(query: $query) {
    count
  }
}
```

#### Active Discounts Query Template
```graphql
query discountNodes($first: Int!, $after: String) {
  discountNodes(first: $first, query: "status:ACTIVE", after: $after) {
    edges {
      node {
        id
        title
        status
        discountClass
        startsAt
        endsAt
        summary
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### Discount by Date Range Template
```graphql
query discountNodes($first: Int!, $query: String, $after: String) {
  discountNodes(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        status
        discountClass
        startsAt
        endsAt
        createdAt
        updatedAt
        summary
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

When generating a discount query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find discounts matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what discounts you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 discounts at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find discount information from your store.

**Query:**
```graphql
query discountNodes($first: Int!, $query: String) {
  discountNodes(first: $first, query: $query) {
    edges {
      node {
        id
        title
        status
        discountClass
        startsAt
        endsAt
        summary
      }
    }
  }
}
```

**What this does:**
This searches for discounts in your store and returns their basic information.

**What I need from you:**
- What specific discounts are you looking for? (by title, status, type, etc.)
- How many discounts would you like to see?

**Examples of what you can search for:**
- All active discounts
- Discounts with specific titles (like "Summer" or "Sale")
- Code discounts vs automatic discounts
- Discounts expiring soon
- Discounts created after a certain date

Would you like me to help you find specific discounts?
```

## Common Discount Query Scenarios

### Discount Discovery and Management
- **Use**: `discountNodes` query with filters
- **Filters**: Title, status, discount class, date ranges
- **Considerations**: Search performance, result relevance

### Individual Discount Lookup
- **Use**: `discountNode` query with ID
- **Use case**: Complete discount details for management
- **Considerations**: Data completeness, discount configuration

### Discount Analytics
- **Use**: `discountNodesCount` query
- **Use case**: Discount metrics, business intelligence
- **Considerations**: Data aggregation, reporting needs

### Discount Performance Analysis
- **Use**: `discountNodes` query with usage filters
- **Use case**: Discount effectiveness, performance tracking
- **Considerations**: Usage data, performance metrics

### Discount Expiration Management
- **Use**: `discountNodes` query with date filters
- **Use case**: Managing expiring discounts, renewal planning
- **Considerations**: Timing, customer communication, business impact

## Search Query Examples

### Basic Discount Searches
- `title:Summer` - Discounts with "Summer" in title
- `status:ACTIVE` - Only active discounts
- `discount_class:CODE` - Only code discounts
- `discount_class:AUTOMATIC` - Only automatic discounts
- `starts_at:>2024-06-01` - Discounts starting after specific date

### Advanced Discount Searches
- `title:Summer AND status:ACTIVE` - Active summer discounts
- `discount_class:CODE AND ends_at:<2024-12-31` - Code discounts expiring before end of year
- `starts_at:>2024-01-01 AND status:ACTIVE` - Active discounts created this year
- `NOT status:ARCHIVED AND discount_class:CODE` - Active code discounts

### Date-Based Searches
- `starts_at:>2024-06-01` - Discounts starting after June 1, 2024
- `ends_at:<2024-12-31` - Discounts ending before December 31, 2024
- `created_at:>2024-01-01` - Discounts created in 2024
- `updated_at:>2024-06-01` - Discounts updated since June 1, 2024

### Status-Based Searches
- `status:ACTIVE` - Currently active discounts
- `status:SCHEDULED` - Scheduled but not yet active discounts
- `status:EXPIRED` - Expired discounts
- `status:ARCHIVED` - Archived discounts

## Discount Types and Classes

### Code Discounts
- **Definition**: Discounts that require customers to enter a code at checkout
- **Usage**: Promotional campaigns, customer incentives, special offers
- **Fields**: Code, usage limits, customer eligibility, application rules
- **Considerations**: Code management, customer awareness, usage tracking

### Automatic Discounts
- **Definition**: Discounts that are applied automatically based on conditions
- **Usage**: Volume discounts, customer segment pricing, automatic promotions
- **Fields**: Conditions, eligibility rules, application criteria
- **Considerations**: Customer experience, pricing strategy, margin impact

### Discount Classes
- **CODE**: Discounts requiring customer entry of discount codes
- **AUTOMATIC**: Discounts applied automatically based on defined conditions
- **APP**: Discounts created and managed by Shopify apps

## Discount Management Use Cases

### Promotional Campaign Management
- **Use**: Discount queries for campaign tracking
- **Filters**: Campaign-specific titles, date ranges, status
- **Considerations**: Campaign performance, ROI analysis, customer engagement

### Customer Segment Analysis
- **Use**: Discount queries for customer segment targeting
- **Filters**: Discount types, usage patterns, customer eligibility
- **Considerations**: Customer behavior, segment profitability, personalization

### Sales Performance Tracking
- **Use**: Discount queries for sales impact analysis
- **Filters**: Active discounts, usage data, revenue impact
- **Considerations**: Sales lift, margin impact, customer acquisition

### Inventory Management
- **Use**: Discount queries for inventory clearance
- **Filters**: Product-specific discounts, expiration dates
- **Considerations**: Inventory turnover, margin optimization, seasonal planning

## Performance Optimization Tips

### Query Efficiency
- Use specific filters to reduce result sets
- Request only necessary fields for your use case
- Implement pagination for large numbers of discounts
- Use cursor-based pagination for better performance

### Data Caching
- Cache discount metadata that doesn't change frequently
- Implement appropriate cache invalidation strategies
- Consider discount update frequency
- Balance cache size with performance needs

### Bulk Operations
- Use GraphQL aliases for multiple discount lookups
- Batch discount queries when possible
- Consider bulk operations for discount management
- Monitor query complexity and costs

### Integration Considerations
- Plan for discount synchronization with other systems
- Consider discount change notifications
- Implement webhook handlers for discount updates
- Design for scalability as discount numbers grow

## Discount Analytics and Reporting

### Usage Metrics
- **Code Usage**: Track how often discount codes are used
- **Revenue Impact**: Measure discount effectiveness on sales
- **Customer Acquisition**: Analyze discount-driven customer acquisition
- **Margin Analysis**: Track discount impact on profit margins

### Performance Indicators
- **Conversion Rate**: Discount-driven conversion improvements
- **Average Order Value**: Impact on customer spending
- **Customer Retention**: Discount effectiveness for repeat business
- **Seasonal Performance**: Discount performance by time periods

### Business Intelligence
- **Campaign ROI**: Return on investment for discount campaigns
- **Customer Segmentation**: Discount usage by customer segments
- **Product Performance**: Discount effectiveness by product categories
- **Competitive Analysis**: Discount strategy compared to market trends

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
