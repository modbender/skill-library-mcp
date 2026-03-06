---
name: clarity-fold-status
description: >
  Get overview and status information from Clarity Protocol.
  Use when the user asks about fold status, how many variants,
  research overview, what data is available, or Clarity Protocol status.
  Capabilities: API info, variant counts, endpoint availability.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Optional CLARITY_API_KEY env var for 100 req/min (vs 10 req/min).
metadata:
  author: clarity-protocol
  version: "1.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Fold Status Skill

Get overview and status information about Clarity Protocol's protein folding research database, including API capabilities, available endpoints, and data statistics.

## Quick Start

Get full status report:

```bash
python scripts/check_status.py
```

Get status in JSON format:

```bash
python scripts/check_status.py --format json
```

## Status Information

The status check provides:

- **API version**: Current API version
- **API description**: What the API provides
- **Total variants**: Count of protein variants in database
- **Available endpoints**: List of all API endpoints
- **Rate limits**: Anonymous and authenticated limits
- **Data freshness**: When data was last updated

## API Endpoints

The Clarity Protocol API v1 provides these endpoints:

- `GET /api/v1/`: API information
- `GET /api/v1/variants`: List all variants (with filters)
- `GET /api/v1/variants/{fold_id}`: Get variant details
- `GET /api/v1/variants/{fold_id}/findings`: Get agent findings
- `GET /api/v1/literature`: List research papers
- `GET /api/v1/literature/{pmid}`: Get paper details
- `GET /api/v1/clinical`: List clinical variants
- `GET /api/v1/clinical/{gene}/{variant}`: Get clinical variant details

## Rate Limits

- **Anonymous (no API key)**: 10 requests/minute
- **With API key**: 100 requests/minute

To use an API key, set the `CLARITY_API_KEY` environment variable:

```bash
export CLARITY_API_KEY=your_key_here
python scripts/check_status.py
```

Get your API key at https://clarityprotocol.io

## Error Handling

**429 Rate Limit**: You've exceeded the rate limit. The script will display how long to wait.

**500 Server Error**: The API server encountered an error. Try again later.

**Timeout**: The request took longer than 30 seconds.

## Use Cases

- Check if the API is available
- Get an overview of available data
- Verify endpoint URLs before making requests
- Monitor rate limit status
- Understand API capabilities for integration planning
