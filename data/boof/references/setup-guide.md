# Boof — Setup Guide

## Prerequisites

- **macOS** with Apple Silicon (M1/M2/M3/M4) or Linux
- **Python 3.11-3.13** (3.14 has compatibility issues with Pillow/PyTorch)
- **bun** (for QMD installation) — install from https://bun.sh

## Step 1: Install Marker (PDF → Markdown converter)

Marker runs locally on your machine using ML models. No API keys needed. First run downloads ~2GB of models.

```bash
# Create isolated Python environment (don't pollute system Python)
python3.13 -m venv ~/.openclaw/tools/marker-env

# Install marker-pdf + missing dependency
~/.openclaw/tools/marker-env/bin/pip install marker-pdf psutil

# Verify installation
~/.openclaw/tools/marker-env/bin/marker_single --help
```

**macOS note:** If Python 3.13 isn't installed: `brew install python@3.13`

**First run:** Marker downloads OCR and layout detection models (~2GB) on first use. This is a one-time cost. Subsequent runs are fast.

### Optional: Create convenience wrapper

```bash
mkdir -p ~/.openclaw/tools/bin
cat > ~/.openclaw/tools/bin/marker << 'EOF'
#!/bin/bash
~/.openclaw/tools/marker-env/bin/marker "$@"
EOF
chmod +x ~/.openclaw/tools/bin/marker
```

## Step 2: Install QMD (Local RAG indexing + retrieval)

QMD (Quick Markdown Database) provides local semantic search over markdown files. It uses local GGUF models — no API keys, no cloud.

```bash
# Install via bun (NOT npm — the npm package is a placeholder)
bun install -g https://github.com/tobi/qmd

# Verify installation
~/.bun/bin/qmd status
```

**First run:** QMD downloads embedding and reranker models (~1-2GB total) on first query. One-time cost.

### Configure QMD for OpenClaw

If using with OpenClaw's memory system, set the QMD path in your config (`~/.openclaw/openclaw.json`):

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      command: "~/.bun/bin/qmd",  // Full path to qmd binary
      limits: {
        timeoutMs: 30000  // First query needs time for model downloads
      }
    }
  }
}
```

## Step 3: Install the Boof Skill

### For OpenClaw users:

```bash
# Copy the skill to your skills directory
cp -r path/to/boof ~/.openclaw/workspace/skills/boof

# Or install from ClewHub (when published):
# openclaw skills install boof
```

### Standalone usage:

The `boof.sh` script works independently of OpenClaw:

```bash
# Set environment variables (or use defaults)
export MARKER_ENV=~/.openclaw/tools/marker-env
export QMD_BIN=~/.bun/bin/qmd

# Run directly
./scripts/boof.sh /path/to/document.pdf
```

## Verify Everything Works

```bash
# Test with any PDF
./scripts/boof.sh ~/Downloads/some-paper.pdf

# Query the indexed content
~/.bun/bin/qmd query "what is the main finding?" -c some-paper

# You should see relevant snippets from the document
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: psutil` | `~/.openclaw/tools/marker-env/bin/pip install psutil` |
| `Failed to build Pillow` | Use Python 3.13, not 3.14: `brew install python@3.13` |
| `qmd: command not found` | Use full path: `~/.bun/bin/qmd`, or add `~/.bun/bin` to PATH |
| QMD queries timeout | Set `timeoutMs: 30000` — first run downloads models |
| Marker hangs on first run | It's downloading models (~2GB). Wait 2-5 minutes. |
| `npm install -g qmd` installs wrong package | The npm `qmd` package is a placeholder. Must use: `bun install -g https://github.com/tobi/qmd` |

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8GB | 16GB+ |
| Disk | 5GB (models) | 10GB+ |
| CPU | Any (ARM or x86) | Apple Silicon (uses MPS acceleration) |
| GPU | Not required | Apple Silicon GPU accelerates Marker |
