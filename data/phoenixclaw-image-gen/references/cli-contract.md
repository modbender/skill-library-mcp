# CLI Contract: Image Generation Skill

This document defines the Command Line Interface (CLI) contract and exit-code policy for the image generation skill.

## CLI Flags

All flags follow the `--flag value` or `--flag=value` pattern.

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--prompt` | Yes | N/A | The text description of the image to generate. |
| `--model` | No | `bytedance-seed/seedream-4.5` | Text-to-Image Model ID. |
| `--i2i-model`| No | `google/gemini-2.5-flash-image` | Image-to-Image Model ID. |
| `--input-image`| No | N/A | Path to input image for image-to-image. |
| `--size` | No | `1K` | Resolution tier (`1K`, `2K`, or `4K`). Not pixel dimensions.
| `--aspect` | No | `1:1` | The aspect ratio for the generated image. |
| `--output` | No | `.sisyphus/generated/image_<timestamp>.png` | Local path to save the generated image. |

|------|----------|---------|-------------|
| `--prompt` | Yes | N/A | The text description of the image to generate. |
| `--model` | No | `bytedance-seed/seedream-4.5` | The OpenRouter model ID to use. |
| `--size` | No | `1K` | Resolution tier (`1K`, `2K`, or `4K`). Not pixel dimensions.
| `--aspect` | No | `1:1` | The aspect ratio for the generated image. |
| `--output` | No | `.sisyphus/generated/image_<timestamp>.png` | Local path to save the generated image. |

### Configuration Precedence
1. **CLI Arguments**: Highest priority, overrides everything else.
2. **Environment Variables**: e.g., `IMAGE_GEN_TEXT_TO_IMAGE_MODEL`, `IMAGE_GEN_IMAGE_TO_IMAGE_MODEL`, `OPENROUTER_API_KEY`.

3. **Hard Defaults**: Built-in defaults as listed above.

---

## Exit Codes

The CLI will exit with one of the following codes to facilitate programmatic usage by OpenClaw or other orchestrators.

| Code | Label | Description |
|------|-------|-------------|
| `0` | `SUCCESS` | Image generated and saved successfully. |
| `1` | `CONFIG_ERROR` | Missing required parameters, invalid flag values, or authentication/API key issues. |
| `2` | `API_ERROR` | Failure during API communication with OpenRouter (e.g., rate limits, server errors). |
| `3` | `FS_ERROR` | Errors related to the local filesystem (e.g., unwritable output path, disk full). |

---

## JSON Error Payload Schema

When a non-zero exit code is returned, the CLI will output a JSON error payload to `stderr` (or `stdout` depending on implementation, typically following the project's `response-helper.js` pattern).

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human readable error message explaining the failure.",
  "details": {},
  "statusCode": 400,
  "timestamp": "2026-02-25T12:00:00.000Z"
}
```

### Fields:
- `success`: Always `false` for errors.
- `error`: A stable, uppercase string code (e.g., `MISSING_PARAMETERS`, `AUTH_FAILED`, `API_TIMEOUT`).
- `message`: A descriptive message for humans.
- `details`: (Optional) Object containing additional context (e.g., which parameter was missing).
- `statusCode`: HTTP-like status code for classification.
- `timestamp`: ISO 8601 timestamp of the error.

---

## Validation Rules

1. **Prompt**: Must be a non-empty string.
2. **Model**: Must be a valid OpenRouter model string.
3. **Size/Aspect**: Should follow `WxH` or `W:H` formats; implementation may restrict to supported values.
4. **Output**: Parent directory must exist or be creatable; file must be writable.
