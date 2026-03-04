# Metadata and Schema - Salesforce API

## List All Objects

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Describe Object

Get full schema including fields, relationships, picklist values:

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/describe" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

Response includes:
- `fields[]` - All field definitions
- `childRelationships[]` - Related child objects
- `recordTypeInfos[]` - Available record types
- `urls{}` - API endpoints for this object

## Describe Field

Get specific field details:

```bash
# Via describe (filter response)
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/describe" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" | jq '.fields[] | select(.name=="Industry")'
```

## Field Types

| Type | Example | Notes |
|------|---------|-------|
| id | `001xx000003ABC` | 15 or 18 char ID |
| string | `"Acme Corp"` | Text field |
| textarea | `"Long text..."` | Long text |
| boolean | `true` / `false` | Checkbox |
| int | `42` | Integer |
| double | `3.14159` | Decimal |
| currency | `1000.00` | Money amount |
| percent | `25.5` | Percentage |
| date | `"2024-12-31"` | Date only |
| datetime | `"2024-12-31T14:30:00.000Z"` | Date and time |
| time | `"14:30:00.000Z"` | Time only |
| email | `"user@example.com"` | Email address |
| phone | `"+1-555-123-4567"` | Phone number |
| url | `"https://example.com"` | Website |
| picklist | `"Technology"` | Single select |
| multipicklist | `"A;B;C"` | Multi-select (semicolon separated) |
| reference | `"001xx000003ABC"` | Lookup/Master-Detail |

## Get Picklist Values

```bash
# From describe
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/describe" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" | jq '.fields[] | select(.name=="Industry") | .picklistValues'
```

## Record Types

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/describe" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" | jq '.recordTypeInfos'
```

## Page Layouts

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/describe/layouts" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Compact Layouts

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/describe/compactLayouts" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Global Describe

Summary of all objects:

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## API Limits

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/limits/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

Response includes:
- `DailyApiRequests`
- `DailyBulkApiRequests`
- `DailyStreamingApiEvents`
- `DataStorageMB`
- `FileStorageMB`

## API Versions

```bash
curl "$SF_INSTANCE_URL/services/data/"
```

## Resources

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Tooling API

For metadata like Apex classes, triggers:

```bash
# List Apex classes
curl "$SF_INSTANCE_URL/services/data/v59.0/tooling/sobjects/ApexClass" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"

# Query Apex classes
curl "$SF_INSTANCE_URL/services/data/v59.0/tooling/query/?q=SELECT+Id,Name,Status+FROM+ApexClass" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"

# Describe tooling object
curl "$SF_INSTANCE_URL/services/data/v59.0/tooling/sobjects/ApexClass/describe" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Custom Metadata Types

```bash
# List custom metadata types
curl "$SF_INSTANCE_URL/services/data/v59.0/tooling/query/?q=SELECT+DeveloperName,Label+FROM+CustomObject+WHERE+DeveloperName+LIKE+'%__mdt'" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```
