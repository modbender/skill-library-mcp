# Shopify Product Creation & Management

This guide helps you generate accurate GraphQL mutations for creating products and managing product data in Shopify.

## Instructions for Mutation Generation

When a user requests to create products or manage product data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific product creation requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider product catalog organization** - ensure proper categorization

## Official Documentation

### Primary Product Creation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productCreate

**What to learn from this documentation:**
- Required input fields for product creation
- Product data structure and validation
- Variant creation within products
- Image and media handling
- SEO and metadata management

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productCreate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productCreate#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productCreate#examples
  - *Review only when you need sample mutation patterns for complex product scenarios*

### Product Management Mutations Documentation

#### Product Set Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet

**What to learn from this documentation:**
- Alternative product creation method
- Product data synchronization
- Bulk product operations
- Product update and creation workflows

#### Product Duplicate Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDuplicate

**What to learn from this documentation:**
- Product duplication workflows
- Variant and image copying
- SKU and handle management
- Duplicate product customization

#### Product Bundle Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productBundleCreate

**What to learn from this documentation:**
- Bundle product creation
- Component product relationships
- Bundle pricing strategies
- Inventory management for bundles

#### Product Options Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate

**What to learn from this documentation:**
- Product option management
- Variant option creation
- Option value management
- Product customization workflows

### Price Management Documentation

#### Price Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/price

**What to learn from this documentation:**
- Price list management
- Currency-specific pricing
- Tiered pricing strategies
- Price rule creation

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating products.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Product Creation Cost Calculation**:
   - Product creation mutations have high costs
   - Complex products with many variants and images increase cost significantly
   - Bundle and option creation add additional complexity
   - Formula: `cost = base_mutation_cost + product_complexity + variant_count + media_count`

3. **Best Practices for Product Creation Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate product data**: Ensure proper SKU, pricing, and inventory data
   - **Handle images efficiently**: Optimize image sizes and formats
   - **Batch related operations**: Create variants and options in logical groups
   - **Use proper error handling**: Always check for user errors in mutation response

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates product with excessive optional fields
   mutation productCreate($input: ProductInput!) {
     productCreate(input: $input) {
       product { id title variants { edges { node { ... } } } images { ... } metafields { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates product with essential fields only
   mutation productCreate($input: ProductInput!) {
     productCreate(input: $input) {
       product {
         id title handle status
         variants(first: 5) {
           edges {
             node { id title sku price }
           }
         }
       }
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating product creation mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$PRODUCT_TITLE$` | Product title | Ask user if not provided | `"Awesome T-Shirt"` |
| `$PRODUCT_HANDLE$` | Product handle | Auto-generated from title | `"awesome-t-shirt"` |
| `$PRODUCT_DESCRIPTION$` | Product description | Ask user if not provided | `"High-quality cotton t-shirt"` |
| `$PRODUCT_TYPE$` | Product type | Ask user if not provided | `"Clothing"` |
| `$VENDOR$` | Product vendor | Ask user if not provided | `"Awesome Brand"` |
| `$SKU$` | Product SKU | Ask user if not provided | `"TSHIRT-001"` |
| `$PRICE$` | Product price | Ask user if not provided | `"29.99"` |
| `$INVENTORY_QUANTITY$` | Inventory quantity | Ask user if not provided | `100` |
| `$WEIGHT$` | Product weight | Ask user if not provided | `0.5` |
| `$WEIGHT_UNIT$` | Weight unit | `"KILOGRAMS"` | `"POUNDS"` |
| `$TAGS$` | Product tags | Ask user if not provided | `["new", "summer", "clothing"]` |
| `$OPTION1_NAME$` | First option name | `"Size"` | `"Color"` |
| `$OPTION1_VALUE$` | First option value | `"Medium"` | `"Red"` |
| `$OPTION2_NAME$` | Second option name | `"Color"` | `"Size"` |
| `$OPTION2_VALUE$` | Second option value | `"Blue"` | `"Large"` |
| `$IMAGE_URL$` | Product image URL | Ask user if not provided | `"https://example.com/image.jpg"` |
| `$IMAGE_ALT_TEXT$` | Image alt text | Ask user if not provided | `"Awesome T-Shirt in Red"` |
| `$SEO_TITLE$` | SEO title | Auto-generated | `"Awesome T-Shirt - Premium Quality"` |
| `$SEO_DESCRIPTION$` | SEO description | Auto-generated | `"Shop our premium quality t-shirt"` |
| `$SOURCE_PRODUCT_ID$` | Source product for duplication | Ask user if not provided | `gid://shopify/Product/123456789` |
| `$BUNDLE_COMPONENTS$` | Bundle component IDs | Ask user if not provided | `[gid://shopify/Product/987654321]` |

### Mutation Structure Templates

#### Basic Product Creation Template
```graphql
mutation productCreate($input: ProductInput!) {
  productCreate(input: $input) {
    product {
      id
      title
      handle
      description
      status
      vendor
      productType
      tags
      createdAt
      updatedAt
      variants(first: 10) {
        edges {
          node {
            id
            title
            sku
            price
            inventoryQuantity
            weight
            weightUnit
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
    userErrors {
      field
      message
    }
  }
}
```

#### Product with Multiple Variants Template
```graphql
mutation productCreate($input: ProductInput!) {
  productCreate(input: $input) {
    product {
      id
      title
      handle
      status
      variants(first: 20) {
        edges {
          node {
            id
            title
            sku
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
      images(first: 10) {
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
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Product Set Template
```graphql
mutation productSet($input: ProductSetInput!) {
  productSet(input: $input) {
    product {
      id
      title
      handle
      status
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Product Duplicate Template
```graphql
mutation productDuplicate($productId: ID!, $newTitle: String, $includeImages: Boolean) {
  productDuplicate(productId: $productId, newTitle: $newTitle, includeImages: $includeImages) {
    product {
      id
      title
      handle
      status
      variants(first: 10) {
        edges {
          node {
            id
            title
            sku
            price
            inventoryQuantity
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

#### Product Bundle Creation Template
```graphql
mutation productBundleCreate($input: ProductBundleInput!) {
  productBundleCreate(input: $input) {
    productBundle {
      id
      name
      description
      product {
        id
        title
        handle
        status
      }
      components {
        id
        quantity
        product {
          id
          title
          handle
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

#### Product Options Creation Template
```graphql
mutation productOptionsCreate($productId: ID!, $options: [ProductOptionInput!]!) {
  productOptionsCreate(productId: $productId, options: $options) {
    product {
      id
      title
      handle
      options {
        id
        name
        values
        position
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Price Management Template
```graphql
mutation price($input: PriceInput!) {
  price(input: $input) {
    price {
      id
      amount
      currencyCode
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a product creation mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create a new product in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the product title, price, and basic details")
3. **Explain any limitations** in simple terms (e.g., "This will create the product but won't automatically add it to collections")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new product in your store.

**Mutation:**
```graphql
mutation productCreate($input: ProductInput!) {
  productCreate(input: $input) {
    product {
      id
      title
      handle
      status
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
    }
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This creates a new product in your Shopify store with the information you provide.

**What I need from you:**
- Product title and description
- Product type and vendor
- Pricing information
- Inventory details
- Any variants (sizes, colors, etc.)

**Important notes:**
- The product will be created as a draft by default
- You'll need to publish it to make it visible to customers
- SKUs should be unique for each variant
- Images should be optimized for web use

Would you like me to help you create a specific product?
```

## Common Product Creation Scenarios

### Simple Product Creation
- **Use**: `productCreate` mutation
- **Use case**: Single product with basic information
- **Considerations**: Title, description, price, inventory

### Multi-Variant Product Creation
- **Use**: `productCreate` with variant options
- **Use case**: Products with sizes, colors, or other variations
- **Considerations**: Option naming, SKU generation, inventory tracking

### Product Duplication
- **Use**: `productDuplicate` mutation
- **Use case**: Creating similar products, seasonal variations
- **Considerations**: Image copying, SKU customization, title changes

### Bundle Product Creation
- **Use**: `productBundleCreate` mutation
- **Use case**: Product bundles, gift sets, combo deals
- **Considerations**: Component relationships, pricing strategy, inventory

### Product Options Management
- **Use**: `productOptionsCreate` mutation
- **Use case**: Adding customization options, variant management
- **Considerations**: Option naming, value management, variant generation

### Product Set Operations
- **Use**: `productSet` mutation
- **Use case**: Bulk product updates, data synchronization
- **Considerations**: Data validation, update scope, performance

## Product Data Validation Guidelines

### Required Product Fields
- **Title**: Must be descriptive and unique
- **Product Type**: Should match store categorization
- **Vendor**: Should be consistent across products
- **Status**: Draft for testing, Active for selling

### Variant Data Validation
- **SKU**: Must be unique across all variants
- **Price**: Must be positive numbers with proper currency
- **Inventory**: Non-negative integers
- **Weight**: Positive numbers with correct units

### Image Requirements
- **Format**: JPG, PNG, GIF, or WEBP
- **Size**: Optimized for web (under 5MB recommended)
- **Alt Text**: Descriptive for accessibility and SEO
- **Order**: Logical arrangement for product display

### SEO Considerations
- **Handles**: URL-friendly, lowercase with hyphens
- **Meta Titles**: Under 60 characters for search results
- **Meta Descriptions**: Under 160 characters for search snippets
- **Tags**: Relevant for search and filtering

## Error Handling

### Common Product Creation Errors
- **Duplicate SKU**: Ensure SKUs are unique across all products
- **Invalid Price**: Check currency and numeric format
- **Missing Required Fields**: Verify all required product data
- **Image Upload Issues**: Check image format and size limits

### Variant Creation Errors
- **Invalid Options**: Ensure option names and values are valid
- **Duplicate Combinations**: Avoid duplicate variant combinations
- **Inventory Conflicts**: Check inventory tracking settings
- **Price Mismatches**: Verify pricing across variants

### Bundle Creation Errors
- **Invalid Components**: Ensure component products exist
- **Circular References**: Avoid bundles that include themselves
- **Inventory Issues**: Check component product availability
- **Pricing Conflicts**: Verify bundle pricing logic

## Best Practices

### Before Creating Products
1. **Plan product structure** - organize categories and types
2. **Prepare product data** - gather all necessary information
3. **Optimize images** - resize and compress for web
4. **Set up inventory tracking** - configure inventory management
5. **Plan SEO strategy** - prepare titles, descriptions, and tags

### After Creating Products
1. **Verify product data** - check all information is correct
2. **Test variants** - ensure all combinations work properly
3. **Add to collections** - organize products for navigation
4. **Set up inventory** - configure stock levels and tracking
5. **Publish product** - make available for customers

### Ongoing Product Management
1. **Monitor inventory levels** - maintain adequate stock
2. **Update product information** - keep descriptions current
3. **Optimize pricing** - adjust based on performance
4. **Manage images** - update photos as needed
5. **Analyze performance** - track sales and customer feedback

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
