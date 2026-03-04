# Superlore API Reference

This document describes the Superlore.ai API endpoints used by the OpenClaw Daily Podcast skill.

## Base URL

```
https://superlore-api.onrender.com
```

> **Note:** This is the official Superlore API, hosted on [Render](https://render.com). The `superlore.ai` website proxies to this backend. Both URLs point to the same service owned and operated by Superlore.

## Authentication

The Superlore API supports multiple authentication methods. **API key is the primary and recommended method for skill and server integrations.**

### API Key (Recommended)

**Required header:**

```
x-api-key: your-api-key-here
```

Get your API key at [superlore.ai](https://superlore.ai) → Account → API Keys, or use the OTP flow below to create one programmatically. **4 free hours of podcast generation included** with every API key.

### OTP Email Authentication (Wizard Flow)

The setup wizard uses a 3-step OTP flow to authenticate new users and create an API key without requiring them to visit the website. This is the **default path** in `setup-crons.js`.

#### Step 1 — Request a Code

```
POST /api/auth/otp-request
Content-Type: application/json

{ "email": "user@example.com" }
```

Sends a 6-digit verification code to the provided email address. The code expires after a short window (typically 10 minutes).

**Response (200 OK):**
```json
{ "message": "Code sent" }
```

**Error responses:**
- `400` — Missing or invalid email
- `429` — Too many requests; wait before retrying

#### Step 2 — Verify the Code

```
POST /api/auth/otp-verify
Content-Type: application/json

{ "email": "user@example.com", "code": "123456" }
```

Verifies the 6-digit code and returns a short-lived JWT.

**Response (200 OK):**
```json
{ "token": "<jwt>" }
```

**Error responses:**
- `400` — Missing fields
- `401` — Code expired or incorrect
- `429` — Too many verification attempts

#### Step 3 — Create an API Key

```
POST /api/auth/create-api-key
Authorization: Bearer <jwt>
Content-Type: application/json
```

Uses the JWT from Step 2 to create a new Superlore API key tied to the authenticated account.

**Response (200 OK):**
```json
{ "apiKey": "sk_live_..." }
```

**Error responses:**
- `401` — Missing, invalid, or expired JWT
- `500` — Key creation failed; retry

#### Full OTP Flow Example (Node.js)

```javascript
const https = require('https');
// ... (httpRequest helper omitted for brevity)

// 1. Request OTP
await httpRequest(`${API_BASE}/api/auth/otp-request`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
}, JSON.stringify({ email }));

// 2. Verify code entered by user
const { token: jwt } = (await httpRequest(`${API_BASE}/api/auth/otp-verify`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
}, JSON.stringify({ email, code }))).data;

// 3. Create API key
const { apiKey } = (await httpRequest(`${API_BASE}/api/auth/create-api-key`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${jwt}`,
  },
})).data;

// apiKey is now ready to use with x-api-key header
```

### Other Auth Methods

JWT and Device ID authentication also exist but are intended for the Superlore consumer web app. For OpenClaw skill integrations and server-side usage, always use an API key.

**Optional analytics header:**

For usage tracking and analytics, you can also include:

```
X-Device-ID: openclaw-daily-podcast-v1
```

This helps Superlore understand usage patterns and improve the service, but is not required for authentication.

## Create Episode

**Endpoint:** `POST /episodes`

Creates a new podcast episode. The API will:
1. Generate a script using AI based on your topic and style
2. Convert the script to speech using the specified TTS voice
3. Optionally perform web research to enrich the content
4. Return episode metadata with a unique slug/ID

### Request

```json
POST /episodes
Content-Type: application/json
x-api-key: your-api-key-here
X-Device-ID: openclaw-daily-podcast-v1

{
  "topic": "Your episode topic/prompt (can be very detailed)",
  "style": "documentary",
  "tone": "documentary", 
  "voice": "af_heart",
  "voiceProvider": "local",
  "voiceSpeed": 0.95,
  "ttsModel": "kokoro",
  "targetMinutes": 7,
  "language": "en",
  "visibility": "private",
  "webSearch": false,
  "altScript": false
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | **Yes** | The episode topic or detailed prompt. Can be very long (20KB+). This is where you include all your briefing data and instructions. |
| `style` | string | No | Preset style: `documentary`, `educational`, `conversational`, `storytelling`, `interview`, `news`, `comedy`. Default: `documentary` |
| `tone` | string | No | Tone override. Usually same as `style`. |
| `voice` | string | No | Voice ID. Options: `af_heart`, `af_sky`, `af_bella`, `am_adam`, `am_michael`, etc. Default: `af_heart` |
| `voiceProvider` | string | No | TTS provider: `local` (Kokoro), `elevenlabs`, `openai`. Default: `local` |
| `voiceSpeed` | number | No | Playback speed multiplier. Range: 0.8-1.2. Default: 1.0 |
| `ttsModel` | string | No | TTS model: `kokoro` (local), `elevenlabs`, `tts-1`, `tts-1-hd`. Default: `kokoro` |
| `targetMinutes` | number | No | Target episode length in minutes. Range: 1-30. Default: 5 |
| `language` | string | No | Language code: `en`, `es`, `fr`, `de`, etc. Default: `en` |
| `visibility` | string | No | `public` or `private`. Default: `public` |
| `webSearch` | boolean | No | Whether to perform web research to enrich content. Default: `false` |
| `altScript` | boolean | No | Use alternative script generation approach. Default: `false` |

### Voice Options

Recommended voices for daily briefings:

- **`af_heart`** (female) — Warm, professional, clear. Best all-around choice.
- **`af_sky`** (female) — Slightly younger, energetic. Good for upbeat styles.
- **`af_bella`** (female) — Warm mentor voice. Good for advisory styles.
- **`am_adam`** (male) — Professional, authoritative.
- **`am_michael`** (male) — Deep, documentary narrator.

Voice provider notes:
- **`local` (Kokoro TTS)**: Free, fast, high-quality. Recommended default.
- **`elevenlabs`**: Premium voices, requires API key on Superlore side.
- **`openai`**: OpenAI's TTS models, requires API key on Superlore side.

For OpenClaw podcast skill, stick with `local` provider and Kokoro voices.

### Response

**Success (202 Accepted):**

```json
{
  "episode": {
    "id": "abc123def456",
    "slug": "your-episode-title-slug",
    "title": "Your Episode Title",
    "status": "processing",
    "visibility": "private",
    "createdAt": "2026-02-15T22:30:00.000Z",
    "topic": "Your topic...",
    "style": "documentary",
    "voice": "af_heart",
    "targetMinutes": 7,
    "estimatedCompletionSec": 120
  }
}
```

The episode is created immediately but processing happens asynchronously. The `status` field will be:
- `processing` — Script generation and TTS in progress
- `ready` — Episode ready to listen
- `completed` — Episode ready to listen (legacy alias for `ready`)
- `failed` — Something went wrong

**Episode URL:**
```
https://superlore.ai/episode/{slug}
```

Visit this URL to listen to the episode once processing completes (usually 2-5 minutes depending on length).

### Error Responses

**400 Bad Request:**
```json
{
  "error": "Missing required field: topic"
}
```

**401 Unauthorized:**
```json
{
  "error": "Invalid or missing API key"
}
```

**402 Payment Required / Usage Limit Exceeded:**
```json
{
  "error": "Usage limit exceeded"
}
```

**429 Too Many Requests:**
```json
{
  "error": "Rate limit exceeded"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Failed to create episode",
  "details": "..."
}
```

## Poll Episode Status

**Endpoint:** `GET /episodes/:id`

Returns the episode object including its current `status` field. Use this to poll for episode completion after creation.

**Polling strategy:** Poll every 5 seconds until `status` is `"ready"` or `"failed"` (max 60 attempts = 5 minutes).

### Request

```
GET /episodes/abc123def456
x-api-key: your-api-key-here
```

### Response

```json
{
  "episode": {
    "id": "abc123def456",
    "slug": "your-episode-title-slug",
    "title": "Your Episode Title",
    "status": "ready",
    "visibility": "private",
    "createdAt": "2026-02-15T22:30:00.000Z",
    "audioUrl": "https://...",
    "durationSec": 342
  }
}
```

## Rate Limits

No official rate limits, but be respectful:
- Don't create more than 1 episode per minute
- Don't create more than 20-30 episodes per day
- The service is free — use it reasonably

## Tips

### Prompt Engineering

The `topic` field is where all your magic happens. Superlore's AI is good at following detailed instructions, so:

1. **Include all context** — paste your briefing data directly
2. **Be specific about structure** — "Start with... then cover... end with..."
3. **Specify tone and style** — even though there's a `style` param, reinforcing it in the prompt helps
4. **Use examples** — "Like a documentary narrator, NOT like a list"
5. **Set expectations** — "Aim for 5-7 minutes" or "Keep it under 3 minutes"

### Optimal Voice Settings

For daily briefings:
- **Morning**: `voiceSpeed: 1.0` (energizing pace)
- **Evening**: `voiceSpeed: 0.93-0.95` (thoughtful, relaxed pace)
- **Weekly reviews**: `voiceSpeed: 0.92` (slower, reflective)

### Episode Length

The `targetMinutes` parameter is a soft target — the AI will try to hit it but may go over/under depending on content. Typical ranges:

- **Daily briefings**: 5-7 minutes
- **Focus/Priorities**: 3-5 minutes
- **Weekly reviews**: 8-12 minutes

### Web Search

Set `webSearch: false` for daily briefings — you're providing all the context. Web search is useful for topic-based episodes ("Tell me about X") where external research adds value.

### Visibility

Use `visibility: "private"` for personal daily briefings. Private episodes:
- Don't appear in public listings
- Don't show up in search
- Are only accessible via direct URL
- May be periodically cleaned up (Superlore may delete old private episodes)

Public episodes are discoverable and permanent.

## Example: Create a Daily Briefing

```javascript
const https = require('https');

const topic = `
You are producing a professional daily briefing podcast.

Good evening, Adam. It is Saturday, February fifteenth, twenty twenty-six.

Today's highlights:
- Shipped the new podcast skill for OpenClaw
- Fixed critical security bug in auth system
- Published 3 blog posts (12,000 words total)

Key metrics:
- Traffic: 1,247 visits (up 12% from yesterday)
- New signups: 23
- DR 41 → DR 43 (backlink growth)

Looking ahead to tomorrow:
- Launch the ClawHub marketplace
- Deploy Redis caching layer
- Write weekly investor update

This is your Superlore daily briefing.
`;

const body = JSON.stringify({
  topic,
  style: 'documentary',
  voice: 'af_heart',
  voiceProvider: 'local',
  voiceSpeed: 0.95,
  ttsModel: 'kokoro',
  targetMinutes: 6,
  visibility: 'private',
  webSearch: false,
});

const options = {
  hostname: 'api.superlore.ai',
  path: '/episodes',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
    'x-api-key': process.env.SUPERLORE_API_KEY,
    'X-Device-ID': 'openclaw-daily-podcast-v1',
  },
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const response = JSON.parse(data);
    const episode = response.episode;
    console.log('Episode created!');
    console.log('URL:', `https://superlore.ai/episode/${episode.slug}`);
    console.log('Status:', episode.status);
    // Poll GET /episodes/:id every 5 seconds until status is "ready" or "failed"
  });
});

req.on('error', (e) => {
  console.error('Error:', e.message);
});

req.write(body);
req.end();
```

## Support

- **Superlore.ai**: [https://superlore.ai](https://superlore.ai)
- **Issues**: Report API issues or feature requests via the Superlore Discord or GitHub
- **Documentation**: This is community-maintained. Official docs may be added in the future.

---

**Note:** This API reference is based on the current implementation as of February 2026 and may change. The Superlore team is actively developing new features.
