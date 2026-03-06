# Talkspresso API Reference

Base URL: `https://api.talkspresso.com`

All requests require: `Authorization: Bearer $TALKSPRESSO_API_KEY`

All responses wrap data in `{ "data": ... }`. Use `jq .data` to extract.

## Table of Contents

- [Profile](#profile)
- [Services](#services)
- [Products](#products)
- [Appointments](#appointments)
- [Clients](#clients)
- [Earnings](#earnings)
- [Calendar](#calendar)
- [File Uploads](#file-uploads)
- [Notifications](#notifications)
- [Testimonials](#testimonials)
- [Promo Codes](#promo-codes)
- [File Library](#file-library)
- [Messaging](#messaging)
- [Google Calendar](#google-calendar)
- [Subscription](#subscription)

## Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile/me` | Get your profile |
| PUT | `/profile` | Update profile fields |

Update fields: `expert_title`, `about`, `bio`, `categories` (array), `profile_photo` (URL), `handle`.

## Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/service/me` | List all services |
| GET | `/service/:id` | Get service details |
| POST | `/service` | Create service |
| PUT | `/service/:id` | Update service |
| DELETE | `/service/:id` | Delete service |
| POST | `/service/:id/duplicate` | Duplicate service |
| GET | `/service/:id/bookings` | Get service bookings |

Create body: `title`, `short_description`, `long_description`, `speaker_notes`, `price`, `duration`, `logistics` (object with `session_type`, `capacity_type`, `capacity`, optional `is_webinar`).

## Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product/me` | List all products |
| GET | `/product/:id` | Get product details |
| POST | `/product` | Create product |
| PUT | `/product/:id` | Update product |
| DELETE | `/product/:id` | Delete product |
| GET | `/product/analytics` | Product analytics |
| GET | `/product/purchases` | All purchases |
| GET | `/product/:id/purchases` | Purchases for product |
| POST | `/product/:id/files` | Attach file to product |
| POST | `/product/generate-details` | AI-generate product details |
| POST | `/product/analyze-file` | AI-analyze uploaded file |

Create body: `title`, `slug`, `short_description`, `long_description`, `price`, `product_type` (download/video/bundle), `status` (draft/active), `keywords` (array).

Attach file body: `file_type` (pdf/video/audio/image/zip/presentation/other), `file_name`, `file_url` (CDN URL from upload), `file_size` (bytes).

Generate details body: `description` (text), `productType` (download/video/bundle).

Analyze file body: `fileUrl` (CDN URL), `fileName`, `fileType` (MIME type), `productType`.

## Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/appointments/me` | List appointments. Params: `status` (upcoming/completed/all), `page`, `limit` |
| GET | `/appointments/:id` | Get appointment details |
| GET | `/appointments/pending` | Get pending bookings |
| POST | `/appointments/invite` | Create appointment |
| POST | `/appointments/:id/approve` | Approve pending booking |
| POST | `/appointments/:id/decline` | Decline booking. Body: `decline_reason` |
| POST | `/appointments/:id/resend-invite` | Send invitation email |
| POST | `/appointments/:id/cancel` | Cancel appointment |
| POST | `/appointments/:id/reschedule` | Reschedule. Body: `start_time`, `end_time` (ISO 8601) |
| POST | `/appointments/slots` | Check availability. Body: `date`, `interval`, `provider_id`, optional `service_id` |

Create body: `client_name`, `client_email`, `service_id`, `scheduled_date` (YYYY-MM-DD), `scheduled_time` (HH:mm 24h), `duration` (minutes), `is_complimentary` (bool), `invitation_message`, `skip_email` (bool), `custom_title`, `custom_price`.

## Clients

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/client/my` | List clients. Params: `search`, `page`, `limit` |
| GET | `/client/:id/appointments` | Client booking history |
| GET | `/client/:id/session-history` | Session summaries and action items |
| GET | `/client/:id/activity` | Client activity dashboard |

## Earnings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transaction/my` | Transaction history. Params: `transaction_type`, `page`, `limit` |

## Calendar

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calendar/me` | Get calendar settings |
| PUT | `/calendar` | Update calendar |

Update body: `timezone` (IANA string), `availability` (object keyed by day name), `booking_interval_days`, `buffer_minutes`.

Availability day format: `{"is_selected": true, "start_time": "09:00", "end_time": "17:00"}`

## File Uploads

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/file/upload/image` | Upload image (multipart, field: `file`) |
| POST | `/file/upload/video` | Upload video (multipart, field: `file`) |
| POST | `/file/upload/file` | Upload any file (multipart, field: `file`) |

Returns CDN URL as the data value.

## Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List notifications |
| PUT | `/notifications/:id/read` | Mark as read |
| PUT | `/notifications/read-all` | Mark all as read |
| GET | `/notifications/count` | Get unread count |

## Testimonials

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/testimonial/me` | List testimonials |
| POST | `/testimonial/request` | Request testimonial. Body: `client_id` or `email`, `name` |
| PUT | `/testimonial/:id` | Update testimonial (approve/reject) |

## Promo Codes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/promo-code/me` | List promo codes |
| POST | `/promo-code` | Create promo code. Body: `code`, `discount_type` (percentage/fixed), `discount_value`, `max_uses`, `expires_at` |
| PUT | `/promo-code/:id` | Update promo code |
| DELETE | `/promo-code/:id` | Delete promo code |

## File Library

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/file-library` | List library files |
| POST | `/file-library` | Add file to library. Body: `name`, `file_url`, `file_type`, `file_size` |
| DELETE | `/file-library/:id` | Delete from library |

## Messaging

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/messaging/conversations` | List conversations |
| GET | `/messaging/conversations/:id` | Get conversation messages |
| POST | `/messaging/conversations/:id/messages` | Send message. Body: `content` |
| POST | `/messaging/conversations` | Start conversation. Body: `participant_id`, `message` |

## Google Calendar

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/google-calendar/status` | Check Google Calendar connection |

## Subscription

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscription/status` | Check subscription status |
