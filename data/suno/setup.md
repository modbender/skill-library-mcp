# Setup — Suno

Read this when `~/suno/` doesn't exist or is empty.

## Your Attitude

You're helping someone create real music. Whether they want a quick jingle or a professional track, your job is to make it happen — from idea to audio file.

## Priority Order

### 1. First: Understand Their Setup

Determine which approach fits:
- **Just prompts?** — Help them craft prompts to paste into suno.com
- **Have API key?** — Use hosted APIs (aimusicapi.ai, EvoLink) for automation
- **Self-hosted?** — Use local API if they've set one up

Ask early:
- "Do you have an API key for Suno, or should I help you generate on the website?"
- "Want me to handle everything programmatically, or just help with prompts and lyrics?"

### 2. Then: Understand Their Music

Get clarity on what they want:
- "What kind of song? Genre, mood, purpose?"
- "Do you have lyrics, or should I write them?"
- "Vocals or instrumental?"

### 3. Finally: Generate

Based on their setup:

**Website users:** Craft optimized prompt/lyrics, they paste into suno.com

**API users:** Generate programmatically, deliver audio URL

**Browser automation:** Navigate suno.com for them if browser tool available

## What You're Saving

In `~/suno/memory.md`:
- Their preferred generation method
- Favorite genres and styles
- Vocal preferences
- Successful prompts that worked
- API configuration reference (not the keys themselves)

## API Configuration

If they have API access, guide them to store keys securely:

```bash
# For aimusicapi.ai
export AIMUSICAPI_KEY="their-key"

# For EvoLink
export EVOLINK_API_KEY="their-key"
```

Never store API keys in plain text files. Use environment variables or system keychain.

## When Done

Once you:
1. Know their preferred method (web, API, browser)
2. Understand their music style
3. Have delivered working audio

...you're set. Future requests will be faster with preferences saved.
