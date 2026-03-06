# HubSpot Companies API

Complete guide for company record management.

## Core Operations

### Create Company
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "name": "ACME Corporation",
      "domain": "acme.com",
      "industry": "Technology",
      "phone": "+1-555-123-4567", 
      "city": "San Francisco",
      "state": "California",
      "country": "United States",
      "website": "https://acme.com",
      "numberofemployees": "500",
      "annualrevenue": "10000000",
      "type": "PROSPECT"
    }
  }'
```

### Get Company by ID
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/companies/12345?properties=name,domain,industry,phone,numberofemployees"
```

### Update Company
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/companies/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "numberofemployees": "750",
      "annualrevenue": "15000000",
      "type": "CUSTOMER"
    }
  }'
```

### Delete Company
```bash
curl -X DELETE "https://api.hubapi.com/crm/v3/objects/companies/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Batch Operations

### Create Multiple Companies
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "name": "TechCorp Inc",
          "domain": "techcorp.com",
          "industry": "Software"
        }
      },
      {
        "properties": {
          "name": "DataSystems LLC",
          "domain": "datasystems.com", 
          "industry": "Data Processing"
        }
      }
    ]
  }'
```

### Batch Update Companies
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/batch/update" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "id": "12345",
        "properties": {"type": "CUSTOMER"}
      },
      {
        "id": "67890",
        "properties": {"type": "PARTNER"}
      }
    ]
  }'
```

## Search & Filtering

### Search by Domain
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "domain",
      "operator": "EQ",
      "value": "acme.com"
    }],
    "properties": ["name", "domain", "industry"],
    "limit": 10
  }'
```

### Search by Industry
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "industry",
      "operator": "CONTAINS_TOKEN",
      "value": "Technology"
    }],
    "properties": ["name", "domain", "industry", "numberofemployees"]
  }'
```

### Large Companies (500+ Employees)
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "numberofemployees",
      "operator": "GTE",
      "value": "500"
    }],
    "sorts": [{"propertyName": "numberofemployees", "direction": "DESCENDING"}],
    "properties": ["name", "domain", "numberofemployees", "annualrevenue"],
    "limit": 50
  }'
```

### Companies by Revenue Range
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "annualrevenue",
      "operator": "BETWEEN",
      "value": "1000000",
      "highValue": "10000000"
    }],
    "properties": ["name", "domain", "annualrevenue", "industry"]
  }'
```

## Company Hierarchies & Relationships

### Set Parent Company
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/companies/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_parent_company_id": "67890"
    }
  }'
```

### Get Child Companies
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_parent_company_id",
      "operator": "EQ",
      "value": "67890"
    }],
    "properties": ["name", "domain", "hs_parent_company_id"]
  }'
```

## Company Associations

### Get Associated Contacts
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/companies/12345/associations/contacts"
```

### Get Associated Deals
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/companies/12345/associations/deals"
```

### Associate Company with Contact
```bash
# Association type 1 = contact→company
curl -X PUT "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID/associations/companies/COMPANY_ID/1" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Company Enrichment

### Auto-populate from Domain
HubSpot can auto-enrich company data from domain. Create with domain only:
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "domain": "salesforce.com"
    }
  }'
```

### Company Insights (Read-only)
These properties are auto-populated:
- `hs_total_deal_value` - Sum of associated deals
- `num_associated_contacts` - Contact count
- `num_associated_deals` - Deal count
- `recent_deal_close_date` - Most recent deal close
- `web_technologies` - Detected website technologies

## Standard Properties

### Required/Key Properties
- `name` (company name)
- `domain` (website domain, unique identifier)

### Company Details
- `industry`, `type` (prospect/customer/partner/etc)
- `phone`, `fax`
- `address`, `city`, `state`, `zip`, `country`
- `website`, `domain`
- `description`, `about_us`

### Company Size & Revenue
- `numberofemployees` (numeric string)
- `annualrevenue` (numeric string in cents)
- `founded_year`

### Sales & Marketing
- `lifecyclestage` (subscriber, lead, mql, sql, opportunity, customer, evangelist, other)
- `hs_lead_status`
- `hubspot_owner_id` (assigned user)

### Get All Company Properties
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/companies"
```

## List All Companies

### Basic List
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/companies?properties=name,domain,industry&limit=100"
```

### With Pagination
```bash
# Get next page using 'after' from previous response
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/companies?properties=name,domain,industry&limit=100&after=12345"
```

## Company Analytics

### Recently Created Companies
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "createdate",
      "operator": "GTE",
      "value": "'$(date -u -d '30 days ago' '+%Y-%m-%d')'"
    }],
    "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
    "properties": ["name", "domain", "createdate", "industry"]
  }'
```

### Companies by Owner
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hubspot_owner_id",
      "operator": "EQ",
      "value": "12345"
    }],
    "properties": ["name", "domain", "hubspot_owner_id"]
  }'
```

## Data Quality

### Find Companies Missing Key Data
```bash
# Missing industry
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "industry",
      "operator": "NOT_HAS_PROPERTY"
    }],
    "properties": ["name", "domain"]
  }'
```

### Find Duplicate Domains
Use search to find companies with same domain (requires custom dedup logic).

## Company Import Best Practices

### CSV Headers for Import
```csv
name,domain,industry,phone,city,state,country,numberofemployees,annualrevenue,type
```

### Domain Normalization
- Remove `http://`, `https://`, `www.`  
- Use root domain: `company.com` not `blog.company.com`
- Lowercase formatting

## HubSpot UI Tips

### Creating Companies
1. Companies → Create company
2. Enter company name and domain
3. HubSpot may auto-suggest existing companies
4. Domain triggers data enrichment

### Company Hierarchy Setup
1. Go to parent company record
2. In "Child companies" section, click "Add"
3. Search and select child companies
4. Alternatively, edit child company and set parent

### Company Scoring
Set up company scoring based on:
- Industry fit
- Company size (employees)
- Revenue range
- Technology stack
- Website traffic

### Bulk Operations in UI
1. Companies → Select multiple records
2. Use "More" dropdown for bulk actions:
   - Assign owner
   - Add to list
   - Update properties
   - Delete/archive

### Company Insights
HubSpot automatically tracks:
- Website visits from company domain
- Email engagement from company contacts  
- Form submissions
- Recent activity timeline