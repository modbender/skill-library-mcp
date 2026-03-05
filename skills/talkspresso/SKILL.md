---
name: talkspresso
description: Manage a Talkspresso business (services, appointments, products, clients, earnings, calendar) using the Talkspresso REST API. Use when the user wants to check bookings, create services, manage digital products, view earnings, update their profile, schedule sessions, or do anything related to their Talkspresso account. Requires TALKSPRESSO_API_KEY environment variable.
metadata:
  {
    "openclaw":
      {
        "emoji": "☕",
        "requires": { "env": ["TALKSPRESSO_API_KEY"] },
      },
  }
---

# Talkspresso

Manage a Talkspresso business via the REST API using `curl` and `jq`.

## Setup

The user needs a `TALKSPRESSO_API_KEY`. If missing:

1. Direct them to https://app.talkspresso.com/settings/api-keys to generate one
2. If they don't have a Talkspresso account, direct them to https://talkspresso.com/signup
3. Set it: `export TALKSPRESSO_API_KEY="tsp_..."`

If the user is new to Talkspresso, help them set up: profile, timezone, availability, first service.

## API Pattern

All calls follow this pattern:

```bash
# GET
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/ENDPOINT" | jq .data

# POST
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' \
  "https://api.talkspresso.com/ENDPOINT" | jq .data

# PUT
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' \
  "https://api.talkspresso.com/ENDPOINT" | jq .data

# DELETE
curl -s -X DELETE -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/ENDPOINT" | jq .data
```

Use `jq .data` on every response. The API wraps all responses in `{ "data": ... }`.

## Quick Reference

### Profile

```bash
# Get profile
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/profile/me" | jq .data

# Update profile
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"expert_title":"Executive Coach","about":"Short bio","bio":"Full bio","categories":["coaching"]}' \
  "https://api.talkspresso.com/profile" | jq .data
```

Key fields: `expert_title`, `about`, `bio`, `categories` (array), `handle` (URL slug), `profile_photo`.

### Services (Video Calls, Workshops)

```bash
# List services
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/service/me" | jq .data

# Create service
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Strategy Call",
    "short_description":"1-on-1 strategy session",
    "long_description":"",
    "price":100,
    "duration":30,
    "logistics":{"session_type":"single","capacity_type":"single","capacity":1}
  }' \
  "https://api.talkspresso.com/service" | jq .data

# Update service
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","price":150}' \
  "https://api.talkspresso.com/service/SERVICE_ID" | jq .data

# Delete service
curl -s -X DELETE -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/service/SERVICE_ID" | jq .data
```

Service types (via `logistics`):
- **1:1 call**: `{"capacity_type":"single","capacity":1}`
- **Group session**: `{"capacity_type":"group","capacity":10}`
- **Webinar**: `{"capacity_type":"group","capacity":50,"is_webinar":true}`

### Products (Digital Downloads)

```bash
# List products
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/product/me" | jq .data

# Create product
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Leadership Guide",
    "slug":"leadership-guide",
    "short_description":"Comprehensive guide for emerging leaders",
    "long_description":"Full description here...",
    "price":29,
    "product_type":"download",
    "status":"active"
  }' \
  "https://api.talkspresso.com/product" | jq .data

# AI-generate product details from description
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"description":"A guide about leadership for new managers","productType":"download"}' \
  "https://api.talkspresso.com/product/generate-details" | jq .data

# Update product
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"price":39,"status":"active"}' \
  "https://api.talkspresso.com/product/PRODUCT_ID" | jq .data

# Delete product
curl -s -X DELETE -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/product/PRODUCT_ID" | jq .data

# Product analytics
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/product/analytics" | jq .data

# List purchases
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/product/purchases" | jq .data
```

Product types: `download`, `video`, `bundle`. Status: `draft`, `active`, `archived`.

### Appointments & Scheduling

```bash
# List appointments (upcoming by default)
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/appointments/me?status=upcoming" | jq .data

# Get specific appointment
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/appointments/APT_ID" | jq .data

# Check available time slots
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-02-20","interval":30,"provider_id":"PROVIDER_ID"}' \
  "https://api.talkspresso.com/appointments/slots" | jq .data

# Create appointment (does NOT send email)
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name":"Jane Smith",
    "client_email":"jane@example.com",
    "service_id":"SERVICE_ID",
    "scheduled_date":"2026-02-20",
    "scheduled_time":"10:00",
    "is_complimentary":true,
    "skip_email":true
  }' \
  "https://api.talkspresso.com/appointments/invite" | jq .data

# Send the invitation email (after reviewing)
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://api.talkspresso.com/appointments/APT_ID/resend-invite" | jq .data

# Approve pending booking
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/appointments/APT_ID/approve" | jq .data

# Cancel appointment
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/appointments/APT_ID/cancel" | jq .data
```

**Important:** Always create appointments with `skip_email: true` first. Show the user the details. Only send the invitation email after they confirm.

### Clients

```bash
# List clients (optional search)
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/client/my?search=jane" | jq .data

# Get client details + booking history
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/client/CLIENT_ID/appointments" | jq .data

# Get session history (summaries, action items)
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/client/CLIENT_ID/session-history" | jq .data
```

### Earnings

```bash
# Get transactions
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/transaction/my?limit=50" | jq .data
```

### Calendar & Availability

```bash
# Get calendar settings (timezone, availability windows)
curl -s -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  "https://api.talkspresso.com/calendar/me" | jq .data

# Update timezone
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timezone":"America/New_York"}' \
  "https://api.talkspresso.com/calendar" | jq .data

# Update availability windows
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"availability":{"Monday":{"is_selected":true,"start_time":"09:00","end_time":"17:00"}}}' \
  "https://api.talkspresso.com/calendar" | jq .data
```

### File Uploads

```bash
# Upload image
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -F "file=@/path/to/image.jpg" \
  "https://api.talkspresso.com/file/upload/image" | jq .data

# Upload video
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -F "file=@/path/to/video.mp4" \
  "https://api.talkspresso.com/file/upload/video" | jq .data

# Upload file (PDF, doc, etc)
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -F "file=@/path/to/document.pdf" \
  "https://api.talkspresso.com/file/upload/file" | jq .data

# Set profile photo (upload, then update profile)
CDN_URL=$(curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -F "file=@/path/to/photo.jpg" \
  "https://api.talkspresso.com/file/upload/image" | jq -r .data)
curl -s -X PUT -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"profile_photo\":\"$CDN_URL\"}" \
  "https://api.talkspresso.com/profile" | jq .data

# Attach file to product
curl -s -X POST -H "Authorization: Bearer $TALKSPRESSO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_type":"pdf","file_name":"Guide.pdf","file_url":"CDN_URL","file_size":12345}' \
  "https://api.talkspresso.com/product/PRODUCT_ID/files" | jq .data
```

File types for products: `pdf`, `video`, `audio`, `image`, `zip`, `presentation`, `other`.

### Booking Link

The public booking page URL is: `https://talkspresso.com/HANDLE`

A specific service: `https://talkspresso.com/HANDLE/SERVICE_SLUG`

Get the handle from the profile (`handle` field).

## Workflows

### New User Setup

1. Get profile to see current state
2. Update profile: `expert_title`, `about`, `bio`
3. Set timezone in calendar
4. Set availability windows
5. Create first service (start with a free 15-min intro call)
6. Share booking link: `https://talkspresso.com/HANDLE`

### Create a Product from Scratch

1. Ask what the product is about
2. Use AI to generate details: `POST /product/generate-details`
3. Create the product with generated details
4. If the user has a file, upload it and attach to the product
5. Share the product link

### Schedule a Session

1. Search for the client: `GET /client/my?search=name`
2. List services to pick the right one
3. Check availability for the date
4. Create appointment with `skip_email: true`
5. Show details to user for confirmation
6. Only then send the invite email

### Revenue Check

1. Get transactions: `GET /transaction/my`
2. Calculate this month's total from payment transactions
3. Show upcoming appointments count
4. Show booking link for sharing

## Rules

- **Never send invites without confirmation.** Always create with `skip_email: true`, show the user, then send.
- **Stripe required for paid sessions.** If the user hasn't connected Stripe, they can only create free services and free products.
- **Get provider_id** from the profile (`id` field) when needed for availability checks.
- **Slugs** are auto-generated from titles if not provided. Lowercase, hyphens, no special chars.
- **Timezone** comes from calendar settings, not the user model. Always check `GET /calendar/me`.

## Additional Endpoints

For full API reference including notifications, testimonials, recordings, promo codes, file library, messaging, Google Calendar sync, and organization features, see [references/api.md](references/api.md).
