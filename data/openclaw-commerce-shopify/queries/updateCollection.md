# Shopify Collection Update & Management

This guide helps you generate accurate GraphQL mutations for updating collections and managing collection data in Shopify.

## Instructions for Mutation Generation

When a user requests to update collections or manage collection data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific collection update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider collection organization impact** - understand how updates affect products and navigation

## Official Documentation

### Primary Collection Update Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUpdate

**What to learn from this documentation:**
- Required input fields for collection updates
- Collection data modification options
- Smart collection rule updates
- SEO and metadata management
- Collection image and media updates

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUpdate#examples
  - *Review only when you need sample mutation patterns for collection update scenarios*

### Collection Management Mutations Documentation

#### Collection Reorder Products Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionReorderProducts

**What to learn from this documentation:**
- Product ordering within collections
- Manual product arrangement
- Display optimization
- Customer experience improvements

#### Collection Unpublish Mutation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUnpublish

**What to learn from this documentation:**
- Collection publication status management
- Sales channel visibility control
- Unpublishing workflows and consequences
- Collection state management

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating collections.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Collection Update Cost Calculation**:
   - Collection update mutations have moderate costs
   - Smart collections with complex rules increase cost
   - Product reordering operations can be expensive for large collections
   - Formula: `cost = base_mutation_cost + collection_complexity + rule_changes + product_count`

3. **Best Practices for Collection Update Mutation Generation**:
   - **Include only changed fields**: Don't send unchanged collection data
   - **Optimize smart collection rules**: Keep rules simple and performant
   - **Batch product reordering**: Reorder products in reasonable batches
   - **Use proper error handling**: Always check for user errors in mutation response
   - **Consider customer experience**: Plan updates to minimize disruption

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates collection with excessive product data
   mutation collectionUpdate($input: CollectionInput!) {
     collectionUpdate(input: $input) {
       collection { id title products { edges { node { ... } } } rules { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates collection with only changed fields
   mutation collectionUpdate($input: CollectionInput!) {
     collectionUpdate(input: $input) {
       collection {
         id
         title
         handle
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

When generating collection update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$COLLECTION_ID$` | Collection ID to update | Ask user if not provided | `gid://shopify/Collection/123456789` |
| `$COLLECTION_TITLE$` | Updated collection title | Ask user if not provided | `"Updated Summer Collection"` |
| `$COLLECTION_DESCRIPTION$` | Updated collection description | Ask user if not provided | `"Updated description for summer collection"` |
| `$COLLECTION_HANDLE$` | Updated collection handle | Auto-generated from title | `"updated-summer-collection"` |
| `$SEO_TITLE$` | Updated SEO title | Ask user if not provided | `"Updated Summer Collection - New Arrivals"` |
| `$SEO_DESCRIPTION$` | Updated SEO description | Ask user if not provided | `"Shop our updated summer collection"` |
| `$STATUS$` | Updated collection status | `"ACTIVE"` | `"ARCHIVED"` |
| `$RULE_COLUMN$` | Smart collection rule column | Ask user if not provided | `"TAG"` |
| `$RULE_RELATION$` | Smart collection rule relation | Ask user if not provided | `"CONTAINS"` |
| `$RULE_CONDITION$` | Smart collection rule condition | Ask user if not provided | `"summer"` |
| `$PRODUCT_IDS$` | Product IDs for reordering | Ask user if not provided | `[gid://shopify/Product/987654321]` |
| `$PUBLICATION_ID$` | Publication ID for unpublish | Ask user if not provided | `gid://shopify/Publication/456789123` |
| `$IMAGE_URL$` | Updated collection image URL | Ask user if not provided | `"https://example.com/collection.jpg"` |
| `$IMAGE_ALT_TEXT$` | Updated image alt text | Ask user if not provided | `"Updated summer collection featured products"` |

### Mutation Structure Templates

#### Basic Collection Update Template
```graphql
mutation collectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
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

#### Smart Collection Rules Update Template
```graphql
mutation collectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
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
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Collection Products Reorder Template
```graphql
mutation collectionReorderProducts($collectionId: ID!, $moves: [Move!]!) {
  collectionReorderProducts(collectionId: $collectionId, moves: $moves) {
    collection {
      id
      title
      handle
      products(first: 10) {
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

#### Collection Unpublish Template
```graphql
mutation collectionUnpublish($input: CollectionUnpublishInput!) {
  collectionUnpublish(input: $input) {
    collection {
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

#### Collection Image Update Template
```graphql
mutation collectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection {
      id
      title
      handle
      description
      image {
        id
        url
        altText
        width
        height
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

## Response Guidelines

When generating a collection update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the collection information in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the collection ID and what information you want to change")
3. **Explain any limitations** in simple terms (e.g., "This will update the collection but may affect how products are displayed")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update an existing collection in your store.

**Mutation:**
```graphql
mutation collectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection {
      id
      title
      handle
      description
      collectionType
      status
      productsCount
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This updates an existing collection's information in your Shopify store.

**What I need from you:**
- The collection ID or title you want to update
- What specific information you want to change (title, description, rules, etc.)
- Any image or SEO updates you want to make

**Important notes:**
- Changes will be reflected immediately across your store
- Smart collection rule changes will update product inclusion automatically
- Custom collection changes won't affect product inclusion unless you modify products

Would you like me to help you update a specific collection?
```

## Common Collection Update Scenarios

### Basic Collection Information Updates
- **Use**: `collectionUpdate` mutation
- **Fields**: Title, description, handle, SEO information
- **Considerations**: SEO impact, navigation structure, customer experience

### Smart Collection Rule Updates
- **Use**: `collectionUpdate` with rules
- **Use case**: Modifying automatic product inclusion criteria
- **Considerations**: Rule performance, product inclusion logic, collection accuracy

### Collection Product Reordering
- **Use**: `collectionReorderProducts` mutation
- **Use case**: Optimizing product display order, featured products
- **Considerations**: Customer experience, sales optimization, visual hierarchy

### Collection Publication Management
- **Use**: `collectionUpdate` or `collectionUnpublish` mutation
- **Use case**: Publishing, archiving, hiding collections
- **Considerations**: Sales channel visibility, customer access, navigation impact

### Collection Image Updates
- **Use**: `collectionUpdate` with image data
- **Use case**: Refreshing collection visuals, seasonal updates
- **Considerations**: Image optimization, visual consistency, branding

## Collection Update Impact Analysis

### SEO Impact
- **Title Changes**: May affect search rankings and navigation
- **Description Updates**: Impact search snippets and customer understanding
- **URL Handle Changes**: May break existing links and bookmarks
- **Image Updates**: Can improve visual appeal and click-through rates

### Navigation Impact
- **Collection Visibility**: Status changes affect menu navigation
- **Title Changes**: Update navigation menu items
- **Handle Changes**: May affect custom navigation links
- **Publication Changes**: Determine where collections appear

### Product Display Impact
- **Smart Collection Rules**: Automatically update product inclusion
- **Product Reordering**: Change how products are displayed to customers
- **Collection Type Changes**: Switch between smart and custom behavior
- **Status Changes**: Hide or show entire collections from customers

### Customer Experience Impact
- **Collection Availability**: Status changes affect customer access
- **Visual Updates**: Image changes improve visual appeal
- **Organization**: Better organization improves product discovery
- **Search Optimization**: SEO improvements help customers find collections

## Data Validation Guidelines

### Collection Update Validation
- **Collection Existence**: Verify collection exists and is accessible
- **Field Constraints**: Ensure data meets field requirements
- **Business Rules**: Validate against store policies
- **Permission Check**: Ensure proper access for updates

### Smart Collection Rule Validation
- **Valid Columns**: Rule columns must be supported
- **Proper Relations**: Must use valid relation operators
- **Logical Conditions**: Conditions must make business sense
- **Performance Impact**: Consider rule complexity and performance

### Product Reordering Validation
- **Product Existence**: Products must exist in collection
- **Position Validity**: Positions must be valid integers
- **Range Constraints**: Positions must be within valid range
- **Duplicate Positions**: Avoid duplicate position assignments

## Error Handling

### Common Collection Update Errors
- **Collection Not Found**: Verify collection ID or handle
- **Invalid Data**: Check field formats and constraints
- **Permission Denied**: Ensure proper API access
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Smart Collection Rule Errors
- **Invalid Columns**: Rule columns must be supported
- **Malformed Conditions**: Rule conditions must be properly formatted
- **Performance Issues**: Complex rules may cause timeouts
- **Logic Conflicts**: Contradictory rules may cause issues

### Product Reordering Errors
- **Product Not in Collection**: Products must exist in collection
- **Invalid Positions**: Position values must be valid
- **Range Errors**: Positions must be within collection bounds
- **Permission Issues**: Verify access to collection and products

### Publication Update Errors
- **Invalid Publication**: Publication must exist and be accessible
- **Permission Denied**: Verify publication access permissions
- **Status Conflicts**: Publication status must be compatible
- **Channel Issues**: Sales channel may have restrictions

## Best Practices

### Before Updating Collections
1. **Backup Data**: Preserve current collection information
2. **Test Changes**: Validate updates in development environment
3. **Plan Impact**: Understand how changes affect navigation and SEO
4. **Communicate Changes**: Inform relevant team members
5. **Schedule Updates**: Choose optimal timing for changes

### During Collection Updates
1. **Use Transactions**: Group related changes together
2. **Validate Input**: Check data before sending mutations
3. **Monitor Performance**: Watch for system impact
4. **Handle Errors**: Implement proper error handling
5. **Log Changes**: Maintain audit trail of updates

### After Collection Updates
1. **Verify Changes**: Confirm updates were applied correctly
2. **Check Navigation**: Ensure navigation menus updated properly
3. **Test SEO**: Verify SEO elements are correct
4. **Monitor Impact**: Watch for unexpected consequences
5. **Update Documentation**: Keep collection documentation current

## Performance Optimization

### Update Efficiency
- **Batch Changes**: Group related updates together
- **Minimize Data**: Send only changed fields
- **Optimize Rules**: Keep smart collection rules simple
- **Use Caching**: Cache frequently accessed collection data

### Smart Collection Performance
- **Rule Optimization**: Keep rules simple and efficient
- **Monitor Load**: Watch collection loading times
- **Test Thoroughly**: Validate rule performance
- **Consider Alternatives**: Use custom collections for complex logic

### Product Reordering Efficiency
- **Batch Operations**: Reorder products in reasonable batches
- **Limit Scope**: Focus on high-impact collections first
- **Monitor Impact**: Watch for performance degradation
- **Test Changes**: Validate reordering results

## SEO Considerations

### Collection Handle Management
- **URL Consistency**: Avoid changing handles frequently
- **Redirect Setup**: Implement redirects for handle changes
- **Keyword Optimization**: Include relevant keywords in handles
- **Structure Consistency**: Follow consistent naming patterns

### Meta Information Updates
- **Title Optimization**: Keep titles under 60 characters
- **Description Quality**: Write compelling descriptions under 160 characters
- **Keyword Integration**: Include relevant search terms naturally
- **Regular Updates**: Keep meta information current and relevant

### Image SEO
- **Alt Text Optimization**: Use descriptive alt text for accessibility
- **File Naming**: Use SEO-friendly image file names
- **Image Optimization**: Balance quality with loading speed
- **Structured Data**: Consider schema markup for collections

## Collection Organization Strategies

### Hierarchical Updates
- **Main Categories**: Update broad category collections first
- **Subcategories**: Coordinate with parent category changes
- **Filter Collections**: Update specialized collections after main changes
- **Cross-References**: Maintain consistent cross-references

### Seasonal Management
- **Current Season**: Prioritize active seasonal collections
- **Upcoming Season**: Prepare future seasonal collections
- **Archive Management**: Update and organize past seasonal collections
- **Transition Planning**: Plan smooth transitions between seasons

### Performance-Based Updates
- **Sales Data**: Use sales data to prioritize collection updates
- **Customer Behavior**: Update based on customer interaction patterns
- **Conversion Rates**: Focus on collections with high conversion potential
- **Search Performance**: Optimize collections based on search data

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
