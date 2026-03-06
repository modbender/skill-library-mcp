---
name: last30days
description: "Research any topic from the last 30 days. Sources: X (Twitter), YouTube transcripts, web search. Generates expert briefings and copy-paste prompts using Gemini."
argument-hint: 'last30 AI agents, last30 marketing automation'
metadata: {"version": "2.1.0", "clawdbot":{"emoji":"🔍","requires":{"bins":["python3","node","yt-dlp"],"env":["AUTH_TOKEN","CT0","BRAVE_API_KEY"]}}, "original_repo": "https://github.com/mvanhorn/last30days-skill", "author": "mvanhorn", "license": "MIT"}
---

> **Credit:** This skill is based on [last30days](https://github.com/mvanhorn/last30days-skill) by [@mvanhorn](https://x.com/mvanhorn). The original skill researches topics across Reddit, X, YouTube, and web. This version adds Gemini synthesis for briefings and prompts.
>
> Original skill: [github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)

# last30days v2.1

Research any topic across X (Twitter), YouTube, and web. Find what's actually being discussed, recommended, and debated right now.

## Setup

```bash
# Environment (should already be set)
export AUTH_TOKEN=your_x_auth_token
export CT0=your_x_ct0_token  
export BRAVE_API_KEY=your_brave_key

# Config
mkdir -p ~/.config/last30days
cat > ~/.config/last30days/.env << 'EOF'
BRAVE_API_KEY=your_key_here
EOF
```

## Usage

```bash
# Quick research (faster, fewer sources)
python3 {baseDir}/scripts/last30days.py "AI agents" --quick

# Full research
python3 {baseDir}/scripts/last30days.py "AI agents" 

# Output formats
python3 {baseDir}/scripts/last30days.py "topic" --emit=json    # JSON for parsing
python3 {baseDir}/scripts/last30days.py "topic" --emit=compact  # Human readable
python3 {baseDir}/scripts/last30days.py "topic" --emit=md       # Full report
```

## Output for AI Synthesis

The `--emit=json` flag outputs structured JSON that can be fed to Gemini for:
- Expert briefing generation
- Copy-paste ready prompts
- Trend analysis

## Sources

| Source | Auth | Notes |
|--------|------|-------|
| X/Twitter | Cookies | Uses bird CLI with existing AUTH_TOKEN/CT0 |
| YouTube | None | Requires yt-dlp for transcripts |
| Web | Brave API | Requires BRAVE_API_KEY |

## Synthesis

This skill researches and returns raw data. For AI-generated briefings and prompts, pipe the JSON output to Gemini:

```bash
python3 {baseDir}/scripts/last30days.py "topic" --quick --emit=json | python3 -c "
import json, sys, os
import urllib.request, urllib.parse

data = json.load(sys.stdin)
prompt = f'Synthesize this research into an expert briefing and 3 copy-paste prompts:\\n{json.dumps(data)}'

body = json.dumps({
    'contents': [{'parts': [{'text': prompt}]}],
    'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 2048}
})

req = urllib.request.Request(
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + os.environ.get('GEMINI_API_KEY'),
    data=body.encode(),
    headers={'Content-Type': 'application/json'}
)
print(json.load(urllib.request.urlopen(req))['candidates'][0]['content']['parts'][0]['text'])
"
```

## Attribution

- **Original Author:** [Mike Van Horn](https://x.com/mvanhorn) ([mvanhorn](https://github.com/mvanhorn))
- **Original Repository:** [github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)
- **License:** MIT (per original)
- **Contributors:** Thanks to [@steipete](https://x.com/steipete) for yt-dlp + summarize inspiration

This skill extends the original with Gemini synthesis for automated briefings.
