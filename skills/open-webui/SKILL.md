---
name: open-webui
description: Complete Open WebUI API integration for managing LLM models, chat completions, Ollama proxy operations, file uploads, knowledge bases (RAG), image generation, audio processing, and pipelines. Use this skill when interacting with Open WebUI instances via REST API - listing models, chatting with LLMs, uploading files for RAG, managing knowledge collections, or executing Ollama commands through the Open WebUI proxy. Requires OPENWEBUI_URL and OPENWEBUI_TOKEN environment variables or explicit parameters.
compatibility: Requires Python 3.8+ with requests library, or curl. Works with any Open WebUI instance (local or remote). Internet access required for external instances.
---

# Open WebUI API Skill

Complete API integration for Open WebUI - a unified interface for LLMs including Ollama, OpenAI, and other providers.

## When to Use

**Activate this skill when the user wants to:**
- List available models from their Open WebUI instance
- Send chat completions to models through Open WebUI
- Upload files for RAG (Retrieval Augmented Generation)
- Manage knowledge collections and add files to them
- Use Ollama proxy endpoints (generate, embed, pull models)
- Generate images or process audio through Open WebUI
- Check Ollama status or manage models (load, unload, delete)
- Create or manage pipelines

**Do NOT activate for:**
- Installing or configuring Open WebUI server itself (use system admin skills)
- General questions about what Open WebUI is (use general knowledge)
- Troubleshooting Open WebUI server issues (use troubleshooting guides)
- Local file operations unrelated to Open WebUI API

## Prerequisites

### Environment Variables (Recommended)

```bash
export OPENWEBUI_URL="http://localhost:3000"  # Your Open WebUI instance URL
export OPENWEBUI_TOKEN="your-api-key-here"    # From Settings > Account in Open WebUI
```

### Authentication

- Bearer Token authentication required
- Token obtained from Open WebUI: **Settings > Account**
- Alternative: JWT token for advanced use cases

## Activation Triggers

**Example requests that SHOULD activate this skill:**

1. "List all models available in my Open WebUI"
2. "Send a chat completion to llama3.2 via Open WebUI with prompt 'Explain quantum computing'"
3. "Upload /path/to/document.pdf to Open WebUI knowledge base"
4. "Create a new knowledge collection called 'Research Papers' in Open WebUI"
5. "Generate an embedding for 'Open WebUI is great' using the nomic-embed-text model"
6. "Pull the llama3.2 model through Open WebUI Ollama proxy"
7. "Get Ollama status from my Open WebUI instance"
8. "Chat with gpt-4 using my Open WebUI with RAG enabled on collection 'docs'"
9. "Generate an image using Open WebUI with prompt 'A futuristic city'"
10. "Delete the old-model from Open WebUI Ollama"

**Example requests that should NOT activate this skill:**

1. "How do I install Open WebUI?" (Installation/Admin)
2. "What is Open WebUI?" (General knowledge)
3. "Configure the Open WebUI environment variables" (Server config)
4. "Troubleshoot why Open WebUI won't start" (Server troubleshooting)
5. "Compare Open WebUI to other UIs" (General comparison)

## Workflow

### 1. Configuration Check

- Verify `OPENWEBUI_URL` and `OPENWEBUI_TOKEN` are set
- Validate URL format (http/https)
- Test connection with GET /api/models or /ollama/api/tags

### 2. Operation Execution

Use the CLI tool or direct API calls:

```bash
# Using the CLI tool (recommended)
python3 scripts/openwebui-cli.py --help
python3 scripts/openwebui-cli.py models list
python3 scripts/openwebui-cli.py chat --model llama3.2 --message "Hello"

# Using curl (alternative)
curl -H "Authorization: Bearer $OPENWEBUI_TOKEN" \
  "$OPENWEBUI_URL/api/models"
```

### 3. Response Handling

- HTTP 200: Success - parse and present JSON
- HTTP 401: Authentication failed - check token
- HTTP 404: Endpoint/model not found
- HTTP 422: Validation error - check request parameters

## Core API Endpoints

### Chat & Completions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/completions` | POST | OpenAI-compatible chat completions |
| `/api/models` | GET | List all available models |
| `/ollama/api/chat` | POST | Native Ollama chat completion |
| `/ollama/api/generate` | POST | Ollama text generation |

### Ollama Proxy

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ollama/api/tags` | GET | List Ollama models |
| `/ollama/api/pull` | POST | Pull/download a model |
| `/ollama/api/delete` | DELETE | Delete a model |
| `/ollama/api/embed` | POST | Generate embeddings |
| `/ollama/api/ps` | GET | List loaded models |

### RAG & Knowledge

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/files/` | POST | Upload file for RAG |
| `/api/v1/files/{id}/process/status` | GET | Check file processing status |
| `/api/v1/knowledge/` | GET/POST | List/create knowledge collections |
| `/api/v1/knowledge/{id}/file/add` | POST | Add file to knowledge base |

### Images & Audio

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/images/generations` | POST | Generate images |
| `/api/v1/audio/speech` | POST | Text-to-speech |
| `/api/v1/audio/transcriptions` | POST | Speech-to-text |

## Safety & Boundaries

### Confirmation Required

Always confirm before:
- **Deleting models** (`DELETE /ollama/api/delete`) - Irreversible
- **Pulling large models** - May take significant time/bandwidth
- **Deleting knowledge collections** - Data loss risk
- **Uploading sensitive files** - Privacy consideration

### Redaction & Security

- **Never log the full API token** - Redact to `sk-...XXXX` format
- **Sanitize file paths** - Verify files exist before upload
- **Validate URLs** - Ensure HTTPS for external instances
- **Handle errors gracefully** - Don't expose stack traces with tokens

### Workspace Safety

- File uploads default to workspace directory
- Confirm before accessing files outside workspace
- No sudo/root operations required (pure API client)

## Examples

### List Models

```bash
python3 scripts/openwebui-cli.py models list
```

### Chat Completion

```bash
python3 scripts/openwebui-cli.py chat \
  --model llama3.2 \
  --message "Explain the benefits of RAG" \
  --stream
```

### Upload File for RAG

```bash
python3 scripts/openwebui-cli.py files upload \
  --file /path/to/document.pdf \
  --process
```

### Add File to Knowledge Base

```bash
python3 scripts/openwebui-cli.py knowledge add-file \
  --collection-id "research-papers" \
  --file-id "doc-123-uuid"
```

### Generate Embeddings (Ollama)

```bash
python3 scripts/openwebui-cli.py ollama embed \
  --model nomic-embed-text \
  --input "Open WebUI is great for LLM management"
```

### Pull Model (Confirmation Required)

```bash
python3 scripts/openwebui-cli.py ollama pull \
  --model llama3.2:70b
# Agent must confirm: "This will download ~40GB. Proceed? [y/N]"
```

### Check Ollama Status

```bash
python3 scripts/openwebui-cli.py ollama status
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid or missing token | Verify OPENWEBUI_TOKEN |
| 404 Not Found | Model/endpoint doesn't exist | Check model name spelling |
| 422 Validation Error | Invalid parameters | Check request body format |
| 400 Bad Request | File still processing | Wait for processing completion |
| Connection refused | Wrong URL | Verify OPENWEBUI_URL |

## Edge Cases

### File Processing Race Condition

Files uploaded for RAG are processed asynchronously. Before adding to knowledge:
1. Upload file → get file_id
2. Poll `/api/v1/files/{id}/process/status` until `status: "completed"`
3. Then add to knowledge collection

### Large Model Downloads

Pulling models (e.g., 70B parameters) can take hours. Always:
- Confirm with user before starting
- Show progress if possible
- Allow cancellation

### Streaming Responses

Chat completions support streaming. Use `--stream` flag for real-time output or collect full response for non-streaming.

## CLI Tool Reference

The included CLI tool (`scripts/openwebui-cli.py`) provides:
- Automatic authentication from environment variables
- Structured JSON output with optional formatting
- Built-in help for all commands
- Error handling with user-friendly messages
- Progress indicators for long operations

Run `python3 scripts/openwebui-cli.py --help` for full usage.
