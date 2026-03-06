# HubSpot Properties API

Create and manage custom properties, field groups, and calculated fields.

## Core Operations

### Get All Properties for Object
```bash
# Contacts
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/contacts"

# Companies
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/companies"

# Deals
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/deals"
```

### Get Specific Property
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/contacts/favorite_color"
```

## Create Properties

### Single Line Text Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "favorite_color",
    "label": "Favorite Color",
    "type": "string",
    "fieldType": "text",
    "description": "Contact'\''s favorite color for personalization",
    "groupName": "contactinformation",
    "options": [],
    "displayOrder": 6,
    "hasUniqueValue": false,
    "hidden": false,
    "formField": true
  }'
```

### Number Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "expected_roi",
    "label": "Expected ROI (%)",
    "type": "number",
    "fieldType": "number",
    "description": "Expected return on investment percentage",
    "groupName": "dealinformation",
    "options": [],
    "displayOrder": 10
  }'
```

### Dropdown/Select Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "lead_source_detail",
    "label": "Lead Source Detail",
    "type": "enumeration",
    "fieldType": "select",
    "description": "Detailed source of how this lead was generated",
    "groupName": "contactinformation",
    "options": [
      {"label": "Google Ads", "value": "google_ads", "displayOrder": 1},
      {"label": "LinkedIn", "value": "linkedin", "displayOrder": 2},
      {"label": "Content Download", "value": "content_download", "displayOrder": 3},
      {"label": "Webinar", "value": "webinar", "displayOrder": 4},
      {"label": "Referral", "value": "referral", "displayOrder": 5}
    ]
  }'
```

### Multi-Checkbox Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/companies" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "interested_products",
    "label": "Interested Products",
    "type": "enumeration",
    "fieldType": "checkbox",
    "description": "Products the company has expressed interest in",
    "groupName": "companyinformation",
    "options": [
      {"label": "CRM Platform", "value": "crm", "displayOrder": 1},
      {"label": "Marketing Hub", "value": "marketing", "displayOrder": 2},
      {"label": "Sales Hub", "value": "sales", "displayOrder": 3},
      {"label": "Service Hub", "value": "service", "displayOrder": 4}
    ]
  }'
```

### Date Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "contract_start_date",
    "label": "Contract Start Date", 
    "type": "date",
    "fieldType": "date",
    "description": "When the contract becomes effective",
    "groupName": "dealinformation"
  }'
```

### Multi-line Text Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/tickets" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "technical_details",
    "label": "Technical Details",
    "type": "string",
    "fieldType": "textarea",
    "description": "Detailed technical information about the issue",
    "groupName": "ticket_information"
  }'
```

## Update Properties

### Update Property Details
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/properties/contacts/favorite_color" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Preferred Color",
    "description": "Contact'\''s preferred color for marketing personalization"
  }'
```

### Update Dropdown Options
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/properties/contacts/lead_source_detail" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "options": [
      {"label": "Google Ads", "value": "google_ads", "displayOrder": 1},
      {"label": "LinkedIn", "value": "linkedin", "displayOrder": 2},
      {"label": "Content Download", "value": "content_download", "displayOrder": 3},
      {"label": "Webinar", "value": "webinar", "displayOrder": 4},
      {"label": "Referral", "value": "referral", "displayOrder": 5},
      {"label": "Trade Show", "value": "trade_show", "displayOrder": 6}
    ]
  }'
```

## Property Groups

### Create Property Group
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/contacts/groups" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "marketing_qualified",
    "label": "Marketing Qualified Info",
    "displayOrder": 5
  }'
```

### Get All Property Groups
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/properties/contacts/groups"
```

### Update Property Group
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/properties/contacts/groups/marketing_qualified" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "MQL Information",
    "displayOrder": 3
  }'
```

## Property Types Reference

### Field Types
- `text` - Single line text
- `textarea` - Multi-line text
- `number` - Numeric values
- `date` - Date picker
- `datetime` - Date and time
- `select` - Dropdown (single selection)
- `radio` - Radio buttons
- `checkbox` - Multi-select checkboxes
- `booleancheckbox` - Single checkbox (true/false)
- `file` - File upload
- `html` - Rich text editor

### Data Types
- `string` - Text values
- `number` - Numeric values
- `bool` - Boolean (true/false)
- `datetime` - Date/time values
- `enumeration` - Predefined options
- `json` - JSON objects

## Calculated Properties

### Create Score Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "engagement_score",
    "label": "Engagement Score",
    "type": "number",
    "fieldType": "calculation_score",
    "description": "Calculated engagement score based on activities",
    "groupName": "contactinformation",
    "calculationFormula": "((email_opens * 2) + (page_views * 1) + (form_submissions * 5))"
  }'
```

### Rollup Property (Company → Contacts)
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/companies" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "total_contact_revenue",
    "label": "Total Contact Revenue",
    "type": "number",
    "fieldType": "calculation_rollup",
    "description": "Sum of all associated contacts'\'' lifetime value",
    "groupName": "companyinformation",
    "calculationFormula": "SUM(associated_contact.total_revenue)"
  }'
```

## Common Property Patterns

### Lead Scoring Properties
```bash
# Demographic score
{
  "name": "demographic_score",
  "label": "Demographic Score",
  "type": "number",
  "description": "Score based on company size, industry, role"
}

# Behavioral score  
{
  "name": "behavioral_score", 
  "label": "Behavioral Score",
  "type": "number",
  "description": "Score based on website visits, email engagement, content downloads"
}

# Combined lead score
{
  "name": "total_lead_score",
  "label": "Total Lead Score", 
  "type": "number",
  "calculationFormula": "demographic_score + behavioral_score"
}
```

### Sales Process Properties
```bash
# Budget information
{
  "name": "budget_range",
  "label": "Budget Range",
  "type": "enumeration",
  "options": [
    {"label": "< $10K", "value": "under_10k"},
    {"label": "$10K - $50K", "value": "10k_50k"},
    {"label": "$50K - $100K", "value": "50k_100k"},
    {"label": "$100K+", "value": "over_100k"}
  ]
}

# Decision timeframe
{
  "name": "decision_timeframe",
  "label": "Decision Timeframe",
  "type": "enumeration", 
  "options": [
    {"label": "Immediate (< 30 days)", "value": "immediate"},
    {"label": "This quarter", "value": "this_quarter"},
    {"label": "Next quarter", "value": "next_quarter"},
    {"label": "No timeframe", "value": "no_timeframe"}
  ]
}
```

### Technical Properties
```bash
# Integration requirements
{
  "name": "required_integrations",
  "label": "Required Integrations",
  "type": "enumeration",
  "fieldType": "checkbox",
  "options": [
    {"label": "Salesforce", "value": "salesforce"},
    {"label": "Slack", "value": "slack"},
    {"label": "Zapier", "value": "zapier"},
    {"label": "API Access", "value": "api"}
  ]
}
```

## Property Validation

### Set Property as Required
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/properties/contacts/industry" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hidden": false,
    "formField": true
  }'
```

### Unique Value Property
```bash
curl -X POST "https://api.hubapi.com/crm/v3/properties/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer_id",
    "label": "Customer ID",
    "type": "string",
    "fieldType": "text",
    "hasUniqueValue": true,
    "description": "Unique customer identifier from external system"
  }'
```

## Delete Properties

### Archive Property
```bash
curl -X DELETE "https://api.hubapi.com/crm/v3/properties/contacts/old_property" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

Note: Deleting properties removes all data. Use carefully!

## Property Usage Analytics

### Find Properties with No Data
```bash
# Search for contacts missing key properties
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "industry",
      "operator": "NOT_HAS_PROPERTY"
    }],
    "properties": ["firstname", "lastname", "email"],
    "limit": 100
  }'
```

### Property Value Distribution
```bash
# Get distribution of lead sources
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": ["hs_lead_status", "createdate"],
    "limit": 1000
  }'
```

## Best Practices

### Naming Conventions
- Use lowercase with underscores: `lead_source_detail`
- Be descriptive but concise
- Prefix custom properties: `custom_priority_level`
- Avoid spaces and special characters

### Property Organization
- Group related properties together
- Use meaningful group names
- Set logical display orders
- Keep groups under 15 properties

### Data Quality
- Set up validation rules
- Use predefined options when possible
- Document property meanings
- Regular data cleanup

### Performance
- Index frequently filtered properties
- Limit calculated properties
- Use appropriate field types
- Avoid too many checkbox options (>20)

## HubSpot UI Tips

### Creating Properties in UI
1. Settings → Properties
2. Select object type (Contacts, Companies, etc.)
3. Click "Create property"
4. Choose field type and configure options

### Property Management
- Use property groups for organization
- Set display order for logical flow
- Configure permissions by user role
- Use dependency rules for conditional fields

### Import with Custom Properties
1. Include custom property names as CSV headers
2. Use internal property names (not labels)
3. Format dates as YYYY-MM-DD
4. Use exact option values for dropdowns

### Property History
- View property change history on records
- Track who made changes and when
- Use for data quality auditing
- Set up change notifications