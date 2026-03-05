# Shopify Code Discount Deletion & Management

This guide helps you generate accurate GraphQL mutations for deleting code discounts and managing code discount data removal in Shopify.

## Instructions for Mutation Generation

When a user requests to delete code discounts or manage code discount data removal, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific code discount deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Primary Code Discount Delete Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeDelete

**What to learn from this documentation:**
- Required input fields for code discount deletion
- Code discount eligibility requirements for deletion
- Order history and customer impact implications
- Code discount deletion workflows and consequences
- Legal and compliance considerations

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

### Code Discount Management Mutations Documentation

#### Bulk Code Discount Deletion
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkDelete

**What to learn from this documentation:**
- Bulk code discount deletion workflows
- Multiple discount management operations
- Efficiency considerations for bulk operations
- Error handling for bulk deletion scenarios

#### Code Discount Deactivation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBulkDeactivate

**What to learn from this documentation:**
- Code discount deactivation workflows
- Temporary discount suspension
- Bulk deactivation operations
- Deactivation vs deletion considerations

#### Code Redemption Management
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeRedeemCodeBulkDelete

**What to learn from this documentation:**
- Code redemption data removal
- Customer assignment management
- Bulk redemption deletion workflows
- Redemption analytics and reporting impact

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting code discounts.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Code Discount Delete Cost Calculation**:
   - Code discount deletion mutations have moderate costs
   - Complex discounts with many codes may have higher costs
   - Bulk operations have higher costs but are more efficient than individual operations
   - Formula: `cost = base_mutation_cost + discount_complexity + code_count + usage_data`

3. **Best Practices for Code Discount Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure code discount is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest deactivation instead of deletion when appropriate
   - **Warn about consequences**: Clearly explain irreversible nature of deletion

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes discount with excessive return fields
   mutation discountCodeDelete($input: DiscountCodeDeleteInput!) {
     discountCodeDelete(input: $input) {
       deletedDiscountId
       discount { id title codes { ... } usageCount { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes discount with essential fields only
   mutation discountCodeDelete($input: DiscountCodeDeleteInput!) {
     discountCodeDelete(input: $input) {
       deletedDiscountId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating code discount delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Discount ID to delete | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$DISCOUNT_IDS$` | Discount IDs for bulk operations | Ask user if not provided | `[gid://shopify/DiscountNode/123456789]` |
| `$DELETE_REASON$` | Reason for deletion | `"DISCOUNT_CLEANUP"` | `"SEASONAL_REMOVAL"` |
| `$REDEEM_CODE$` | Code to delete redemption for | Ask user if not provided | `"SUMMER2024"` |
| `$CUSTOMER_IDS$` | Customer IDs for redemption deletion | Ask user if not provided | `[gid://shopify/Customer/987654321]` |

### Mutation Structure Templates

#### Code Discount Delete Template
```graphql
mutation discountCodeDelete($input: DiscountCodeDeleteInput!) {
  discountCodeDelete(input: $input) {
    deletedDiscountId
    userErrors {
      field
      message
    }
  }
}
```

#### Bulk Code Discount Delete Template
```graphql
mutation discountCodeBulkDelete($discountIds: [ID!]!) {
  discountCodeBulkDelete(discountIds: $discountIds) {
    deletedDiscountIds
    userErrors {
      field
      message
    }
  }
}
```

#### Bulk Code Discount Deactivate Template
```graphql
mutation discountCodeBulkDeactivate($discountIds: [ID!]!) {
  discountCodeBulkDeactivate(discountIds: $discountIds) {
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

#### Code Redemption Bulk Delete Template
```graphql
mutation discountCodeRedeemCodeBulkDelete($code: String!, $customerIds: [ID!]!) {
  discountCodeRedeemCodeBulkDelete(code: $code, customerIds: $customerIds) {
    deletedDiscountCodeRedeemCodes {
      id
      code
      customerId
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating a code discount delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the discount code from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all discount data will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the discount ID or code")
4. **Explain any limitations** in simple terms (e.g., "Only certain discounts can be deleted - others must be deactivated")
5. **Suggest alternatives** when appropriate (e.g., "Consider deactivating instead of deleting to preserve data")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete a discount code from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the discount code and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation discountCodeDelete($input: DiscountCodeDeleteInput!) {
  discountCodeDelete(input: $input) {
    deletedDiscountId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes a discount code from your Shopify store.

**What I need from you:**
- The discount ID or code you want to delete

**Important consequences:**
- All discount configuration will be permanently erased
- Usage history and analytics will be lost
- Any customers with saved codes will lose access
- Marketing materials referencing the code will become invalid
- This action cannot be reversed

**Alternatives to consider:**
- Deactivate the discount to preserve data and usage history
- Set an early end date instead of deletion
- Archive the discount for future reference
- Update the discount instead of deleting it

**Are you sure you want to proceed with permanent deletion?**
```

## Common Code Discount Deletion Scenarios

### Discount Removal
- **Use**: `discountCodeDelete` mutation
- **Eligibility**: Most code discounts can be deleted unless they have specific restrictions
- **Considerations**: Usage history preservation, customer impact, marketing materials

### Seasonal Discount Cleanup
- **Use**: Code discount deletion or deactivation
- **Use case**: End-of-season cleanup, expired promotional codes
- **Considerations**: Customer expectations, future re-use possibilities, data preservation

### Bulk Discount Management
- **Use**: `discountCodeBulkDelete` mutation
- **Use case**: Removing multiple outdated discounts, system cleanup
- **Considerations**: Performance impact, error handling, partial success scenarios

### Test Discount Cleanup
- **Use**: Code discount deletion for test codes
- **Use case**: Removing development or test discount codes
- **Considerations**: Data isolation, production safety, team coordination

### Customer Data Management
- **Use**: `discountCodeRedeemCodeBulkDelete` mutation
- **Use case**: Removing customer-specific redemption data
- **Considerations**: Privacy compliance, data retention policies, customer experience

## Deletion Limitations

### Code Discount Deletion Restrictions
- **Active Usage**: Discounts with recent or active usage may be protected
- **Order Dependencies**: Discounts referenced in recent orders may have restrictions
- **Legal Requirements**: Some jurisdictions require data retention for specific periods
- **Store Policies**: Individual stores may have additional deletion restrictions

### Bulk Operation Restrictions
- **Rate Limiting**: Bulk operations may be limited by API rate limits
- **Error Handling**: Some discounts in bulk operations may fail while others succeed
- **System Performance**: Large bulk operations may affect system performance
- **Permission Issues**: Verify API access for bulk deletion operations

### Redemption Data Restrictions
- **Customer Privacy**: Customer data deletion may be restricted by privacy laws
- **Order History**: Redemption data may be required for order history
- **Legal Compliance**: Some redemption data must be retained for compliance
- **Analytics Impact**: Redemption data deletion affects analytics and reporting

## Safety Precautions

### Before Deleting Code Discounts
1. **Verify discount importance** - assess usage history and customer impact
2. **Check customer dependencies** - ensure no customers rely on the discount
3. **Consider marketing impact** - understand how deletion affects marketing campaigns
4. **Backup critical data** - preserve important discount information
5. **Communicate with stakeholders** - inform relevant team members

### Before Bulk Deletion Operations
1. **Verify discount list** - ensure all discounts in bulk operation should be deleted
2. **Test with small batches** - validate bulk operation with small test batches
3. **Plan error handling** - prepare for partial success scenarios
4. **Monitor system performance** - watch for performance impact during bulk operations
5. **Document operation** - maintain records of bulk deletion operations

### Before Redemption Data Deletion
1. **Verify privacy requirements** - ensure compliance with privacy regulations
2. **Check legal obligations** - understand legal data retention requirements
3. **Consider analytics impact** - understand how deletion affects reporting
4. **Customer communication** - inform customers if their data is being deleted
5. **Backup critical information** - preserve essential customer data

### After Deletion Operations
1. **Verify deletion success** - confirm discounts were removed
2. **Check related systems** - ensure integrations updated properly
3. **Monitor customer impact** - watch for customer access issues
4. **Update documentation** - maintain current discount documentation
5. **Analyze system impact** - assess changes in system performance

## Error Handling

### Common Code Discount Delete Errors
- **Discount Not Found**: Verify discount ID or code exists
- **Discount Not Eligible**: Check usage status, order dependencies, or legal restrictions
- **Permission Denied**: Verify API access and discount ownership
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Bulk Operation Errors
- **Partial Success**: Some discounts may delete while others fail
- **Rate Limiting**: Bulk operations may hit API rate limits
- **Validation Failures**: Individual discounts may fail validation
- **System Constraints**: System limitations may affect bulk operations

### Redemption Data Errors
- **Customer Privacy**: Customer data deletion may be restricted
- **Order Dependencies**: Redemption data may be required for orders
- **Legal Compliance**: Data retention requirements may prevent deletion
- **Permission Issues**: Verify access to customer redemption data

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest deactivation, archiving, or other solutions
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Maintain Professionalism** - handle errors calmly and helpfully
5. **Document Issues** - track recurring problems for system improvements

## Best Practices

### Code Discount Deletion Best Practices
1. **Use Deactivation When Possible** - preserve data and usage history
2. **Plan Customer Communication** - inform customers about discount changes
3. **Document Deletion Reasons** - maintain records for analysis and compliance
4. **Monitor Customer Impact** - track changes in customer behavior
5. **Consider Future Re-use** - think about whether discounts might be needed again

### Bulk Deletion Best Practices
1. **Test Before Scaling** - validate operations with small test batches
2. **Implement Error Handling** - handle partial success scenarios gracefully
3. **Monitor Performance** - watch system performance during bulk operations
4. **Document Operations** - maintain detailed records of bulk deletions
5. **Plan Rollback Strategy** - prepare for potential rollback scenarios

### Redemption Data Management Best Practices
1. **Understand Legal Requirements** - comply with data retention and privacy laws
2. **Consider Analytics Impact** - understand how deletion affects reporting
3. **Customer Privacy First** - prioritize customer privacy in data management
4. **Backup Critical Data** - preserve essential customer and business data
5. **Document Data Policies** - maintain clear data retention and deletion policies

### Alternative Strategies

### Discount Deactivation
- **Preserve Data**: Maintain all discount data and usage history
- **Enable Reactivation**: Allow discount to be reactivated if needed
- **Reduce Active Management**: Hide discount without permanent deletion
- **Maintain Data Integrity**: Preserve historical data for analysis

### Discount Archiving
- **Data Preservation**: Keep discount data for future reference
- **Analytics Maintenance**: Preserve historical usage data
- **Compliance Support**: Maintain data for legal and compliance needs
- **Future Re-use**: Enable potential discount re-use with preserved configuration

### Schedule-Based Management
- **Early Termination**: Set early end dates instead of deletion
- **Future Activation**: Schedule discounts for future use
- **Seasonal Planning**: Plan for seasonal discount re-use
- **Campaign Coordination**: Align discount schedules with marketing campaigns

### Discount Updates Instead of Deletion
- **Configuration Changes**: Modify discount settings instead of deletion
- **Code Updates**: Update discount codes while preserving configuration
- **Condition Modifications**: Adjust eligibility conditions
- **Value Adjustments**: Modify discount values while preserving structure

## Compliance Considerations

### Data Retention Requirements
- **Tax Compliance**: Some jurisdictions require discount data retention for tax purposes
- **Consumer Protection**: Discount information may need to be retained for consumer rights
- **Financial Regulations**: Transaction data may require discount information preservation
- **Industry Standards**: Specific industries may have additional retention requirements

### Customer Data Protection
- **Privacy Laws**: GDPR, CCPA, and other privacy regulations may apply
- **Customer Consent**: Consider customer consent for data deletion
- **Data Minimization**: Delete only necessary customer data
- **Right to be Forgotten**: Honor customer requests for data deletion

### Business Continuity
- **Analytics Data**: Historical discount data may be needed for business analysis
- **Performance Metrics**: Discount performance data may be important for planning
- **Customer Insights**: Discount usage data may provide valuable customer insights
- **Future Planning**: Historical data may inform future discount strategies

### Legal and Regulatory Compliance
- **Advertising Laws**: Discount advertising claims may have legal requirements
- **Consumer Rights**: Discount terms may have legal implications
- **Financial Reporting**: Discount data may be required for financial reporting
- **Audit Requirements**: Discount data may be needed for audit purposes

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
