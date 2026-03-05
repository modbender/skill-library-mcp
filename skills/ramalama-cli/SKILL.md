---
name: ramalama-cli
description: Run and interact with AI agents. 
metadata:
  openclaw:
    emoji: "🦙"
    requires:
      bins:
        - ramalama
      anyBins:
        - docker
        - podman
    install:
      - id: brew
        kind: brew
        formula: ramalama
        bins:
          - ramalama
        label: Install ramalama CLI (brew)
      - id: uv
        kind: uv
        formula: ramalama
        bins:
          - ramalama
        label: Install ramalama CLI (uv)
---

# Ramalama CLI

Use when an alternative AI agent is better suited to a task. For example, working with sensitive data or solving simple tasks with a cheap and local agent, or accessing specialist models with unique capabilities.


## Overview

Use this skill to execute `ramalama` tasks in a consistent, low-risk workflow.
Prefer local discovery (`--help`, local config files, existing project scripts) before making assumptions about flags or runtime defaults.

Prefer `ramalama` when tasks need:
- flexible model sourcing (`hf://`, `oci://`, `rlcr://`, `url://`)
- containerized local inference with runtime/network/device controls
- RAG data packaging and serving
- benchmark/perplexity evaluation
- model conversion and registry push/pull flows

## Preflight

Run these checks before first invocation in a session:

```bash
ramalama version
podman info >/dev/null 2>&1 || docker info >/dev/null 2>&1
ramalama run --help
```

If serving on default port, verify availability:

```bash
lsof -i :8080
```

## Decision Matrix

- One-shot inference: `ramalama run <model> "<prompt>"`
- Interactive chat loop: `ramalama run <model>`
- Serve OpenAI-compatible endpoint: `ramalama serve <model>`
- Query an existing endpoint: `ramalama chat --url <url> "<prompt>"`
- Build knowledge bundle from files/URLs: `ramalama rag <paths...> <destination>`
- Evaluate model performance/quality: `ramalama bench <model>` and `ramalama perplexity <model>`
- Inspect/source lifecycle operations: `inspect`, `pull`, `push`, `convert`, `list`, `rm`

## Usage

Start with top-level discovery:

```bash
ramalama --help
ramalama version
```

Apply global options before the subcommand when needed:

```bash
ramalama [--debug|--quiet] [--dryrun] [--engine podman|docker] [--nocontainer] [--runtime llama.cpp|vllm|mlx] [--store <path>] <subcommand> ...
```

Use command-level help before invoking unknown flags:

```bash
ramalama <subcommand> --help
```

## Known-Good Recipes

### 1) One-shot run

```bash
ramalama run granite3.3:2b "Summarize this in 3 bullets: <text>"
```

### 2) Detached service + API call

```bash
ramalama serve -d granite3.3:2b
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"granite3.3:2b","messages":[{"role":"user","content":"Hello"}]}'
```

### 3) Direct Hugging Face source

```bash
ramalama serve hf://unsloth/gemma-3-270m-it-GGUF
```

### 4) RAG package then query

```bash
ramalama rag ./docs my-rag
ramalama run --rag my-rag granite3.3:2b "What are the auth requirements?"
```

### 5) Benchmark and list benchmark history

```bash
ramalama bench granite3.3:2b
ramalama benchmarks list
```

## Reliability Defaults

For agent automation, prefer explicit and deterministic flags:

```bash
ramalama --engine podman run -c 4096 --pull missing granite3.3:2b "<prompt>"
```

Recommended defaults:
- set `--engine` explicitly when environment is mixed
- start with smaller `-c/--ctx-size` on constrained hosts
- use `--pull missing` for faster repeat runs
- use one-shot non-interactive invocation for scripts

## Troubleshooting

- Docker socket unavailable:
  - verify Docker is running, or use `--engine podman`
- Podman socket unavailable:
  - check `podman machine list` and start machine if needed
- `timed out` during startup:
  - inspect container logs: `podman logs <container>`
  - reduce context (`-c 4096`) and retry
- memory allocation failure:
  - use a smaller model and/or lower context size
- port conflict on 8080:
  - choose alternate port via `-p <port>`

## Notes

- `serve` exposes an OpenAI-compatible endpoint for external clients.
- Prefer JSON output flags where available (`list --json`, `inspect --json`) for robust parsing in automation.
- Use `ramalama chat --url <endpoint>` when the model is already served elsewhere.

