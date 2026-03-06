# Shopify Catalog Creation

This guide helps you generate accurate GraphQL mutations for creating catalogs in Shopify.

## Instructions for Mutation Generation

When a user requests to create catalogs, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific catalog creation requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider catalog organization strategy** - plan for multi-storefront or market-specific catalogs

## Official Documentation

### Primary Catalog Creation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogCreate

**What to learn from this documentation:**
- Required input fields for catalog creation
- Catalog data structure and validation
- Publication and channel management
- Catalog settings and configuration
- Multi-storefront catalog strategies

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogCreate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogCreate#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogCreate#examples
  - *Review only when you need sample mutation patterns for catalog creation scenarios*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating catalogs.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Catalog Creation Cost Calculation**:
   - Catalog creation mutations have moderate costs
   - Complex catalog configurations increase cost
   - Publication setup adds additional complexity
   - Formula: `cost = base_mutation_cost + catalog_complexity + publication_settings`

3. **Best Practices for Catalog Creation Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate catalog data**: Ensure proper naming and configuration
   - **Plan publication strategy**: Configure channels and markets appropriately
   - **Use proper error handling**: Always check for user errors in mutation response
   - **Consider catalog hierarchy**: Plan for multi-catalog organization

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates catalog with excessive optional fields
   mutation catalogCreate($input: CatalogInput!) {
     catalogCreate(input: $input) {
       catalog { id name settings { ... } publication { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates catalog with essential fields only
   mutation catalogCreate($input: CatalogInput!) {
     catalogCreate(input: $input) {
       catalog {
         id
         name
         description
         status
         productCount
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

When generating catalog creation mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CATALOG_NAME$` | Catalog name | Ask user if not provided | `"Main Catalog"` |
| `$CATALOG_DESCRIPTION$` | Catalog description | Ask user if not provided | `"Primary product catalog for main store"` |
| `$PUBLICATION_ID$` | Publication ID | Ask user if not provided | `gid://shopify/Publication/123456789` |
| `$STATUS$` | Catalog status | `"ACTIVE"` | `"DRAFT"` |
| `$CURRENCY_CODE$` | Currency code | `"USD"` | `"EUR"` |
| `$MARKET_ID$` | Market ID | Ask user if not provided | `gid://shopify/Market/987654321` |

### Mutation Structure Templates

#### Basic Catalog Creation Template
```graphql
mutation catalogCreate($input: CatalogInput!) {
  catalogCreate(input: $input) {
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
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Catalog with Publication Template
```graphql
mutation catalogCreate($input: CatalogInput!) {
  catalogCreate(input: $input) {
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
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a catalog creation mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create a new catalog for your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the catalog name and what products it will contain")
3. **Explain any limitations** in simple terms (e.g., "This creates the catalog structure but doesn't automatically add products")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new catalog for your store.

**Mutation:**
```graphql
mutation catalogCreate($input: CatalogInput!) {
  catalogCreate(input: $input) {
    catalog {
      id
      name
      description
      status
      createdAt
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
This creates a new catalog in your Shopify store to organize your products.

**What I need from you:**
- Catalog name and description
- What type of catalog you're creating (main store, specific market, etc.)
- Whether this will be an active catalog or start as a draft

**Important notes:**
- The catalog will be created empty - you'll need to add products and collections
- You can configure publication settings after creation
- Consider your overall catalog strategy before creating multiple catalogs

Would you like me to help you create a specific catalog?
```

## Common Catalog Creation Scenarios

### Main Store Catalog
- **Use**: `catalogCreate` mutation with basic settings
- **Use case**: Primary catalog for main storefront
- **Considerations**: Product organization, publication settings

### Market-Specific Catalog
- **Use**: `catalogCreate` with market configuration
- **Use case**: Regional or country-specific catalogs
- **Considerations**: Currency, language, product selection

### B2B Catalog
- **Use**: `catalogCreate` with B2B publication settings
- **Use case**: Business-to-business storefront
- **Considerations**: Pricing tiers, customer groups, product selection

### Seasonal Catalog
- **Use**: `catalogCreate` with temporary settings
- **Use case**: Seasonal or promotional catalogs
- **Considerations**: Timing, product selection, publication schedule

### Development Catalog
- **Use**: `catalogCreate` with draft status
- **Use case**: Testing and development purposes
- **Considerations**: Isolation from production, data management

## Catalog Organization Strategies

### Multi-Storefront Strategy
- **Approach**: Separate catalogs for different storefronts
- **Benefits**: Independent product management, targeted offerings
- **Considerations**: Cross-catalog consistency, management overhead

### Market-Based Strategy
- **Approach**: Catalogs organized by geographic markets
- **Benefits**: Localized offerings, currency support
- **Considerations**: Market regulations, shipping logistics

### Customer Segment Strategy
- **Approach**: Catalogs for different customer types
- **Benefits**: Targeted product selection, pricing strategies
- **Considerations**: Access control, customer management

### Seasonal Strategy
- **Approach**: Time-based catalog organization
- **Benefits**: Fresh content, seasonal promotions
- **Considerations**: Timing coordination, inventory planning

## Catalog Configuration Options

### Publication Settings
- **Online Store**: Main e-commerce storefront
- **Point of Sale**: Physical retail locations
- **Buy Button**: Embeddable purchase options
- **Mobile App**: Custom mobile applications

### Currency Configuration
- **Single Currency**: Standard for most stores
- **Multi-Currency**: International stores
- **Market-Specific**: Currency by market or region

### Market Integration
- **Domestic Markets**: Local customer base
- **International Markets**: Global expansion
- **Custom Markets**: Specialized customer segments

## Data Validation Guidelines

### Required Catalog Fields
- **Name**: Must be descriptive and unique
- **Status**: Draft for testing, Active for production
- **Publication**: Must be valid and accessible

### Optional Configuration
- **Description**: Helpful for catalog identification
- **Currency**: Must match supported currencies
- **Market**: Must be valid and configured

### Publication Validation
- **Channel Access**: Verify publication permissions
- **Market Compatibility**: Ensure market supports catalog
- **Currency Support**: Verify currency availability

## Error Handling

### Common Catalog Creation Errors
- **Duplicate Name**: Catalog names must be unique
- **Invalid Publication**: Publication must exist and be accessible
- **Market Configuration**: Market must support catalog operations
- **Permission Issues**: Verify API access and permissions

### Configuration Errors
- **Currency Mismatch**: Currency not supported by market
- **Publication Conflicts**: Publication already assigned to catalog
- **Market Access**: Market not accessible or configured
- **Status Validation**: Invalid catalog status

### Best Practices for Error Resolution
1. **Provide clear explanations** - explain what went wrong in business terms
2. **Offer alternatives** - suggest different configuration options
3. **Guide next steps** - provide clear instructions for resolution
4. **Verify prerequisites** - ensure all requirements are met
5. **Document issues** - track recurring problems for system improvements

## Best Practices

### Before Creating Catalogs
1. **Plan catalog strategy** - define purpose and scope
2. **Verify prerequisites** - ensure publications and markets are ready
3. **Prepare catalog data** - gather names, descriptions, and settings
4. **Test configuration** - validate settings in development
5. **Document structure** - maintain catalog organization documentation

### After Creating Catalogs
1. **Verify catalog setup** - confirm all settings are correct
2. **Add products and collections** - populate catalog with content
3. **Configure publication** - set up storefront integration
4. **Test functionality** - verify catalog works as expected
5. **Monitor performance** - track catalog usage and effectiveness

### Ongoing Catalog Management
1. **Regular updates** - keep catalog content current
2. **Performance monitoring** - track catalog effectiveness
3. **User feedback** - gather feedback from store users
4. **Optimization** - improve catalog organization and performance
5. **Documentation maintenance** - keep catalog documentation updated

## Integration Considerations

### Multi-Channel Integration
- **Online Store**: Primary e-commerce channel
- **Point of Sale**: Physical retail integration
- **Marketplace**: Third-party platform connections
- **Social Commerce**: Social media storefronts

### API Integration
- **Product Synchronization**: Keep products consistent across catalogs
- **Inventory Management**: Coordinate inventory across catalogs
- **Order Processing**: Handle orders from multiple catalogs
- **Customer Management**: Maintain customer data consistency

### Third-Party Systems
- **ERP Integration**: Enterprise resource planning
- **CRM Integration**: Customer relationship management
- **Inventory Systems**: Warehouse and stock management
- **Analytics Platforms**: Performance tracking and reporting

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
