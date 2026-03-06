---
name: Open Notebook Integration
description: A skill for integrating OpenClaw agents with open-notebook, a local
  AI research assistant (NotebookLM alternative).
---

# Open Notebook Integration

A skill for integrating OpenClaw agents with open-notebook, a local AI research assistant (NotebookLM alternative).

## What It Does

- Connects your agent to open-notebook running locally
- Creates thematic notebooks for research, agent discovery, and personal knowledge
- Enables saving and querying knowledge across sessions (second brain for agents)
- Supports local Ollama models (free, no API costs)

## Prerequisites

1. **Install Docker Desktop** (required for open-notebook)
2. **Install Ollama** with a model (e.g., qwen3-4b-thinking-32k)
3. **Run open-notebook:**
   ```powershell
   docker compose -f docker-compose-host-ollama.yml up -d
   ```
   
   Or use the default compose:
   ```powershell
   docker compose up -d
   ```

## Setup

The skill expects open-notebook at:
- UI: http://localhost:8502
- API: http://localhost:5055

## Functions (INCLUDED)

This skill provides these PowerShell functions directly:

### Add-ToNotebook
```powershell
function Add-ToNotebook {
    param(
        [string]$Content,
        [string]$NotebookId = "YOUR_NOTEBOOK_ID"
    )
    $body = @{
        content = $Content
        notebook_id = $NotebookId
        type = "text"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:5055/api/sources/json" -Method Post -ContentType "application/json" -Body $body
}
```

### Search-Notebook
```powershell
function Search-Notebook {
    param(
        [string]$Query,
        [string]$NotebookId = "YOUR_NOTEBOOK_ID"
    )
    $body = @{
        question = $Query
        notebook_ids = @($NotebookId)
        strategy_model = "model:YOUR_MODEL_ID"
        answer_model = "model:YOUR_MODEL_ID"
        final_answer_model = "model:YOUR_MODEL_ID"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:5055/api/search/ask" -Method Post -ContentType "application/json" -Body $body
}
```

### New-Notebook
```powershell
function New-Notebook {
    param(
        [string]$Name,
        [string]$Description = ""
    )
    $body = @{
        name = $Name
        description = $Description
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:5055/api/notebooks" -Method Post -ContentType "application/json" -Body $body
}
```

## Notebook IDs

After creating notebooks, update these variables in your scripts:

```powershell
$SIMULATION = "notebook:YOUR_SIMULATION_ID"
$CONSCIOUSNESS = "notebook:YOUR_CONSCIOUSNESS_ID"
$ENJAMBRE = "notebook:YOUR_ENJAMBRE_ID"
$OSIRIS = "notebook:YOUR_OSIRIS_ID"
$RESEARCH = "notebook:YOUR_RESEARCH_ID"
```

## Example Usage

```powershell
# Create a new notebook
New-Notebook -Name "My Research" -Description "Research notes"

# Save content
Add-ToNotebook -Content "This is my insight" -NotebookId "notebook:xxx"

# Query knowledge
$result = Search-Notebook -Query "What did I learn about X?" -NotebookId "notebook:xxx"
```

## Configuration Required

Before using, you MUST:
1. Run open-notebook with Docker
2. Create notebooks via the UI (http://localhost:8502) or API
3. Get your notebook IDs from the API response
4. Update the $NotebookId parameters in the functions

## Requirements

- Docker Desktop running
- Ollama with at least one model installed
- open-notebook containers running (SurrealDB + app)

## Troubleshooting

- If API fails, check containers: `docker ps`
- Check open-notebook logs: `docker compose logs`
- Verify Ollama is running: `curl http://localhost:11434/api/tags`

## Version

1.0.1 - Improved documentation, included function examples
