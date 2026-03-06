---
name: memos
description: "Use MemOS API for memory operations. Use when: (1) user asks to
  save/store/remember something to memory, (2) user asks to read/retrieve
  memory, (3) user wants to list/delete memory files, (4) replacing OpenClaw's
  default memory with MemOS."
---


# MemOS - External Memory Service

MemOS provides persistent memory storage via REST API.

## API Base URL
```
{{MEMOS_API_URL}}
```

## Available Endpoints

### Add Memory
```bash
POST /add
Body: {"content": "...", "source": "agent/filename.md"}
```

### Read Memory
```bash
GET /read/{agent}/{filename}
```

### List Memories
```bash
GET /memories
```

### Search Memories
```bash
POST /search
Body: {"query": "...", "top_k": 3}
```

### Delete Memory
```bash
DELETE /delete/{agent}/{filename}
```

### List Agents
```bash
GET /agents
```

### Health Check
```bash
GET /health
```

## Usage Examples

**Add memory:**
```python
import requests
requests.post('{{MEMOS_API_URL}}/add', json={
    'content': '咖啡大佬今天教我使用MemOS',
    'source': 'alin/2026-02-23.md'
})
```

**Read memory:**
```python
import requests
r = requests.get('{{MEMOS_API_URL}}/read/alin/2026-02-23.md')
print(r.json()['content'])
```

**Search memory:**
```python
import requests
r = requests.post('{{MEMOS_API_URL}}/search', json={
    'query': '咖啡大佬教了什么',
    'top_k': 3
})
for item in r.json():
    print(f"{item['source']}: {item['score']}")
```

**Delete memory:**
```python
import requests
requests.delete('{{MEMOS_API_URL}}/delete/alin/2026-02-23.md')
```

**List all agents:**
```python
import requests
r = requests.get('{{MEMOS_API_URL}}/agents')
for agent in r.json()['agents']:
    print(f"{agent['name']}: {agent['file_count']} files")
```

## Notes

- Use Python `requests` library for API calls
- Always use `json=` parameter (not raw body) for POST requests
- File path format: `{agent}/{filename}.md`
- API returns JSON with `content` field for read operations
- Delete removes both file and vector index
- Run MemOS server: `python D:\AI\MemOS\api_server.py`
