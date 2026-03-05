# Shopify Customer Update & Management

This guide helps you generate accurate GraphQL mutations for updating and managing existing customers in Shopify.

## Instructions for Mutation Generation

When a user requests to update customers or modify customer information, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific customer update requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider data consistency** - ensure updates don't break customer relationships

## Official Documentation

### Primary Customer Update Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdate

**What to learn from this documentation:**
- Required input fields for customer updates
- Customer data modification options
- Address and contact information updates
- Email marketing preference changes
- Customer tags and metafields management
- Password and account security updates

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdate#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdate#return-fields
  - *Review only when you need to verify what data is returned after update*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdate#examples
  - *Review only when you need sample mutation patterns for complex customer update scenarios*

### Order Customer Assignment Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCustomerSet

**What to learn from this documentation:**
- Assigning customers to existing orders
- Customer order relationship management
- Order ownership transfer
- Customer data synchronization with orders

### Customer Default Address Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdateDefaultAddress

**What to learn from this documentation:**
- Default address management for customers
- Address validation and formatting
- Shipping and billing address preferences
- Multi-address customer handling

### Customer Address Update Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressUpdate

**What to learn from this documentation:**
- Update existing customer addresses
- Address modification and validation
- Address ID management
- Customer address book maintenance

### Customer Merge Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerMerge

**What to learn from this documentation:**
- Merge duplicate customer accounts
- Customer data consolidation
- Order history merging
- Customer record cleanup

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when updating customers.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Customer Update Cost Calculation**:
   - Customer update mutations have moderate costs
   - Complex updates with addresses and metafields increase cost
   - Order customer assignment may have higher costs due to order modifications
   - Formula: `cost = base_mutation_cost + update_complexity`

3. **Best Practices for Customer Update Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate customer ID**: Ensure customer exists before updating
   - **Handle address updates carefully**: Validate address format and completeness
   - **Consider order impact**: Understand how customer updates affect existing orders
   - **Batch related updates**: Group multiple customer changes in single mutations when possible

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Updates customer with excessive optional fields
   mutation customerUpdate($input: CustomerInput!) {
     customerUpdate(input: $input) {
       customer { id email firstName lastName phone addresses { ... } orders { ... } tags metafields { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Updates customer with essential fields only
   mutation customerUpdate($input: CustomerInput!) {
     customerUpdate(input: $input) {
       customer { id email firstName lastName phone }
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating customer update mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CUSTOMER_ID$` | Customer ID to update | Ask user if not provided | `gid://shopify/Customer/123456789` |
| `$EMAIL$` | Updated customer email | Ask user if not provided | `"updated@example.com"` |
| `$FIRST_NAME$` | Updated customer first name | Ask user if not provided | `"John"` |
| `$LAST_NAME$` | Updated customer last name | Ask user if not provided | `"Doe"` |
| `$PHONE$` | Updated customer phone | Ask user if not provided | `"+1234567890"` |
| `$ACCEPTS_MARKETING$` | Updated email marketing consent | Ask user if not provided | `true` |
| `$TAGS$` | Updated customer tags | Ask user if not provided | `["VIP", "premium"]` |
| `$ADDRESS_ID$` | Address ID for default address | Ask user if not provided | `gid://shopify/MailingAddress/987654321` |
| `$ORDER_ID$` | Order ID for customer assignment | Ask user if not provided | `gid://shopify/Order/456789123` |
| `$ADDRESS1$` | Updated address line 1 | Ask user if not provided | `"123 Main St"` |
| `$CITY$` | Updated city | Ask user if not provided | `"New York"` |
| `$PROVINCE$` | Updated state/Province | Ask user if not provided | `"NY"` |
| `$COUNTRY$` | Updated country | Ask user if not provided | `"United States"` |
| `$ZIP$` | Updated postal code | Ask user if not provided | `"10001"` |

### Mutation Structure Templates

#### Customer Update Template
```graphql
mutation customerUpdate($input: CustomerInput!) {
  customerUpdate(input: $input) {
    customer {
      id
      email
      firstName
      lastName
      phone
      createdAt
      updatedAt
      tags
      acceptsMarketing
      state
      addresses {
        id
        address1
        address2
        city
        province
        country
        zip
        phone
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Order Customer Assignment Template
```graphql
mutation orderCustomerSet($orderId: ID!, $customerId: ID!) {
  orderCustomerSet(orderId: $orderId, customerId: $customerId) {
    order {
      id
      name
      customer {
        id
        email
        firstName
        lastName
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Default Address Update Template
```graphql
mutation customerUpdateDefaultAddress($customerId: ID!, $addressId: ID!) {
  customerUpdateDefaultAddress(customerId: $customerId, addressId: $addressId) {
    customer {
      id
      email
      defaultAddress {
        id
        address1
        address2
        city
        province
        country
        zip
        phone
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Customer Address Update Template
```graphql
mutation customerAddressUpdate($customerId: ID!, $addressId: ID!, $address: MailingAddressInput!) {
  customerAddressUpdate(customerId: $customerId, addressId: $addressId, address: $address) {
    customerAddress {
      id
      address1
      address2
      city
      province
      country
      zip
      phone
    }
    customer {
      id
      email
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Customer Merge Template
```graphql
mutation customerMerge($sourceCustomerId: ID!, $destinationCustomerId: ID!) {
  customerMerge(sourceCustomerId: $sourceCustomerId, destinationCustomerId: $destinationCustomerId) {
    customer {
      id
      email
      firstName
      lastName
      phone
      createdAt
      updatedAt
      tags
      acceptsMarketing
      state
      ordersCount
    }
    mergedCustomers {
      id
      email
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a customer update mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will update the customer's contact information in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the customer's ID and what information you want to change")
3. **Explain any limitations** in simple terms (e.g., "This will update the customer's information but may affect their existing orders")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you update an existing customer's information in your store.

**Mutation:**
```graphql
mutation customerUpdate($input: CustomerInput!) {
  customerUpdate(input: $input) {
    customer {
      id
      email
      firstName
      lastName
      phone
      updatedAt
      tags
      acceptsMarketing
      state
    }
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This updates an existing customer's information in your Shopify store.

**What I need from you:**
- The customer's ID or email address
- What specific information you want to update (name, email, phone, etc.)
- Any new tags you want to apply

**Important notes:**
- This will modify the customer's existing information
- Changes may affect their order history and communications
- The customer may receive notifications about certain updates

Would you like me to help you update a specific customer?
```

## Common Customer Update Scenarios

### Basic Customer Information Updates
- **Use**: `customerUpdate` mutation
- **Fields**: Email, name, phone, marketing preferences
- **Considerations**: Email validation, duplicate checking, notification preferences

### Customer Address Updates
- **Use**: `customerUpdate` mutation with address input
- **Fields**: Complete address information, default address setting
- **Considerations**: Address validation, shipping implications, tax calculations

### Customer Tag Management
- **Use**: `customerUpdate` mutation with tags
- **Use case**: Customer segmentation, VIP status, wholesale classification
- **Considerations**: Tag consistency, automated tagging rules

### Order Customer Assignment
- **Use**: `orderCustomerSet` mutation
- **Use case**: Correcting order ownership, guest customer conversion
- **Considerations**: Order history integrity, customer communication

### Default Address Management
- **Use**: `customerUpdateDefaultAddress` mutation
- **Use case**: Shipping preferences, billing address updates
- **Considerations**: Multi-address customers, shipping cost calculations

### Customer Status Updates
- **Use**: `customerUpdate` mutation
- **Use case**: Account status changes, marketing preferences
- **Considerations**: Legal compliance, customer communication

## Data Validation Guidelines

### Customer Updates
- Verify customer exists before updating
- Validate email format and uniqueness
- Check phone number format and validity
- Ensure tags follow store conventions

### Address Updates
- Validate required address fields
- Check country and province codes
- Verify postal code format for country
- Consider address standardization

### Order Assignments
- Verify order exists and is assignable
- Check customer eligibility for order assignment
- Consider payment and fulfillment implications
- Maintain audit trail for changes

## Customer Communication Considerations

### Update Notifications
- Inform customers about significant account changes
- Provide clear explanations for updates
- Offer customer support for questions
- Consider legal notification requirements

### Marketing Preference Changes
- Respect opt-in/opt-out requests immediately
- Update all marketing systems accordingly
- Provide confirmation to customers
- Maintain compliance records

### Address Change Notifications
- Notify customers of address updates
- Explain impact on pending orders
- Provide opportunity to correct mistakes
- Update shipping expectations

## Error Handling

### Common Customer Update Errors
- **Customer not found**: Verify customer ID or email address
- **Email already exists**: Check for duplicate customer accounts
- **Invalid address format**: Request corrected address information
- **Permission denied**: Verify API access and customer ownership

### Order Assignment Errors
- **Order not found**: Verify order ID and status
- **Customer not eligible**: Check customer account status
- **Order already assigned**: Verify current order ownership
- **Payment processing conflict**: Consider order payment status

### Address Update Errors
- **Address not found**: Verify address ID belongs to customer
- **Invalid address data**: Request complete address information
- **Country not supported**: Check shipping destination validity
- **Default address conflict**: Verify address selection

## Best Practices

### Before Updating Customers
1. **Verify customer identity** - ensure you're updating the right customer
2. **Validate new information** - check email format, address validity
3. **Consider order impact** - understand how updates affect existing orders
4. **Backup critical data** - preserve important customer information
5. **Communicate changes** - inform customers of significant updates

### After Updating Customers
1. **Verify update success** - confirm changes were applied correctly
2. **Check related data** - ensure orders, addresses, and tags are consistent
3. **Monitor for issues** - watch for unexpected consequences
4. **Update integrations** - sync changes with other systems if needed
5. **Document changes** - maintain audit trail for customer updates

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
