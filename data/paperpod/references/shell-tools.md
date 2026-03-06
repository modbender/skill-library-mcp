# Shell Tools Reference

The PaperPod sandbox includes 50+ pre-installed tools for code execution, data processing, and system operations.

## Available Tools

| Category | Tools |
|----------|-------|
| **Runtimes** | `python`, `python3`, `pip`, `node`, `npm`, `npx`, `bun` |
| **Version Control** | `git`, `gh` (GitHub CLI) |
| **HTTP & Networking** | `curl`, `httpie`, `jq`, `dig`, `ss` |
| **Search & Text** | `rg` (ripgrep), `find`, `sed`, `awk`, `tree` |
| **Media & Docs** | `ffmpeg`, `imagemagick`, `pandoc` |
| **Build & Data** | `make`, `sqlite3`, `tar`, `gzip`, `zip`, `unzip` |

## Running Shell Commands

### CLI (Recommended)

```bash
ppod exec "git clone https://github.com/user/repo"
ppod exec "pip install pandas && python train.py"
ppod exec "ffmpeg -i input.mp4 output.gif"
```

### HTTP

Use `language: "shell"` with `/execute`:

```bash
curl -X POST https://paperpod.dev/execute \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"code": "git clone https://github.com/user/repo", "language": "shell"}'
```

Or wrap in Python subprocess:

```python
import subprocess
result = subprocess.run("git --version", shell=True, capture_output=True, text=True)
print(result.stdout)
```

## Tool Examples

### ripgrep (rg)

```bash
# Search for pattern in files
ppod exec "rg --line-number 'def ' /workspace"

# Search with context
ppod exec "rg -C 2 'TODO' ."

# Search specific file types
ppod exec "rg --type py 'import'"
```

### jq

```bash
# Parse JSON
ppod exec "cat data.json | jq '.users[].name'"

# API response processing
ppod exec "curl -s https://api.example.com/data | jq '.results | length'"
```

### ffmpeg

```bash
# Generate audio tone
ppod exec "ffmpeg -f lavfi -i sine=frequency=440:duration=3 tone.wav"

# Convert video to GIF
ppod exec "ffmpeg -i video.mp4 -vf 'fps=10,scale=320:-1' output.gif"

# Extract audio
ppod exec "ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3"
```

### imagemagick

```bash
# Create gradient image
ppod exec "convert -size 200x100 gradient:blue-red gradient.png"

# Resize image
ppod exec "convert input.png -resize 50% output.png"

# Add text to image
ppod exec "convert input.png -pointsize 24 -annotate +10+30 'Hello' output.png"
```

### pandoc

```bash
# Markdown to HTML
ppod exec "pandoc doc.md -o doc.html"

# Convert between formats
ppod exec "pandoc input.docx -o output.md"
```

### sqlite3

```bash
# Query database
ppod exec "sqlite3 app.db 'SELECT * FROM users LIMIT 10'"

# Create table
ppod exec "sqlite3 app.db 'CREATE TABLE logs (id INTEGER PRIMARY KEY, msg TEXT)'"
```

### git

```bash
# Clone repository
ppod exec "git clone --depth 1 https://github.com/user/repo /tmp/repo"

# Get commit history
ppod exec "git log --oneline -20"
```

### Network tools

```bash
# DNS lookup
ppod exec "dig +short google.com"

# HTTP request
ppod exec "curl -s https://api.example.com | jq ."

# Check listening ports
ppod exec "ss -tlnp"
```

## Common Gotchas

| Issue | Solution |
|-------|----------|
| `pip` not found | Use `pip3` or `python3 -m pip` |
| Empty stdout | Check stderr — many tools output there |
| Command timeout | Add `--timeout 60000` to CLI |
| File not found | Use `/tmp/` or `/workspace/` paths |
| Permission denied | Files in `/tmp` and `/workspace` are writable |

## Runtime Tips

| Runtime | Best for | Speed |
|---------|----------|-------|
| `node` | Maximum compatibility | Normal |
| `bun` | TypeScript, speed | Faster |
| `python3` | Data science, scripting | Normal |

For TypeScript without build step:
```bash
ppod exec "bun run script.ts"
```
