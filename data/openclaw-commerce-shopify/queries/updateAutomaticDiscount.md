# Shopify Automatic Discount Update & Management

This guide helps you generate accurate GraphQL mutations for updating automatic discounts and managing automatic discount data in Shopify.

## Instructions for Mutation Generation

When a user requests to update automatic discounts or manage automatic discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific automatic discount update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider discount strategy impact** - understand how updates affect active promotions and customer experience

## Official Documentation

### Primary Automatic Discount Update Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate

**What to learn from this documentation:**
- Required input fields for automatic discount updates
- Automatic discount data modification options
- Condition logic and eligibility rule updates
- Customer targeting and segmentation changes
- Discount application criteria modifications

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate#examples
  - *Review only when you need sample mutation patterns for complex update scenarios*

### Automatic Discount Update Mutations Documentation

#### Basic Automatic Discount Update
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicUpdate

**What to learn from this documentation:**
- Simple percentage and fixed amount automatic discount updates
- Basic condition configuration modifications
- Customer eligibility setting changes
- Application logic updates

#### Buy X Get Y Automatic Discount Update
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBxgyUpdate

**What to learn from this documentation:**
- Buy X Get Y automatic discount configuration updates
- Product selection and bundling rule changes
- Quantity requirement modifications
- Application logic and customer experience updates

#### Free Shipping Automatic Discount Update
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingUpdate

**What to learn from this documentation:**
- Free shipping automatic discount configuration updates
- Shipping method and destination rule changes
- Minimum purchase requirement modifications
- Geographic and carrier restriction updates

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating automatic discounts.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Automatic Discount Update Cost Calculation**:
   - Automatic discount update mutations have high costs due to complexity
   - Condition logic updates significantly increase cost
   - Customer targeting and eligibility changes add complexity
   - Formula: `cost = base_mutation_cost + condition_complexity_updates + eligibility_logic_changes + customer_targeting_updates`

3. **Best Practices for Automatic Discount Update Mutation Generation**:
   - **Include only changed fields**: Don't send unchanged discount data
   - **Validate condition logic**: Ensure updated conditions make business sense
   - **Test discount behavior**: Validate updated automatic application logic
   - **Consider customer impact**: Understand how updates affect customer experience
   - **Plan update timing**: Coordinate updates to minimize customer disruption

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates discount with excessive configuration
   mutation discountAutomaticAppUpdate($input: DiscountAutomaticAppInput!) {
     discountAutomaticAppUpdate(input: $input) {
       discount { id title conditions { ... } 
       customerSelection { ... } discountClass { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates discount with only changed fields
   mutation discountAutomaticAppUpdate($input: DiscountAutomaticAppInput!) {
     discountAutomaticAppUpdate(input: $input) {
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

When generating automatic discount update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Discount ID to update | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$DISCOUNT_TITLE$` | Updated discount title | Ask user if not provided | `"Updated Volume Discount"` |
| `$DISCOUNT_TYPE$` | Updated discount type | `"PERCENTAGE"` or `"FIXED_AMOUNT"` | `"PERCENTAGE"` |
| `$DISCOUNT_VALUE$` | Updated discount value | Ask user if not provided | `15.0` |
| `$STARTS_AT$` | Updated discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Updated discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |
| `$MINIMUM_AMOUNT$` | Updated minimum purchase amount | Ask user if not provided | `120.00` |
| `$MINIMUM_QUANTITY$` | Updated minimum purchase quantity | Ask user if not provided | `6` |
| `$PRODUCT_IDS$` | Updated product IDs for discount | Ask user if not provided | `[gid://shopify/Product/123456789]` |
| `$COLLECTION_IDS$` | Updated collection IDs for discount | Ask user if not provided | `[gid://shopify/Collection/987654321]` |
| `$CUSTOMER_SEGMENT_IDS$` | Updated customer segment IDs | Ask user if not provided | `[gid://shopify/CustomerSegment/456789123]` |
| `$BUY_QUANTITY$` | Updated buy quantity for BXGY | Ask user if not provided | `3` |
| `$GET_QUANTITY$` | Updated get quantity for BXGY | Ask user if not provided | `1` |
| `$BUY_PRODUCT_IDS$` | Updated buy product IDs for BXGY | Ask user if not provided | `[gid://shopify/Product/111222333]` |
| `$GET_PRODUCT_IDS$` | Updated get product IDs for BXGY | Ask user if not provided | `[gid://shopify/Product/444555666]` |

### Mutation Structure Templates

#### Basic Automatic Discount Update Template
```graphql
mutation discountAutomaticBasicUpdate($input: DiscountAutomaticBasicInput!) {
  discountAutomaticBasicUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
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
        ... on DiscountCustomerSavedSearches {
          savedSearches {
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

#### Buy X Get Y Automatic Discount Update Template
```graphql
mutation discountAutomaticBxgyUpdate($input: DiscountAutomaticBxgyInput!) {
  discountAutomaticBxgyUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
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
        ... on DiscountCustomerSavedSearches {
          savedSearches {
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

#### Free Shipping Automatic Discount Update Template
```graphql
mutation discountAutomaticFreeShippingUpdate($input: DiscountAutomaticFreeShippingInput!) {
  discountAutomaticFreeShippingUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
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
        ... on DiscountCustomerSavedSearches {
          savedSearches {
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

#### App-Based Automatic Discount Update Template
```graphql
mutation discountAutomaticAppUpdate($input: DiscountAutomaticAppInput!) {
  discountAutomaticAppUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
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
        ... on DiscountCustomerSavedSearches {
          savedSearches {
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

When generating an automatic discount update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the automatic discount settings in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the discount ID and what settings you want to change")
3. **Explain any limitations** in simple terms (e.g., "This will update the discount but may affect customers who are currently shopping")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update an existing automatic discount in your store.

**Mutation:**
```graphql
mutation discountAutomaticBasicUpdate($input: DiscountAutomaticBasicInput!) {
  discountAutomaticBasicUpdate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
      updatedAt
      summary
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

**What this does:**
This updates an existing automatic discount's settings in your Shopify store.

**What I need from you:**
- The discount ID or title you want to update
- What specific settings you want to change (conditions, discount amount, dates, etc.)
- Any new customer targeting or eligibility changes

**Important notes:**
- Changes will be applied immediately to customer carts
- Updates may affect customers who are currently shopping
- Consider timing updates to minimize customer confusion
- Test condition changes to ensure they work as expected

Would you like me to help you update a specific automatic discount?
```

## Common Automatic Discount Update Scenarios

### Discount Value Updates
- **Use**: `discountAutomaticBasicUpdate` mutation
- **Use case**: Adjusting automatic discount percentages or amounts
- **Considerations**: Margin impact, customer expectations, competitive positioning

### Condition Logic Updates
- **Use**: Any automatic discount update mutation with condition changes
- **Use case**: Modifying purchase requirements, eligibility criteria
- **Considerations**: Customer experience, condition complexity, performance

### Customer Targeting Updates
- **Use**: Any automatic discount update mutation with customer selection changes
- **Use case**: Expanding or restricting customer eligibility
- **Considerations**: Segment management, customer classification, privacy

### Schedule and Timing Updates
- **Use**: Any automatic discount update mutation with date changes
- **Use case**: Extending or shortening automatic discount periods
- **Considerations**: Customer experience, marketing coordination, campaign timing

### Product and Collection Updates
- **Use**: `discountAutomaticBxgyUpdate` or basic updates with product changes
- **Use case**: Updating product selection for automatic discounts
- **Considerations**: Inventory coordination, product availability, category strategy

## Automatic Discount Configuration Updates

### Discount Value Modifications
- **Percentage Changes**: Adjust automatic discount percentages
- **Fixed Amount Changes**: Modify fixed automatic discount amounts
- **Value Validation**: Ensure new values are within acceptable ranges
- **Margin Impact**: Calculate impact on profit margins

### Condition Logic Updates
- **Quantity Requirements**: Modify minimum quantity conditions
- **Amount Requirements**: Adjust minimum purchase amount conditions
- **Product Conditions**: Update product-specific eligibility conditions
- **Customer Conditions**: Modify customer eligibility criteria

### Schedule and Timing Updates
- **Start Date Changes**: Modify automatic discount activation timing
- **End Date Extensions**: Extend automatic discount periods
- **Early Termination**: End automatic discounts before scheduled dates
- **Seasonal Adjustments**: Align with seasonal campaigns

### Customer Eligibility Updates
- **Segment Expansion**: Add new customer segments
- **Segment Restriction**: Remove customer segments
- **Dynamic Segments**: Update saved search criteria
- **Universal Application**: Change to all customers or specific groups

## Update Impact Analysis

### Customer Experience Impact
- **Automatic Application**: Changes affect how discounts are automatically applied
- **Checkout Flow**: Updates may impact checkout experience
- **Transparency**: Customers should understand discount application
- **Trust Considerations**: Maintain customer trust with consistent behavior

### Marketing Campaign Impact
- **Campaign Coordination**: Align updates with marketing campaigns
- **Promotional Timing**: Coordinate updates with promotional schedules
- **Channel Consistency**: Ensure consistency across marketing channels
- **Performance Tracking**: Monitor impact on campaign performance

### Operational Impact
- **System Performance**: Consider impact on condition evaluation performance
- **Order Processing**: Ensure smooth integration with order processing
- **Inventory Coordination**: Coordinate with inventory management
- **Customer Service**: Prepare customer service for update-related inquiries

### Financial Impact
- **Margin Analysis**: Calculate impact on profit margins
- **Budget Considerations**: Consider budget implications of changes
- **ROI Tracking**: Track return on investment for updated discounts
- **Revenue Impact**: Monitor impact on overall revenue

## Condition Logic Updates

### Quantity-Based Condition Updates
- **Minimum Quantity Changes**: Adjust minimum purchase quantities
- **Product Quantity Rules**: Modify product-specific quantity requirements
- **Category Quantity**: Update category-level quantity conditions
- **Tiered Quantity**: Implement or modify tiered quantity discounts

### Amount-Based Condition Updates
- **Minimum Amount Changes**: Adjust minimum purchase amounts
- **Currency Considerations**: Handle multi-currency amount conditions
- **Tiered Amount**: Implement or modify tiered amount discounts
- **Cart Value**: Update cart value-based conditions

### Product-Based Condition Updates
- **Product Selection**: Modify eligible products
- **Collection Updates**: Update collection-based conditions
- **Product Type Changes**: Adjust product type eligibility
- **Tag-Based Conditions**: Update product tag-based eligibility

### Customer-Based Condition Updates
- **Segment Updates**: Modify customer segment eligibility
- **Behavioral Conditions**: Update behavior-based eligibility
- **Location-Based**: Adjust geographic eligibility conditions
- **Purchase History**: Update purchase history-based conditions

## Error Handling

### Common Automatic Discount Update Errors
- **Discount Not Found**: Verify discount ID exists
- **Invalid Update Data**: Check field formats and constraints
- **Permission Denied**: Ensure proper API access for updates
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Condition Logic Errors
- **Invalid Conditions**: Condition logic must be valid and achievable
- **Conflicting Rules**: Updated conditions must not create conflicts
- **Performance Issues**: Complex conditions may affect system performance
- **Circular Logic**: Conditions must not create circular dependencies

### Customer Targeting Errors
- **Invalid Segments**: Customer segments must exist and be valid
- **Permission Issues**: Verify access to customer segments
- **Segment Conflicts**: Targeting changes must not create conflicts
- **Privacy Considerations**: Ensure compliance with privacy regulations

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest different update approaches
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Validate Logic** - ensure condition logic is sound and achievable
5. **Test Thoroughly** - test updated discount behavior before activation

## Best Practices

### Before Updating Automatic Discounts
1. **Analyze Current Performance** - review discount effectiveness before changes
2. **Test Condition Logic** - validate updated conditions before implementation
3. **Calculate Impact** - understand financial and operational impact
4. **Plan Update Timing** - coordinate updates to minimize disruption
5. **Communicate Changes** - plan internal communication about updates

### During Automatic Discount Updates
1. **Validate Input Data** - ensure all update data is valid
2. **Monitor Update Success** - track successful discount updates
3. **Handle Errors Gracefully** - provide clear error messages
4. **Document Changes** - maintain records of discount modifications
5. **Coordinate Timing** - time updates to minimize customer impact

### After Automatic Discount Updates
1. **Verify Update Success** - confirm updates were applied correctly
2. **Test Customer Experience** - ensure discounts apply correctly at checkout
3. **Monitor Performance** - track discount performance after updates
4. **Analyze Results** - evaluate effectiveness of updates
5. **Gather Feedback** - collect customer and team feedback

### Ongoing Update Management
1. **Regular Performance Reviews** - periodically review discount performance
2. **Condition Optimization** - refine condition logic for better performance
3. **Customer Feedback Analysis** - analyze customer response to updates
4. **Continuous Improvement** - continuously improve discount management
5. **Documentation Maintenance** - keep discount documentation current

## Performance Optimization

### Condition Evaluation Optimization
- **Simple Conditions**: Use simple, efficient condition logic
- **Index Optimization**: Structure conditions for efficient evaluation
- **Caching Strategy**: Cache frequently accessed condition data
- **Performance Monitoring**: Monitor condition evaluation performance

### Update Efficiency
- **Targeted Updates** - Update only necessary fields and conditions
- **Batch Operations** - Group related updates when possible
- **Input Validation** - Validate input data before mutations
- **Error Handling** - Implement efficient error handling

### System Performance
- **Query Optimization** - Structure updates for maximum efficiency
- **Resource Management** - Manage system resources effectively
- **Rate Limit Management** - Monitor and manage API rate limits
- **Load Balancing** - Distribute discount processing load

### Customer Experience Optimization
- **Fast Application** - Ensure updated discounts apply quickly at checkout
- **Consistent Behavior** - Maintain consistent discount application
- **Clear Display** - Clearly display applied discounts to customers
- **Mobile Optimization** - Ensure updates work well on mobile devices

## Integration Considerations

### Checkout Integration
- **Real-time Updates** - Ensure updated conditions are evaluated in real-time
- **Order Processing** - Integrate smoothly with order processing systems
- **Payment Processing** - Coordinate with payment processing
- **Customer Experience** - Maintain smooth checkout experience

### Customer Management Integration
- **Segment Updates** - Keep customer segments current and accurate
- **Behavior Tracking** - Track customer response to updated discounts
- **Loyalty Integration** - Coordinate with customer loyalty programs
- **Personalization** - Use discount data for personalization

### Inventory Management Integration
- **Stock Coordination** - Coordinate updates with inventory management
- **Product Availability** - Ensure discounted products are available
- **Supply Chain Impact** - Consider supply chain implications
- **Forecasting** - Use discount data for inventory forecasting

### Analytics Integration
- **Performance Tracking** - Track updated discount performance metrics
- **ROI Analysis** - Analyze return on investment for updated discounts
- **Customer Analytics** - Monitor customer behavior with updated discounts
- **Business Intelligence** - integrate with BI tools for analysis

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
