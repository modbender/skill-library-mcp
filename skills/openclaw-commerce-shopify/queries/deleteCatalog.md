# Shopify Catalog Deletion

This guide helps you generate accurate GraphQL mutations for deleting catalogs and managing catalog data removal in Shopify.

## Instructions for Mutation Generation

When a user requests to delete catalogs or manage catalog data removal, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific catalog deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Primary Catalog Delete Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogDelete

**What to learn from this documentation:**
- Required input fields for catalog deletion
- Catalog eligibility requirements for deletion
- Product and collection data implications
- Catalog deletion workflows and consequences
- Multi-storefront impact considerations

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting catalogs.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Catalog Delete Cost Calculation**:
   - Catalog deletion mutations have moderate costs
   - Complex catalogs with many products may have higher costs
   - Publication and market settings add complexity
   - Formula: `cost = base_mutation_cost + catalog_complexity + product_count`

3. **Best Practices for Catalog Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure catalog is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest archiving instead of deletion when appropriate
   - **Warn about consequences**: Clearly explain irreversible nature of deletion

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes catalog with excessive return fields
   mutation catalogDelete($input: CatalogDeleteInput!) {
     catalogDelete(input: $input) {
       deletedCatalogId
       catalog { id name products { ... } collections { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes catalog with essential fields only
   mutation catalogDelete($input: CatalogDeleteInput!) {
     catalogDelete(input: $input) {
       deletedCatalogId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating catalog delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CATALOG_ID$` | Catalog ID to delete | Ask user if not provided | `gid://shopify/Catalog/123456789` |
| `$DELETE_REASON$` | Reason for deletion | `"CATALOG_CLEANUP"` | `"STORE_REORGANIZATION"` |

### Mutation Structure Templates

#### Catalog Delete Template
```graphql
mutation catalogDelete($input: CatalogDeleteInput!) {
  catalogDelete(input: $input) {
    deletedCatalogId
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a catalog delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the catalog from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all catalog data will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the catalog ID or name")
4. **Explain any limitations** in simple terms (e.g., "Only certain catalogs can be deleted - others must be archived")
5. **Suggest alternatives** when appropriate (e.g., "Consider archiving instead of deleting to preserve data")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete a catalog from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the catalog and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation catalogDelete($input: CatalogDeleteInput!) {
  catalogDelete(input: $input) {
    deletedCatalogId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes a catalog from your Shopify store.

**What I need from you:**
- The catalog ID or name you want to delete

**Important consequences:**
- All catalog configuration will be permanently erased
- Products and collections may be affected
- Publication settings will be lost
- Market configurations may be impacted
- This action cannot be reversed

**Alternatives to consider:**
- Archive the catalog to preserve configuration
- Deactivate the catalog to hide it temporarily
- Reorganize products instead of deleting the catalog

**Are you sure you want to proceed with permanent deletion?**
```

## Common Catalog Deletion Scenarios

### Catalog Removal
- **Use**: `catalogDelete` mutation
- **Eligibility**: Only certain catalogs can be deleted (typically those without active dependencies)
- **Considerations**: Product organization, publication settings, market configuration

### Store Reorganization
- **Use**: Catalog deletion or archiving
- **Use case**: Restructuring store organization, consolidating catalogs
- **Considerations**: Product migration, customer experience, SEO impact

### Multi-Storefront Cleanup
- **Use**: Catalog deletion for unused storefronts
- **Use case**: Removing unnecessary catalogs, cleaning up multi-storefront setup
- **Considerations**: Cross-catalog consistency, customer access, marketing impact

### Market-Specific Catalog Removal
- **Use**: Catalog deletion for discontinued markets
- **Use case**: Exiting specific markets, discontinuing regional catalogs
- **Considerations**: Market regulations, customer communication, legal requirements

### Development Catalog Cleanup
- **Use**: Catalog deletion for test catalogs
- **Use case**: Removing development or test catalogs
- **Considerations**: Data isolation, production safety, team coordination

## Deletion Limitations

### Catalog Deletion Restrictions
- **Active dependencies**: Catalogs with active products or collections may be protected
- **Publication usage**: Catalogs in use by publications may not be deletable
- **Market dependencies**: Catalogs assigned to markets may have restrictions
- **Legal requirements**: Some jurisdictions require data retention for specific periods

### Publication Restrictions
- **Active publications**: Catalogs used by active publications cannot be deleted
- **Sales channel dependencies**: Catalogs supporting sales channels may be protected
- **Customer access**: Catalogs accessible to customers may have usage restrictions
- **Integration dependencies**: Third-party integrations may prevent deletion

### Market Configuration Restrictions
- **Active markets**: Catalogs supporting active markets cannot be deleted
- **Currency dependencies**: Catalogs with currency configurations may be protected
- **Regional requirements**: Market-specific catalogs may have legal retention requirements
- **Customer expectations**: Market-specific customer expectations may prevent deletion

## Safety Precautions

### Before Deleting Catalogs
1. **Verify catalog eligibility** - not all catalogs can be deleted
2. **Check dependencies** - ensure no active dependencies exist
3. **Consider business impact** - understand how deletion affects operations
4. **Backup critical data** - preserve configuration and settings
5. **Communicate with stakeholders** - inform relevant team members and customers

### Before Deleting Multi-Storefront Catalogs
1. **Verify customer impact** - ensure customer access is not disrupted
2. **Check market requirements** - consider regional legal requirements
3. **Plan product migration** - ensure products have alternative homes
4. **Update integrations** - modify third-party system integrations
5. **Document changes** - maintain records of catalog reorganization

### Before Deleting Market-Specific Catalogs
1. **Verify market compliance** - ensure deletion complies with market regulations
2. **Check customer expectations** - consider customer communication needs
3. **Plan market exit strategy** - ensure orderly market withdrawal
4. **Update pricing strategy** - adjust pricing for remaining markets
5. **Handle inventory** - manage inventory across remaining catalogs

### After Deletion Operations
1. **Verify deletion success** - confirm catalog was removed
2. **Check related systems** - ensure integrations updated properly
3. **Monitor customer impact** - watch for customer access issues
4. **Update documentation** - maintain current catalog documentation
5. **Analyze performance** - assess impact on store operations

## Error Handling

### Common Catalog Delete Errors
- **Catalog not found**: Verify catalog ID or name
- **Catalog not eligible**: Check dependencies, publications, or market usage
- **Permission denied**: Verify API access and catalog ownership
- **Legal compliance**: Check data retention requirements for your jurisdiction

### Dependency Resolution Errors
- **Active publications**: Catalogs in use cannot be deleted
- **Market assignments**: Catalogs assigned to markets may be protected
- **Product dependencies**: Products may depend on catalog configuration
- **Integration conflicts**: Third-party integrations may prevent deletion

### Best Practices for Error Resolution
1. **Provide clear explanations** - explain what went wrong in business terms
2. **Offer alternatives** - suggest archiving, deactivation, or reorganization
3. **Guide next steps** - provide clear instructions for resolution
4. **Maintain professionalism** - handle errors calmly and helpfully
5. **Document issues** - track recurring problems for system improvements

## Best Practices

### Catalog Deletion Best Practices
1. **Use archiving when possible** - preserve configuration and settings
2. **Verify dependencies before deletion** - ensure no active dependencies exist
3. **Plan catalog reorganization** - minimize need for catalog deletion
4. **Communicate with stakeholders** - inform relevant team members and customers
5. **Document deletion reasons** - maintain records for compliance and analysis

### Multi-Storefront Management Best Practices
1. **Plan catalog strategy** - minimize catalog creation and deletion
2. **Maintain catalog consistency** - ensure consistent organization across catalogs
3. **Monitor catalog performance** - track catalog effectiveness and usage
4. **Test catalog changes** - validate changes in development environment
5. **Consider customer impact** - prioritize customer experience in catalog management

### Market-Specific Catalog Best Practices
1. **Understand market requirements** - research regional legal requirements
2. **Plan market entry/exit** - develop strategies for market-specific catalogs
3. **Maintain market compliance** - ensure catalogs meet market regulations
4. **Communicate market changes** - keep customers informed of market changes
5. **Monitor market performance** - track catalog effectiveness by market

## Compliance Considerations

### Data Retention Requirements
- **Tax compliance**: Some jurisdictions require catalog data retention for tax purposes
- **Consumer protection**: Catalog information may need to be retained for consumer rights
- **Financial regulations**: Transaction data may require catalog information preservation
- **Industry standards**: Specific industries may have additional retention requirements

### Market-Specific Regulations
- **Regional laws**: Different markets may have different data retention requirements
- **Consumer rights**: Market-specific consumer protection laws may apply
- **Tax regulations**: Market-specific tax requirements may affect data retention
- **Business licenses**: Market-specific business licenses may have data requirements

### Business Continuity
- **Analytics data**: Historical catalog data may be needed for business analysis
- **Performance metrics**: Catalog performance data may be important for planning
- **Customer insights**: Catalog data may provide valuable customer insights
- **Future planning**: Historical catalog data may inform future catalog strategies

## Alternative Strategies

### Catalog Archiving
- **Preserve configuration**: Maintain catalog settings and structure
- **Enable reactivation**: Allow catalog to be reactivated if needed
- **Reduce storage impact**: Minimize active catalog overhead
- **Maintain data integrity**: Preserve historical catalog data

### Catalog Deactivation
- **Temporary hiding**: Hide catalog without permanent deletion
- **Maintain configuration**: Preserve all catalog settings
- **Enable reactivation**: Quickly reactivate catalog when needed
- **Minimize disruption**: Reduce impact on operations and customers

### Catalog Reorganization
- **Restructure hierarchy**: Reorganize catalog structure instead of deletion
- **Merge catalogs**: Combine similar catalogs to reduce complexity
- **Redistribute products**: Move products to alternative catalogs
- **Maintain continuity**: Preserve customer experience and access

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

### Product Migration Strategies
- **Gradual migration**: Move products gradually to minimize disruption
- **Bulk migration**: Transfer products in bulk for efficiency
- **Selective migration**: Move only relevant products to new catalogs
- **Maintain SEO**: Preserve SEO value during migration process
