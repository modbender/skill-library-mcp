# Prepper Skill Setup Guide

## Prerequisites

This skill requires ollama to be installed and the dolphin-llama3 model to be available locally.

## Installation

### 1. Install Ollama

**macOS:**
```bash
# Download from https://ollama.ai
# Or via Homebrew:
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download installer from https://ollama.ai

### 2. Pull the Model

Once ollama is installed, pull the dolphin-llama3 model:

```bash
ollama pull dolphin-llama3
```

This downloads the model (~7GB). You only need to do this once.

### 3. Verify Installation

Check that the model is available:

```bash
ollama list | grep dolphin-llama3
```

You should see output like:
```
dolphin-llama3:latest    7.4 GB   ...
```

## Running Ollama

### Option A: Foreground (Development/Testing)
```bash
ollama serve
```

This starts ollama on `localhost:11434` and keeps the terminal attached. Stop with Ctrl+C.

### Option B: Background (Production)

**macOS/Linux (systemd):**
```bash
# Ollama installs itself as a service
# Start: 
sudo systemctl start ollama

# Status:
sudo systemctl status ollama

# Stop:
sudo systemctl stop ollama
```

**macOS (launchd):**
```bash
# Ollama installs a LaunchAgent
# It auto-starts on login
# Check status:
launchctl list | grep ollama
```

## Verify Connectivity

Test that ollama is reachable:

```bash
curl http://localhost:11434/api/tags
```

You should get a JSON response listing available models.

## Troubleshooting

### "Connection refused" error
- Is ollama running? Check with: `ps aux | grep ollama`
- If not, start it: `ollama serve` or `sudo systemctl start ollama`

### "Model not found" error
- Pull the model: `ollama pull dolphin-llama3`
- Verify it exists: `ollama list`

### Port already in use
- Ollama uses port 11434 by default
- Check what's using it: `lsof -i :11434`
- Change ollama port via `OLLAMA_HOST` environment variable if needed

## API Details

- **Base URL**: `http://localhost:11434`
- **Endpoint**: `/api/generate`
- **Authentication**: None required (local use)
- **Model**: `dolphin-llama3`

See ollama docs for API reference: https://github.com/jmorganca/ollama/blob/main/docs/api.md
