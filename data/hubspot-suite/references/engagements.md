# HubSpot Engagements API

Track all sales and support activities: calls, emails, meetings, notes, and tasks.

## Core Engagement Types

### Calls
Log phone calls and track call outcomes.

### Emails  
Record sent/received emails and track opens/clicks.

### Meetings
Schedule and log meetings, demos, and presentations.

### Notes
Capture important information and conversation details.

### Tasks
Create follow-up actions and reminders.

## Create Engagements

### Log a Phone Call
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/calls" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_call_title": "Discovery Call - ACME Corp",
      "hs_call_body": "Discussed current pain points and requirements. Strong interest in enterprise package.",
      "hs_call_duration": "1800000",
      "hs_call_from_number": "+15551234567",
      "hs_call_to_number": "+15559876543",
      "hs_call_status": "COMPLETED",
      "hs_call_direction": "OUTBOUND",
      "hs_call_disposition": "f240bbac-87c9-4f6e-bf70-924b57d47db7",
      "hs_activity_type": "Sales call"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 194}]
      },
      {
        "to": {"id": "DEAL_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 214}]
      }
    ]
  }'
```

### Log an Email
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/emails" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_email_subject": "Follow up on Enterprise Demo",
      "hs_email_text": "Hi John, Thanks for taking the time to see our demo yesterday. I wanted to follow up...",
      "hs_email_direction": "EMAIL",
      "hs_email_status": "SENT",
      "hs_email_tracker_key": "unique-tracking-key-123"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 198}]
      }
    ]
  }'
```

### Schedule a Meeting
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/meetings" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_meeting_title": "Product Demo - Enterprise Package",
      "hs_meeting_body": "30-minute product demonstration focusing on enterprise features and integration capabilities.",
      "hs_meeting_start_time": "2024-03-15T14:00:00.000Z",
      "hs_meeting_end_time": "2024-03-15T14:30:00.000Z",
      "hs_meeting_location": "Zoom: https://zoom.us/j/123456789",
      "hs_meeting_outcome": "Scheduled"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 200}]
      },
      {
        "to": {"id": "DEAL_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 216}]
      }
    ]
  }'
```

### Create a Note
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/notes" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_note_body": "Contact expressed strong interest in Q4 implementation. Budget approved. Next step: technical evaluation with IT team.",
      "hs_attachment_ids": "123456789"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}]
      },
      {
        "to": {"id": "DEAL_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 218}]
      }
    ]
  }'
```

### Create a Task
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tasks" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_task_subject": "Send pricing proposal",
      "hs_task_body": "Create and send customized pricing proposal based on discovery call requirements.",
      "hs_task_status": "NOT_STARTED",
      "hs_task_priority": "HIGH",
      "hs_task_type": "TODO",
      "hs_task_completion_date": "2024-03-20T17:00:00.000Z"
    },
    "associations": [
      {
        "to": {"id": "CONTACT_ID"},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 204}]
      }
    ]
  }'
```

## Get Engagements

### Get Call Details
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/calls/12345?properties=hs_call_title,hs_call_duration,hs_call_disposition"
```

### Get Contact's Recent Activities
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/calls/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "associations.contact",
      "operator": "EQ",
      "value": "CONTACT_ID"
    }],
    "sorts": [{"propertyName": "hs_createdate", "direction": "DESCENDING"}],
    "properties": ["hs_call_title", "hs_call_duration", "hs_call_disposition", "hs_createdate"],
    "limit": 10
  }'
```

### Get All Activities for Deal
```bash
# Get calls
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/calls"

# Get emails  
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/emails"

# Get meetings
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/meetings"
```

## Update Engagements

### Update Call Outcome
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/calls/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_call_disposition": "Connected",
      "hs_call_body": "Updated call notes: Customer agreed to demo next week."
    }
  }'
```

### Mark Task Complete
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/tasks/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_task_status": "COMPLETED",
      "hs_task_completion_date": "'$(date -u --iso-8601=seconds)'"
    }
  }'
```

### Update Meeting Outcome
```bash
curl -X PATCH "https://api.hubapi.com/crm/v3/objects/meetings/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_meeting_outcome": "Completed",
      "hs_meeting_body": "Demo went well. Customer interested in advanced features. Scheduling technical deep-dive."
    }
  }'
```

## Batch Engagement Operations

### Log Multiple Calls
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/calls/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "hs_call_title": "Cold outreach - Lead 1",
          "hs_call_duration": "300000",
          "hs_call_disposition": "No answer"
        }
      },
      {
        "properties": {
          "hs_call_title": "Follow-up call - Lead 2", 
          "hs_call_duration": "900000",
          "hs_call_disposition": "Connected"
        }
      }
    ]
  }'
```

### Create Multiple Tasks
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tasks/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "hs_task_subject": "Send welcome email",
          "hs_task_priority": "MEDIUM",
          "hs_task_status": "NOT_STARTED"
        }
      },
      {
        "properties": {
          "hs_task_subject": "Schedule onboarding call",
          "hs_task_priority": "HIGH", 
          "hs_task_status": "NOT_STARTED"
        }
      }
    ]
  }'
```

## Search & Filter Engagements

### Recent High-Value Call Activity
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/calls/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_call_disposition",
        "operator": "EQ",
        "value": "Connected"
      },
      {
        "propertyName": "hs_createdate",
        "operator": "GTE",
        "value": "'$(date -u -d '7 days ago' '+%Y-%m-%d')'"
      }
    ],
    "sorts": [{"propertyName": "hs_createdate", "direction": "DESCENDING"}],
    "properties": ["hs_call_title", "hs_call_duration", "hs_call_disposition", "hs_createdate"]
  }'
```

### Overdue Tasks
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tasks/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_task_status",
        "operator": "NEQ",
        "value": "COMPLETED"
      },
      {
        "propertyName": "hs_task_completion_date",
        "operator": "LTE",
        "value": "'$(date -u '+%Y-%m-%d')'"
      }
    ],
    "properties": ["hs_task_subject", "hs_task_priority", "hs_task_completion_date", "hubspot_owner_id"]
  }'
```

### Meetings This Week
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/meetings/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_meeting_start_time",
      "operator": "BETWEEN",
      "value": "'$(date -u -d 'monday this week' '+%Y-%m-%d')'",
      "highValue": "'$(date -u -d 'sunday this week' '+%Y-%m-%d')'"
    }],
    "properties": ["hs_meeting_title", "hs_meeting_start_time", "hs_meeting_outcome"]
  }'
```

## Engagement Properties

### Call Properties
- `hs_call_title` - Call subject/title
- `hs_call_body` - Call notes/description
- `hs_call_duration` - Duration in milliseconds
- `hs_call_from_number` - Caller phone number
- `hs_call_to_number` - Recipient phone number
- `hs_call_status` - BUSY, CALLING_CRM_USER, CANCELED, COMPLETED, etc.
- `hs_call_direction` - INBOUND, OUTBOUND
- `hs_call_disposition` - Connected, No answer, Left voicemail, etc.

### Email Properties
- `hs_email_subject` - Email subject line
- `hs_email_text` - Email body content
- `hs_email_direction` - EMAIL, INCOMING_EMAIL
- `hs_email_status` - SENT, DELIVERED, OPENED, CLICKED
- `hs_email_html` - HTML email content
- `hs_email_tracker_key` - Unique tracking identifier

### Meeting Properties
- `hs_meeting_title` - Meeting title/subject
- `hs_meeting_body` - Meeting description/notes
- `hs_meeting_start_time` - Start time (ISO 8601)
- `hs_meeting_end_time` - End time (ISO 8601)
- `hs_meeting_location` - Meeting location/URL
- `hs_meeting_outcome` - Scheduled, Completed, Rescheduled, No Show

### Task Properties
- `hs_task_subject` - Task title
- `hs_task_body` - Task description
- `hs_task_status` - NOT_STARTED, IN_PROGRESS, COMPLETED, WAITING, DEFERRED
- `hs_task_priority` - LOW, MEDIUM, HIGH
- `hs_task_type` - TODO, CALL, EMAIL
- `hs_task_completion_date` - Due date (ISO 8601)

### Note Properties
- `hs_note_body` - Note content
- `hs_attachment_ids` - Attached file IDs

## Activity Analytics

### Call Volume by Rep
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/calls/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_createdate",
      "operator": "GTE",
      "value": "'$(date -u -d '30 days ago' '+%Y-%m-%d')'"
    }],
    "properties": ["hubspot_owner_id", "hs_call_disposition", "hs_createdate"]
  }'
```

### Email Response Rates
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/emails/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_email_status",
      "operator": "IN",
      "values": ["OPENED", "CLICKED", "REPLIED"]
    }],
    "properties": ["hs_email_subject", "hs_email_status", "hs_createdate"]
  }'
```

### Task Completion Rates
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/tasks/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": ["hs_task_subject", "hs_task_status", "hs_task_completion_date", "hubspot_owner_id"]
  }'
```

## Automation with Engagements

### Auto-create Follow-up Task After Call
Create workflow in HubSpot UI:
1. Trigger: Call created with disposition "Connected"
2. Action: Create task "Send follow-up email"
3. Delay: 1 hour
4. Assign to call owner

### Meeting No-Show Handling
1. Trigger: Meeting outcome = "No Show"
2. Action: Create task "Reschedule meeting"
3. Action: Send automated email

### Email Tracking Workflows
1. Trigger: Email status = "Opened"
2. Action: Add contact to "Engaged prospects" list
3. Action: Create task for salesperson "Follow up on email"

## HubSpot UI Tips

### Activity Timeline
- View all activities on contact/company/deal records
- Filter by activity type (calls, emails, meetings, etc.)
- Click activities to view/edit details

### Logging Activities
- Use "Log call" button in contact records
- Email tracking automatically logs sent emails
- Meeting links auto-sync with calendar

### Task Management
- Use Tasks view for personal task list
- Set up task queues for team workflows
- Configure task templates for common activities

### Activity Templates
- Create call script templates
- Set up email templates for common scenarios
- Use meeting templates for consistent agendas

### Reporting on Activities
- Use Activity dashboard in Reports
- Track call volume, email opens, meeting rates
- Monitor team activity performance