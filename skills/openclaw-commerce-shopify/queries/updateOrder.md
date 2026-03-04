# Shopify Order Update & Edit Operations

This guide helps you generate accurate GraphQL mutations for updating and modifying existing orders in Shopify.

## Instructions for Mutation Generation

When a user requests to update orders or modify order details, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation

## Official Documentation

### Primary Order Update Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderUpdate

**What to learn from this documentation:**
- Required input fields for order updates
- Optional fields and their data types
- Order status and property updates
- Customer information modifications
- Shipping and billing address updates
- Payment processing updates

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderUpdate#examples
  - *Review only when you need sample mutation patterns for complex update scenarios*

### Order Edit Operations Documentation

#### Order Edit Management
**Order Edit Update Shipping Line**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditUpdateShippingLine
- Update shipping lines for existing orders
- Modify shipping costs and methods

**Order Edit Update Discount**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditUpdateDiscount
- Update discount information for orders
- Modify discount codes and amounts

**Order Edit Set Quantity**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditSetQuantity
- Update quantities for existing line items
- Handle inventory adjustments

#### Order Edit Removal Operations
**Order Edit Remove Shipping Line**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveShippingLine
- Remove shipping lines from orders
- Handle shipping charge removals

**Order Edit Remove Line Item Discount**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveLineItemDiscount
- Remove discounts from specific line items
- Handle discount reversals

**Order Edit Remove Discount**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveDiscount
- Remove order-level discounts
- Handle discount code removal

#### Order Edit Addition Operations
**Order Edit Add Variant**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddVariant
- Add product variants to existing orders
- Handle new line item additions

**Order Edit Add Shipping Line**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddShippingLine
- Add new shipping lines to orders
- Handle additional shipping methods

**Order Edit Add Line Item Discount**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddLineItemDiscount
- Add discounts to specific line items
- Handle targeted discount applications

**Order Edit Add Custom Item**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddCustomItem
- Add custom items to orders
- Handle non-product line items

#### Draft Order Update Operations
**Draft Order Update**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderUpdate
- Update existing draft orders
- Modify draft order properties and line items
- Handle draft order completion and invoicing

**Note**: *Review these order edit mutation documentations when working with specific order modification scenarios beyond basic updates*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating orders.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Update Mutation Cost Calculation**:
   - Update mutations generally have moderate costs
   - Complex edit operations increase cost
   - Nested line item modifications add to cost
   - Formula: `cost = base_mutation_cost + input_complexity`

3. **Best Practices for Update Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Use specific edit mutations**: Prefer targeted edit mutations over full order updates
   - **Validate input**: Ensure all required data is provided before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Batch updates**: Group related changes in single mutations when possible

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates order with excessive optional fields
   mutation orderUpdate($input: OrderInput!) {
     orderUpdate(input: $input) {
       order { id name customer { ... } lineItems { ... } shippingAddress { ... } billingAddress { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates order with essential fields only
   mutation orderUpdate($input: OrderInput!) {
     orderUpdate(input: $input) {
       order { id name totalPriceSet { shopMoney { amount } } }
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$ORDER_ID$` | Order ID | Ask user if not provided | `gid://shopify/Order/123456789` |
| `$CUSTOMER_ID$` | Customer ID | Ask user if not provided | `gid://shopify/Customer/987654321` |
| `$PRODUCT_VARIANT_ID$` | Product variant ID | Ask user if not provided | `gid://shopify/ProductVariant/456789123` |
| `$QUANTITY$ | Updated quantity | 1 | `3` |
| `$EMAIL$ | Updated customer email | Ask user if not provided | `"updated@example.com"` |
| `$SHIPPING_ADDRESS$ | Updated shipping address object | Ask user if not provided | Address object |
| `$BILLING_ADDRESS$ | Updated billing address object | Ask user if not provided | Address object |
| `$DISCOUNT_CODE$ | Discount code | Ask user if not provided | `"SAVE10"` |
| `$SHIPPING_LINE$ | Shipping line object | Ask user if not provided | Shipping line object |
| `$EDIT_ID$` | Order edit ID | Ask user if not provided | `gid://shopify/OrderEdit/987654321` |

### Mutation Structure Templates

#### Basic Order Update Template
```graphql
mutation orderUpdate($input: OrderInput!) {
  orderUpdate(input: $input) {
    order {
      id
      name
      updatedAt
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

#### Order Edit Add Variant Template
```graphql
mutation orderEditAddVariant($orderEditId: ID!, $lineItem: OrderEditLineItemInput!) {
  orderEditAddVariant(orderEditId: $orderEditId, lineItem: $lineItem) {
    orderEdit {
      id
      addedLineItems {
        id
        quantity
        variant {
          id
          title
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

When generating an update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the shipping address for your customer's order")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the order number and the new shipping address")
3. **Explain any limitations** in simple terms (e.g., "This updates the order but may affect inventory")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update your existing order.

**Mutation:**
```graphql
mutation orderUpdate($input: OrderInput!) {
  orderUpdate(input: $input) {
    order {
      id
      name
      updatedAt
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
This updates an existing order in your store with new information.

**What I need from you:**
- The order number or ID you want to update
- What specific information you want to change (shipping address, customer info, etc.)

**Important notes:**
- This will modify the existing order
- Some changes may affect inventory or billing
- The customer may receive notifications about the update

Would you like me to help you update a specific order?
```

## Common Update Scenarios

### Customer Information Updates
- **Use**: `orderUpdate` mutation
- **Fields**: Customer email, phone, notes
- **Considerations**: Customer communication preferences

### Shipping Address Updates
- **Use**: `orderUpdate` mutation
- **Fields**: Complete shipping address
- **Considerations**: May affect shipping costs and delivery

### Order Item Modifications
- **Use**: Order edit mutations (`orderEditAddVariant`, `orderEditSetQuantity`)
- **Fields**: Line items, quantities, variants
- **Considerations**: Inventory impact and pricing changes

### Discount Updates
- **Use**: `orderEditUpdateDiscount` or `orderEditAddLineItemDiscount`
- **Fields**: Discount codes, amounts, applications
- **Considerations**: Order total and customer notifications

### Shipping Line Updates
- **Use**: `orderEditUpdateShippingLine` or `orderEditAddShippingLine`
- **Fields**: Shipping methods, costs, carriers
- **Considerations**: Delivery timelines and customer charges

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
