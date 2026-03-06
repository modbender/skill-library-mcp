# Shopify Automatic Discount Creation & Management

This guide helps you generate accurate GraphQL mutations for creating automatic discounts and managing automatic discount data in Shopify.

## Instructions for Mutation Generation

When a user requests to create automatic discounts or manage automatic discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific automatic discount creation requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider discount strategy impact** - understand how automatic discounts affect pricing and customer experience

## Official Documentation

### Primary Automatic Discount Creation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate

**What to learn from this documentation:**
- Required input fields for automatic discount creation
- Automatic discount data structure and validation
- Condition logic and eligibility rules
- Customer targeting and segmentation
- Discount application criteria

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate#examples
  - *Review only when you need sample mutation patterns for complex discount scenarios*

### Automatic Discount Management Mutations Documentation

#### Basic Automatic Discount Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicCreate

**What to learn from this documentation:**
- Simple percentage and fixed amount automatic discount creation
- Basic condition configuration
- Customer eligibility settings
- Application logic and timing

#### Buy X Get Y Automatic Discount Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBxgyCreate

**What to learn from this documentation:**
- Automatic Buy X Get Y discount configuration
- Product selection and bundling rules
- Quantity requirements and automatic application
- Customer experience considerations

#### Free Shipping Automatic Discount Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingCreate

**What to learn from this documentation:**
- Automatic free shipping discount configuration
- Shipping method and destination rules
- Minimum purchase requirements and conditions
- Geographic and carrier restrictions

#### Automatic Discount Activation Management
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticActivate

**What to learn from this documentation:**
- Automatic discount activation workflows
- Status management and scheduling
- Condition validation and testing
- Activation timing and coordination

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating automatic discounts.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Automatic Discount Creation Cost Calculation**:
   - Automatic discount creation mutations have high costs due to complexity
   - Condition logic and eligibility rules significantly increase cost
   - Customer targeting and segmentation add additional complexity
   - Formula: `cost = base_mutation_cost + condition_complexity + eligibility_logic + customer_targeting`

3. **Best Practices for Automatic Discount Creation Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate condition logic**: Ensure discount conditions make business sense
   - **Test discount behavior**: Validate automatic application before activation
   - **Consider customer experience**: Design automatic discounts for smooth checkout
   - **Optimize condition evaluation**: Structure conditions for efficient evaluation

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates discount with excessive condition logic
   mutation discountAutomaticAppCreate($input: DiscountAutomaticAppInput!) {
     discountAutomaticAppCreate(input: $input) {
       discount { id title conditions { ... } 
       customerSelection { ... } discountClass { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates discount with essential fields only
   mutation discountAutomaticAppCreate($input: DiscountAutomaticAppInput!) {
     discountAutomaticAppCreate(input: $input) {
       discount {
         id
         title
         status
         startsAt
         endsAt
         summary
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

When generating automatic discount creation mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_TITLE$` | Discount title | Ask user if not provided | `"Volume Discount"` |
| `$DISCOUNT_TYPE$` | Discount type | `"PERCENTAGE"` or `"FIXED_AMOUNT"` | `"PERCENTAGE"` |
| `$DISCOUNT_VALUE$` | Discount value | Ask user if not provided | `10.0` |
| `$STARTS_AT$` | Discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |
| `$MINIMUM_AMOUNT$` | Minimum purchase amount | Ask user if not provided | `100.00` |
| `$MINIMUM_QUANTITY$` | Minimum purchase quantity | Ask user if not provided | `5` |
| `$PRODUCT_IDS$` | Product IDs for discount | Ask user if not provided | `[gid://shopify/Product/123456789]` |
| `$COLLECTION_IDS$` | Collection IDs for discount | Ask user if not provided | `[gid://shopify/Collection/987654321]` |
| `$CUSTOMER_SEGMENT_IDS$` | Customer segment IDs | Ask user if not provided | `[gid://shopify/CustomerSegment/456789123]` |
| `$DISCOUNT_ID$` | Discount ID for activation | Ask user if not provided | `gid://shopify/DiscountNode/789123456` |
| `$BUY_QUANTITY$` | Buy quantity for BXGY | Ask user if not provided | `2` |
| `$GET_QUANTITY$` | Get quantity for BXGY | Ask user if not provided | `1` |
| `$BUY_PRODUCT_IDS$` | Buy product IDs for BXGY | Ask user if not provided | `[gid://shopify/Product/111222333]` |
| `$GET_PRODUCT_IDS$` | Get product IDs for BXGY | Ask user if not provided | `[gid://shopify/Product/444555666]` |

### Mutation Structure Templates

#### Basic Automatic Discount Creation Template
```graphql
mutation discountAutomaticBasicCreate($input: DiscountAutomaticBasicInput!) {
  discountAutomaticBasicCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### Buy X Get Y Automatic Discount Creation Template
```graphql
mutation discountAutomaticBxgyCreate($input: DiscountAutomaticBxgyInput!) {
  discountAutomaticBxgyCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### Free Shipping Automatic Discount Creation Template
```graphql
mutation discountAutomaticFreeShippingCreate($input: DiscountAutomaticFreeShippingInput!) {
  discountAutomaticFreeShippingCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### App-Based Automatic Discount Creation Template
```graphql
mutation discountAutomaticAppCreate($input: DiscountAutomaticAppInput!) {
  discountAutomaticAppCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### Automatic Discount Activation Template
```graphql
mutation discountAutomaticActivate($id: ID!) {
  discountAutomaticActivate(id: $id) {
    discount {
      id
      title
      status
      startsAt
      endsAt
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating an automatic discount creation mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create an automatic discount that applies when customers meet certain conditions")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the discount title, conditions, and who should receive it")
3. **Explain any limitations** in simple terms (e.g., "This creates the discount but you'll need to activate it before it applies to customer orders")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new automatic discount for your store.

**Mutation:**
```graphql
mutation discountAutomaticBasicCreate($input: DiscountAutomaticBasicInput!) {
  discountAutomaticBasicCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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
This creates an automatic discount that will be applied to customer orders when specific conditions are met.

**What I need from you:**
- Discount title and conditions (e.g., "Volume Discount" for orders over $100)
- Discount type and amount (percentage or fixed amount)
- Who should receive the discount (all customers or specific groups)
- When the discount should start and end

**Important notes:**
- Automatic discounts apply without customers needing to enter codes
- You can set conditions like minimum purchase amounts or quantities
- Consider how the discount will affect your profit margins
- The discount will need to be activated before it applies to orders

Would you like me to help you create a specific automatic discount?
```

## Common Automatic Discount Creation Scenarios

### Volume-Based Discounts
- **Use**: `discountAutomaticBasicCreate` mutation with quantity conditions
- **Use case**: Bulk purchase incentives, wholesale pricing, volume optimization
- **Considerations**: Inventory management, margin calculation, customer segmentation

### Cart Value-Based Discounts
- **Use**: `discountAutomaticBasicCreate` mutation with amount conditions
- **Use case**: Average order value optimization, cart abandonment reduction
- **Considerations**: Average order value analysis, customer spending patterns

### Customer Segment Discounts
- **Use**: Any automatic discount creation with customer segment targeting
- **Use case**: VIP pricing, wholesale pricing, loyalty programs
- **Considerations**: Segment management, customer classification, privacy

### Product-Specific Automatic Discounts
- **Use**: `discountAutomaticBasicCreate` with product targeting
- **Use case**: Product promotions, category sales, inventory clearance
- **Considerations**: Product selection, inventory coordination, category strategy

### Buy X Get Y Automatic Discounts
- **Use**: `discountAutomaticBxgyCreate` mutation
- **Use case**: Product bundling, cross-selling, inventory management
- **Considerations**: Product selection, inventory coordination, customer experience

### Free Shipping Automatic Discounts
- **Use**: `discountAutomaticFreeShippingCreate` mutation
- **Use case**: Shipping cost incentives, cart value optimization
- **Considerations**: Shipping costs, geographic limitations, profit margins

## Automatic Discount Configuration Options

### Discount Value Types
- **Percentage**: Percentage off total cart or specific items
- **Fixed Amount**: Fixed monetary amount off total cart or specific items
- **Free Shipping**: Free or discounted shipping
- **Custom**: App-specific discount logic

### Condition Logic Types
- **Minimum Quantity**: Discount applies when minimum quantity is met
- **Minimum Amount**: Discount applies when minimum cart value is reached
- **Product-Specific**: Discount applies to specific products or collections
- **Customer-Based**: Discount applies based on customer attributes

### Customer Targeting Options
- **All Customers**: Available to all store customers
- **Customer Segments**: Specific customer groups (VIP, wholesale, etc.)
- **Saved Searches**: Dynamic customer groups based on criteria
- **Individual Customers**: Specific customer assignments

### Application Rules
- **Automatic Application**: Discount applies automatically when conditions are met
- **Priority Ordering**: Define which discount applies when multiple qualify
- **Combination Rules**: Define how discounts combine with other promotions
- **Exclusion Rules**: Define products or customers excluded from discounts

## Condition Logic and Rules

### Quantity-Based Conditions
- **Minimum Cart Quantity**: Discount applies when cart has minimum items
- **Product Quantity**: Discount applies when specific product quantities are met
- **Category Quantity**: Discount applies when category quantities are met
- **Variant Quantity**: Discount applies for specific variant quantities

### Amount-Based Conditions
- **Minimum Cart Value**: Discount applies when cart reaches minimum value
- **Product Value**: Discount applies when specific product values are met
- **Category Value**: Discount applies when category values are met
- **Currency Handling**: Multi-currency support and conversion

### Product-Based Conditions
- **Specific Products**: Discount applies to selected products
- **Product Collections**: Discount applies to entire collections
- **Product Types**: Discount applies to specific product types
- **Product Tags**: Discount applies based on product tags

### Customer-Based Conditions
- **Customer Segments**: Discount applies to specific customer segments
- **Customer Tags**: Discount applies based on customer tags
- **Purchase History**: Discount applies based on purchase behavior
- **Location-Based**: Discount applies based on customer location

## Automatic Discount Strategy Considerations

### Customer Experience Impact
- **Checkout Flow**: Automatic discounts should not complicate checkout
- **Transparency**: Customers should understand why discounts are applied
- **Consistency**: Discount application should be predictable and consistent
- **Mobile Experience**: Ensure automatic discounts work well on mobile devices

### Margin and Profit Impact
- **Cost Analysis**: Calculate impact on profit margins
- **Break-Even Points**: Determine break-even usage levels
- **Customer Lifetime Value**: Consider long-term customer value
- **Competitive Analysis**: Analyze competitive positioning

### Operational Considerations
- **System Performance**: Ensure automatic discounts don't slow checkout
- **Inventory Impact**: Coordinate discounts with inventory management
- **Order Processing**: Ensure discounts integrate smoothly with order processing
- **Customer Service**: Prepare customer service for discount-related inquiries

### Marketing Integration
- **Promotion Coordination**: Align automatic discounts with marketing campaigns
- **Customer Communication**: Plan customer communication strategy
- **Performance Tracking**: Track discount performance and effectiveness
- **Campaign Measurement**: Measure impact on marketing campaign success

## Error Handling

### Common Automatic Discount Creation Errors
- **Invalid Condition Logic**: Conditions must be logically consistent
- **Conflicting Rules**: Discount rules must not conflict with each other
- **Invalid Date Ranges**: Start and end dates must be valid
- **Permission Issues**: Verify API access for discount creation

### Configuration Validation Errors
- **Invalid Product Selection**: Products must exist and be accessible
- **Customer Segment Issues**: Customer segments must be valid
- **Condition Conflicts**: Conditions must not create logical conflicts
- **Currency Issues**: Currency values must be valid for store

### Condition Logic Errors
- **Circular Logic**: Conditions must not create circular dependencies
- **Impossible Conditions**: Conditions must be achievable by customers
- **Conflicting Conditions**: Multiple conditions must not conflict
- **Performance Issues**: Complex conditions may affect system performance

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest different discount configurations
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Validate Logic** - ensure condition logic is sound and achievable
5. **Test Thoroughly** - test discount behavior before activation

## Best Practices

### Before Creating Automatic Discounts
1. **Define Clear Objectives** - establish clear business goals
2. **Analyze Customer Behavior** - understand customer purchasing patterns
3. **Calculate Margin Impact** - understand financial implications
4. **Test Condition Logic** - validate conditions before implementation
5. **Plan Customer Communication** - prepare customer messaging

### During Automatic Discount Creation
1. **Validate Input Data** - ensure all required fields are valid
2. **Test Discount Behavior** - verify discount application logic
3. **Monitor Creation Success** - track successful discount creation
4. **Handle Errors Gracefully** - provide clear error messages
5. **Document Configuration** - maintain records of discount settings

### After Automatic Discount Creation
1. **Verify Discount Setup** - confirm discounts are configured correctly
2. **Test Customer Experience** - ensure discounts work as expected
3. **Monitor Application** - track discount application and performance
4. **Analyze Results** - evaluate discount effectiveness and impact
5. **Optimize Strategy** - adjust discount strategy based on results

### Ongoing Automatic Discount Management
1. **Regular Performance Reviews** - periodically review discount effectiveness
2. **Condition Logic Optimization** - refine conditions for better performance
3. **Customer Feedback Analysis** - gather and analyze customer feedback
4. **Strategy Refinement** - continuously improve discount strategy
5. **Compliance Monitoring** - ensure discounts comply with regulations

## Performance Optimization

### Condition Evaluation Efficiency
- **Simple Conditions**: Use simple, efficient condition logic
- **Index Optimization**: Structure conditions for efficient evaluation
- **Caching Strategy**: Cache frequently accessed condition data
- **Performance Monitoring**: Monitor condition evaluation performance

### System Performance
- **Query Optimization** - structure mutations for maximum efficiency
- **Resource Management** - manage system resources effectively
- **Rate Limit Management** - monitor and manage API rate limits
- **Load Balancing** - distribute discount processing load

### Customer Experience Optimization
- **Fast Application** - ensure quick discount application at checkout
- **Clear Display** - clearly display applied discounts to customers
- **Mobile Optimization** - optimize for mobile checkout experience
- **Accessibility** - ensure discount functionality is accessible

## Integration Considerations

### Checkout Integration
- **Real-time Application** - ensure fast discount application during checkout
- **Condition Evaluation** - efficient condition logic evaluation
- **Order Processing** - integrate smoothly with order processing
- **Payment Processing** - coordinate with payment processing systems

### Customer Management
- **Segment Updates** - keep customer segments current and accurate
- **Behavior Tracking** - track customer response to automatic discounts
- **Loyalty Integration** - integrate with customer loyalty programs
- **Personalization** - use discount data for personalization

### Inventory Management
- **Stock Coordination** - coordinate automatic discounts with inventory
- **Product Availability** - ensure discounted products are available
- **Supply Chain Impact** - consider supply chain implications
- **Forecasting** - use discount data for inventory forecasting

### Analytics Integration
- **Performance Tracking** - track automatic discount performance metrics
- **ROI Analysis** - calculate return on investment
- **Customer Analytics** - analyze customer behavior with automatic discounts
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
