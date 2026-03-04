# Shopify Order & Draft Order Deletion

This guide helps you generate accurate GraphQL mutations for deleting orders and draft orders in Shopify.

## Instructions for Mutation Generation

When a user requests to delete orders or draft orders, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Order Delete Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderDelete

**What to learn from this documentation:**
- Required input fields for order deletion
- Order eligibility requirements for deletion
- Cancellation and refund implications
- Inventory restoration behavior
- Customer notification handling

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

### Draft Order Delete Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDelete

**What to learn from this documentation:**
- Required input fields for draft order deletion
- Draft order eligibility requirements
- Inventory reservation handling
- Customer communication implications

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDelete#examples
  - *Review only when you need sample mutation patterns for draft order deletion*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting orders.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Delete Mutation Cost Calculation**:
   - Delete mutations generally have moderate costs
   - Complex order deletions may have higher costs due to inventory adjustments
   - Formula: `cost = base_mutation_cost + deletion_complexity`

3. **Best Practices for Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure order is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest cancellation instead of deletion when appropriate
   - **Batch carefully**: Delete multiple orders in separate mutations to avoid complexity

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes order with excessive return fields
   mutation orderDelete($input: OrderDeleteInput!) {
     orderDelete(input: $input) {
       deletedOrderId
       order { id name customer { ... } lineItems { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes order with essential fields only
   mutation orderDelete($input: OrderDeleteInput!) {
     orderDelete(input: $input) {
       deletedOrderId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$ORDER_ID$` | Order ID to delete | Ask user if not provided | `gid://shopify/Order/123456789` |
| `$DRAFT_ORDER_ID$` | Draft Order ID to delete | Ask user if not provided | `gid://shopify/DraftOrder/987654321` |
| `$CANCEL_REASON$` | Reason for cancellation/deletion | `"CUSTOMER_REQUEST"` | `"FRAUD"` |

### Mutation Structure Templates

#### Order Delete Template
```graphql
mutation orderDelete($input: OrderDeleteInput!) {
  orderDelete(input: $input) {
    deletedOrderId
    userErrors {
      field
      message
    }
  }
}
```

#### Draft Order Delete Template
```graphql
mutation draftOrderDelete($input: DraftOrderDeleteInput!) {
  draftOrderDelete(input: $input) {
    deletedDraftOrderId
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the order from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all order data will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the order number you want to delete")
4. **Explain any limitations** in simple terms (e.g., "Only certain orders can be deleted - others must be cancelled")
5. **Suggest alternatives** when appropriate (e.g., "Consider cancelling instead of deleting to preserve order history")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete an order from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the order and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation orderDelete($input: OrderDeleteInput!) {
  orderDelete(input: $input) {
    deletedOrderId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes an order from your Shopify store.

**What I need from you:**
- The order number or ID you want to delete

**Important consequences:**
- All order data will be permanently erased
- Inventory will be restored (if applicable)
- Customer may lose access to order information
- This action cannot be reversed

**Alternative to consider:**
Instead of deleting, you could cancel the order to preserve the order history for your records.

**Are you sure you want to proceed with permanent deletion?**
```

## Common Deletion Scenarios

### Order Deletion
- **Use**: `orderDelete` mutation
- **Eligibility**: Only certain orders can be deleted (typically test orders or those with specific status)
- **Considerations**: Inventory restoration, customer data removal, financial record impact

### Draft Order Deletion
- **Use**: `draftOrderDelete` mutation
- **Eligibility**: Most draft orders can be deleted
- **Considerations**: Inventory reservation release, customer communication

### When to Delete vs Cancel
- **Delete**: For test orders, duplicate orders, or completely invalid orders
- **Cancel**: For customer-requested cancellations, inventory issues, or payment problems

### Deletion Limitations
- **Fulfilled orders**: Cannot be deleted, must be cancelled or returned
- **Paid orders**: May have restrictions on deletion
- **Orders with financial transactions**: May require cancellation instead

## Safety Precautions

### Before Deleting
1. **Verify order eligibility** - not all orders can be deleted
2. **Check financial impact** - ensure no payment processing issues
3. **Consider customer impact** - inform customers if necessary
4. **Backup data** - ensure you have records if needed
5. **Review alternatives** - consider cancellation or archiving

### After Deletion
1. **Verify inventory restoration** - ensure stock levels are correct
2. **Check customer accounts** - verify customer access is appropriate
3. **Review financial records** - ensure accounting is accurate
4. **Monitor for issues** - watch for any unexpected consequences

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
