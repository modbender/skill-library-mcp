# Skill Installer

A convenient tool for installing OpenClaw skills from clawhub.ai ZIP files directly from the command line.

## Quick Start

```bash
# Install a skill
python3 scripts/skill_install.py my-skill.zip

# Or search for ZIP files in current directory
python3 scripts/skill_install.py
```

## Features

- 🚀 **One-Click Installation**: Install skills with a single command
- 🔍 **Smart File Search**: Automatically finds ZIP files when filename is not specified
- ✅ **Validation**: Ensures skill structure is correct before installation
- 🔄 **Auto Update**: Automatically restarts Gateway to make new skills available
- 📋 **List Skills**: View all installed skills with descriptions

## Installation

This skill is included in the skill-installer package. To use it:

1. Ensure Python 3.6+ is installed
2. Ensure OpenClaw is installed (`npm install -g openclaw`)
3. Run the script from the skill directory

## Usage Examples

### Install a Specific Skill

```bash
python3 scripts/skill_install.py github-skill.zip
```

### Interactive Selection

```bash
python3 scripts/skill_install.py
```

The script will display all ZIP files in the current directory and prompt you to select one.

### List All Installed Skills

```bash
python3 scripts/skill_install.py --list
```

## How It Works

1. **Detects OpenClaw**: Automatically finds your OpenClaw installation
2. **Validates ZIP**: Checks if the ZIP file contains valid skill structure
3. **Checks Duplicates**: Prevents overwriting existing skills
4. **Installs**: Extracts skill to the correct location
5. **Updates Gateway**: Restarts Gateway to make the skill available

## Requirements

- Python 3.6 or higher
- OpenClaw installed via npm or nvm
- Write permissions to OpenClaw skills directory

## Troubleshooting

### "OpenClaw not found"

Make sure OpenClaw is installed:
```bash
npm install -g openclaw
```

### "ZIP file not found"

Check that the filename and path are correct. Use `--list` to see installed skills.

### "Skill already exists"

The skill is already installed. You can manually remove it if you want to reinstall:
```bash
rm -rf ~/.nvm/versions/node/*/lib/node_modules/openclaw/skills/skill-name
```

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues or questions, please visit the OpenClaw community or check the documentation at clawhub.ai.
