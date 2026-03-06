# HubSpot Associations API

Complete guide for linking CRM objects together.

## Core Concepts

### Association Types (v4 API)
- **1**: Contact → Company (Primary Company)
- **3**: Deal → Contact  
- **5**: Deal → Company
- **16**: Ticket → Contact
- **26**: Ticket → Company
- **279**: Deal → Ticket
- **Custom**: User-defined association types

### Association Labels
- Primary Company (contact's main company)
- Decision Maker (contact's role in deal)
- Account Manager (company owner)
- Support Contact (ticket assignee)

## Create Associations

### Associate Contact with Company
```bash
curl -X PUT "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID/associations/companies/COMPANY_ID/1" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Associate Deal with Contact
```bash
curl -X PUT "https://api.hubapi.com/crm/v3/objects/deals/DEAL_ID/associations/contacts/CONTACT_ID/3" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Associate Deal with Company
```bash
curl -X PUT "https://api.hubapi.com/crm/v3/objects/deals/DEAL_ID/associations/companies/COMPANY_ID/5" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Associate Ticket with Contact
```bash
curl -X PUT "https://api.hubapi.com/crm/v3/objects/tickets/TICKET_ID/associations/contacts/CONTACT_ID/16" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Create Association with Label (v4)
```bash
curl -X PUT "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "associationCategory": "HUBSPOT_DEFINED",
      "associationTypeId": 3,
      "label": "Decision Maker"
    }
  ]'
```

## Read Associations

### Get Contact's Associated Companies
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/contacts/CONTACT_ID/associations/companies"
```

### Get Deal's Associated Contacts
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/contacts"
```

### Get Company's Associated Deals
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/companies/COMPANY_ID/associations/deals"
```

### Get All Association Types for Object
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/contacts/CONTACT_ID/associations"
```

## Batch Associations

### Create Multiple Associations
```bash
curl -X POST "https://api.hubapi.com/crm/v4/associations/contacts/companies/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "from": {"id": "CONTACT_1"},
        "to": {"id": "COMPANY_1"},
        "types": [
          {
            "associationCategory": "HUBSPOT_DEFINED",
            "associationTypeId": 1
          }
        ]
      },
      {
        "from": {"id": "CONTACT_2"},
        "to": {"id": "COMPANY_1"},
        "types": [
          {
            "associationCategory": "HUBSPOT_DEFINED", 
            "associationTypeId": 1
          }
        ]
      }
    ]
  }'
```

### Delete Associations
```bash
curl -X DELETE "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID/associations/companies/COMPANY_ID/1" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Batch Delete Associations
```bash
curl -X POST "https://api.hubapi.com/crm/v4/associations/contacts/companies/batch/archive" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "from": {"id": "CONTACT_1"},
        "to": {"id": "COMPANY_1"},
        "types": [
          {
            "associationCategory": "HUBSPOT_DEFINED",
            "associationTypeId": 1
          }
        ]
      }
    ]
  }'
```

## Custom Association Types

### Create Custom Association Type
```bash
curl -X POST "https://api.hubapi.com/crm/v4/associations/contacts/deals/labels" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Technical Contact",
    "name": "technical_contact",
    "inverseLabel": "Technical Deal"
  }'
```

### List Custom Association Types
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/associations/contacts/deals/labels"
```

### Use Custom Association
```bash
curl -X PUT "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "associationCategory": "USER_DEFINED",
      "associationTypeId": CUSTOM_TYPE_ID,
      "label": "Technical Contact"
    }
  ]'
```

## Advanced Association Patterns

### Full Deal Setup with Associations
```bash
# 1. Create deal
DEAL_RESPONSE=$(curl -X POST "https://api.hubapi.com/crm/v3/objects/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealname": "Enterprise Deal",
      "amount": "100000"
    }
  }')

DEAL_ID=$(echo $DEAL_RESPONSE | jq -r '.id')

# 2. Associate with company
curl -X PUT "https://api.hubapi.com/crm/v3/objects/deals/$DEAL_ID/associations/companies/COMPANY_ID/5" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"

# 3. Associate with decision maker
curl -X PUT "https://api.hubapi.com/crm/v4/objects/deals/$DEAL_ID/associations/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "associationCategory": "HUBSPOT_DEFINED",
      "associationTypeId": 3,
      "label": "Decision Maker"
    }
  ]'
```

### Company Hierarchy Associations
```bash
# Set parent company relationship
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/companies/CHILD_COMPANY_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_parent_company_id": "PARENT_COMPANY_ID"
    }
  }'

# Get child companies
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_parent_company_id",
      "operator": "EQ",
      "value": "PARENT_COMPANY_ID"
    }]
  }'
```

## Multi-Object Queries with Associations

### Get Deal with All Associations
```bash
curl -X GET "https://api.hubapi.com/crm/v3/objects/deals/DEAL_ID?associations=contacts,companies,tickets" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Search Deals with Contact Info
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "dealstage",
      "operator": "EQ",
      "value": "qualifiedtobuy"
    }],
    "properties": ["dealname", "amount", "dealstage"],
    "associations": ["contacts", "companies"],
    "limit": 100
  }'
```

## Common Association Scenarios

### 1. Contact-Company Relationships
```bash
# Primary company (employee)
TYPE_ID=1

# Secondary company (consultant/contractor)  
TYPE_ID=279

# Past company (former employee)
TYPE_ID=280
```

### 2. Deal-Contact Roles
```bash
# Decision maker
TYPE_ID=3

# Influencer  
TYPE_ID=4

# Technical contact
TYPE_ID=CUSTOM_ID
```

### 3. Support Ticket Associations
```bash
# Primary contact (reporter)
TYPE_ID=16

# Company account
TYPE_ID=26

# Related deal
TYPE_ID=279
```

## Association Analytics

### Count Associations per Object
```bash
# Contacts per company
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": ["name", "num_associated_contacts"],
    "sorts": [{"propertyName": "num_associated_contacts", "direction": "DESCENDING"}]
  }'
```

### Find Orphaned Records
```bash
# Contacts without companies
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "num_associated_companies",
      "operator": "EQ",
      "value": "0"
    }],
    "properties": ["firstname", "lastname", "email"]
  }'
```

### Deals without Contacts
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "num_associated_contacts",
      "operator": "EQ", 
      "value": "0"
    }],
    "properties": ["dealname", "amount", "dealstage"]
  }'
```

## Error Handling

### Common Errors
- **400**: Invalid association type ID
- **404**: Object ID not found
- **409**: Association already exists (for unique types)

### Validation Before Association
```bash
# Check if objects exist before associating
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID" || echo "Contact not found"

curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/companies/COMPANY_ID" || echo "Company not found"
```

## Best Practices

### 1. Association Strategy
- Use primary company for main employer
- Use custom types for specific roles
- Document association meanings in your system

### 2. Data Integrity
- Validate object existence before associating
- Use batch operations for bulk associations
- Handle association errors gracefully

### 3. Performance
- Use v4 API for new implementations
- Batch association creates/deletes when possible
- Include associations in object queries when needed

### 4. Cleanup
- Remove associations when objects are archived
- Audit orphaned records regularly
- Update associations when relationships change

## HubSpot UI Tips

### Creating Associations in UI
1. Open any CRM record
2. Use "Associate" buttons in sidebar
3. Search and select related records
4. Custom association labels appear in dropdown

### Association Cards
1. View associated objects in record sidebar
2. Click to navigate to associated record
3. Edit association labels inline
4. Remove associations with X button

### Bulk Association
1. Select multiple records in list view
2. Use "More" → "Associate" actions
3. Choose association type and target objects
4. Confirm bulk association operation