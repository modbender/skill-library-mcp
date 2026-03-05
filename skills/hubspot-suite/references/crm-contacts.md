# HubSpot Contacts API

Complete guide for contact management via API.

## Core Operations

### Create Contact
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "email": "john.doe@example.com",
      "firstname": "John",
      "lastname": "Doe",
      "phone": "+1-555-123-4567",
      "company": "ACME Corp",
      "website": "https://example.com",
      "jobtitle": "VP Sales",
      "lifecyclestage": "lead"
    }
  }'
```

### Get Contact by ID
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts/12345?properties=email,firstname,lastname,phone,company"
```

### Update Contact
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "phone": "+1-555-999-8888",
      "lifecyclestage": "customer"
    }
  }'
```

### Delete (Archive) Contact
```bash
curl -X DELETE "https://api.hubapi.com/crm/v3/objects/contacts/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Batch Operations

### Create Multiple Contacts (Max 100)
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "email": "alice@company.com",
          "firstname": "Alice",
          "lastname": "Smith"
        }
      },
      {
        "properties": {
          "email": "bob@company.com", 
          "firstname": "Bob",
          "lastname": "Johnson"
        }
      }
    ]
  }'
```

### Batch Update
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/update" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "id": "12345",
        "properties": {"lifecyclestage": "customer"}
      },
      {
        "id": "67890", 
        "properties": {"lifecyclestage": "opportunity"}
      }
    ]
  }'
```

### Batch Read by IDs
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/read" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"id": "12345"},
      {"id": "67890"}
    ],
    "properties": ["email", "firstname", "lastname", "phone"]
  }'
```

## Search & Filtering

### Search by Email
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "email",
      "operator": "EQ",
      "value": "john@example.com"
    }],
    "properties": ["email", "firstname", "lastname"],
    "limit": 10
  }'
```

### Advanced Search - Recent Leads
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "lifecyclestage",
        "operator": "EQ", 
        "value": "lead"
      },
      {
        "propertyName": "createdate",
        "operator": "GTE",
        "value": "'$(date -u -d '30 days ago' '+%Y-%m-%d')'"
      }
    ],
    "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
    "properties": ["email", "firstname", "lastname", "createdate", "lifecyclestage"],
    "limit": 100
  }'
```

### Search by Company
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "company",
      "operator": "CONTAINS_TOKEN",
      "value": "ACME"
    }]
  }'
```

## List All Contacts (Paginated)

### First Page
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?properties=email,firstname,lastname&limit=100"
```

### Next Page (use `after` from previous response)
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?properties=email,firstname,lastname&limit=100&after=12345"
```

## Contact Merge

### Merge Two Contacts
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/merge" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "primaryObjectId": "12345",
    "objectIdToMerge": "67890"
  }'
```

## Common Properties

### Standard Properties
- `email` (unique identifier)
- `firstname`, `lastname`
- `phone`, `mobilephone`
- `company`, `jobtitle`
- `website`, `city`, `state`, `country`
- `lifecyclestage` (subscriber, lead, mql, sql, opportunity, customer, evangelist, other)
- `hs_lead_status` (new, open, in_progress, open_deal, unqualified, attempted_to_contact, connected, bad_timing)

### Calculated Properties (Read-only)
- `createdate`, `lastmodifieddate`
- `hs_object_id` (HubSpot ID)
- `num_associated_deals`
- `total_revenue`

### Get All Available Properties
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/contacts"
```

## Contact by Email (Alternative Method)

### Get Contact by Email
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/contacts/v1/contact/email/john@example.com/profile"
```

### Update Contact by Email
```bash
curl -X POST "https://api.hubapi.com/contacts/v1/contact/email/john@example.com/profile" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": [
      {"property": "firstname", "value": "John"},
      {"property": "lastname", "value": "Doe"}
    ]
  }'
```

## Associations

### Get Contact's Companies
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/contacts/12345/associations/companies"
```

### Get Contact's Deals
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/contacts/12345/associations/deals"
```

## Lifecycle Stage Automation

### Move Through Lifecycle Stages
```bash
# Lead → MQL
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"lifecyclestage": "marketingqualifiedlead"}}'

# MQL → SQL  
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"lifecyclestage": "salesqualifiedlead"}}'
```

## Data Quality Helpers

### Find Contacts with Missing Email
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "email",
      "operator": "NOT_HAS_PROPERTY"
    }],
    "limit": 100
  }'
```

### Find Recent Unqualified Leads
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_lead_status",
        "operator": "EQ",
        "value": "unqualified"
      },
      {
        "propertyName": "lastmodifieddate", 
        "operator": "GTE",
        "value": "'$(date -u -d '7 days ago' '+%Y-%m-%d')'"
      }
    ]
  }'
```

## Error Handling

### Common Errors
- **400**: Invalid property name/value
- **409**: Contact with email already exists (use PATCH to update)
- **404**: Contact ID not found

### Handling Duplicates
HubSpot prevents duplicate emails. To handle:
1. Try POST (create)
2. If 409 error, search by email to get ID
3. Use PATCH to update existing contact

## HubSpot UI Tips

### Creating Contacts in UI
1. Contacts → Create contact
2. Fill required fields (email is unique)
3. Use "Company" field to auto-associate

### Import from CSV
1. Contacts → Import
2. Upload CSV with email column
3. Map columns to HubSpot properties
4. Review and import

### Contact Views
1. Create saved views with filters
2. Use "All contacts" for broad searches
3. "My contacts" for owner-specific views

### Contact Quality Score
- Email formatting validation
- Phone number validation  
- Company domain matching
- Duplicate detection alerts