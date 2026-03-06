# Shopify Collection Queries

This guide helps you generate accurate GraphQL queries for fetching collection information from Shopify.

## Instructions for Query Generation

When a user requests to fetch collection data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific collection data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Collection Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/collections

**What to learn from this documentation:**
- Required input fields for collection queries
- Available filters and search parameters
- Pagination and sorting options
- Collection data structure and available fields
- Collection types and hierarchy

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/collections#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/collections#return-fields
  - *Review only when you need to verify what collection data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/collections#examples
  - *Review only when you need sample query patterns for complex collection scenarios*

### Individual Collection Queries Documentation

#### Specific Collection Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/collection

**What to learn from this documentation:**
- Fetch individual collection by ID
- Complete collection data structure
- Collection products and rules
- Collection metadata and settings

#### Collection by Handle Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/collectionByHandle

**What to learn from this documentation:**
- Fetch collection by URL handle
- Handle validation and formatting
- SEO-friendly collection access

#### Collection by Identifier Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/collectionByIdentifier

**What to learn from this documentation:**
- Fetch collection by various identifiers
- Identifier validation and formatting
- Multiple identifier support

### Collection Count and Analytics Documentation

#### Collection Count Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/collectionsCount

**What to learn from this documentation:**
- Collection count aggregation options
- Filtering for count queries
- Performance considerations for large datasets
- Collection analytics and reporting

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying collection data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Collection Query Cost Calculation**:
   - Collection queries have moderate to high costs
   - Collections with many products increase cost significantly
   - Large result sets require pagination to manage costs
   - Formula: `cost = base_query_cost + collection_complexity + result_size`

3. **Best Practices for Collection Query Generation**:
   - **Include only required fields**: Don't request unnecessary collection data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed collection data
   - **Limit product data**: Request minimal product information within collections

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all collections with excessive product data
   query {
     collections(first: 50) {
       edges {
         node {
           id title handle products { edges { node { ... } } }
           rules { ... } image { ... } metafields { ... }
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches collections with essential fields only
   query {
     collections(first: 10, query:"title:*Summer*") {
       edges {
         node {
           id title handle description
           productsCount
           updatedAt
         }
       }
     }
   }
   ```

## Query Generation Rules

### Variable Placeholders

When generating collection queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$COLLECTION_ID$` | Collection ID | Ask user if not provided | `gid://shopify/Collection/123456789` |
| `$COLLECTION_HANDLE$` | Collection handle | Ask user if not provided | `"summer-collection"` |
| `$TITLE$` | Collection title | Ask user if not provided | `"Summer Collection"` |
| `$COLLECTION_TYPE$` | Collection type | Ask user if not provided | `"SMART"` or `"CUSTOM"` |
| `$STATUS$` | Collection status | `"ACTIVE"` | `"ARCHIVED"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"title:Summer AND status:ACTIVE"` |
| `$PRODUCT_LIMIT$` | Number of products to show | `5` | `10` |

### Query Structure Templates

#### Multiple Collections Query Template
```graphql
query collections($first: Int!, $query: String, $after: String) {
  collections(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        handle
        description
        collectionType
        status
        createdAt
        updatedAt
        productsCount
        image {
          id
          url
          altText
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

#### Specific Collection Query Template
```graphql
query collection($id: ID!) {
  collection(id: $id) {
    id
    title
    handle
    description
    collectionType
    status
    createdAt
    updatedAt
    productsCount
    image {
      id
      url
      altText
      width
      height
    }
    products(first: 10) {
      edges {
        node {
          id
          title
          handle
          vendor
          productType
          totalInventory
          priceRangeV2 {
            minVariantPrice {
              amount
              currencyCode
            }
            maxVariantPrice {
              amount
              currencyCode
            }
          }
          images(first: 1) {
            edges {
              node {
                id
                url
                altText
              }
            }
          }
        }
      }
    }
    rules {
      column
      relation
      condition
    }
  }
}
```

#### Collection by Handle Query Template
```graphql
query collectionByHandle($handle: String!) {
  collectionByHandle(handle: $handle) {
    id
    title
    handle
    description
    collectionType
    status
    productsCount
    image {
      id
      url
      altText
    }
    products(first: 5) {
      edges {
        node {
          id
          title
          handle
          vendor
          priceRangeV2 {
            minVariantPrice {
              amount
              currencyCode
            }
          }
          images(first: 1) {
            edges {
              node {
                id
                url
                altText
              }
            }
          }
        }
      }
    }
  }
}
```

#### Collection Count Query Template
```graphql
query collectionsCount($query: String) {
  collectionsCount(query: $query) {
    count
  }
}
```

#### Smart Collection Rules Template
```graphql
query collection($id: ID!) {
  collection(id: $id) {
    id
    title
    collectionType
    rules {
      column
      relation
      condition
    }
    productsCount
  }
}
```

## Response Guidelines

When generating a collection query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find collections matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what collections you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 collections at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find collection information from your store.

**Query:**
```graphql
query collections($first: Int!, $query: String) {
  collections(first: $first, query: $query) {
    edges {
      node {
        id
        title
        handle
        description
        collectionType
        status
        productsCount
        image {
          id
          url
          altText
        }
      }
    }
  }
}
```

**What this does:**
This searches for collections in your store and returns their basic information and product counts.

**What I need from you:**
- What specific collections are you looking for? (by title, type, status, etc.)
- How many collections would you like to see?

**Examples of what you can search for:**
- All active collections
- Smart collections vs manual collections
- Collections with specific titles (like "Summer" or "Sale")
- Collections created after a certain date
- Collections with specific product counts

Would you like me to help you find specific collections?
```

## Common Collection Query Scenarios

### Collection Discovery and Management
- **Use**: `collections` query with filters
- **Filters**: Title, type, status, product count, creation date
- **Considerations**: Search performance, result relevance

### Individual Collection Lookup
- **Use**: `collection`, `collectionByHandle`, or `collectionByIdentifier` query
- **Use case**: Complete collection details for editing or display
- **Considerations**: Data completeness, product information, rules

### Collection Analytics
- **Use**: `collectionsCount` query
- **Use case**: Collection metrics, business intelligence
- **Considerations**: Data aggregation, reporting needs

### Smart Collection Management
- **Use**: `collection` query with rules
- **Use case**: Understanding automated collection rules
- **Considerations**: Rule complexity, product matching logic

### Collection Product Analysis
- **Use**: `collection` query with products
- **Use case**: Product organization, cross-selling opportunities
- **Considerations**: Product data volume, pagination needs

## Search Query Examples

### Basic Collection Searches
- `title:Summer` - Collections with "Summer" in title
- `collection_type:SMART` - Only smart collections
- `status:ACTIVE` - Only active collections
- `products_count:>10` - Collections with more than 10 products
- `created_at:>2024-01-01` - Collections created after specific date

### Advanced Collection Searches
- `title:Summer AND status:ACTIVE` - Active summer collections
- `collection_type:SMART AND products_count:>50` - Large smart collections
- `created_at:>2024-01-01 AND status:ACTIVE` - Recently created active collections
- `NOT status:ARCHIVED AND products_count:>0` - Non-empty active collections

### Collection Performance Searches
- `products_count:0` - Empty collections
- `products_count:>100` - Very large collections
- `updated_at:<2024-01-01` - Stale collections not updated recently
- `collection_type:SMART AND title:*Sale*` - Smart sale collections

## Collection Types and Use Cases

### Smart Collections
- **Use**: Automated product grouping based on rules
- **Rules**: Title, type, vendor, tag, price, inventory, weight
- **Benefits**: Automatically updated, easy maintenance
- **Considerations**: Rule complexity, performance impact

### Custom Collections
- **Use**: Manually curated product selections
- **Management**: Manual product addition/removal
- **Benefits**: Complete control, featured products
- **Considerations**: Manual maintenance overhead

### Mixed Strategy
- **Use**: Combination of smart and custom collections
- **Approach**: Smart for automation, custom for curation
- **Benefits**: Balance of automation and control
- **Considerations**: Consistent user experience

## Collection Management Best Practices

### Collection Organization
- Use clear, descriptive titles
- Implement consistent naming conventions
- Consider customer navigation patterns
- Plan for seasonal collections

### Smart Collection Rules
- Keep rules simple and performant
- Test rule logic thoroughly
- Consider rule interactions
- Monitor collection performance

### Product Assignment
- Avoid over-assigning products to collections
- Consider collection relevance
- Monitor product collection relationships
- Plan for collection cross-references

### SEO Considerations
- Use SEO-friendly handles
- Write compelling descriptions
- Optimize collection images
- Consider collection hierarchy

## Performance Optimization Tips

### Query Efficiency
- Use specific filters to reduce result sets
- Request only necessary fields for your use case
- Limit product data within collections
- Implement pagination for large collections

### Data Caching
- Cache collection metadata and product counts
- Implement appropriate cache invalidation
- Consider collection update frequency
- Balance cache size with performance needs

### Smart Collection Performance
- Monitor smart collection rule performance
- Optimize complex rules
- Consider collection rebuild frequency
- Plan for scaling with product growth

### Bulk Operations
- Use GraphQL aliases for multiple collection lookups
- Batch collection queries when possible
- Consider bulk operations for collection management
- Monitor query complexity and costs

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
