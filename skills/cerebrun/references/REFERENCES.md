# Cerebrun MCP API Reference

Complete reference for all available tools in the Cerebrun MCP server.

## Context Management

### get_context
Retrieve user context data for a specific layer.

**Parameters:**
- `layer` (required): 0, 1, 2, or 3
  - 0: Language, timezone, communication preferences
  - 1: Active projects, goals, pinned memories
  - 2: Personal identity info
  - 3: Encrypted vault (requires consent)
- `fields` (optional): Array of specific fields to retrieve

**Example:**
```json
{
  "layer": 1,
  "fields": ["active_projects", "current_goals"]
}
```

### update_context
Update user context for a specific layer.

**Parameters:**
- `layer` (required): 0, 1, or 2 (vault layer 3 cannot be directly updated)
- `data` (required): Object with fields to update

**Example:**
```json
{
  "layer": 1,
  "data": {
    "active_projects": ["New Project"],
    "current_goals": ["Learning", "Building"]
  }
}
```

### search_context
Semantic search across all context layers and knowledge base.

**Parameters:**
- `query` (required): Natural language search query
- `include_knowledge` (optional): Also search Knowledge Base (default true)
- `limit` (optional): Max results to return
- `min_similarity` (optional): Minimum similarity threshold 0.0-1.0

**Example:**
```json
{
  "query": "Rust authentication implementation",
  "limit": 5,
  "min_similarity": 0.7
}
```

### request_vault_access
Request access to encrypted vault data (Layer 3).

**Parameters:**
- `reason` (required): Reason for access
- `requested_fields` (required): Array of field names

**Example:**
```json
{
  "reason": "Need to verify identity",
  "requested_fields": ["full_name", "birth_date"]
}
```

## Knowledge Base

### push_knowledge
Store categorized knowledge entry.

**Parameters:**
- `content` (required): Main knowledge content
- `category` (required): Type of knowledge
  - project_update, code_change, decision, learning, todo, insight, architecture, bug_fix, feature, note
- `summary` (optional): One-line summary
- `source_project` (optional): Related project name
- `subcategory` (optional): More specific category
- `tags` (optional): Array of tags

**Example:**
```json
{
  "content": "Discovered that caching reduces latency by 80%",
  "category": "insight",
  "summary": "Caching performance gains",
  "source_project": "api-optimization",
  "tags": ["performance", "caching", "redis"]
}
```

### query_knowledge
Search Knowledge Base with filtering.

**Parameters:**
- `keyword` (optional): Search in content/summary
- `category` (optional): Filter by category
- `tag` (optional): Filter by tag
- `source_project` (optional): Filter by project
- `limit` (optional): Max results (default 20)
- `offset` (optional): Skip first N results

**Example:**
```json
{
  "category": "project_update",
  "tag": "rust",
  "limit": 10
}
```

### list_knowledge_categories
List all knowledge categories with entry counts.

**No parameters required.**

## LLM Gateway

### list_conversations
List user's LLM Gateway conversations.

**Parameters:**
- `limit` (optional): Max conversations (default 20)
- `provider` (optional): Filter by provider (openai, gemini, anthropic, ollama)

**Example:**
```json
{
  "limit": 10,
  "provider": "openai"
}
```

### get_conversation
Get full conversation history.

**Parameters:**
- `conversation_id` (required): UUID of conversation

**Example:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### search_conversations
Search through all conversation history.

**Parameters:**
- `query` (required): Search keyword or phrase
- `limit` (optional): Max results (default 5)
- `provider` (optional): Filter by provider

**Example:**
```json
{
  "query": "authentication error",
  "limit": 10
}
```

### chat_with_llm
Send message to an LLM through the Gateway.

**Parameters:**
- `message` (required): Message to send
- `provider` (required): LLM provider
- `model` (required): Model name
- `conversation_id` (optional): Continue existing conversation
- `title` (optional): Title for new conversation

**Example:**
```json
{
  "message": "Explain quantum computing",
  "provider": "openai",
  "model": "gpt-4",
  "title": "Quantum Learning"
}
```

### fork_conversation
Fork conversation at a specific message to use different LLM.

**Parameters:**
- `conversation_id` (required): Source conversation UUID
- `message_id` (required): Fork point message UUID
- `new_provider` (required): New LLM provider
- `new_model` (required): New model name

**Example:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660f9511-f30c-52e5-b827-557766551111",
  "new_provider": "anthropic",
  "new_model": "claude-sonnet-4.6"
}
```

### get_llm_usage
Get token usage metrics across all providers.

**No parameters required.**

Returns:
- Total tokens used
- Breakdown by provider
- Breakdown by model

## MCP Discovery

### tools/list
List all available MCP tools.

**No parameters required.**

Returns complete list with descriptions and input schemas.