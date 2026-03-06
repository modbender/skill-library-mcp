# ReelWords Caption API (minimal reference)

Base URL:
- `https://api.reelwords.ai`

Auth:
- Required header: `x-api-key: rw_...`

## Create a caption job

- `POST /api/v1/caption-jobs`
- Body (application/json):
  - `videoUrl` (string, uri, required)
  - `preferences` (object, required)
    - `addEmojis` (bool, optional)
    - `maxWordsPerLine` (int, optional)
    - `style` (object)
      - `styleId` (string, required)
      - optional: `positionY`, `fontSize`, `mainColor`, `highlightColor`, `hookColor`, `highlightOpacity`, `highlightCornerRadius`, `highlightMode`, `highlightScale`, `fontFamily`, `styleClasses`

Example curl (from docs):

```bash
curl https://api.reelwords.ai/api/v1/caption-jobs \
  --request POST \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: YOUR_SECRET_TOKEN' \
  --data '{
    "videoUrl": "https://cdn.reelwords.ai/sample.mp4",
    "preferences": {
      "addEmojis": true,
      "maxWordsPerLine": 6,
      "style": {
        "styleId": "style1",
        "positionY": 82,
        "fontSize": 54,
        "highlightColor": "#FFD803",
        "hookColor": "#FF5CAA"
      }
    }
  }'
```

Responses:
- 201 created
- 400 validation error
- 401 API key required or invalid
- 402 usage limit reached
- 404 style not found

## Get job status

- `GET /api/v1/caption-jobs/{id}`

## Download rendered video

- `GET /api/v1/caption-jobs/{id}/video`
- Redirects (302) to a signed storage URL once the job completes.
- Possible errors: 409 job not ready, 401 invalid key, 404 job not found.

Example curl:

```bash
curl https://api.reelwords.ai/api/v1/caption-jobs/123e4567-e89b-12d3-a456-426614174000 \
  --header 'x-api-key: YOUR_SECRET_TOKEN'
```

Responses:
- 200 status payload (includes `status`, optional failure info, and `result.downloadUrl` when complete)
- 400 invalid job id
- 401 API key required or invalid
- 404 job not found

Example curl (download endpoint):

```bash
curl -i https://api.reelwords.ai/api/v1/caption-jobs/123e4567-e89b-12d3-a456-426614174000/video \
  --header 'x-api-key: YOUR_SECRET_TOKEN'
```

Responses:
- 302 redirect to signed video URL
- 409 job not ready
