# Shopify Code Discount Creation & Management

This guide helps you generate accurate GraphQL mutations for creating code discounts and managing code discount data in Shopify.

## Instructions for Mutation Generation

When a user requests to create code discounts or manage code discount data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific code discount creation requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider discount strategy impact** - understand how new discounts affect pricing and promotions

## Official Documentation

### Primary Code Discount Creation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate

**What to learn from this documentation:**
- Required input fields for code discount creation
- Code discount data structure and validation
- Discount configuration options and rules
- Customer eligibility and targeting settings
- Code generation and management

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate#examples
  - *Review only when you need sample mutation patterns for complex discount scenarios*

### Code Discount Management Mutations Documentation

#### Basic Code Discount Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate

**What to learn from this documentation:**
- Simple percentage and fixed amount discount creation
- Basic discount configuration options
- Code generation and validation
- Usage limit management

#### Buy X Get Y Code Discount Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBxgyCreate

**What to learn from this documentation:**
- Buy X Get Y discount configuration
- Product selection and bundling rules
- Quantity requirements and conditions
- Application logic and customer experience

#### Free Shipping Code Discount Creation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeFreeShippingCreate

**What to learn from this documentation:**
- Free shipping discount configuration
- Shipping method and destination rules
- Minimum purchase requirements
- Geographic and carrier restrictions

#### Code Discount Activation Management
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeActivate

**What to learn from this documentation:**
- Code discount activation workflows
- Status management and scheduling
- Bulk activation operations
- Activation timing and coordination

#### Bulk Code Discount Operations
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkActivate

**What to learn from this documentation:**
- Bulk code discount activation workflows
- Multiple discount management
- Efficiency considerations for bulk operations
- Error handling for bulk operations

#### Code Redemption Management
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountRedeemCodeBulkAdd

**What to learn from this documentation:**
- Code redemption and usage management
- Bulk code redemption workflows
- Customer assignment and usage tracking
- Redemption analytics and reporting

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating code discounts.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Code Discount Creation Cost Calculation**:
   - Code discount creation mutations have moderate to high costs
   - Complex discount rules and conditions increase cost significantly
   - Bulk operations have higher costs but are more efficient than individual operations
   - Formula: `cost = base_mutation_cost + discount_complexity + condition_logic + customer_targeting`

3. **Best Practices for Code Discount Creation Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate discount logic**: Ensure discount rules make business sense
   - **Use bulk operations**: Create multiple codes in single mutations when possible
   - **Test discount logic**: Validate discount behavior before activation
   - **Consider customer experience**: Design codes for easy customer use

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates discount with excessive configuration
   mutation discountCodeAppCreate($input: DiscountCodeAppInput!) {
     discountCodeAppCreate(input: $input) {
       discount { id title codes { edges { node { ... } } } 
       customerSelection { ... } discountClass { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates discount with essential fields only
   mutation discountCodeAppCreate($input: DiscountCodeAppInput!) {
     discountCodeAppCreate(input: $input) {
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

## Mutation Generation Rules

### Variable Placeholders

When generating code discount creation mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_TITLE$` | Discount title | Ask user if not provided | `"Summer Sale"` |
| `$DISCOUNT_CODE$` | Discount code string | Ask user if not provided | `"SUMMER2024"` |
| `$DISCOUNT_TYPE$` | Discount type | `"PERCENTAGE"` or `"FIXED_AMOUNT"` | `"PERCENTAGE"` |
| `$DISCOUNT_VALUE$` | Discount value | Ask user if not provided | `15.0` |
| `$STARTS_AT$` | Discount start date | Ask user if not provided | `"2024-06-01T00:00:00Z"` |
| `$ENDS_AT$` | Discount end date | Ask user if not provided | `"2024-08-31T23:59:59Z"` |
| `$MINIMUM_AMOUNT$` | Minimum purchase amount | Ask user if not provided | `50.00` |
| `$MINIMUM_QUANTITY$` | Minimum purchase quantity | Ask user if not provided | `2` |
| `$USAGE_LIMIT$` | Total usage limit | Ask user if not provided | `1000` |
| `$USAGE_LIMIT_PER_CUSTOMER$` | Usage limit per customer | Ask user if not provided | `5` |
| `$PRODUCT_IDS$` | Product IDs for discount | Ask user if not provided | `[gid://shopify/Product/123456789]` |
| `$COLLECTION_IDS$` | Collection IDs for discount | Ask user if not provided | `[gid://shopify/Collection/987654321]` |
| `$CUSTOMER_SEGMENT_IDS$` | Customer segment IDs | Ask user if not provided | `[gid://shopify/CustomerSegment/456789123]` |
| `$DISCOUNT_IDS$` | Discount IDs for bulk operations | Ask user if not provided | `[gid://shopify/DiscountNode/789123456]` |
| `$REDEEM_CODE$` | Code to redeem | Ask user if not provided | `"REDEEM2024"` |

### Mutation Structure Templates

#### Basic Code Discount Creation Template
```graphql
mutation discountCodeBasicCreate($input: DiscountCodeBasicInput!) {
  discountCodeBasicCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### Buy X Get Y Code Discount Creation Template
```graphql
mutation discountCodeBxgyCreate($input: DiscountCodeBxgyInput!) {
  discountCodeBxgyCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### Free Shipping Code Discount Creation Template
```graphql
mutation discountCodeFreeShippingCreate($input: DiscountCodeFreeShippingInput!) {
  discountCodeFreeShippingCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### App-Based Code Discount Creation Template
```graphql
mutation discountCodeAppCreate($input: DiscountCodeAppInput!) {
  discountCodeAppCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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

#### Code Discount Activation Template
```graphql
mutation discountCodeActivate($id: ID!) {
  discountCodeActivate(id: $id) {
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

#### Bulk Code Discount Activation Template
```graphql
mutation discountCodeBulkActivate($discountIds: [ID!]!) {
  discountCodeBulkActivate(discountIds: $discountIds) {
    discounts {
      id
      title
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Code Redemption Bulk Add Template
```graphql
mutation discountRedeemCodeBulkAdd($code: String!, $customerIds: [ID!]!) {
  discountRedeemCodeBulkAdd(code: $code, customerIds: $customerIds) {
    discountCodeRedeemCodes {
      id
      code
      customerId
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a code discount creation mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create a new discount code for your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the discount title, code, and discount amount")
3. **Explain any limitations** in simple terms (e.g., "This creates the discount but you'll need to activate it before customers can use it")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new discount code for your store.

**Mutation:**
```graphql
mutation discountCodeBasicCreate($input: DiscountCodeBasicInput!) {
  discountCodeBasicCreate(input: $input) {
    discount {
      id
      title
      status
      startsAt
      endsAt
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
This creates a new discount code that customers can use at checkout.

**What I need from you:**
- Discount title and code (e.g., "Summer Sale" and "SUMMER2024")
- Discount type and amount (percentage or fixed amount)
- When the discount should start and end
- Any usage limits or customer restrictions

**Important notes:**
- The discount will be created but may need to be activated
- You can set usage limits to control how many times the code can be used
- Consider who should be able to use the discount (all customers or specific groups)

Would you like me to help you create a specific discount code?
```

## Common Code Discount Creation Scenarios

### Percentage Discount Creation
- **Use**: `discountCodeBasicCreate` mutation
- **Use case**: Percentage-based promotions, seasonal sales
- **Considerations**: Margin impact, customer appeal, competitive positioning

### Fixed Amount Discount Creation
- **Use**: `discountCodeBasicCreate` mutation
- **Use case**: Fixed amount promotions, specific value incentives
- **Considerations**: Currency handling, average order value impact

### Buy X Get Y Discount Creation
- **Use**: `discountCodeBxgyCreate` mutation
- **Use case**: Product bundling, cross-selling, inventory management
- **Considerations**: Product selection, inventory coordination, customer experience

### Free Shipping Discount Creation
- **Use**: `discountCodeFreeShippingCreate` mutation
- **Use case**: Shipping cost incentives, cart value optimization
- **Considerations**: Shipping costs, geographic limitations, profit margins

### Customer Segment-Specific Discounts
- **Use**: Any code discount creation mutation with customer targeting
- **Use case**: VIP pricing, wholesale pricing, loyalty programs
- **Considerations**: Segment management, customer classification, privacy

## Code Discount Configuration Options

### Discount Value Types
- **Percentage**: Percentage off total cart or specific items
- **Fixed Amount**: Fixed monetary amount off total cart or specific items
- **Free Shipping**: Free or discounted shipping
- **Custom**: App-specific discount logic

### Usage Limits and Restrictions
- **Total Usage Limit**: Maximum number of times code can be used
- **Per Customer Limit**: Maximum uses per individual customer
- **Time-Based Limits**: Usage restrictions by time period
- **Product-Specific Limits**: Usage restrictions for specific products

### Customer Targeting Options
- **All Customers**: Available to all store customers
- **Customer Segments**: Specific customer groups (VIP, wholesale, etc.)
- **Saved Searches**: Dynamic customer groups based on criteria
- **Individual Customers**: Specific customer assignments

### Product and Collection Targeting
- **All Products**: Discount applies to all products
- **Specific Products**: Discount applies to selected products
- **Collections**: Discount applies to entire collections
- **Product Variants**: Discount applies to specific variants

## Code Generation Strategies

### Sequential Code Generation
- **Pattern**: SUMMER001, SUMMER002, etc.
- **Benefits**: Easy tracking, organized management
- **Considerations**: Predictability, security concerns
- **Use Case**: Campaign management, bulk code creation

### Random Code Generation
- **Pattern**: Random alphanumeric strings
- **Benefits**: Security, uniqueness, unpredictability
- **Considerations**: Customer memorability, distribution challenges
- **Use Case**: Security-sensitive promotions, unique offers

### Descriptive Code Generation
- **Pattern**: SUMMER24, WELCOME10, etc.
- **Benefits**: Customer memorability, marketing value
- **Considerations**: Predictability, potential for guessing
- **Use Case**: Customer-facing promotions, marketing campaigns

### Campaign-Specific Codes
- **Pattern**: BLACKFRIDAY2024, etc.
- **Benefits**: Brand alignment, campaign recognition
- **Considerations**: Seasonal relevance, timing coordination
- **Use Case**: Seasonal promotions, event-based marketing

## Discount Strategy Considerations

### Margin Impact Analysis
- **Cost Calculation**: Calculate discount impact on profit margins
- **Break-Even Analysis**: Determine break-even points for discount usage
- **Customer Lifetime Value**: Consider long-term customer value impact
- **Competitive Positioning**: Analyze discount strategy vs competitors

### Customer Behavior Impact
- **Purchase Patterns**: How discounts affect customer purchasing behavior
- **Average Order Value**: Impact on customer spending patterns
- **Customer Acquisition**: Effect on new customer acquisition
- **Customer Retention**: Impact on customer loyalty and repeat purchases

### Inventory Management
- **Stock Coordination**: Coordinate discounts with inventory levels
- **Seasonal Planning**: Align discounts with seasonal inventory needs
- **Product Lifecycle**: Use discounts to manage product lifecycle
- **Supply Chain Impact**: Consider supply chain implications

### Marketing Integration
- **Campaign Coordination**: Align discounts with marketing campaigns
- **Channel Distribution**: Distribute codes through appropriate channels
- **Customer Communication**: Plan customer communication strategy
- **Performance Tracking**: Track discount performance and ROI

## Error Handling

### Common Code Discount Creation Errors
- **Invalid Discount Values**: Discount values must be within valid ranges
- **Duplicate Codes**: Discount codes must be unique
- **Invalid Date Ranges**: Start and end dates must be valid
- **Permission Issues**: Verify API access for discount creation

### Configuration Validation Errors
- **Invalid Product Selection**: Products must exist and be accessible
- **Customer Segment Issues**: Customer segments must be valid
- **Usage Limit Conflicts**: Usage limits must be logically consistent
- **Currency Issues**: Currency values must be valid for store

### Bulk Operation Errors
- **Partial Success**: Some operations may succeed while others fail
- **Rate Limiting**: Bulk operations may hit rate limits
- **Validation Failures**: Individual items may fail validation
- **System Constraints**: System limitations may affect bulk operations

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest different discount configurations
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Validate Input** - ensure all required data is provided and valid
5. **Monitor Performance** - track discount creation success rates

## Best Practices

### Before Creating Code Discounts
1. **Plan Discount Strategy** - define clear business objectives
2. **Calculate Margin Impact** - understand financial implications
3. **Define Target Audience** - identify who should receive discounts
4. **Set Usage Limits** - establish appropriate usage restrictions
5. **Plan Distribution** - determine how codes will be distributed

### During Code Discount Creation
1. **Validate Input Data** - ensure all required fields are valid
2. **Test Discount Logic** - verify discount behavior before activation
3. **Monitor Creation Success** - track successful discount creation
4. **Handle Errors Gracefully** - provide clear error messages
5. **Document Discounts** - maintain records of discount configurations

### After Code Discount Creation
1. **Verify Discount Setup** - confirm discounts are configured correctly
2. **Test Customer Experience** - ensure discounts work as expected
3. **Monitor Usage** - track discount usage and performance
4. **Analyze Results** - evaluate discount effectiveness
5. **Optimize Strategy** - adjust discount strategy based on results

### Ongoing Discount Management
1. **Regular Reviews** - periodically review discount performance
2. **Usage Monitoring** - track discount usage patterns
3. **Customer Feedback** - gather feedback on discount effectiveness
4. **Strategy Optimization** - continuously improve discount strategy
5. **Compliance Monitoring** - ensure discounts comply with regulations

## Performance Optimization

### Creation Efficiency
- **Batch Operations** - create multiple codes in single operations
- **Template Reuse** - use consistent templates for similar discounts
- **Input Validation** - validate input data before mutation
- **Error Handling** - implement efficient error handling

### System Performance
- **Rate Limit Management** - monitor and manage API rate limits
- **Caching Strategy** - cache frequently accessed discount data
- **Query Optimization** - structure mutations for maximum efficiency
- **Resource Management** - manage system resources effectively

### Customer Experience
- **Fast Validation** - ensure quick code validation at checkout
- **Clear Error Messages** - provide helpful error messages to customers
- **Mobile Optimization** - optimize code entry for mobile devices
- **Accessibility** - ensure discount functionality is accessible

## Integration Considerations

### Marketing Platforms
- **Email Integration** - sync codes with email marketing platforms
- **Social Media** - distribute codes through social channels
- **Affiliate Programs** - track affiliate-generated code usage
- **Influencer Marketing** - manage influencer-specific codes

### Customer Management
- **CRM Integration** - sync discount usage with customer data
- **Loyalty Programs** - integrate with customer loyalty systems
- **Customer Segmentation** - maintain accurate customer segments
- **Personalization** - use discount data for personalization

### Analytics and Reporting
- **Performance Tracking** - track discount performance metrics
- **ROI Analysis** - calculate return on investment for discounts
- **Customer Analytics** - analyze customer behavior with discounts
- **Business Intelligence** - integrate with BI tools for analysis

### Third-Party Applications
- **App Integration** - coordinate with Shopify apps for advanced features
- **API Consistency** - maintain consistent API usage across systems
- **Data Synchronization** - ensure discount data is synchronized
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
