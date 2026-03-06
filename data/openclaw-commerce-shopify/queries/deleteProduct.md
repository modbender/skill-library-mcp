# Shopify Product & Options Deletion

This guide helps you generate accurate GraphQL mutations for deleting products and managing product data removal in Shopify.

## Instructions for Mutation Generation

When a user requests to delete products or manage product data removal, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific product deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Primary Product Delete Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete

**What to learn from this documentation:**
- Required input fields for product deletion
- Product eligibility requirements for deletion
- Order history and data retention implications
- Product deletion workflows and consequences
- Legal and compliance considerations

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

### Product Options Delete Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete

**What to learn from this documentation:**
- Product option deletion workflows
- Variant impact and management
- Product structure changes
- Option deletion consequences

### Price List Delete Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListDelete

**What to learn from this documentation:**
- Price list deletion workflows
- Pricing data management
- Currency-specific pricing removal
- Price list deletion consequences

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting products.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Product Delete Cost Calculation**:
   - Product deletion mutations have moderate costs
   - Complex products with many variants may have higher costs
   - Option deletions affect variant structures
   - Formula: `cost = base_mutation_cost + product_complexity + variant_count`

3. **Best Practices for Product Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure product is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest archiving instead of deletion when appropriate
   - **Warn about consequences**: Clearly explain irreversible nature of deletion

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes product with excessive return fields
   mutation productDelete($input: ProductDeleteInput!) {
     productDelete(input: $input) {
       deletedProductId
       product { id title variants { ... } orders { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes product with essential fields only
   mutation productDelete($input: ProductDeleteInput!) {
     productDelete(input: $input) {
       deletedProductId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating product delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$PRODUCT_ID$` | Product ID to delete | Ask user if not provided | `gid://shopify/Product/123456789` |
| `$OPTION_ID$` | Option ID to delete | Ask user if not provided | `gid://shopify/ProductOption/987654321` |
| `$PRICE_LIST_ID$` | Price list ID to delete | Ask user if not provided | `gid://shopify/PriceList/456789123` |
| `$DELETE_REASON$` | Reason for deletion | `"DATA_CLEANUP"` | `"SEASONAL_REMOVAL"` |

### Mutation Structure Templates

#### Product Delete Template
```graphql
mutation productDelete($input: ProductDeleteInput!) {
  productDelete(input: $input) {
    deletedProductId
    userErrors {
      field
      message
    }
  }
}
```

#### Product Options Delete Template
```graphql
mutation productOptionsDelete($productId: ID!, $optionIds: [ID!]!) {
  productOptionsDelete(productId: $productId, optionIds: $optionIds) {
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

#### Price List Delete Template
```graphql
mutation priceListDelete($input: PriceListDeleteInput!) {
  priceListDelete(input: $input) {
    deletedPriceListId
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a product delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the product from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all product data will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the product ID or title")
4. **Explain any limitations** in simple terms (e.g., "Only certain products can be deleted - others must be archived")
5. **Suggest alternatives** when appropriate (e.g., "Consider archiving instead of deleting to preserve order history")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete a product from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the product and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation productDelete($input: ProductDeleteInput!) {
  productDelete(input: $input) {
    deletedProductId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes a product from your Shopify store.

**What I need from you:**
- The product ID or title you want to delete

**Important consequences:**
- All product data will be permanently erased
- Order history may be affected or anonymized
- Customer reviews and ratings will be lost
- Product URLs will become invalid
- This action cannot be reversed

**Alternatives to consider:**
- Archive the product to preserve order history
- Unpublish the product to hide it from customers
- Set inventory to 0 to prevent sales

**Are you sure you want to proceed with permanent deletion?**
```

## Common Product Deletion Scenarios

### Product Account Deletion
- **Use**: `productDelete` mutation
- **Eligibility**: Only certain products can be deleted (typically those without active orders)
- **Considerations**: Order history preservation, legal requirements, customer communication

### Product Options Removal
- **Use**: `productOptionsDelete` mutation
- **Eligibility**: Options can be deleted if variants can be restructured
- **Considerations**: Variant impact, customer experience, inventory management

### Price List Removal
- **Use**: `priceListDelete` mutation
- **Eligibility**: Price lists can be deleted if not in use
- **Considerations**: Pricing strategy, market impact, customer pricing

### Data Cleanup Operations
- **Use**: Product deletion mutations
- **Use case**: Removing test data, duplicate products, outdated information
- **Considerations**: Data integrity, compliance requirements, backup needs

### Seasonal Product Removal
- **Use**: Product deletion or archiving
- **Use case**: End-of-season cleanup, discontinued products
- **Considerations**: Customer expectations, inventory management, future re-listing

## Deletion Limitations

### Product Deletion Restrictions
- **Active orders**: Products with recent or active orders may not be deletable
- **Payment processing**: Products with pending payments may be protected
- **Legal requirements**: Some jurisdictions require data retention for specific periods
- **Store policies**: Individual stores may have additional deletion restrictions

### Options Deletion Restrictions
- **Variant dependencies**: Options cannot be deleted if variants depend on them
- **Active orders**: Options used in order processing may be protected
- **Inventory tracking**: Options with inventory may have restrictions
- **Customer orders**: Historical orders may reference specific options

### Price List Deletion Restrictions
- **Active usage**: Price lists in use cannot be deleted
- **Market dependencies**: Price lists assigned to markets may be protected
- **Customer pricing**: Active customer pricing may depend on price lists
- **Legal compliance**: Some pricing data must be retained for compliance

## Safety Precautions

### Before Deleting Products
1. **Verify product eligibility** - not all products can be deleted
2. **Check legal requirements** - ensure compliance with data retention laws
3. **Consider business impact** - understand how deletion affects analytics and reporting
4. **Backup critical data** - preserve information needed for business operations
5. **Communicate with customers** - inform about product discontinuation if applicable

### Before Deleting Options
1. **Verify option dependencies** - ensure no variants depend on the option
2. **Check inventory impact** - understand how option deletion affects inventory
3. **Consider customer experience** - plan for customer communication
4. **Update product information** - ensure product data remains consistent
5. **Test variant structure** - verify variants work correctly after deletion

### Before Deleting Price Lists
1. **Verify price list usage** - ensure price list is not in active use
2. **Check market dependencies** - ensure no markets depend on the price list
3. **Consider pricing strategy** - plan for alternative pricing approaches
4. **Update customer pricing** - ensure customer pricing remains consistent
5. **Document changes** - maintain records of pricing changes

### After Deletion Operations
1. **Verify deletion success** - confirm product or option was removed
2. **Check related data** - ensure orders, inventory, and other records are handled properly
3. **Update integrations** - sync changes with other systems if needed
4. **Document actions** - maintain audit trail for compliance and business purposes
5. **Monitor for issues** - watch for unexpected consequences or system errors

## Error Handling

### Common Product Delete Errors
- **Product not found**: Verify product ID or handle
- **Product not eligible**: Check order status, payment processing, or legal restrictions
- **Permission denied**: Verify API access and product ownership
- **Legal compliance**: Check data retention requirements for your jurisdiction

### Common Option Delete Errors
- **Option not found**: Verify option ID belongs to product
- **Variant dependency**: Options used by variants cannot be deleted
- **Inventory conflict**: Options with inventory may be protected
- **Permission denied**: Verify API access and option ownership

### Common Price List Delete Errors
- **Price list not found**: Verify price list ID
- **Active usage**: Price list in use cannot be deleted
- **Market dependency**: Markets using price list cannot be deleted
- **Permission denied**: Verify API access and price list ownership

### Best Practices for Error Resolution
1. **Provide clear explanations** - explain what went wrong in business terms
2. **Offer alternatives** - suggest archiving, updating, or other solutions
3. **Guide next steps** - provide clear instructions for resolution
4. **Maintain professionalism** - handle errors calmly and helpfully
5. **Document issues** - track recurring problems for system improvements

## Best Practices

### Product Deletion Best Practices
1. **Use archiving when possible** - preserve order history and customer data
2. **Verify eligibility before deletion** - ensure product can be legally deleted
3. **Communicate with stakeholders** - inform relevant team members and customers
4. **Document deletion reasons** - maintain records for compliance and analysis
5. **Plan for consequences** - understand impact on analytics, reporting, and operations

### Options Management Best Practices
1. **Plan option structure carefully** - minimize need for option deletion
2. **Test option changes** - validate impact on variants and inventory
3. **Communicate changes** - inform team members of option modifications
4. **Monitor variant performance** - ensure variants work correctly after changes
5. **Maintain consistency** - keep product structure logical and organized

### Price List Management Best Practices
1. **Plan pricing strategy** - minimize frequent price list changes
2. **Test pricing changes** - validate impact on markets and customers
3. **Document pricing decisions** - maintain records of pricing strategy
4. **Monitor pricing performance** - track effectiveness of pricing changes
5. **Consider alternatives** - use price adjustments instead of deletion when possible

## Compliance Considerations

### Data Retention Requirements
- **Tax compliance**: Some jurisdictions require product data retention for tax purposes
- **Consumer protection**: Product information may need to be retained for warranty claims
- **Financial regulations**: Transaction data may require product information preservation
- **Industry standards**: Specific industries may have additional retention requirements

### Customer Data Protection
- **Order history**: Customer order data may need to be preserved
- **Warranty information**: Product warranty data may have legal retention requirements
- **Safety regulations**: Product safety information may need to be maintained
- **Consumer rights**: Product information may be required for consumer protection

### Business Continuity
- **Analytics data**: Historical product data may be needed for business analysis
- **Inventory records**: Product information may be needed for inventory management
- **Supplier relationships**: Product data may be important for supplier management
- **Future re-listing**: Product information may be useful for future product offerings

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
