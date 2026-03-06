# GIF providers for openclaw-whatsapp-gif

## Supported providers

### Tenor
- Endpoint: `https://tenor.googleapis.com/v2/search`
- Env var: `TENOR_API_KEY`
- Useful params: `q`, `limit`, `media_filter=minimal`, `contentfilter=low`, `searchfilter=sticker,-static`

### Giphy
- Endpoint: `https://api.giphy.com/v1/gifs/search`
- Env var: `GIPHY_API_KEY`
- Useful params: `q`, `limit`, `rating=g`, `lang=en`, `bundle=messaging_non_clips`

## Provider selection

Default strategy:
1. Try Tenor (clean messaging fit, good reaction inventory)
2. Fallback to Giphy

## Safety guidance

- Use safe rating/content filters by default.
- Reject results whose title/alt text suggests NSFW/hate/violence.
- Prefer short, lightweight assets for message delivery reliability.

## Output shape expected by skill

Each candidate should provide:
- `provider`
- `url` (preferred MP4/WebM or GIF URL)
- `preview`
- `title`
- `score` (higher is better)
