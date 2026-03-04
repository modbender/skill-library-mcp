---
name: cloudinary
description: "Cloudinary — manage images/videos, upload, transform, and search assets via REST API"
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "☁️", "requires": {"env": ["CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET", "CLOUDINARY_CLOUD_NAME"]}, "primaryEnv": "CLOUDINARY_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# ☁️ Cloudinary

Cloudinary — manage images/videos, upload, transform, and search assets via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `CLOUDINARY_API_KEY` | ✅ | API key |
| `CLOUDINARY_API_SECRET` | ✅ | API secret |
| `CLOUDINARY_CLOUD_NAME` | ✅ | Cloud name |

## Quick Start

```bash
# List resources
python3 {{baseDir}}/scripts/cloudinary.py resources --prefix <value> --max_results <value>

# Get resource
python3 {{baseDir}}/scripts/cloudinary.py resource-get public_id <value>

# Upload asset
python3 {{baseDir}}/scripts/cloudinary.py upload --file <value> --folder <value> --public_id <value>

# Delete asset
python3 {{baseDir}}/scripts/cloudinary.py destroy --public_id <value>

# Rename asset
python3 {{baseDir}}/scripts/cloudinary.py rename --from_public_id <value> --to_public_id <value>

# Search assets
python3 {{baseDir}}/scripts/cloudinary.py search --expression <value> --max_results <value>

# List tags
python3 {{baseDir}}/scripts/cloudinary.py tags --prefix <value>

# List root folders
python3 {{baseDir}}/scripts/cloudinary.py folders
```

## All Commands

| Command | Description |
|---------|-------------|
| `resources` | List resources |
| `resource-get` | Get resource |
| `upload` | Upload asset |
| `destroy` | Delete asset |
| `rename` | Rename asset |
| `search` | Search assets |
| `tags` | List tags |
| `folders` | List root folders |
| `folder-create` | Create folder |
| `folder-delete` | Delete folder |
| `transformations` | List transformations |
| `usage` | Get usage stats |
| `presets` | List upload presets |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/cloudinary.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/cloudinary.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
