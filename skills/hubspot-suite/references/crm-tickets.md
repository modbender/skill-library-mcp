# HubSpot Tickets API

Complete guide for support ticket and service management.

## Core Operations

### Create Ticket
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "subject": "Email integration not working",
      "content": "Customer reports emails not syncing properly with CRM",
      "hs_pipeline": "0",
      "hs_pipeline_stage": "1",
      "hs_ticket_priority": "HIGH",
      "source_type": "EMAIL",
      "hs_ticket_category": "TECHNICAL_ISSUE"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 16}]
      }
    ]
  }'
```

### Get Ticket by ID
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/tickets/12345?properties=subject,content,hs_pipeline_stage,hs_ticket_priority,createdate"
```

### Update Ticket
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/tickets/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_pipeline_stage": "3",
      "hs_ticket_priority": "MEDIUM",
      "hs_resolution": "Updated email settings and tested sync"
    }
  }'
```

### Close Ticket
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/tickets/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_pipeline_stage": "4",
      "hs_resolution": "Issue resolved. Email sync working correctly.",
      "closed_date": "'$(date -u '+%Y-%m-%d')'"
    }
  }'
```

## Ticket Priorities & Categories

### Priority Levels
- `LOW` - Low priority
- `MEDIUM` - Medium priority  
- `HIGH` - High priority
- `URGENT` - Urgent/critical

### Common Categories
- `TECHNICAL_ISSUE` - Technical support
- `BILLING` - Billing questions
- `FEATURE_REQUEST` - Product enhancement
- `BUG_REPORT` - Software bugs
- `TRAINING` - User training/help
- `OTHER` - General inquiries

### Source Types
- `EMAIL` - Email support
- `CHAT` - Live chat
- `PHONE` - Phone support
- `WEB` - Web form
- `FACEBOOK` - Facebook Messenger
- `TWITTER` - Twitter support

## Ticket Pipelines & Stages

### Get All Ticket Pipelines
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/pipelines/tickets"
```

### Default Ticket Stages
- `1` - New
- `2` - Waiting on contact
- `3` - Waiting on us
- `4` - Closed

### Move Ticket Through Pipeline
```bash
# Move to "Waiting on us" stage
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/tickets/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_pipeline_stage": "3"
    }
  }'
```

## Search & Filtering

### Open High Priority Tickets
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_ticket_priority",
        "operator": "EQ",
        "value": "HIGH"
      },
      {
        "propertyName": "hs_pipeline_stage",
        "operator": "NEQ",
        "value": "4"
      }
    ],
    "sorts": [{"propertyName": "createdate", "direction": "ASCENDING"}],
    "properties": ["subject", "hs_ticket_priority", "hs_pipeline_stage", "createdate"]
  }'
```

### Tickets by Category
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_ticket_category",
      "operator": "EQ",
      "value": "TECHNICAL_ISSUE"
    }],
    "properties": ["subject", "hs_ticket_category", "hs_ticket_priority", "createdate"]
  }'
```

### Overdue Tickets (SLA Breach)
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_pipeline_stage",
        "operator": "NEQ",
        "value": "4"
      },
      {
        "propertyName": "createdate",
        "operator": "LTE",
        "value": "'$(date -u -d '2 days ago' '+%Y-%m-%d')'"
      }
    ],
    "sorts": [{"propertyName": "createdate", "direction": "ASCENDING"}],
    "properties": ["subject", "hs_ticket_priority", "createdate", "hubspot_owner_id"]
  }'
```

### Tickets by Agent
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hubspot_owner_id",
      "operator": "EQ",
      "value": "12345"
    }],
    "properties": ["subject", "hs_pipeline_stage", "hs_ticket_priority", "createdate"]
  }'
```

## Batch Operations

### Create Multiple Tickets
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "subject": "Password reset request",
          "hs_ticket_priority": "MEDIUM",
          "hs_ticket_category": "TECHNICAL_ISSUE"
        }
      },
      {
        "properties": {
          "subject": "Billing inquiry",
          "hs_ticket_priority": "LOW",
          "hs_ticket_category": "BILLING"
        }
      }
    ]
  }'
```

### Batch Close Tickets
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/batch/update" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "id": "12345",
        "properties": {
          "hs_pipeline_stage": "4",
          "hs_resolution": "Resolved via phone call"
        }
      },
      {
        "id": "67890",
        "properties": {
          "hs_pipeline_stage": "4",
          "hs_resolution": "Duplicate ticket, merged"
        }
      }
    ]
  }'
```

## Standard Properties

### Required Properties
- `subject` (ticket title/summary)
- `content` (detailed description)

### Stage & Status
- `hs_pipeline` (pipeline ID, default: "0")
- `hs_pipeline_stage` (stage ID within pipeline)
- `closed_date` (when ticket was closed)

### Classification
- `hs_ticket_priority` (LOW, MEDIUM, HIGH, URGENT)
- `hs_ticket_category` (predefined or custom categories)
- `source_type` (how ticket was created)

### Assignment
- `hubspot_owner_id` (assigned support agent)
- `hs_createdate` (when ticket was created)
- `hs_lastmodifieddate` (last update time)

### Resolution
- `hs_resolution` (description of how ticket was resolved)
- `time_to_close` (calculated field)
- `first_agent_reply_date` (SLA tracking)

## Ticket Associations

### Get Associated Contact
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/tickets/12345/associations/contacts"
```

### Get Associated Company  
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/tickets/12345/associations/companies"
```

### Associate Ticket with Contact
```bash
# Association type 16 = ticket→contact
curl -X PUT "https://api.hubapi.com/crm/v3/objects/tickets/12345/associations/contacts/CONTACT_ID/16" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## SLA Management

### Track Response Times
```bash
# Get tickets without first agent reply
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "first_agent_reply_date", 
        "operator": "NOT_HAS_PROPERTY"
      },
      {
        "propertyName": "hs_pipeline_stage",
        "operator": "NEQ",
        "value": "4"
      }
    ],
    "properties": ["subject", "createdate", "hs_ticket_priority"]
  }'
```

### SLA Breach Analysis
```bash
# High priority tickets open > 4 hours
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_ticket_priority",
        "operator": "EQ",
        "value": "HIGH"
      },
      {
        "propertyName": "createdate",
        "operator": "LTE", 
        "value": "'$(date -u -d '4 hours ago' --iso-8601=minutes)'"
      },
      {
        "propertyName": "hs_pipeline_stage",
        "operator": "NEQ",
        "value": "4"
      }
    ]
  }'
```

## Ticket Analytics

### Tickets Created Today
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "createdate",
      "operator": "GTE",
      "value": "'$(date -u '+%Y-%m-%d')'"
    }],
    "properties": ["subject", "hs_ticket_priority", "hs_ticket_category", "createdate"]
  }'
```

### Resolution Time Analysis
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tickets/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_pipeline_stage",
      "operator": "EQ", 
      "value": "4"
    }],
    "properties": ["subject", "createdate", "closed_date", "time_to_close", "hs_ticket_priority"]
  }'
```

## Common Workflows

### 1. Auto-assign by Category
```bash
# Technical issues → Technical team
# Billing → Finance team  
# Feature requests → Product team
```

### 2. Escalation Rules
- High priority: 2 hours response time
- Medium priority: 4 hours response time
- Low priority: 24 hours response time

### 3. Customer Satisfaction Survey
Auto-send CSAT survey after ticket closure

## HubSpot UI Tips

### Ticket Board View
1. Service → Tickets → Board view
2. Drag tickets between stages
3. Filter by priority, category, agent
4. Bulk actions on multiple tickets

### SLA Configuration
1. Service → SLAs
2. Set response time targets by priority
3. Configure escalation rules
4. Track SLA performance

### Ticket Templates
1. Create templates for common issues
2. Include standard resolution steps
3. Pre-populate categories and priorities

### Knowledge Base Integration
1. Link tickets to KB articles
2. Track which articles resolve tickets
3. Identify gaps in documentation

### Customer Portal
1. Enable customer ticket creation
2. Allow status tracking
3. Provide knowledge base access
4. Enable ticket updates/replies