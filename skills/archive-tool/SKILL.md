---
name: archive-tool
description: "Extract and create archive files (zip, rar, 7z, tar, gz). Use
  when: (1) Extracting zip/rar/7z files, (2) Creating zip archives, (3) Viewing
  archive contents, (4) Batch extracting files."
---


# Archive Skill

Extract and create archive files. Uses Python stdlib for zip/tar/gz, falls back to system tools for rar/7z.

## Install

```bash
# Optional (for rar/7z support)
brew install unar p7zip
```

## Features

- ✅ Extract: zip, tar, tar.gz, tgz, gz
- ⚠️ Extract: rar, 7z (if tools installed)
- ✅ Create: zip, tar, tar.gz
- ✅ List: View archive contents

## Usage

### Extract

```bash
python archive.py extract file.zip
python archive.py extract file.zip -o ./output
python archive.py extract file.rar --password secret
python archive.py extract "*.zip"  # Batch
```

### Create

```bash
python archive.py create output.zip ./folder
python archive.py create output.tar ./folder
python archive.py create output.tar.gz ./folder
```

### List

```bash
python archive.py list file.zip
```

## Examples

```bash
# Extract to current folder
python archive.py extract archive.zip

# Extract to specific folder
python archive.py extract archive.zip -o ./extracted

# Create zip from folder
python archive.py create myfiles.zip ./myfolder

# List contents
python archive.py list archive.zip
```

## Supported Formats

| Format | Extract | Create | Stdlib |
|--------|---------|--------|--------|
| zip | ✅ | ✅ | ✅ |
| tar | ✅ | ✅ | ✅ |
| tar.gz / tgz | ✅ | ✅ | ✅ |
| gz | ✅ | ❌ | ✅ |
| rar | ⚠️ | ❌ | - |
| 7z | ⚠️ | ❌ | - |

⚠️ = requires system tools (unar, p7zip)
