# KallyAI API Reference

## Table of Contents

1. [Authentication](#authentication)
2. [Coordination Endpoints](#coordination-endpoints)
3. [Call Endpoints](#call-endpoints)
4. [Inbound Endpoints](#inbound-endpoints)
5. [Phone Number Endpoints](#phone-number-endpoints)
6. [Actions Endpoints](#actions-endpoints)
7. [Messages Endpoints](#messages-endpoints)
8. [Search Endpoints](#search-endpoints)
9. [Email Management Endpoints](#email-management-endpoints)
10. [Channel Endpoints](#channel-endpoints)
11. [Outreach Endpoints](#outreach-endpoints)
12. [Budget Endpoints](#budget-endpoints)
13. [Credits Endpoints](#credits-endpoints)
14. [Subscription Endpoints](#subscription-endpoints)
15. [Referral Endpoints](#referral-endpoints)
16. [Notification Endpoints](#notification-endpoints)
17. [Error Codes](#error-codes)

---

## Authentication

**Type:** OAuth2 Bearer Token

**Header:**
```
Authorization: Bearer <access_token>
```

### Authentication Methods

| Method | Use Case | Endpoint |
|--------|----------|----------|
| CLI Auth | Terminal tools, AI agents | `GET /v1/auth/cli` |
| OAuth2 Authorization Code | GPT Actions, web apps | `GET /v1/auth/authorize` |
| Google Sign-In | Mobile apps | `POST /v1/auth/google/validate` |
| Apple Sign-In | iOS apps | `POST /v1/auth/apple/token` |

### CLI Authentication (Terminal Tools & AI Agents)

**Step 1: Open auth page with localhost redirect**
```
GET /v1/auth/cli?redirect_uri=http://localhost:PORT&state=OPTIONAL_STATE
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `redirect_uri` | Yes | Must be `http://localhost:PORT` or `http://127.0.0.1:PORT` |
| `state` | No | CSRF protection token passed back in redirect |

After authentication, redirects to:
```
http://localhost:PORT?access_token=TOKEN&refresh_token=TOKEN&expires_in=3600&state=STATE
```

**Security:** Only localhost/127.0.0.1 redirect URIs are allowed.

### OAuth2 Authorization Code Flow (GPT Actions)

**Step 1: Redirect to authorization**
```
GET /v1/auth/authorize?response_type=code&client_id=ID&redirect_uri=URI&state=STATE&scope=SCOPES
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `response_type` | Yes | Must be `code` |
| `client_id` | Yes | OAuth client ID |
| `redirect_uri` | Yes | Callback URL |
| `state` | No | CSRF protection |
| `scope` | No | Space-separated scopes |

**Step 2: Exchange code for tokens**
```
POST /v1/auth/gpt/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&client_id=ID&client_secret=SECRET&code=CODE&redirect_uri=URI
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "scope": "calls:read calls:write coordination:read coordination:write"
}
```

### Google Sign-In (Mobile)

```
POST /v1/auth/google/validate
Content-Type: application/json

{"id_token": "GOOGLE_ID_TOKEN"}
```

### Apple Sign-In (iOS)

```
POST /v1/auth/apple/token
Content-Type: application/json

{
  "identity_token": "APPLE_IDENTITY_TOKEN",
  "authorization_code": "APPLE_AUTH_CODE",
  "full_name": "John Smith"
}
```

### Token Refresh

```
POST /v1/auth/refresh
Content-Type: application/json

{"refresh_token": "REFRESH_TOKEN"}
```

### Scopes

| Scope | Description |
|-------|-------------|
| `calls:read` | Read call history and details |
| `calls:write` | Make and manage phone calls |
| `coordination:read` | Read goals and conversations |
| `coordination:write` | Create goals, send messages |
| `actions:read` | Read action log and results |
| `actions:write` | Create calendar events, bookings, etc. |
| `messages:read` | Read inbox messages |
| `messages:write` | Mark messages read |
| `search:read` | Perform searches |
| `email:read` | Read email messages |
| `email:write` | Send emails, manage accounts |
| `credits:read` | Read credit balance and history |
| `budget:read` | Read budget info |
| `budget:write` | Approve budgets |
| `transcripts:read` | Read call transcripts |
| `recordings:read` | Access call recordings |
| `subscription:read` | Read subscription status |
| `billing:manage` | Access billing portal |

---

## Coordination Endpoints

### Send Message

**`POST /v1/coordination/message`**

Send a natural language message to the coordination AI. Automatically creates goals and dispatches actions.

**Request:**
```json
{
  "message": "Book a table at Nobu for 4 tonight at 8pm",
  "conversation_id": "uuid (optional)"
}
```

**Response:**
```json
{
  "response": "I'll book a table at Nobu for 4 at 8pm tonight. Creating a goal for this now.",
  "goal_id": "uuid",
  "conversation_id": "uuid",
  "actions_taken": ["goal_created", "call_initiated"]
}
```

---

### Get Conversation History

**`GET /v1/coordination/history`**

| Param | Type | Description |
|-------|------|-------------|
| `conversation_id` | string | Filter by conversation |
| `limit` | int | Max results |

---

### List Conversations

**`GET /v1/coordination/conversations`**

**Response:**
```json
{
  "conversations": [
    {"id": "uuid", "title": "Restaurant booking", "created_at": "2026-02-13T10:00:00Z", "message_count": 5}
  ]
}
```

---

### Create Conversation

**`POST /v1/coordination/conversations`**

Creates a new empty conversation.

---

### List Goals

**`GET /v1/coordination/goals`**

| Param | Type | Description |
|-------|------|-------------|
| `status` | enum | `active`, `completed`, `cancelled`, `pending`, `archived` |
| `limit` | int | Max results |

**Response:**
```json
{
  "goals": [
    {
      "id": "uuid",
      "title": "Book restaurant",
      "status": "active",
      "created_at": "2026-02-13T10:00:00Z",
      "credits_used": 2,
      "sub_goal_count": 1
    }
  ]
}
```

---

### Get Goal Details

**`GET /v1/coordination/goals/{goal_id}`**

**Response:**
```json
{
  "id": "uuid",
  "title": "Book restaurant at Nobu",
  "status": "active",
  "description": "Reserve table for 4 at 8pm",
  "created_at": "2026-02-13T10:00:00Z",
  "updated_at": "2026-02-13T10:02:00Z",
  "credits_used": 2,
  "credits_estimated": 3,
  "parent_goal_id": null,
  "steps": [
    {"step": 1, "description": "Search for Nobu phone number", "status": "completed"},
    {"step": 2, "description": "Call Nobu to reserve", "status": "in_progress"}
  ]
}
```

---

### Get Goal Tree

**`GET /v1/coordination/goals/{goal_id}/tree`**

Returns goal with all sub-goals as a tree structure.

---

### Cancel Goal

**`POST /v1/coordination/goals/{goal_id}/cancel`**

Cancels a single goal (not sub-goals).

---

### Cascade Cancel

**`POST /v1/coordination/goals/{goal_id}/cascade-cancel`**

Cancels goal and all sub-goals recursively.

---

### Escalate Goal

**`POST /v1/coordination/goals/{goal_id}/escalate`**

Marks goal for user attention (e.g., needs decision, hit budget limit).

---

### Approve Step

**`POST /v1/coordination/goals/{goal_id}/approve-step`**

Approves the next pending approval step in a goal.

---

### Accept Outcome

**`POST /v1/coordination/goals/{goal_id}/accept-outcome`**

Accepts the goal's result and marks it satisfied.

---

### Continue Negotiating

**`POST /v1/coordination/goals/{goal_id}/continue-negotiating`**

Instructs KallyAI to continue negotiating (e.g., ask for better price, different time).

---

### Archive Goal

**`POST /v1/coordination/goals/{goal_id}/archive`**

Archives a completed/cancelled goal.

---

### Batch Archive

**`POST /v1/coordination/goals/batch-archive`**

**Request:**
```json
{"goal_ids": ["uuid1", "uuid2"]}
```

---

### Get Goal Budget

**`GET /v1/coordination/goals/{goal_id}/budget`**

**Response:**
```json
{
  "goal_id": "uuid",
  "credits_estimated": 5,
  "credits_used": 2,
  "credits_remaining": 3,
  "breakdown": [
    {"action": "phone_call", "credits": 1.5},
    {"action": "search", "credits": 0.5}
  ]
}
```

---

## Call Endpoints

### Create Call

**`POST /v1/calls`**

**Headers:**
```
Authorization: Bearer <token>
Idempotency-Key: <uuid> (recommended)
```

**Request:**
```json
{
  "submission": {
    "task_category": "restaurant",
    "task_description": "Reserve table for 4 at 8pm",
    "respondent_phone": "+15551234567",
    "business_name": "Nobu",
    "user_name": "John Smith",
    "party_size": 4,
    "appointment_date": "2026-02-14",
    "appointment_time": "20:00",
    "language": "en",
    "call_language": "en",
    "is_urgent": false,
    "additional_instructions": []
  },
  "timezone": "America/New_York"
}
```

**SubmissionPayload fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_category` | enum | Yes | `restaurant`, `clinic`, `hotel`, `general` |
| `task_description` | string | Yes | What the AI should accomplish |
| `respondent_phone` | string | Yes | Phone to call (E.164: +1234567890) |
| `business_name` | string | No | Business name |
| `user_name` | string | No | User's name |
| `user_phone` | string | No | User's callback number |
| `appointment_date` | date | No | YYYY-MM-DD |
| `appointment_time` | string | No | HH:MM (24-hour) |
| `time_preference_text` | string | No | "morning", "after 5pm" |
| `party_size` | int | No | 1-50 |
| `language` | enum | No | `en`, `es` (app language) |
| `call_language` | enum | No | `en`, `es` (call language) |
| `is_urgent` | bool | No | Prioritize call |
| `additional_instructions` | array | No | Extra instructions |

**Response:** `201 Created`
```json
{
  "call_id": "uuid",
  "status": "success",
  "highlights": "Reserved table for 4 at 8pm on Feb 14",
  "next_steps": "Confirmation number: #12345",
  "duration_seconds": 95.2,
  "credits_used": 1.5,
  "metadata": {"created_at": "2026-02-13T15:30:00Z"},
  "submission": {}
}
```

---

### List Calls

**`GET /v1/calls`**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 50 | Max results (1-200) |
| `offset` | int | 0 | Pagination offset |

---

### Get Call Details

**`GET /v1/calls/{call_id}`**

Returns full call details including submission, highlights, next_steps, duration.

---

### Get Transcript

**`GET /v1/calls/{call_id}/transcript`**

**Response:**
```json
{
  "entries": [
    {"speaker": "AI", "content": "Hello, I'm calling to make a reservation.", "timestamp": "00:00:01"},
    {"speaker": "HUMAN", "content": "Hi, how can I help you?", "timestamp": "00:00:05"}
  ]
}
```

---

### Get Recording

**`GET /v1/calls/{call_id}/recording`**

**Response:**
```json
{
  "url": "https://storage.kallyai.com/recordings/...",
  "duration_seconds": 95.2,
  "format": "mp3"
}
```

Requires `recordings:read` scope.

---

### Get Calendar Event

**`GET /v1/calls/{call_id}/calendar.ics`**

Returns ICS calendar file for importing appointments extracted from call.

---

### Cancel Call

**`POST /v1/calls/{call_id}/cancel`**

Cancel a scheduled or queued call before it connects.

---

### Reschedule Call

**`POST /v1/calls/{call_id}/reschedule`**

**Request:**
```json
{
  "date": "2026-02-15",
  "time": "19:00"
}
```

---

### Stop Call

**`POST /v1/calls/{call_id}/stop`**

Immediately disconnect an active call.

---

## Inbound Endpoints

> AI receptionist — handles incoming calls automatically.

### List Inbound Calls

**`GET /v1/inbound/calls`**

| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Max results (1-100, default 20) |
| `offset` | int | Pagination offset |
| `status` | enum | `active`, `completed`, `missed`, `rejected` |
| `vip_only` | bool | Only VIP caller calls |
| `date_from` | string | Start date filter |
| `date_to` | string | End date filter |

---

### Delete Inbound Calls

**`DELETE /v1/inbound/calls`**

Bulk delete inbound call records.

---

### Get Inbound Call Summary

**`GET /v1/inbound/calls/summary`**

Returns aggregate statistics for inbound calls (total, completed, missed, avg duration).

---

### Get Inbound Call Analytics

**`GET /v1/inbound/calls/analytics`**

| Param | Type | Description |
|-------|------|-------------|
| `date_from` | string | Start date |
| `date_to` | string | End date |

---

### Get Inbound Call Details

**`GET /v1/inbound/calls/{call_id}`**

Returns full inbound call details including caller info, summary, action items.

---

### Get Inbound Call Transcript

**`GET /v1/inbound/calls/{call_id}/transcript`**

---

### Get Inbound Call Recording

**`GET /v1/inbound/calls/{call_id}/recording`**

---

### Update Action Item

**`PATCH /v1/inbound/calls/{call_id}/action-items/{index}`**

**Request:**
```json
{"status": "completed"}
```

---

### Transfer Call

**`POST /v1/inbound/calls/{call_id}/transfer`**

Transfer a live inbound call to another number.

**Request:**
```json
{"target_number": "+15551234567"}
```

---

### Take Over Call

**`POST /v1/inbound/calls/{call_id}/takeover`**

Take over a live inbound call (switch from AI to human).

---

### Reject Call

**`POST /v1/inbound/calls/{call_id}/reject`**

**Request:**
```json
{"reason": "user_rejected"}
```

---

### List Routing Rules

**`GET /v1/inbound/rules`**

Returns call routing rules ordered by priority.

---

### Create Routing Rule

**`POST /v1/inbound/rules`**

**Request:**
```json
{
  "name": "VIP callers",
  "priority": 10,
  "is_active": true,
  "conditions": {"caller_vip": true},
  "action": "transfer",
  "action_config": {"target": "+15551234567"}
}
```

---

### Update Routing Rule

**`PUT /v1/inbound/rules/{rule_id}`**

---

### Delete Routing Rule

**`DELETE /v1/inbound/rules/{rule_id}`**

---

### List Voicemails

**`GET /v1/inbound/voicemails`**

---

### Get Voicemail Details

**`GET /v1/inbound/voicemails/{voicemail_id}`**

---

### Get Voicemail Playback

**`GET /v1/inbound/voicemails/{voicemail_id}/playback`**

Returns audio URL for voicemail playback.

---

### List Contacts

**`GET /v1/inbound/contacts`**

Returns contacts used for caller identification and VIP routing.

---

### Create Contact

**`POST /v1/inbound/contacts`**

**Request:**
```json
{
  "name": "John Smith",
  "phone_number": "+15551234567",
  "is_vip": true,
  "notes": "Key client"
}
```

---

### Update Contact

**`PUT /v1/inbound/contacts/{contact_id}`**

---

### Delete Contact

**`DELETE /v1/inbound/contacts/{contact_id}`**

---

### Import Contacts

**`POST /v1/inbound/contacts/import`**

**Request:**
```json
{"source": "google"}
```

---

### Get Inbound Events

**`GET /v1/inbound/events`**

Returns event log for inbound call activity (SSE-capable).

---

### Get Stream Info

**`GET /v1/inbound/stream/info`**

Returns info about the real-time inbound call event stream.

---

## Phone Number Endpoints

> Manage KallyAI phone numbers for inbound and outbound calls.

### List Supported Countries

**`GET /v1/phone-numbers/supported-countries`**

Returns countries where phone numbers can be provisioned and calls can be made.

---

### Get Forwarding Targets

**`GET /v1/phone-numbers/forwarding-targets`**

Returns configured forwarding target numbers.

---

### Search Available Numbers

**`GET /v1/phone-numbers/available`**

| Param | Type | Description |
|-------|------|-------------|
| `country` | string | ISO country code (e.g., "US") |
| `area_code` | string | Optional area code filter |

---

### Provision Number

**`POST /v1/phone-numbers/provision`**

**Request:**
```json
{
  "country": "US",
  "area_code": "415"
}
```

---

### Set Up Forwarding Number

**`POST /v1/phone-numbers/forwarding`**

Configure a forwarding number (user's existing phone) for call handoff.

---

### Start Phone Verification

**`POST /v1/phone-numbers/verify/start`**

**Request:**
```json
{"phone_number": "+15551234567"}
```

---

### Check Verification Code

**`POST /v1/phone-numbers/verify/check`**

**Request:**
```json
{"phone_number": "+15551234567", "code": "123456"}
```

---

### Configure Verified Number

**`POST /v1/phone-numbers/verify/configure`**

---

### List Phone Numbers

**`GET /v1/phone-numbers`**

Returns all phone numbers owned by the user.

---

### Get Phone Number

**`GET /v1/phone-numbers/{phone_number_id}`**

---

### Set Call Forwarding

**`PUT /v1/phone-numbers/{phone_number_id}/forwarding`**

**Request:**
```json
{"forwarding_number": "+15559876543"}
```

---

### Remove Call Forwarding

**`DELETE /v1/phone-numbers/{phone_number_id}/forwarding`**

---

### Verify Phone Number Ownership

**`POST /v1/phone-numbers/{phone_number_id}/verify`**

---

### Get Phone Number Details

**`GET /v1/phone-numbers/{phone_number_id}/details`**

Returns extended details including capabilities and configuration.

---

### Set Caller ID

**`PUT /v1/phone-numbers/{phone_number_id}/caller-id`**

**Request:**
```json
{"caller_id_name": "John's Office"}
```

---

### Release Phone Number

**`DELETE /v1/phone-numbers/{phone_number_id}`**

Releases the phone number (cannot be undone).

---

## Actions Endpoints

### Calendar

#### Create Event

**`POST /v1/actions/calendar/events`**

**Request:**
```json
{
  "title": "Dinner at Nobu",
  "start": "2026-02-14T20:00:00",
  "end": "2026-02-14T22:00:00",
  "location": "Nobu Restaurant",
  "description": "Table for 4, confirmation #12345"
}
```

#### Get Available Slots

**`GET /v1/actions/calendar/slots`**

| Param | Type | Description |
|-------|------|-------------|
| `date` | string | YYYY-MM-DD |
| `duration_minutes` | int | Slot duration |

#### Sync Calendar

**`POST /v1/actions/calendar/sync`**

Triggers sync with connected calendar providers (Google Calendar, Outlook).

#### Delete Event

**`DELETE /v1/actions/calendar/events/{event_id}`**

---

### Restaurant Search

**`POST /v1/actions/bookings/restaurants/search`**

**Request:**
```json
{
  "query": "Italian restaurant downtown",
  "location": "New York, NY",
  "party_size": 4,
  "date": "2026-02-14",
  "time": "20:00"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "rest_uuid",
      "name": "Carbone",
      "cuisine": "Italian",
      "rating": 4.7,
      "price_range": "$$$$",
      "phone": "+12125551234",
      "address": "181 Thompson St",
      "availability": "available"
    }
  ]
}
```

---

### Bookings

#### Create Booking

**`POST /v1/actions/bookings`**

**Request:**
```json
{
  "type": "restaurant",
  "restaurant_id": "rest_uuid",
  "date": "2026-02-14",
  "time": "20:00",
  "party_size": 4,
  "name": "John Smith",
  "notes": "Window table preferred"
}
```

#### Cancel Booking

**`DELETE /v1/actions/bookings/{booking_id}`**

---

### Bill Analysis

#### Analyze Bill

**`POST /v1/actions/bills/analyze`**

**Request:**
```json
{
  "description": "Comcast internet bill $89.99/month",
  "amount": 89.99,
  "provider": "Comcast"
}
```

**Response:**
```json
{
  "analysis": {
    "fair_price_range": "$50-70",
    "overcharge_detected": true,
    "savings_potential": "$20-40/month",
    "recommendations": ["Call to negotiate", "Mention competitor pricing"]
  }
}
```

#### Dispute Bill

**`POST /v1/actions/bills/dispute`**

**Request:**
```json
{
  "description": "Unexpected $35 fee on cable bill",
  "amount": 35.00,
  "provider": "Comcast",
  "reason": "Unauthorized charge"
}
```

---

### Task Actions

#### Request Ride

**`POST /v1/actions/tasks/ride`**

**Request:**
```json
{
  "pickup": "123 Main St",
  "destination": "JFK Airport",
  "pickup_time": "2026-02-14T16:00:00"
}
```

#### Order Food

**`POST /v1/actions/tasks/food`**

**Request:**
```json
{
  "description": "2 pepperoni pizzas from Joe's Pizza",
  "delivery_address": "456 Oak Ave"
}
```

#### Run Errand

**`POST /v1/actions/tasks/errand`**

**Request:**
```json
{
  "description": "Pick up dry cleaning from ABC Cleaners on 5th Ave"
}
```

---

### Email Actions

#### Send Email

**`POST /v1/actions/email/send`**

Queues an email for approval before sending.

**Request:**
```json
{
  "to": "doctor@clinic.com",
  "subject": "Reschedule appointment",
  "body": "I need to reschedule my Thursday appointment. Is Friday available?",
  "cc": "spouse@email.com"
}
```

#### Approve Queued Email

**`POST /v1/actions/email/{email_id}/approve`**

#### Cancel Queued Email

**`POST /v1/actions/email/{email_id}/cancel`**

#### List Outbox

**`GET /v1/actions/email/outbox`**

**Response:**
```json
{
  "emails": [
    {
      "id": "uuid",
      "to": "doctor@clinic.com",
      "subject": "Reschedule appointment",
      "status": "pending_approval",
      "created_at": "2026-02-13T10:00:00Z"
    }
  ]
}
```

#### Get Email Replies

**`GET /v1/actions/email/{email_id}/replies`**

---

### Action Log

**`GET /v1/actions/log`**

| Param | Type | Description |
|-------|------|-------------|
| `type` | enum | `calendar`, `booking`, `bill`, `ride`, `food`, `errand`, `email` |
| `limit` | int | Max results |

**Response:**
```json
{
  "actions": [
    {
      "id": "uuid",
      "type": "booking",
      "description": "Created restaurant booking at Nobu",
      "status": "completed",
      "created_at": "2026-02-13T10:00:00Z",
      "undoable": true
    }
  ]
}
```

### Undo Action

**`POST /v1/actions/{action_id}/undo`**

Reverses an action if it's undoable (e.g., cancel a booking, delete a calendar event).

---

## Messages Endpoints

### List Inbox

**`GET /v1/messages/inbox`**

| Param | Type | Description |
|-------|------|-------------|
| `channel` | enum | `email`, `sms`, `call`, `chat` |
| `limit` | int | Max results |
| `unread` | bool | Only unread messages |

**Response:**
```json
{
  "messages": [
    {
      "id": "uuid",
      "from": "doctor@clinic.com",
      "subject": "Appointment confirmed",
      "channel": "email",
      "preview": "Your appointment is confirmed for...",
      "unread": true,
      "received_at": "2026-02-13T14:00:00Z"
    }
  ]
}
```

---

### Read Message

**`GET /v1/messages/inbox/{message_id}`**

Returns full message content.

---

### Get Conversation Thread

**`GET /v1/messages/conversation/{conversation_id}`**

Returns all messages in a conversation thread.

---

### Mark Messages Read

**`POST /v1/messages/mark-read`**

**Request:**
```json
{"message_ids": ["uuid1", "uuid2"]}
```

---

## Search Endpoints

### Search

**`POST /v1/search`**

Full search with detailed results.

**Request:**
```json
{
  "query": "best plumber near me",
  "location": "San Francisco, CA"
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Mike's Plumbing",
      "description": "Licensed plumber, 4.9 stars",
      "phone": "+14155559876",
      "address": "789 Market St",
      "rating": 4.9,
      "price_range": "$$",
      "url": "https://mikesplumbing.com"
    }
  ],
  "credits_used": 0.5
}
```

---

### Quick Search

**`POST /v1/search/quick`**

Faster, less detailed search.

**Request:**
```json
{"query": "Nobu phone number"}
```

---

### Search History

**`GET /v1/search/history`**

Lists previous searches.

---

### Search Sources

**`GET /v1/search/sources`**

Lists available search providers and their capabilities.

---

## Email Management Endpoints

### List Accounts

**`GET /v1/email/accounts`**

**Response:**
```json
{
  "accounts": [
    {
      "id": "uuid",
      "provider": "gmail",
      "email": "user@gmail.com",
      "connected_at": "2026-01-15T10:00:00Z",
      "status": "active"
    }
  ]
}
```

---

### Connect Gmail

**`GET /v1/email/oauth/gmail/url`**

Returns OAuth URL for connecting Gmail account.

---

### Connect Outlook

**`GET /v1/email/oauth/outlook/url`**

Returns OAuth URL for connecting Outlook account.

---

### Disconnect Account

**`DELETE /v1/email/accounts/{account_id}`**

---

### List Email Messages

**`GET /v1/email/messages`**

| Param | Type | Description |
|-------|------|-------------|
| `classification` | enum | `important`, `actionable`, `informational`, `spam` |
| `limit` | int | Max results |

---

### Read Email

**`GET /v1/email/messages/{message_id}`**

Returns full email content with headers, body, and attachments list.

---

### Respond to Email

**`POST /v1/email/messages/{message_id}/respond`**

Generates a response using the user's voice profile.

**Request:**
```json
{
  "instructions": "Accept the meeting but suggest 3pm instead of 2pm"
}
```

---

### Get Voice Profile

**`GET /v1/email/voice-profile`**

Returns the user's email writing style profile.

---

### Train Voice Profile

**`POST /v1/email/voice-profile/train`**

Trains the voice profile from recent sent emails.

---

## Budget Endpoints

### Estimate Cost

**`POST /v1/goals/estimate`**

**Request:**
```json
{
  "type": "call",
  "description": "Call restaurant to make reservation"
}
```

**Response:**
```json
{
  "estimated_credits": 1.5,
  "breakdown": {
    "search": 0.5,
    "call": 1.0
  },
  "confidence": "high"
}
```

---

### Approve Budget

**`POST /v1/goals/{goal_id}/approve-budget`**

Approves the estimated budget for a goal to proceed.

---

### Get Cost Breakdown

**`GET /v1/goals/{goal_id}/cost-breakdown`**

**Response:**
```json
{
  "goal_id": "uuid",
  "total_credits": 3.5,
  "items": [
    {"action": "search", "credits": 0.5, "timestamp": "2026-02-13T10:00:00Z"},
    {"action": "call_1", "credits": 1.5, "timestamp": "2026-02-13T10:01:00Z"},
    {"action": "call_2", "credits": 1.5, "timestamp": "2026-02-13T10:05:00Z"}
  ]
}
```

---

### Acknowledge Soft Cap

**`POST /v1/goals/{goal_id}/acknowledge-soft-cap`**

Acknowledges that a goal has reached its soft budget cap, allowing it to continue.

---

## Credits Endpoints

> **Credits are the sole billing unit.** Minutes and calls_allocated are obsolete legacy fields.

### Get Balance

**`GET /v1/credits/balance`**

**Response:**
```json
{
  "credits_remaining": 458,
  "credits_used": 142,
  "credits_allocated": 600,
  "plan_type": "pro",
  "period_start": "2026-02-01T00:00:00Z",
  "period_end": "2026-03-01T00:00:00Z"
}
```

**Plans:**
| Plan | Credits/Month | Price |
|------|---------------|-------|
| Starter | 200 | $19 |
| Pro | 600 | $49 |
| Power | 1500 | $99 |
| Business | 4500 | $249 |

---

### Get History

**`GET /v1/credits/history`**

| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Max results |

**Response:**
```json
{
  "entries": [
    {
      "id": "uuid",
      "type": "call",
      "description": "Phone call to Nobu",
      "credits": 1.5,
      "timestamp": "2026-02-13T15:30:00Z",
      "goal_id": "uuid"
    }
  ]
}
```

---

### Get Cost Reference

**`GET /v1/credits/costs`**

Public endpoint — no authentication required.

**Response:**
```json
{
  "costs": {
    "call": {"base": 1.0, "per_minute": 0.1},
    "search": {"per_query": 0.5},
    "email_send": {"per_email": 0.3},
    "booking": {"per_booking": 0.5},
    "bill_analysis": {"per_analysis": 1.0},
    "ride": {"per_request": 0.5},
    "food": {"per_order": 0.5},
    "errand": {"per_errand": 1.0}
  }
}
```

---

### Get Spending Breakdown

**`GET /v1/credits/breakdown`**

Get credit spending breakdown grouped by action type for the current billing period.

**Response:**
```json
{
  "items": [
    {
      "action_type": "call",
      "credits_total": 85,
      "transaction_count": 12
    },
    {
      "action_type": "search",
      "credits_total": 30,
      "transaction_count": 15
    }
  ],
  "total_spent": 115,
  "period_start": "2026-02-01T00:00:00Z",
  "period_end": "2026-03-01T00:00:00Z"
}
```

---

### Get Credit Plans

**`GET /v1/credits/plans`**

Public endpoint — no authentication required. Returns available credit plans with details.

**Response:**
```json
{
  "plans": {
    "starter": {
      "name": "Starter",
      "credits_allocated": 200,
      "price_monthly": 19,
      "overage_rate": "0.15"
    },
    "pro": {
      "name": "Pro",
      "credits_allocated": 600,
      "price_monthly": 49,
      "overage_rate": "0.10"
    },
    "power": {
      "name": "Power",
      "credits_allocated": 1500,
      "price_monthly": 99,
      "overage_rate": "0.08"
    },
    "business": {
      "name": "Business",
      "credits_allocated": 4500,
      "price_monthly": 249,
      "overage_rate": "0.05"
    }
  }
}
```

---

## Channel Endpoints

Multi-channel management for email contacts, WhatsApp, and Telegram.

### Get All Channel Statuses

**`GET /v1/channels/status`**

Returns connection status for all available channels (email, WhatsApp, Telegram, LinkedIn, Instagram, Twitter).

**Response:**
```json
{
  "channels": [
    {
      "channel": "email",
      "connected": true,
      "account_name": "user@example.com",
      "connected_at": "2026-02-01T10:00:00Z"
    },
    {
      "channel": "whatsapp",
      "connected": false,
      "account_name": null,
      "connected_at": null
    },
    {
      "channel": "telegram",
      "connected": true,
      "account_name": "@MyBot",
      "connected_at": "2026-02-10T12:00:00Z"
    }
  ],
  "email": {
    "connected": true,
    "contact_count": 2,
    "primary_email": "user@example.com",
    "kally_mailbox": "assistant-abc123@kallyai.com"
  }
}
```

---

### Add Contact Email

**`POST /v1/channels/email/add`**

Register a contact email address. Sends a verification email.

**Request:**
```json
{
  "email_address": "user@example.com",
  "label": "Work",
  "is_primary": true
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email_address": "user@example.com",
  "label": "Work",
  "is_primary": true,
  "receives_copies": true,
  "receives_notifications": true,
  "verified": false,
  "verified_at": null,
  "created_at": "2026-02-13T10:00:00Z"
}
```

| Error | Code | Description |
|-------|------|-------------|
| 409 | Conflict | Email already registered |

---

### List Contact Emails

**`GET /v1/channels/email/list`**

List all registered contact emails for the user.

**Response:**
```json
{
  "emails": [
    {
      "id": "uuid",
      "email_address": "user@example.com",
      "label": "Work",
      "is_primary": true,
      "receives_copies": true,
      "receives_notifications": true,
      "verified": true,
      "verified_at": "2026-02-13T10:05:00Z",
      "created_at": "2026-02-13T10:00:00Z"
    }
  ],
  "total": 1,
  "kally_mailbox": "assistant-abc123@kallyai.com"
}
```

---

### Update Contact Email

**`PUT /v1/channels/email/{email_id}`**

Update a contact email's settings (label, primary, copies, notifications).

**Request:**
```json
{
  "label": "Personal",
  "is_primary": false,
  "receives_copies": true,
  "receives_notifications": false
}
```

---

### Delete Contact Email

**`DELETE /v1/channels/email/{email_id}`**

Remove a contact email address. Returns 204 on success.

---

### Verify Email

**`GET /v1/channels/email/verify?token=TOKEN`**

Verify a contact email using the token from the verification email. No authentication required. Redirects to app settings with success/error status.

---

### Get Kally Mailbox

**`GET /v1/channels/mailbox`**

Get the user's KallyAI internal mailbox address (format: `assistant-{user_id}@kallyai.com`).

**Response:**
```json
{
  "mailbox": "assistant-abc123@kallyai.com",
  "user_id": "abc123"
}
```

---

### Connect Webhook Channel

**`POST /v1/channels/webhook/{channel}/connect`**

Connect a webhook-based messaging channel (WhatsApp or Telegram).

**For Telegram:**
```json
{
  "bot_token": "123456:ABC-DEF..."
}
```

**For WhatsApp:**
```json
{
  "phone_number_id": "1234567890",
  "access_token": "EAAx...",
  "business_account_id": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "channel": "telegram",
  "account_name": "@MyBot"
}
```

---

### Test Webhook Connection

**`POST /v1/channels/webhook/{channel}/test`**

Test webhook credentials without saving. Same request body as connect.

**Response:**
```json
{
  "success": true,
  "account_name": "@MyBot"
}
```

---

### Disconnect Channel

**`POST /v1/channels/disconnect/{channel}`**

Disconnect a connected messaging channel (WhatsApp or Telegram). For email, use `DELETE /v1/channels/email/{email_id}` instead.

**Response:**
```json
{
  "success": true,
  "channel": "telegram"
}
```

---

## Outreach Endpoints

Multi-channel outreach task management with intelligent channel selection.

### List Outreach Tasks

**`GET /v1/outreach/tasks`**

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by status (comma-separated). Values: `pending`, `in_progress`, `completed`, `failed`, `cancelled` |
| `limit` | int | Max results (1-100, default 50) |
| `offset` | int | Pagination offset (default 0) |

**Response:**
```json
{
  "tasks": [
    {
      "id": "uuid",
      "goal": "Contact Dr. Smith about rescheduling",
      "recipient_identifier": "+15551234567",
      "recipient_name": "Dr. Smith",
      "status": "completed",
      "urgency": "high",
      "selected_channel": "call",
      "completed_via_channel": "call",
      "completion_summary": "Successfully rescheduled to Thursday 3pm",
      "created_at": "2026-02-13T10:00:00Z",
      "updated_at": "2026-02-13T10:05:00Z",
      "completed_at": "2026-02-13T10:05:00Z"
    }
  ],
  "total": 1,
  "has_more": false
}
```

---

### Get Outreach Task

**`GET /v1/outreach/tasks/{task_id}`**

Returns full task details including delivery attempts.

**Response:**
```json
{
  "id": "uuid",
  "goal": "Contact Dr. Smith about rescheduling",
  "recipient_identifier": "+15551234567",
  "recipient_name": "Dr. Smith",
  "status": "completed",
  "urgency": "high",
  "selected_channel": "call",
  "completed_via_channel": "call",
  "completion_summary": "Successfully rescheduled to Thursday 3pm",
  "created_at": "2026-02-13T10:00:00Z",
  "attempts": [
    {
      "channel": "call",
      "status": "success",
      "started_at": "2026-02-13T10:02:00Z",
      "completed_at": "2026-02-13T10:05:00Z"
    }
  ]
}
```

---

### Create Outreach Task

**`POST /v1/outreach/tasks`**

Create a new outreach task with intelligent channel selection.

**Request:**
```json
{
  "goal": "Contact Dr. Smith about rescheduling Thursday appointment",
  "recipient_identifier": "+15551234567",
  "recipient_name": "Dr. Smith",
  "urgency": "high",
  "coordination_message_id": "optional-msg-id",
  "auto_execute": true
}
```

**Response (201):** Same as Get Outreach Task.

---

### Retry Outreach Task

**`POST /v1/outreach/tasks/{task_id}/retry`**

Retry a failed or awaiting outreach task.

---

### Cancel Outreach Task

**`POST /v1/outreach/tasks/{task_id}/cancel`**

Cancel a pending or in-progress outreach task.

---

## Subscription Endpoints

Plan management — upgrades, downgrades, and status.

### Change Plan

**`POST /v1/subscriptions/change-plan`**

Upgrade, downgrade, or refresh subscription. Upgrades are instant. Downgrades are scheduled for next billing period.

**Request:**
```json
{
  "new_plan": "pro",
  "annual": false
}
```

**Response:**
```json
{
  "success": true,
  "change_type": "upgrade",
  "new_plan": "pro",
  "bonus_minutes": 0,
  "new_period_start": "2026-02-13T00:00:00Z",
  "new_period_end": "2026-03-13T00:00:00Z"
}
```

| `change_type` | Description |
|---------------|-------------|
| `upgrade` | Instant plan upgrade |
| `downgrade_scheduled` | Takes effect at next billing period |
| `refresh` | Reset billing period on same plan |

| Error | Code | Description |
|-------|------|-------------|
| 400 | `trial_requires_checkout` | Trial users must use Stripe Checkout |
| 400 | `pending_change_exists` | Cancel existing pending change first |
| 400 | `no_active_subscription` | No subscription found |
| 429 | `rate_limited` | Max 3 plan changes per hour |

---

### Cancel Pending Change

**`DELETE /v1/subscriptions/pending-change`**

Cancel a scheduled downgrade, keeping the current plan.

**Response:**
```json
{
  "success": true,
  "message": "Pending plan change canceled. Your current plan remains active."
}
```

---

### Get Subscription Status

**`GET /v1/subscriptions/status`**

Get current subscription status including any pending changes.

**Response:**
```json
{
  "plan_type": "pro",
  "status": "active",
  "current_period_start": "2026-02-01T00:00:00Z",
  "current_period_end": "2026-03-01T00:00:00Z",
  "pending_change": {
    "new_plan": "starter",
    "effective_date": "2026-03-01T00:00:00Z"
  }
}
```

---

## Referral Endpoints

Referral program management.

### Get Referral Code

**`GET /v1/referrals/code`**

Get or create the user's unique referral code.

**Response:**
```json
{
  "code": "ABC123",
  "is_active": true,
  "share_url": "https://kallyai.com/?ref=ABC123",
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### Get Referral Stats

**`GET /v1/referrals/stats`**

Get referral statistics — counts by status and total rewards earned.

**Response:**
```json
{
  "total_referrals": 5,
  "pending": 2,
  "converted": 3,
  "total_reward_minutes": 30,
  "total_reward_credits": 45.0
}
```

---

### Get Referral History

**`GET /v1/referrals/history`**

Get all referrals made by this user, ordered by creation date.

**Response:**
```json
{
  "referrals": [
    {
      "id": "uuid",
      "referred_email": "friend@example.com",
      "status": "converted",
      "referrer_reward_minutes": 10,
      "referred_reward_minutes": 10,
      "referrer_reward_credits": 15.0,
      "referred_reward_credits": 15.0,
      "created_at": "2026-01-20T10:00:00Z",
      "converted_at": "2026-01-25T14:30:00Z"
    }
  ]
}
```

---

### Validate Referral Code

**`GET /v1/referrals/validate/{code}`**

Validate a referral code. No authentication required. Rate limited to 20/hour per IP.

**Response:**
```json
{
  "valid": true,
  "code": "ABC123"
}
```

---

### Track Referral

**`POST /v1/referrals/track`**

Track a referral attribution when a user visits via referral link. No authentication required. Rate limited to 10/hour per IP.

**Request:**
```json
{
  "code": "ABC123",
  "email": "newuser@example.com"
}
```

**Response (201):**
```json
{
  "tracked": true,
  "message": "Referral tracked successfully"
}
```

---

## Notification Endpoints

Notification polling for pending actions, goals, and messages.

### Get Pending Notifications

**`GET /v1/notifications/pending`**

Aggregates counts from actions, goals, and inbox for notification polling.

**Response:**
```json
{
  "actions": {
    "count": 2,
    "items": [
      {"id": "uuid", "type": "email_approval", "summary": "Email to Dr. Smith ready for review"}
    ]
  },
  "goals": {
    "count": 1,
    "items": [
      {"id": "uuid", "status": "needs_input", "summary": "Restaurant booking needs date preference"}
    ]
  },
  "inbox": {
    "count": 3,
    "items": [
      {"id": "uuid", "channel": "email", "preview": "Re: Appointment confirmation"}
    ]
  },
  "total_pending": 6,
  "active_goal": {
    "id": "uuid",
    "summary": "Booking dinner at Nobu",
    "status": "in_progress",
    "current_step_description": "Calling restaurant"
  },
  "generated_at": "2026-02-13T15:30:00Z"
}
```

---

## Error Codes

### Standard Error Format

```json
{
  "error": {
    "code": "error_code",
    "message": "Human readable message",
    "details": {"reason": "Additional context"},
    "correlation_id": "uuid"
  }
}
```

### Error Code Reference

| Code | HTTP | Description |
|------|------|-------------|
| `quota_exceeded` | 402 | Out of credits |
| `budget_exceeded` | 402 | Goal over budget |
| `budget_approval_required` | 402 | Need to approve budget before proceeding |
| `soft_cap_reached` | 402 | Goal hit soft cap, needs acknowledgment |
| `missing_phone_number` | 422 | No phone in submission |
| `emergency_number` | 422 | Cannot call 911/emergency |
| `toll_number` | 422 | Cannot call premium rate numbers |
| `blocked_number` | 403 | Number flagged as fraud |
| `suppression_violation` | 403 | Number on DNC list |
| `safety_violation` | 422 | Content violates guidelines |
| `scheduling_violation` | 422 | Invalid date/time |
| `consent_denied` | 422 | User declined consent |
| `country_restriction` | 403 | Country not supported by region |
| `unsupported_country` | 403 | Country not supported globally |
| `unsupported_language` | 422 | Language not supported |
| `email_not_connected` | 400 | No email account connected |
| `email_send_failed` | 500 | Email delivery failed |
| `calendar_sync_failed` | 500 | Calendar sync error |
| `search_failed` | 500 | Search provider error |
| `goal_not_found` | 404 | Goal doesn't exist |
| `goal_already_completed` | 409 | Goal already finished |
| `goal_already_cancelled` | 409 | Goal already cancelled |
| `action_not_undoable` | 409 | Action cannot be reversed |
| `missing_token` | 401 | No Authorization header |
| `token_expired` | 401 | Access token expired |
| `forbidden` | 403 | Insufficient permissions |
| `call_not_found` | 404 | Call doesn't exist |
| `transcript_not_found` | 404 | No transcript available |
| `recording_not_found` | 404 | No recording available |
| `rate_limited` | 429 | Too many requests |

---

## Supported Countries

Calls supported to US, Canada, UK, Spain, and most European countries. Emergency numbers (911, 112, etc.) are blocked.

## Supported Languages

- English (`en`)
- Spanish (`es`)

Set `language` for app interface, `call_language` for the phone conversation.
