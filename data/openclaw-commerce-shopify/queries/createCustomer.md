# Shopify Customer Creation & Management

This guide helps you generate accurate GraphQL mutations for creating and managing customers in Shopify.

## Instructions for Mutation Generation

When a user requests to create customers or manage customer accounts, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific customer creation requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Consider customer communication preferences** - account invitations and notifications

## Official Documentation

### Primary Customer Creation Mutation Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSet

**What to learn from this documentation:**
- Required input fields for customer creation
- Customer data structure and validation
- Address and contact information handling
- Email marketing preferences
- Customer tags and metafields
- Password and account creation options

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSet#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSet#return-fields
  - *Review only when you need to verify what data is returned after creation*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSet#examples
  - *Review only when you need sample mutation patterns for complex customer scenarios*

### Customer Account Invitation Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerSendAccountInviteEmail

**What to learn from this documentation:**
- Account invitation email functionality
- Email template customization
- Invitation expiration and tracking
- Customer activation workflows

### Customer Payment Method Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodSendUpdateEmail

**What to learn from this documentation:**
- Payment method update email functionality
- Secure payment information handling
- Customer verification workflows
- Email template and branding options

### Customer Address Creation Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressCreate

**What to learn from this documentation:**
- Create new addresses for existing customers
- Address validation and formatting
- Multiple address management
- Default address setting options

### Customer Create Alternative Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerCreate

**What to learn from this documentation:**
- Alternative customer creation method
- Different input requirements and validation
- Customer account creation workflows
- Comparison with customerSet mutation

### Customer Account Activation Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerGenerateAccountActivationUrl

**What to learn from this documentation:**
- Generate account activation URLs
- Customer account activation workflows
- Secure URL generation and expiration
- Customer onboarding processes

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when creating customers.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Customer Creation Cost Calculation**:
   - Customer creation mutations have moderate costs
   - Complex customer data with addresses and metafields increase cost
   - Email sending operations may have additional costs
   - Formula: `cost = base_mutation_cost + customer_data_complexity`

3. **Best Practices for Customer Creation Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate email addresses**: Ensure proper email format before mutation
   - **Handle duplicates**: Check for existing customers before creating new ones
   - **Respect preferences**: Honor email marketing consent
   - **Batch carefully**: Create multiple customers in separate mutations

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Creates customer with excessive optional fields
   mutation customerSet($input: CustomerInput!) {
     customerSet(input: $input) {
       customer { id email firstName lastName phone addresses { ... } orders { ... } tags metafields { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Creates customer with essential fields only
   mutation customerSet($input: CustomerInput!) {
     customerSet(input: $input) {
       customer { id email firstName lastName phone }
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating customer creation mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$EMAIL$` | Customer email | Ask user if not provided | `"customer@example.com"` |
| `$FIRST_NAME$` | Customer first name | Ask user if not provided | `"John"` |
| `$LAST_NAME$` | Customer last name | Ask user if not provided | `"Doe"` |
| `$PHONE$` | Customer phone | Ask user if not provided | `"+1234567890"` |
| `$PASSWORD$` | Customer password | Ask user if not provided | `"securePassword123"` |
| `$ACCEPTS_MARKETING$` | Email marketing consent | `false` | `true` |
| `$TAGS$` | Customer tags | `[]` | `["VIP", "wholesale"]` |
| `$ADDRESS1$` | Address line 1 | Ask user if not provided | `"123 Main St"` |
| `$CITY$` | City | Ask user if not provided | `"New York"` |
| `$PROVINCE$` | State/Province | Ask user if not provided | `"NY"` |
| `$COUNTRY$` | Country | Ask user if not provided | `"United States"` |
| `$ZIP$` | Postal code | Ask user if not provided | `"10001"` |
| `$CUSTOMER_ID$` | Customer ID for emails | Ask user if not provided | `gid://shopify/Customer/123456789` |

### Mutation Structure Templates

#### Customer Creation Template
```graphql
mutation customerSet($input: CustomerInput!) {
  customerSet(input: $input) {
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
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Customer with Address Creation Template
```graphql
mutation customerSet($input: CustomerInput!) {
  customerSet(input: $input) {
    customer {
      id
      email
      firstName
      lastName
      phone
      addresses {
        address1
        address2
        city
        province
        country
        zip
        phone
      }
      createdAt
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

#### Account Invitation Template
```graphql
mutation customerSendAccountInviteEmail($input: CustomerSendAccountInviteEmailInput!) {
  customerSendAccountInviteEmail(input: $input) {
    customer {
      id
      email
      state
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Payment Method Update Template
```graphql
mutation customerPaymentMethodSendUpdateEmail($input: CustomerPaymentMethodSendUpdateEmailInput!) {
  customerPaymentMethodSendUpdateEmail(input: $input) {
    customer {
      id
      email
      paymentMethods {
        id
        type
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

#### Customer Address Creation Template
```graphql
mutation customerAddressCreate($customerId: ID!, $address: MailingAddressInput!) {
  customerAddressCreate(customerId: $customerId, address: $address) {
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

#### Customer Create Alternative Template
```graphql
mutation customerCreate($input: CustomerCreateInput!) {
  customerCreate(input: $input) {
    customer {
      id
      email
      firstName
      lastName
      phone
      createdAt
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

#### Customer Account Activation URL Template
```graphql
mutation customerGenerateAccountActivationUrl($customerId: ID!) {
  customerGenerateAccountActivationUrl(customerId: $customerId) {
    accountActivationUrl
    customer {
      id
      email
      state
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a customer creation mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the mutation does** in simple business terms (e.g., "This will create a new customer account in your store")
2. **Explain what information is needed** in simple terms (e.g., "I'll need the customer's email and basic information")
3. **Explain any limitations** in simple terms (e.g., "The customer will receive an email to activate their account")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you create a new customer account for your store.

**Mutation:**
```graphql
mutation customerSet($input: CustomerInput!) {
  customerSet(input: $input) {
    customer {
      id
      email
      firstName
      lastName
      phone
      createdAt
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
This creates a new customer account in your Shopify store with their contact information.

**What I need from you:**
- Customer's email address
- Customer's first and last name
- Phone number (optional)
- Whether they consent to marketing emails
- Any tags you want to apply (like "VIP" or "wholesale")

**Important notes:**
- The customer will receive an email to set up their password
- You can add shipping addresses if needed
- Customer accounts help with order tracking and repeat purchases

Would you like me to help you create a customer account?
```

## Common Customer Creation Scenarios

### Basic Customer Account Creation
- **Use**: `customerSet` mutation
- **Fields**: Email, name, phone, marketing preferences
- **Considerations**: Email validation, duplicate checking

### Customer with Shipping Address
- **Use**: `customerSet` mutation with address input
- **Fields**: Complete address information
- **Considerations**: Address validation, formatting standards

### Wholesale Customer Setup
- **Use**: `customerSet` mutation with tags
- **Fields**: Business information, wholesale tags
- **Considerations**: Tax settings, pricing rules

### Customer Account Invitation
- **Use**: `customerSendAccountInviteEmail` mutation
- **Use case**: Existing customer needs account activation
- **Considerations**: Email deliverability, invitation expiration

### Payment Method Update
- **Use**: `customerPaymentMethodSendUpdateEmail` mutation
- **Use case**: Customer needs to update payment information
- **Considerations**: Security, verification process

### Bulk Customer Import
- **Use**: Multiple `customerSet` mutations
- **Use case**: Migrating customers from another system
- **Considerations**: Rate limiting, data validation, duplicate handling

## Data Validation Guidelines

### Email Validation
- Ensure proper email format
- Check for existing customers with same email
- Verify email domain validity
- Consider disposable email detection

### Phone Number Validation
- Use international format (+country code)
- Validate phone number length
- Consider country-specific formats
- Handle extension numbers if needed

### Address Validation
- Verify required address fields
- Check country and province codes
- Validate postal code format
- Consider address standardization

### Data Privacy Considerations
- Honor marketing consent preferences
- Follow GDPR/CCPA requirements
- Secure sensitive customer data
- Provide data deletion options

## Customer Communication Best Practices

### Welcome Emails
- Send clear account setup instructions
- Include store branding and contact information
- Provide next steps for shopping
- Offer customer support contacts

### Account Activation
- Use secure password reset links
- Set reasonable expiration times
- Provide clear activation instructions
- Handle failed attempts gracefully

### Marketing Communications
- Respect email preferences
- Provide easy unsubscribe options
- Segment customers appropriately
- Personalize content when possible

## Error Handling

### Common Customer Creation Errors
- **Email already exists**: Offer account recovery or alternative email
- **Invalid email format**: Request corrected email address
- **Missing required fields**: Specify which information is needed
- **Rate limiting**: Suggest trying again later or batching requests

### Customer Communication Errors
- **Email delivery failure**: Verify email address and try again
- **Invitation expired**: Send new invitation
- **Payment method issues**: Guide customer to secure update process

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
