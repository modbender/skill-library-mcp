---
name: powerdrill-data-analysis
description: This skill should be used when the user wants to analyze, explore, visualize, or query data using Powerdrill. Covers listing, creating, and deleting datasets; uploading local files as data sources; creating analysis sessions; running natural-language data analysis queries; and retrieving charts, tables, and insights. Triggers on requests like "analyze my data", "query my dataset", "upload this file for analysis", "list my datasets", "create a dataset", "visualize sales trends", "continue my previous analysis", "delete this dataset", or any data exploration task mentioning Powerdrill.
license: MIT
compatibility: claude
metadata:
  audience: human
  workflow: powerdrill
---

# Powerdrill Data Analysis Skill

Analyze data using the Powerdrill API via the Python client at `scripts/powerdrill_client.py`. All operations use the Powerdrill REST API v2 (`https://ai.data.cloud/api`).

## Prerequisites & Setup

Before using any Powerdrill functions, the user must have:

1. **A Powerdrill Teamspace** - Created by following: https://www.youtube.com/watch?v=I-0yGD9HeDw
2. **API Credentials** - Obtained by following: https://www.youtube.com/watch?v=qs-GsUgjb1g

Set these environment variables before running any script:

```bash
export POWERDRILL_USER_ID="your_user_id"
export POWERDRILL_PROJECT_API_KEY="your_project_api_key"
```

The only Python dependency is `requests`. Install with: `pip install requests`

If a call fails with an authentication error, verify the two environment variables are set and the API key is valid.

## How to Use

Import the client module and call functions directly. All functions read credentials from the environment automatically.

```python
import sys
sys.path.insert(0, "/absolute/path/to/scripts")  # adjust to actual location
from powerdrill_client import *
```

Or run via CLI:

```bash
python scripts/powerdrill_client.py <command> [args]
```

## Available Functions

### Datasets

#### `list_datasets(page_number=1, page_size=10, search=None) -> dict`
List datasets in the user's account. Typically the first step in any workflow.

```python
result = list_datasets(search="sales")
for ds in result["data"]["records"]:
    print(ds["id"], ds["name"])
```

#### `create_dataset(name, description="") -> dict`
Create a new empty dataset. Returns `{"data": {"id": "dset-..."}}`.

```python
ds = create_dataset("Q4 Sales Data", "Quarterly sales analysis")
dataset_id = ds["data"]["id"]
```

#### `get_dataset_overview(dataset_id) -> dict`
Get dataset summary, exploration questions, and keywords. Use after data sources are synced.

```python
overview = get_dataset_overview(dataset_id)
print(overview["data"]["summary"])
for q in overview["data"]["exploration_questions"]:
    print(f"  - {q}")
```

#### `get_dataset_status(dataset_id) -> dict`
Check how many data sources are synced/syncing/invalid.

```python
status = get_dataset_status(dataset_id)
# status["data"] = {"synched_count": 3, "synching_count": 0, "invalid_count": 0}
```

#### `delete_dataset(dataset_id) -> dict`
Permanently delete a dataset and all its data sources. **Irreversible** - always confirm with the user first.

### Data Sources

#### `list_data_sources(dataset_id, page_number=1, page_size=10, status=None) -> dict`
List files within a dataset. Filter by status: `synched`, `synching`, `invalid`.

```python
sources = list_data_sources(dataset_id, status="synched")
```

#### `create_data_source(dataset_id, name, *, url=None, file_object_key=None) -> dict`
Create a data source from a public URL or an uploaded file key. Provide exactly one of `url` or `file_object_key`.

```python
# From public URL
ds = create_data_source(dataset_id, "report.pdf", url="https://example.com/report.pdf")

# From uploaded file (see upload_local_file)
ds = create_data_source(dataset_id, "data.csv", file_object_key=key)
```

#### `upload_local_file(file_path) -> str`
Upload a local file via multipart upload. Returns `file_object_key` for use with `create_data_source()`.

Supported formats: `.csv`, `.tsv`, `.md`, `.mdx`, `.json`, `.txt`, `.pdf`, `.pptx`, `.docx`, `.xls`, `.xlsx`

#### `upload_and_create_data_source(dataset_id, file_path) -> dict`
Convenience function: uploads a local file then creates the data source in one call.

```python
result = upload_and_create_data_source(dataset_id, "/path/to/sales.csv")
datasource_id = result["data"]["id"]
```

#### `wait_for_dataset_sync(dataset_id, max_attempts=30, delay_seconds=3.0) -> dict`
Poll until all data sources in the dataset are synced. Raises `RuntimeError` on timeout or if invalid sources are detected.

```python
upload_and_create_data_source(dataset_id, "data.csv")
wait_for_dataset_sync(dataset_id)  # blocks until synced
```

### Sessions

#### `create_session(name, output_language="AUTO", job_mode="AUTO", max_contextual_job_history=10) -> dict`
Create an analysis session. Required before running jobs.

```python
session = create_session("Sales Analysis Session")
session_id = session["data"]["id"]
```

#### `list_sessions(page_number=1, page_size=10, search=None) -> dict`
List existing sessions. Use to find a previous session for resumption.

#### `delete_session(session_id) -> dict`
Delete a session. Use during cleanup after analysis is complete.

### Jobs (Data Analysis)

#### `create_job(session_id, question, dataset_id=None, datasource_ids=None, stream=False, output_language="AUTO", job_mode="AUTO") -> dict`
Run a natural-language analysis query. This is the core analysis function.

**Non-streaming** (default): returns full response with all blocks.

```python
result = create_job(session_id, "What are the top 5 products by revenue?", dataset_id=dataset_id)
for block in result["data"]["blocks"]:
    if block["type"] == "MESSAGE":
        print(block["content"])
    elif block["type"] == "TABLE":
        print(f"Table: {block['content']['url']}")
    elif block["type"] == "IMAGE":
        print(f"Chart: {block['content']['url']}")
```

**Streaming**: returns parsed result with accumulated text and separate blocks.

```python
result = create_job(session_id, "Summarize trends", dataset_id=dataset_id, stream=True)
print(result["text"])        # accumulated MESSAGE text
for b in result["blocks"]:   # TABLE, IMAGE, etc.
    print(b["type"], b["content"])
```

**Response block types:**
- `MESSAGE` - Analytical text
- `CODE` - Code snippets (Markdown)
- `TABLE` - `{name, url, expires_at}` - download before expiration
- `IMAGE` - `{name, url, expires_at}` - download before expiration
- `SOURCES` - Citation references
- `QUESTIONS` - Suggested follow-up questions
- `CHART_INFO` - Chart configuration and data

### Cleanup

#### `cleanup(session_id=None, dataset_id=None) -> None`
Delete session and/or dataset after analysis. Always call this when done.

```python
cleanup(session_id=session_id, dataset_id=dataset_id)
```

#### `cleanup_session(session_id) -> None` / `cleanup_dataset(dataset_id) -> None`
Delete individual resources. Errors are logged but not raised.

## Recommended Workflows

### Full analysis workflow (upload, analyze, cleanup)

```python
from powerdrill_client import *

# 1. Create dataset and upload data
ds = create_dataset("My Analysis")
dataset_id = ds["data"]["id"]

upload_and_create_data_source(dataset_id, "/path/to/data.csv")
wait_for_dataset_sync(dataset_id)

# 2. Create session and run analysis
session = create_session("Analysis Session")
session_id = session["data"]["id"]

result = create_job(session_id, "What are the key trends?", dataset_id=dataset_id)
for block in result["data"]["blocks"]:
    if block["type"] == "MESSAGE":
        print(block["content"])

# 3. Ask follow-up questions (same session for context)
result = create_job(session_id, "Break this down by region", dataset_id=dataset_id)

# 4. Cleanup when done
cleanup(session_id=session_id, dataset_id=dataset_id)
```

### Analyze existing dataset

```python
from powerdrill_client import *

# 1. Find the dataset
datasets = list_datasets(search="sales")
dataset_id = datasets["data"]["records"][0]["id"]

# 2. Explore it
overview = get_dataset_overview(dataset_id)
print(overview["data"]["summary"])

# 3. Create session and analyze
session = create_session("Quick Analysis")
session_id = session["data"]["id"]

result = create_job(session_id, overview["data"]["exploration_questions"][0], dataset_id=dataset_id)

# 4. Cleanup session when done (keep dataset)
cleanup_session(session_id)
```

### CLI usage

```bash
# List datasets
python scripts/powerdrill_client.py list-datasets --search "sales"

# Create dataset + upload file
python scripts/powerdrill_client.py create-dataset "Test Data"
python scripts/powerdrill_client.py upload-file dset-xxx /path/to/file.csv
python scripts/powerdrill_client.py wait-sync dset-xxx

# Create session and run a job
python scripts/powerdrill_client.py create-session "My Session"
python scripts/powerdrill_client.py create-job SESSION_ID "Summarize the data" --dataset-id dset-xxx

# Cleanup
python scripts/powerdrill_client.py cleanup --session-id SESSION_ID --dataset-id dset-xxx
```

## Error Handling

- **Authentication errors:** Verify `POWERDRILL_USER_ID` and `POWERDRILL_PROJECT_API_KEY`. Direct the user to the setup videos above.
- **Dataset not found:** Re-run `list_datasets()` to verify the ID. The dataset may have been deleted.
- **Job execution failure:** Ensure the dataset has at least one synced data source (`wait_for_dataset_sync()`). Retry with a rephrased question.
- **Upload timeout:** `wait_for_dataset_sync()` polls up to 30 attempts (90s). Use `get_dataset_status()` to check manually.
- **Invalid data sources:** Check file format is supported. Re-upload with correct file type.
- **Rate limiting:** Wait before retrying. Space out rapid sequential API calls.

## Important Notes

- Always create a session before running analysis jobs
- Always call `cleanup()` to delete sessions and datasets after analysis is complete
- Sessions maintain conversational context - reuse the same session for related follow-up questions
- TABLE and IMAGE URLs in job responses expire - download or present results promptly
- Call `wait_for_dataset_sync()` after uploading files, before running analysis
- Dataset and session names are limited to 128 characters
- Supported file formats: `.csv`, `.tsv`, `.md`, `.mdx`, `.json`, `.txt`, `.pdf`, `.pptx`, `.docx`, `.xls`, `.xlsx`
