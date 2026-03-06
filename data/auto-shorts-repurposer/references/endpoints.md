# Endpoints

- Prefer local processing when possible.
- If a transcription API is used, follow the provider's official docs and keep requests minimal.
- Do not use unofficial upload or scraping endpoints.

## Generic request template

Use this as a conceptual template and adapt to the chosen provider.

```
POST /transcribe
{
  "media_url": "...",
  "language": "en",
  "timestamps": true,
  "speaker_labels": false
}
```
