# Shopify Product Queries

This guide helps you generate accurate GraphQL queries for fetching product information from Shopify.

## Instructions for Query Generation

When a user requests to fetch product data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific product data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Product Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/products

**What to learn from this documentation:**
- Required input fields for product queries
- Available filters and search parameters
- Pagination and sorting options
- Product data structure and available fields
- Query optimization techniques

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/products#return-fields
  - *Review only when you need to verify what product data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/products#examples
  - *Review only when you need sample query patterns for complex product scenarios*

### Individual Product Queries Documentation

#### Specific Product Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/product

**What to learn from this documentation:**
- Fetch individual product by ID
- Complete product data structure
- Related product data (variants, images, collections)

#### Product by Handle Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productByHandle

**What to learn from this documentation:**
- Fetch product by URL handle
- Handle validation and formatting
- SEO-friendly product access

#### Product by Identifier Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productByIdentifier

**What to learn from this documentation:**
- Fetch product by various identifiers (SKU, barcode, etc.)
- Identifier validation and formatting
- Multiple identifier support

#### Product Operation Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productOperation

**What to learn from this documentation:**
- Check product operation status
- Product processing workflows
- Bulk operation tracking

### Product Count and Analytics Documentation

#### Product Count Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productsCount

**What to learn from this documentation:**
- Product count aggregation options
- Filtering for count queries
- Performance considerations for large datasets

#### Product Tags Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productTags

**What to learn from this documentation:**
- Fetch all product tags
- Tag usage analytics
- Product categorization data

#### Product Types Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productTypes

**What to learn from this documentation:**
- Fetch all product types
- Product type analytics
- Category management data

#### Product Vendors Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productVendors

**What to learn from this documentation:**
- Fetch all product vendors
- Vendor analytics
- Supplier management data

### Product Variant Queries Documentation

#### Product Variant Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariant

**What to learn from this documentation:**
- Fetch individual product variant
- Variant-specific data structure
- Inventory and pricing information

#### Product Variant by Identifier Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariantByIdentifier

**What to learn from this documentation:**
- Fetch variant by SKU or barcode
- Variant identifier validation
- Inventory lookup by identifier

#### Product Variants Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariants

**What to learn from this documentation:**
- Fetch multiple product variants
- Variant filtering and pagination
- Bulk variant data access

#### Product Variants Count Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariantsCount

**What to learn from this documentation:**
- Variant count aggregation
- Variant analytics
- Inventory reporting

### Price List Queries Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/priceList

**What to learn from this documentation:**
- Fetch price list information
- Pricing tier management
- Currency-specific pricing

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying product data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Product Query Cost Calculation**:
   - Product queries have moderate to high costs
   - Complex products with many variants and images increase cost
   - Large result sets require pagination to manage costs
   - Formula: `cost = base_query_cost + product_complexity + result_size`

3. **Best Practices for Product Query Generation**:
   - **Include only required fields**: Don't request unnecessary product data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed product data
   - **Batch efficiently**: Query multiple products in single requests when possible

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all products with excessive fields
   query {
     products(first: 50) {
       edges {
         node {
           id title handle variants { edges { node { ... } } }
           images { edges { node { ... } } } collections { edges { node { ... } } }
           metafields { ... } tags
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches products with essential fields only
   query {
     products(first: 10, query:"status:ACTIVE") {
       edges {
         node {
           id title handle status
           variants(first: 5) {
             edges {
               node {
                 id title sku price
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

When generating product queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$PRODUCT_ID$` | Product ID | Ask user if not provided | `gid://shopify/Product/123456789` |
| `$PRODUCT_HANDLE$` | Product handle | Ask user if not provided | `"awesome-t-shirt"` |
| `$SKU$` | Product SKU | Ask user if not provided | `"TSHIRT-001"` |
| `$BARCODE$` | Product barcode | Ask user if not provided | `"1234567890123"` |
| `$TITLE$` | Product title | Ask user if not provided | `"Awesome T-Shirt"` |
| `$TAG$` | Product tag | Ask user if not provided | `"new-arrival"` |
| `$PRODUCT_TYPE$` | Product type | Ask user if not provided | `"Clothing"` |
| `$VENDOR$` | Product vendor | Ask user if not provided | `"Awesome Brand"` |
| `$STATUS$` | Product status | `"ACTIVE"` | `"ARCHIVED"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"title:T-shirt AND tag:new"` |
| `$VARIANT_ID$` | Variant ID | Ask user if not provided | `gid://shopify/ProductVariant/987654321` |

### Query Structure Templates

#### Multiple Products Query Template
```graphql
query products($first: Int!, $query: String, $after: String) {
  products(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        handle
        status
        createdAt
        updatedAt
        vendor
        productType
        tags
        totalInventory
        variants(first: 10) {
          edges {
            node {
              id
              title
              sku
              barcode
              price
              compareAtPrice
              inventoryQuantity
              selectedOptions {
                name
                value
              }
            }
          }
        }
        images(first: 5) {
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
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### Specific Product Query Template
```graphql
query product($id: ID!) {
  product(id: $id) {
    id
    title
    handle
    description
    status
    createdAt
    updatedAt
    vendor
    productType
    tags
    totalInventory
    variants(first: 50) {
      edges {
        node {
          id
          title
          sku
          barcode
          price
          compareAtPrice
          inventoryQuantity
          weight
          weightUnit
          selectedOptions {
            name
            value
          }
          image {
            id
            url
            altText
          }
        }
      }
    }
    images(first: 20) {
      edges {
        node {
          id
          url
          altText
          width
          height
        }
      }
    }
    collections(first: 10) {
      edges {
        node {
          id
          title
          handle
        }
      }
    }
  }
}
```

#### Product by Handle Query Template
```graphql
query productByHandle($handle: String!) {
  productByHandle(handle: $handle) {
    id
    title
    handle
    description
    status
    vendor
    productType
    tags
    variants(first: 10) {
      edges {
        node {
          id
          title
          sku
          price
          inventoryQuantity
          selectedOptions {
            name
            value
          }
        }
      }
    }
    images(first: 5) {
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
```

#### Product Count Query Template
```graphql
query productsCount($query: String) {
  productsCount(query: $query) {
    count
  }
}
```

#### Product Variants Query Template
```graphql
query productVariants($first: Int!, $query: String, $after: String) {
  productVariants(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        title
        sku
        barcode
        price
        compareAtPrice
        inventoryQuantity
        weight
        weightUnit
        selectedOptions {
          name
          value
        }
        product {
          id
          title
          handle
        }
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

#### Product Tags Query Template
```graphql
query productTags($first: Int!, $query: String) {
  productTags(first: $first, query: $query) {
    edges {
      node
    }
  }
}
```

## Response Guidelines

When generating a product query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find products matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what products you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 products at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find product information from your store.

**Query:**
```graphql
query products($first: Int!, $query: String) {
  products(first: $first, query: $query) {
    edges {
      node {
        id
        title
        handle
        status
        vendor
        productType
        tags
        totalInventory
        variants(first: 5) {
          edges {
            node {
              id
              title
              sku
              price
              inventoryQuantity
              selectedOptions {
                name
                value
              }
            }
          }
        }
        images(first: 3) {
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
```

**What this does:**
This searches for products in your store and returns their basic information, variants, and images.

**What I need from you:**
- What specific products are you looking for? (by title, SKU, tag, vendor, etc.)
- How many products would you like to see?

**Examples of what you can search for:**
- All products with a specific tag (like "sale" or "new-arrival")
- Products from a specific vendor
- Products by type (like "clothing" or "electronics")
- Products with low inventory
- Products by SKU or barcode

Would you like me to help you find specific products?
```

## Common Product Query Scenarios

### Product Search and Discovery
- **Use**: `products` query with filters
- **Filters**: Title, SKU, vendor, type, tags, status, inventory
- **Considerations**: Search performance, result relevance

### Individual Product Lookup
- **Use**: `product`, `productByHandle`, or `productByIdentifier` query
- **Use case**: Complete product details for editing or display
- **Considerations**: Data completeness, variant information

### Product Inventory Management
- **Use**: `products` or `productVariants` query with inventory filters
- **Use case**: Stock monitoring, reorder planning
- **Considerations**: Real-time data, inventory accuracy

### Product Analytics
- **Use**: `productsCount`, `productTags`, `productTypes`, `productVendors` queries
- **Use case**: Business metrics, catalog analysis
- **Considerations**: Data aggregation, reporting needs

### Product Performance Analysis
- **Use**: `products` query with sales-related filters
- **Use case**: Best-seller identification, underperforming products
- **Considerations**: Sales data integration, performance metrics

## Search Query Examples

### Basic Product Searches
- `title:T-shirt` - Products with "T-shirt" in title
- `vendor:Awesome Brand` - Products from specific vendor
- `tag:new-arrival` - Products with specific tag
- `status:ACTIVE` - Only active products
- `product_type:Clothing` - Products of specific type

### Advanced Product Searches
- `title:T-shirt AND vendor:Awesome Brand` - T-shirts from specific vendor
- `inventory_total:<10` - Products with low inventory
- `created_at:>2024-01-01` - Products created after specific date
- `tag:sale AND price:<50` - Sale products under $50
- `NOT tag:archived AND status:ACTIVE` - Active non-archived products

### Inventory and Stock Searches
- `inventory_total:0` - Out of stock products
- `inventory_total:<5` - Low stock products
- `variants.inventory_quantity:>100` - Products with high inventory
- `tag:clearance AND inventory_total:>0` - In-stock clearance items

### Variant-Specific Searches
- `variants.sku:TSHIRT-001` - Products with specific SKU
- `variants.barcode:1234567890123` - Products with specific barcode
- `variants.price:>100` - Products with variants over $100
- `variants.inventory_quantity:0` - Products with out-of-stock variants

## Performance Optimization Tips

### Query Efficiency
- Use specific filters to reduce result sets
- Request only necessary fields
- Implement pagination for large catalogs
- Use cursor-based pagination for better performance

### Data Caching
- Cache frequently accessed product data
- Implement appropriate cache invalidation strategies
- Consider product data change frequency
- Balance cache size with performance needs

### Bulk Operations
- Use GraphQL aliases for multiple similar queries
- Batch product lookups when possible
- Consider bulk operations for large datasets
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
