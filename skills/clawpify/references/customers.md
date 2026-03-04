# Shopify Customers

## List Customers

```graphql
query ListCustomers($first: Int!, $after: String, $query: String) {
  customers(first: $first, after: $after, query: $query) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      displayName
      defaultEmailAddress {
        emailAddress
      }
      defaultPhoneNumber {
        phoneNumber
      }
      createdAt
      numberOfOrders
      amountSpent {
        amount
        currencyCode
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

Customer query syntax:
- `email:*@gmail.com` - by email pattern
- `number_of_orders:>5` - by order count
- `amount_spent:>100` - by total spent

## Get Customer by ID

```graphql
query GetCustomer($id: ID!) {
  customer(id: $id) {
    id
    displayName
    firstName
    lastName
    defaultEmailAddress {
      emailAddress
    }
    defaultPhoneNumber {
      phoneNumber
    }
    createdAt
    numberOfOrders
    amountSpent {
      amount
      currencyCode
    }
    tags
    addresses {
      address1
      address2
      city
      province
      country
      zip
    }
    orders(first: 10) {
      nodes {
        id
        name
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Customer/123" }`

## Create Customer

```graphql
mutation CreateCustomer($input: CustomerInput!) {
  customerCreate(input: $input) {
    customer {
      id
      displayName
      defaultEmailAddress {
        emailAddress
      }
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
  "input": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "tags": ["vip"]
  }
}
```

## Update Customer

```graphql
mutation UpdateCustomer($input: CustomerInput!) {
  customerUpdate(input: $input) {
    customer {
      id
      tags
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
  "input": {
    "id": "gid://shopify/Customer/123",
    "tags": ["vip", "wholesale"]
  }
}
```
