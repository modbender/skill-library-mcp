# API Integration — Suno

Suno has no official public API. These hosted services provide API access.

## Options

| Service | Website | Setup |
|---------|---------|-------|
| **AI Music API** | aimusicapi.ai | Sign up, get API key |
| **EvoLink** | evolink.ai | Sign up, get API key |

Both are pay-per-use services that handle Suno integration for you.

---

## AI Music API

### Setup
1. Sign up at [aimusicapi.ai](https://aimusicapi.ai)
2. Get API key from dashboard
3. Store securely as environment variable:
```bash
export AIMUSICAPI_KEY="your-key-here"
```

### Python Example

```python
import os
import requests
import time

API_KEY = os.environ.get("AIMUSICAPI_KEY")
BASE = "https://api.aimusicapi.ai/api/v1/sonic"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def poll_task(task_id, timeout=300):
    """Poll until task completes."""
    for _ in range(timeout // 5):
        r = requests.get(f"{BASE}/task/{task_id}", headers=HEADERS)
        data = r.json()
        if data["status"] == "completed":
            return data["songs"]
        if data["status"] == "failed":
            raise Exception(f"Generation failed: {data.get('error')}")
        time.sleep(5)
    raise TimeoutError("Generation timed out")

def generate(prompt, instrumental=False):
    """Generate a song from prompt."""
    r = requests.post(f"{BASE}/generate", 
        headers=HEADERS,
        json={
            "prompt": prompt,
            "make_instrumental": instrumental
        })
    r.raise_for_status()
    return poll_task(r.json()["task_id"])

def generate_custom(lyrics, style_tags, title):
    """Generate with custom lyrics."""
    r = requests.post(f"{BASE}/custom_generate",
        headers=HEADERS,
        json={
            "prompt": lyrics,
            "tags": style_tags,
            "title": title,
            "make_instrumental": False
        })
    r.raise_for_status()
    return poll_task(r.json()["task_id"])

def generate_lyrics(topic):
    """Generate lyrics from topic."""
    r = requests.post(f"{BASE}/lyrics",
        headers=HEADERS,
        json={"prompt": topic})
    r.raise_for_status()
    return r.json()["lyrics"]
```

### Usage

```python
# Simple generation
songs = generate("upbeat electronic dance track female vocals")
print(f"Audio: {songs[0]['audio_url']}")

# Custom with lyrics
songs = generate_custom(
    lyrics="""
[Verse]
Walking down the street tonight
Stars are shining ever bright

[Chorus]
This is my moment
This is my time
    """,
    style_tags="pop, upbeat, female vocals",
    title="My Moment"
)

# Generate lyrics first
lyrics = generate_lyrics("a summer love story")
songs = generate_custom(lyrics, "indie pop, dreamy", "Summer Love")
```

### cURL

```bash
# Generate
curl -X POST "https://api.aimusicapi.ai/api/v1/sonic/generate" \
  -H "Authorization: Bearer $AIMUSICAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "rock anthem guitar", "make_instrumental": false}'

# Check status
curl "https://api.aimusicapi.ai/api/v1/sonic/task/TASK_ID" \
  -H "Authorization: Bearer $AIMUSICAPI_KEY"
```

---

## EvoLink

### Setup
1. Sign up at [evolink.ai](https://evolink.ai)
2. Get API key from dashboard
3. Store as: `EVOLINK_API_KEY`

### Python Example

```python
import os
import requests
import time

API_KEY = os.environ.get("EVOLINK_API_KEY")
BASE = "https://api.evolink.ai/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def generate_evolink(prompt, model="suno-v4", duration=120):
    """Generate with EvoLink API."""
    r = requests.post(f"{BASE}/audios/generations",
        headers=HEADERS,
        json={
            "model": model,
            "prompt": prompt,
            "duration": duration
        })
    task_id = r.json()["task_id"]
    
    for _ in range(60):
        status = requests.get(f"{BASE}/tasks/{task_id}", 
            headers=HEADERS).json()
        if status["status"] == "completed":
            return status["result"]
        time.sleep(5)
    return None
```

### Models
- `suno-v4` — Default, balanced
- `suno-v4.5` — Better style control
- `suno-v5` — Studio-grade quality

---

## Error Handling

```python
def safe_generate(prompt, retries=3):
    """Generate with retry logic."""
    for attempt in range(retries):
        try:
            return generate(prompt)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API key")
            if e.response.status_code == 429:
                time.sleep(60)  # Rate limited
                continue
            raise
        except TimeoutError:
            if attempt < retries - 1:
                continue
            raise
    return None
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid key | Check API key |
| 429 Rate Limited | Too many requests | Wait 1-2 min |
| Timeout | Server busy | Retry later |

## Best Practices

1. **Store keys in env vars** — Never in code or plain files
2. **Handle rate limits** — Implement backoff
3. **Poll with delays** — 5 second intervals minimum
4. **Download quickly** — Audio URLs may expire
5. **Log successful prompts** — Reuse what works
