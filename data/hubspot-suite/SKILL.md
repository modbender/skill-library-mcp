---
name: hubspot-suite
description: "Comprehensive HubSpot CRM, Marketing, Sales, Service, and CMS management suite. Covers all HubSpot APIs: CRM objects (contacts, companies, deals, tickets, custom objects), associations, properties, engagements (calls, emails, meetings, notes, tasks), workflows & automation, lists, forms, email marketing, reporting & analytics, data quality & dedup, import/export, webhooks, pipelines, owners, CMS content, conversations, and commerce. Supports both Private App (API key) authentication and the new HubSpot Developer Platform (CLI-based apps). Use for ANY HubSpot-related task including CRM management, marketing automation, sales pipeline management, data migration, reporting, data quality audits, or HubSpot administration."
metadata:
  openclaw:
    requires:
      env:
        - HUBSPOT_ACCESS_TOKEN
    primaryCredential: HUBSPOT_ACCESS_TOKEN
---

# HubSpot Suite - Complete CRM & Marketing Platform

The ultimate HubSpot skill covering ALL aspects of the platform: CRM, Marketing, Sales, Service, CMS, and Developer tools.

## Quick Start

### 1. Authentication Setup
```bash
# Private App (Recommended)
export HUBSPOT_ACCESS_TOKEN="pat-na1-xxx"  # or pat-eu1-xxx

# Legacy API Key
export HUBSPOT_API_KEY="your-api-key"
```

See `references/auth-setup.md` for complete authentication guide including new Developer Platform.

### 2. Basic API Test
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
```

## What Do You Want To Do?

**CRM Management:**
- `references/crm-contacts.md` → Create, update, search contacts
- `references/crm-companies.md` → Company records, hierarchies
- `references/crm-deals.md` → Sales pipeline, deal stages
- `references/crm-tickets.md` → Support tickets, SLA management
- `references/crm-custom-objects.md` → Custom object schemas

**Data & Associations:**
- `references/associations.md` → Link records (contact→company, deal→contact)
- `references/properties.md` → Custom properties, field groups
- `references/data-quality.md` → Deduplication, data cleanup
- `references/import-export.md` → Bulk data migration

**Activities & Automation:**
- `references/engagements.md` → Log calls, emails, meetings, tasks
- `references/workflows.md` → Automation, triggers, enrollment
- `references/pipelines.md` → Configure pipelines, stages

**Marketing & Sales:**
- `references/lists.md` → Contact lists, segmentation
- `references/forms.md` → Landing page forms
- `references/email-marketing.md` → Email campaigns
- `references/conversations.md` → Live chat, chatbots

**Analytics & Reporting:**
- `references/reporting.md` → Custom dashboards, KPIs
- `references/webhooks.md` → Real-time event notifications

**Content & Commerce:**
- `references/cms.md` → Website pages, blog posts, HubDB
- `references/commerce.md` → Products, quotes, invoices

**Platform & Development:**
- `references/developer-platform.md` → HubSpot CLI, custom apps
- `references/owners.md` → User management, permissions
- `references/knowledge-base-tips.md` → UI navigation, admin tasks

## Most Common Workflows

### 1. Import Contacts from CSV
```bash
./scripts/bulk-import.sh contacts contacts.csv
```

### 2. Find & Merge Duplicate Contacts
```bash
./scripts/find-duplicates.sh contacts email
./scripts/merge-records.sh contacts ID1 ID2
```

### 3. Create Deal with Associations
```bash
# Create deal
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealname": "Big Deal",
      "amount": "50000",
      "dealstage": "qualifiedtobuy"
    }
  }'

# Associate to contact (type 3 = deal→contact)
curl -X PUT "https://api.hubapi.com/crm/v3/objects/deals/DEAL_ID/associations/contacts/CONTACT_ID/3" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### 4. Data Quality Audit
```bash
./scripts/data-audit.sh
```

### 5. Export Pipeline Report
```bash
./scripts/pipeline-report.sh > pipeline_report.csv
```

### 6. Log Activity (Call/Email/Meeting)
```bash
# Log a sales call
curl -X POST "https://api.hubapi.com/crm/v3/objects/calls" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_call_title": "Discovery Call",
      "hs_call_duration": "1800000",
      "hs_call_disposition": "Connected"
    },
    "associations": [{
      "to": { "id": "CONTACT_ID" },
      "types": [{ "associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 194 }]
    }]
  }'
```

## Script Usage

All scripts are in `scripts/` directory. Make executable first:
```bash
chmod +x scripts/*.sh
```

**Universal API Helper:**
```bash
./scripts/hs-api.sh GET /crm/v3/objects/contacts
./scripts/hs-api.sh POST /crm/v3/objects/companies '{"properties":{"name":"ACME"}}'
```

**Data Management:**
```bash
./scripts/bulk-import.sh [object-type] [csv-file]
./scripts/bulk-export.sh [object-type] [output-file]
./scripts/find-duplicates.sh [object-type] [property]
./scripts/merge-records.sh [object-type] [primary-id] [duplicate-id]
```

**Reports & Analytics:**
```bash
./scripts/data-audit.sh > audit-report.txt
./scripts/pipeline-report.sh > pipeline-analysis.csv
```

## API Fundamentals

### Rate Limits
- **Private Apps:** 100 requests/10 seconds
- **OAuth Apps:** 100 requests/10 seconds  
- **Search API:** 4 requests/second
- **Batch Operations:** 100 records max per request

### Pagination
All list endpoints use `after` parameter:
```bash
curl "https://api.hubapi.com/crm/v3/objects/contacts?after=12345&limit=100"
```

### Error Handling
- **429:** Rate limit exceeded → Wait and retry
- **400:** Bad request → Check property names/values
- **401:** Authentication failed → Check token/scopes
- **404:** Object not found → Verify ID exists

### Common Headers
```bash
-H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
-H "Content-Type: application/json"
```

### Batch Operations Pattern
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"properties": {"firstname": "John", "lastname": "Doe"}},
      {"properties": {"firstname": "Jane", "lastname": "Smith"}}
    ]
  }'
```

## Search Filters & Operators

### Filter Syntax
```json
{
  "filters": [{
    "propertyName": "email",
    "operator": "EQ",
    "value": "john@example.com"
  }]
}
```

### Operators
- **EQ, NEQ:** Equals, not equals
- **LT, LTE, GT, GTE:** Less/greater than
- **CONTAINS_TOKEN:** Contains word
- **HAS_PROPERTY, NOT_HAS_PROPERTY:** Property exists
- **IN, NOT_IN:** Value in list
- **BETWEEN:** Numeric/date range

### Advanced Search Example
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "createdate",
      "operator": "GTE", 
      "value": "2024-01-01"
    }],
    "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
    "limit": 100
  }'
```

## Environment Variables

Set these in your shell/environment:

```bash
# Required
export HUBSPOT_ACCESS_TOKEN="pat-na1-xxx"  # Private app token

# Optional  
export HUBSPOT_API_KEY="xxx"               # Legacy API key
export HUBSPOT_PORTAL_ID="12345"           # For some API calls
export HUBSPOT_BASE_URL="https://api.hubapi.com"  # Override for testing
```

## Need Help?

1. **API Issues:** Check `references/rate-limits.md` and `references/search-filters.md`
2. **Authentication:** See `references/auth-setup.md`
3. **UI Tasks:** Check `references/knowledge-base-tips.md`
4. **Data Problems:** Use `references/data-quality.md`
5. **Specific Objects:** Find the relevant `references/crm-*.md` file

This skill covers the entire HubSpot platform. Start with the reference file that matches your task, then use the scripts to automate repetitive operations.