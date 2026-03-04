# API Reference — Udio

Udio has no official public API. Community wrappers interact with the internal API.

## Available Wrappers

| Wrapper | Language | Install | Repo |
|---------|----------|---------|------|
| udio_wrapper | Python | `pip install udio_wrapper` | github.com/flowese/UdioWrapper |
| udio-wrapper | TypeScript | `npm install udio-wrapper` | github.com/josephgodwinkimani/udio-wrapper |

## Getting the Auth Token

The wrappers require `sb-api-auth-token` from your browser session.

### Steps
1. Go to [udio.com](https://www.udio.com) and log in
2. Open DevTools:
   - **Chrome/Edge:** `Ctrl+Shift+I` (Windows) or `Cmd+Option+I` (Mac)
   - **Firefox:** `Ctrl+Shift+I` or `F12`
3. Navigate to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click **Cookies** > **https://www.udio.com**
5. Find `sb-api-auth-token`
6. Copy the **Value** (long string starting with `base64-...`)

### Token Handling
```python
# GOOD: Use environment variable
import os
auth_token = os.getenv('UDIO_AUTH_TOKEN')

# GOOD: Use keychain (macOS)
# security add-generic-password -a udio -s udio_auth_token -w "token-value"
# security find-generic-password -a udio -s udio_auth_token -w
```

**Never store tokens in plain text files or commit to git.**

### Token Expiration
Tokens expire after ~7 days of inactivity. If you get 401 errors:
1. Log into udio.com again
2. Re-extract the token from cookies
3. Update your environment variable

## Python Wrapper (udio_wrapper)

### Installation
```bash
pip install udio_wrapper
# or from source
pip install git+https://github.com/flowese/UdioWrapper.git
```

### Basic Usage
```python
from udio_wrapper import UdioWrapper

udio = UdioWrapper(auth_token)

# Create a song (~30 seconds)
result = udio.create_song(
    prompt="electronic ambient chill downtempo synth pads warm",
    seed=-1,  # -1 = random seed
    custom_lyrics=None  # Optional
)

print(f"Song ID: {result['id']}")
print(f"Audio URL: {result['song_path']}")
```

### Extend a Song
```python
# Extend the first clip to ~1 minute
extended = udio.extend(
    prompt="add subtle drums and bass, maintain atmosphere",
    seed=-1,
    audio_conditioning_path=result['song_path'],
    audio_conditioning_song_id=result['id'],
    custom_lyrics=None
)
```

### Add Outro
```python
# Add ending section
outro = udio.add_outro(
    prompt="gentle fade out, peaceful resolution",
    seed=-1,
    audio_conditioning_path=extended['song_path'],
    audio_conditioning_song_id=extended['id'],
    custom_lyrics="Final words fade away..."
)
```

### Complete Song Sequence
Generate intro + extensions + outro in one call:
```python
complete = udio.create_complete_song(
    short_prompt="acoustic guitar fingerpicking peaceful morning",
    extend_prompts=[
        "add soft piano accompaniment",
        "introduce gentle strings, building emotion"
    ],
    outro_prompt="peaceful resolution, fading into silence",
    num_extensions=2,
    custom_lyrics_short="The sun rises...",
    custom_lyrics_extend=[
        "A new day begins...",
        "Hope fills the air..."
    ],
    custom_lyrics_outro="And so it ends..."
)

# Returns list of all generated segments with URLs
for segment in complete:
    print(f"{segment['type']}: {segment['song_path']}")
```

### Parameters Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | str | Music description (genre, mood, instruments) |
| `seed` | int | Reproducibility seed. -1 = random |
| `custom_lyrics` | str | Optional lyrics to include |
| `audio_conditioning_path` | str | URL of song to extend |
| `audio_conditioning_song_id` | str | ID of song to extend |

## TypeScript/Node Wrapper (udio-wrapper)

### Installation
```bash
npm install udio-wrapper
```

### Node.js Usage
```typescript
import { createUdioWrapper } from 'udio-wrapper/node';

async function generateMusic() {
    const client = await createUdioWrapper(process.env.UDIO_AUTH_TOKEN);
    
    // Create song
    const song = await client.createSong({
        prompt: 'indie rock upbeat energetic electric guitar',
        seed: 12345,
        customLyrics: 'Optional lyrics here'
    });
    
    console.log('Song created:', song.id);
    
    // Wait for completion
    const completed = await client.waitForCompletion(song.id, {
        pollingInterval: 3000,  // Check every 3 seconds
        maxAttempts: 30,        // Max 30 attempts
        onProgress: (status) => {
            console.log(`Status: ${status.status}`);
        }
    });
    
    console.log('Download URL:', completed.url);
}
```

### Browser Usage
```typescript
import { createUdioWrapper } from 'udio-wrapper/browser';

const client = createUdioWrapper(authToken);
// Same API as Node.js
```

### Extend Song
```typescript
const extended = await client.extendSong({
    prompt: 'add drums and build energy',
    audioConditioningPath: song.url,
    audioConditioningSongId: song.id,
    customLyrics: 'The beat drops...'
});
```

### Complete Sequence
```typescript
const sequence = await client.createCompleteSequence({
    shortPrompt: 'peaceful piano melody',
    extendPrompts: [
        'add strings',
        'introduce soft percussion'
    ],
    outroPrompt: 'gentle fade to silence',
    numExtensions: 2,
    customLyricsShort: 'Opening...',
    customLyricsExtend: ['Middle...', 'Bridge...'],
    customLyricsOutro: 'The end...'
});
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Token expired or invalid | Re-extract from browser |
| 429 Rate Limited | Too many requests | Wait and retry |
| 500 Server Error | Udio service issue | Retry later |
| Timeout | Generation taking too long | Increase timeout, retry |

```python
from udio_wrapper import UdioWrapper
import time

def generate_with_retry(udio, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return udio.create_song(prompt=prompt)
        except Exception as e:
            if "401" in str(e):
                raise Exception("Token expired - re-extract from browser")
            if "429" in str(e):
                wait = 60 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## Response Structure

### Create Song Response
```json
{
    "id": "song_abc123",
    "status": "processing",
    "song_path": "https://...",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Completed Song
```json
{
    "id": "song_abc123",
    "status": "completed",
    "song_path": "https://cdn.udio.com/songs/abc123.mp3",
    "duration": 32.5,
    "seed": 12345
}
```

## Rate Limits

Udio has undocumented rate limits:
- Free tier: ~10 generations/day
- Paid tiers: Higher limits based on plan
- Respect rate limits to avoid account restrictions

## Disclaimer

These wrappers are community-maintained and not officially supported by Udio. The internal API may change without notice. Use at your own risk and respect Udio's terms of service.
