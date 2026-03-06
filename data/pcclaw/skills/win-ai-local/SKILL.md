---
name: win-ai-local
description: Local AI inference via Ollama — run LLMs on-device, manage models, detect NPU/GPU/DirectML hardware, zero cloud dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "os": ["win32"],
        "requires": { "bins": ["ollama"] },
      },
  }
---

# win-ai-local

Run LLMs locally on Windows via Ollama. Manage models, generate text, chat, and detect AI hardware (NPU, GPU, DirectML, WinML).

Requires [Ollama](https://ollama.com) installed. Works on Windows 10/11.

## Detect AI Hardware

```powershell
powershell.exe -NoProfile -Command "
Write-Host '--- NPU ---'
Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'NPU|Neural|AI Boost|Movidius|VPU' } | ForEach-Object {
    Write-Host ('{0} [{1}]' -f $_.Name, $_.Status)
}
Write-Host ''
Write-Host '--- GPU ---'
Get-CimInstance Win32_VideoController | Where-Object { $_.Status -eq 'OK' } | ForEach-Object {
    Write-Host ('{0} (VRAM: {1} GB)' -f $_.Name, [math]::Round($_.AdapterRAM/1GB,1))
}
Write-Host ''
Write-Host '--- ML Runtimes ---'
$dml = Get-Item 'C:\Windows\System32\DirectML.dll' -ErrorAction SilentlyContinue
if ($dml) { Write-Host ('DirectML: {0}' -f $dml.VersionInfo.FileVersion) }
else { Write-Host 'DirectML: Not found' }
$winml = Get-Item 'C:\Windows\System32\windows.ai.machinelearning.dll' -ErrorAction SilentlyContinue
if ($winml) { Write-Host ('WinML: {0}' -f $winml.VersionInfo.FileVersion) }
else { Write-Host 'WinML: Not found' }
"
```

## Ollama Status

```powershell
powershell.exe -NoProfile -Command "
$proc = Get-Process -Name 'ollama*' -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host ('Ollama: Running (PID {0})' -f ($proc.Id -join ', '))
} else {
    Write-Host 'Ollama: Not running'
}
$ver = & ollama --version 2>&1
Write-Host $ver
"
```

## Start Ollama

```powershell
powershell.exe -NoProfile -Command "
Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden
Write-Host 'Ollama server starting...'
Start-Sleep -Seconds 2
$proc = Get-Process -Name 'ollama*' -ErrorAction SilentlyContinue
if ($proc) { Write-Host 'Ollama is running.' }
else { Write-Host 'Failed to start. Try running ollama serve manually.' }
"
```

## Stop Ollama

```powershell
powershell.exe -NoProfile -Command "
Stop-Process -Name 'ollama*' -Force -ErrorAction SilentlyContinue
Write-Host 'Ollama stopped.'
"
```

## List Models

```powershell
powershell.exe -NoProfile -Command "
ollama list
"
```

## Pull a Model

```powershell
powershell.exe -NoProfile -Command "
ollama pull MODEL_NAME
"
```

Replace `MODEL_NAME` with the model to download (e.g., `gemma3:4B`, `llama3.2:3b`, `phi4-mini`, `qwen2.5:7b`).

Recommended models for AIPC (8-32 GB RAM):

| Model | Size | Good for |
|-------|------|----------|
| `gemma3:4B` | 3.3 GB | General, fast |
| `phi4-mini` | 2.5 GB | Reasoning, compact |
| `llama3.2:3b` | 2.0 GB | General, lightweight |
| `qwen2.5:7b` | 4.7 GB | Multilingual (Chinese) |
| `deepseek-r1:8b` | 4.9 GB | Coding, reasoning |

## Delete a Model

```powershell
powershell.exe -NoProfile -Command "
ollama rm MODEL_NAME
"
```

## Show Model Info

```powershell
powershell.exe -NoProfile -Command "
ollama show MODEL_NAME
"
```

## Generate Text

Single prompt, single response (no conversation):

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$body = @{
    model = 'MODEL_NAME'
    prompt = 'PROMPT_TEXT'
    stream = $false
} | ConvertTo-Json -Depth 3
$response = Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method POST -Body $body -ContentType 'application/json'
Write-Host $response.response
Write-Host ''
Write-Host ('Tokens: {0} | Duration: {1:N1}s | Speed: {2:N1} tok/s' -f $response.eval_count, ($response.total_duration / 1e9), ($response.eval_count / ($response.eval_duration / 1e9)))
"
```

- `MODEL_NAME`: model to use (e.g., `gemma3:4B`)
- `PROMPT_TEXT`: the prompt to send

### With System Prompt

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$body = @{
    model = 'MODEL_NAME'
    prompt = 'PROMPT_TEXT'
    system = 'SYSTEM_PROMPT'
    stream = $false
} | ConvertTo-Json -Depth 3
$response = Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method POST -Body $body -ContentType 'application/json'
Write-Host $response.response
"
```

### With Parameters (Temperature, Max Tokens)

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$body = @{
    model = 'MODEL_NAME'
    prompt = 'PROMPT_TEXT'
    stream = $false
    options = @{
        temperature = 0.7
        num_predict = 500
    }
} | ConvertTo-Json -Depth 3
$response = Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method POST -Body $body -ContentType 'application/json'
Write-Host $response.response
"
```

- `temperature`: 0.0 (deterministic) to 2.0 (creative), default 0.8
- `num_predict`: max tokens to generate, default 128

## Chat (Multi-Turn)

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$body = @{
    model = 'MODEL_NAME'
    messages = @(
        @{ role = 'system'; content = 'SYSTEM_PROMPT' }
        @{ role = 'user'; content = 'USER_MESSAGE' }
    )
    stream = $false
} | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Uri 'http://localhost:11434/api/chat' -Method POST -Body $body -ContentType 'application/json'
Write-Host $response.message.content
Write-Host ''
Write-Host ('Tokens: {0} | Speed: {1:N1} tok/s' -f $response.eval_count, ($response.eval_count / ($response.eval_duration / 1e9)))
"
```

### Multi-Turn Conversation

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$body = @{
    model = 'MODEL_NAME'
    messages = @(
        @{ role = 'user'; content = 'FIRST_MESSAGE' }
        @{ role = 'assistant'; content = 'FIRST_RESPONSE' }
        @{ role = 'user'; content = 'SECOND_MESSAGE' }
    )
    stream = $false
} | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Uri 'http://localhost:11434/api/chat' -Method POST -Body $body -ContentType 'application/json'
Write-Host $response.message.content
"
```

## Embeddings

Generate text embeddings for semantic search or RAG:

```powershell
powershell.exe -NoProfile -Command "
$body = @{
    model = 'MODEL_NAME'
    input = 'TEXT_TO_EMBED'
} | ConvertTo-Json -Depth 3
$response = Invoke-RestMethod -Uri 'http://localhost:11434/api/embed' -Method POST -Body $body -ContentType 'application/json'
Write-Host ('Dimensions: {0}' -f $response.embeddings[0].Count)
Write-Host ('First 5: {0}' -f ($response.embeddings[0][0..4] -join ', '))
"
```

Use an embedding model like `nomic-embed-text` or `mxbai-embed-large`.

## Common Workflows

### Quick local inference (no API key needed)

```
1. win-ai-local: check Ollama status (start if needed)
2. win-ai-local: generate text with a prompt
3. Use the result in your workflow
```

### Translate text locally

```
1. win-ai-local: generate with system prompt "Translate to English"
2. No data leaves the machine — fully private
```

### Summarize a document privately

```
1. Read the document content
2. win-ai-local: generate with prompt "Summarize: {content}"
3. Confidential data stays local
```

### Agent delegates to local LLM

```
1. Main agent identifies a sub-task suitable for local inference
2. win-ai-local: chat with appropriate system prompt
3. Main agent uses the response
4. Saves API costs for simple tasks
```

### On-device RAG pipeline

```
1. win-ai-local: generate embeddings for documents
2. Store embeddings locally
3. On query, embed the query and find similar docs
4. win-ai-local: chat with retrieved context
```

## Notes

- Requires [Ollama](https://ollama.com) installed and running (`ollama serve`).
- Models are stored at `%USERPROFILE%\.ollama\models\`.
- Ollama API runs at `http://localhost:11434` — fully local, no data leaves the machine.
- GPU acceleration: Ollama auto-detects and uses available GPU (Intel Arc, NVIDIA, AMD).
- NPU acceleration: not yet supported by Ollama directly. Use OpenVINO or WinML for NPU inference.
- For Chinese text, use `qwen2.5` models which have strong multilingual support.
- Inference speed depends on model size and hardware. On Intel Arc 140V: ~5-10 tok/s for 4B models.
- `stream = $false` returns the full response at once. Set to `$true` for streaming (requires different parsing).
- Max context window varies by model (typically 2K-128K tokens). Check with `ollama show MODEL_NAME`.
- For production use, consider running Ollama as a Windows service for auto-start.
