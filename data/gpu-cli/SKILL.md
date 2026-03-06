---
name: gpu-cli
description: Run ML training, LLM inference, and ComfyUI workflows on remote NVIDIA GPUs (A100, H100, RTX 4090). Cloud GPU compute with smart file sync — prefix any command with 'gpu' to run it remotely.
version: 0.14.0
metadata:
  openclaw:
    requires:
      bins:
        - gpu
    install:
      brew: gpu-cli/tap/gpu
      script: curl -fsSL https://gpu-cli.sh/install | sh
    homepage: https://gpu-cli.sh
    tags:
      - gpu
      - machine-learning
      - cloud-compute
      - remote-execution
      - llm
      - comfyui
      - nvidia
      - cuda
      - training
      - inference
      - runpod
      - pytorch
      - stable-diffusion
---

# GPU CLI

GPU CLI runs local commands on remote NVIDIA GPUs by prefixing with `gpu`. It provisions a pod, syncs your code, streams logs, and syncs outputs back: `uv run python train.py` becomes `gpu run uv run python train.py`.

## Quick diagnostics

```bash
gpu doctor --json       # Check if setup is healthy (daemon, auth, provider keys)
gpu status --json       # See running pods and costs
gpu inventory --json    # See available GPUs and pricing
```

## Command families

### Getting started

| Command | Purpose |
|---|---|
| `gpu login` | Browser-based authentication |
| `gpu logout [-y]` | Remove session |
| `gpu init [--gpu-type T] [--force]` | Initialize project config |
| `gpu upgrade` | Open subscription upgrade page |

### Running code

| Command | Purpose |
|---|---|
| `gpu run <command>` | Execute on remote GPU (main command) |
| `gpu run -d <command>` | Run detached (background) |
| `gpu run -a <job_id>` | Reattach to running job |
| `gpu run --cancel <job_id>` | Cancel a running job |
| `gpu status [--json]` | Show project status, pods, costs |
| `gpu logs [-j JOB] [-f] [--tail N] [--json]` | View job output |
| `gpu attach <job_id>` | Reattach to job output stream |
| `gpu stop [POD_ID] [-y]` | Stop active pod |

Key `gpu run` flags: `--gpu-type`, `--gpu-count <1-8>`, `--min-vram`, `--rebuild`, `-o/--output`, `--no-output`, `--sync`, `-p/--publish <PORT>`, `-e <KEY=VALUE>`, `-i/--interactive`.

### GPU inventory

| Command | Purpose |
|---|---|
| `gpu inventory [--available] [--min-vram N] [--max-price P] [--json]` | List GPUs with pricing |

### Volumes

| Command | Purpose |
|---|---|
| `gpu volume list [--detailed] [--json]` | List network volumes |
| `gpu volume create [--name N] [--size GB] [--datacenter DC]` | Create volume |
| `gpu volume delete <VOL> [--force]` | Delete volume |
| `gpu volume extend <VOL> --size <GB>` | Increase size |
| `gpu volume set-global <VOL>` | Set default volume |
| `gpu volume status [--volume V] [--json]` | Volume usage |
| `gpu volume migrate <VOL> --to <DC>` | Migrate to datacenter |
| `gpu volume sync <SRC> <DEST>` | Sync between volumes |

### Vault (encrypted storage)

| Command | Purpose |
|---|---|
| `gpu vault list [--json]` | List encrypted output files |
| `gpu vault export <PATH> <DEST>` | Export decrypted file |
| `gpu vault stats [--json]` | Storage usage stats |

### Configuration

| Command | Purpose |
|---|---|
| `gpu config show [--json]` | Show merged config |
| `gpu config validate` | Validate against schema |
| `gpu config schema` | Print JSON schema |
| `gpu config set <KEY> <VALUE>` | Set global config option |
| `gpu config get <KEY>` | Get global config value |

### Authentication

| Command | Purpose |
|---|---|
| `gpu auth login [--profile P]` | Authenticate with cloud provider |
| `gpu auth logout` | Remove credentials |
| `gpu auth status` | Show auth status |
| `gpu auth add <HUB>` | Add hub credentials (hf, civitai) |
| `gpu auth remove <HUB>` | Remove hub credentials |
| `gpu auth hubs` | List configured hubs |

### Organizations

| Command | Purpose |
|---|---|
| `gpu org list` | List organizations |
| `gpu org create <NAME>` | Create organization |
| `gpu org switch [SLUG]` | Set active org context |
| `gpu org invite <EMAIL>` | Invite member |
| `gpu org service-account create --name N` | Create service token |
| `gpu org service-account list` | List service accounts |
| `gpu org service-account revoke <ID>` | Revoke token |

### LLM inference

| Command | Purpose |
|---|---|
| `gpu llm run [--ollama\|--vllm] [--model M] [-y]` | Launch LLM inference |
| `gpu llm info [MODEL] [--url URL] [--json]` | Show model info |

### ComfyUI workflows

| Command | Purpose |
|---|---|
| `gpu comfyui list [--json]` | Browse available workflows |
| `gpu comfyui info <WORKFLOW> [--json]` | Show workflow details |
| `gpu comfyui validate <WORKFLOW> [--json]` | Pre-flight checks |
| `gpu comfyui run <WORKFLOW>` | Run workflow on GPU |
| `gpu comfyui generate "<PROMPT>"` | Text-to-image generation |
| `gpu comfyui stop [WORKFLOW] [--all]` | Stop ComfyUI pod |

### Notebooks

| Command | Purpose |
|---|---|
| `gpu notebook [FILE] [--run] [--new NAME]` | Run Marimo notebook on GPU |

Alias: `gpu nb`

### Serverless endpoints

| Command | Purpose |
|---|---|
| `gpu serverless deploy [--template T] [--json]` | Deploy endpoint |
| `gpu serverless status [ENDPOINT] [--json]` | Endpoint status |
| `gpu serverless logs [ENDPOINT]` | View request logs |
| `gpu serverless list [--json]` | List all endpoints |
| `gpu serverless delete [ENDPOINT]` | Delete endpoint |
| `gpu serverless warm [--cpu\|--gpu]` | Pre-warm endpoint |

### Templates

| Command | Purpose |
|---|---|
| `gpu template list [--json]` | Browse official templates |
| `gpu template clear-cache` | Clear cached templates |

### Daemon control

| Command | Purpose |
|---|---|
| `gpu daemon status [--json]` | Show daemon health |
| `gpu daemon start` | Start daemon |
| `gpu daemon stop` | Stop daemon |
| `gpu daemon restart` | Restart daemon |
| `gpu daemon logs [-f] [-n N]` | View daemon logs |

### Tools and utilities

| Command | Purpose |
|---|---|
| `gpu dashboard` | Interactive TUI for pods and jobs |
| `gpu doctor [--json]` | Diagnostic checks |
| `gpu agent-docs` | Print agent reference to stdout |
| `gpu update [--check]` | Update CLI |
| `gpu changelog [VERSION]` | View release notes |
| `gpu issue ["desc"]` | Report issue |
| `gpu desktop` | Desktop app management |
| `gpu support` | Open community Discord |

## Common workflows

1. **Setup**: `gpu login` then `gpu init`
2. **Run job**: `gpu run python train.py --epochs 10`
3. **With specific GPU**: `gpu run --gpu-type "RTX 4090" python train.py`
4. **Detached job**: `gpu run -d python long_training.py` then `gpu status --json`
5. **Check status**: `gpu status --json`
6. **View logs**: `gpu logs --json`
7. **Stop pods**: `gpu stop -y`
8. **LLM inference**: `gpu llm run --ollama --model llama3 -y`
9. **ComfyUI**: `gpu comfyui run flux_schnell`
10. **Diagnose issues**: `gpu doctor --json`

`gpu run` is pod-reuse oriented: after a command completes, the next `gpu run` reuses the existing pod until you `gpu stop` or cooldown ends.

## JSON output

Most commands support `--json` for machine-readable output. Structured data goes to stdout; human-oriented status and progress messages go to stderr.

Commands with `--json`: `status`, `logs`, `doctor`, `inventory`, `config show`, `daemon status`, `volume list`, `volume status`, `vault list`, `vault stats`, `comfyui list`, `comfyui info`, `comfyui validate`, `serverless deploy`, `serverless status`, `serverless list`, `template list`, `llm info`.

## Exit codes

| Code | Meaning | Recovery |
|---|---|---|
| `0` | Success | Proceed |
| `1` | General error | Read stderr |
| `2` | Usage error | Fix command syntax |
| `10` | Auth required | `gpu auth login` |
| `11` | Quota exceeded | `gpu upgrade` or wait |
| `12` | Not found | Check resource ID |
| `13` | Daemon unavailable | `gpu daemon start`, retry |
| `14` | Timeout | Retry |
| `15` | Cancelled | Re-run if needed |
| `130` | Interrupted | Re-run if needed |

## Configuration

- Project config: `gpu.toml`, `gpu.jsonc`, or `pyproject.toml [tool.gpu]`
- Global config: `~/.gpu-cli/config.toml` (via `gpu config set/get`)
- Sync model: `.gitignore` controls upload; `outputs` patterns control download
- Secrets and credentials must stay in the OS keychain, never plaintext project files
- CI env vars: `GPU_RUNPOD_API_KEY`, `GPU_SSH_PRIVATE_KEY`, `GPU_SSH_PUBLIC_KEY`

## References

- Project generation and task setup: `references/create.md`
- Debugging and common failures: `references/debug.md`
- Config schema and field examples: `references/config.md`
- Cost and GPU selection guidance: `references/optimize.md`
- Persistent storage and volumes: `references/volumes.md`
