---
name: comfyui-workflow
description: Universal ComfyUI workflow executor with 33+ workflow templates. Self-describing — use --inspect on ANY workflow to discover inputs and outputs automatically. Works with local ComfyUI, Windows Portable via WSL, or remote servers.
---

# ComfyUI Workflows — Agent Usage Guide

> **⚠️ READ-ONLY WARNING**: The scripts in this skill (`comfy_run.py`, `comfy_api.py`) are
> production-validated and **must not be modified**. They handle 33+ workflow JSONs with complex LiteGraph→API
> conversion, subgraph expansion, bypass resolution, and multi-format output downloading. Any modification risks
> breaking all workflows. **Only read and use the scripts — never edit them.**

---

## Requirements

Before using this skill, ensure your environment meets these requirements:

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10 or higher |
| **pip packages** | `websocket-client`, `requests` |
| **ComfyUI server** | Must be running before executing workflows |
| **Token** | Required if ComfyUI has authentication enabled |

Install Python dependencies:
```bash
pip install websocket-client requests
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `COMFY_HOST` | ComfyUI server address | `127.0.0.1:8188` |
| `COMFY_WORKFLOW_DIRS` | Additional workflow directories | (none) |

### Credentials

| Credential | Required | Source |
|------------|----------|--------|
| ComfyUI Token | Only if auth enabled | ComfyUI settings page |

---

## Personal Configuration Required

Before using this skill, ensure these items are configured for your environment:

| Item | Description | Where to Configure |
|------|-------------|-------------------|
| `comfy_host` | Your ComfyUI server address | `scripts/config.json` or `COMFY_HOST` env |
| ComfyUI server | Must be running before executing workflows | Start manually |
| Model paths | Your local model directories | `MODELS_INVENTORY.md` (for reference) |
| Token | ComfyUI authentication token | Get from ComfyUI settings |
| Workflow files | Your own workflow JSON files | `workflows/` directory (see note below) |

## Quick Setup

### 1. Start ComfyUI

Start your ComfyUI server manually before executing any workflows. The skill expects ComfyUI to be running at the configured host.

### 2. Configure Connection

Create `scripts/config.json`:

```json
{
  "comfy_host": "127.0.0.1:8188",
  "workflow_dirs": []
}
```

Or set environment variables:
```bash
export COMFY_HOST="127.0.0.1:8188"
```

### 3. Install Dependencies

```bash
pip install websocket-client requests
```

### 4. Add Your Workflows

Place workflow JSON files in `workflows/` directory, organized by category:

```
workflows/
├── Image-Text/
│   ├── workflow1.json
│   └── workflow2.json
├── Image-Edit/
│   └── ...
└── Video/
    └── ...
```

## Shell Variables (use in all commands)

```bash
VENV=python3  # or path to your venv
SCRIPT=/path/to/comfyui-workflow-skill/scripts/comfy_run.py
```

---

## End-to-End Workflow (Steps 0–5)

### Step 0 — Ensure ComfyUI Is Running

Start ComfyUI manually. Verify it's accessible at `http://127.0.0.1:8188`.

### Step 1 — List Available Workflows

```bash
$VENV $SCRIPT --list
```

### Step 2 — Inspect the Workflow

```bash
$VENV $SCRIPT -w "workflow_name" --inspect
```

### Step 3 — Prepare Inputs

```bash
--prompt "your prompt"           # Text prompts
--image /path/to/image.jpg       # Image inputs
--audio /path/to/audio.wav       # Audio inputs
--video /path/to/video.mp4       # Video inputs
--width 1024 --height 1024       # Resolution
--steps 50 --cfg 4.0 --seed 42   # Sampler settings
--override '{"node_id": {"key": value}}'  # Advanced overrides
```

### Step 4 — Execute

```bash
$VENV $SCRIPT -w "workflow_name" --prompt "..." -o /tmp
```

### Step 5 — Collect Outputs

Outputs are saved to the `-o` directory with auto-generated prefixes.

---

## CLI Reference

```
Usage: comfy_run.py [-w WORKFLOW] [options]

Modes:
  --list              List all available workflows
  --inspect           Human-readable input/output inspection
  --inspect-json      Machine-readable JSON inspection
  --dry-run           Print API JSON without executing
  --queue             Submit to queue and return immediately
  --status [IDs...]   Check queue state

Input customization:
  --prompt, -p TEXT        Positive prompt
  --negative, -n TEXT      Negative prompt
  --image, -i PATH [...]   Input image(s)
  --audio, -a PATH [...]   Input audio file(s)
  --video, -v PATH [...]   Input video file(s)

Generation settings:
  --width, -W INT          Output width
  --height, -H INT         Output height
  --steps INT              Sampling steps
  --cfg FLOAT              CFG scale
  --seed INT               Random seed

Advanced:
  --override JSON          Node input overrides
  --config PATH            YAML/JSON config file
  --server HOST:PORT       ComfyUI server
  --output-dir, -o PATH    Output directory
  --output-prefix TEXT     Output filename prefix
  --no-ensure              Skip auto-starting ComfyUI
  --no-validate            Skip input validation
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Workflow not found` | Use `--list` to see available workflows |
| `NO OUTPUTS generated` | Run `--inspect` to check required inputs |
| `Cannot reach ComfyUI` | Ensure ComfyUI is running at configured host |
| `Image file not found` | Use absolute paths, verify with `ls -la` |
| GPU out of memory | Reduce resolution or steps |

---

## Knowledge Cache Pattern

`MODELS_INVENTORY.md` and `WORKFLOWS_SUMMARY.md` serve as the agent's persistent knowledge base for the user's actual ComfyUI setup. Use them to cache learned information across sessions:

> **⚠️ DO NOT REFERENCE THE EXAMPLE CONTENT**: The default content in these files describes sanitized example workflows that will NOT work. Agents MUST update them with the user's actual data before relying on them. Using outdated example data will cause workflow failures.

### Initial Setup (First Time)

When the user first provides their own workflow files:
1. **Clean the example content** — Remove the sanitized example entries from both files
2. **Populate with user's data** — Run `--inspect` on each workflow, document findings in `WORKFLOWS_SUMMARY.md`
3. **Inventory models** — Scan user's model directories, update `MODELS_INVENTORY.md` with their actual models

### Ongoing Maintenance

- **After using a new workflow** → Add its documentation to `WORKFLOWS_SUMMARY.md`
- **After downloading models** → Update `MODELS_INVENTORY.md` status
- **When learning model-specific quirks** → Document tips/tricks in the relevant section

### Session Workflow

```
1. Read MODELS_INVENTORY.md → know available models
2. Read WORKFLOWS_SUMMARY.md → know workflow capabilities
3. Select appropriate workflow without re-inspecting
4. If new workflow discovered → document it for future sessions
```

This pattern lets the agent skip repeated discovery and work efficiently with cached knowledge.

---

## Reference Documents

| Document | Purpose |
|----------|---------|
| `MODELS_INVENTORY.md` | **Knowledge cache** — user's installed models, status, paths |
| `WORKFLOWS_SUMMARY.md` | **Knowledge cache** — workflow capabilities, settings, tips |
| `references/prompting-guide.md` | Prompt anatomy, model-specific strategies |
| `references/maintenance.md` | Code structure, debugging |
| `references/architecture.md` | Design principles |