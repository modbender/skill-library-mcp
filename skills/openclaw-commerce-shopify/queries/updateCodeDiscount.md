# Shopify Code Discount Update & Management

This guide helps you generate accurate GraphQL mutations for updating code discounts and managing code discount data in Shopify.

## Instructions for Mutation Generation

When a user requests to update code discounts or manage code discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific code discount update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider discount strategy impact** - understand how updates affect active promotions and customers

## Official Documentation

### Primary Code Discount Update Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate

**What to learn from this documentation:**
- Required input fields for code discount updates
- Code discount data modification options
- Discount configuration and rule updates
- Customer eligibility and targeting changes
- Code management and usage limit updates

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate#examples
  - *Review only when you need sample mutation patterns for complex update scenarios*

### Code Discount Update Mutations Documentation

#### Basic Code Discount Update
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicUpdate

**What to learn from this documentation:**
- Simple percentage and fixed amount discount updates
- Basic discount configuration modifications
- Code updates and validation
- Usage limit management changes

#### Buy X Get Y Code Discount Update
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBxgyUpdate

**What to learn from this documentation:**
- Buy X Get Y discount configuration updates
- Product selection and bundling rule changes
- Quantity requirement modifications
- Application logic updates

#### Free Shipping Code Discount Update
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeFreeShippingUpdate

**What to learn from this documentation:**
- Free shipping discount configuration updates
- Shipping method and destination rule changes
- Minimum purchase requirement modifications
- Geographic and carrier restriction updates

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating code discounts.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Code Discount Update Cost Calculation**:
   - Code discount update mutations have moderate to high costs
   - Complex discount rule updates increase cost significantly
   - Usage limit and customer targeting changes add complexity
   - Formula: `cost = base_mutation_cost + discount_complexity + rule_changes + customer_targeting_updates`

3. **Best Practices for Code Discount Update Mutation Generation**:
   - **Include only changed fields**: Don't send unchanged discount data
   - **Validate update logic**: Ensure discount updates make business sense
   - **Test discount behavior**: Validate updated discount behavior
   - **Consider customer impact**: Understand how updates affect customers
   - **Plan update timing**: Coordinate updates with marketing campaigns

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates discount with excessive configuration
   mutation discountCodeAppUpdate($input: DiscountCodeAppInput!) {
     discountCodeAppUpdate(input: $input) {
       discount { id title codes { edges { node { ... } } } 
       customerSelection { ... } discountClass { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates discount with only changed fields
   mutation discountCodeAppUpdate($input: DiscountCodeAppInput!) {
     discountCodeAppUpdate(input: $input) {
       discount {
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

When generating code discount update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Discount ID to update | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$DISCOUNT_TITLE$` | Updated discount title | Ask user if not provided | `"Updated Summer Sale"` |
| `$DISCOUNT_CODE$` | Updated discount code string | Ask user if not provided | `"SUMMER2024"` |
| `$DISCOUNT_TYPE$` | Updated discount type | `"PERCENTAGE"` or `"FIXED_AMOUNT"` | `"PERCENTAGE"` |
| `$DISCOUNT_VALUE$` | Updated discount value | Ask user if not provided | `20.0` |
| `$STARTS_AT$` | Updated discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Updated discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |
| `$MINIMUM_AMOUNT$` | Updated minimum purchase amount | Ask user if not provided | `75.00` |
| `$MINIMUM_QUANTITY$` | Updated minimum purchase quantity | Ask user if not provided | `3` |
| `$USAGE_LIMIT$` | Updated total usage limit | Ask user if not provided | `1500` |
| `$USAGE_LIMIT_PER_CUSTOMER$` | Updated usage limit per customer | Ask user if not provided | `10` |
| `$PRODUCT_IDS$` | Updated product IDs for discount | Ask user if not provided | `[gid://shopify/Product/123456789]` |
| `$COLLECTION_IDS$` | Updated collection IDs for discount | Ask user if not provided | `[gid://shopify/Collection/987654321]` |
| `$CUSTOMER_SEGMENT_IDS$` | Updated customer segment IDs | Ask user if not provided | `[gid://shopify/CustomerSegment/456789123]` |
| `$BUY_QUANTITY$` | Updated buy quantity for BXGY | Ask user if not provided | `3` |
| `$GET_QUANTITY$` | Updated get quantity for BXGY | Ask user if not provided | `1` |
| `$BUY_PRODUCT_IDS$` | Updated buy product IDs for BXGY | Ask user if not provided | `[gid://shopify/Product/111222333]` |
| `$GET_PRODUCT_IDS$` | Updated get product IDs for BXGY | Ask user if not provided | `[gid://shopify/Product/444555666]` |

### Mutation Structure Templates

#### Basic Code Discount Update Template
```graphql
mutation discountCodeBasicUpdate($input: DiscountCodeBasicInput!) {
  discountCodeBasicUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
      codes(first: 10) {
        edges {
          node {
            id
            code
            usageCount
          }
        }
      }
      customerSelection {
        __typename
        ... on DiscountCustomerAll {
          allCustomers
        }
        ... on DiscountCustomerSegments {
          segments {
            id
            name
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

#### Buy X Get Y Code Discount Update Template
```graphql
mutation discountCodeBxgyUpdate($input: DiscountCodeBxgyInput!) {
  discountCodeBxgyUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
      codes(first: 10) {
        edges {
          node {
            id
            code
            usageCount
          }
        }
      }
      customerSelection {
        __typename
        ... on DiscountCustomerAll {
          allCustomers
        }
        ... on DiscountCustomerSegments {
          segments {
            id
            name
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

#### Free Shipping Code Discount Update Template
```graphql
mutation discountCodeFreeShippingUpdate($input: DiscountCodeFreeShippingInput!) {
  discountCodeFreeShippingUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
      codes(first: 10) {
        edges {
          node {
            id
            code
            usageCount
          }
        }
      }
      customerSelection {
        __typename
        ... on DiscountCustomerAll {
          allCustomers
        }
        ... on DiscountCustomerSegments {
          segments {
            id
            name
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

#### App-Based Code Discount Update Template
```graphql
mutation discountCodeAppUpdate($input: DiscountCodeAppInput!) {
  discountCodeAppUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
      codes(first: 10) {
        edges {
          node {
            id
            code
            usageCount
          }
        }
      }
      customerSelection {
        __typename
        ... on DiscountCustomerAll {
          allCustomers
        }
        ... on DiscountCustomerSegments {
          segments {
            id
            name
          }
        }
      }
      discountApp {
        id
        title
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

When generating a code discount update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the discount code settings in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the discount ID and what settings you want to change")
3. **Explain any limitations** in simple terms (e.g., "This will update the discount but may affect customers who are currently using it")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update an existing discount code in your store.

**Mutation:**
```graphql
mutation discountCodeBasicUpdate($input: DiscountCodeBasicInput!) {
  discountCodeBasicUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
      codes(first: 5) {
        edges {
          node {
            id
            code
            usageCount
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
This updates an existing discount code's settings in your Shopify store.

**What I need from you:**
- The discount ID or code you want to update
- What specific settings you want to change (title, discount amount, dates, etc.)
- Any new usage limits or customer restrictions

**Important notes:**
- Changes will be reflected immediately for customers
- Updates may affect customers who have saved or shared the discount code
- Consider timing updates to minimize customer confusion
- Some changes may require reactivation of the discount

Would you like me to help you update a specific discount code?
```

## Common Code Discount Update Scenarios

### Discount Value Updates
- **Use**: `discountCodeBasicUpdate` mutation
- **Use case**: Adjusting discount percentages or amounts
- **Considerations**: Margin impact, customer expectations, competitive positioning

### Discount Schedule Updates
- **Use**: Any code discount update mutation with date changes
- **Use case**: Extending or shortening promotion periods
- **Considerations**: Customer communication, marketing coordination, campaign timing

### Usage Limit Updates
- **Use**: Any code discount update mutation with usage limit changes
- **Use case**: Adjusting usage limits based on performance
- **Considerations**: Customer experience, budget management, promotion effectiveness

### Customer Targeting Updates
- **Use**: Any code discount update mutation with customer selection changes
- **Use case**: Expanding or restricting customer eligibility
- **Considerations**: Segment management, customer classification, privacy

### Product and Collection Updates
- **Use**: `discountCodeBxgyUpdate` or basic updates with product changes
- **Use case**: Updating product selection for discounts
- **Considerations**: Inventory coordination, product availability, category strategy

## Code Discount Configuration Updates

### Discount Value Modifications
- **Percentage Changes**: Adjust discount percentages
- **Fixed Amount Changes**: Modify fixed discount amounts
- **Value Validation**: Ensure new values are within acceptable ranges
- **Margin Impact**: Calculate impact on profit margins

### Schedule and Timing Updates
- **Start Date Changes**: Modify discount activation timing
- **End Date Extensions**: Extend promotion periods
- **Early Termination**: End discounts before scheduled dates
- **Seasonal Adjustments**: Align with seasonal campaigns

### Usage Limit Adjustments
- **Total Limit Changes**: Adjust overall usage limits
- **Per Customer Limits**: Modify individual customer restrictions
- **Time-Based Limits**: Update time-based usage restrictions
- **Performance-Based Adjustments**: Adjust based on usage patterns

### Customer Eligibility Updates
- **Segment Expansion**: Add new customer segments
- **Segment Restriction**: Remove customer segments
- **Dynamic Segments**: Update saved search criteria
- **Individual Customer Changes**: Add or remove specific customers

## Update Impact Analysis

### Customer Experience Impact
- **Code Recognition**: Changes may affect customer recognition of codes
- **Usage Patterns**: Updates may change how customers use discounts
- **Communication Needs**: May require customer communication about changes
- **Trust Considerations**: Maintain customer trust with clear communication

### Marketing Campaign Impact
- **Campaign Coordination**: Align updates with marketing campaigns
- **Promotional Timing**: Coordinate updates with promotional schedules
- **Channel Consistency**: Ensure consistency across marketing channels
- **Performance Tracking**: Monitor impact on campaign performance

### Operational Impact
- **System Performance**: Consider impact on system performance
- **Order Processing**: Ensure smooth integration with order processing
- **Customer Service**: Prepare customer service for update-related inquiries
- **Inventory Coordination**: Coordinate with inventory management

### Financial Impact
- **Margin Analysis**: Calculate impact on profit margins
- **Budget Considerations**: Consider budget implications of changes
- **ROI Tracking**: Track return on investment for updated discounts
- **Revenue Impact**: Monitor impact on overall revenue

## Error Handling

### Common Code Discount Update Errors
- **Discount Not Found**: Verify discount ID or code exists
- **Invalid Update Data**: Check field formats and constraints
- **Permission Denied**: Ensure proper API access for updates
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Configuration Validation Errors
- **Invalid Discount Values**: Discount values must be within valid ranges
- **Conflicting Updates**: Updates must not create logical conflicts
- **Date Range Issues**: Start and end dates must be valid
- **Usage Limit Conflicts**: Usage limits must be logically consistent

### Customer Targeting Errors
- **Invalid Segments**: Customer segments must exist and be valid
- **Permission Issues**: Verify access to customer segments
- **Segment Conflicts**: Targeting changes must not create conflicts
- **Privacy Considerations**: Ensure compliance with privacy regulations

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest different update approaches
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Validate Input** - ensure all update data is valid and consistent
5. **Monitor Impact** - track the impact of updates on customers and operations

## Best Practices

### Before Updating Code Discounts
1. **Analyze Current Performance** - review discount effectiveness before changes
2. **Plan Update Strategy** - define clear objectives for updates
3. **Calculate Impact** - understand financial and operational impact
4. **Communicate Changes** - plan customer communication strategy
5. **Test Updates** - validate update logic before implementation

### During Code Discount Updates
1. **Validate Input Data** - ensure all update data is valid
2. **Monitor Update Success** - track successful discount updates
3. **Handle Errors Gracefully** - provide clear error messages
4. **Document Changes** - maintain records of discount modifications
5. **Coordinate Timing** - time updates to minimize customer disruption

### After Code Discount Updates
1. **Verify Update Success** - confirm updates were applied correctly
2. **Test Customer Experience** - ensure discounts work as expected
3. **Monitor Performance** - track discount performance after updates
4. **Analyze Results** - evaluate effectiveness of updates
5. **Gather Feedback** - collect customer and team feedback

### Ongoing Update Management
1. **Regular Performance Reviews** - periodically review discount performance
2. **Update Strategy Optimization** - refine update strategies based on results
3. **Customer Feedback Analysis** - analyze customer response to updates
4. **Continuous Improvement** - continuously improve discount management
5. **Documentation Maintenance** - keep discount documentation current

## Performance Optimization

### Update Efficiency
- **Targeted Updates** - Update only necessary fields and configurations
- **Batch Operations** - Group related updates when possible
- **Input Validation** - Validate input data before mutations
- **Error Handling** - Implement efficient error handling

### System Performance
- **Query Optimization** - Structure updates for maximum efficiency
- **Resource Management** - Manage system resources effectively
- **Rate Limit Management** - Monitor and manage API rate limits
- **Caching Strategy** - Cache frequently accessed discount data

### Customer Experience Optimization
- **Fast Updates** - Ensure updates are applied quickly
- **Clear Communication** - Communicate changes clearly to customers
- **Consistent Experience** - Maintain consistent discount experience
- **Mobile Optimization** - Ensure updates work well on mobile devices

## Integration Considerations

### Marketing Platform Integration
- **Campaign Synchronization** - Sync discount updates with marketing campaigns
- **Email Marketing** - Update email marketing platforms with discount changes
- **Social Media** - Coordinate social media communications about updates
- **Analytics Integration** - Track update performance across platforms

### Customer Management Integration
- **CRM Updates** - Sync discount changes with customer management systems
- **Loyalty Programs** - Coordinate updates with loyalty program systems
- **Customer Communication** - Update customer communication channels
- **Segment Management** - Maintain consistent customer segmentation

### Analytics and Reporting Integration
- **Performance Tracking** - Track discount performance after updates
- **ROI Analysis** - Analyze return on investment for updated discounts
- **Customer Analytics** - Monitor customer response to updates
- **Business Intelligence** - Integrate with BI tools for analysis

### Third-Party Application Integration
- **App Coordination** - Coordinate updates with Shopify apps
- **API Consistency** - Maintain consistent API usage across systems
- **Data Synchronization** - Ensure discount data is synchronized
- **Security Considerations** - maintain security for discount systems

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
