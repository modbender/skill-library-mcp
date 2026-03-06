# I'm Pretty Amazing API Reference

## Base URL
`https://api.imprettyamazing.com`

## General
All endpoints use JSON (`Content-Type: application/json`) except `POST /profile/avatar` and `POST /profile/cover` (multipart form data).

Success responses vary by endpoint (single object, list + pagination, or empty body/status for some deletes).

## Authentication
Session-cookie requirements:

- No-login endpoints: `POST /auth/register`, `POST /auth/login`, `POST /auth/forgot-password`, `POST /auth/reset-password`, `POST /auth/verify-email`
- Cookie-auth endpoints: `POST /auth/resend-verification`, `GET /auth/me`, and all non-auth resource endpoints

For cookie-auth endpoints, login first and send cookies on subsequent requests (for example with curl `-c` on login, `-b` on later calls).

Cookies may include JWT-based token values (for example `access_token`), but auth is passed via cookies.

Client guidance: you may persist cookie token values (`access_token`, optionally `refresh_token`) and reuse them until access-token expiry, then re-login.

Canonical expiry tracking: derive `Access Token Expires At (UTC)` from the `access_token` JWT `exp` claim and refresh auth when expired.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | `{"email": "...", "password": "..."}`. Sets `access_token` and `refresh_token` cookies. |
| POST | `/auth/register` | `{"email": "...", "password": "...", "username": "..."}`. Username: letters, numbers, hyphens, 3-30 chars. |
| GET | `/auth/me` | Get current user info |
| POST | `/auth/forgot-password` | `{"email": "..."}`. Sends reset email if account exists. |
| POST | `/auth/reset-password` | `{"token": "...", "password": "..."}`. Token from reset email link. |
| POST | `/auth/verify-email` | `{"token": "..."}`. Token from verification email link. |
| POST | `/auth/resend-verification` | Resend verification email for current user |

## Wins

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/wins` | Create a win (`content`, `type`, `visibility`) |
| GET | `/wins/my-wins` | List current user's wins |
| GET | `/wins/:id` | Get a specific win |
| PATCH | `/wins/:id` | Update a win (JSON body, any subset of fields) |
| DELETE | `/wins/:id` | Delete a win |

### Win Types
`PERSONAL`, `PROFESSIONAL`, `HEALTH`, `SOCIAL`, `CREATIVE`, `LEARNING`

### Visibility
`PUBLIC`, `PRIVATE`

### Win Object Fields
`id`, `userId`, `content`, `type`, `visibility`, `status`, `imageUrl`, `tags`, `starFormat`, `sourceApp`, `sourceAppId`, `summary`, `createdAt`, `updatedAt`, `likeCount`, `commentCount`, `isLiked`

### STAR Format (optional)

Wins can include a `starFormat` object for structured accomplishment tracking (Situation, Task, Action, Result).

**Create:** Include `starFormat` in `POST /wins` body. All four fields (`situation`, `task`, `action`, `result`) are **required** when `starFormat` is provided.

**Update:** Include `starFormat` in `PATCH /wins/:id` body. Can add STAR format to an existing win or update an existing one.

**STAR Format Object Fields:**
`id`, `winId`, `situation` (string, required), `task` (string, required), `action` (string, required), `result` (string, required), `createdAt`, `updatedAt`

Example payload:
```json
{
  "content": "Shipped the feature",
  "type": "PROFESSIONAL",
  "visibility": "PUBLIC",
  "starFormat": {
    "situation": "Legacy system couldn't handle load",
    "task": "Re-architect the data pipeline",
    "action": "Redesigned with event-driven processing",
    "result": "100x throughput improvement"
  }
}
```

## Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wins/:id/comments` | List comments on a win |
| POST | `/wins/:id/comments` | Add a comment (`{"content": "..."}`) |
| DELETE | `/wins/comments/:commentId` | Delete a comment |

## Likes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/wins/:id/like` | Like a win |
| DELETE | `/wins/:id/like` | Unlike a win |

## Social / Follows

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/follows/:userId` | Follow a user |
| DELETE | `/follows/:userId` | Unfollow a user |
| GET | `/follows/check/:userId` | Check if following a user |
| GET | `/follows/following` | List users you follow |
| GET | `/follows/followers` | List your followers |
| DELETE | `/follows/followers/:userId` | Remove a follower |
| GET | `/follows/stats` | Follow/follower counts |

## Blocks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/blocks` | List blocked users |
| POST | `/blocks/:userId` | Block a user |
| DELETE | `/blocks/:userId` | Unblock a user |

## Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/u/:username` | Get user profile |
| GET | `/u/:username/stats` | Get user stats |
| PATCH | `/profile` | Update profile. Fields: `username`, `bio` (max 500 chars), `location`, `website` |
| POST | `/profile/avatar` | Upload avatar (multipart, field name: `avatar`) |
| POST | `/profile/cover` | Upload cover image (multipart, field name: `cover`, keep under ~1MB) |

## Feed

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/feed` | Main feed |
| GET | `/feed/discover` | Discover feed |

## Pagination

List endpoints support pagination via query params:

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number |
| `limit` | 20 | Items per page |
| `quality` | `all` | Filter (feed endpoints) |

Response includes a `pagination` object: `{ total, page, limit, totalPages }`

Example: `GET /follows/following?page=1&limit=20`

## Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feedback` | Submit feedback (JSON, see below) |

Feedback payload:
```json
{"category": "BUG|FEATURE_REQUEST|GENERAL", "message": "...", "pageUrl": "...", "pageContext": "..."}
```
Message max 1000 characters.

## Known Limits

- Bio: max 500 characters
- Feedback message: max 1000 characters
- Cover image: keep file small (under ~1MB, 413 on large uploads)
- Password: UI requires a symbol, but API does not enforce this (known bug)
