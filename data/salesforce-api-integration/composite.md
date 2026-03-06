# Composite API - Salesforce API

Execute multiple operations in a single request.

## Composite Request

Up to 25 subrequests in one call:

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "allOrNone": true,
    "compositeRequest": [
      {
        "method": "POST",
        "url": "/services/data/v59.0/sobjects/Account",
        "referenceId": "newAccount",
        "body": {"Name": "Acme Corp"}
      },
      {
        "method": "POST",
        "url": "/services/data/v59.0/sobjects/Contact",
        "referenceId": "newContact",
        "body": {
          "LastName": "Smith",
          "AccountId": "@{newAccount.id}"
        }
      }
    ]
  }'
```

- `allOrNone`: true = rollback all if any fails
- `referenceId`: Reference results in later requests with `@{refId.field}`

## Batch Request

Execute multiple independent requests:

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite/batch" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batchRequests": [
      {
        "method": "GET",
        "url": "v59.0/sobjects/Account/001xxx"
      },
      {
        "method": "GET",
        "url": "v59.0/sobjects/Contact/003xxx"
      }
    ]
  }'
```

## SObject Tree (Create Related Records)

Create parent and children in one request:

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite/tree/Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "attributes": {"type": "Account", "referenceId": "ref1"},
        "Name": "Parent Account",
        "Contacts": {
          "records": [
            {
              "attributes": {"type": "Contact", "referenceId": "ref2"},
              "LastName": "Smith"
            },
            {
              "attributes": {"type": "Contact", "referenceId": "ref3"},
              "LastName": "Jones"
            }
          ]
        }
      }
    ]
  }'
```

Response includes IDs for all created records.

## SObject Collections

### Create Multiple Records

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite/sobjects" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "allOrNone": false,
    "records": [
      {
        "attributes": {"type": "Account"},
        "Name": "Account 1"
      },
      {
        "attributes": {"type": "Account"},
        "Name": "Account 2"
      }
    ]
  }'
```

### Update Multiple Records

```bash
curl -X PATCH "$SF_INSTANCE_URL/services/data/v59.0/composite/sobjects" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "allOrNone": false,
    "records": [
      {
        "attributes": {"type": "Account"},
        "Id": "001xxx",
        "Industry": "Technology"
      },
      {
        "attributes": {"type": "Account"},
        "Id": "001yyy",
        "Industry": "Finance"
      }
    ]
  }'
```

### Delete Multiple Records

```bash
curl -X DELETE "$SF_INSTANCE_URL/services/data/v59.0/composite/sobjects?ids=001xxx,001yyy&allOrNone=false" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

### Get Multiple Records

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite/sobjects/Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["001xxx", "001yyy"],
    "fields": ["Id", "Name", "Industry"]
  }'
```

## Composite Graph

Complex operations with dependencies:

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite/graph" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "graphs": [
      {
        "graphId": "graph1",
        "compositeRequest": [
          {
            "method": "POST",
            "url": "/services/data/v59.0/sobjects/Account",
            "referenceId": "newAccount",
            "body": {"Name": "Graph Account"}
          }
        ]
      }
    ]
  }'
```

## Limits

| Operation | Limit |
|-----------|-------|
| Composite subrequests | 25 |
| Batch requests | 25 |
| SObject Collections | 200 records |
| SObject Tree | 200 records total |
| Composite Graph | 500 nodes |
