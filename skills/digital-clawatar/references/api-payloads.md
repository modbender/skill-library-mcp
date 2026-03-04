# API Payloads Reference

Full request/response schemas for each operating mode of the UNITH Digital Humans API.

**Base URL**: `https://platform-api.unith.ai`

---

## Common Required Fields (all modes)

| Field | Type | Description |
|-------|------|-------------|
| `headVisualId` | string | Face ID from `GET /headvisual/list` |
| `alias` | string | Display name shown to end users |
| `operationMode` | string | One of: `ttt`, `oc`, `doc_qa`, `voiceflow`, `plugin` |
| `ttsVoice` | string | Voice name from `GET /voice/list` |
| `ttsProvider` | string | One of: `elevenlabs`, `azure`, `audiostack` |

## Common Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Internal slug identifier (lowercase, hyphens) |
| `language` | string | UI language code (e.g., `en-US`, `es-ES`) |
| `languageSpeechRecognition` | string | Speech recognition language (e.g., `en-US`) |
| `greetings` | string | Initial message the avatar speaks on load |
| `ocProvider` | string | Conversational AI provider (e.g., `playground`) |

---

## Text-to-Video (`ttt`)

Generates an MP4 video of the avatar speaking provided text.

### Request — `POST /head/create`

```json
{
  "headVisualId": "<face_id>",
  "alias": "Video Presenter",
  "operationMode": "ttt",
  "ttsVoice": "coco",
  "ttsProvider": "audiostack",
  "language": "en-US",
  "languageSpeechRecognition": "en-US",
  "greetings": "Hello and welcome!"
}
```

### Response

```json
{
  "id": "<head_id>",
  "alias": "Video Presenter",
  "operationMode": "ttt",
  "publicUrl": "https://app.unith.ai/s/<publicId>",
  "publicId": "<publicId>"
}
```

---

## Open Dialogue (`oc`)

Free-form conversational avatar guided by a system prompt.

### Request — `POST /head/create`

```json
{
  "headVisualId": "<face_id>",
  "alias": "Sales Assistant",
  "operationMode": "oc",
  "ttsVoice": "rachel",
  "ttsProvider": "elevenlabs",
  "ocProvider": "playground",
  "language": "en-US",
  "languageSpeechRecognition": "en-US",
  "greetings": "Hi there! How can I help you today?",
  "promptConfig": {
    "system_prompt": "You are a friendly sales assistant for Acme Corp. Be helpful, concise, and professional."
  }
}
```

### Response

Same structure as `ttt` response.

### Notes

- `promptConfig.system_prompt` is strongly recommended. Without it the avatar uses a generic default.
- `ocProvider` controls the conversational AI backend.

---

## Document Q&A (`doc_qa`)

Avatar answers questions from uploaded documents.

### Request — `POST /head/create`

```json
{
  "headVisualId": "<face_id>",
  "alias": "FAQ Bot",
  "operationMode": "doc_qa",
  "ttsVoice": "jenny",
  "ttsProvider": "azure",
  "ocProvider": "playground",
  "language": "en-US",
  "languageSpeechRecognition": "en-US",
  "greetings": "Ask me anything about our documentation!",
  "promptConfig": {
    "system_prompt": "Answer user questions based only on the uploaded documents. If the answer is not in the documents, say so."
  }
}
```

### Response

Same structure as `ttt` response.

### Post-creation step

After creating the head, upload one or more knowledge documents:

```bash
bash scripts/upload-document.sh <headId> /path/to/document.pdf
```

Or via the API directly:

```
POST /document/upload
Content-Type: multipart/form-data

Fields:
  file    - The document file (PDF, etc.)
  headId  - The digital human ID
```

---

## Voiceflow (`voiceflow`)

Guided conversation flow via Voiceflow.

### Request — `POST /head/create`

```json
{
  "headVisualId": "<face_id>",
  "alias": "Onboarding Guide",
  "operationMode": "voiceflow",
  "ttsVoice": "rachel",
  "ttsProvider": "elevenlabs",
  "language": "en-US",
  "languageSpeechRecognition": "en-US",
  "greetings": "Welcome! Let me guide you through setup.",
  "voiceflowApiKey": "VF.DM.xxxx.yyyy"
}
```

### Response

Same structure as `ttt` response.

### Notes

- Requires a Voiceflow account and API key.
- The `voiceflowApiKey` is obtained from your Voiceflow project settings.

---

## Plugin (`plugin`)

Connect any external LLM or conversational engine via webhook.

### Request — `POST /head/create`

```json
{
  "headVisualId": "<face_id>",
  "alias": "Custom Agent",
  "operationMode": "plugin",
  "ttsVoice": "coco",
  "ttsProvider": "audiostack",
  "language": "en-US",
  "languageSpeechRecognition": "en-US",
  "greetings": "Hello!",
  "pluginOperationalModeConfig": {
    "url": "https://your-server.com/chat"
  }
}
```

### Response

Same structure as `ttt` response.

### Notes

- `pluginOperationalModeConfig.url` must be a publicly accessible HTTPS endpoint.
- UNITH sends conversation messages to your endpoint and expects text responses.

---

## Update a Digital Human — `PUT /head/update`

Modify any parameter except the face (`headVisualId`). Changing face requires creating a new head.

```json
{
  "id": "<head_id>",
  "ttsVoice": "new_voice_name",
  "greetings": "Updated greeting!"
}
```

Only include the fields you want to change plus the `id`.

---

## Delete a Digital Human — `DELETE /head/<headId>`

Permanently removes a digital human.

```
DELETE /head/<headId>
Authorization: Bearer <token>
```

Returns `200` on success.
