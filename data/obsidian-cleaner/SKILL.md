---
name: obsidian-cleaner
description: Automatically clean up loose images and attachments in Obsidian vault root, moving them to the Attachments folder. Trigger when user says "clean obsidian", "clean attachments", or "整理附件".
---

# Obsidian Attachment Cleaner

A skill that automatically finds and moves loose images/attachments from your Obsidian vault root to the designated Attachments folder.

## When to Use

Trigger when user says:
- "Clean Obsidian"
- "Clean attachments"
- "整理附件"
- "Move images to attachments"
- "Obsidian 清理"

## Features

- **Auto-discovery**: Finds loose files (`.png`, `.jpg`, `.gif`, `.jpeg`, `.webp`, `.pdf`, `.docx`)
- **Safe move**: Moves files to `Attachments/` folder (creates if not exists)
- **Dry run**: Preview what will be moved before executing
- **Detailed report**: Shows exactly what was moved and where

## Usage

### Quick Clean (Auto-detect)

```bash
python obsidian_cleaner.py
```

### Dry Run (Preview Only)

```bash
python obsidian_cleaner.py --dry-run
```

### Specify Vault Path

```bash
python obsidian_cleaner.py --vault /path/to/Obsidian/Vault
```

### Custom Attachments Folder

```bash
python obsidian_cleaner.py --attachments "My Attachments"
```

## How It Works

1. Scans Obsidian vault root for loose attachment files
2. Checks if Attachments folder exists (creates if missing)
3. Moves each file to the Attachments folder
4. Reports what was moved and any errors

## Configuration

Default vault path: `~/Documents/Obsidian Vault`

Default attachments folder: `Attachments/`

## Example Output

```
🔍 Scanning /Users/skin/Documents/Obsidian Vault for loose attachments...

📁 Found 3 files:
  ├── screenshot_20240101.png
  ├── photo.jpg
  └── diagram.gif

📦 Moving to Attachments/...

✅ Success!
  ├── screenshot_20240101.png → Attachments/screenshot_20240101.png
  ├── photo.jpg → Attachments/photo.jpg
  └── diagram.gif → Attachments/diagram.gif

🎉 3 files moved. Vault is now clean!
```

## Integration

Add to your `HEARTBEAT.md` or daily routine:

```markdown
## Daily Obsidian Cleanup (Optional)

If you notice loose images in your vault root, run:
- "Clean Obsidian" - Automatically organize attachments
```

## Notes

- Only moves files, doesn't delete anything
- Won't overwrite existing files (skips with warning)
- Case-insensitive file extension matching
- Safe to run multiple times
