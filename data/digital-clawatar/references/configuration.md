# Configuration Reference

All configurable parameters for UNITH digital humans.

---

## Head Configuration Fields

These fields can be set at creation (`POST /head/create`) and updated later (`PUT /head/update`), except `headVisualId` which is immutable after creation.

### Identity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headVisualId` | string | Yes | Face visual ID. Immutable after creation. Get from `GET /headvisual/list`. |
| `name` | string | No | Internal slug identifier (lowercase, hyphens). Must be unique within the organization. |
| `alias` | string | Yes | Display name shown to end users. |

### Voice & Speech

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ttsVoice` | string | Yes | Voice name. Get from `GET /voice/list`. |
| `ttsProvider` | string | Yes | Voice provider: `elevenlabs`, `azure`, or `audiostack`. |
| `language` | string | No | UI language code (e.g., `en-US`, `es-ES`, `fr-FR`). |
| `languageSpeechRecognition` | string | No | Speech recognition language code. |

### Behavior

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operationMode` | string | Yes | Operating mode: `ttt`, `oc`, `doc_qa`, `voiceflow`, `plugin`. |
| `ocProvider` | string | No | Conversational AI provider (e.g., `playground`). |
| `greetings` | string | No | Initial message the avatar speaks on load. |
| `suggestions` | string | No | JSON-encoded array of suggested questions shown to users. Example: `"[\"What is X?\",\"How do I Y?\"]"` |

### Prompt Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `promptConfig.system_prompt` | string | No* | System prompt for `oc` and `doc_qa` modes. Defines personality and behavior. *Strongly recommended for `oc`/`doc_qa`. |

### Mode-Specific Fields

| Field | Type | Modes | Description |
|-------|------|-------|-------------|
| `voiceflowApiKey` | string | `voiceflow` | Voiceflow project API key. Required for voiceflow mode. |
| `pluginOperationalModeConfig.url` | string | `plugin` | Webhook URL for custom conversational engine. Required for plugin mode. |

---

## Environment Variables

These control the behavior of the skill scripts:

| Variable | Default | Description |
|----------|---------|-------------|
| `UNITH_EMAIL` | *(required)* | Account email for authentication. |
| `UNITH_SECRET_KEY` | *(required)* | Secret key for authentication. |
| `UNITH_MAX_RETRIES` | `3` | Max retry attempts on transient failures. |
| `UNITH_RETRY_DELAY` | `2` | Initial delay between retries (seconds). Doubles each retry (exponential backoff). |
| `UNITH_CURL_TIMEOUT` | `30` | Max time for API requests (seconds). Upload script uses 120. |
| `UNITH_CONNECT_TIMEOUT` | `10` | Connection timeout (seconds). Controls how long to wait for TCP connection. |
| `UNITH_TOKEN_CACHE` | `/tmp/.unith_token_cache` | Path for token cache file. Set to empty string to disable caching. |

---

## Voice Provider Comparison

| Provider | Latency | Quality | Languages | Best for |
|----------|---------|---------|-----------|----------|
| `audiostack` | Low | Good | Wide | Real-time conversation |
| `elevenlabs` | Medium | High | Wide | Natural-sounding voices |
| `azure` | Low | Good | Very wide | Multi-language support |

---

## Language Codes

Common language codes for `language` and `languageSpeechRecognition`:

| Code | Language |
|------|----------|
| `en-US` | English (US) |
| `en-GB` | English (UK) |
| `es-ES` | Spanish (Spain) |
| `es-MX` | Spanish (Mexico) |
| `fr-FR` | French (France) |
| `de-DE` | German |
| `it-IT` | Italian |
| `pt-BR` | Portuguese (Brazil) |
| `ja-JP` | Japanese |
| `ko-KR` | Korean |
| `zh-CN` | Chinese (Simplified) |

Use `bash scripts/list-resources.sh languages` for the full list supported by the API.
