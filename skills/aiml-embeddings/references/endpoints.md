# AIMLAPI Embeddings API Reference

**Endpoint:** `POST https://api.aimlapi.com/v1/embeddings`

## Parameters

| Name | Type | Description |
| :--- | :--- | :--- |
| `model` | string | Model ID (e.g., `text-embedding-3-large`) |
| `input` | string/array | Input text to embed |
| `encoding_format` | string | `float` or `base64`. Default: `float` |
| `dimensions` | number | Optional. Number of dimensions in the output |

## Example Response (Partial)

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [
        0.02531846985220909,
        -0.04148460552096367,
        ...
      ]
    }
  ],
  "model": "text-embedding-3-large",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```
