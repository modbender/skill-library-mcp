# Powerdrill Data Analysis Skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for AI-powered data analysis using the [Powerdrill](https://chat.powerdrill.ai/) platform. Upload datasets, ask natural-language questions, and get insights with charts, tables, and analytical reports.

## What This Does

This skill enables Claude to analyze data through Powerdrill's API. Given a file or dataset, Claude can:

- Upload local files (CSV, Excel, PDF, etc.) for analysis
- Ask natural-language questions about your data
- Generate charts, tables, and statistical insights
- Manage datasets and analysis sessions
- Automatically clean up resources when done

## Quick Start

### 1. Get Powerdrill Credentials

You need a Powerdrill Teamspace and API key:

1. **Create a Teamspace** - [Watch setup tutorial](https://www.youtube.com/watch?v=I-0yGD9HeDw)
2. **Get your API key** - [Watch API key tutorial](https://www.youtube.com/watch?v=qs-GsUgjb1g)

### 2. Set Environment Variables

```bash
export POWERDRILL_USER_ID="your_user_id"
export POWERDRILL_PROJECT_API_KEY="your_project_api_key"
```

### 3. Install Dependency

```bash
pip install requests
```

### 4. Run

**As a Python library:**

```python
from scripts.powerdrill_client import *

# Create dataset and upload a file
ds = create_dataset("Sales Data")
dataset_id = ds["data"]["id"]

upload_and_create_data_source(dataset_id, "sales.csv")
wait_for_dataset_sync(dataset_id)

# Create session and ask questions
session = create_session("Analysis")
session_id = session["data"]["id"]

result = create_job(session_id, "What are the top 5 products by revenue?", dataset_id=dataset_id)
for block in result["data"]["blocks"]:
    if block["type"] == "MESSAGE":
        print(block["content"])

# Clean up when done
cleanup(session_id=session_id, dataset_id=dataset_id)
```

**As a CLI:**

```bash
python scripts/powerdrill_client.py create-dataset "Sales Data"
python scripts/powerdrill_client.py upload-file dset-xxx sales.csv
python scripts/powerdrill_client.py wait-sync dset-xxx
python scripts/powerdrill_client.py create-session "Analysis"
python scripts/powerdrill_client.py create-job SESSION_ID "What are the top 5 products by revenue?" --dataset-id dset-xxx
python scripts/powerdrill_client.py cleanup --session-id SESSION_ID --dataset-id dset-xxx
```

## Project Structure

```
powerdrill-skills/
  SKILL.md                        # Skill definition (Claude Code reads this)
  README.md                       # This file
  scripts/
    powerdrill_client.py           # Python API client + CLI
  test/
    testdata.csv                   # Sample data for testing (gitignored)
```

## API Coverage

The Python client covers all Powerdrill API v2 endpoints:

| Function | API Endpoint | Description |
|----------|-------------|-------------|
| `list_datasets()` | `GET /v2/team/datasets` | List all datasets |
| `create_dataset()` | `POST /v2/team/datasets` | Create a new dataset |
| `get_dataset_overview()` | `GET /v2/team/datasets/{id}/overview` | Get dataset summary and suggested questions |
| `get_dataset_status()` | `GET /v2/team/datasets/{id}/status` | Check data source sync status |
| `delete_dataset()` | `DELETE /v2/team/datasets/{id}` | Delete a dataset |
| `list_data_sources()` | `GET /v2/team/datasets/{id}/datasources` | List files in a dataset |
| `create_data_source()` | `POST /v2/team/datasets/{id}/datasources` | Add a data source (URL or uploaded file) |
| `upload_local_file()` | `POST /v2/team/file/init-multipart-upload` | Upload a local file via multipart upload |
| `upload_and_create_data_source()` | (composite) | Upload + create data source in one call |
| `wait_for_dataset_sync()` | `GET /v2/team/datasets/{id}/status` | Poll until all sources are synced |
| `list_sessions()` | `GET /v2/team/sessions` | List analysis sessions |
| `create_session()` | `POST /v2/team/sessions` | Create a new session |
| `delete_session()` | `DELETE /v2/team/sessions/{id}` | Delete a session |
| `create_job()` | `POST /v2/team/jobs` | Run a natural-language analysis query |
| `cleanup()` | (composite) | Delete session and dataset |

## Supported File Formats

`.csv`, `.tsv`, `.md`, `.mdx`, `.json`, `.txt`, `.pdf`, `.pptx`, `.docx`, `.xls`, `.xlsx`

## Analysis Response Types

When you run `create_job()`, the response contains blocks of different types:

| Block Type | Content |
|-----------|---------|
| `MESSAGE` | Analytical text and conclusions |
| `CODE` | Python code used for analysis |
| `TABLE` | CSV download URL (expires after ~6 days) |
| `IMAGE` | Chart/visualization PNG URL (expires after ~6 days) |
| `SOURCES` | File citations and references |
| `QUESTIONS` | Suggested follow-up questions |
| `CHART_INFO` | Chart configuration data |

## CLI Reference

```
python scripts/powerdrill_client.py <command> [options]

Datasets:
  list-datasets [--search TEXT] [--page-size N]
  create-dataset NAME [--description TEXT]
  get-dataset-overview DATASET_ID
  delete-dataset DATASET_ID

Data Sources:
  list-data-sources DATASET_ID
  upload-file DATASET_ID FILE_PATH
  wait-sync DATASET_ID

Sessions:
  list-sessions [--search TEXT]
  create-session NAME [--output-language LANG]
  delete-session SESSION_ID

Jobs:
  create-job SESSION_ID QUESTION [--dataset-id ID] [--stream]

Cleanup:
  cleanup [--session-id ID] [--dataset-id ID]
```

## Key Concepts

- **Dataset** - A container that holds one or more data sources (files)
- **Data Source** - An individual file uploaded to a dataset
- **Session** - A conversation context that maintains history across multiple analysis jobs
- **Job** - A single natural-language analysis query against a dataset

### Typical Workflow

```
create_dataset -> upload file -> wait_for_sync -> create_session -> create_job (repeat) -> cleanup
```

Always create a session before running jobs. Always call `cleanup()` after analysis to delete temporary sessions and datasets.

## References

- [Powerdrill API Documentation](https://docs.powerdrill.ai/api-reference/v2)
- [Quick Start Guide](https://docs.powerdrill.ai/developer-guides/quick-start-v2)
- [Streaming Response Handling](https://docs.powerdrill.ai/api-reference/v2/streaming#streaming-response)
- [Checking Data Source Status](https://docs.powerdrill.ai/api-reference/v2/how-to-check-data-sources)
- [Powerdrill MCP Server (Node.js)](https://github.com/powerdrillai/powerdrill-mcp)

## License

MIT
