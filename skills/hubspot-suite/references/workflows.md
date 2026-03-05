# HubSpot Workflows & Automation

Create powerful automated workflows for lead nurturing, sales processes, and customer success.

## Core Workflow Concepts

### Workflow Types
- **Contact-based**: Trigger on contact properties/actions
- **Company-based**: Trigger on company changes
- **Deal-based**: Trigger on deal progression
- **Ticket-based**: Trigger on support activities
- **Quote-based**: Trigger on quote status changes

### Enrollment Triggers
- **Property changes**: When field value changes
- **Form submissions**: When contact fills out form
- **List membership**: When added/removed from list
- **Page views**: When visits specific page
- **Email engagement**: Opens, clicks, bounces
- **Manual enrollment**: Sales rep manually adds

## Basic Workflow Operations

### Get All Workflows
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/automation/v3/workflows"
```

### Get Specific Workflow
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/automation/v3/workflows/12345"
```

### Create Simple Workflow
```bash
curl -X POST "https://api.hubapi.com/automation/v3/workflows" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome New Subscribers",
    "type": "DRIP_DELAY",
    "enabled": true,
    "insertedAt": 0,
    "onlyExecOnBizDays": false,
    "enrollmentCriteria": [
      {
        "filterFamily": "PropertyValue",
        "withinTimeMode": "PAST",
        "property": "lifecyclestage",
        "type": "string",
        "operation": {
          "operator": "EQ",
          "operationType": "MULTISTRING",
          "values": ["subscriber"]
        }
      }
    ]
  }'
```

## Common Workflow Patterns

### Lead Nurturing Workflow
```bash
# Create lead nurturing workflow
curl -X POST "https://api.hubapi.com/automation/v3/workflows" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lead Nurture - Content Download",
    "type": "DRIP_DELAY", 
    "enabled": true,
    "description": "Nurture leads who downloaded whitepaper",
    "enrollmentCriteria": [
      {
        "filterFamily": "FormSubmission",
        "operator": "EQ",
        "property": "form_submission",
        "value": "whitepaper-form-guid"
      }
    ],
    "actions": [
      {
        "type": "DELAY",
        "delayMillis": 86400000,
        "description": "Wait 1 day"
      },
      {
        "type": "SEND_EMAIL",
        "emailId": "email-template-id",
        "description": "Send follow-up email"
      },
      {
        "type": "SET_CONTACT_PROPERTY", 
        "property": "lead_status",
        "newValue": "nurtured",
        "description": "Mark as nurtured lead"
      }
    ]
  }'
```

### Deal Stage Automation
```bash
# Workflow for deal progression
curl -X POST "https://api.hubapi.com/automation/v3/workflows" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deal Stage - Qualified to Buy",
    "type": "PROPERTY_CHANGE",
    "enabled": true,
    "objectType": "DEAL",
    "enrollmentCriteria": [
      {
        "filterFamily": "PropertyValue",
        "property": "dealstage", 
        "operator": "EQ",
        "value": "qualifiedtobuy"
      }
    ],
    "actions": [
      {
        "type": "CREATE_TASK",
        "taskType": "CALL",
        "subject": "Schedule product demo",
        "description": "Contact is qualified - schedule demo call",
        "dueDate": "1_DAY",
        "assignToOwner": true
      },
      {
        "type": "SEND_INTERNAL_EMAIL",
        "toEmailAddress": "sales-team@company.com",
        "subject": "New Qualified Deal: {{ deal.dealname }}",
        "emailBody": "Deal {{ deal.dealname }} worth ${{ deal.amount }} moved to qualified stage."
      }
    ]
  }'
```

### Customer Onboarding
```bash
# Customer success workflow
curl -X POST "https://api.hubapi.com/automation/v3/workflows" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Onboarding Sequence",
    "type": "DRIP_DELAY",
    "enabled": true,
    "enrollmentCriteria": [
      {
        "filterFamily": "PropertyValue",
        "property": "lifecyclestage",
        "operator": "EQ", 
        "value": "customer"
      }
    ],
    "actions": [
      {
        "type": "SEND_EMAIL",
        "emailId": "welcome-email-template",
        "description": "Send welcome email immediately"
      },
      {
        "type": "DELAY",
        "delayMillis": 259200000,
        "description": "Wait 3 days"
      },
      {
        "type": "SEND_EMAIL", 
        "emailId": "getting-started-email",
        "description": "Send getting started guide"
      },
      {
        "type": "DELAY",
        "delayMillis": 604800000,
        "description": "Wait 1 week"
      },
      {
        "type": "CREATE_TASK",
        "taskType": "EMAIL",
        "subject": "Check in with new customer",
        "assignToOwner": true
      }
    ]
  }'
```

## Advanced Workflow Features

### Conditional Logic (If/Then Branches)
```bash
# Workflow with branching logic
curl -X POST "https://api.hubapi.com/automation/v3/workflows" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lead Scoring with Branches",
    "type": "PROPERTY_CHANGE",
    "enabled": true,
    "enrollmentCriteria": [
      {
        "property": "hubspotscore",
        "operator": "GTE",
        "value": "50"
      }
    ],
    "actions": [
      {
        "type": "IF_THEN_BRANCH",
        "criteria": [
          {
            "property": "hubspotscore",
            "operator": "GTE", 
            "value": "80"
          }
        ],
        "yesActions": [
          {
            "type": "SET_CONTACT_PROPERTY",
            "property": "lifecyclestage",
            "newValue": "marketingqualifiedlead"
          },
          {
            "type": "ADD_TO_LIST",
            "listId": "hot-leads-list-id"
          }
        ],
        "noActions": [
          {
            "type": "SET_CONTACT_PROPERTY", 
            "property": "lead_status",
            "newValue": "warm"
          }
        ]
      }
    ]
  }'
```

### A/B Testing in Workflows
```bash
# A/B test email templates
curl -X POST "https://api.hubapi.com/automation/v3/workflows" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "A/B Test Welcome Email",
    "type": "DRIP_DELAY",
    "enabled": true,
    "enrollmentCriteria": [
      {
        "property": "lifecyclestage",
        "operator": "EQ",
        "value": "subscriber"
      }
    ],
    "actions": [
      {
        "type": "AB_TEST",
        "testName": "Welcome Email Test",
        "sampleSizeType": "PERCENTAGE",
        "sampleSize": 50,
        "winnerCriteria": "OPEN_RATE",
        "testDuration": 168,
        "variantA": {
          "type": "SEND_EMAIL",
          "emailId": "welcome-email-a"
        },
        "variantB": {
          "type": "SEND_EMAIL", 
          "emailId": "welcome-email-b"
        }
      }
    ]
  }'
```

## Workflow Management

### Enable/Disable Workflow
```bash
# Enable workflow
curl -X PUT "https://api.hubapi.com/automation/v3/workflows/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Disable workflow
curl -X PUT "https://api.hubapi.com/automation/v3/workflows/12345" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Manual Enrollment
```bash
# Manually enroll contact in workflow
curl -X POST "https://api.hubapi.com/automation/v3/workflows/12345/enrollments" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enrollments": [
      {
        "objectId": "CONTACT_ID",
        "objectType": "CONTACT"
      }
    ]
  }'
```

### Unenroll Contact
```bash
# Remove contact from workflow
curl -X DELETE "https://api.hubapi.com/automation/v3/workflows/12345/enrollments/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

## Workflow Actions Reference

### Email Actions
```bash
{
  "type": "SEND_EMAIL",
  "emailId": "template-id",
  "description": "Send marketing email"
}

{
  "type": "SEND_INTERNAL_EMAIL",
  "toEmailAddress": "team@company.com", 
  "subject": "Notification",
  "emailBody": "Custom email content"
}
```

### Property Updates
```bash
{
  "type": "SET_CONTACT_PROPERTY",
  "property": "lifecyclestage",
  "newValue": "customer"
}

{
  "type": "COPY_PROPERTY",
  "fromProperty": "company",
  "toProperty": "company_backup"
}

{
  "type": "CALCULATE_PROPERTY",
  "property": "total_score", 
  "operation": "SUM",
  "operands": ["demographic_score", "behavioral_score"]
}
```

### List Management
```bash
{
  "type": "ADD_TO_LIST",
  "listId": "static-list-id"
}

{
  "type": "REMOVE_FROM_LIST",
  "listId": "static-list-id" 
}
```

### Task Creation
```bash
{
  "type": "CREATE_TASK",
  "taskType": "CALL",
  "subject": "Follow up call needed",
  "description": "Contact showed high engagement",
  "dueDate": "2_DAYS",
  "assignToOwner": true,
  "priority": "HIGH"
}
```

### Integration Actions
```bash
{
  "type": "WEBHOOK",
  "url": "https://your-app.com/webhook",
  "method": "POST",
  "headers": {"Authorization": "Bearer token"},
  "body": "{\"contact_id\": \"{{ contact.id }}\"}"
}

{
  "type": "SALESFORCE_SYNC",
  "operation": "CREATE_LEAD",
  "mappings": {
    "FirstName": "{{ contact.firstname }}",
    "LastName": "{{ contact.lastname }}",
    "Email": "{{ contact.email }}"
  }
}
```

## Workflow Performance & Analytics

### Get Workflow Performance
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/automation/v3/workflows/12345/performance"
```

### Workflow Enrollment History
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/automation/v3/workflows/12345/enrollments?limit=100"
```

## Common Use Cases

### 1. Lead Qualification
**Trigger**: Form submission
**Actions**:
- Assign lead score +20
- Add to "New Leads" list  
- Create task for sales rep
- Send internal notification

### 2. Deal Pipeline Automation
**Trigger**: Deal stage change
**Actions**:
- Create follow-up tasks
- Send email templates
- Update deal properties
- Notify team members

### 3. Customer Success
**Trigger**: Deal closed-won
**Actions**:
- Change lifecycle stage to "customer"
- Send welcome email sequence
- Create onboarding tasks
- Add to customer list

### 4. Re-engagement Campaign
**Trigger**: No email engagement in 90 days
**Actions**:
- Send re-engagement email
- If no response in 30 days, remove from active lists
- Tag as "inactive"

### 5. Upsell Opportunities
**Trigger**: Customer property changes
**Actions**:
- Identify expansion opportunities
- Create tasks for account managers
- Send targeted content
- Track engagement

## Best Practices

### Workflow Design
✅ Start simple, add complexity gradually  
✅ Test workflows with small groups first  
✅ Use clear, descriptive names  
✅ Document workflow logic  
✅ Set up proper enrollment criteria  

### Performance Optimization
✅ Use specific enrollment triggers  
✅ Limit workflow complexity  
✅ Regular performance reviews  
✅ Clean up unused workflows  
✅ Monitor enrollment numbers  

### Data Quality
✅ Validate data before workflow actions  
✅ Handle edge cases (empty properties)  
✅ Test with different contact types  
✅ Monitor error rates  
✅ Set up fallback actions  

## Troubleshooting

### Common Issues
- **Contacts not enrolling**: Check enrollment criteria
- **Actions not triggering**: Verify property values
- **Emails not sending**: Check email template status
- **Performance issues**: Review workflow complexity

### Debugging Steps
1. Check workflow enrollment criteria
2. Verify contact meets all conditions  
3. Test with sample contacts
4. Review workflow action logs
5. Check for conflicting workflows

## HubSpot UI Tips

### Workflow Builder
- Visual drag-and-drop interface
- Preview enrollment criteria
- Test workflow logic
- Clone existing workflows
- Set up A/B tests

### Workflow Analytics
- Monitor enrollment rates
- Track action completion
- Measure goal achievement
- Compare workflow performance
- Export performance data