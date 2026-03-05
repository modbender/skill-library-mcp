---
name: elevenlabs
description: |
  ElevenLabs API integration with managed authentication. AI-powered text-to-speech, voice cloning, sound effects, and audio processing.
  Use this skill when users want to generate speech from text, clone voices, create sound effects, or process audio.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# ElevenLabs

Access the ElevenLabs API with managed authentication. Generate lifelike speech from text, clone voices, create sound effects, and process audio.

## Quick Start

```bash
# List available voices
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/elevenlabs/v1/voices')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/elevenlabs/{native-api-path}
```

Replace `{native-api-path}` with the actual ElevenLabs API endpoint path. The gateway proxies requests to `api.elevenlabs.io` and automatically injects your API key.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your ElevenLabs connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=elevenlabs&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'elevenlabs'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "ff2079b1-f40a-43b7-a807-1d5deea29c5b",
    "status": "ACTIVE",
    "creation_time": "2026-02-12T00:50:40.292363Z",
    "last_updated_time": "2026-02-12T00:51:14.547893Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "elevenlabs",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple ElevenLabs connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/elevenlabs/v1/voices')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'ff2079b1-f40a-43b7-a807-1d5deea29c5b')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Text-to-Speech

#### Convert Text to Speech

```bash
POST /elevenlabs/v1/text-to-speech/{voice_id}
Content-Type: application/json

{
  "text": "Hello, this is a test of the ElevenLabs API.",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  }
}
```

Returns audio data (mp3 by default).

Query parameters:
- `output_format` - Audio format (e.g., `mp3_44100_128`, `pcm_16000`, `pcm_22050`)

#### Stream Text to Speech

```bash
POST /elevenlabs/v1/text-to-speech/{voice_id}/stream
Content-Type: application/json

{
  "text": "Hello, this is streamed audio.",
  "model_id": "eleven_multilingual_v2"
}
```

Returns streaming audio data.

#### Text to Speech with Timestamps

```bash
POST /elevenlabs/v1/text-to-speech/{voice_id}/with-timestamps
Content-Type: application/json

{
  "text": "Hello world",
  "model_id": "eleven_multilingual_v2"
}
```

Returns audio with word-level timestamps.

### Voices

#### List Voices

```bash
GET /elevenlabs/v1/voices
```

Returns all available voices including premade and cloned voices.

#### Get Voice

```bash
GET /elevenlabs/v1/voices/{voice_id}
```

Returns metadata about a specific voice.

#### Get Default Voice Settings

```bash
GET /elevenlabs/v1/voices/settings/default
```

#### Get Voice Settings

```bash
GET /elevenlabs/v1/voices/{voice_id}/settings
```

#### Create Voice Clone

```bash
POST /elevenlabs/v1/voices/add
Content-Type: multipart/form-data

name: My Cloned Voice
files: [audio_sample.mp3]
description: A custom voice clone
remove_background_noise: false
```

#### Edit Voice

```bash
PATCH /elevenlabs/v1/voices/{voice_id}/edit
Content-Type: multipart/form-data

name: Updated Voice Name
description: Updated description
```

#### Delete Voice

```bash
DELETE /elevenlabs/v1/voices/{voice_id}
```

### Models

#### List Models

```bash
GET /elevenlabs/v1/models
```

Returns available models:
- `eleven_multilingual_v2` - Latest multilingual model
- `eleven_turbo_v2_5` - Low-latency model
- `eleven_monolingual_v1` - Legacy English model (deprecated)

### User

#### Get User Info

```bash
GET /elevenlabs/v1/user
```

#### Get Subscription Info

```bash
GET /elevenlabs/v1/user/subscription
```

Returns subscription details including character limits and usage.

### History

#### List History Items

```bash
GET /elevenlabs/v1/history?page_size=100
```

Query parameters:
- `page_size` - Number of items per page (default: 100, max: 1000)
- `start_after_history_item_id` - Cursor for pagination
- `voice_id` - Filter by voice

#### Get History Item

```bash
GET /elevenlabs/v1/history/{history_item_id}
```

#### Get Audio from History

```bash
GET /elevenlabs/v1/history/{history_item_id}/audio
```

Returns the audio file for a history item.

#### Delete History Item

```bash
DELETE /elevenlabs/v1/history/{history_item_id}
```

#### Download History Items

```bash
POST /elevenlabs/v1/history/download
Content-Type: application/json

{
  "history_item_ids": ["id1", "id2", "id3"]
}
```

Returns a zip file with the requested audio files.

### Sound Effects

#### Generate Sound Effect

```bash
POST /elevenlabs/v1/sound-generation
Content-Type: application/json

{
  "text": "A thunderstorm with heavy rain and distant thunder",
  "duration_seconds": 10.0
}
```

Query parameters:
- `output_format` - Audio format (e.g., `mp3_44100_128`)

### Audio Isolation

#### Remove Background Noise

```bash
POST /elevenlabs/v1/audio-isolation
Content-Type: multipart/form-data

audio: [audio_file.mp3]
```

Returns cleaned audio with background noise removed.

#### Stream Audio Isolation

```bash
POST /elevenlabs/v1/audio-isolation/stream
Content-Type: multipart/form-data

audio: [audio_file.mp3]
```

### Speech-to-Text

#### Transcribe Audio

```bash
POST /elevenlabs/v1/speech-to-text
Content-Type: multipart/form-data

audio: [audio_file.mp3]
model_id: scribe_v1
```

Returns transcription with optional word-level timestamps.

### Speech-to-Speech (Voice Changer)

#### Convert Voice

```bash
POST /elevenlabs/v1/speech-to-speech/{voice_id}
Content-Type: multipart/form-data

audio: [source_audio.mp3]
model_id: eleven_multilingual_sts_v2
```

Transforms audio to use a different voice while preserving intonation.

### Projects

#### List Projects

```bash
GET /elevenlabs/v1/projects
```

#### Get Project

```bash
GET /elevenlabs/v1/projects/{project_id}
```

#### Create Project

```bash
POST /elevenlabs/v1/projects
Content-Type: application/json

{
  "name": "My Audiobook Project",
  "default_title_voice_id": "voice_id",
  "default_paragraph_voice_id": "voice_id"
}
```

### Pronunciation Dictionaries

#### List Pronunciation Dictionaries

```bash
GET /elevenlabs/v1/pronunciation-dictionaries
```

#### Create Pronunciation Dictionary

```bash
POST /elevenlabs/v1/pronunciation-dictionaries/add-from-file
Content-Type: multipart/form-data

name: My Dictionary
file: [lexicon.pls]
```

## Response Headers

ElevenLabs API responses include useful headers:
- `x-character-count` - Characters used in the request
- `request-id` - Unique request identifier

## Pagination

History and other list endpoints use cursor-based pagination:

```bash
GET /elevenlabs/v1/history?page_size=100&start_after_history_item_id=last_item_id
```

## Code Examples

### JavaScript - Text to Speech

```javascript
const response = await fetch(
  'https://gateway.maton.ai/elevenlabs/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: 'Hello world!',
      model_id: 'eleven_multilingual_v2'
    })
  }
);
const audioBuffer = await response.arrayBuffer();
```

### Python - Text to Speech

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/elevenlabs/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={
        'text': 'Hello world!',
        'model_id': 'eleven_multilingual_v2'
    }
)
audio_data = response.content
with open('output.mp3', 'wb') as f:
    f.write(audio_data)
```

### Python - List Voices

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/elevenlabs/v1/voices',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
voices = response.json()
for voice in voices['voices']:
    print(f"{voice['name']}: {voice['voice_id']}")
```

## Notes

- Text-to-Speech is billed per character
- Sound Effects are billed per generation
- Speech-to-Text is billed per audio minute
- Audio output format can be specified as `codec_sample_rate_bitrate` (e.g., `mp3_44100_128`)
- Models available: `eleven_multilingual_v2` (recommended), `eleven_turbo_v2_5` (low latency)
- Voice IDs can be found using the List Voices endpoint
- Maximum text length varies by model
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq`, environment variables may not expand correctly. Use Python examples instead.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing ElevenLabs connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions or quota exceeded |
| 422 | Invalid parameters |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from ElevenLabs API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `elevenlabs`. For example:

- Correct: `https://gateway.maton.ai/elevenlabs/v1/voices`
- Incorrect: `https://gateway.maton.ai/v1/voices`

## Resources

- [ElevenLabs API Documentation](https://elevenlabs.io/docs/api-reference)
- [ElevenLabs Developer Portal](https://elevenlabs.io/developers)
- [ElevenLabs Models Overview](https://elevenlabs.io/docs/overview/models)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
