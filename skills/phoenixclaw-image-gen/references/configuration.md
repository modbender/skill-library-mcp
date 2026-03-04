# Configuration Specification

This document defines the environment variables, configuration defaults, and validation policy for the `image-generation` skill.

## 1. Configuration Precedence

The following order of precedence is applied when resolving configuration values:

1.  **CLI Arguments** (Highest priority)
2.  **Environment Variables**
3.  **Hardcoded Defaults** (Lowest priority)

## 2. Environment Variables

### Required
- `OPENROUTER_API_KEY`: The API key for OpenRouter. Without this, the skill will fail fast.

### Optional
- `IMAGE_GEN_TEXT_TO_IMAGE_MODEL`: The default text-to-image model.
    - Default value: `bytedance-seed/seedream-4.5`
- `IMAGE_GEN_IMAGE_TO_IMAGE_MODEL`: The default image-to-image model.
    - Default value: `google/gemini-2.5-flash-image`

## 3. Validation Policy

### Missing API Key
If `OPENROUTER_API_KEY` is not set, the skill must:
1.  Fail immediately (Fail Fast).
2.  Exit with a non-zero exit code.
3.  Provide a clear, actionable error message: `Missing OPENROUTER_API_KEY environment variable.`

### Missing Prompt
The `--prompt` CLI argument is mandatory. If missing:
1.  Fail immediately.
2.  Exit with a non-zero exit code.
3.  Provide a clear error message: `The --prompt argument is required.`

## 4. Default Model Mapping

| Source | Model ID |
| :--- | :--- |
| **Hardcoded Default (T2I)** | `bytedance-seed/seedream-4.5` |
| **Hardcoded Default (I2I)** | `google/gemini-2.5-flash-image` |
| **Provider** | OpenRouter |

---
*Note: Future providers will be documented in the [Extension Guide](./extension-guide.md).*
