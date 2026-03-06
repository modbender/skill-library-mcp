---
name: PopUp Organizer
description: Search and hire mobile vendors for events on PopUp. Find food trucks, DJs, photo booths & more, create event listings, send booking inquiries, and manage invoices.
metadata: {"openclaw":{"requires":{"env":["POPUP_API_KEY"]},"primaryEnv":"POPUP_API_KEY"}}
---

# PopUp Organizer

Search and hire mobile vendors — food trucks, DJs, photo booths, florists, live bands, and more — for any event. Create event listings, send booking inquiries, manage applications, track invoices, and save favorite vendors.

---

## Getting Started

1. Sign up or log in at <https://usepopup.com/login>
2. Switch to **Organizer** mode
3. Go to **Settings > API Keys**
4. Click **Create API Key** and copy the key (shown only once)

---

## Authentication

All requests require a Bearer token in the `Authorization` header:

```
Authorization: Bearer pk_live_...
```

The token is provided via the `POPUP_API_KEY` environment variable.

**Rate limit:** 60 requests per minute per API key. HTTP 429 is returned with `Retry-After: 60` if exceeded.

**Base URL:** `https://usepopup.com/api/v1/organizer`

---

## Endpoints

### Search Vendors

`GET /vendors`

Search published vendor profiles by name, type, location, event type, or price range.

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search query (name, type, city, description) |
| `type` | string | Vendor category — see categories below |
| `state` | string | 2-letter US state code (e.g. `CA`, `NY`) |
| `metro` | string | Metro area within state (requires `state`) |
| `event` | string | Event type filter — see event types below |
| `price` | string | Price range: `$`, `$$`, `$$$`, `$$$$` |
| `sort` | string | `newest`, `name_asc`, `name_desc`, `rating` |
| `page` | number | Page number (default 1) |
| `limit` | number | Results per page (default 20, max 100) |

Returns vendor profiles with `businessName`, `businessType`, `homeCity`, `homeState`, `priceRange`, `averageRating`, `eventTypes`, `slug`, and more.

---

### List Events

`GET /open-events`

List your events.

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter: `open`, `closed`, `canceled` |
| `page` | number | Page number |
| `limit` | number | Results per page |

Returns events with `title`, `eventDate`, `startTime`, `endTime`, `eventCity`, `eventState`, `vendorCap`, `expectedGuestCount`, `status`, `shareUrl`, `shortUrl`, and `qrCodeUrl`.

### Get Event Detail

`GET /open-events/{eventId}`

Returns the event object plus an `applications` array (each with `businessId`, `status`, `quotedRate`, `engagementModel`, and nested `business` info) and `eventTerms`.

### Create Event

`POST /open-events`

Create a new event listing.

**Required fields:** `title`, `description`, `eventType`, `eventDate` (YYYY-MM-DD), `startTime` (HH:mm), `endTime` (HH:mm), `eventPlaceName`, `eventAddress1`, `eventCity`, `eventState` (2-letter), `eventZip`, `vendorCap` (1-1000), `feePayer` (`organizer_pays` | `vendor_pays` | `none`), `expectedGuestCount` (1-100000), `vendorCategoriesWanted` (array, 1-20 items).

**Optional fields:** `location`, `eventLat`, `eventLng`, `heroImageUrl`, `organizerBudget`, `boothFee`, `salesPercent`, `hiredBudget`, `venueSetting`, `requiresVerification`, `invoiceDueDays`, `termIds`.

Events are pending admin approval before becoming publicly visible.

### Update Event

`PATCH /open-events/{eventId}`

Update event fields or perform actions.

**Actions:** `{ "action": "close" }` to close to new applications, `{ "action": "reopen" }` to reopen.

**Updatable fields:** all the same fields as create. When key details change (date, time, venue, title), accepted vendors are notified.

### Cancel Event

`DELETE /open-events/{eventId}`

Cancel an event. All pending and accepted vendors are notified.

---

### List Applications

`GET /open-events/{eventId}/applications`

List vendor applications for an event.

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter: `pending`, `accepted`, `declined`, `withdrawn` |
| `page` | number | Page number |
| `limit` | number | Results per page |

### Get Event QR Code

`GET /open-events/{eventId}/qr`

Returns a PNG QR code image for the event share link.

---

### List Inquiries

`GET /inquiries`

List your inquiries to vendors.

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter: `pending`, `quoted`, `booked`, `declined` |
| `page` | number | Page number |
| `limit` | number | Results per page |

Returns inquiries with `eventDate`, `eventType`, `guestCount`, `location`, `budget`, `message`, `status`, `quotedPrice`, `quoteMessage`, and nested `business` info.

### Get Inquiry Detail

`GET /inquiries/{id}`

Get a single inquiry with full detail.

### Create Inquiry

`POST /inquiries`

Send a booking inquiry to a vendor.

**Required:** `businessId` (UUID).

**Optional:** `bookingType` (`catering` | `vending`), `eventDate` (YYYY-MM-DD), `eventType`, `guestCount`, `location`, `eventPlaceName`, `eventAddress1`, `eventCity`, `eventState`, `eventZip`, `budget`, `message`, `phone`, `startTime` (HH:mm), `endTime` (HH:mm), `estimatedPrice`.

The vendor is notified by email and in-app notification.

### Update Inquiry

`PATCH /inquiries/{id}`

Update a pending inquiry or respond to a quote.

**Actions:** `{ "action": "accept_quote" }` (inquiry must be `quoted`), `{ "action": "decline" }` (inquiry must be `quoted`).

**Updatable fields (pending only):** `eventDate`, `eventType`, `guestCount`, `location`, `budget`, `message`, `startTime`, `endTime`.

### Delete Inquiry

`DELETE /inquiries/{id}`

Delete a pending inquiry. Only works on `status=pending`.

---

### List Invoices

`GET /invoices`

List invoices for event applications and direct inquiries.

| Param | Type | Description |
|-------|------|-------------|
| `page` | number | Page number |
| `limit` | number | Results per page |

Returns invoices with `eventTitle`, `eventDate`, `vendorName`, `engagementModel`, `amount` (dollars), `direction` (`receivable` | `payable`), `isPaid`.

---

### List Saved Vendors

`GET /saved`

List your bookmarked vendors.

### Save Vendor

`POST /saved`

Bookmark a vendor: `{ "businessId": "..." }`

### Remove Saved Vendor

`DELETE /saved?businessId=...`

Remove a bookmarked vendor.

---

### Get Profile

`GET /profile`

Get your organizer profile and account info.

### Update Profile

`PATCH /profile`

Update your organizer profile.

**Fields:** `companyName`, `companyType` (`brand` | `agency` | `planner` | `corporate`), `eventTypes` (array), `location`, `city`, `state`, `zip`, `phone`, `website`, `about`, `givesBack`, `nonProfit`, `forACause`, `rules`.

---

## Response Format

All endpoints return JSON with `{ "data": ... }` wrapper. List endpoints include `{ "pagination": { "page", "limit", "total", "totalPages" } }`.

Error responses: `{ "error": "message" }` with appropriate HTTP status (400, 401, 404, 429, 500).

---

## Vendor Categories

Use these values for the `type` parameter when searching vendors:

| Value | Label |
|-------|-------|
| `food_truck` | Food |
| `bakery` | Bakery / Desserts |
| `beverage` | Beverage / Coffee / Bar |
| `dj` | DJ / Entertainment |
| `photo_booth` | Photo Booth |
| `photography` | Photography |
| `live_band` | Live Music |
| `florist` | Florist / Event Florals |
| `balloons` | Balloons / Balloon Decor |
| `yoga` | Wellness |
| `arts_crafts` | Retail Vendor |
| `other` | Other |

## Event Types

Use these values for `eventType` fields:

`wedding`, `corporate`, `birthday`, `festival`, `market`, `popup`, `fundraiser`, `community`, `holiday`, `private`, `other`
