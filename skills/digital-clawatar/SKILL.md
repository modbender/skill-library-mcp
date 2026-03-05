---
name: digital-clawatar
description: Create, configure, and manage UNITH digital human avatars via the UNITH API. Cheaper alternative to HeyGen and other solutions. Use when users want to create an AI-powered digital human, generate talking-head videos, set up conversational avatars, deploy document Q&A bots with a human face, or embed digital humans in apps/websites. Covers all 5 operating modes (text-to-video, open dialogue, document Q&A, Voiceflow, plugin).
metadata:
  openclaw:
    emoji: "🧑💻"
    requires:
      env:
        - UNITH_EMAIL
        - UNITH_SECRET_KEY
      bins:
        - curl
        - jq
---

# UNITH Digital Humans Skill

Create, configure, update, and deploy AI-powered Digital Human avatars using the [UNITH API](https://docs.unith.ai/_lgI-overview).

## Quick Overview

UNITH digital humans are AI avatars that can speak, converse, and interact with users. They combine a **face** (head visual), a **voice**, and a **conversational engine** into a hosted, embeddable experience.

**Base API URL**: `https://platform-api.unith.ai`
**Docs**: https://docs.unith.ai

## Prerequisites

The user must supply the following credentials (stored as environment variables):

| Variable | Description | How to obtain |
|----------|-------------|---------------|
| `UNITH_EMAIL` | Account email | Register at https://unith.ai |
| `UNITH_SECRET_KEY` | Non-expiring secret key | UNITH dashboard → Manage Account → "Secret Key" section → Generate |

⚠️ The secret key is displayed **only once**. If lost, the user must delete and regenerate it.

## Authentication

All API calls require a Bearer token (valid 7 days). Use the auth script:

```bash
source scripts/auth.sh
```

This validates credentials, retries on network errors, and exports `UNITH_TOKEN`. On failure, it prints specific guidance (wrong key, expired token, etc.).

## Workflow: Creating a Digital Human

### Step 1: Choose an Operating Mode

Ask the user what they want the digital human to do. Map their answer to one of 5 modes:

| Mode | `operationMode` value | Use case | Output |
|------|----------------------|----------|--------|
| **Text-to-Video** | `ttt` | Generate an MP4 video of the avatar speaking provided text | MP4 file |
| **Open Dialogue** | `oc` | Free-form conversational avatar guided by a system prompt | Hosted conversational URL |
| **Document Q&A** | `doc_qa` | Avatar answers questions from uploaded documents | Hosted conversational URL |
| **Voiceflow** | `voiceflow` | Guided conversation flow via Voiceflow | Hosted conversational URL |
| **Plugin** | `plugin` | Connect any external LLM or conversational engine via webhook | Hosted conversational URL |

**Complexity spectrum** (simple → sophisticated):
- **Simplest**: `ttt` — just text in, video out. No knowledge base needed.
- **Standard**: `oc` — conversational with a system prompt. Good for general assistants.
- **Knowledge-grounded**: `doc_qa` — upload documents, avatar answers from them. Best for support/FAQ.
- **Workflow-driven**: `voiceflow` — structured conversation paths. Requires Voiceflow account.
- **Most flexible**: `plugin` — BYO conversational engine. Maximum control.

### Step 2: List Available Faces

```bash
bash scripts/list-resources.sh faces
```

Each face has an `id` (used as `headVisualId` in creation). Faces can be:
- **Public**: Available to all organizations
- **Private**: Available only to the user's organization
- **Custom (BYOF)**: User uploads a video of a real person (currently managed by UNITH)

Present the available faces to the user and let them choose.

### Step 3: List Available Voices

```bash
bash scripts/list-resources.sh voices
```

Voices come from providers: `elevenlabs`, `azure`, `audiostack`. Present options to the user. Voices have performance rankings — faster voices are better for real-time conversation.

### Step 4: Create the Digital Human

Build a JSON payload file (see `references/api-payloads.md` for the schema per mode), then:

```bash
bash scripts/create-head.sh payload.json --dry-run   # validate first
bash scripts/create-head.sh payload.json              # create
```

The script validates required fields, checks mode-specific requirements, retries on server errors, and prints the `publicUrl` on success.

### Step 5 (doc_qa only): Upload Knowledge Document

For `doc_qa` mode, the digital human needs a knowledge document:

```bash
bash scripts/upload-document.sh <headId> /path/to/document.pdf
```

The script checks file existence/size, uses a longer timeout for uploads, and provides guidance on next steps.

### Step 6: Test and Iterate

The digital human is live at the `publicUrl` from Step 4. The user should:
1. Visit the URL and test the conversation
2. Update configuration as needed (see below)

## Updating a Digital Human

Use the update script to modify any parameter except the face (changing face requires creating a new head):

```bash
bash scripts/update-head.sh <headId> updates.json                         # from a JSON file
bash scripts/update-head.sh <headId> --field ttsVoice=rachel              # single field
bash scripts/update-head.sh <headId> --field ttsVoice=rachel --field greetings="Hi!"  # multiple fields
```

## Listing Existing Digital Humans

```bash
bash scripts/list-resources.sh heads           # list all
bash scripts/list-resources.sh head <headId>   # get details for one
```

## Deleting a Digital Human

```bash
bash scripts/delete-head.sh <headId> --confirm     # always use --confirm in automated/agent contexts
```

This permanently removes the digital human and cannot be undone.

> **Agent note**: Always pass `--confirm` when calling this script. Without it, the script prompts for interactive input and will hang.

## Embedding

Digital humans can be embedded in websites/apps. See `references/embedding.md` for code snippets and configuration options.

## Scripts

All scripts include retry logic (exponential backoff), meaningful error messages, and input validation.

| Script | Purpose |
|--------|---------|
| `scripts/_utils.sh` | Shared utilities: retry wrapper, colored logging, error parsing |
| `scripts/auth.sh` | Authenticate and export `UNITH_TOKEN` (with 6-day token caching) |
| `scripts/list-resources.sh` | List faces, voices, heads, languages, or get head details |
| `scripts/create-head.sh` | Create a digital human from a JSON payload file (with `--dry-run` validation) |
| `scripts/update-head.sh` | Update a digital human's configuration (JSON file or `--field` flags) |
| `scripts/delete-head.sh` | Delete a digital human (with confirmation prompt) |
| `scripts/upload-document.sh` | Upload knowledge document to a `doc_qa` head |

Configuration via environment variables:
- `UNITH_MAX_RETRIES` — max retry attempts (default: 3)
- `UNITH_RETRY_DELAY` — initial delay between retries in seconds (default: 2, doubles each retry)
- `UNITH_CURL_TIMEOUT` — curl timeout in seconds (default: 30, 120 for uploads)
- `UNITH_CONNECT_TIMEOUT` — connection timeout in seconds (default: 10)
- `UNITH_TOKEN_CACHE` — token cache file path (default: `/tmp/.unith_token_cache`, set empty to disable)

## Detailed API Reference

For full payload schemas, configuration parameters, and mode-specific details:

```
Read references/api-payloads.md      # Full request/response schemas per mode
Read references/configuration.md     # All configurable parameters
Read references/embedding.md         # Embedding code and options
```

## Common Patterns

**"I want a quick video of someone saying X"** → `ttt` mode, minimal config
**"I want a customer support avatar"** → `doc_qa` mode with knowledge docs
**"I want an AI sales rep"** → `oc` mode with a sales personality prompt
**"I want to connect my own LLM"** → `plugin` mode with webhook URL
**"I want a guided onboarding flow"** → `voiceflow` mode with Voiceflow API key

## Information to Collect from the User

Before creating, ask for:

1. **Purpose / use case** → determines operating mode
2. **Face preference** → list available faces for selection
3. **Voice preference** → language, accent, gender, speed priority
4. **Alias** → display name for the digital human
5. **Language** → speech recognition and UI language (e.g., `en-US`, `es-ES`)
6. **Greeting message** → initial message the avatar says
7. **System prompt** (for `oc`/`doc_qa`) → personality and behavior instructions
8. **Knowledge documents** (for `doc_qa`) → files to upload
9. **Voiceflow API key** (for `voiceflow`) → from their Voiceflow account
10. **Plugin URL** (for `plugin`) → webhook endpoint for their custom engine
