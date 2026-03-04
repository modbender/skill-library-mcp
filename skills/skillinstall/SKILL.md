---
name: skill-installer
description: Install OpenClaw skills from clawhub.ai ZIP files with automatic detection, validation, and Gateway updates. Supports file search, duplicate checking, and interactive selection when multiple files are found.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "python3",
              "kind": "system",
              "bins": ["python3"],
              "label": "Python 3.6+ (required)",
            },
          ],
      },
  }
---

# Skill Installer

Install OpenClaw skills from clawhub.ai ZIP files with automatic detection, validation, and Gateway updates.

## Features

- **Automatic Detection**: Finds OpenClaw installation location automatically
- **File Search**: Search for ZIP files in current directory when filename is not specified
- **Duplicate Check**: Verifies if a skill is already installed before proceeding
- **Interactive Selection**: Prompts user to choose when multiple matching files are found
- **Validation**: Validates skill structure (SKILL.md, _meta.json)
- **Gateway Update**: Automatically restarts Gateway to make new skills available
- **Progress Feedback**: Detailed status messages throughout the installation process

## Usage

### Basic Installation

```bash
# Install from a specific ZIP file
python3 scripts/skill_install.py my-skill.zip

# Search for ZIP files in current directory
python3 scripts/skill_install.py

# List all installed skills
python3 scripts/skill_install.py --list

# Show help
python3 scripts/skill_install.py --help
```

### Workflow

1. **File Detection**:
   - If filename is provided: Use that file directly
   - If no filename: Search for *.zip files in current directory
   - If multiple files found: Display list and ask user to choose

2. **Validation**:
   - Check if OpenClaw is installed
   - Validate ZIP file structure
   - Verify SKILL.md and _meta.json exist

3. **Duplicate Check**:
   - Extract skill name from SKILL.md
   - Check if skill already exists in skills directory
   - Prompt for confirmation if duplicate found

4. **Installation**:
   - Extract ZIP file to skills directory
   - Verify extracted files
   - Restart OpenClaw Gateway

5. **Completion**:
   - Display success message
   - Show skill path
   - Confirm Gateway restart

## File Structure

The script expects skills to have the following structure:

```
skill-name.zip
├── SKILL.md          # Required: Skill metadata and documentation
├── _meta.json        # Required: Additional metadata
├── scripts/          # Optional: Python/Node scripts
│   └── *.py/*.mjs
├── references/       # Optional: Reference documentation
└── README.md         # Optional: Extended documentation
```

## Examples

### Install from Current Directory

```bash
# List all ZIP files in current directory
python3 scripts/skill_install.py

# Output:
# Found 3 ZIP files:
# 1. github-skill.zip
# 2. weather-skill.zip
# 3. notion-skill.zip
#
# Select a file (1-3) or 'q' to quit: 1
#
# Installing: github-skill.zip
# ...
```

### Install Specific File

```bash
python3 scripts/skill_install.py github-skill.zip

# Output:
# ============================================================
# 📦 OpenClaw Skill Installer
# ============================================================
#
# 🔍 正在搜索 OpenClaw 安装位置...
# ✅ 找到 OpenClaw: /home/user/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw
#
# 📂 正在解析 ZIP 文件...
# ✅ 找到 SKILL.md
# ✅ Skill 名称: github
# ✅ Skill 描述: GitHub operations via gh CLI
#
# 🔍 检查是否已安装...
# ℹ️  Skill 'github' 未安装
#
# 📦 正在安装 skill...
# ✅ 安装成功！
#
# 🔄 正在重启 Gateway...
# ✅ Gateway 已重启
#
# 🎉 安装完成！
# Skill 路径: /home/user/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/github
#
# 现在可以在 OpenClaw 中使用 'github' skill 了！
```

### List Installed Skills

```bash
python3 scripts/skill_install.py --list

# Output:
# ============================================================
# 📋 已安装的 Skills
# ============================================================
#
# 1. github
#    📁 文件夹: github
#    📝 描述: GitHub operations via gh CLI
#    📍 路径: /home/user/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/github
#
# 2. weather
#    📁 文件夹: weather
#    📝 描述: Get current weather and forecasts
#    📍 路径: /home/user/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/weather
#
# ...
```

## Requirements

- Python 3.6 or higher
- OpenClaw installed (via npm or nvm)
- Sufficient permissions to write to OpenClaw skills directory

## Error Handling

### Common Errors

**Error**: `❌ 未找到 OpenClaw 安装位置`
- **Solution**: Install OpenClaw first using `npm install -g openclaw`

**Error**: `❌ ZIP 文件不存在`
- **Solution**: Check the filename and path

**Error**: `❌ ZIP 文件不包含 SKILL.md`
- **Solution**: Ensure the ZIP file is a valid skill from clawhub.ai

**Error**: `⚠️  Skill 已存在`
- **Solution**: Confirm if you want to overwrite or use a different skill

**Error**: `❌ Gateway 重启失败`
- **Solution**: Manually restart Gateway using `openclaw daemon restart`

## Advanced Usage

### Custom OpenClaw Path

If the script cannot find OpenClaw automatically, you can modify the `OPENCLAW_PATH` variable in the script:

```python
OPENCLAW_PATH = "/custom/path/to/openclaw"
```

### Skip Gateway Restart

To restart Gateway manually, comment out the restart call:

```python
# restart_gateway(openclaw_root)
```

## Troubleshooting

### Permission Denied

If you encounter permission errors:

```bash
# Fix permissions
chmod 755 ~/.nvm/versions/node/*/lib/node_modules/openclaw/skills
```

### Skill Not Appearing in OpenClaw

After installation, if the skill doesn't appear:

1. Restart Gateway manually:
   ```bash
   openclaw daemon restart
   ```

2. Check OpenClaw logs:
   ```bash
   openclaw logs --follow
   ```

3. Verify skill structure:
   ```bash
   ls -la ~/.nvm/versions/node/*/lib/node_modules/openclaw/skills/your-skill/
   ```

## Changelog

### Version 1.0.0 (2025-02-26)

**Initial Release**

Features:
- Automatic OpenClaw detection
- ZIP file installation from clawhub.ai
- File search and interactive selection
- Duplicate checking
- Gateway auto-restart
- Progress feedback
- List installed skills command

Enhancements:
- Support for multiple ZIP file selection
- Detailed error messages
- Skill validation (SKILL.md, _meta.json)
- Cross-platform compatibility (Linux, macOS, Windows)

Bug Fixes:
- Fixed path resolution on different Node.js installations
- Improved ZIP extraction handling
- Better error recovery

Known Issues:
- May require manual Gateway restart on some systems
- Limited to single skill installation per run

## Notes

- The script searches for OpenClaw in common locations:
  - `~/.nvm/versions/node/*/lib/node_modules/openclaw`
  - `/usr/local/lib/node_modules/openclaw`
  - `/opt/node_modules/openclaw`

- Skills are installed to:
  - `<OpenClaw Root>/skills/<skill-name>/`

- Gateway restart requires systemd support (Linux) or manual restart (other platforms)

- For development or testing, use `--list` to verify skills before installation
