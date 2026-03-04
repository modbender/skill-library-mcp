# Shopify Order & Draft Order Creation

This guide helps you generate accurate GraphQL mutations for creating orders and draft orders in Shopify.

## Instructions for Mutation Generation

When a user requests to create orders or draft orders, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation

## Official Documentation

### Order Creation Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate

**What to learn from this documentation:**
- Required input fields for order creation
- Optional fields and their data types
- Line item structure and variants
- Customer information handling
- Shipping and tax calculation
- Payment processing options

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate#examples
  - *Review only when you need sample mutation patterns for complex order scenarios*

### Draft Order Creation Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate

**What to learn from this documentation:**
- Required input fields for draft order creation
- Draft order-specific options (like email sending)
- Line item structure for draft orders
- Customer handling in draft orders
- Draft order payment options
- Invoice and checkout settings

**Note**: *Review this documentation only when working specifically with draft orders, not regular orders*

### Additional Order Management Mutations

#### Order Payment Mutations
**Order Manual Payment**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment
- Create manual payments for existing orders
- Handle payment recording and status updates

**Order Invoice Send**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend
- Send invoices to customers for existing orders
- Manage invoice delivery and tracking

**Order Mark As Paid**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderMarkAsPaid
- Mark orders as paid manually
- Handle payment status updates

#### Order Risk & Status Management
**Order Risk Assessment**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderRiskAssessmentCreate
- Create risk assessments for orders
- Fraud detection and prevention

**Order Open**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderOpen
- Reopen closed orders
- Manage order lifecycle

#### Draft Order Management
**Draft Order Invoice Send**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend
- Send invoices for draft orders
- Convert draft orders to active orders

**Draft Order Create From Order**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreateFromOrder
- Create draft orders from existing orders
- Order duplication and modification

**Draft Order Duplicate**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDuplicate
- Duplicate existing draft orders
- Template creation for recurring orders

**Note**: *Review these additional mutation documentations when working with specific order management scenarios beyond basic creation*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating mutations.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Mutation Cost Calculation**:
   - Mutations generally have higher costs than queries
   - Complex input objects increase cost
   - Nested line items and customer data add to cost
   - Formula: `cost = base_mutation_cost + input_complexity`

3. **Best Practices for Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Batch operations**: Create multiple orders in separate mutations if needed
   - **Validate input**: Ensure all required data is provided before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Use draft orders first**: For complex scenarios, consider draft orders then complete

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates order with excessive optional fields
   mutation orderCreate($input: OrderInput!) {
     orderCreate(input: $input) {
       order { id name customer { ... } lineItems { ... } shippingAddress { ... } billingAddress { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates order with essential fields only
   mutation orderCreate($input: OrderInput!) {
     orderCreate(input: $input) {
       order { id name totalPriceSet { shopMoney { amount } } }
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CUSTOMER_ID$` | Customer ID | Ask user if not provided | `gid://shopify/Customer/123456789` |
| `$PRODUCT_VARIANT_ID$` | Product variant ID | Ask user if not provided | `gid://shopify/ProductVariant/987654321` |
| `$QUANTITY$ | Item quantity | 1 | `2` |
| `$EMAIL$ | Customer email | Ask user if not provided | `"customer@example.com"` |
| `$SHIPPING_ADDRESS$ | Shipping address object | Ask user if not provided | Address object |
| `$BILLING_ADDRESS$ | Billing address object | Ask user if not provided | Address object |
| `$SEND_RECEIPT$ | Send email receipt | `false` | `true` |
| `$SEND_INVOICE$ | Send draft invoice | `false` | `true` |

### Mutation Structure Template

```graphql
mutation orderCreate($input: OrderInput!) {
  orderCreate(input: $input) {
    order {
      id
      name
      createdAt
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
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

When generating a mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create a new order for your customer")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the customer's email and what they want to order")
3. **Explain any limitations** in simple terms (e.g., "This creates the order but doesn't process payment")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new [order/draft order] for your business.

**Mutation:**
```graphql
mutation orderCreate($input: OrderInput!) {
  orderCreate(input: $input) {
    order {
      id
      name
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
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
- Creates a new order with the details you provide
- Shows the order number and total amount
- Lets you know if there are any errors
- This keeps the process simple and reliable

To create this order, I'll need:
- Customer email address
- Product details (what they're ordering)
- Shipping address
- Any special instructions?

Would you like to:
- Create a draft order first (easier to modify)?
- Set up automatic email receipt?
- Include tax calculations?
- Add shipping costs?
```

## Common Mutation Patterns

### Pattern 1: Basic Order Creation
```graphql
mutation orderCreate($input: OrderInput!) {
  orderCreate(input: $input) {
    order {
      id
      name
      email
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
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

### Pattern 2: Draft Order Creation
```graphql
mutation draftOrderCreate($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      name
      email
      totalPrice
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

### Pattern 3: Order with Customer Information
```graphql
mutation orderCreate($input: OrderInput!) {
  orderCreate(input: $input) {
    order {
      id
      name
      customer {
        id
        email
        firstName
        lastName
      }
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
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

### Pattern 4: Draft Order with Invoice
```graphql
mutation draftOrderCreate($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      name
      email
      totalPrice
      invoiceUrl
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

## Important Notes

- **Always check the documentation** before generating mutations - field requirements may change
- **Validate required fields** - mutations will fail without required input data
- **Handle user errors** - always check the userErrors field in response
- **Test with simple orders** first before creating complex ones
- **Use draft orders** for complex scenarios that might need modifications
- **Payment processing** - orderCreate doesn't process payments, use payment mutations separately
- **Inventory management** - creating orders affects inventory levels
- **Customer creation** - you can create new customers or use existing ones

## Learning Resources

- **GraphQL Admin API Overview**: https://shopify.dev/docs/api/admin-graphql
  - *Review only when you need general GraphQL API understanding beyond order creation*
- **API Rate Limits**: https://shopify.dev/docs/api/usage/rate-limits
  - *Review only when you encounter rate limiting issues or need optimization guidance*
- **Payment Processing**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate
  - *Review only when you need to handle payment processing with orders*
- **Customer Management**: https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer
  - *Review only when you need to understand customer data structure*
- **Product Variants**: https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant
  - *Review only when you need to understand product variant structure*

## Troubleshooting

If a mutation fails or returns unexpected results:

1. **Check required fields** - ensure all mandatory input fields are provided
2. **Verify customer ID format** - must be full GID (e.g., `gid://shopify/Customer/123`)
3. **Check product variant availability** - variant must exist and be in stock
4. **Review user errors** - the response will explain what went wrong
5. **Validate address format** - shipping/billing addresses must be properly formatted
6. **Check API permissions** - ensure app has required scopes for order creation
7. **Verify currency** - currency must match shop's currency settings

---

**Remember**: The goal is to create accurate, reliable mutations that work correctly while providing exactly what the user needs. When in doubt, consult the official documentation links provided above.

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