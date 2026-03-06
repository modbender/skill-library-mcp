# Shopify Product Update & Management

This guide helps you generate accurate GraphQL mutations for updating products and managing product data in Shopify.

## Instructions for Mutation Generation

When a user requests to update products or manage product data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific product update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider product catalog impact** - understand how updates affect collections and orders

## Official Documentation

### Primary Product Update Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate

**What to learn from this documentation:**
- Required input fields for product updates
- Product data modification options
- Variant update capabilities
- Image and media management
- SEO and metadata updates

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate#examples
  - *Review only when you need sample mutation patterns for complex update scenarios*

### Product Management Mutations Documentation

#### Product Unpublish Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUnpublish

**What to learn from this documentation:**
- Product publication status management
- Sales channel visibility control
- Unpublishing workflows and consequences
- Publication state management

#### Product Bundle Update Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productBundleUpdate

**What to learn from this documentation:**
- Bundle product modification
- Component relationship updates
- Bundle pricing adjustments
- Inventory management for bundles

#### Product Options Management Documentation

#### Product Options Reorder Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder

**What to learn from this documentation:**
- Option order management
- Variant option reorganization
- Product customization workflow updates
- Display order optimization

#### Product Option Update Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate

**What to learn from this documentation:**
- Individual option modification
- Option value updates
- Variant synchronization
- Product option management

### Price Management Documentation

#### Price List Update Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListUpdate

**What to learn from this documentation:**
- Price list modification
- Currency-specific pricing updates
- Tiered pricing adjustments
- Price rule management

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating products.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Product Update Cost Calculation**:
   - Product update mutations have moderate to high costs
   - Complex updates with many variants increase cost significantly
   - Bundle and option updates add additional complexity
   - Formula: `cost = base_mutation_cost + product_complexity + variant_count + update_scope`

3. **Best Practices for Product Update Mutation Generation**:
   - **Include only changed fields**: Don't send unchanged product data
   - **Validate updates**: Ensure data integrity before mutation
   - **Batch related updates**: Group multiple changes in single mutations
   - **Use proper error handling**: Always check for user errors in mutation response
   - **Consider dependencies**: Understand how updates affect variants and collections

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates product with excessive fields
   mutation productUpdate($input: ProductInput!) {
     productUpdate(input: $input) {
       product { id title variants { edges { node { ... } } } images { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates product with only changed fields
   mutation productUpdate($input: ProductInput!) {
     productUpdate(input: $input) {
       product {
         id
         title
         updatedAt
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

When generating product update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$PRODUCT_ID$` | Product ID to update | Ask user if not provided | `gid://shopify/Product/123456789` |
| `$PRODUCT_TITLE$` | Updated product title | Ask user if not provided | `"Updated Awesome T-Shirt"` |
| `$PRODUCT_DESCRIPTION$` | Updated product description | Ask user if not provided | `"Enhanced description with more details"` |
| `$PRODUCT_TYPE$` | Updated product type | Ask user if not provided | `"Premium Clothing"` |
| `$VENDOR$` | Updated product vendor | Ask user if not provided | `"Updated Brand"` |
| `$STATUS$` | Updated product status | `"ACTIVE"` | `"ARCHIVED"` |
| `$TAGS$` | Updated product tags | Ask user if not provided | `["updated", "premium", "featured"]` |
| `$SEO_TITLE$` | Updated SEO title | Ask user if not provided | `"Updated Awesome T-Shirt - Premium Quality"` |
| `$SEO_DESCRIPTION$` | Updated SEO description | Ask user if not provided | `"Shop our updated premium t-shirt"` |
| `$BUNDLE_ID$` | Bundle ID to update | Ask user if not provided | `gid://shopify/ProductBundle/987654321` |
| `$OPTION_ID$` | Option ID to update | Ask user if not provided | `gid://shopify/ProductOption/456789123` |
| `$OPTION_NAME$` | Updated option name | Ask user if not provided | `"Size"` |
| `$PRICE_LIST_ID$` | Price list ID to update | Ask user if not provided | `gid://shopify/PriceList/789123456` |
| `$PUBLICATION_ID$` | Publication ID for unpublish | Ask user if not provided | `gid://shopify/Publication/321654987` |

### Mutation Structure Templates

#### Basic Product Update Template
```graphql
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product {
      id
      title
      handle
      description
      status
      vendor
      productType
      tags
      updatedAt
      variants(first: 10) {
        edges {
          node {
            id
            title
            sku
            price
            inventoryQuantity
            updatedAt
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

#### Product Unpublish Template
```graphql
mutation productUnpublish($input: ProductUnpublishInput!) {
  productUnpublish(input: $input) {
    product {
      id
      title
      handle
      status
      publications(first: 10) {
        edges {
          node {
            id
            name
            publishableUnpublishable
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

#### Product Bundle Update Template
```graphql
mutation productBundleUpdate($input: ProductBundleInput!) {
  productBundleUpdate(input: $input) {
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
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Product Options Reorder Template
```graphql
mutation productOptionsReorder($productId: ID!, $optionIds: [ID!]!) {
  productOptionsReorder(productId: $productId, optionIds: $optionIds) {
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
      variants(first: 10) {
        edges {
          node {
            id
            title
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

#### Product Option Update Template
```graphql
mutation productOptionUpdate($productId: ID!, $optionId: ID!, $option: ProductOptionInput!) {
  productOptionUpdate(productId: $productId, optionId: $optionId, option: $option) {
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
      variants(first: 10) {
        edges {
          node {
            id
            title
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

#### Price List Update Template
```graphql
mutation priceListUpdate($input: PriceListInput!) {
  priceListUpdate(input: $input) {
    priceList {
      id
      name
      currencyCode
      createdAt
      updatedAt
      prices(first: 10) {
        edges {
          node {
            id
            amount
            currencyCode
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

## Response Guidelines

When generating a product update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the product information in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the product ID and what information you want to change")
3. **Explain any limitations** in simple terms (e.g., "This will update the product but may affect existing orders")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update an existing product in your store.

**Mutation:**
```graphql
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product {
      id
      title
      handle
      description
      status
      updatedAt
      variants(first: 5) {
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

**What this does:**
This updates an existing product's information in your Shopify store.

**What I need from you:**
- The product ID or title you want to update
- What specific information you want to change (title, description, price, etc.)
- Any new tags or categories you want to apply

**Important notes:**
- Changes will be reflected immediately across your store
- Updates may affect the product's visibility in collections
- SEO information will be updated for search engines

Would you like me to help you update a specific product?
```

## Common Product Update Scenarios

### Basic Product Information Updates
- **Use**: `productUpdate` mutation
- **Fields**: Title, description, vendor, product type, tags
- **Considerations**: SEO impact, collection organization, search visibility

### Product Status Management
- **Use**: `productUpdate` or `productUnpublish` mutation
- **Use case**: Publishing, archiving, hiding products
- **Considerations**: Sales channel visibility, customer access, order processing

### Product Bundle Updates
- **Use**: `productBundleUpdate` mutation
- **Use case**: Modifying bundle components, pricing
- **Considerations**: Component availability, pricing strategy, inventory impact

### Product Options Management
- **Use**: `productOptionUpdate` or `productOptionsReorder` mutation
- **Use case**: Changing variant options, reordering display
- **Considerations**: Variant synchronization, customer experience, inventory tracking

### Price List Updates
- **Use**: `priceListUpdate` mutation
- **Use case**: Adjusting prices, currency updates
- **Considerations**: Market-specific pricing, currency conversion, profit margins

## Product Update Impact Analysis

### SEO Impact
- **Title Changes**: May affect search rankings
- **Description Updates**: Impact search snippets
- **URL Handle Changes**: May break existing links
- **Tag Modifications**: Affect filtering and search

### Collection Impact
- **Product Type Changes**: May affect smart collection inclusion
- **Tag Updates**: Can add/remove from smart collections
- **Status Changes**: Affect collection visibility
- **Vendor Changes**: May impact vendor-based collections

### Order Impact
- **Price Updates**: Don't affect existing orders
- **Product Changes**: Preserve order history
- **Variant Updates**: May affect order processing
- **Inventory Updates**: Affect future order fulfillment

### Customer Impact
- **Product Availability**: Status changes affect customer access
- **Price Changes**: Visible to customers immediately
- **Description Updates**: Help customers make informed decisions
- **Image Updates**: Improve product presentation

## Data Validation Guidelines

### Product Update Validation
- **Product Existence**: Verify product exists and is accessible
- **Field Constraints**: Ensure data meets field requirements
- **Business Rules**: Validate against store policies
- **Permission Check**: Ensure proper access for updates

### Bundle Update Validation
- **Component Availability**: Verify component products exist
- **Pricing Logic**: Ensure bundle pricing makes business sense
- **Inventory Check**: Consider component product availability
- **Circular References**: Avoid bundles containing themselves

### Option Update Validation
- **Option Uniqueness**: Ensure option names are unique within product
- **Value Consistency**: Maintain valid option values
- **Variant Impact**: Understand how changes affect variants
- **Display Order**: Consider customer experience for option ordering

## Error Handling

### Common Product Update Errors
- **Product Not Found**: Verify product ID or handle
- **Invalid Data**: Check field formats and constraints
- **Permission Denied**: Ensure proper API access
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Bundle Update Errors
- **Invalid Components**: Component products must exist
- **Pricing Conflicts**: Bundle pricing must be logical
- **Inventory Issues**: Consider component availability
- **Circular Dependencies**: Avoid invalid bundle structures

### Option Update Errors
- **Invalid Option Names**: Option names must be valid
- **Value Conflicts**: Option values must be consistent
- **Variant Synchronization**: Handle variant update conflicts
- **Display Order Issues**: Validate option positioning

### Price Update Errors
- **Invalid Currency**: Currency codes must be supported
- **Negative Prices**: Prices must be positive numbers
- **Permission Issues**: Verify price update access
- **Market Conflicts**: Ensure market-specific pricing is valid

## Best Practices

### Before Updating Products
1. **Backup Data**: Preserve current product information
2. **Test Changes**: Validate updates in development environment
3. **Plan Impact**: Understand how changes affect other systems
4. **Communicate Changes**: Inform relevant team members
5. **Schedule Updates**: Choose optimal timing for changes

### During Product Updates
1. **Use Transactions**: Group related changes together
2. **Validate Input**: Check data before sending mutations
3. **Monitor Performance**: Watch for system impact
4. **Handle Errors**: Implement proper error handling
5. **Log Changes**: Maintain audit trail of updates

### After Product Updates
1. **Verify Changes**: Confirm updates were applied correctly
2. **Check Dependencies**: Ensure related systems updated properly
3. **Monitor Impact**: Watch for unexpected consequences
4. **Update Documentation**: Keep product information current
5. **Gather Feedback**: Collect feedback from stakeholders

## Performance Optimization

### Update Efficiency
- **Batch Changes**: Group related updates together
- **Minimize Data**: Send only changed fields
- **Use Caching**: Cache frequently accessed product data
- **Optimize Images**: Compress and optimize product images

### System Performance
- **Monitor Load**: Watch system resource usage
- **Schedule Updates**: Perform updates during low-traffic periods
- **Use Queues**: Queue large update operations
- **Monitor Errors**: Track and resolve update errors quickly

### User Experience
- **Maintain Availability**: Minimize downtime during updates
- **Provide Feedback**: Keep users informed of changes
- **Test Thoroughly**: Ensure updates don't break functionality
- **Rollback Plans**: Prepare for quick rollback if needed

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
