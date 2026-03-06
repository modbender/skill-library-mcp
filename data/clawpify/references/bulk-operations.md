# Shopify Bulk Operations

Run large queries and mutations asynchronously via the GraphQL Admin API.

## Overview

Bulk operations handle large data sets efficiently by processing requests asynchronously and returning results in JSONL files.

## Run Bulk Query

```graphql
mutation RunBulkQuery($query: String!) {
  bulkOperationRunQuery(query: $query) {
    bulkOperation {
      id
      status
      url
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "query": "{ products { edges { node { id title variants { edges { node { id title sku } } } } } } }"
}
```

## Example Bulk Queries

### Export All Products

```graphql
mutation ExportProducts {
  bulkOperationRunQuery(query: """
    {
      products {
        edges {
          node {
            id
            title
            handle
            status
            vendor
            productType
            tags
            variants {
              edges {
                node {
                  id
                  title
                  sku
                  price
                  inventoryQuantity
                }
              }
            }
          }
        }
      }
    }
  """) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

### Export All Orders

```graphql
mutation ExportOrders {
  bulkOperationRunQuery(query: """
    {
      orders {
        edges {
          node {
            id
            name
            createdAt
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            customer {
              id
              displayName
            }
            lineItems {
              edges {
                node {
                  title
                  quantity
                  variant {
                    sku
                  }
                }
              }
            }
          }
        }
      }
    }
  """) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

### Export Customers

```graphql
mutation ExportCustomers {
  bulkOperationRunQuery(query: """
    {
      customers {
        edges {
          node {
            id
            displayName
            defaultEmailAddress {
              emailAddress
            }
            numberOfOrders
            amountSpent {
              amount
              currencyCode
            }
          }
        }
      }
    }
  """) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

## Check Bulk Operation Status

```graphql
query GetBulkOperation($id: ID!) {
  node(id: $id) {
    ... on BulkOperation {
      id
      status
      errorCode
      objectCount
      fileSize
      url
      partialDataUrl
      createdAt
      completedAt
    }
  }
}
```
Variables: `{ "id": "gid://shopify/BulkOperation/123" }`

## Get Current Bulk Operation

```graphql
query GetCurrentBulkOperation {
  currentBulkOperation {
    id
    status
    errorCode
    createdAt
    completedAt
    objectCount
    fileSize
    url
    query
  }
}
```

## List Bulk Operations

```graphql
query ListBulkOperations($first: Int!) {
  bulkOperations(first: $first, sortKey: CREATED_AT, reverse: true) {
    nodes {
      id
      status
      type
      createdAt
      completedAt
      objectCount
      fileSize
    }
  }
}
```
Variables: `{ "first": 10 }`

## Cancel Bulk Operation

```graphql
mutation CancelBulkOperation($id: ID!) {
  bulkOperationCancel(id: $id) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

## Run Bulk Mutation

First, upload JSONL data using staged uploads, then run the mutation.

### Step 1: Create Staged Upload

```graphql
mutation CreateStagedUpload {
  stagedUploadsCreate(input: {
    resource: BULK_MUTATION_VARIABLES
    filename: "bulk_input.jsonl"
    mimeType: "text/jsonl"
    httpMethod: POST
  }) {
    stagedTargets {
      url
      resourceUrl
      parameters {
        name
        value
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

### Step 2: Run Bulk Mutation

```graphql
mutation RunBulkMutation($mutation: String!, $stagedUploadPath: String!) {
  bulkOperationRunMutation(mutation: $mutation, stagedUploadPath: $stagedUploadPath) {
    bulkOperation {
      id
      status
      url
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "mutation": "mutation UpdateProduct($input: ProductInput!) { productUpdate(input: $input) { product { id } userErrors { field message } } }",
  "stagedUploadPath": "tmp/bulk_input.jsonl"
}
```

### Example JSONL Input for Bulk Mutation

Each line is a separate mutation input:

```jsonl
{"input": {"id": "gid://shopify/Product/1", "title": "Updated Title 1"}}
{"input": {"id": "gid://shopify/Product/2", "title": "Updated Title 2"}}
{"input": {"id": "gid://shopify/Product/3", "title": "Updated Title 3"}}
```

## Bulk Operation Status

| Status | Description |
|--------|-------------|
| `CREATED` | Operation created, not started |
| `RUNNING` | Currently processing |
| `COMPLETED` | Finished successfully |
| `CANCELING` | Being cancelled |
| `CANCELED` | Cancelled |
| `FAILED` | Failed with error |
| `EXPIRED` | Results expired (7 days) |

## Error Codes

| Code | Description |
|------|-------------|
| `ACCESS_DENIED` | Insufficient permissions |
| `INTERNAL_SERVER_ERROR` | Server error |
| `TIMEOUT` | Operation timed out |

## JSONL Output Format

Results are in JSONL (JSON Lines) format:

```jsonl
{"id":"gid://shopify/Product/1","title":"Product 1","__parentId":null}
{"id":"gid://shopify/ProductVariant/1","title":"Default","__parentId":"gid://shopify/Product/1"}
{"id":"gid://shopify/Product/2","title":"Product 2","__parentId":null}
```

The `__parentId` field links nested objects to their parent.

## Polling Strategy

```javascript
// Pseudo-code for polling
async function pollBulkOperation(operationId) {
  let status = 'RUNNING';
  let delay = 1000; // Start with 1 second
  
  while (status === 'RUNNING' || status === 'CREATED') {
    await sleep(delay);
    const result = await queryBulkOperation(operationId);
    status = result.status;
    
    if (status === 'COMPLETED') {
      return result.url; // Download URL for results
    }
    
    // Exponential backoff, max 30 seconds
    delay = Math.min(delay * 2, 30000);
  }
  
  throw new Error(`Bulk operation failed: ${status}`);
}
```

## Limits

| Limit | Value |
|-------|-------|
| Concurrent query operations | 1 per shop |
| Concurrent mutation operations | 1 per shop |
| Result availability | 7 days |
| Max connections per query | 5 |
| Max nesting depth | 2 levels |

## API Scopes Required

- Depends on the resources being queried/mutated
- `read_products` for product queries
- `write_products` for product mutations
- etc.

## Notes

- One bulk query and one bulk mutation can run simultaneously
- Results are available for 7 days after completion
- Use `__parentId` to reconstruct nested relationships
- Bulk operations bypass rate limits but have their own constraints
- Download and process results before they expire
- Mutations require staged upload with JSONL input
