# Shopify Customer Queries

This guide helps you generate accurate GraphQL queries for fetching customer information from Shopify.

## Instructions for Query Generation

When a user requests to fetch customer data, follow these steps:

1. **Read and understand** the official Shopify documentation thoroughly
2. **Analyze** the user's specific customer data requirements
3. **Generate** the appropriate GraphQL query based on the documentation
4. **Apply** rate limiting best practices
5. **Validate** that all required fields are included in the query

## Official Documentation

### Primary Customer Queries Documentation
**Primary Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers

**What to learn from this documentation:**
- Required input fields for customer queries
- Available filters and search parameters
- Pagination and sorting options
- Customer data structure and available fields
- Query optimization techniques

**Important sections to review:**
- Arguments: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#arguments
  - *Review only when you need to verify query parameters or find new filter options*
- Return fields: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#return-fields
  - *Review only when you need to verify what customer data is available*
- Examples: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#examples
  - *Review only when you need sample query patterns for complex customer scenarios*

### Customer Count Query Documentation
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/customersCount

**What to learn from this documentation:**
- Customer count aggregation options
- Filtering for count queries
- Performance considerations for large datasets

### Individual Customer Queries Documentation

#### Customer Search Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers

**Note**: *This is the same as the primary reference but focuses on search functionality*

#### Specific Customer Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/customer

**What to learn from this documentation:**
- Fetch individual customer by ID
- Complete customer data structure
- Related customer data (orders, addresses, etc.)

#### Customer by Identifier Query
**Reference**: https://shopify.dev/docs/api/admin-graphql/latest/queries/customerByIdentifier

**What to learn from this documentation:**
- Fetch customer by various identifiers (email, phone, etc.)
- Identifier validation and formatting
- Multiple identifier support

## Rate Limiting Guidelines

**Critical**: Always follow Shopify's rate limiting rules when querying customer data.

**Documentation**: https://shopify.dev/docs/api/usage/rate-limits

**Note**: *Review rate limit documentation only when you encounter throttling issues or need to optimize expensive queries*

### Key Rate Limiting Principles

1. **GraphQL Admin API Rate Limits**:
   - Calculated cost-based system (not simple request count)
   - Each field and connection has a cost
   - Maximum 1000 points per app per store per minute (by default)
   - Restore rate: 50 points per second

2. **Customer Query Cost Calculation**:
   - Customer queries have moderate costs
   - Complex filters and connections increase cost
   - Large result sets require pagination to manage costs
   - Formula: `cost = base_query_cost + filter_complexity + result_size`

3. **Best Practices for Customer Query Generation**:
   - **Include only required fields**: Don't request unnecessary customer data
   - **Use specific filters**: Narrow results to reduce data transfer
   - **Implement pagination**: Use cursor-based pagination for large datasets
   - **Cache results**: Store frequently accessed customer data
   - **Batch efficiently**: Query multiple customers in single requests when possible

4. **Cost Optimization Examples**:
   ```graphql
   # ❌ HIGH COST - Fetches all customers with excessive fields
   query {
     customers(first: 50) {
       edges {
         node {
           id email firstName lastName phone orders { edges { node { ... } } }
           addresses { ... } tags metafields { ... }
         }
       }
     }
   }
   
   # ✅ LOW COST - Fetches customers with essential fields only
   query {
     customers(first: 10, query:"email:*@example.com") {
       edges {
         node {
           id email firstName lastName
         }
       }
     }
   }
   ```

## Query Generation Rules

### Variable Placeholders

When generating customer queries, use these placeholders that will be replaced with actual values:

| Placeholder | Description | Default Value | Example |
|-------------|-------------|---------------|---------|
| `$CUSTOMER_ID$` | Customer ID | Ask user if not provided | `gid://shopify/Customer/123456789` |
| `$EMAIL$` | Customer email | Ask user if not provided | `"customer@example.com"` |
| `$PHONE$` | Customer phone | Ask user if not provided | `"+1234567890"` |
| `$FIRST_NAME$` | Customer first name | Ask user if not provided | `"John"` |
| `$LAST_NAME$` | Customer last name | Ask user if not provided | `"Doe"` |
| `$TAG$` | Customer tag | Ask user if not provided | `"VIP"` |
| `$LIMIT$` | Number of results | `10` | `25` |
| `$CURSOR$` | Pagination cursor | `null` | `"eyJjb25uZWN0aW9u..."` |
| `$QUERY_STRING$` | Search query string | `""` | `"email:@example.com AND country:United States"` |

### Query Structure Templates

#### Multiple Customers Query Template
```graphql
query customers($first: Int!, $query: String, $after: String) {
  customers(first: $first, query: $query, after: $after) {
    edges {
      node {
        id
        email
        firstName
        lastName
        phone
        createdAt
        updatedAt
        tags
        state
        numberOfOrders
        totalSpentV2 {
          amount
          currencyCode
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### Specific Customer Query Template
```graphql
query customer($id: ID!) {
  customer(id: $id) {
    id
    email
    firstName
    lastName
    phone
    createdAt
    updatedAt
    tags
    state
    numberOfOrders
    totalSpentV2 {
      amount
      currencyCode
    }
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
    orders(first: 5) {
      edges {
        node {
          id
          name
          processedAt
          totalPriceV2 {
            amount
            currencyCode
          }
        }
      }
    }
  }
}
```

#### Customer Count Query Template
```graphql
query customersCount($query: String) {
  customersCount(query: $query) {
    count
  }
}
```

## Response Guidelines

When generating a customer query for the user:

**Important**: Users are Shopify merchants, not technical developers. Always explain in simple, business-friendly terms.

1. **Explain what the query does** in simple business terms (e.g., "This will find customers matching your criteria")
2. **Explain what information is needed** in simple terms (e.g., "I'll need to know what customers you're looking for")
3. **Explain any limitations** in simple terms (e.g., "This will show up to 50 customers at a time")
4. **Ask for clarification** if requirements are unclear, using business language
5. **Offer practical options** that relate to their business needs
6. **Avoid technical jargon** - no mentions of "cost", "query complexity", "optimization", etc.

### Example Response Format

```
I'll help you find customer information from your store.

**Query:**
```graphql
query customers($first: Int!, $query: String) {
  customers(first: $first, query: $query) {
    edges {
      node {
        id
        email
        firstName
        lastName
        phone
        createdAt
        tags
        numberOfOrders
        totalSpentV2 {
          amount
          currencyCode
        }
      }
    }
  }
}
```

**What this does:**
This searches for customers in your store and returns their contact information and order history.

**What I need from you:**
- What specific customers are you looking for? (by email, name, tags, etc.)
- How many customers would you like to see?

**Examples of what you can search for:**
- All customers with a specific email domain
- Customers who placed orders in the last month
- Customers with specific tags (like "VIP" or "wholesale")
- Customers by name or location

Would you like me to help you find specific customers?
```

## Common Customer Query Scenarios

### Customer Search and Filtering
- **Use**: `customers` query with filters
- **Filters**: Email, name, tags, location, order history, spending
- **Considerations**: Search performance, result relevance

### Individual Customer Lookup
- **Use**: `customer` query with ID
- **Use case**: Complete customer profile with order history
- **Considerations**: Data completeness, privacy concerns

### Customer Analytics
- **Use**: `customersCount` query
- **Use case**: Customer segmentation, business metrics
- **Considerations**: Filter accuracy, real-time data needs

### Customer Communication
- **Use**: `customers` query with contact filters
- **Use case**: Marketing campaigns, customer service
- **Considerations**: Communication preferences, consent management

### Customer Data Export
- **Use**: `customers` query with pagination
- **Use case**: Data analysis, backup, migration
- **Considerations**: Data volume, export format requirements

## Search Query Examples

### Basic Customer Searches
- `email:@example.com` - Customers with specific email domain
- `first_name:John` - Customers named John
- `country:United States` - Customers from specific country
- `tags:VIP` - Customers with VIP tag
- `orders_count:>10` - Customers with more than 10 orders

### Advanced Customer Searches
- `email:@example.com AND orders_count:>5` - Domain-specific high-value customers
- `created_at:>2024-01-01 AND country:Canada` - New Canadian customers
- `total_spent:>1000 AND tags:wholesale` - High-value wholesale customers
- `NOT tags:inactive AND last_order_at:>2024-06-01` - Active recent customers

### Customer Performance Queries
- `orders_count:>0 AND total_spent:>500` - Customers with significant purchase history
- `average_order_value:>200` - High average order value customers
- `last_order_at:<2024-01-01` - Customers who haven't ordered recently

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
