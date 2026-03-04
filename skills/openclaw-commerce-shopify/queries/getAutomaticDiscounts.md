# Shopify Automatic Discount Queries

This guide helps you generate accurate GraphQL queries for fetching automatic discount information from Shopify.

## Instructions for Query Generation

When a user requests to fetch automatic discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific automatic discount data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Automatic Discount Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes

**What to learn from this documentation:**
- Required input fields for automatic discount queries
- Available filters and search parameters
- Pagination and sorting options
- Automatic discount data structure and available fields
- Discount conditions and eligibility rules

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes#return-fields
  - *Review only when you need to verify what automatic discount data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes#examples
  - *Review only when you need sample query patterns for complex automatic discount scenarios*

### Individual Automatic Discount Queries Documentation

#### Specific Automatic Discount Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscount

**What to learn from this documentation:**
- Fetch individual automatic discount by ID
- Complete automatic discount data structure
- Condition logic and eligibility rules
- Discount configuration and application criteria

#### All Automatic Discounts Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscounts

**What to learn from this documentation:**
- Fetch all automatic discounts without pagination limits
- Complete automatic discount listing
- Bulk discount management
- System-wide discount overview

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying automatic discount data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Automatic Discount Query Cost Calculation**:
   - Automatic discount queries have moderate to high costs
   - Complex condition logic increases cost significantly
   - Eligibility rules and customer segments add complexity
   - Formula: `cost = base_query_cost + discount_complexity + condition_logic + eligibility_rules`

3. **Best Practices for Automatic Discount Query Generation**:
   - **Include only required fields**: Don't request unnecessary automatic discount data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed automatic discount data
   - **Optimize condition queries**: Structure condition queries efficiently

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all automatic discounts with excessive fields
   query {
     automaticDiscountNodes(first: 50) {
       edges {
         node {
           id title status conditions { ... } 
           customerSelection { ... } discountClass { ... }
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches automatic discounts with essential fields only
   query {
     automaticDiscountNodes(first: 10, query:"status:ACTIVE") {
       edges {
         node {
           id
           title
           status
           startsAt
           endsAt
           summary
         }
       }
     }
   }
   ```

## Query Generation Rules

### Variable Placeholders

When generating automatic discount queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Automatic discount ID | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$TITLE$` | Automatic discount title | Ask user if not provided | `"Volume Discount"` |
| `$STATUS$` | Automatic discount status | `"ACTIVE"` | `"ARCHIVED"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"title:Volume AND status:ACTIVE"` |
| `$STARTS_AT$` | Discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |
| `$MINIMUM_QUANTITY$` | Minimum quantity condition | Ask user if not provided | `5` |
| `$MINIMUM_AMOUNT$` | Minimum amount condition | Ask user if not provided | `100.00` |

### Query Structure Templates

#### Multiple Automatic Discounts Query Template
```graphql
query automaticDiscountNodes($first: Int!, $query: String, $after: String) {
  automaticDiscountNodes(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        createdAt
        updatedAt
        summary
        customerSelection {
          __typename
          ... on DiscountCustomerAll {
            allCustomers
          }
          ... on DiscountCustomerSegments {
            segments {
              id
              name
            }
          }
          ... on DiscountCustomerSavedSearches {
            savedSearches {
              id
              name
            }
          }
        }
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

#### Specific Automatic Discount Query Template
```graphql
query automaticDiscount($id: ID!) {
  automaticDiscount(id: $id) {
    id
    title
    status
    startsAt
    endsAt
    createdAt
    updatedAt
    summary
    customerSelection {
      __typename
      ... on DiscountCustomerAll {
        allCustomers
      }
      ... on DiscountCustomerSegments {
        segments {
          id
          name
        }
      }
      ... on DiscountCustomerSavedSearches {
        savedSearches {
          id
          name
        }
      }
    }
    discountApp {
      id
      title
    }
  }
}
```

#### All Automatic Discounts Query Template
```graphql
query automaticDiscounts {
  automaticDiscounts {
    id
    title
    status
    startsAt
    endsAt
    summary
    customerSelection {
      __typename
      ... on DiscountCustomerAll {
        allCustomers
      }
      ... on DiscountCustomerSegments {
        segments {
          id
          name
        }
      }
    }
  }
}
```

#### Active Automatic Discounts Template
```graphql
query automaticDiscountNodes($first: Int!, $after: String) {
  automaticDiscountNodes(first: $first, query: "status:ACTIVE", after: $after) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        summary
        customerSelection {
          __typename
          ... on DiscountCustomerAll {
            allCustomers
          }
          ... on DiscountCustomerSegments {
            segments {
              id
              name
            }
          }
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

#### Automatic Discount by Date Range Template
```graphql
query automaticDiscountNodes($first: Int!, $query: String, $after: String) {
  automaticDiscountNodes(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        createdAt
        updatedAt
        summary
        customerSelection {
          __typename
          ... on DiscountCustomerAll {
            allCustomers
          }
          ... on DiscountCustomerSegments {
            segments {
              id
              name
            }
          }
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

## Response Guidelines

When generating an automatic discount query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find automatic discounts matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what automatic discounts you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 automatic discounts at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find automatic discount information from your store.

**Query:**
```graphql
query automaticDiscountNodes($first: Int!, $query: String) {
  automaticDiscountNodes(first: $first, query: $query) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        summary
        customerSelection {
          __typename
          ... on DiscountCustomerAll {
            allCustomers
          }
          ... on DiscountCustomerSegments {
            segments {
              id
              name
            }
          }
        }
      }
    }
  }
}
```

**What this does:**
This searches for automatic discounts in your store and returns their basic information and eligibility rules.

**What I need from you:**
- What specific automatic discounts are you looking for? (by title, status, customer type, etc.)
- How many automatic discounts would you like to see?

**Examples of what you can search for:**
- All active automatic discounts
- Volume-based automatic discounts
- Customer segment-specific automatic discounts
- Automatic discounts expiring soon
- Automatic discounts for specific customer groups

Would you like me to help you find specific automatic discounts?
```

## Common Automatic Discount Query Scenarios

### Automatic Discount Discovery and Management
- **Use**: `automaticDiscountNodes` query with filters
- **Filters**: Title, status, customer segments, date ranges
- **Considerations**: Search performance, result relevance

### Individual Automatic Discount Lookup
- **Use**: `automaticDiscount` query with ID
- **Use case**: Complete automatic discount details for management
- **Considerations**: Data completeness, condition logic, eligibility rules

### System-Wide Automatic Discount Overview
- **Use**: `automaticDiscounts` query
- **Use case**: Complete listing of all automatic discounts
- **Considerations**: Performance for large discount sets, system overview

### Customer Segment Analysis
- **Use**: `automaticDiscountNodes` query with customer segment filters
- **Use case**: Analyze discounts for specific customer groups
- **Considerations**: Segment-specific pricing, customer targeting

### Performance and Analytics
- **Use**: `automaticDiscountNodes` query with performance data
- **Use case**: Discount effectiveness analysis, performance tracking
- **Considerations**: Usage metrics, revenue impact, customer behavior

## Search Query Examples

### Basic Automatic Discount Searches
- `title:Volume` - Automatic discounts with "Volume" in title
- `status:ACTIVE` - Only active automatic discounts
- `starts_at:>2024-06-01` - Automatic discounts starting after specific date
- `customer_selection:segments` - Automatic discounts for customer segments

### Advanced Automatic Discount Searches
- `title:Volume AND status:ACTIVE` - Active volume automatic discounts
- `ends_at:<2024-12-31 AND status:ACTIVE` - Active automatic discounts expiring before end of year
- `created_at:>2024-01-01 AND status:ACTIVE` - Active automatic discounts created this year
- `NOT status:ARCHIVED AND customer_selection:all` - Active automatic discounts for all customers

### Customer Segment Searches
- `customer_selection:segments` - Automatic discounts for customer segments
- `customer_selection:all` - Automatic discounts for all customers
- `customer_selection:saved_searches` - Automatic discounts for saved search customer groups
- `status:ACTIVE AND customer_selection:segments` - Active automatic discounts for customer segments

### Date-Based Searches
- `starts_at:>2024-06-01` - Automatic discounts starting after June 1, 2024
- `ends_at:<2024-12-31` - Automatic discounts ending before December 31, 2024
- `created_at:>2024-01-01` - Automatic discounts created in 2024
- `updated_at:>2024-06-01` - Automatic discounts updated since June 1, 2024

### Performance-Based Searches
- `status:ACTIVE` - Currently active automatic discounts
- `status:SCHEDULED` - Scheduled but not yet active automatic discounts
- `status:EXPIRED` - Expired automatic discounts
- `status:ARCHIVED` - Archived automatic discounts

## Automatic Discount Types and Structures

### Basic Automatic Discounts
- **Definition**: Simple percentage or fixed amount discounts applied automatically
- **Usage**: Volume pricing, customer tier pricing, automatic promotions
- **Fields**: Discount value, applicability, minimum requirements
- **Considerations**: Margin impact, customer experience, pricing strategy

### Buy X Get Y (BXGY) Automatic Discounts
- **Definition**: Automatically applied when customers buy specific products
- **Usage**: Product bundling, cross-selling, inventory management
- **Fields**: Customer buys conditions, customer gets benefits, application rules
- **Considerations**: Product selection, inventory coordination, complexity

### Free Shipping Automatic Discounts
- **Definition**: Automatic free or discounted shipping based on conditions
- **Usage**: Cart value incentives, shipping cost reduction, customer loyalty
- **Fields**: Shipping discount conditions, minimum requirements, destination rules
- **Considerations**: Shipping costs, geographic limitations, profit margins

### App-Generated Automatic Discounts
- **Definition**: Automatic discounts created by Shopify apps with custom logic
- **Usage**: Advanced pricing strategies, third-party integrations, custom rules
- **Fields**: App-specific configuration, custom condition logic
- **Considerations**: App dependencies, custom logic complexity, integration needs

## Customer Eligibility and Targeting

### All Customers
- **Definition**: Automatic discounts available to all store customers
- **Usage**: General promotions, store-wide sales, broad marketing campaigns
- **Benefits**: Maximum reach, simple implementation, broad appeal
- **Considerations**: Margin impact, customer expectations, competitive positioning

### Customer Segments
- **Definition**: Automatic discounts for specific customer groups
- **Usage**: VIP pricing, wholesale pricing, loyalty programs
- **Benefits**: Targeted pricing, customer retention, segmentation strategy
- **Considerations**: Segment management, customer classification, complexity

### Saved Searches
- **Definition**: Dynamic customer groups based on search criteria
- **Usage**: Behavioral targeting, purchase history-based pricing, dynamic segmentation
- **Benefits**: Automatic customer grouping, behavior-based pricing, flexibility
- **Considerations**: Search criteria maintenance, performance overhead, complexity

## Condition Logic and Rules

### Minimum Quantity Conditions
- **Definition**: Discounts applied when minimum quantity requirements are met
- **Usage**: Volume pricing, bulk purchase incentives, inventory management
- **Fields**: Minimum quantity, applicable products, cart requirements
- **Considerations**: Inventory coordination, margin calculation, customer behavior

### Minimum Amount Conditions
- **Definition**: Discounts applied when minimum cart value is reached
- **Usage**: Cart value incentives, average order value optimization, free shipping
- **Fields**: Minimum amount, currency, applicable items, calculation method
- **Considerations**: Currency handling, tax calculations, international customers

### Product-Specific Conditions
- **Definition**: Discounts applied to specific products or collections
- **Usage**: Product promotions, category sales, inventory clearance
- **Fields**: Product selection, collection targeting, variant rules
- **Considerations**: Product management, inventory coordination, category strategy

### Customer-Based Conditions
- **Definition**: Discounts based on customer attributes or behavior
- **Usage**: Loyalty programs, customer tier pricing, behavioral incentives
- **Fields**: Customer attributes, purchase history, behavior patterns
- **Considerations**: Customer data privacy, segmentation accuracy, performance

## Performance Optimization Tips

### Query Efficiency
- Use specific filters to reduce result sets
- Request only necessary fields for your use case
- Implement pagination for large numbers of automatic discounts
- Use cursor-based pagination for better performance

### Condition Logic Optimization
- Structure condition queries efficiently
- Cache frequently accessed condition data
- Optimize customer segment lookups
- Monitor condition evaluation performance

### Customer Selection Performance
- Optimize customer segment queries
- Cache customer eligibility data
- Implement efficient saved search evaluation
- Monitor customer selection performance

### Bulk Operations
- Use GraphQL aliases for multiple automatic discount lookups
- Batch automatic discount queries when possible
- Consider bulk operations for discount management
- Monitor query complexity and costs

## Analytics and Reporting

### Discount Performance Metrics
- **Application Rate**: How often discounts are applied to carts
- **Revenue Impact**: Revenue generated by automatic discounts
- **Customer Impact**: Effect on customer acquisition and retention
- **Margin Analysis**: Impact on profit margins and pricing strategy

### Customer Behavior Analysis
- **Segment Response**: How different customer segments respond to discounts
- **Purchase Pattern Changes**: Changes in customer purchasing behavior
- **Cart Value Impact**: Effect on average order value
- **Loyalty Impact**: Effect on customer loyalty and repeat purchases

### Business Intelligence
- **Pricing Strategy Effectiveness**: Overall impact on pricing strategy
- **Competitive Positioning**: How automatic discounts affect competitive position
- **Seasonal Trends**: Discount performance by season and time period
- **Product Impact**: Effect of discounts on product sales and inventory

## Integration Considerations

### Checkout Integration
- **Real-time Application**: Fast discount application during checkout
- **Condition Evaluation**: Efficient condition logic evaluation
- **Customer Experience**: Smooth discount application without delays
- **Mobile Performance**: Optimized performance for mobile checkout

### Inventory Management
- **Stock Coordination**: Coordinate discounts with inventory levels
- **Product Availability**: Ensure discounted products are available
- **Supply Chain Impact**: Consider supply chain implications of discounts
- **Forecasting**: Use discount data for inventory forecasting

### Customer Management
- **Segment Updates**: Keep customer segments current and accurate
- **Behavior Tracking**: Track customer response to discounts
- **Loyalty Integration**: Integrate with customer loyalty programs
- **Communication**: Coordinate discount communication with customers

### Analytics Integration
- **Performance Tracking**: Feed discount performance data to analytics systems
- **Reporting Integration**: Integrate with business intelligence tools
- **Marketing Integration**: Coordinate with marketing campaign tracking
- **Financial Integration**: Track financial impact of discounts

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
