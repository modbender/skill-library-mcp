# Hylo GHL Knowledge API — Quick Reference

## Workflow Actions (102 total, 19 categories)

| Category | # | Examples |
|----------|---|---------|
| Communication | 27 | Send Email, Send SMS, WhatsApp, Call, Voicemail, Instagram DM |
| Contact | 16 | Create Contact, Find Contact, Add Contact Tag, Update Contact Field |
| Internal | 16 | If / Else, Wait, Split, Go To, Math Operation, Custom Code (BETA) |
| Opportunity | 9 | Create/Update Opportunity, Find Opportunity (BETA) |
| Conversation AI | 8 | AI Capture Information, Book Appointment, AI Splitter, AI Message |
| Affiliate | 6 | Add To Affiliate Manager, Add Leads Under An Affiliate |
| Communities | 6 | Smart Push Notification, Grant Group Access, Revoke Group Access |
| Custom Objects | 5 | Create/Update/Clear Associated Record For Contact |
| Marketing | 5 | Google Ads, Facebook Custom Audience, Meta Conversion API |
| Payments | 5 | Stripe One Time Charge, Send Invoice, Send Estimate |
| IVR | 5 | Gather Input On Call, Connect To Call, End Call |
| External AI Models | 4 | GPT Powered By OpenAI, Eliza, Send To Eliza Agent Platform |
| AI Actions | 4 | AI Translate, AI Summarize, AI Intent Detection, AI Decision Maker |
| Send Data | 3 | Webhook, Custom Webhook, Google Sheets |
| Appointments | 3 | Update Appointment Status, Generate One Time Booking Link |
| Company | 3 | Create/Update/Clear Associated Company (BETA) |
| Membership | 2 | Course Grant Offer, Course Revoke Offer |
| Certificates | 1 | Issue Certificate |
| Voice AI | 1 | Voice AI Outbound Call (BETA) |

## Workflow Triggers (70 total, 14 categories)

| Category | # | Examples |
|----------|---|---------|
| Events | 22 | Form Submitted, Customer Replied, Email Events, Inbound Webhook |
| Contact | 12 | Contact Created, Contact Changed, Birthday Reminder, Task Added |
| Courses | 12 | New Signup, Lesson Started/Completed, Product Access Granted |
| Payments | 12 | Payment Received, Invoice, Subscription, Refund, Order Submitted |
| Opportunities | 5 | Pipeline Stage Changed, Opportunity Created/Changed |
| Communities | 5 | Group Access Granted/Revoked, Leaderboard Level Changed |
| Affiliate | 4 | Affiliate Created, New Affiliate Sales |
| Appointments | 3 | Customer Booked Appointment, Appointment Status |
| Shopify | 3 | Abandoned Checkout, Order Placed, Order Fulfilled |
| Facebook/Instagram | 2 | Comments On A Post (BETA) |
| Communication | 2 | TikTok Comments On A Video, Transcript Generated |
| IVR | 1 | Start IVR Trigger |
| Certificates | 1 | Certificates Issued |
| Google Ads | 1 | Google Lead Form Submitted |

## Navigate/Protocol Features

Use with `GET /navigate/{feature}` (quick hints) or `GET /protocols/{feature}` (full step-by-step with selectors).

| Feature | Description |
|---------|-------------|
| common | Common GHL UI patterns (shared across features) |
| workflows | Workflow builder navigation and creation |
| calendar | Calendar and appointment settings |
| custom-values | Custom values/fields management |
| forms-sites | Forms, surveys, funnels, and websites |
| ai-bot | Conversation AI bot configuration |
| email-domain | Email and domain setup |
| marketing | Marketing tools and ad integrations |

## API Schema Categories (423 endpoints)

Top categories by endpoint count:

| Category | # | Category | # |
|----------|---|----------|---|
| invoices | 41 | social-media-posting | 40 |
| calendars | 34 | contacts | 31 |
| products | 27 | locations | 25 |
| payments | 24 | conversations | 20 |
| store | 18 | knowledge-bases | 14 |
| saas | 11 | saas-api | 11 |
| voice-ai | 11 | associations | 10 |
| opportunities | 10 | objects | 9 |
| custom-fields | 8 | blogs | 7 |
| funnels | 7 | marketplace | 7 |

Use `GET /schemas?q=KEYWORD` to search, or `GET /schemas?category=CATEGORY` to list a category.

## POST Body Examples

### POST /templates/workflow

```bash
curl -X POST https://api.hylo.pro/v1/templates/workflow \
  -H "Authorization: Bearer $HYLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Send 3 follow-up emails after a contact fills out a form",
    "constraints": {
      "max_steps": 10,
      "include_delays": true
    }
  }'
```

### POST /validate

```bash
curl -X POST https://api.hylo.pro/v1/validate \
  -H "Authorization: Bearer $HYLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "Contact Created",
    "actions": [
      {"type": "Send Email", "config": {"delay": "5m"}},
      {"type": "Add Tag", "config": {"tag": "new-lead"}}
    ]
  }'
```
