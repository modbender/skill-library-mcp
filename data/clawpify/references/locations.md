# Shopify Locations

Manage inventory locations for fulfillment via the GraphQL Admin API.

## Overview

Locations are physical places where you stock inventory and fulfill orders from. Each location can have different inventory levels and fulfillment settings.

## List Locations

```graphql
query ListLocations($first: Int!, $includeInactive: Boolean) {
  locations(first: $first, includeInactive: $includeInactive) {
    nodes {
      id
      name
      isActive
      fulfillsOnlineOrders
      address {
        address1
        address2
        city
        province
        country
        zip
        phone
      }
    }
  }
}
```
Variables: `{ "first": 20, "includeInactive": false }`

## Get Location

```graphql
query GetLocation($id: ID!) {
  location(id: $id) {
    id
    name
    isActive
    isPrimary
    fulfillsOnlineOrders
    hasActiveInventory
    shipsInventory
    address {
      address1
      address2
      city
      province
      provinceCode
      country
      countryCode
      zip
      phone
    }
    localPickupSettingsV2 {
      instructions
      pickupTime
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Location/123" }`

## Get Locations Count

```graphql
query GetLocationsCount {
  locationsCount {
    count
  }
}
```

## Add Location

```graphql
mutation AddLocation($input: LocationAddInput!) {
  locationAdd(input: $input) {
    location {
      id
      name
      address {
        address1
        city
        country
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
    "name": "New York Warehouse",
    "address": {
      "address1": "123 Warehouse Ave",
      "city": "New York",
      "provinceCode": "NY",
      "countryCode": "US",
      "zip": "10001",
      "phone": "+1-212-555-0100"
    },
    "fulfillsOnlineOrders": true
  }
}
```

## Edit Location

```graphql
mutation EditLocation($id: ID!, $input: LocationEditInput!) {
  locationEdit(id: $id, input: $input) {
    location {
      id
      name
      address {
        address1
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
  "id": "gid://shopify/Location/123",
  "input": {
    "name": "NY Warehouse - Main",
    "address": {
      "phone": "+1-212-555-0200"
    }
  }
}
```

## Activate Location

```graphql
mutation ActivateLocation($locationId: ID!) {
  locationActivate(locationId: $locationId) {
    location {
      id
      isActive
    }
    userErrors {
      field
      message
    }
  }
}
```

## Deactivate Location

```graphql
mutation DeactivateLocation($locationId: ID!, $destinationLocationId: ID) {
  locationDeactivate(locationId: $locationId, destinationLocationId: $destinationLocationId) {
    location {
      id
      isActive
    }
    userErrors {
      field
      message
    }
  }
}
```

Note: When deactivating, inventory moves to the destination location.

## Delete Location

```graphql
mutation DeleteLocation($locationId: ID!) {
  locationDelete(locationId: $locationId) {
    deletedLocationId
    userErrors {
      field
      message
    }
  }
}
```

## Enable Local Pickup

```graphql
mutation EnableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
  locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
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
  "localPickupSettings": {
    "locationId": "gid://shopify/Location/123",
    "instructions": "Located at the back of the store. Ring the bell for assistance.",
    "pickupTime": "TWENTY_FOUR_HOURS"
  }
}
```

## Disable Local Pickup

```graphql
mutation DisableLocalPickup($locationId: ID!) {
  locationLocalPickupDisable(locationId: $locationId) {
    userErrors {
      field
      message
    }
  }
}
```

## Location by Identifier

```graphql
query GetLocationByIdentifier($identifier: LocationIdentifierInput!) {
  locationByIdentifier(identifier: $identifier) {
    id
    name
    isActive
  }
}
```
Variables:
```json
{
  "identifier": {
    "gid": "gid://shopify/Location/123"
  }
}
```

## Locations for Delivery Profiles

```graphql
query GetDeliveryLocations($first: Int!) {
  locationsAvailableForDeliveryProfilesConnection(first: $first) {
    nodes {
      id
      name
      fulfillsOnlineOrders
    }
  }
}
```

## Location Fields

| Field | Description |
|-------|-------------|
| `name` | Display name |
| `isActive` | Whether location is active |
| `isPrimary` | Default location for inventory |
| `fulfillsOnlineOrders` | Can fulfill online orders |
| `hasActiveInventory` | Has inventory tracked here |
| `shipsInventory` | Can ship from this location |
| `activatable` | Can be activated |
| `deactivatable` | Can be deactivated |
| `deletable` | Can be deleted |

## Local Pickup Times

| Value | Description |
|-------|-------------|
| `ONE_HOUR` | Ready in 1 hour |
| `TWO_HOURS` | Ready in 2 hours |
| `FOUR_HOURS` | Ready in 4 hours |
| `TWENTY_FOUR_HOURS` | Ready in 24 hours |
| `TWO_TO_FOUR_DAYS` | Ready in 2-4 days |
| `FIVE_OR_MORE_DAYS` | Ready in 5+ days |

## B2B Company Locations

For B2B businesses:

```graphql
query ListCompanyLocations($first: Int!) {
  companyLocations(first: $first) {
    nodes {
      id
      name
      company {
        id
        name
      }
      billingAddress {
        address1
        city
      }
      shippingAddress {
        address1
        city
      }
    }
  }
}
```

### Create Company Location

```graphql
mutation CreateCompanyLocation($companyId: ID!, $input: CompanyLocationInput!) {
  companyLocationCreate(companyId: $companyId, input: $input) {
    companyLocation {
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

## API Scopes Required

- `read_locations` - Read locations
- `write_locations` - Create, update, delete locations
- `read_inventory` - Read inventory at locations
- `write_inventory` - Manage inventory at locations

## Notes

- At least one location must remain active
- Deactivating transfers inventory to another location
- Primary location is the default for new inventory
- Location changes affect fulfillment order assignments
- Local pickup requires location address to be complete
