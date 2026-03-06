# AutoClipper

Automatic video clip and highlight generator for OpenClaw.

## Quick Start

```bash
# Install dependencies
brew install ffmpeg

# Configure watch folder in config.json
# Edit watchFolder to point to your media folder

# Run once
python3 scripts/auto_clipper.py run

# Enable cron scheduling
# Edit config.json: cron.enabled = true
# Add to crontab: 0 * * * * /path/to/auto-clipper/scripts/run.sh
```

## Requirements

- **ffmpeg** - Video processing
- **Python 3.8+** - Runtime
- **OpenClaw** - With Agent Swarm (agent-swarm skill) configured

## Configuration

Edit `config.json` to customize:

- `watchFolder` - Where to look for new videos
- `outputFolder` - Where to save clips
- `fileExtensions` - File types to process
- `clipSettings` - Output format and quality

## Features

- 🎬 Automatic clip extraction from media folders
- 🧠 Agent Swarm integration for intelligent clip planning  
- ⏰ Cron-ready for scheduled automation
- 📁 Organized output with date-based folders
- 🔔 Optional notifications when clips are ready