# Shopify Collection & Product Removal

This guide helps you generate accurate GraphQL mutations for deleting collections and removing products from collections in Shopify.

## Instructions for Mutation Generation

When a user requests to delete collections or remove products from collections, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific collection deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Primary Collection Delete Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDelete

**What to learn from this documentation:**
- Required input fields for collection deletion
- Collection eligibility requirements for deletion
- Product and navigation implications
- Collection deletion workflows and consequences
- SEO and customer experience impact

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

### Collection Product Removal Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionRemoveProducts

**What to learn from this documentation:**
- Product removal from collection workflows
- Bulk product removal operations
- Collection-product relationship management
- Performance considerations for large removals

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting collections.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Collection Delete Cost Calculation**:
   - Collection deletion mutations have moderate costs
   - Collections with many products may have higher costs
   - Product removal operations can be expensive for large collections
   - Formula: `cost = base_mutation_cost + collection_complexity + product_count`

3. **Best Practices for Collection Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure collection is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest archiving instead of deletion when appropriate
   - **Warn about consequences**: Clearly explain irreversible nature of deletion

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes collection with excessive return fields
   mutation collectionDelete($input: CollectionDeleteInput!) {
     collectionDelete(input: $input) {
       deletedCollectionId
       collection { id title products { ... } rules { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes collection with essential fields only
   mutation collectionDelete($input: CollectionDeleteInput!) {
     collectionDelete(input: $input) {
       deletedCollectionId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating collection delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$COLLECTION_ID$` | Collection ID to delete | Ask user if not provided | `gid://shopify/Collection/123456789` |
| `$PRODUCT_IDS$` | Product IDs to remove | Ask user if not provided | `[gid://shopify/Product/987654321]` |
| `$DELETE_REASON$` | Reason for deletion | `"COLLECTION_CLEANUP"` | `"SEASONAL_REMOVAL"` |

### Mutation Structure Templates

#### Collection Delete Template
```graphql
mutation collectionDelete($input: CollectionDeleteInput!) {
  collectionDelete(input: $input) {
    deletedCollectionId
    userErrors {
      field
      message
    }
  }
}
```

#### Remove Products from Collection Template
```graphql
mutation collectionRemoveProducts($collectionId: ID!, $productIds: [ID!]!) {
  collectionRemoveProducts(collectionId: $collectionId, productIds: $productIds) {
    collection {
      id
      title
      handle
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

## Response Guidelines

When generating a collection delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the collection from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all collection data will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the collection ID or title")
4. **Explain any limitations** in simple terms (e.g., "Only certain collections can be deleted - others must be archived")
5. **Suggest alternatives** when appropriate (e.g., "Consider archiving instead of deleting to preserve SEO value")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete a collection from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the collection and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation collectionDelete($input: CollectionDeleteInput!) {
  collectionDelete(input: $input) {
    deletedCollectionId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes a collection from your Shopify store.

**What I need from you:**
- The collection ID or title you want to delete

**Important consequences:**
- All collection configuration will be permanently erased
- SEO value and search rankings will be lost
- Navigation links will become invalid
- Customer bookmarks will break
- Products will need to be reorganized
- This action cannot be reversed

**Alternatives to consider:**
- Archive the collection to preserve SEO value
- Remove products instead of deleting the collection
- Unpublish the collection to hide it temporarily
- Reorganize products into other collections

**Are you sure you want to proceed with permanent deletion?**
```

## Common Collection Deletion Scenarios

### Collection Removal
- **Use**: `collectionDelete` mutation
- **Eligibility**: Most collections can be deleted unless they have specific restrictions
- **Considerations**: SEO impact, navigation structure, customer experience

### Seasonal Collection Cleanup
- **Use**: Collection deletion or archiving
- **Use case**: End-of-season cleanup, discontinued seasonal collections
- **Considerations**: SEO preservation, customer expectations, future re-listing

### Product Reorganization
- **Use**: `collectionRemoveProducts` mutation
- **Use case**: Removing products from collections, reorganizing product structure
- **Considerations**: Product visibility, customer experience, collection relevance

### Store Restructuring
- **Use**: Collection deletion and reorganization
- **Use case**: Major store reorganization, navigation changes
- **Considerations**: SEO impact, customer experience, navigation consistency

### Collection Duplicate Cleanup
- **Use**: Collection deletion for duplicates
- **Use case**: Removing duplicate or test collections
- **Considerations**: Data consistency, SEO impact, navigation cleanup

## Product Removal from Collections

### Bulk Product Removal
- **Use**: `collectionRemoveProducts` mutation with multiple product IDs
- **Use case**: Removing multiple products from collection
- **Considerations**: Performance impact, collection relevance, customer experience

### Selective Product Removal
- **Use**: `collectionRemoveProducts` mutation with specific product IDs
- **Use case**: Removing specific products while keeping collection
- **Considerations**: Collection completeness, customer expectations, SEO impact

### Collection Refresh
- **Use**: Product removal followed by adding new products
- **Use case**: Refreshing collection content, seasonal updates
- **Considerations**: Collection continuity, customer experience, SEO maintenance

## Deletion Limitations

### Collection Deletion Restrictions
- **Active promotions**: Collections with active promotions may be protected
- **Navigation dependencies**: Collections used in navigation may have restrictions
- **SEO considerations**: Important collections may have SEO value considerations
- **Customer expectations**: Frequently accessed collections may have usage restrictions

### Product Removal Restrictions
- **Product existence**: Products must exist in collection to be removed
- **Permission issues**: Verify access to both collection and products
- **Concurrent updates**: Handle conflicts with simultaneous collection changes
- **Smart collection rules**: Products in smart collections may be automatically re-added

### Publication Restrictions
- **Active publications**: Collections used by active publications may be protected
- **Sales channel dependencies**: Collections supporting sales channels may have restrictions
- **Customer access**: Collections accessible to customers may have usage limitations
- **Marketing campaigns**: Collections used in marketing may have temporary restrictions

## Safety Precautions

### Before Deleting Collections
1. **Verify collection importance** - assess SEO value and customer usage
2. **Check navigation dependencies** - ensure navigation won't break
3. **Consider SEO impact** - plan for SEO value preservation
4. **Backup collection data** - preserve important collection information
5. **Communicate with stakeholders** - inform relevant team members

### Before Removing Products from Collections
1. **Verify product collection membership** - ensure products are in the collection
2. **Consider customer experience** - plan for customer communication
3. **Check collection relevance** - ensure collection remains useful after removal
4. **Monitor performance** - watch for performance impact of large removals
5. **Document changes** - maintain records of collection modifications

### Before Major Collection Restructuring
1. **Plan new structure** - design new collection organization
2. **Test changes** - validate in development environment
3. **Preserve SEO value** - plan redirects or preservation strategies
4. **Update navigation** - prepare navigation menu updates
5. **Communicate changes** - inform customers of organizational changes

### After Deletion Operations
1. **Verify deletion success** - confirm collection or products were removed
2. **Check navigation** - ensure navigation menus updated properly
3. **Monitor SEO** - watch for SEO impact and rankings changes
4. **Update integrations** - sync changes with other systems if needed
5. **Analyze customer impact** - assess changes in customer behavior

## Error Handling

### Common Collection Delete Errors
- **Collection not found**: Verify collection ID or handle
- **Permission denied**: Verify API access and collection ownership
- **Concurrent updates**: Handle conflicts with simultaneous changes
- **Navigation dependencies**: Collection may be in use by navigation systems

### Common Product Removal Errors
- **Product not in collection**: Verify product is actually in the collection
- **Permission denied**: Verify access to both collection and products
- **Smart collection rules**: Products may be automatically re-added by rules
- **Collection locked**: Collection may be temporarily locked for updates

### Best Practices for Error Resolution
1. **Provide clear explanations** - explain what went wrong in business terms
2. **Offer alternatives** - suggest different approaches or solutions
3. **Guide next steps** - provide clear instructions for resolution
4. **Maintain professionalism** - handle errors calmly and helpfully
5. **Document issues** - track recurring problems for system improvements

## Best Practices

### Collection Deletion Best Practices
1. **Use archiving for SEO value** - preserve SEO value when possible
2. **Plan redirects** - implement redirects for important collections
3. **Communicate changes** - keep customers informed of collection changes
4. **Monitor SEO impact** - track search rankings after deletion
5. **Document deletion reasons** - maintain records for analysis

### Product Removal Best Practices
1. **Batch removal operations** - remove products in reasonable batches
2. **Monitor collection relevance** - ensure collections remain useful
3. **Consider customer experience** - minimize disruption to shopping experience
4. **Test removal impact** - validate changes in development environment
5. **Maintain collection quality** - keep collections focused and relevant

### Collection Organization Best Practices
1. **Plan collection hierarchy** - design logical collection structure
2. **Maintain consistency** - keep collection organization consistent
3. **Monitor collection performance** - track collection effectiveness
4. **Regular cleanup** - periodically review and clean up collections
5. **Customer-focused organization** - organize collections for customer benefit

## SEO Considerations

### Collection Deletion SEO Impact
- **URL value loss**: Collection URLs and their SEO value will be lost
- **Internal links**: Internal links to collection will break
- **External backlinks**: External backlinks will become invalid
- **Search rankings**: Collection search rankings will be lost
- **Customer bookmarks**: Customer bookmarks will no longer work

### SEO Preservation Strategies
- **Implement redirects**: Redirect old collection URLs to relevant new collections
- **Update internal links**: Update all internal links to collections
- **Communicate externally**: Inform external sites of URL changes
- **Monitor rankings**: Track search ranking changes after deletion
- **Preserve content**: Move valuable content to new collections when possible

### Collection Content Migration
- **Content preservation**: Move valuable content to new collections
- **Meta information**: Transfer SEO titles and descriptions when appropriate
- **Image optimization**: Ensure collection images are optimized for new collections
- **Customer experience**: Maintain consistent customer experience during migration
- **Analytics tracking**: Track performance of migrated content

## Alternative Strategies

### Collection Archiving
- **Preserve SEO value**: Maintain collection SEO value and rankings
- **Enable reactivation**: Allow collection to be reactivated if needed
- **Reduce active management**: Hide collection without permanent deletion
- **Maintain data integrity**: Preserve all collection data and configuration

### Collection Unpublishing
- **Temporary hiding**: Hide collection from customers temporarily
- **Maintain configuration**: Preserve all collection settings and rules
- **Quick reactivation**: Enable fast collection reactivation
- **Minimal disruption**: Reduce impact on store operations

### Collection Merging
- **Combine similar collections**: Merge related collections to reduce complexity
- **Preserve SEO value**: Consolidate SEO value into stronger collection
- **Improve organization**: Create more focused and useful collections
- **Reduce maintenance**: Decrease collection management overhead

### Product Reorganization
- **Strategic product placement**: Move products to more appropriate collections
- **Improve collection relevance**: Make collections more focused and useful
- **Enhance customer experience**: Improve product discovery and navigation
- **Maintain SEO consistency**: Preserve product SEO value during reorganization

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
