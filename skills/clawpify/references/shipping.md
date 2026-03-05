# Shopify Shipping & Delivery

Manage delivery profiles, shipping zones, and rates via the GraphQL Admin API.

## Overview

Delivery profiles define shipping settings for products, including zones, rates, and fulfillment locations.

## List Delivery Profiles

```graphql
query ListDeliveryProfiles($first: Int!) {
  deliveryProfiles(first: $first) {
    nodes {
      id
      name
      default
      profileLocationGroups {
        locationGroup {
          id
          locations(first: 5) {
            nodes {
              name
            }
          }
        }
        locationGroupZones(first: 10) {
          nodes {
            zone {
              id
              name
              countries {
                code {
                  countryCode
                }
                provinces {
                  code
                  name
                }
              }
            }
            methodDefinitions(first: 5) {
              nodes {
                id
                name
                active
                rateProvider {
                  ... on DeliveryRateDefinition {
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## Get Delivery Profile

```graphql
query GetDeliveryProfile($id: ID!) {
  deliveryProfile(id: $id) {
    id
    name
    default
    profileItems(first: 20) {
      nodes {
        product {
          id
          title
        }
        variants(first: 5) {
          nodes {
            id
            title
          }
        }
      }
    }
    profileLocationGroups {
      locationGroup {
        locations(first: 10) {
          nodes {
            id
            name
          }
        }
      }
      locationGroupZones(first: 10) {
        nodes {
          zone {
            name
          }
          methodDefinitions(first: 5) {
            nodes {
              name
              active
            }
          }
        }
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/DeliveryProfile/123" }`

## Create Delivery Profile

```graphql
mutation CreateDeliveryProfile($profile: DeliveryProfileInput!) {
  deliveryProfileCreate(profile: $profile) {
    profile {
      id
      name
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
  "profile": {
    "name": "Heavy Items",
    "locationGroupsToCreate": [
      {
        "locations": ["gid://shopify/Location/123"],
        "zonesToCreate": [
          {
            "name": "Domestic",
            "countries": [
              {
                "code": "US",
                "includeAllProvinces": true
              }
            ],
            "methodDefinitionsToCreate": [
              {
                "name": "Standard Shipping",
                "active": true,
                "rateDefinition": {
                  "price": {
                    "amount": "9.99",
                    "currencyCode": "USD"
                  }
                }
              },
              {
                "name": "Express Shipping",
                "active": true,
                "rateDefinition": {
                  "price": {
                    "amount": "19.99",
                    "currencyCode": "USD"
                  }
                }
              }
            ]
          }
        ]
      }
    ],
    "variantsToAssociate": [
      "gid://shopify/ProductVariant/456",
      "gid://shopify/ProductVariant/789"
    ]
  }
}
```

## Update Delivery Profile

```graphql
mutation UpdateDeliveryProfile($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile {
      id
      name
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
  "id": "gid://shopify/DeliveryProfile/123",
  "profile": {
    "name": "Heavy Items - Updated",
    "locationGroupsToUpdate": [
      {
        "id": "gid://shopify/DeliveryLocationGroup/456",
        "zonesToCreate": [
          {
            "name": "Canada",
            "countries": [
              {
                "code": "CA",
                "includeAllProvinces": true
              }
            ],
            "methodDefinitionsToCreate": [
              {
                "name": "Canada Standard",
                "active": true,
                "rateDefinition": {
                  "price": {
                    "amount": "14.99",
                    "currencyCode": "USD"
                  }
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## Delete Delivery Profile

```graphql
mutation DeleteDeliveryProfile($id: ID!) {
  deliveryProfileRemove(id: $id) {
    job {
      id
      done
    }
    userErrors {
      field
      message
    }
  }
}
```

## Add Products to Profile

```graphql
mutation AddProductsToProfile($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile {
      id
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
  "id": "gid://shopify/DeliveryProfile/123",
  "profile": {
    "variantsToAssociate": [
      "gid://shopify/ProductVariant/111",
      "gid://shopify/ProductVariant/222"
    ]
  }
}
```

## Remove Products from Profile

```graphql
mutation RemoveProductsFromProfile($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile {
      id
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
  "id": "gid://shopify/DeliveryProfile/123",
  "profile": {
    "variantsToDissociate": [
      "gid://shopify/ProductVariant/111"
    ]
  }
}
```

## Rate Types

### Flat Rate
```json
{
  "rateDefinition": {
    "price": {
      "amount": "9.99",
      "currencyCode": "USD"
    }
  }
}
```

### Weight-Based Rate
```json
{
  "weightConditionsToCreate": [
    {
      "criteria": {
        "unit": "KILOGRAMS",
        "value": 5.0
      },
      "operator": "LESS_THAN_OR_EQUAL_TO"
    }
  ],
  "rateDefinition": {
    "price": {
      "amount": "9.99",
      "currencyCode": "USD"
    }
  }
}
```

### Price-Based Rate
```json
{
  "priceConditionsToCreate": [
    {
      "criteria": {
        "amount": "50.00",
        "currencyCode": "USD"
      },
      "operator": "GREATER_THAN_OR_EQUAL_TO"
    }
  ],
  "rateDefinition": {
    "price": {
      "amount": "0.00",
      "currencyCode": "USD"
    }
  }
}
```

## Delivery Zone Structure

| Component | Description |
|-----------|-------------|
| **Profile** | Top-level shipping configuration |
| **Location Group** | Group of fulfillment locations |
| **Zone** | Geographic region (countries/provinces) |
| **Method Definition** | Shipping option with rate |

## Country Code Examples

| Code | Country |
|------|---------|
| `US` | United States |
| `CA` | Canada |
| `GB` | United Kingdom |
| `AU` | Australia |
| `DE` | Germany |
| `FR` | France |

## Condition Operators

| Operator | Description |
|----------|-------------|
| `GREATER_THAN` | > value |
| `GREATER_THAN_OR_EQUAL_TO` | >= value |
| `LESS_THAN` | < value |
| `LESS_THAN_OR_EQUAL_TO` | <= value |
| `BETWEEN` | Between two values |

## API Scopes Required

- `read_shipping` - Read delivery profiles
- `write_shipping` - Create, update, delete delivery profiles

## Notes

- Default profile applies to products not in other profiles
- Products can only belong to one delivery profile
- Zones define geographic areas for shipping
- Rates can be flat, weight-based, or price-based
- Multiple locations can share the same zone configuration
- Carrier-calculated rates require additional setup
