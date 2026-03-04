# Shopify Collection Creation & Management

This guide helps you generate accurate GraphQL mutations for creating collections and managing collection data in Shopify.

## Instructions for Mutation Generation

When a user requests to create collections or manage collection data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific collection creation requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider collection organization strategy** - plan for product categorization

## Official Documentation

### Primary Collection Creation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate

**What to learn from this documentation:**
- Required input fields for collection creation
- Collection data structure and validation
- Smart vs custom collection types
- Collection rules and automation
- SEO and metadata management

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate#examples
  - *Review only when you need sample mutation patterns for collection creation scenarios*

### Collection Management Mutations Documentation

#### Collection Add Products Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProducts

**What to learn from this documentation:**
- Adding products to existing collections
- Bulk product addition workflows
- Collection-product relationship management
- Performance considerations for large additions

#### Collection Duplicate Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDuplicate

**What to learn from this documentation:**
- Collection duplication workflows
- Product copying and reference management
- Collection customization after duplication
- SEO and handle management for duplicates

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating collections.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Collection Creation Cost Calculation**:
   - Collection creation mutations have moderate costs
   - Smart collections with complex rules increase cost
   - Adding many products to collections significantly increases cost
   - Formula: `cost = base_mutation_cost + collection_complexity + product_count + rule_complexity`

3. **Best Practices for Collection Creation Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Optimize smart collection rules**: Keep rules simple and performant
   - **Batch product additions**: Add products in reasonable batch sizes
   - **Use proper error handling**: Always check for user errors in mutation response
   - **Consider collection type**: Choose smart vs custom based on use case

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates collection with excessive product data
   mutation collectionCreate($input: CollectionInput!) {
     collectionCreate(input: $input) {
       collection { id title products { edges { node { ... } } } rules { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates collection with essential fields only
   mutation collectionCreate($input: CollectionInput!) {
     collectionCreate(input: $input) {
       collection {
         id
         title
         handle
         description
         collectionType
         productsCount
       }
       userErrors {
         field
         message
       }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating collection creation mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$COLLECTION_TITLE$` | Collection title | Ask user if not provided | `"Summer Collection"` |
| `$COLLECTION_HANDLE$` | Collection handle | Auto-generated from title | `"summer-collection"` |
| `$COLLECTION_DESCRIPTION$` | Collection description | Ask user if not provided | `"Our latest summer arrivals"` |
| `$COLLECTION_TYPE$` | Collection type | `"CUSTOM"` or `"SMART"` | `"SMART"` |
| `$SEO_TITLE$` | SEO title | Auto-generated | `"Summer Collection - New Arrivals"` |
| `$SEO_DESCRIPTION$` | SEO description | Auto-generated | `"Shop our latest summer collection"` |
| `$PRODUCT_IDS$` | Product IDs to add | Ask user if not provided | `[gid://shopify/Product/123456789]` |
| `$RULE_COLUMN$` | Smart collection rule column | Ask user if not provided | `"TAG"` |
| `$RULE_RELATION$` | Smart collection rule relation | Ask user if not provided | `"CONTAINS"` |
| `$RULE_CONDITION$` | Smart collection rule condition | Ask user if not provided | `"summer"` |
| `$SOURCE_COLLECTION_ID$` | Source collection for duplication | Ask user if not provided | `gid://shopify/Collection/987654321` |
| `$IMAGE_URL$` | Collection image URL | Ask user if not provided | `"https://example.com/collection.jpg"` |
| `$IMAGE_ALT_TEXT$` | Image alt text | Ask user if not provided | `"Summer collection featured products"` |

### Mutation Structure Templates

#### Basic Collection Creation Template
```graphql
mutation collectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection {
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
    userErrors {
      field
      message
    }
  }
}
```

#### Smart Collection with Rules Template
```graphql
mutation collectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection {
      id
      title
      handle
      description
      collectionType
      status
      productsCount
      rules {
        column
        relation
        condition
      }
      image {
        id
        url
        altText
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Custom Collection with Products Template
```graphql
mutation collectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection {
      id
      title
      handle
      description
      collectionType
      status
      productsCount
      products(first: 10) {
        edges {
          node {
            id
            title
            handle
            vendor
            productType
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
    userErrors {
      field
      message
    }
  }
}
```

#### Add Products to Collection Template
```graphql
mutation collectionAddProducts($collectionId: ID!, $productIds: [ID!]!) {
  collectionAddProducts(collectionId: $collectionId, productIds: $productIds) {
    collection {
      id
      title
      productsCount
      products(first: 5) {
        edges {
          node {
            id
            title
            handle
          }
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Collection Duplicate Template
```graphql
mutation collectionDuplicate($collectionId: ID!, $newTitle: String) {
  collectionDuplicate(collectionId: $collectionId, newTitle: $newTitle) {
    collection {
      id
      title
      handle
      description
      collectionType
      productsCount
      image {
        id
        url
        altText
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a collection creation mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create a new collection to organize your products")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the collection name and what products should be included")
3. **Explain any limitations** in simple terms (e.g., "This creates the collection but you'll need to add products separately")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new collection for your store.

**Mutation:**
```graphql
mutation collectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection {
      id
      title
      handle
      description
      collectionType
      status
      productsCount
    }
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This creates a new collection in your Shopify store to organize your products.

**What I need from you:**
- Collection name and description
- Collection type (smart collection with automatic rules or custom collection with manual product selection)
- Whether you want to add products now or later

**Important notes:**
- Smart collections automatically include products based on rules you define
- Custom collections require manual product addition
- Collections help customers find related products easily

Would you like me to help you create a specific collection?
```

## Common Collection Creation Scenarios

### Smart Collection Creation
- **Use**: `collectionCreate` mutation with rules
- **Use case**: Automatically organized collections based on product attributes
- **Considerations**: Rule complexity, performance impact, maintenance needs

### Custom Collection Creation
- **Use**: `collectionCreate` mutation without rules
- **Use case**: Manually curated product selections
- **Considerations**: Manual maintenance, product selection control

### Seasonal Collection Creation
- **Use**: `collectionCreate` with seasonal rules or manual selection
- **Use case**: Time-based product groupings
- **Considerations**: Timing, product availability, marketing coordination

### Featured Products Collection
- **Use**: `collectionCreate` with manual product selection
- **Use case**: Highlighting specific products
- **Considerations**: Product selection criteria, rotation strategy

### Collection Duplication
- **Use**: `collectionDuplicate` mutation
- **Use case**: Creating similar collections, seasonal variations
- **Considerations**: Product copying, rule adaptation, SEO implications

## Collection Types and Strategies

### Smart Collections
- **Automation**: Products automatically added/removed based on rules
- **Maintenance**: Low ongoing maintenance
- **Performance**: Can be resource-intensive with complex rules
- **Use Cases**: Tag-based collections, price ranges, new arrivals

### Custom Collections
- **Control**: Complete control over product selection
- **Maintenance**: Higher manual maintenance required
- **Performance**: Better performance for large collections
- **Use Cases**: Featured products, curated selections, editorial content

### Hybrid Approach
- **Strategy**: Combine smart and custom collections
- **Benefits**: Balance automation and control
- **Implementation**: Use smart for broad categories, custom for featured items

## Smart Collection Rules

### Common Rule Types
- **Tag Rules**: `tag CONTAINS "summer"`
- **Vendor Rules**: `vendor EQUALS "Awesome Brand"`
- **Type Rules**: `product_type EQUALS "Clothing"`
- **Price Rules**: `price GREATER_THAN 50`
- **Inventory Rules**: `inventory_total GREATER_THAN 0`
- **Title Rules**: `title CONTAINS "T-shirt"`

### Rule Combinations
- **AND Logic**: Multiple conditions must all be true
- **OR Logic**: Any condition can be true
- **Complex Rules**: Multiple rule groups for sophisticated filtering

### Rule Best Practices
- **Keep rules simple**: Avoid overly complex conditions
- **Test thoroughly**: Verify rules include intended products
- **Monitor performance**: Watch for slow-loading collections
- **Document logic**: Keep record of rule purposes

## Collection Organization Strategies

### Hierarchical Structure
- **Main Categories**: Broad product categories
- **Subcategories**: More specific groupings
- **Filter Collections**: Specialized views and searches

### Seasonal Organization
- **Current Season**: Active seasonal collections
- **Upcoming Season**: Preview collections
- **Archive**: Past seasonal collections

### Customer Journey
- **New Arrivals**: Latest products
- **Best Sellers**: Popular products
- **Sale Items**: Discounted products
- **Featured Items**: Curated selections

## Data Validation Guidelines

### Required Collection Fields
- **Title**: Must be descriptive and unique
- **Collection Type**: Must be SMART or CUSTOM
- **Status**: Draft for testing, Active for publication

### Smart Collection Rules
- **Valid Columns**: Must use supported rule columns
- **Proper Relations**: Must use valid relation operators
- **Logical Conditions**: Conditions must make business sense

### Product Validation
- **Product Existence**: Products must exist and be accessible
- **Publication Status**: Products should be published for visibility
- **Inventory Considerations**: Consider stock levels for collections

## Error Handling

### Common Collection Creation Errors
- **Duplicate Title**: Collection titles must be unique
- **Invalid Rules**: Smart collection rules must be valid
- **Permission Issues**: Verify API access for collection operations
- **Product Access**: Products must be accessible for addition

### Smart Collection Rule Errors
- **Invalid Columns**: Rule columns must be supported
- **Malformed Conditions**: Rule conditions must be properly formatted
- **Performance Issues**: Complex rules may cause timeouts
- **Logic Conflicts**: Contradictory rules may cause issues

### Product Addition Errors
- **Product Not Found**: Products must exist and be accessible
- **Already in Collection**: Avoid duplicate product additions
- **Publication Status**: Unpublished products may not be visible
- **Permission Denied**: Verify access to products and collections

## Best Practices

### Before Creating Collections
1. **Plan collection structure** - organize categories logically
2. **Choose collection type** - smart vs custom based on needs
3. **Prepare product data** - ensure products are properly tagged
4. **Test rules** - validate smart collection logic
5. **Consider SEO** - plan handles and metadata

### After Creating Collections
1. **Verify collection setup** - confirm all settings are correct
2. **Add products** - populate collections with appropriate products
3. **Test functionality** - ensure collections work as expected
4. **Monitor performance** - watch for loading issues
5. **Optimize rules** - refine smart collection rules if needed

### Ongoing Collection Management
1. **Regular reviews** - update collections as needed
2. **Performance monitoring** - track collection effectiveness
3. **Rule optimization** - improve smart collection performance
4. **User feedback** - gather feedback from customers
5. **SEO maintenance** - keep collection metadata current

## SEO Considerations

### Collection Handles
- **URL-Friendly**: Use lowercase with hyphens
- **Descriptive**: Include relevant keywords
- **Unique**: Avoid duplicate handles
- **Consistent**: Follow naming conventions

### Meta Information
- **Titles**: Under 60 characters for search results
- **Descriptions**: Under 160 characters for search snippets
- **Keywords**: Include relevant search terms
- **Structure**: Use hierarchical keyword organization

### Collection Images
- **High Quality**: Use clear, professional images
- **Optimized Size**: Balance quality with loading speed
- **Alt Text**: Descriptive for accessibility and SEO
- **Consistent Style**: Maintain visual consistency

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
