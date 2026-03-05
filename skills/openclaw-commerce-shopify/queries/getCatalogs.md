# Shopify Catalog Queries

This guide helps you generate accurate GraphQL queries for fetching catalog information from Shopify.

## Instructions for Query Generation

When a user requests to fetch catalog data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific catalog data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Catalog Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs

**What to learn from this documentation:**
- Required input fields for catalog queries
- Available filters and search parameters
- Pagination and sorting options
- Catalog data structure and available fields
- Catalog hierarchy and relationships

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#return-fields
  - *Review only when you need to verify what catalog data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogs#examples
  - *Review only when you need sample query patterns for complex catalog scenarios*

### Individual Catalog Queries Documentation

#### Specific Catalog Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/catalog

**What to learn from this documentation:**
- Fetch individual catalog by ID
- Complete catalog data structure
- Catalog metadata and settings
- Related catalog entities

### Catalog Count and Analytics Documentation

#### Catalog Count Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/catalogsCount

**What to learn from this documentation:**
- Catalog count aggregation options
- Filtering for count queries
- Performance considerations for large datasets
- Catalog analytics and reporting

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying catalog data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Catalog Query Cost Calculation**:
   - Catalog queries generally have moderate costs
   - Complex catalogs with many products and variants increase cost
   - Large result sets require pagination to manage costs
   - Formula: `cost = base_query_cost + catalog_complexity + result_size`

3. **Best Practices for Catalog Query Generation**:
   - **Include only required fields**: Don't request unnecessary catalog data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed catalog data
   - **Batch efficiently**: Query multiple catalogs in single requests when possible

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all catalogs with excessive fields
   query {
     catalogs(first: 50) {
       edges {
         node {
           id name description products { edges { node { ... } } }
           collections { edges { node { ... } } } settings { ... }
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches catalogs with essential fields only
   query {
     catalogs(first: 10) {
       edges {
         node {
           id name description status
           productCount
           collectionCount
         }
       }
     }
   }
   ```

## Query Generation Rules

### Variable Placeholders

When generating catalog queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CATALOG_ID$` | Catalog ID | Ask user if not provided | `gid://shopify/Catalog/123456789` |
| `$CATALOG_NAME$` | Catalog name | Ask user if not provided | `"Main Catalog"` |
| `$STATUS$` | Catalog status | `"ACTIVE"` | `"ARCHIVED"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"name:Main AND status:ACTIVE"` |

### Query Structure Templates

#### Multiple Catalogs Query Template
```graphql
query catalogs($first: Int!, $query: String, $after: String) {
  catalogs(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        name
        description
        status
        createdAt
        updatedAt
        productCount
        collectionCount
        settings {
          publication {
            id
            name
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

#### Specific Catalog Query Template
```graphql
query catalog($id: ID!) {
  catalog(id: $id) {
    id
    name
    description
    status
    createdAt
    updatedAt
    productCount
    collectionCount
    settings {
      publication {
        id
        name
      }
    }
    products(first: 10) {
      edges {
        node {
          id
          title
          handle
          status
          vendor
          productType
          totalInventory
        }
      }
    }
    collections(first: 10) {
      edges {
        node {
          id
          title
          handle
          description
        }
      }
    }
  }
}
```

#### Catalog Count Query Template
```graphql
query catalogsCount($query: String) {
  catalogsCount(query: $query) {
    count
  }
}
```

## Response Guidelines

When generating a catalog query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find catalogs matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what catalogs you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 catalogs at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find catalog information from your store.

**Query:**
```graphql
query catalogs($first: Int!, $query: String) {
  catalogs(first: $first, query: $query) {
    edges {
      node {
        id
        name
        description
        status
        createdAt
        updatedAt
        productCount
        collectionCount
      }
    }
  }
}
```

**What this does:**
This searches for catalogs in your store and returns their basic information and statistics.

**What I need from you:**
- What specific catalogs are you looking for? (by name, status, etc.)
- How many catalogs would you like to see?

**Examples of what you can search for:**
- All active catalogs
- Catalogs with specific names
- Catalogs created after a certain date
- Catalogs with specific product counts

Would you like me to help you find specific catalogs?
```

## Common Catalog Query Scenarios

### Catalog Discovery and Management
- **Use**: `catalogs` query with filters
- **Filters**: Name, status, creation date, product count
- **Considerations**: Search performance, result relevance

### Individual Catalog Lookup
- **Use**: `catalog` query with ID
- **Use case**: Complete catalog details for management
- **Considerations**: Data completeness, product and collection relationships

### Catalog Analytics
- **Use**: `catalogsCount` query
- **Use case**: Catalog metrics, business intelligence
- **Considerations**: Data aggregation, reporting needs

### Catalog Performance Analysis
- **Use**: `catalogs` query with product and collection counts
- **Use case**: Catalog utilization, optimization opportunities
- **Considerations**: Performance metrics, catalog efficiency

### Multi-Catalog Management
- **Use**: `catalogs` query with pagination
- **Use case**: Managing multiple storefronts or markets
- **Considerations**: Cross-catalog consistency, management overhead

## Search Query Examples

### Basic Catalog Searches
- `name:Main` - Catalogs with "Main" in name
- `status:ACTIVE` - Only active catalogs
- `product_count:>100` - Catalogs with more than 100 products
- `created_at:>2024-01-01` - Catalogs created after specific date

### Advanced Catalog Searches
- `name:Main AND status:ACTIVE` - Active main catalogs
- `product_count:>50 AND collection_count:>10` - Large catalogs with many collections
- `created_at:>2024-01-01 AND status:ACTIVE` - Recently created active catalogs
- `NOT status:ARCHIVED` - Non-archived catalogs

### Catalog Performance Searches
- `product_count:0` - Empty catalogs
- `collection_count:0` - Catalogs without collections
- `product_count:>1000` - Very large catalogs
- `updated_at:<2024-01-01` - Stale catalogs not updated recently

## Catalog Management Use Cases

### Multi-Storefront Operations
- **Use**: Catalog queries to manage different storefronts
- **Filters**: Status, publication settings
- **Considerations**: Cross-catalog product management, consistency

### Market-Specific Catalogs
- **Use**: Catalog queries for regional or market-specific offerings
- **Filters**: Product types, pricing, availability
- **Considerations**: Market localization, currency differences

### Seasonal Catalog Management
- **Use**: Catalog queries for seasonal or temporary collections
- **Filters**: Creation dates, status changes
- **Considerations**: Timing, inventory planning, marketing coordination

### B2B vs B2C Catalogs
- **Use**: Separate catalogs for different customer segments
- **Filters**: Product types, pricing tiers, customer groups
- **Considerations**: Access control, pricing strategies, product selection

## Performance Optimization Tips

### Query Efficiency
- Use specific filters to reduce result sets
- Request only necessary fields for your use case
- Implement pagination for large numbers of catalogs
- Use cursor-based pagination for better performance

### Data Caching
- Cache catalog metadata that doesn't change frequently
- Implement appropriate cache invalidation strategies
- Consider catalog update frequency
- Balance cache size with performance needs

### Bulk Operations
- Use GraphQL aliases for multiple catalog lookups
- Batch catalog queries when possible
- Consider bulk operations for catalog management
- Monitor query complexity and costs

### Integration Considerations
- Plan for catalog synchronization with other systems
- Consider catalog change notifications
- Implement webhook handlers for catalog updates
- Design for scalability as catalog numbers grow

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
