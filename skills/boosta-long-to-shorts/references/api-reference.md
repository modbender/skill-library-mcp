# Boosta API Reference (Condensed)

## Base

- Base URL: `https://boosta.pro/api/v1`
- Auth header: `Authorization: Bearer <BOOSTA_API_KEY>`
- Content type for POST: `application/json`

## Endpoints

### `POST /jobs`

Submit a new processing job.

Request JSON:

```json
{
  "video_url": "https://youtube.com/watch?v=xxx",
  "video_type": "conversation",
  "config_name": "My Config"
}
```

Fields:
- `video_url` required
- `video_type` required
- `config_name` optional

Typical response:

```json
{
  "job_id": "job_1234567890_abc123",
  "status": "queued",
  "message": "Job submitted successfully"
}
```

### `GET /jobs/:job_id`

Return status for a specific job.

Processing response example:

```json
{
  "job_id": "job_1234567890_abc123",
  "status": "processing",
  "progress": 45,
  "step": "Creating clips..."
}
```

Completed response example:

```json
{
  "job_id": "job_1234567890_abc123",
  "status": "completed",
  "title": "Video Title",
  "clips_count": 7,
  "clip_urls": [
    "https://cdn.boosta.pro/.../clip_001.mp4",
    "https://cdn.boosta.pro/.../clip_002.mp4"
  ]
}
```

### `GET /jobs`

List completed jobs.

Example response:

```json
{
  "jobs": [
    {
      "job_id": "job_xxx",
      "title": "Video Title",
      "clips_count": 7
    }
  ],
  "count": 1
}
```

### `GET /usage`

Check credit balance and usage state.

## Operational Constraints

- One active job at a time per account/key.
- Poll job status; treat workflow as async.
- Use API key from environment variable `BOOSTA_API_KEY`.
