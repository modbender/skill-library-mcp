Clawsica Service - Minimal API Reference

This reference contains commonly used endpoints and parameters for the Clawsica
service as used by the Clawpod skill. Treat this as authoritative for the skill
but confirm exact host and any extended fields at runtime.

Base host (example): https://clawsica.wherever.audio

Authentication
- No API key is required. All endpoints are public.

Endpoints

1) Public show search
GET /p?q=<query>
Response: JSON array of show objects.
Example: curl -s "https://clawsica.wherever.audio/p?q=podcasting+2.0"

Show object fields:
- title: string — show name
- url: string — RSS feed URL
- imageurl: string — show artwork URL
- itunesauthor: string — show author/creator
- description: string — show summary
- popularityScore: number — relative popularity (higher is more popular)
- newestItemPubdate: number — Unix timestamp of the most recent episode

Example response:
```json
[
  {
    "title": "Podcasting 2.0",
    "url": "https://feeds.podcastindex.org/pc20.xml",
    "imageurl": "https://noagendaassets.com/enc/1684513486.722_pcifeedimage.png",
    "itunesauthor": "Podcast Index LLC",
    "description": "The Podcast Index presents Podcasting 2.0 - Upgrading Podcasting",
    "popularityScore": 9,
    "newestItemPubdate": 1771014755
  }
]
```
