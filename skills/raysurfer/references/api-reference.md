# Raysurfer API Reference

Base URL: `https://api.raysurfer.com`

All endpoints require authentication via Bearer token in the `Authorization` header. The token is read from the `RAYSURFER_API_KEY` environment variable.

Common headers for all requests:
```
Authorization: Bearer $RAYSURFER_API_KEY
Content-Type: application/json
```

---

## POST /api/retrieve/search

Search the cache for code matching a task description.

### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `task` | string | yes | - | Natural language description of the coding task |
| `top_k` | int | no | 5 | Maximum number of results to return |
| `min_verdict_score` | float | no | 0.3 | Minimum combined score threshold (0.0 to 1.0) |

### Example Request

```bash
curl -s -X POST https://api.raysurfer.com/api/retrieve/search \
  -H "Authorization: Bearer $RAYSURFER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Read a CSV file and plot a histogram with matplotlib",
    "top_k": 5,
    "min_verdict_score": 0.3
  }'
```

### Response Body

```json
{
  "matches": [
    {
      "code_block": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "csv-histogram-matplotlib",
        "source": "import pandas as pd\nimport matplotlib.pyplot as plt\n...",
        "language": "python"
      },
      "combined_score": 0.87,
      "thumbs_up": 14,
      "thumbs_down": 2
    }
  ],
  "total_found": 1
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `matches` | array | List of matching cached code blocks |
| `matches[].code_block.id` | string | Unique identifier for the code block (used for voting) |
| `matches[].code_block.name` | string | Human-readable name |
| `matches[].code_block.source` | string | The cached source code |
| `matches[].code_block.language` | string | Programming language |
| `matches[].combined_score` | float | Relevance score from 0.0 to 1.0 |
| `matches[].thumbs_up` | int | Number of positive votes |
| `matches[].thumbs_down` | int | Number of negative votes |
| `total_found` | int | Total number of matches found |

---

## POST /api/store/execution-result

Upload code that was successfully generated and executed.

### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `task` | string | yes | - | Natural language description of what the code does |
| `file_written` | object | yes | - | File to cache |
| `file_written.path` | string | yes | - | Relative file path |
| `file_written.content` | string | yes | - | Full file content |
| `succeeded` | bool | yes | - | Whether the code executed successfully |
| `use_raysurfer_ai_voting` | bool | no | true | Enable AI-powered voting on the uploaded code |

### Example Request

```bash
curl -s -X POST https://api.raysurfer.com/api/store/execution-result \
  -H "Authorization: Bearer $RAYSURFER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Read a CSV file and plot a histogram with matplotlib",
    "file_written": {
      "path": "plot_histogram.py",
      "content": "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndf = pd.read_csv(\"data.csv\")\ndf[\"value\"].hist(bins=20)\nplt.savefig(\"histogram.png\")\n"
    },
    "succeeded": true
  }'
```

### Response Body

```json
{
  "success": true,
  "code_blocks_stored": 1,
  "message": "Storage queued for 1 code file",
  "status_url": "/api/store/status/ert_xxx"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the upload was accepted |
| `code_blocks_stored` | int | Number of code blocks stored |
| `message` | string | Human-readable status message |
| `status_url` | string | URL to poll for background task status |

---

## POST /api/store/cache-usage

Vote on a cached code block after using it.

### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `code_block_id` | string | yes | - | ID of the code block being voted on |
| `code_block_name` | string | yes | - | Name of the code block being voted on |
| `code_block_description` | string | yes | - | Description of the code block being voted on |
| `succeeded` | bool | yes | - | `true` for upvote (code worked), `false` for downvote (code failed) |
| `task` | string | yes | - | Description of the task the code was used for |

### Example Request

```bash
curl -s -X POST https://api.raysurfer.com/api/store/cache-usage \
  -H "Authorization: Bearer $RAYSURFER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code_block_id": "550e8400-e29b-41d4-a716-446655440000",
    "code_block_name": "csv-histogram-matplotlib",
    "code_block_description": "Reads a CSV and plots a histogram",
    "succeeded": true,
    "task": "Read a CSV file and plot a histogram with matplotlib"
  }'
```

### Response Body

```json
{
  "success": true,
  "vote_pending": true,
  "message": "Cache usage recorded, voting queued"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the vote was recorded |
| `vote_pending` | bool | Whether the vote is pending AI review |
| `message` | string | Human-readable status message |

---

## Error Responses

All endpoints return standard HTTP error codes:

| Status | Meaning |
|--------|---------|
| 401 | Missing or invalid `RAYSURFER_API_KEY` |
| 422 | Invalid request body (check required fields) |
| 500 | Server error (retry or skip cache operations) |

Error response body:
```json
{
  "detail": "Human-readable error message"
}
```
