# SurrealFS -- AI Agent Virtual Filesystem

SurrealFS is a virtual filesystem backed by SurrealDB, designed primarily for AI agent workflows. It provides a familiar file and directory interface with persistent storage, enabling AI agents to manage workspace files, notes, and project artifacts through standard filesystem operations.

---

## Overview

SurrealFS consists of two components:

1. **Rust Core** (`surrealfs` crate): The filesystem engine providing async API and CLI REPL
2. **Python Agent** (`surrealfs-ai`): A Pydantic AI agent that exposes SurrealFS as a conversational interface

All filesystem data is stored in SurrealDB, making it queryable, persistent, and shareable across processes and machines.

---

## Rust Core (`surrealfs`)

### Installation

```bash
cargo install surrealfs
```

### Storage Backends

SurrealFS supports two storage backends:

**Embedded RocksDB** (local, single-process):

```bash
surrealfs --storage rocksdb://./my_fs_data
```

**Remote SurrealDB** (shared, multi-process):

```bash
surrealfs --storage ws://localhost:8000 \
  --namespace my_ns \
  --database my_db \
  --username root \
  --password root
```

### CLI REPL

SurrealFS provides an interactive REPL with standard filesystem commands:

```
$ surrealfs --storage rocksdb://./data

surrealfs> pwd
/

surrealfs> mkdir /projects
Created directory: /projects

surrealfs> mkdir /projects/my-app
Created directory: /projects/my-app

surrealfs> cd /projects/my-app
/projects/my-app

surrealfs> write_file README.md "# My Application\n\nA sample project."
Written: /projects/my-app/README.md (36 bytes)

surrealfs> cat README.md
# My Application

A sample project.

surrealfs> ls
README.md

surrealfs> touch notes.txt
Created: /projects/my-app/notes.txt

surrealfs> edit notes.txt "Meeting notes from today's standup."
Written: /projects/my-app/notes.txt (35 bytes)

surrealfs> ls /
projects/
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ls [path]` | List directory contents | `ls /projects` |
| `cat <path>` | Display file contents | `cat /readme.md` |
| `tail <path> [n]` | Display last N lines of a file | `tail /logs/app.log 20` |
| `nl <path>` | Display file with line numbers | `nl /src/main.rs` |
| `grep <pattern> <path>` | Search for pattern in file | `grep "TODO" /src/main.rs` |
| `touch <path>` | Create an empty file | `touch /notes.txt` |
| `mkdir <path>` | Create a directory | `mkdir /projects` |
| `write_file <path> <content>` | Write content to a file | `write_file /hello.txt "Hello"` |
| `edit <path> <content>` | Replace file contents | `edit /hello.txt "Updated"` |
| `cp <src> <dst>` | Copy a file or directory | `cp /a.txt /b.txt` |
| `cd <path>` | Change working directory | `cd /projects` |
| `pwd` | Print working directory | `pwd` |

### Path Normalization and Safety

SurrealFS enforces path safety:
- All paths are normalized to prevent directory traversal
- Paths cannot escape the root `/` directory
- Relative paths like `../../../etc/passwd` are resolved safely within the virtual filesystem
- Symbolic links are not supported (no escape vectors)

### Async Rust API

For programmatic use in Rust applications:

```rust
use surrealfs::SurrealFs;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Connect to a remote SurrealDB instance
    let fs = SurrealFs::connect("ws://localhost:8000", "my_ns", "my_db").await?;

    // Or use embedded storage
    let fs = SurrealFs::open_rocksdb("./my_fs_data").await?;

    // Create directories
    fs.mkdir("/projects/my-app").await?;

    // Write files
    fs.write_file("/projects/my-app/README.md", "# My App").await?;

    // Read files
    let content = fs.read_file("/projects/my-app/README.md").await?;
    println!("{}", content);

    // List directories
    let entries = fs.ls("/projects").await?;
    for entry in entries {
        println!("{}", entry.name);
    }

    // Copy files
    fs.cp("/projects/my-app/README.md", "/backups/readme_backup.md").await?;

    // Search within files
    let matches = fs.grep("TODO", "/projects/my-app/src/main.rs").await?;

    Ok(())
}
```

### Curl Piping Support

SurrealFS supports piping content from external sources:

```bash
# In the REPL, pipe curl output to a file
surrealfs> write_file /data/response.json $(curl -s https://api.example.com/data)
```

---

## Python Agent (`surrealfs-ai`)

### Installation

```bash
pip install surrealfs-ai
```

### Quick Start

```python
from surrealfs_ai import build_chat_agent
import uvicorn

# Build the agent with default configuration
agent = build_chat_agent()

# Convert to a web application
app = agent.to_web()

# Serve on port 7932
uvicorn.run(app, host="127.0.0.1", port=7932)
```

### Architecture

The Python agent wraps SurrealFS operations in a Pydantic AI agent:

- **Agent Framework**: Built on Pydantic AI agents
- **Default LLM**: Claude Haiku (fast, cost-effective for filesystem operations)
- **Observability**: Pydantic Logfire integration for tracing and monitoring
- **Interface**: HTTP API served via Uvicorn (default port 7932)

### Configuration

```python
from surrealfs_ai import build_chat_agent, AgentConfig

config = AgentConfig(
    # SurrealDB connection
    surreal_endpoint="ws://localhost:8000",
    surreal_namespace="my_ns",
    surreal_database="my_db",
    surreal_username="root",
    surreal_password="root",

    # LLM configuration
    model="claude-haiku",  # Default LLM

    # Server configuration
    host="127.0.0.1",
    port=7932,
)

agent = build_chat_agent(config)
```

### Conversational Interface

Once running, interact with the agent via HTTP:

```bash
# Create a directory
curl -X POST http://localhost:7932/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a directory called /notes/meetings"}'

# Write a file
curl -X POST http://localhost:7932/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a file at /notes/meetings/standup.md with the agenda for today"}'

# Read a file
curl -X POST http://localhost:7932/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me the contents of /notes/meetings/standup.md"}'

# Search files
curl -X POST http://localhost:7932/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find all files that mention deployment in /notes"}'
```

### Logfire Telemetry

The Python agent integrates with Pydantic Logfire for observability:

```python
import logfire

logfire.configure()

agent = build_chat_agent()
# All filesystem operations are automatically traced
```

---

## Use Cases

### AI Agent Workspace Management

SurrealFS provides a persistent workspace for AI agents that need to create, modify, and organize files as part of their workflows.

```python
# An AI coding agent can use SurrealFS to manage its workspace
agent_workspace = SurrealFs.connect("ws://localhost:8000", "agents", "workspace")

# Store generated code
await agent_workspace.write_file("/output/generated_module.py", generated_code)

# Keep scratch notes
await agent_workspace.write_file("/scratch/analysis.md", analysis_notes)

# Maintain state between sessions
await agent_workspace.write_file("/state/last_run.json", state_json)
```

### Persistent Note-Taking Systems

Build note-taking systems where all data is stored in SurrealDB and queryable:

```python
# Notes are stored as files but backed by SurrealDB
# This means they can be queried using SurrealQL

# Write notes
await fs.write_file("/notes/2026-02-19.md", daily_notes)

# The underlying SurrealDB data can be queried directly
# for advanced search, aggregation, and analysis
```

### Multi-Agent Collaboration

Multiple AI agents can share a filesystem backed by the same remote SurrealDB instance:

```python
# Agent 1: Research agent writes findings
research_fs = SurrealFs.connect("ws://surrealdb:8000", "project", "shared")
await research_fs.write_file("/research/findings.md", research_results)

# Agent 2: Writing agent reads findings and produces output
writer_fs = SurrealFs.connect("ws://surrealdb:8000", "project", "shared")
findings = await writer_fs.read_file("/research/findings.md")
await writer_fs.write_file("/output/report.md", generate_report(findings))

# Agent 3: Review agent reads output
reviewer_fs = SurrealFs.connect("ws://surrealdb:8000", "project", "shared")
report = await reviewer_fs.read_file("/output/report.md")
```

### Content Organization

Organize and manage content with directory hierarchies:

```
/
├── projects/
│   ├── project-alpha/
│   │   ├── README.md
│   │   ├── spec.md
│   │   └── notes/
│   └── project-beta/
│       ├── README.md
│       └── design.md
├── templates/
│   ├── project-template.md
│   └── meeting-template.md
└── archive/
    └── 2025/
```

---

## Integration Patterns

### As an MCP Tool

SurrealFS can be exposed as an MCP (Model Context Protocol) tool for AI coding agents:

```json
{
  "name": "surrealfs",
  "description": "Virtual filesystem for persistent file management",
  "tools": [
    {
      "name": "read_file",
      "description": "Read the contents of a file",
      "parameters": {
        "path": { "type": "string", "description": "File path" }
      }
    },
    {
      "name": "write_file",
      "description": "Write content to a file",
      "parameters": {
        "path": { "type": "string", "description": "File path" },
        "content": { "type": "string", "description": "File content" }
      }
    },
    {
      "name": "list_directory",
      "description": "List files and directories at a path",
      "parameters": {
        "path": { "type": "string", "description": "Directory path" }
      }
    }
  ]
}
```

### Embedded in Agentic Workflows

```python
from surrealfs_ai import build_chat_agent

# Use SurrealFS as a tool within a larger agent pipeline
fs_agent = build_chat_agent()

async def research_pipeline(topic: str):
    # Step 1: Research agent gathers information
    research = await research_agent.run(topic)

    # Step 2: Store research in SurrealFS
    await fs_agent.run(f"Write the following research to /research/{topic}.md: {research}")

    # Step 3: Analysis agent reads and analyzes
    content = await fs_agent.run(f"Read /research/{topic}.md")
    analysis = await analysis_agent.run(content)

    # Step 4: Store analysis
    await fs_agent.run(f"Write analysis to /analysis/{topic}.md: {analysis}")
```

### REST API Access

The Python agent's HTTP interface provides a REST-like API:

```
POST /chat
Content-Type: application/json

{
  "message": "Your natural language filesystem command"
}
```

The agent interprets the natural language request and executes the appropriate filesystem operations.

### CLI Integration

Use SurrealFS from shell scripts and automation:

```bash
#!/bin/bash
# Backup script that stores results in SurrealFS

BACKUP_DATE=$(date +%Y-%m-%d)

# Run backup
pg_dump mydb > /tmp/backup.sql

# Store in SurrealFS via the REPL
echo "write_file /backups/${BACKUP_DATE}/database.sql $(cat /tmp/backup.sql)" | surrealfs --storage ws://localhost:8000

# Clean up
rm /tmp/backup.sql
```

---

## Storage Model

All filesystem data is stored in SurrealDB tables:

- **Files**: Stored as records with path, content, metadata (size, created, modified timestamps)
- **Directories**: Stored as records with path and metadata
- **Queryable**: Since data lives in SurrealDB, you can query it directly using SurrealQL for operations beyond standard filesystem commands (e.g., find all files modified in the last 24 hours, search across all file contents)

```surrealql
-- Find recently modified files
SELECT path, modified_at FROM fs_file
WHERE modified_at > time::now() - 24h
ORDER BY modified_at DESC;

-- Search across all file contents
SELECT path, content FROM fs_file
WHERE content CONTAINS "deployment";

-- Get total storage usage
SELECT math::sum(size) AS total_bytes FROM fs_file;
```
