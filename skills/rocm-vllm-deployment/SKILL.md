---
name: rocm_vllm_deployment
description: Production-ready vLLM deployment on AMD ROCm GPUs. Combines environment auto-check, model parameter detection, Docker Compose deployment, health verification, and functional testing with comprehensive logging and security best practices.
version: 1.0.0
author: Alex He <heye_dev@163.com>
timeout: 3600s
platform: Linux (AMD GPU ROCm)
tags:
  - LLM
  - Deployment
  - AMD
  - ROCm
  - Docker Compose
  - vLLM
  - Automation
  - EnvCheck
  - AutoRepair
---

# ROCm vLLM Deployment Skill

Production-ready automation for deploying vLLM inference services on AMD ROCm GPUs using Docker Compose.

## Features

- Environment Auto-Check - Detects and repairs missing dependencies
- Model Parameter Detection - Auto-reads config.json for optimal settings
- VRAM Estimation - Calculates memory requirements before deployment
- Secure Token Handling - Never writes tokens to compose files
- **Structured Output** - All logs and test results saved per-model
- **Deployment Reports** - Human-readable summary for each deployment
- Health Verification - Automated health checks and functional tests
- Troubleshooting Guide - Common issues and solutions

## Environment Prerequisites

**Recommended (for production):** Add to `~/.bash_profile`:

```bash
# HuggingFace authentication token (required for gated models)
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Model cache directory (optional)
export HF_HOME="$HOME/models"

# Apply changes
source ~/.bash_profile
```

**Not required for testing:** The skill will proceed without these set:
- **HF_TOKEN**: Optional — public models work without it; gated models fail at download with clear error
- **HF_HOME**: Optional — defaults to `/root/.cache/huggingface/hub`

### Environment Variable Detection

**Priority Order:**
1. **Explicit parameter** (highest) — Provided in task/request (e.g., `hf_token: "xxx"`)
2. **Environment variable** — Already set in shell or from parent process
3. **~/.bash_profile** — Source to load variables
4. **Default value** (lowest) — HF_HOME defaults to `/root/.cache/huggingface/hub`

| Variable | Required | If Missing |
|----------|----------|------------|
| `HF_TOKEN` | **Conditional** | Continue without token (public models work; gated models fail at download with clear error) |
| `HF_HOME` | No | **Warning + Default** — Use `/root/.cache/huggingface/hub` |

**Philosophy:** Fail fast for configuration errors, fail at download time for authentication errors.

---

## Helper Scripts

**Location:** `<skill-dir>/scripts/`

### check-env.sh

Validate and load environment variables before deployment.

**Usage:**
```bash
# Basic check (HF_TOKEN optional, HF_HOME optional with default)
./scripts/check-env.sh

# Strict mode (HF_HOME required, fails if not set)
./scripts/check-env.sh --strict

# Quiet mode (minimal output, for automation)
./scripts/check-env.sh --quiet

# Test with environment variables
HF_TOKEN="hf_xxx" HF_HOME="/models" ./scripts/check-env.sh
```

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | Environment check completed (variables loaded or defaulted) |
| 2 | Critical error (e.g., cannot source ~/.bash_profile) |

**Note:** This script is optional. You can also directly run `source ~/.bash_profile`.

---

### generate-report.sh

Generate human-readable deployment report after successful deployment.

**Usage:**
```bash
./scripts/generate-report.sh <model-id> <container-name> <port> <status> [model-load-time] [memory-used]

# Example:
./scripts/generate-report.sh \
  "Qwen-Qwen3-0.6B" \
  "vllm-qwen3-0-6b" \
  "8001" \
  "✅ Success" \
  "3.6" \
  "1.2"
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `model-id` | Yes | Model ID (with `/` replaced by `-`) |
| `container-name` | Yes | Docker container name |
| `port` | Yes | Host port for API endpoint |
| `status` | Yes | Deployment status (e.g., "✅ Success") |
| `model-load-time` | No | Model loading time in seconds |
| `memory-used` | No | Memory consumption in GiB |

**Output:** `$HOME/vllm-compose/<model-id>/DEPLOYMENT_REPORT.md`

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | Report generated successfully |
| 1 | Missing required parameters |
| 2 | Output directory not found |

**Integration:** This script is automatically called in **Phase 7** of the deployment workflow.

---

## Input Schema

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| model_id | String | Yes | - | HuggingFace model ID |
| docker_image | String | No | rocm/vllm-dev:nightly | vLLM Docker image |
| tensor_parallel_size | Integer | No | 1 | Number of GPUs |
| port | Integer | No | 9999 | API server port |
| hf_home | String | No | `${HF_HOME}` or `/root/.cache/huggingface/hub` | Model cache directory |
| hf_token | Secret | Conditional | `${HF_TOKEN}` | HuggingFace token (optional for public models, required for gated models) |
| max_model_len | Integer | No | Auto-detect | Maximum sequence length |
| gpu_memory_utilization | Float | No | 0.85 | GPU memory utilization |
| auto_install | Boolean | No | true | Auto-install dependencies |
| log_level | String | No | INFO | Logging verbosity |

## Output Structure

**All deployment artifacts MUST be saved to:**
```
$HOME/vllm-compose/<model-id-slash-to-dash>/
```

Convert model ID to directory name by replacing `/` with `-`:
- `openai/gpt-oss-20b` → `$HOME/vllm-compose/openai-gpt-oss-20b/`
- `Qwen/Qwen3-Coder-Next-FP8` → `$HOME/vllm-compose/Qwen-Qwen3-Coder-Next-FP8/`

**Per-model directory structure:**
```
$HOME/vllm-compose/<model-id>/
├── deployment.log          # Full deployment logs (stdout + stderr)
├── test-results.json       # Functional test results (JSON format)
├── docker-compose.yml      # Generated Docker Compose file
├── .env                    # HF_TOKEN environment (chmod 600, optional)
└── DEPLOYMENT_REPORT.md    # Human-readable deployment summary
```

**File requirements:**
- `deployment.log` — Capture ALL container logs during deployment
- `test-results.json` — Save API response from functional test request
- `DEPLOYMENT_REPORT.md` — Generated in Phase 7
- All three files MUST exist before marking deployment as complete

## Execution Workflow

### Phase 0: Environment Check & Auto-Repair

**Step 0.1: Load Environment Variables**

```bash
# Source ~/.bash_profile to load HF_HOME and HF_TOKEN
source ~/.bash_profile

# If HF_HOME is not defined, it defaults to /root/.cache/huggingface/hub
```

If HF_HOME is not defined in ~/.bash_profile, it defaults to `/root/.cache/huggingface/hub`.

**Step 0.2: Create Output Directory**
- Create: `$HOME/vllm-compose/<model-id>/`

**Step 0.3: Initialize Logging**
- All output → `$HOME/vllm-compose/<model-id>/deployment.log`

**Step 0.4: System Checks**
- Detect OS and package manager
- Check Python, pip, huggingface_hub
- Check Docker, docker compose
- Check ROCm tools (rocm-smi/amd-smi)
- Check GPU access (/dev/kfd, /dev/dri)
- Check disk space (20GB minimum)

### Phase 1: Model Download

**Use HF_HOME from Phase 0 (environment variable or default):**

```bash
# Download model to HF_HOME
huggingface-cli download <model_id> --local-dir "$HF_HOME/hub/models--<org>--<model>"

# Or use snapshot_download via Python:
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='<model_id>', cache_dir='$HF_HOME')"
```

**Authentication Handling:**

| Scenario | Behavior |
|----------|----------|
| Public model + no token | ✅ Download succeeds |
| Public model + token provided | ✅ Download succeeds |
| Gated model + no token | ❌ Download fails with "authentication required" error |
| Gated model + invalid token | ❌ Download fails with "invalid token" error |
| Gated model + valid token | ✅ Download succeeds |

**On Authentication Failure:**
```bash
echo "ERROR: Model download failed - authentication required"
echo "This model requires a valid HF_TOKEN."
echo ""
echo "Please add to ~/.bash_profile:"
echo "  export HF_TOKEN=\"hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\""
echo "Then run: source ~/.bash_profile"
exit 1
```

- Locate model path in HF cache: `$HF_HOME/hub/models--<org>--<model-name>/`
- Log download progress to `deployment.log`

### Phase 2: Model Parameter Detection
- Read config.json from model
- Auto-detect: max_model_len, hidden_size, num_attention_heads, num_hidden_layers, vocab_size, dtype
- Validate TP size divides attention heads
- Estimate VRAM requirement

### Phase 3: Docker Compose Configuration

**Generate files in output directory:**

- **docker-compose.yml** → `$HOME/vllm-compose/<model-id>/docker-compose.yml`
  - Mount HF_HOME as volume (read-only for models)
  - NO hardcoded tokens in compose file

- **.env** → `$HOME/vllm-compose/<model-id>/.env` (optional)
  - Contains: `HF_TOKEN=<value>`
  - Permissions: `chmod 600`
  - Only created if user explicitly requests persistent token storage

**Volume mount example:**
```yaml
volumes:
  - ${HF_HOME}:/root/.cache/huggingface/hub:ro
  - /dev/kfd:/dev/kfd
  - /dev/dri:/dev/dri
```

**Important:** Docker Compose reads `${HF_HOME}` from the host environment at runtime. Before running docker compose, source ~/.bash_profile: `source ~/.bash_profile`


### Phase 4: Container Launch

**Important:** Before deploying, pull the latest image to ensure updates:
```bash
docker pull rocm/vllm-dev:nightly
```

**Note:** Default port is 9999. Before running docker compose, check if port is available: `ss -tlnp | grep :<port>`. If port is in use, specify a different port in docker-compose.yml.

- Pass HF_TOKEN at runtime: HF_TOKEN=$HF_TOKEN docker compose up -d
- Wait for container initialization

### Phase 5: Health Verification
- Check container status
- Test /health endpoint
- Test /v1/models endpoint

### Phase 6: Functional Testing
- Run completion test via `/v1/chat/completions` API
- **Save response to:** `$HOME/vllm-compose/<model-id>/test-results.json`
- Verify response contains valid completion
- **Log deployment complete** → Append to `deployment.log`
- **Deployment is complete only when both files exist:**
  - `deployment.log`
  - `test-results.json`

### Phase 7: Deployment Report

**Generate human-readable deployment report using the helper script.**

**Step 7.1: Extract Deployment Metrics**

```bash
# Parse deployment.log for metrics
MODEL_LOAD_TIME=$(grep -o "model loading took [0-9.]* seconds" deployment.log | grep -o '[0-9.]*' || echo "N/A")
MEMORY_USED=$(grep -o "took [0-9.]* GiB memory" deployment.log | grep -o '[0-9.]*' || echo "N/A")
```

**Step 7.2: Generate Report**

```bash
# Execute the report generation script
<skill-dir>/scripts/generate-report.sh \
  "<model-id>" \
  "<container-name>" \
  "<port>" \
  "<status>" \
  "$MODEL_LOAD_TIME" \
  "$MEMORY_USED"

# Example:
./scripts/generate-report.sh \
  "Qwen-Qwen3-0.6B" \
  "vllm-qwen3-0-6b" \
  "8001" \
  "✅ Success" \
  "3.6" \
  "1.2"
```

**Output:** `$HOME/vllm-compose/<model-id>/DEPLOYMENT_REPORT.md`

**Report Contents:**
- Output structure verification (file checklist)
- Deployment summary table (health, test, metrics)
- Test results (request/response preview)
- Environment configuration
- Quick commands for operations

**Completion Criteria:**
- `DEPLOYMENT_REPORT.md` exists in output directory
- Report contains all required sections
- All file checks show ✅

## Security Best Practices

1. **Never commit tokens to version control** — Add `.env` to `.gitignore`
2. **Use .env files with chmod 600** — Restrict access to owner only
3. **Mask tokens in logs** — Show only first 10 chars: `${TOKEN:0:10}...`
4. **Pass tokens at runtime** — `HF_TOKEN=$HF_TOKEN docker compose up -d`
5. **Store tokens in ~/.bash_profile** — For production environments, set `HF_TOKEN` in user's shell config
6. **Set token for gated models** — HF_TOKEN is validated at download time; set in ~/.bash_profile for production

## Troubleshooting

### Environment Variables

| Issue | Solution |
|-------|----------|
| `HF_TOKEN not set` | Add `export HF_TOKEN="hf_xxx"` to `~/.bash_profile`, then `source ~/.bash_profile`. Or provide via parameter. |
| `HF_HOME not set` | defaults to `/root/.cache/huggingface/hub`. For production, add `export HF_HOME="/path"` to `~/.bash_profile`. |
| `~/.bash_profile not found` | Create `~/.bash_profile` and add environment variables. |
| `Changes not taking effect` | Run `source ~/.bash_profile` or restart terminal. |
| `HF_TOKEN provided but download still fails` | Token may be invalid or lack access to the model. Verify token at https://huggingface.co/settings/tokens |

### Model Download

| Issue | Solution |
|-------|----------|
| `Authentication required` (gated model) | Set `HF_TOKEN` in `~/.bash_profile` or provide via parameter. Ensure token has access to the model. |
| `Model not found` | Verify model ID is correct (case-sensitive). Check model exists on HuggingFace. |
| `Download timeout` | Check network connection. Large models may take time. |

### Deployment

| Issue | Solution |
|-------|----------|
| hf CLI not found | `pip install huggingface_hub` |
| Docker Compose fails | Use `docker compose` (no hyphen) |
| GPU access fails | Add user to `render` group: `sudo usermod -aG render $USER` |
| Port in use | Change `port` parameter |
| OOM | Reduce `gpu_memory_utilization` |

## Cleanup

```bash
cd $HOME/vllm-compose/<model-id>
docker compose down
```

## Status Check

**Check deployment status and logs:**

```bash
# View deployment directory
ls -la $HOME/vllm-compose/<model-id>/

# View live logs
tail -f $HOME/vllm-compose/<model-id>/deployment.log

# View test results
cat $HOME/vllm-compose/<model-id>/test-results.json

# Check container status
docker ps | grep <model-id>

# Verify environment variables
echo "HF_TOKEN: ${HF_TOKEN:0:10}..."
echo "HF_HOME: $HF_HOME"
```

## Quick Start (Production)

**Step 1: Add environment variables to ~/.bash_profile**

```bash
# Required: HuggingFace token
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Recommended: Custom model storage path (production)
export HF_HOME="/data/models/huggingface"

# Apply changes
source ~/.bash_profile
```

**Step 2: Verify environment is ready**

```bash
# Source ~/.bash_profile to load variables
source ~/.bash_profile

# Expected output:
# === Environment Ready ===
# Summary:
#   HF_TOKEN: hf_xxxxxx...
#   HF_HOME:  /data/models/huggingface
```

**Step 3: Run deployment**

```bash
# The skill will automatically:
# 1. Source ~/.bash_profile to load HF_HOME and HF_TOKEN
# 2. Use HF_TOKEN and HF_HOME from environment (or ~/.bash_profile, or defaults)
# 3. Proceed without token for public models
# 4. Fail at download time with clear error if gated model requires token
```

## Version History

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial release |

