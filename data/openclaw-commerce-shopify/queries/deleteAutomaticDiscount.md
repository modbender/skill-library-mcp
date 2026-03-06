# Shopify Automatic Discount Deletion & Management

This guide helps you generate accurate GraphQL mutations for deleting automatic discounts and managing automatic discount data removal in Shopify.

## Instructions for Mutation Generation

When a user requests to delete automatic discounts or manage automatic discount data removal, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific automatic discount deletion requirements
3. **Generate** the appropriate GraphQL mutation based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the mutation
6. **Warn about irreversible consequences** - deletion is permanent

## Official Documentation

### Primary Automatic Discount Delete Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDelete

**What to learn from this documentation:**
- Required input fields for automatic discount deletion
- Automatic discount eligibility requirements for deletion
- Order history and customer impact implications
- Condition logic and rule deletion consequences
- Legal and compliance considerations

**Important sections to review:**
- Input fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDelete#argument-input
  - *Review only when you need to verify required fields or find new input options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDelete#return-fields
  - *Review only when you need to verify what data is returned after deletion*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDelete#examples
  - *Review only when you need sample mutation patterns for deletion scenarios*

### Automatic Discount Management Mutations Documentation

#### Bulk Automatic Discount Deletion
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBulkDelete

**What to learn from this documentation:**
- Bulk automatic discount deletion workflows
- Multiple discount management operations
- Efficiency considerations for bulk operations
- Error handling for bulk deletion scenarios

#### Automatic Discount Deactivation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDeactivate

**What to learn from this documentation:**
- Automatic discount deactivation workflows
- Temporary discount suspension
- Condition logic preservation during deactivation
- Deactivation vs deletion considerations

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when deleting automatic discounts.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive mutations*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Automatic Discount Delete Cost Calculation**:
   - Automatic discount deletion mutations have moderate to high costs
   - Complex condition logic and rules increase deletion cost
   - Bulk operations have higher costs but are more efficient than individual operations
   - Formula: `cost = base_mutation_cost + condition_complexity + rule_logic + customer_targeting`

3. **Best Practices for Automatic Discount Delete Mutation Generation**:
   - **Include only required fields**: Don't add optional fields unless needed
   - **Validate eligibility**: Ensure automatic discount is eligible for deletion before mutation
   - **Handle errors**: Always check for user errors in mutation response
   - **Consider alternatives**: Suggest deactivation instead of deletion when appropriate
   - **Warn about consequences**: Clearly explain irreversible nature of deletion

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Deletes discount with excessive return fields
   mutation discountAutomaticDelete($input: DiscountAutomaticDeleteInput!) {
     discountAutomaticDelete(input: $input) {
       deletedDiscountId
       discount { id title conditions { ... } customerSelection { ... } }
       userErrors { field message }
     }
   }
   
   # ✅ LOW COST - Deletes discount with essential fields only
   mutation discountAutomaticDelete($input: DiscountAutomaticDeleteInput!) {
     discountAutomaticDelete(input: $input) {
       deletedDiscountId
       userErrors { field message }
     }
   }
   ```

## Mutation Generation Rules

### Variable Placeholders

When generating automatic discount delete mutations, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$DISCOUNT_ID$` | Discount ID to delete | Ask user if not provided | `gid://shopify/DiscountNode/123456789` |
| `$DISCOUNT_IDS$` | Discount IDs for bulk operations | Ask user if not provided | `[gid://shopify/DiscountNode/123456789]` |
| `$DELETE_REASON$` | Reason for deletion | `"DISCOUNT_CLEANUP"` | `"STRATEGY_CHANGE"` |

### Mutation Structure Templates

#### Automatic Discount Delete Template
```graphql
mutation discountAutomaticDelete($input: DiscountAutomaticDeleteInput!) {
  discountAutomaticDelete(input: $input) {
    deletedDiscountId
    userErrors {
      field
      message
    }
  }
}
```

#### Bulk Automatic Discount Delete Template
```graphql
mutation discountAutomaticBulkDelete($discountIds: [ID!]!) {
  discountAutomaticBulkDelete(discountIds: $discountIds) {
    deletedDiscountIds
    userErrors {
      field
      message
    }
  }
}
```

#### Automatic Discount Deactivate Template
```graphql
mutation discountAutomaticDeactivate($id: ID!) {
  discountAutomaticDeactivate(id: $id) {
    discount {
      id
      title
      status
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

## Response Guidelines

When generating an automatic discount delete mutation for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms. **CRITICAL**: Always warn about the permanent nature of deletion.

1. **Explain what the mutation does** in simple business terms (e.g., "This will permanently delete the automatic discount from your store")
2. **Warn about consequences** in clear terms (e.g., "This action cannot be undone - all discount data and conditions will be permanently removed")
3. **Explain what information is needed** in simple terms (e.g., "I'll need the discount ID or title")
4. **Explain any limitations** in simple terms (e.g., "Only certain automatic discounts can be deleted - others must be deactivated")
5. **Suggest alternatives** when appropriate (e.g., "Consider deactivating instead of deleting to preserve data")
6. **Ask for confirmation** before proceeding with deletion
7. **Avoid technical jargon** - no mentions of "cost", "mutation complexity", "optimization", etc.

### Example Response Format

```
I'll help you delete an automatic discount from your store.

**⚠️ IMPORTANT WARNING**: This will permanently delete the automatic discount and all associated data. This action cannot be undone.

**Mutation:**
```graphql
mutation discountAutomaticDelete($input: DiscountAutomaticDeleteInput!) {
  discountAutomaticDelete(input: $input) {
    deletedDiscountId
    userErrors {
      field
      message
    }
  }
}
```

**What this does:**
This permanently removes an automatic discount from your Shopify store.

**What I need from you:**
- The discount ID or title you want to delete

**Important consequences:**
- All discount configuration and conditions will be permanently erased
- Usage history and performance analytics will be lost
- Customer pricing behavior will immediately change
- Any marketing materials referencing the discount will become invalid
- This action cannot be reversed

**Alternatives to consider:**
- Deactivate the discount to preserve data and configuration
- Set an early end date instead of deletion
- Update the discount conditions instead of deleting
- Archive the discount for future reference

**Are you sure you want to proceed with permanent deletion?**
```

## Common Automatic Discount Deletion Scenarios

### Discount Removal
- **Use**: `discountAutomaticDelete` mutation
- **Eligibility**: Most automatic discounts can be deleted unless they have specific restrictions
- **Considerations**: Usage history preservation, customer pricing impact, marketing materials

### Strategy Change Cleanup
- **Use**: Automatic discount deletion or deactivation
- **Use case**: Pricing strategy changes, business model updates
- **Considerations**: Customer expectations, competitive positioning, profit margins

### Bulk Discount Management
- **Use**: `discountAutomaticBulkDelete` mutation
- **Use case**: Removing multiple outdated automatic discounts, system cleanup
- **Considerations**: Performance impact, error handling, partial success scenarios

### Test Discount Cleanup
- **Use**: Automatic discount deletion for test configurations
- **Use case**: Removing development or test automatic discounts
- **Considerations**: Data isolation, production safety, team coordination

### Condition Logic Simplification
- **Use**: Automatic discount deletion for complex or outdated rules
- **Use case**: Simplifying discount strategy, removing redundant conditions
- **Considerations**: Customer experience, system performance, management complexity

## Deletion Limitations

### Automatic Discount Deletion Restrictions
- **Active Application**: Discounts currently applying to customer carts may be protected
- **Order Dependencies**: Discounts referenced in recent orders may have restrictions
- **Legal Requirements**: Some jurisdictions require data retention for specific periods
- **Store Policies**: Individual stores may have additional deletion restrictions

### Condition Logic Restrictions
- **Complex Dependencies**: Discounts with complex condition logic may have deletion restrictions
- **Customer Segments**: Discounts tied to specific customer segments may be protected
- **Integration Dependencies**: Discounts integrated with third-party apps may have limitations
- **Performance Considerations**: System performance may restrict deletion during peak times

### Bulk Operation Restrictions
- **Rate Limiting**: Bulk operations may be limited by API rate limits
- **Error Handling**: Some discounts in bulk operations may fail while others succeed
- **System Performance**: Large bulk operations may affect system performance
- **Permission Issues**: Verify API access for bulk deletion operations

## Safety Precautions

### Before Deleting Automatic Discounts
1. **Verify discount importance** - assess usage history and customer impact
2. **Check customer dependencies** - understand how deletion affects customer pricing
3. **Consider competitive impact** - understand how deletion affects competitive positioning
4. **Backup critical data** - preserve important discount configuration and performance data
5. **Communicate with stakeholders** - inform relevant team members about changes

### Before Bulk Deletion Operations
1. **Verify discount list** - ensure all discounts in bulk operation should be deleted
2. **Test with small batches** - validate bulk operation with small test batches
3. **Plan error handling** - prepare for partial success scenarios
4. **Monitor system performance** - watch for performance impact during bulk operations
5. **Document operation** - maintain records of bulk deletion operations

### Before Strategy Changes
1. **Analyze customer impact** - understand how pricing changes affect customers
2. **Calculate financial impact** - assess impact on revenue and profit margins
3. **Plan customer communication** - prepare customer messaging about pricing changes
4. **Monitor competitive response** - watch for competitive reactions to pricing changes
5. **Test new strategy** - validate new pricing strategy before implementation

### After Deletion Operations
1. **Verify deletion success** - confirm discounts were removed
2. **Monitor customer behavior** - watch for changes in customer purchasing patterns
3. **Check system performance** - ensure system performance is maintained
4. **Update documentation** - maintain current discount documentation
5. **Analyze results** - assess impact of deletion on business metrics

## Error Handling

### Common Automatic Discount Delete Errors
- **Discount Not Found**: Verify discount ID exists
- **Discount Not Eligible**: Check usage status, order dependencies, or legal restrictions
- **Permission Denied**: Verify API access and discount ownership
- **Concurrent Updates**: Handle conflicts with simultaneous changes

### Condition Logic Errors
- **Complex Dependencies**: Discounts with complex conditions may fail deletion
- **Integration Conflicts**: Third-party app integrations may prevent deletion
- **Performance Issues**: System performance may affect deletion operations
- **Validation Failures**: Condition logic may prevent deletion

### Bulk Operation Errors
- **Partial Success**: Some discounts may delete while others fail
- **Rate Limiting**: Bulk operations may hit API rate limits
- **System Constraints**: System limitations may affect bulk operations
- **Validation Errors**: Individual discounts may fail validation

### Best Practices for Error Resolution
1. **Provide Clear Explanations** - explain what went wrong in business terms
2. **Offer Alternatives** - suggest deactivation, archiving, or other solutions
3. **Guide Next Steps** - provide clear instructions for resolution
4. **Maintain Professionalism** - handle errors calmly and helpfully
5. **Document Issues** - track recurring problems for system improvements

## Best Practices

### Automatic Discount Deletion Best Practices
1. **Use Deactivation When Possible** - preserve data and configuration for future use
2. **Plan Customer Communication** - inform customers about pricing changes
3. **Document Deletion Reasons** - maintain records for analysis and compliance
4. **Monitor Customer Impact** - track changes in customer behavior and satisfaction
5. **Consider Future Re-use** - think about whether discounts might be needed again

### Bulk Deletion Best Practices
1. **Test Before Scaling** - validate operations with small test batches
2. **Implement Error Handling** - handle partial success scenarios gracefully
3. **Monitor Performance** - watch system performance during bulk operations
4. **Document Operations** - maintain detailed records of bulk deletions
5. **Plan Rollback Strategy** - prepare for potential rollback scenarios

### Strategy Change Best Practices
1. **Analyze Impact Thoroughly** - understand all implications of pricing strategy changes
2. **Phase Changes Gradually** - implement changes in phases to minimize disruption
3. **Monitor Customer Response** - track customer reaction to pricing changes
4. **Adjust Based on Feedback** - be prepared to adjust strategy based on results
5. **Maintain Competitive Awareness** - monitor competitive positioning during changes

## Alternative Strategies

### Automatic Discount Deactivation
- **Preserve Configuration**: Maintain all discount data and condition logic
- **Enable Reactivation**: Allow discount to be reactivated if needed
- **Reduce Active Management**: Hide discount without permanent deletion
- **Maintain Data Integrity**: Preserve historical data for analysis

### Discount Archiving
- **Data Preservation**: Keep discount data for future reference
- **Analytics Maintenance**: Preserve historical usage and performance data
- **Compliance Support**: Maintain data for legal and compliance needs
- **Future Re-use**: Enable potential discount re-use with preserved configuration

### Condition Logic Updates
- **Modify Instead of Delete**: Update discount conditions instead of deletion
- **Simplify Logic**: Reduce complexity of condition logic
- **Update Targeting**: Modify customer eligibility criteria
- **Adjust Values**: Change discount values while preserving structure

### Schedule-Based Management
- **Early Termination**: Set early end dates instead of deletion
- **Future Activation**: Schedule discounts for future use
- **Seasonal Planning**: Plan for seasonal discount re-use
- **Campaign Coordination**: Align discount schedules with marketing campaigns

## Impact Analysis

### Customer Experience Impact
- **Pricing Changes**: Customers will immediately notice price changes
- **Checkout Experience**: Automatic discount removal affects checkout flow
- **Trust Considerations**: Maintain customer trust with consistent pricing
- **Communication Needs**: Plan customer communication about pricing changes

### Business Impact
- **Revenue Impact**: Understand how deletion affects overall revenue
- **Margin Analysis**: Calculate impact on profit margins
- **Competitive Positioning**: Analyze competitive implications
- **Customer Retention**: Assess impact on customer loyalty and retention

### Operational Impact
- **System Performance**: Monitor system performance after deletion
- **Order Processing**: Ensure smooth order processing without discounts
- **Customer Service**: Prepare customer service for pricing-related inquiries
- **Analytics Impact**: Understand how deletion affects reporting and analysis

### Marketing Impact
- **Campaign Coordination**: Align deletion with marketing campaigns
- **Promotional Strategy**: Update promotional strategies
- **Channel Consistency**: Ensure consistency across marketing channels
- **Performance Tracking**: Monitor impact on marketing metrics

## Compliance Considerations

### Data Retention Requirements
- **Tax Compliance**: Some jurisdictions require discount data retention for tax purposes
- **Consumer Protection**: Discount information may need to be retained for consumer rights
- **Financial Regulations**: Transaction data may require discount information preservation
- **Industry Standards**: Specific industries may have additional retention requirements

### Pricing Regulations
- **Price Advertising**: Discount pricing may be subject to advertising regulations
- **Consumer Rights**: Pricing changes may be subject to consumer protection laws
- **Fair Pricing**: Ensure pricing practices comply with fair pricing regulations
- **Transparency Requirements**: Maintain transparency in pricing practices

### Business Continuity
- **Analytics Data**: Historical discount data may be needed for business analysis
- **Performance Metrics**: Discount performance data may be important for planning
- **Customer Insights**: Discount usage data may provide valuable customer insights
- **Future Planning**: Historical data may inform future pricing strategies

### Legal and Regulatory Compliance
- **Contractual Obligations**: Discounts may be part of customer contracts
- **Regulatory Reporting**: Discount data may be required for regulatory reporting
- **Audit Requirements**: Discount data may be needed for audit purposes
- **Industry Compliance**: Specific industries may have additional compliance requirements

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
