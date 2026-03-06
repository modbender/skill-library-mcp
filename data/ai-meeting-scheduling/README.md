# Skipup - AI Meeting Scheduling

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.ai/skills/skipup-meeting-scheduler)
[![Version](https://img.shields.io/badge/version-1.1.0-green)](https://clawhub.ai/skills/skipup-meeting-scheduler)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API Docs](https://img.shields.io/badge/docs-API%20reference-informational)](https://support.skipup.ai/api/meeting-requests/)

**Booking links don't work when three people need to find a time. SkipUp does.** One API call coordinates 2-50 participants across timezones via email — no booking links, no calendar access, no polling. SkipUp emails every participant, collects availability, and books the meeting. Install and make your first request in under five minutes.

## Setup

### 1. Get a SkipUp API key

Sign up at [skipup.ai](https://skipup.ai) and generate an API key from your workspace settings. The key needs `meeting_requests.read`, `meeting_requests.write`, and `members.read` scopes.

### 2. Set the environment variable

```bash
export SKIPUP_API_KEY="sk_live_your_key_here"
```

### 3. Install the skill

```bash
clawhub install skipup-meeting-scheduler
```

## Example: schedule a meeting

User says to your agent: *"Set up a 30-minute call with alex@acme.com about the proposal"*

Your agent calls:

```json
POST https://api.skipup.ai/api/v1/meeting_requests

{
  "organizer_email": "sarah@yourcompany.com",
  "participant_emails": ["alex@acme.com"],
  "context": {
    "title": "Proposal discussion",
    "purpose": "Review the proposal",
    "duration_minutes": 30
  }
}
```

Response (202 Accepted):

```json
{
  "data": {
    "id": "mr_01HQ...",
    "status": "active",
    "participant_emails": ["alex@acme.com"]
  }
}
```

SkipUp emails Alex, collects availability, and books the meeting. No polling required -- check status anytime with `GET /api/v1/meeting_requests/:id`.

## Capabilities

- **Schedule meetings** with 2-50 participants across any timezone
- **Pause, resume, or cancel** coordination mid-flight
- **Check status** and list all requests with cursor-based pagination
- **Pre-validate organizers** against workspace membership

## How async email scheduling works

SkipUp coordinates via email, not instant-booking. Creating a request starts an asynchronous process -- participants receive emails, reply with availability, and get calendar invites once a time is confirmed. This typically takes hours, not seconds, and that's by design.

## Why SkipUp over booking link tools

Booking links solve a 1:1 problem: send a link, pick a slot, done. When you need five stakeholders in three timezones to agree on a time, that model has no mechanism. There is no shared view. No negotiation. No follow-up.

SkipUp coordinates the hard case. One API call triggers outreach to every participant via email -- the channel they already use. SkipUp collects availability windows, finds overlapping slots, sends reminders, and books a confirmed time. Your agent fires the request and moves on.

**Active, not passive.** SkipUp reaches out and follows up. Participants reply to email -- no links, no logins.

**2-50 participants.** Cross-timezone negotiation is the default, not an edge case.

**Pause and resume.** Swap a stakeholder mid-flight without losing context.

## API reference

| Action | Endpoint | Scope |
|---|---|---|
| Create meeting | `POST /api/v1/meeting_requests` | `meeting_requests.write` |
| Cancel meeting | `POST /api/v1/meeting_requests/:id/cancel` | `meeting_requests.write` |
| Pause meeting | `POST /api/v1/meeting_requests/:id/pause` | `meeting_requests.write` |
| Resume meeting | `POST /api/v1/meeting_requests/:id/resume` | `meeting_requests.write` |
| List meetings | `GET /api/v1/meeting_requests` | `meeting_requests.read` |
| Get meeting | `GET /api/v1/meeting_requests/:id` | `meeting_requests.read` |
| List members | `GET /api/v1/workspace_members` | `members.read` |

## Not supported

- Instant booking -- async only, no real-time calendar holds
- Calendar read/write -- no direct calendar access
- Free/busy lookup -- availability collected via email
- Recurring meetings -- single requests only
- Room/resource booking
- Meeting modification -- create a new request instead

## Documentation and support

- [OpenClaw integration guide](https://support.skipup.ai/integrations/openclaw/)
- [Meeting scheduling API reference](https://support.skipup.ai/api/meeting-requests/)
- [API authentication and scopes](https://support.skipup.ai/api/authentication/)
- [SkipUp llms.txt](https://skipup.ai/llms.txt)
- [About SkipUp](https://blog.skipup.ai/llm/index)

## License

MIT

[SkipUp scheduling platform](https://skipup.ai) | [SkipUp blog](https://blog.skipup.ai) | [Meeting scheduling API reference](https://support.skipup.ai/api/meeting-requests/)
