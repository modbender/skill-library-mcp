---
name: octoflow
display_name: OctoFlow
description: >
  Use when the user wants to run GPU-accelerated computations, analyze data,
  process images, train ML models, or generate code from natural language.
  OctoFlow turns English task descriptions into GPU programs via Vulkan.
  Also runs as an MCP server (`octoflow mcp-serve`) with 7 structured tools.
  No Python, no CUDA, no dependencies — single 3.2 MB binary.
  Use for: "sort a million numbers", "cluster this CSV", "blur this image",
  "plot my data", "calculate statistics", "run regression".
version: 1.3.3
metadata:
  openclaw:
    emoji: "\U0001F419"
    requires:
      anyBins:
        - octoflow
    install:
      - id: github-release
        kind: download
        url: https://github.com/octoflow-lang/octoflow/releases/latest
        bins: [octoflow]
        label: "Download OctoFlow from GitHub Releases (3.2 MB, zero dependencies)"
    os: [linux, win32]
    always: false
tags: [gpu, vulkan, compute, data-analysis, image-processing,
       machine-learning, programming-language, natural-language]
author: octoflow-lang
repository: https://github.com/octoflow-lang/octoflow
homepage: https://octoflow-lang.github.io/octoflow/
license: MIT
permissions:
  # All permissions are DENIED by default.
  # Users must explicitly opt-in with --allow-* flags.
  # See "Security Model" section below.
---

# OctoFlow

GPU-native programming language. Describe tasks in English, run them on any GPU via Vulkan.

## When to Use This Skill

**Use this skill when** the user says:
- "sort a million numbers on GPU" / "benchmark GPU performance"
- "load this CSV and show me statistics" / "analyze my data"
- "cluster my dataset" / "run K-means" / "train a classifier"
- "blur this image" / "resize this BMP" / "encode a GIF"
- "plot height vs weight" / "create a scatter plot"
- "calculate the Sharpe ratio" / "compute correlation"
- "find primes" / "generate random numbers on GPU"
- "run linear regression on my dataset"

**Do NOT use this skill when:**
- The user wants Python/JavaScript/Rust code (use the appropriate language tool)
- The task doesn't benefit from GPU acceleration or OctoFlow's built-in functions
- The user explicitly asks for a different language

## How to Run OctoFlow

### Chat mode (natural language to running code)
```bash
octoflow chat "sort 1M numbers on GPU"
```

### Run a .flow script
```bash
octoflow run program.flow
```

### Run with permissions (sandboxed by default)
```bash
# Allow reading data files
octoflow run analysis.flow --allow-read=./data

# Allow network access to specific domain
octoflow chat "fetch weather data" --allow-net=api.weather.com

# Allow writing output files
octoflow run report.flow --allow-read=./data --allow-write=./output
```

## Security Model

OctoFlow uses Deno-style permissions. **Everything is denied by default.**

| Permission | Default | How to enable | Example |
|------------|---------|---------------|---------|
| File read | **DENIED** | `--allow-read=./data` | Read CSV from `./data` only |
| File write | **DENIED** | `--allow-write=./output` | Write results to `./output` only |
| Network | **DENIED** | `--allow-net=api.example.com` | Fetch from one domain only |
| Process exec | **DENIED** | `--allow-exec=curl` | Allow `curl` only |

Without flags, OctoFlow can only read `.flow` source files and print to stdout.
No file access, no network, no subprocesses unless the user explicitly opts in.

## MCP Server

OctoFlow can run as an MCP server for AI agent integration:

```bash
octoflow mcp-serve
```

Add to your OpenClaw, Claude Desktop, or Cursor config:

```json
{"mcpServers": {"octoflow": {"command": "octoflow", "args": ["mcp-serve"]}}}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `octoflow_run` | Execute OctoFlow code directly |
| `octoflow_chat` | Natural language to GPU code |
| `octoflow_check` | Validate .flow syntax |
| `octoflow_gpu_sort` | GPU-accelerated sorting |
| `octoflow_gpu_stats` | GPU statistical operations |
| `octoflow_image` | Image processing (BMP, GIF) |
| `octoflow_csv` | CSV data analysis |

## Common Patterns

### Data Analysis
```bash
# User: "analyze sales.csv and show trends"
octoflow chat "load sales.csv, compute monthly averages, and plot the trend" --allow-read=.
```

### GPU Compute
```bash
# User: "sort a large dataset on GPU"
octoflow chat "generate 1M random numbers on GPU and sort them"
```

### Machine Learning
```bash
# User: "cluster my customers"
octoflow chat "load customers.csv, run K-means with 5 clusters, print cluster sizes" --allow-read=.
```

### Image Processing
```bash
# User: "blur this photo"
octoflow chat "load photo.bmp, apply gaussian blur, save as blurred.bmp" --allow-read=. --allow-write=.
```

### Statistics
```bash
# User: "what's the correlation between these columns?"
octoflow chat "load data.csv, compute Pearson correlation between col1 and col2" --allow-read=.
```

## Key Capabilities

| Feature | Detail |
|---------|--------|
| Builtins | 207 built-in functions |
| Stdlib | 246 modules across 18 domains |
| GPU kernels | 102 Vulkan compute shaders |
| GPU support | Any Vulkan GPU (NVIDIA, AMD, Intel) |
| Binary size | 3.2 MB, zero dependencies |
| Chat mode | English to code with auto-fix loop (max 3 retries) |
| Errors | 69 structured error codes with auto-fix suggestions |
| MCP Server | 7 structured tools via JSON-RPC 2.0 |
| Platforms | Windows, Linux |

## Data Storage

OctoFlow optionally saves your preferences to `~/.octoflow/` (user-level) and `.octoflow/` (per-project).

Contents: which stdlib modules you use frequently and corrections from previous sessions.

- **No telemetry.** No data is sent anywhere.
- **No network calls** unless you explicitly use `--allow-net`.
- **All data stays local** on your machine.
- **Disable entirely** with `--no-memory` flag — nothing is saved.
- **Project config** via `OCTOFLOW.md` in your project root (like `.eslintrc` or `pyproject.toml`).

## Install

### Download (recommended)

| Platform | File | SHA-256 |
|----------|------|---------|
| Windows x64 | [octoflow-v1.3.0-x86_64-windows.zip](https://github.com/octoflow-lang/octoflow/releases/download/v1.3.0/octoflow-v1.3.0-x86_64-windows.zip) | `84753c206a1c238b` |
| Linux x64 | [octoflow-v1.3.0-x86_64-linux.tar.gz](https://github.com/octoflow-lang/octoflow/releases/download/v1.3.0/octoflow-v1.3.0-x86_64-linux.tar.gz) | `4630ee16ec04f61f` |

Verify: `sha256sum octoflow-v1.3.0-*` (full checksums in [SHA256SUMS.txt](https://github.com/octoflow-lang/octoflow/releases/download/v1.3.0/SHA256SUMS.txt)).

Unzip/extract, add to PATH. No installer needed.

## Links

- [GitHub](https://github.com/octoflow-lang/octoflow)
- [Documentation](https://octoflow-lang.github.io/octoflow/)
- [Releases](https://github.com/octoflow-lang/octoflow/releases)
