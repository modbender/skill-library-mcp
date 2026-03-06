# Shopify Customer & Address Deletion

This guide helps you generate accurate GraphQL mutations for deleting customers and customer addresses in Shopify.

## Instructions for Mutation Generation

When a user requests to delete customers or customer addresses, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Customer Delete Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerDelete

**What to learn from this documentation:**
- Required input fields for customer deletion
- Customer eligibility requirements for deletion
- Order history and data retention implications
- Customer account deletion workflows
- Legal and compliance considerations

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

### Customer Address Delete Mutation Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressDelete

**What to learn from this documentation:**
- Required input fields for address deletion
- Address eligibility requirements for deletion
- Default address handling and reassignment
- Customer address book management
- Order address reference implications

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressDelete#examples
  - *Review only when you need sample mutation patterns for address deletion*

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting customers.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Customer Delete Cost Calculation**:
   - Customer deletion mutations have moderate costs
   - Complex customer deletions with order history may have higher costs
   - Address deletions generally have lower costs
   - Formula: `cost = base_mutation_cost + deletion_complexity`

3. **Best Practices for Customer Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure customer is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest archiving instead of deletion when appropriate
   - **Batch carefully**: Delete multiple customers in separate mutations to avoid complexity

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes customer with excessive return fields
   mutation customerDelete($input: CustomerDeleteInput!) {
     customerDelete(input: $input) {
       deletedCustomerId
       customer { id email orders { ... } addresses { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes customer with essential fields only
   mutation customerDelete($input: CustomerDeleteInput!) {
     customerDelete(input: $input) {
       deletedCustomerId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating customer delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CUSTOMER_ID$` | Customer ID to delete | Ask user if not provided | `gid://shopify/Customer/123456789` |
| `$ADDRESS_ID$` | Address ID to delete | Ask user if not provided | `gid://shopify/MailingAddress/987654321` |
| `$DELETE_REASON$` | Reason for deletion | `"CUSTOMER_REQUEST"` | `"DATA_CLEANUP"` |

### Mutation Structure Templates

#### Customer Delete Template
```graphql
mutation customerDelete($input: CustomerDeleteInput!) {
  customerDelete(input: $input) {
    deletedCustomerId
    userErrors {
      field
      message
    }
  }
}
```

#### Customer Address Delete Template
```graphql
mutation customerAddressDelete($customerId: ID!, $addressId: ID!) {
  customerAddressDelete(customerId: $customerId, addressId: $addressId) {
    deletedCustomerAddressId
    customer {
      id
      email
      addresses {
        id
        address1
        city
        province
        country
        zip
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

When generating a customer delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the customer account from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all customer data will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the customer ID or email address")
4. **Explain any limitations** in simple terms (e.g., "Only certain customers can be deleted - others must be archived")
5. **Suggest alternatives** when appropriate (e.g., "Consider archiving instead of deleting to preserve order history")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete a customer from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the customer account and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation customerDelete($input: CustomerDeleteInput!) {
  customerDelete(input: $input) {
    deletedCustomerId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes a customer account from your Shopify store.

**What I need from you:**
- The customer ID or email address you want to delete

**Important consequences:**
- All customer data will be permanently erased
- Order history may be affected or anonymized
- Customer will lose access to their account
- This action cannot be reversed

**Alternative to consider:**
Instead of deleting, you could archive the customer to preserve their order history for your records.

**Are you sure you want to proceed with permanent deletion?**
```

## Common Deletion Scenarios

### Customer Account Deletion
- **Use**: `customerDelete` mutation
- **Eligibility**: Only certain customers can be deleted (typically those without active orders or payment issues)
- **Considerations**: Order history preservation, legal requirements, customer communication

### Customer Address Deletion
- **Use**: `customerAddressDelete` mutation
- **Eligibility**: Most customer addresses can be deleted except default addresses or those referenced in orders
- **Considerations**: Default address reassignment, order address references, customer convenience

### Data Cleanup Operations
- **Use**: Customer and address deletion mutations
- **Use case**: Removing test data, duplicate accounts, outdated information
- **Considerations**: Data integrity, compliance requirements, backup needs

### Privacy Request Compliance
- **Use**: `customerDelete` mutation
- **Use case**: GDPR/CCPA data deletion requests
- **Considerations**: Legal compliance, documentation, verification of identity

### Account Management
- **Use**: Customer deletion or archiving
- **Use case**: Customer requests account closure, inactive account cleanup
- **Considerations**: Customer satisfaction, data retention policies, alternative solutions

## Deletion Limitations

### Customer Deletion Restrictions
- **Active orders**: Customers with recent or active orders may not be deletable
- **Payment processing**: Customers with pending payments may be protected
- **Legal requirements**: Some jurisdictions require data retention for specific periods
- **Store policies**: Individual stores may have additional deletion restrictions

### Address Deletion Restrictions
- **Default addresses**: Cannot delete default addresses without setting a new default
- **Order references**: Addresses used in orders cannot be deleted
- **Active subscriptions**: Addresses used for recurring orders may be protected
- **Multiple address requirements**: Some business models require minimum address counts

## Safety Precautions

### Before Deleting Customers
1. **Verify customer eligibility** - not all customers can be deleted
2. **Check legal requirements** - ensure compliance with data retention laws
3. **Consider business impact** - understand how deletion affects analytics and reporting
4. **Backup critical data** - preserve information needed for business operations
5. **Communicate with customer** - inform about account closure if applicable

### Before Deleting Addresses
1. **Verify address ownership** - ensure address belongs to specified customer
2. **Check default status** - verify address is not the customer's default
3. **Review order references** - ensure address is not used in active orders
4. **Consider customer impact** - understand how address removal affects customer experience
5. **Plan for replacement** - ensure customer has alternative addresses if needed

### After Deletion Operations
1. **Verify deletion success** - confirm customer or address was removed
2. **Check related data** - ensure orders, subscriptions, and other records are handled properly
3. **Update integrations** - sync changes with other systems if needed
4. **Document actions** - maintain audit trail for compliance and business purposes
5. **Monitor for issues** - watch for unexpected consequences or system errors

## Error Handling

### Common Customer Delete Errors
- **Customer not found**: Verify customer ID or email address
- **Customer not eligible**: Check order status, payment processing, or legal restrictions
- **Permission denied**: Verify API access and customer ownership
- **Legal compliance**: Check data retention requirements for your jurisdiction

### Common Address Delete Errors
- **Address not found**: Verify address ID belongs to customer
- **Default address**: Cannot delete default address without replacement
- **Order reference**: Address is used in existing orders
- **Permission denied**: Verify API access and address ownership

### Best Practices for Error Resolution
1. **Provide clear explanations** - explain what went wrong in business terms
2. **Offer alternatives** - suggest archiving, updating, or other solutions
3. **Guide next steps** - provide clear instructions for resolution
4. **Maintain professionalism** - handle errors calmly and helpfully
5. **Document issues** - track recurring problems for system improvements

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
