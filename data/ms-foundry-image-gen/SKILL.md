---
name: ms-foundry-image-gen
description: Azure Foundry image generation skill for OpenClaw; generates images via a Foundry deployment and returns image bytes or URLs.
homepage: https://github.com/jacqueskang/openclaw-skill-azure-image-gen
metadata: {"clawdbot":{"emoji":"🖼️","requires":{"bins":["curl","jq","base64"],"env":["FOUNDRY_API_KEY","FOUNDRY_ENDPOINT","FOUNDRY_DEPLOYMENT"]},"primaryEnv":"FOUNDRY_API_KEY"}}
---

# Azure Foundry Image Generation

AI image generation using an Azure Foundry (Cognitive Services / OpenAI) images deployment. Returns raw image bytes (PNG/JPEG) or a URL depending on the deployment response.

Overview
--------
- Requires network access to your Foundry endpoint and a valid API key.

Usage
-----
Set environment variables (example):

```bash
export FOUNDRY_ENDPOINT="https://aif-sbxe2e-ai-agent-02.cognitiveservices.azure.com/"
export FOUNDRY_API_KEY="<your_api_key>"
export FOUNDRY_DEPLOYMENT="FLUX-1.1-pro"
export FOUNDRY_API_VERSION="2025-04-01-preview"
```

Generate an image (safe example using `jq` to build JSON):

```bash
# Basic validation (reject obviously malformed endpoints)
if ! printf '%s' "${FOUNDRY_ENDPOINT:-}" | grep -Eq '^https?://[A-Za-z0-9._:-]+/?$'; then
  echo "FOUNDRY_ENDPOINT looks unsafe or is not set" >&2
  exit 1
fi

url="${FOUNDRY_ENDPOINT%/}/openai/deployments/${FOUNDRY_DEPLOYMENT}/images/generations?api-version=${FOUNDRY_API_VERSION:-2025-04-01-preview}"

PROMPT="a red fox"
jq -n --arg prompt "$PROMPT" '{prompt:$prompt, n:1, size:"1024x1024", output_format:"png"}' | \
  curl --fail --show-error --silent \
    --url "$url" \
    -H 'Content-Type: application/json' \
    -H "api-key: ${FOUNDRY_API_KEY}" \
    --data-binary @- -o /tmp/generation_result.json
  
# Stream base64 payload to avoid storing large values in shell variables
jq -r '.data[0].b64_json' /tmp/generation_result.json | base64 --decode > /tmp/generated_image.png
echo "Image saved to: /tmp/generated_image.png"
```

Options
-------
- `FOUNDRY_ENDPOINT` (required): Azure base URI for Foundry (include scheme, e.g. https://<name>.cognitiveservices.azure.com/)
- `FOUNDRY_API_KEY` (required): API key (primary credential)
- `FOUNDRY_DEPLOYMENT` (required): Deployment name to call
- `FOUNDRY_API_VERSION` (optional): API version (default: `2025-04-01-preview`)

Notes
-----
- The skill manifest (`src/manifest.json`) declares the required environment variables and marks `FOUNDRY_API_KEY` as the primary credential.
- This document provides a safe example using `jq --arg` and streaming to prevent shell interpolation and command-injection risks.

Troubleshooting
---------------
- If you see authentication errors, verify `FOUNDRY_API_KEY` permissions for the deployment.
- If `jq` or `base64` are missing, install them via your package manager (e.g., `apt install jq coreutils` on Debian/Ubuntu).

License / Attribution
---------------------
This skill is a minimal wrapper around the Foundry images generation REST endpoint for use in OpenClaw workflows.
