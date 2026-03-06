# SkillNet API & CLI Reference

## REST API (Public, No Auth)

**Base URL**: `https://api-skillnet.openkg.cn/v1`

> **Data handling**: The search API only sends your query string to return matching skills. No local files, credentials, or personal data are transmitted during search or download operations.

### `GET /search`

| Parameter   | Type   | Default      | Description                            |
| ----------- | ------ | ------------ | -------------------------------------- |
| `q`         | string | **required** | Search query                           |
| `mode`      | string | `"keyword"`  | `"keyword"` or `"vector"`              |
| `category`  | string | —            | Filter by category                     |
| `limit`     | int    | 20           | Max results                            |
| `page`      | int    | 1            | Page number (keyword only)             |
| `min_stars` | int    | 0            | Minimum stars (keyword only)           |
| `sort_by`   | string | `"stars"`    | `"stars"` or `"recent"` (keyword only) |
| `threshold` | float  | 0.8          | Similarity 0.0–1.0 (vector only)       |

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "skill_name": "pdf-parser",
      "skill_description": "Parse and extract text from PDF files...",
      "author": "...",
      "stars": 5,
      "skill_url": "https://github.com/...",
      "category": "data-science-visualization",
      "evaluation": {
        "safety": { "level": "Good", "reason": "..." },
        "completeness": { "level": "Average", "reason": "..." },
        "executability": { "level": "Good", "reason": "..." },
        "maintainability": { "level": "Average", "reason": "..." },
        "cost_awareness": { "level": "Good", "reason": "..." }
      }
    }
  ],
  "meta": {
    "query": "pdf",
    "mode": "keyword",
    "total": 42,
    "page": 1,
    "limit": 20
  }
}
```

---

## CLI Commands

Install: `pip install skillnet-ai` or `pipx install skillnet-ai` (provides `skillnet` command)

### `skillnet search`

```
skillnet search QUERY [OPTIONS]

Arguments:
  QUERY                         Search query (required)

Options:
  --mode TEXT                   "keyword" or "vector"  [default: keyword]
  --category TEXT               Filter by category
  --limit INTEGER               Max results  [default: 20]
  --page INTEGER                Page number (keyword)  [default: 1]
  --min-stars INTEGER           Minimum star rating  [default: 0]
  --sort-by TEXT                "stars" or "recent"  [default: stars]
  --threshold FLOAT             Similarity 0.0-1.0 (vector)  [default: 0.8]
```

### `skillnet download`

```
skillnet download URL [OPTIONS]

Arguments:
  URL                           GitHub URL of the skill folder (required)

Options:
  -d, --target-dir TEXT         Local install directory  [default: .]
  -t, --token TEXT              GitHub token override
```

### `skillnet create`

```
skillnet create [OPTIONS]

Options:
  --github TEXT                 GitHub repository URL
  --office TEXT                 Path to PDF/PPT/DOCX
  --prompt TEXT                 Natural-language description
  TRAJECTORY                    Path to trajectory/log file (positional)
  --output-dir TEXT             Output directory  [default: ./generated_skills]
  --model TEXT                  LLM model  [default: gpt-4o]
  --max-files INTEGER           Max files for GitHub mode  [default: 20]
```

Input types (auto-detected):

- `github` — analyses repo structure, README, key source files
- `trajectory` — extracts patterns from execution logs
- `office` — extracts knowledge from documents
- `prompt` — generates from description

### `skillnet evaluate`

```
skillnet evaluate TARGET [OPTIONS]

Arguments:
  TARGET                        Local path or GitHub URL (required)

Options:
  --name TEXT                   Override skill name
  --category TEXT               Override category
  --description TEXT            Override description
  --model TEXT                  LLM model  [default: gpt-4o]
  --max-workers INTEGER         Concurrency  [default: 5]
```

Output: Five dimensions — Safety, Completeness, Executability, Maintainability, Cost-Awareness. Each rated Good / Average / Poor with a textual reason.

### `skillnet analyze`

```
skillnet analyze SKILLS_DIR [OPTIONS]

Arguments:
  SKILLS_DIR                    Directory containing skill folders (required)

Options:
  --no-save                     Don't write relationships.json
  --model TEXT                  LLM model  [default: gpt-4o]
```

Output: `relationships.json` with edges:

```json
[
  {
    "source": "skill-a",
    "target": "skill-b",
    "type": "similar_to",
    "reason": "Both handle PDF parsing but with different approaches"
  }
]
```

Relationship types: `similar_to`, `belong_to`, `compose_with`, `depend_on`.

---

## Python SDK

```python
from skillnet_ai import SkillNetClient

client = SkillNetClient(
    api_key="sk-...",          # env: API_KEY (required for create/evaluate/analyze)
    base_url="https://...",    # env: BASE_URL (optional)
    github_token="ghp_..."    # env: GITHUB_TOKEN (optional)
)
```

### `client.search(q, mode, category, limit, page, min_stars, sort_by, threshold)`

Returns `List[SkillModel]`. Each object has:

- `.skill_name` (str)
- `.skill_description` (str)
- `.author` (str)
- `.stars` (int)
- `.skill_url` (str)
- `.category` (str)
- `.evaluation` (dict or None)

### `client.download(url, target_dir, token)`

Returns `str` — absolute path to installed skill directory.

### `client.create(input_type, trajectory_content, github_url, office_file, prompt, output_dir, model, max_files)`

Returns `List[str]` — paths to generated skill directories.

### `client.evaluate(target, name, category, description, model, max_workers, cache_dir)`

Returns `Dict[str, Any]` — evaluation report with five dimension keys.

### `client.analyze(skills_dir, save_to_file, model)`

Returns `List[Dict[str, Any]]` — relationship edges.

---

## Environment Variables

| Variable       | Purpose                         | Required                      |
| -------------- | ------------------------------- | ----------------------------- |
| `API_KEY`      | LLM API key (OpenAI-compatible) | For create, evaluate, analyze |
| `BASE_URL`     | Custom LLM endpoint             | No (defaults to OpenAI)       |
| `GITHUB_TOKEN` | GitHub PAT for private repos    | No                            |

## Security & Privacy

### Credential Scope

- **API_KEY**: Used exclusively for authenticating with the LLM endpoint (`BASE_URL`). It is never sent to the SkillNet API or any other third-party service.
- **GITHUB_TOKEN**: Sent only to `api.github.com` (read-only `repo` scope sufficient). Never forwarded elsewhere.

### Network Endpoints

The CLI only contacts:

- `api-skillnet.openkg.cn` — skill search/download (read-only, no auth)
- `api.github.com` — repo access (only with GITHUB_TOKEN)
- Your configured `BASE_URL` — LLM processing

Set `BASE_URL` to a local endpoint (e.g., `http://127.0.0.1:8000/v1`) for air-gapped usage.

### No Destructive Operations

The CLI never executes file deletion commands. Skill cleanup should be performed manually using safe methods (e.g., moving to a backup directory).
