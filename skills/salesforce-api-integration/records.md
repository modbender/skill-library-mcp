# Records CRUD - Salesforce API

## Get Record by ID

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/001xx000003DGbYAAW" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

### Specific Fields Only

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/001xx000003DGbYAAW?fields=Id,Name,Industry" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Create Record

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Acme Corporation",
    "Industry": "Technology",
    "Website": "https://acme.com"
  }'
```

Response:
```json
{
  "id": "001xx000003NEWID",
  "success": true,
  "errors": []
}
```

### Create Contact

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Contact" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john.doe@example.com",
    "AccountId": "001xx000003DGbYAAW"
  }'
```

### Create Opportunity

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Opportunity" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "New Deal - Acme",
    "AccountId": "001xx000003DGbYAAW",
    "StageName": "Prospecting",
    "CloseDate": "2025-12-31",
    "Amount": 50000
  }'
```

## Update Record

```bash
curl -X PATCH "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/001xx000003DGbYAAW" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Industry": "Finance",
    "Website": "https://newsite.com"
  }'
```

Returns `204 No Content` on success.

## Delete Record

```bash
curl -X DELETE "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/001xx000003DGbYAAW" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

Returns `204 No Content` on success.

## Upsert (Insert or Update)

Using external ID field:

```bash
curl -X PATCH "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/External_ID__c/EXT123" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Acme Updated",
    "Industry": "Technology"
  }'
```

- Returns `201 Created` if inserted
- Returns `204 No Content` if updated

## Get Record by External ID

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/External_ID__c/EXT123" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Get Deleted Records

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/deleted/?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Get Updated Records

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/updated/?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Recently Viewed

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/recent/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Search with External IDs

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/External_ID__c" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["EXT001", "EXT002", "EXT003"]'
```

## Get Multiple Records

Using IDs:

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/composite/sobjects/Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["001xx000003ABC", "001xx000003DEF"],
    "fields": ["Id", "Name", "Industry"]
  }'
```
