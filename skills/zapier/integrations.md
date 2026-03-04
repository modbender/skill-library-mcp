# Popular Integrations — Zapier

## Google Workspace

### Google Sheets

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Spreadsheet Row | Process new entries |
| New or Updated Row | Sync changes |
| New Spreadsheet | Monitor file creation |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Spreadsheet Row | Log data |
| Update Spreadsheet Row | Modify existing |
| Lookup Spreadsheet Row | Find by value |
| Create Spreadsheet | Generate reports |

**Common Pattern: Form to Sheet**
```
Typeform → Create Row in Google Sheets
  Name: {{trigger.name}}
  Email: {{trigger.email}}
  Submitted: {{zap_meta_human_now}}
```

### Gmail

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Email | Process incoming |
| New Labeled Email | Filtered processing |
| New Attachment | File handling |

**Actions:**
| Action | Use Case |
|--------|----------|
| Send Email | Notifications |
| Create Draft | Review before send |
| Add Label | Organization |

**Common Pattern: Lead Notification**
```
New Salesforce Lead
→ Send Gmail:
  To: sales@company.com
  Subject: New Lead: {{trigger.name}}
  Body: Company: {{trigger.company}}
        Email: {{trigger.email}}
```

### Google Calendar

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Event | Track meetings |
| Event Start | Reminders |
| Updated Event | Sync changes |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Event | Schedule meetings |
| Quick Add Event | Natural language |
| Find Event | Lookup existing |
| Update Event | Modify details |

### Google Drive

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New File in Folder | Process uploads |
| New File (any) | Global monitoring |
| Updated File | Track changes |

**Actions:**
| Action | Use Case |
|--------|----------|
| Upload File | Store documents |
| Copy File | Duplicate templates |
| Create Folder | Organization |
| Move File | Workflow routing |

## Slack

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Message (Channel) ⚡ | Monitor discussions |
| New Message (DM) ⚡ | Personal alerts |
| New Reaction ⚡ | Approval workflows |
| New User | Onboarding |

**Actions:**
| Action | Use Case |
|--------|----------|
| Send Channel Message | Notifications |
| Send Direct Message | Personal alerts |
| Create Channel | Project channels |
| Set Status | Availability |
| Add Reaction | Confirmations |

**Common Pattern: Error Alert**
```
Catch Hook (error webhook)
→ Send Slack Message:
  Channel: #alerts
  Text: 🚨 Error: {{trigger.error_message}}
        Service: {{trigger.service}}
        Time: {{zap_meta_human_now}}
```

**Slack Blocks (Rich Messages):**
```json
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*New Lead* 🎉\n*Name:* {{trigger.name}}\n*Company:* {{trigger.company}}"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "View in CRM"},
          "url": "https://crm.example.com/leads/{{trigger.id}}"
        }
      ]
    }
  ]
}
```

## Salesforce

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Lead | Sales pipeline |
| New Contact | Customer management |
| New Opportunity | Deal tracking |
| Updated Record | Sync changes |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Lead | Inbound leads |
| Create Contact | Customer records |
| Create Opportunity | Deal creation |
| Update Record | Status changes |
| Find Record | Lookups |
| Add to Campaign | Marketing |

**Common Pattern: Web-to-Lead**
```
Typeform Submission
→ Find or Create Salesforce Contact (by email)
→ Create Salesforce Lead:
  First Name: {{trigger.first_name}}
  Last Name: {{trigger.last_name}}
  Email: {{trigger.email}}
  Company: {{trigger.company}}
  Lead Source: Website
```

## HubSpot

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Contact | CRM sync |
| New Deal | Pipeline |
| Form Submission | Lead capture |
| New Company | Account management |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create/Update Contact | Sync contacts |
| Create Deal | Sales pipeline |
| Create Company | Account records |
| Create Engagement | Log activities |
| Add to List | Segmentation |

## Notion

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Database Item | Track additions |
| Updated Database Item | Sync changes |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Database Item | Add records |
| Update Database Item | Modify records |
| Append to Page | Add content |
| Create Page | New documents |

**Common Pattern: Task Management**
```
New Slack Message in #requests
→ Create Notion Database Item:
  Database: Tasks
  Name: {{trigger.text}}
  Status: To Do
  Requested By: {{trigger.user.name}}
```

## Airtable

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Record | Process additions |
| New or Updated Record | Sync all changes |
| New Record in View | Filtered processing |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Record | Add data |
| Update Record | Modify data |
| Find Record | Lookups |
| Find or Create | Dedupe sync |
| Delete Record | Cleanup |

## Stripe

**Triggers (all instant ⚡):**
| Trigger | Use Case |
|---------|----------|
| New Payment | Revenue tracking |
| New Customer | User sync |
| New Subscription | SaaS metrics |
| Canceled Subscription | Churn handling |
| Failed Payment | Dunning |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Customer | Setup billing |
| Create Charge | One-time payment |
| Create Invoice | Billing |

## Mailchimp / Email Marketing

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Subscriber | Welcome flow |
| Unsubscribed | Churn tracking |
| Campaign Sent | Tracking |

**Actions:**
| Action | Use Case |
|--------|----------|
| Add Subscriber | List building |
| Update Subscriber | Profile sync |
| Add/Remove Tags | Segmentation |
| Send Campaign | Newsletters |

## Trello / Asana / Monday.com

**Common Triggers:**
- New Card/Task
- Card/Task Moved
- Due Date Approaching

**Common Actions:**
- Create Card/Task
- Update Card/Task
- Move Card/Task
- Add Comment

**Common Pattern: Issue to Task**
```
New GitHub Issue
→ Create Trello Card:
  Board: Development
  List: Backlog
  Name: {{trigger.title}}
  Description: {{trigger.body}}
  Due Date: +7 days
```

## Twilio (SMS)

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New SMS ⚡ | Two-way messaging |
| New Call ⚡ | Call tracking |

**Actions:**
| Action | Use Case |
|--------|----------|
| Send SMS | Notifications |
| Make Call | Phone alerts |

**Common Pattern: Order Shipped**
```
Shopify Order Fulfilled
→ Send Twilio SMS:
  To: {{trigger.customer.phone}}
  Body: Your order {{trigger.order_number}} has shipped! 
        Track: {{trigger.tracking_url}}
```

## GitHub

**Triggers:**
| Trigger | Use Case |
|---------|----------|
| New Issue ⚡ | Bug tracking |
| New Pull Request ⚡ | Code review |
| New Commit ⚡ | CI/CD |
| New Release | Announcements |

**Actions:**
| Action | Use Case |
|--------|----------|
| Create Issue | Ticket creation |
| Create Comment | Responses |
| Update Issue | Status changes |

## Multi-App Patterns

### Lead → CRM → Notification
```
Typeform (New Entry)
→ Find or Create Salesforce Contact
→ Create Salesforce Lead
→ Send Slack Message to #sales
→ Create Google Calendar Event (follow-up)
```

### Payment → Delivery → Communication
```
Stripe (New Payment)
→ Update Airtable Order Status
→ Send Gmail Order Confirmation
→ Send Twilio SMS with ETA
→ Create Trello Card for Fulfillment
```

### Content → Distribution
```
WordPress (New Post)
→ Create Twitter Thread
→ Post to LinkedIn
→ Send to Mailchimp Campaign
→ Create Buffer Queue Item
```
