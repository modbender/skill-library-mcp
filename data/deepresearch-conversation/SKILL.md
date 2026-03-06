---
name: deepresearch-conversation
description: Deep ReSearch Conversation is provided by Baidu for multi-round streaming conversations with "Deep Research" agents. "In-depth research" is a long-process task involving multi-step reasoning and execution, which is different from the ordinary "question-and-answer". A dialogue that requires the user to repeatedly verify and correct it until a satisfactory answer is reached.
metadata: { "openclaw": { "emoji": "📌", "requires": { "bins": ["python3", "curl"], "env": ["BAIDU_API_KEY"] }, "primaryEnv": "BAIDU_API_KEY" } }
---

# Deep Research Conversation

This skill allows OpenClaw agents to conduct in-depth research discussions with users on a given topic. The API Key is automatically loaded from the OpenClaw config — no manual setup is needed.

## API Table
|    name    |               path              |            description                |
|------------|---------------------------------|---------------------------------------|
|DeepresearchConversation|/v2/agent/deepresearch/run|Multi-round streaming deep research conversation (via Python script)|
|ConversationCreate|/v2/agent/deepresearch/create|Create a new conversation session, returns conversation_id|
|FileUpload|/v2/agent/file/upload|Upload a file for the conversation|
|FileParseSubmit|/v2/agent/file/parse/submit|Submit an uploaded file for parsing|
|FileParseQuery|/v2/agent/file/parse/query|Query the status of a file parsing task|

## Workflow

### Path A: Topic discussion without files
1. Call **DeepresearchConversation** directly with the user's query. A new conversation is created automatically.

### Path B: Topic discussion with files
1. Call **ConversationCreate** to get a `conversation_id`.
2. Call **FileUpload** with the `conversation_id` to upload files.
3. Call **FileParseSubmit** with the returned `file_id`.
4. Poll **FileParseQuery** every few seconds until parsing succeeds.
5. Call **DeepresearchConversation** with the `query`, `conversation_id`, and `file_ids`.

### Multi-round conversation rules
- The DeepresearchConversation API is a **SSE streaming** interface that returns data incrementally.
- After the first call, you **must** pass `conversation_id` in all subsequent calls.
- If the response contains an `interrupt_id` (for "demand clarification" or "outline confirmation"), the next call **must** include that `interrupt_id`.
- If the response contains a `structured_outline`, present it to the user for confirmation/modification, then pass the final outline in the next call.
- Keep calling DeepresearchConversation iteratively until the user is satisfied with the result.

## APIS

### ConversationCreate API

#### Parameters
no parameters

#### Execute shell
```bash
curl -X POST "https://qianfan.baidubce.com/v2/agent/deepresearch/create" \
  -H "X-Appbuilder-From: openclaw" \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### FileUpload API

#### Parameters
- `agent_code`: Fixed value `"deepresearch"` (required)
- `conversation_id`: From ConversationCreate response (required)
- `file`: Local file binary (mutually exclusive with file_url). Max 10 files. Supported formats:
  - Text: .doc, .docx, .txt, .pdf, .ppt, .pptx (txt ≤ 10MB, pdf ≤ 100MB/3000 pages, doc/docx ≤ 100MB/2500 pages, ppt/pptx ≤ 400 pages)
  - Table: .xlsx, .xls (≤ 100MB, single Sheet only)
  - Image: .png, .jpg, .jpeg, .bmp (≤ 10MB each)
  - Audio: .wav, .pcm (≤ 10MB)
- `file_url`: Public URL of the file (mutually exclusive with file)

#### Local file upload
```bash
curl -X POST "https://qianfan.baidubce.com/v2/agent/file/upload" \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -H "X-Appbuilder-From: openclaw" \
  -F "agent_code=deepresearch" \
  -F "conversation_id=$conversation_id" \
  -F "file=@local_file_path"
```

#### File URL upload
```bash
curl -X POST "https://qianfan.baidubce.com/v2/agent/file/upload" \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -H "X-Appbuilder-From: openclaw" \
  -F "agent_code=deepresearch" \
  -F "conversation_id=$conversation_id" \
  -F "file_url=$file_url"
```

### FileParseSubmit API

#### Parameters
- `file_id`: From FileUpload response (required)

#### Execute shell
```bash
curl -X POST "https://qianfan.baidubce.com/v2/agent/file/parse/submit" \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Appbuilder-From: openclaw" \
  -d '{"file_id": "$file_id"}'
```

### FileParseQuery API

#### Parameters
- `task_id`: From FileParseSubmit response (required)

#### Execute shell
```bash
curl -X GET "https://qianfan.baidubce.com/v2/agent/file/parse/query?task_id=$task_id" \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "X-Appbuilder-From: openclaw"
```

### DeepresearchConversation API

#### Parameters
- `query`: The user's question or research topic (required)
- `conversation_id`: Optional on first call (auto-generated). Required on subsequent calls.
- `file_ids`: List of parsed file IDs (optional, only when discussing files)
- `interrupt_id`: Required when responding to "demand clarification" or "outline confirmation" from previous round. Found in `content.text.data` of the previous SSE response.
- `structured_outline`: The research report outline. Required on subsequent calls if the previous round generated one. Structure:
```json
{
    "title": "string",
    "locale": "string",
    "description": "string",
    "sub_chapters": [
        {
            "title": "string",
            "locale": "string",
            "description": "string",
            "sub_chapters": []
        }
    ]
}
```
- `version`: `"Lite"` (faster, within 10 min) or `"Standard"` (deeper, slower). Default: `"Standard"`.

#### Execute shell
```bash
python3 scripts/deepresearch_conversation.py '{"query": "your question here", "version": "Standard"}'
```

#### Example with all parameters
```bash
python3 scripts/deepresearch_conversation.py '{"query": "the question", "file_ids": ["file_id_1"], "interrupt_id": "interrupt_id", "conversation_id": "conversation_id", "structured_outline": {"title": "Report Title", "locale": "zh", "description": "desc", "sub_chapters": [{"title": "Chapter 1", "locale": "zh", "description": "chapter desc", "sub_chapters": []}]}, "version": "Standard"}'
```
