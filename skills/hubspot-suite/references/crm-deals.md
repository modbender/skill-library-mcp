# HubSpot Deals API

Complete guide for sales pipeline and deal management.

## Core Operations

### Create Deal
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealname": "Enterprise Software Deal",
      "amount": "50000",
      "dealstage": "qualifiedtobuy",
      "pipeline": "default",
      "closedate": "2024-12-31",
      "deal_currency_code": "USD",
      "dealtype": "newbusiness",
      "hs_priority": "high"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}]
      },
      {
        "to": {"id": "COMPANY_ID"},  
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}]
      }
    ]
  }'
```

### Get Deal by ID
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/deals/12345?properties=dealname,amount,dealstage,closedate,pipeline"
```

### Update Deal
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/deals/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "amount": "75000",
      "dealstage": "contractsent",
      "closedate": "2024-11-30"
    }
  }'
```

### Move Deal Through Pipeline
```bash
# Move to next stage
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/deals/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealstage": "decisionmakerboughtin"
    }
  }'
```

### Close Deal (Won)
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/deals/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealstage": "closedwon",
      "closedate": "'$(date -u '+%Y-%m-%d')'"
    }
  }'
```

### Close Deal (Lost)
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/deals/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealstage": "closedlost",
      "closed_lost_reason": "Budget constraints",
      "closedate": "'$(date -u '+%Y-%m-%d')'"
    }
  }'
```

## Batch Operations

### Create Multiple Deals
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "dealname": "Q4 Software License",
          "amount": "25000",
          "dealstage": "appointmentscheduled"
        }
      },
      {
        "properties": {
          "dealname": "Annual Support Contract",
          "amount": "15000",
          "dealstage": "qualifiedtobuy"
        }
      }
    ]
  }'
```

### Batch Update Deal Stages
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/batch/update" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "id": "12345",
        "properties": {"dealstage": "presentationscheduled"}
      },
      {
        "id": "67890",
        "properties": {"dealstage": "contractsent"}
      }
    ]
  }'
```

## Deal Stages & Pipelines

### Get All Pipelines
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/pipelines/deals"
```

### Get Pipeline Stages
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/pipelines/deals/default"
```

### Common Default Deal Stages
- `appointmentscheduled` - Appointment Scheduled
- `qualifiedtobuy` - Qualified to Buy  
- `presentationscheduled` - Presentation Scheduled
- `decisionmakerboughtin` - Decision Maker Bought-In
- `contractsent` - Contract Sent
- `closedwon` - Closed Won
- `closedlost` - Closed Lost

## Search & Filtering

### Deals by Stage
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
    "properties": ["dealname", "amount", "dealstage", "closedate"],
    "limit": 100
  }'
```

### Deals Closing This Quarter
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "closedate",
        "operator": "BETWEEN",
        "value": "2024-10-01",
        "highValue": "2024-12-31"
      },
      {
        "propertyName": "dealstage",
        "operator": "NEQ",
        "value": "closedlost"
      }
    ],
    "sorts": [{"propertyName": "closedate", "direction": "ASCENDING"}],
    "properties": ["dealname", "amount", "dealstage", "closedate", "hubspot_owner_id"]
  }'
```

### High-Value Deals ($50K+)
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "amount",
      "operator": "GTE",
      "value": "50000"
    }],
    "sorts": [{"propertyName": "amount", "direction": "DESCENDING"}],
    "properties": ["dealname", "amount", "dealstage", "closedate"]
  }'
```

### Recently Created Deals
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "createdate",
      "operator": "GTE",
      "value": "'$(date -u -d '7 days ago' '+%Y-%m-%d')'"
    }],
    "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
    "properties": ["dealname", "amount", "dealstage", "createdate"]
  }'
```

## Deal Associations

### Get Associated Contacts
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/deals/12345/associations/contacts"
```

### Get Associated Company
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/deals/12345/associations/companies"
```

### Associate Deal with Contact
```bash
# Association type 3 = deal→contact
curl -X PUT "https://api.hubapi.com/crm/v3/objects/deals/12345/associations/contacts/CONTACT_ID/3" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### Associate Deal with Company
```bash
# Association type 5 = deal→company
curl -X PUT "https://api.hubapi.com/crm/v3/objects/deals/12345/associations/companies/COMPANY_ID/5" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Standard Properties

### Deal Basics
- `dealname` (deal title)
- `amount` (deal value in cents or dollars)
- `dealstage` (current pipeline stage)
- `pipeline` (pipeline ID, default: "default")
- `closedate` (expected close date, YYYY-MM-DD)

### Deal Classification
- `dealtype` (newbusiness, existingbusiness, renewal)
- `deal_currency_code` (USD, EUR, etc.)
- `hs_priority` (high, medium, low)
- `deal_probability` (0-100 percentage)

### Sales Process
- `hubspot_owner_id` (assigned salesperson)
- `hs_deal_stage_probability` (auto-calculated based on stage)
- `num_contacted_notes` (activity count)
- `days_to_close` (calculated field)

### Loss Tracking
- `closed_lost_reason` (why deal was lost)
- `hs_deal_stage_probability` (probability based on stage)

### Custom Fields
Create custom properties for:
- Lead source
- Competitor information
- Technical requirements
- Decision maker details

## Deal Forecasting

### Revenue by Close Date
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "closedate",
        "operator": "BETWEEN",
        "value": "2024-11-01",
        "highValue": "2024-11-30"
      },
      {
        "propertyName": "dealstage",
        "operator": "NOT_IN",
        "values": ["closedlost"]
      }
    ],
    "properties": ["dealname", "amount", "dealstage", "closedate", "hs_deal_stage_probability"]
  }'
```

### Weighted Pipeline Value
Calculate probability × amount for each deal:
```bash
# Get deals with probability and amount
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "dealstage",
      "operator": "NOT_IN",
      "values": ["closedwon", "closedlost"]
    }],
    "properties": ["dealname", "amount", "dealstage", "hs_deal_stage_probability"]
  }'
```

## Deal Analytics

### Won Deals Analysis
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "dealstage",
        "operator": "EQ",
        "value": "closedwon"
      },
      {
        "propertyName": "closedate",
        "operator": "GTE",
        "value": "2024-01-01"
      }
    ],
    "properties": ["dealname", "amount", "closedate", "hubspot_owner_id", "days_to_close"]
  }'
```

### Lost Deal Analysis
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "dealstage",
      "operator": "EQ",
      "value": "closedlost"
    }],
    "properties": ["dealname", "amount", "closedate", "closed_lost_reason", "hubspot_owner_id"]
  }'
```

## Deal Velocity Metrics

### Average Deal Size
Sum of closed-won deals ÷ number of deals

### Win Rate
Closed-won deals ÷ (closed-won + closed-lost)

### Sales Cycle Length
Average `days_to_close` for closed-won deals

### Pipeline Velocity
(Number of qualified opportunities × Average deal value × Win rate) ÷ Sales cycle length

## Common Deal Workflows

### 1. Lead to Deal Conversion
```bash
# Create deal from qualified lead
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealname": "Lead Conversion - Company Name",
      "amount": "0",
      "dealstage": "appointmentscheduled"
    }
  }'
```

### 2. Deal Stage Automation
Set up workflows in HubSpot UI to:
- Auto-advance stages based on activities
- Send notifications on stage changes
- Create tasks for next steps
- Update deal probabilities

### 3. Deal Assignment Rules
- Round-robin by territory
- Lead score-based assignment
- Company size-based routing
- Industry specialization matching

## HubSpot UI Tips

### Deal Board View
1. Sales → Deals → Board view
2. Drag deals between stages
3. Click deal to edit inline
4. Filter by owner, pipeline, date range

### Deal Forecasting
1. Reports → Deal Forecast Report
2. Filter by time period and pipeline
3. View by probability-weighted amounts
4. Export forecast data

### Deal Templates
1. Create deal templates for common types
2. Include standard properties and values
3. Associate with relevant assets (quotes, presentations)

### Pipeline Management
1. Settings → Objects → Deals → Pipelines
2. Customize stages and probabilities
3. Set up stage requirements
4. Configure automation rules

### Deal Rotation
1. Set up deal assignment rules
2. Configure territory-based routing
3. Use workflows for automatic assignment
4. Monitor distribution across team