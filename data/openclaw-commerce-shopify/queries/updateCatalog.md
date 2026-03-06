# Shopify Catalog Update & Management

This guide helps you generate accurate GraphQL mutations for updating catalogs and managing catalog data in Shopify.

## Instructions for Mutation Generation

When a user requests to update catalogs or manage catalog data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific catalog update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider catalog organization impact** - understand how updates affect products and collections

## Official Documentation

### Primary Catalog Update Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogUpdate

**What to learn from this documentation:**
- Required input fields for catalog updates
- Catalog data modification options
- Publication and channel management updates
- Catalog settings and configuration changes
- Multi-storefront catalog management

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogUpdate#examples
  - *Review only when you need sample mutation patterns for catalog update scenarios*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating catalogs.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Catalog Update Cost Calculation**:
   - Catalog update mutations have moderate costs
   - Complex catalog configuration changes increase cost
   - Publication updates add additional complexity
   - Formula: `cost = base_mutation_cost + catalog_complexity + publication_changes`

3. **Best Practices for Catalog Update Mutation Generation**:
   - **Include only changed fields**: Don't send unchanged catalog data
   - **Validate updates**: Ensure data integrity before mutation
   - **Plan publication changes**: Understand channel impact
   - **Use proper error handling**: Always check for user errors in mutation response
   - **Consider dependencies**: Understand how updates affect products and collections

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates catalog with excessive fields
   mutation catalogUpdate($input: CatalogInput!) {
     catalogUpdate(input: $input) {
       catalog { id name settings { ... } publication { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates catalog with only changed fields
   mutation catalogUpdate($input: CatalogInput!) {
     catalogUpdate(input: $input) {
       catalog {
         id
         name
         description
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

When generating catalog update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CATALOG_ID$` | Catalog ID to update | Ask user if not provided | `gid://shopify/Catalog/123456789` |
| `$CATALOG_NAME$` | Updated catalog name | Ask user if not provided | `"Updated Main Catalog"` |
| `$CATALOG_DESCRIPTION$` | Updated catalog description | Ask user if not provided | `"Updated description for main catalog"` |
| `$STATUS$` | Updated catalog status | `"ACTIVE"` | `"DRAFT"` |
| `$PUBLICATION_ID$` | Updated publication ID | Ask user if not provided | `gid://shopify/Publication/987654321` |
| `$CURRENCY_CODE$` | Updated currency code | `"USD"` | `"EUR"` |
| `$MARKET_ID$` | Updated market ID | Ask user if not provided | `gid://shopify/Market/456789123` |

### Mutation Structure Templates

#### Basic Catalog Update Template
```graphql
mutation catalogUpdate($input: CatalogInput!) {
  catalogUpdate(input: $input) {
    catalog {
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
        currencyCode
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Catalog Publication Update Template
```graphql
mutation catalogUpdate($input: CatalogInput!) {
  catalogUpdate(input: $input) {
    catalog {
      id
      name
      description
      status
      settings {
        publication {
          id
          name
        }
        currencyCode
      }
      productCount
      collectionCount
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Catalog Status Update Template
```graphql
mutation catalogUpdate($input: CatalogInput!) {
  catalogUpdate(input: $input) {
    catalog {
      id
      name
      description
      status
      updatedAt
      productCount
      collectionCount
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a catalog update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the catalog settings in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the catalog ID and what settings you want to change")
3. **Explain any limitations** in simple terms (e.g., "This will update the catalog but may affect product visibility")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update an existing catalog in your store.

**Mutation:**
```graphql
mutation catalogUpdate($input: CatalogInput!) {
  catalogUpdate(input: $input) {
    catalog {
      id
      name
      description
      status
      updatedAt
      productCount
      collectionCount
    }
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This updates an existing catalog's settings in your Shopify store.

**What I need from you:**
- The catalog ID or name you want to update
- What specific settings you want to change (name, description, status, etc.)
- Any publication or market changes you want to make

**Important notes:**
- Changes will affect how the catalog displays products
- Publication changes may impact storefront visibility
- Status changes will affect catalog accessibility

Would you like me to help you update a specific catalog?
```

## Common Catalog Update Scenarios

### Basic Catalog Information Updates
- **Use**: `catalogUpdate` mutation
- **Fields**: Name, description, status
- **Considerations**: SEO impact, catalog organization, user experience

### Catalog Publication Management
- **Use**: `catalogUpdate` with publication settings
- **Use case**: Changing sales channels, updating storefronts
- **Considerations**: Channel availability, customer access, marketing impact

### Catalog Status Changes
- **Use**: `catalogUpdate` mutation
- **Use case**: Activating/deactivating catalogs, seasonal management
- **Considerations**: Product visibility, order processing, customer experience

### Currency and Market Updates
- **Use**: `catalogUpdate` with currency settings
- **Use case**: International expansion, currency changes
- **Considerations**: Currency conversion, market regulations, pricing strategy

## Catalog Update Impact Analysis

### Product Visibility Impact
- **Publication Changes**: May affect product visibility across channels
- **Status Updates**: Can hide or show entire product catalogs
- **Market Changes**: May limit product availability to specific regions
- **Currency Updates**: Can affect pricing display and payment processing

### Collection Organization Impact
- **Catalog Structure Changes**: May affect collection hierarchy
- **Publication Updates**: Can change collection visibility
- **Market Configuration**: May impact collection availability by region

### Customer Experience Impact
- **Catalog Availability**: Status changes affect customer access
- **Publication Settings**: Determine where customers can shop
- **Currency Display**: Affects pricing presentation and payment options

### Order Processing Impact
- **Catalog Status**: May affect order processing capabilities
- **Market Configuration**: Can impact shipping and tax calculations
- **Publication Settings**: May affect order routing and fulfillment

## Data Validation Guidelines

### Catalog Update Validation
- **Catalog Existence**: Verify catalog exists and is accessible
- **Field Constraints**: Ensure data meets field requirements
- **Business Rules**: Validate against store policies
- **Permission Check**: Ensure proper access for updates

### Publication Validation
- **Channel Access**: Verify publication permissions
- **Market Compatibility**: Ensure market supports catalog
- **Currency Support**: Verify currency availability
- **Configuration Consistency**: Ensure settings are compatible

### Status Update Validation
- **Transition Rules**: Validate status change permissions
- **Dependency Check**: Ensure no dependent processes are affected
- **Business Impact**: Consider operational consequences
- **User Access**: Verify user permissions for status changes

## Error Handling

### Common Catalog Update Errors
- **Catalog Not Found**: Verify catalog ID or name
- **Invalid Data**: Check field formats and constraints
- **Permission Denied**: Ensure proper API access
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Publication Update Errors
- **Invalid Publication**: Publication must exist and be accessible
- **Market Conflicts**: Market must support catalog operations
- **Currency Mismatch**: Currency not supported by market
- **Configuration Errors**: Publication settings must be valid

### Status Update Errors
- **Invalid Transitions**: Status changes must follow business rules
- **Dependency Conflicts**: Check for dependent processes
- **Permission Issues**: Verify status change permissions
- **Operational Impact**: Consider order processing implications

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest different configuration options
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Verify Prerequisites** - ensure all requirements are met
5. **Document Issues** - track recurring problems for system improvements

## Best Practices

### Before Updating Catalogs
1. **Backup Configuration**: Preserve current catalog settings
2. **Test Changes**: Validate updates in development environment
3. **Plan Impact**: Understand how changes affect products and customers
4. **Communicate Changes**: Inform relevant team members and stakeholders
5. **Schedule Updates**: Choose optimal timing for changes

### During Catalog Updates
1. **Use Transactions**: Group related changes together
2. **Validate Input**: Check data before sending mutations
3. **Monitor Performance**: Watch for system impact
4. **Handle Errors**: Implement proper error handling
5. **Log Changes**: Maintain audit trail of updates

### After Catalog Updates
1. **Verify Changes**: Confirm updates were applied correctly
2. **Check Dependencies**: Ensure related systems updated properly
3. **Monitor Impact**: Watch for unexpected consequences
4. **Update Documentation**: Keep catalog documentation current
5. **Gather Feedback**: Collect feedback from users and stakeholders

## Performance Optimization

### Update Efficiency
- **Batch Changes**: Group related updates together
- **Minimize Data**: Send only changed fields
- **Use Caching**: Cache frequently accessed catalog data
- **Optimize Queries**: Structure updates for maximum efficiency

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

## Integration Considerations

### Multi-Channel Impact
- **Online Store**: Update may affect main storefront
- **Point of Sale**: Consider physical retail implications
- **Marketplace**: Update third-party platform connections
- **Social Commerce**: Maintain social media storefront consistency

### API Integration
- **Product Synchronization**: Ensure products remain consistent
- **Inventory Management**: Coordinate inventory across catalogs
- **Order Processing**: Handle orders from updated catalogs
- **Customer Management**: Maintain customer data consistency

### Third-Party Systems
- **ERP Integration**: Update enterprise resource planning systems
- **CRM Integration**: Maintain customer relationship management data
- **Inventory Systems**: Coordinate with warehouse and stock management
- **Analytics Platforms**: Update performance tracking and reporting

## Catalog Management Strategies

### Proactive Management
- **Regular Reviews**: Schedule periodic catalog evaluations
- **Performance Monitoring**: Track catalog effectiveness metrics
- **User Feedback**: Collect feedback from store users and customers
- **Optimization**: Continuously improve catalog organization

### Reactive Management
- **Issue Resolution**: Quickly address catalog problems
- **Emergency Updates**: Handle urgent configuration changes
- **Rollback Procedures**: Prepare for quick reversal of problematic changes
- **Communication Plans**: Maintain clear communication during issues

### Strategic Planning
- **Growth Planning**: Plan catalog expansion and reorganization
- **Market Expansion**: Prepare catalogs for new markets or regions
- **Seasonal Planning**: Plan seasonal catalog changes
- **Technology Updates**: Plan for system upgrades and migrations

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
