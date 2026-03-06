# Shopify Code Discount Queries

This guide helps you generate accurate GraphQL queries for fetching code discount information from Shopify.

## Instructions for Query Generation

When a user requests to fetch code discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific code discount data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Code Discount Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes

**What to learn from this documentation:**
- Required input fields for code discount queries
- Available filters and search parameters
- Pagination and sorting options
- Code discount data structure and available fields
- Code usage and eligibility information

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes#return-fields
  - *Review only when you need to verify what code discount data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes#examples
  - *Review only when you need sample query patterns for complex code discount scenarios*

### Individual Code Discount Queries Documentation

#### Specific Code Discount Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNode

**What to learn from this documentation:**
- Fetch individual code discount by ID
- Complete code discount data structure
- Code-specific fields and usage information
- Discount configuration and eligibility rules

#### Code Discount by Code Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodeByCode

**What to learn from this documentation:**
- Fetch code discount by discount code string
- Code validation and lookup
- Real-time code verification
- Customer-facing code validation

### Code Discount Count Documentation

#### Code Discount Count Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/discountCodesCount

**What to learn from this documentation:**
- Code discount count aggregation options
- Filtering for count queries
- Performance considerations for large datasets
- Code discount analytics and reporting

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying code discount data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Code Discount Query Cost Calculation**:
   - Code discount queries have moderate costs
   - Complex discounts with many codes increase cost
   - Usage data and eligibility rules add complexity
   - Formula: `cost = base_query_cost + discount_complexity + code_count + usage_data`

3. **Best Practices for Code Discount Query Generation**:
   - **Include only required fields**: Don't request unnecessary code discount data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed code discount data
   - **Optimize code lookups**: Use efficient code validation patterns

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all code discounts with excessive fields
   query {
     codeDiscountNodes(first: 50) {
       edges {
         node {
           id title status codes { edges { node { ... } } }
           usageCount customerSelection { ... } discountClass { ... }
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches code discounts with essential fields only
   query {
     codeDiscountNodes(first: 10, query:"status:ACTIVE") {
       edges {
         node {
           id
           title
           status
           startsAt
           endsAt
           codes(first: 5) {
             edges {
               node {
                 id
                 code
                 usageCount
               }
             }
           }
         }
       }
     }
   }
   ```

## Query Generation Rules

### Variable Placeholders

When generating code discount queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Code discount ID | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$DISCOUNT_CODE$` | Discount code string | Ask user if not provided | `"SUMMER2024"` |
| `$TITLE$` | Code discount title | Ask user if not provided | `"Summer Sale"` |
| `$STATUS$` | Code discount status | `"ACTIVE"` | `"ARCHIVED"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"title:Summer AND status:ACTIVE"` |
| `$STARTS_AT$` | Discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |
| `$CODE_PREFIX$` | Code prefix for filtering | Ask user if not provided | `"SUMMER"` |

### Query Structure Templates

#### Multiple Code Discounts Query Template
```graphql
query codeDiscountNodes($first: Int!, $query: String, $after: String) {
  codeDiscountNodes(first: $first, query: $query, after: $after) {
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
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### Specific Code Discount Query Template
```graphql
query codeDiscountNode($id: ID!) {
  codeDiscountNode(id: $id) {
    id
    title
    status
    startsAt
    endsAt
    createdAt
    updatedAt
    summary
    codes(first: 50) {
      edges {
        node {
          id
          code
          usageCount
          createdAt
        }
      }
    }
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

#### Code Discount by Code Template
```graphql
query codeDiscountNodeByCode($code: String!) {
  codeDiscountNodeByCode(code: $code) {
    id
    title
    status
    startsAt
    endsAt
    summary
    codes(first: 10) {
      edges {
        node {
          id
          code
          usageCount
        }
      }
    }
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

#### Code Discount Count Template
```graphql
query discountCodesCount($query: String) {
  discountCodesCount(query: $query) {
    count
  }
}
```

#### Active Code Discounts Template
```graphql
query codeDiscountNodes($first: Int!, $after: String) {
  codeDiscountNodes(first: $first, query: "status:ACTIVE", after: $after) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        summary
        codes(first: 5) {
          edges {
            node {
              id
              code
              usageCount
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

#### Code Usage Analysis Template
```graphql
query codeDiscountNodes($first: Int!, $query: String, $after: String) {
  codeDiscountNodes(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        codes(first: 20) {
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
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Response Guidelines

When generating a code discount query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find code discounts matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what code discounts you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 code discounts at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find code discount information from your store.

**Query:**
```graphql
query codeDiscountNodes($first: Int!, $query: String) {
  codeDiscountNodes(first: $first, query: $query) {
    edges {
      node {
        id
        title
        status
        startsAt
        endsAt
        summary
        codes(first: 5) {
          edges {
            node {
              id
              code
              usageCount
            }
          }
        }
      }
    }
  }
}
```

**What this does:**
This searches for code discounts in your store and returns their basic information and usage data.

**What I need from you:**
- What specific code discounts are you looking for? (by title, status, code pattern, etc.)
- How many code discounts would you like to see?

**Examples of what you can search for:**
- All active code discounts
- Code discounts with specific titles (like "Summer" or "Sale")
- Discounts with codes starting with specific text
- Code discounts expiring soon
- Most frequently used discount codes

Would you like me to help you find specific code discounts?
```

## Common Code Discount Query Scenarios

### Code Discount Discovery and Management
- **Use**: `codeDiscountNodes` query with filters
- **Filters**: Title, status, code patterns, date ranges
- **Considerations**: Search performance, result relevance

### Individual Code Discount Lookup
- **Use**: `codeDiscountNode` query with ID
- **Use case**: Complete code discount details for management
- **Considerations**: Data completeness, usage tracking

### Code Validation and Lookup
- **Use**: `codeDiscountNodeByCode` query
- **Use case**: Real-time code validation, customer-facing lookup
- **Considerations**: Performance, real-time requirements, customer experience

### Code Usage Analytics
- **Use**: `codeDiscountNodes` query with usage data
- **Use case**: Code performance analysis, customer behavior tracking
- **Considerations**: Usage metrics, effectiveness analysis

### Code Discount Count and Reporting
- **Use**: `discountCodesCount` query
- **Use case**: Code discount metrics, business intelligence
- **Considerations**: Data aggregation, reporting needs

## Search Query Examples

### Basic Code Discount Searches
- `title:Summer` - Code discounts with "Summer" in title
- `status:ACTIVE` - Only active code discounts
- `codes:SUMMER2024` - Code discounts with specific code
- `starts_at:>2024-06-01` - Code discounts starting after specific date

### Advanced Code Discount Searches
- `title:Summer AND status:ACTIVE` - Active summer code discounts
- `ends_at:<2024-12-31 AND status:ACTIVE` - Active code discounts expiring before end of year
- `codes:SUMMER* AND status:ACTIVE` - Active code discounts with codes starting with "SUMMER"
- `created_at:>2024-01-01 AND status:ACTIVE` - Active code discounts created this year

### Code Pattern Searches
- `codes:SUMMER*` - Code discounts with codes starting with "SUMMER"
- `codes:*2024` - Code discounts with codes ending with "2024"
- `codes:*SALE*` - Code discounts with codes containing "SALE"
- `codes:WELCOME*` - Code discounts with welcome codes

### Usage-Based Searches
- `codes.usage_count:>10` - Code discounts with codes used more than 10 times
- `status:ACTIVE AND codes.usage_count:>0` - Active code discounts that have been used
- `codes.usage_count:0 AND status:ACTIVE` - Active code discounts that haven't been used yet

### Date-Based Searches
- `starts_at:>2024-06-01` - Code discounts starting after June 1, 2024
- `ends_at:<2024-12-31` - Code discounts ending before December 31, 2024
- `created_at:>2024-01-01` - Code discounts created in 2024
- `updated_at:>2024-06-01` - Code discounts updated since June 1, 2024

## Code Discount Types and Structures

### Basic Code Discounts
- **Definition**: Simple percentage or fixed amount discounts
- **Usage**: General promotions, customer incentives
- **Fields**: Discount value, applicability, usage limits
- **Considerations**: Margin impact, customer appeal, simplicity

### Buy X Get Y (BXGY) Code Discounts
- **Definition**: Buy specific products get other products discounted
- **Usage**: Product bundling, cross-selling, inventory management
- **Fields**: Customer buys, customer gets, application rules
- **Considerations**: Product selection, inventory coordination, complexity

### Free Shipping Code Discounts
- **Definition**: Free or discounted shipping promotions
- **Usage**: Cart value incentives, shipping cost reduction
- **Fields**: Shipping discount, minimum requirements, destination restrictions
- **Considerations**: Shipping costs, geographic limitations, profit margins

### App-Generated Code Discounts
- **Definition**: Code discounts created by Shopify apps
- **Usage**: Advanced discount logic, third-party integrations
- **Fields**: App-specific configuration, custom rules
- **Considerations**: App dependencies, custom logic, integration complexity

## Code Management Strategies

### Code Generation Patterns
- **Sequential Codes**: SUMMER001, SUMMER002, etc.
- **Random Codes**: Unique random strings for security
- **Descriptive Codes**: SUMMER24, WELCOME10, etc.
- **Campaign-Specific Codes**: BLACKFRIDAY2024, etc.

### Usage Limit Management
- **Total Usage Limits**: Maximum number of times code can be used
- **Customer Usage Limits**: Maximum uses per customer
- **Time-Based Limits**: Usage restrictions by time period
- **Segment-Based Limits**: Usage limits by customer segments

### Customer Eligibility
- **All Customers**: Available to all store customers
- **Customer Segments**: Specific customer groups
- **Saved Searches**: Dynamic customer groups based on criteria
- **Individual Customers**: Specific customer assignments

## Performance Optimization Tips

### Query Efficiency
- Use specific filters to reduce result sets
- Request only necessary fields for your use case
- Implement pagination for large numbers of code discounts
- Use cursor-based pagination for better performance

### Code Lookup Optimization
- Cache frequently accessed code discount data
- Implement efficient code validation patterns
- Use code-specific queries for real-time validation
- Consider code lookup performance for customer-facing applications

### Usage Data Management
- Track usage metrics efficiently
- Implement usage aggregation for reporting
- Cache usage statistics for performance
- Monitor usage patterns for optimization

### Bulk Operations
- Use GraphQL aliases for multiple code discount lookups
- Batch code discount queries when possible
- Consider bulk operations for code management
- Monitor query complexity and costs

## Analytics and Reporting

### Code Performance Metrics
- **Usage Frequency**: How often codes are used
- **Revenue Impact**: Revenue generated by code usage
- **Customer Acquisition**: New customers acquired through codes
- **Conversion Rate**: Code-driven conversion improvements

### Customer Behavior Analysis
- **Code Preferences**: Which codes customers prefer
- **Usage Patterns**: When and how customers use codes
- **Segment Analysis**: Code usage by customer segments
- **Geographic Patterns**: Regional code usage differences

### Business Intelligence
- **Campaign ROI**: Return on investment for code campaigns
- **Seasonal Trends**: Code usage patterns by season
- **Product Impact**: Effect of codes on product sales
- **Competitive Analysis**: Code strategy compared to market

## Integration Considerations

### Customer-Facing Applications
- **Real-time Validation**: Fast code validation for checkout
- **Error Handling**: Clear error messages for invalid codes
- **User Experience**: Smooth code entry and application process
- **Mobile Optimization**: Code entry optimized for mobile devices

### Backend Systems
- **Inventory Integration**: Coordinate with inventory management
- **Order Processing**: Ensure proper code application in orders
- **Customer Management**: Track code usage by customers
- **Analytics Integration**: Feed usage data to analytics systems

### Third-Party Integrations
- **Marketing Platforms**: Sync codes with email marketing tools
- **Social Media**: Distribute codes through social channels
- **Affiliate Programs**: Track affiliate-generated code usage
- **Customer Service**: Provide code information to support teams

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
