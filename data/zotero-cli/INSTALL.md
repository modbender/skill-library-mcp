# zotero-cli Installation Guide

Comprehensive installation instructions for zotero-cli, with special considerations for PEP 668-compliant systems.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method的选择](#method的选择)
3. [Installation by Method](#installation-by-method)
4. [Post-Installation Steps](#post-installation-steps)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)

---

## Prerequisites

### Required Software

- **Python 3.7+** - For running zotero-cli
- **pip** or **pipx** - For package installation
- **Zotero account** - For accessing your library (https://www.zotero.org)

### Optional Software

- **pandoc** - For note format conversion (highly recommended)
- **text editor** - vim, nano, emacs, VS Code, etc.

### Check Your System

Check if Python 3 is installed:
```bash
python3 --version
```

Check if pip is installed:
```bash
pip3 --version
```

Check if pipx is installed:
```bash
pipx --version
```

---

## Method的选择

### What is PEP 668?

[PEP 668](https://peps.python.org/pep-0668/) is a Python Enhancement Proposal that prevents installing Python packages to system directories using pip. This design is intended to:
- Prevent conflict between system packages and Python packages
- Maintain system stability
- Improve package management

### Which Distributions Follow PEP 668?

- **Debian 11+ (Bullseye)**
- **Ubuntu 23.04+**
- **Fedora 34+**
- **Arch Linux**
- **RHEL 9+**
- **Alpine Linux** (edge)

### Recommended Installation Method

| System Type | Recommended Method | Why? |
|-------------|-------------------|------|
| **PEP 668-compliant** | **pipx** | Isolated environments, no system conflicts |
| **Non-PEP 668** | pip or pipx | Either works, pip is simpler |
| **Development** | pip (editable) | For testing and contributing |
| **Container/Docker** | pip (no-user) | Already isolated |

---

## Installation by Method

### Method 1: pipx Installation (Recommended for PEP 668 systems)

pipx installs Python applications in isolated virtual environments, preventing conflicts with system packages.

#### Step 1: Install pipx

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install pipx -y
pipx ensurepath
```

**Arch Linux:**
```bash
sudo pacman -S pipx
pipx ensurepath
```

**Fedora:**
```bash
sudo dnf install pipx
pipx ensurepath
```

**RHEL/CentOS:**
```bash
sudo yum install pipx
pipx ensurepath
```

**Using pip (any system):**
```bash
# Using system pip (if allowed)
sudo pip install pipx
# OR using user pip
pip install --user pipx
pipx ensurepath
```

**Note:** After `pipx ensurepath`, you may need to log out and back in, or run:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

#### Step 2: Install zotero-cli

```bash
pipx install zotero-cli
```

#### Step 3: Verify Installation

```bash
zotcli --version
# OR
zotero-cli --version
```

You should see version information without errors.

#### Step 4: Configure zotero-cli

```bash
zotcli configure
```

Follow the prompts to enter your Zotero userID and generate an API key.

### Method 2: pip Installation (Generic)

For systems without PEP 668 restrictions or when using virtual environments.

#### Step 1: Install zotero-cli

**Using user installation (recommended):**
```bash
pip install --user zotero-cli
```

Ensure `~/.local/bin` is in your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Using virtual environment (best practice):**
```bash
python3 -m venv ~/.venvs/zotero-cli
source ~/.venvs/zotero-cli/bin/activate
pip install zotero-cli

# To use zotero-cli later
source ~/.venvs/zotero-cli/bin/activate
zotcli configure
```

**System-wide installation (not recommended on PEP 668 systems):**
```bash
# This will fail on PEP 668-compliant systems
sudo pip install zotero-cli

# To force install (not recommended, potential for system conflicts)
sudo python3 -m pip install --break-system-packages zotero-cli
```

**⚠️ Warning:** Using `--break-system-packages` is dangerous and can damage your system's Python installation. Use pipx or virtual environments instead.

#### Step 2: Verify Installation

```bash
zotcli --version
```

#### Step 3: Configure zotero-cli

```bash
zotcli configure
```

### Method 3: Development Installation

For developers or to test the latest features.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/jbaiter/zotero-cli.git
cd zotero-cli
```

#### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install in Editable Mode

```bash
pip install -e .
```

This installs zotero-cli in "editable" mode, so changes to the code are immediately available.

#### Step 4: Verify Installation

```bash
zotcli --version
```

### Method 4: Install from Git Repository Using pip

Direct installation from GitHub (latest development version):

```bash
# Using pipx (recommended)
pipx install git+git://github.com/jbaiter/zotero-cli.git@master

# Using pip with user installation
pip install --user git+git://github.com/jbaiter/zotero-cli.git@master

# Using virtual environment
python3 -m venv venv
source venv/bin/activate
pip install git+git://github.com/jbaiter/zotero-cli.git@master
```

### Method 5: Using System Package Manager

Some distributions provide zotero-cli in their repositories.

**Alpine Linux:**
```bash
# Check if available first
apk search zotero

# If found
sudo apk add py3-zotero-cli
```

**Arch Linux (AUR):**
```bash
# Clone from AUR (if available)
git clone https://aur.archlinux.org/python-zotero-cli.git
cd python-zotero-cli
makepkg -si
```

**Note:** Always check your distribution's repository first as package names may vary.

---

## Post-Installation Steps

### 1. Configuration

Run the initial configuration:
```bash
zotcli configure
```

This will:
1. Prompt for your Zotero userID
   - Find it at https://www.zotero.org/settings/keys
   - Click "Create new private key"
2. Prompt to generate an API key
3. Set up the configuration file at `~/.config/zotcli/config.ini`

### 2. Set Your Preferred Editor

Set the `VISUAL` environment variable for note editing:

```bash
# For current session
export VISUAL=nano  # or vim, emacs, code, etc.

# For permanent configuration (bash)
echo 'export VISUAL=nano' >> ~/.bashrc
source ~/.bashrc

# For permanent configuration (zsh)
echo 'export VISUAL=nano' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install Pandoc (Optional but Recommended)

For note format conversion:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install pandoc -y
```

**Arch Linux:**
```bash
sudo pacman -S pandoc
```

**Fedora:**
```bash
sudo dnf install pandoc
```

**macOS:**
```bash
brew install pandoc
```

**Windows:**
Download from https://pandoc.org/installing.html

### 4. Test Installation

Test all basic functions:

```bash
# Test command availability
zotcli --help

# Try your first search (after configuration)
zotcli query "test"
```

### 5. Configure Note Format (Optional)

Edit `~/.config/zotcli/config.ini` to set your preferred format:

```ini
[note_format]
note_format = markdown  # Options: markdown, rst, latex, html, etc.
```

---

## Troubleshooting

### Problem: Permission Denied on pip Installation

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError:
[Errno 13] Permission denied
```

**Cause (PEP 668):**
You're trying to install to system directories on a PEP 668-compliant system.

**Solutions:**

1. **Use pipx (recommended):**
```bash
pipx install zotero-cli
```

2. **Use user installation:**
```bash
pip install --user zotero-cli
```

3. **Use virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install zotero-cli
```

4. **Force system installation (⚠️ dangerous):**
```bash
sudo python3 -m pip install --break-system-packages zotero-cli
```
**Warning:** This is not recommended and can damage your system.

### Problem: Command Not Found After Installation

**Symptoms:**
```
zotcli: command not found
```

**Solutions:**

1. **Ensure pipx PATH is set:**
```bash
pipx ensurepath
source ~/.bashrc  # or ~/.zshrc
```

2. **Add to PATH manually:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

3. **Check where it's installed:**
```bash
python3 -m pip show zotero-cli
# Look at "Location:" field
```

### Problem: Authentication Errors

**Symptoms:**
```
Error: Could not authenticate with Zotero API
```

**Solutions:**

1. **Re-run configuration:**
```bash
zotcli configure
```

2. **Verify credentials:**
   - Check userID at https://www.zotero.org/settings/keys
   - Regenerate API key if needed
   - Ensure API key has "Read" and "Write" permissions

3. **Check network connection:**
```bash
ping www.zotero.org
```

### Problem: Python Version Too Old

**Symptoms:**
```
ERROR: Package requires a different Python version
```

**Solutions:**

1. **Check Python version:**
```bash
python3 --version
```

2. **Install Python 3.7+:**

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python
```

**Fedora:**
```bash
sudo dnf install python3
```

3. **Use pyenv (advanced):**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11

# Set as default
pyenv global 3.11

# Install zotero-cli with this Python
~/.pyenv/versions/3.11/bin/pip install zotero-cli
```

### Problem: pipx Not Available

**Symptoms:**
```
pipx: command not found
```

**Solutions:**

1. **Install pipx with pip:**
```bash
pip install --user pipx
export PATH="$HOME/.local/bin:$PATH"
```

2. **Install via package manager:**
```bash
# Debian/Ubuntu
sudo apt install pipx

# Arch Linux
sudo pacman -S pipx

# Fedora
sudo dnf install pipx
```

### Problem: Virtual Environment Issues

**Symptoms:**
```
ERROR: virtualenv is not installed
```

**Solutions:**

1. **Install venv:**
```bash
# Debian/Ubuntu
sudo apt install python3.11-venv

# Arch Linux
sudo pacman -S python-virtualenv

# Fedora
sudo dnf install python3-virtualenv
```

2. **Use Python's built-in venv:**
```bash
python3 -m venv venv
```

### Problem: Configuration File Not Found

**Symptoms:**
```
ERROR: Configuration file not found
```

**Solutions:**

1. **Create configuration directory:**
```bash
mkdir -p ~/.config/zotcli
```

2. **Re-run configuration:**
```bash
zotcli configure
```

3. **Check configuration location:**
```bash
ls -la ~/.config/zotcli/
```

### Problem: Editor Not Launching

**Symptoms:**
Note editing doesn't open an editor.

**Solutions:**

1. **Set VISUAL environment variable:**
```bash
export VISUAL=nano  # or your preferred editor
```

2. **Make editor available in PATH:**
```bash
which vim nano emacs
```

3. **Test editor manually:**
```bash
vim test.txt  # or nano, emacs, etc.
```

---

## Uninstallation

### Using pipx

```bash
pipx uninstall zotero-cli
```

### Using pip

```bash
pip uninstall zotero-cli
```

### Remove Configuration Files

```bash
# Remove configuration directory
rm -rf ~/.config/zotcli

# Remove virtual environment (if used)
rm -rf ~/.venvs/zotero-cli

# Remove cloned repository (if installed from source)
rm -rf ~/zotero-cli
```

### Remove PATH Entries

Edit your shell configuration and remove the PATH entry you added:

**For .bashrc:**
```bash
nano ~/.bashrc
# Remove the line: export PATH="$HOME/.local/bin:$PATH"
```

**For .zshrc:**
```bash
nano ~/.zshrc
# Remove the line: export PATH="$HOME/.local/bin:$PATH"
```

---

## Platform-Specific Notes

### Debian/Ubuntu

- Follow PEP 668 enforcement (Debian 11+, Ubuntu 23.04+)
- Use pipx for installation
- Install dependencies via apt:

```bash
sudo apt update
sudo apt install python3 python3-pip pipx pandoc
```

### Arch Linux

- pipx is available in official repositories
- AUR packages may be available

```bash
sudo pacman -S python python-pip pipx pandoc
```

### Fedora

- PEP 668 compliant (Fedora 34+)
- Use pipx or dnf

```bash
sudo dnf install python3 python3-pip pipx pandoc
```

### RHEL/CentOS/Rocky Linux

- May need EPEL repositories
- Use pipx or pip with user installation

```bash
sudo yum install python3 python3-pip epel-release
sudo yum install pipx
```

### Alpine Linux

- Use py3-* packages
- Check availability in repositories

```bash
apk add python3 py3-pip py3-pandoc
```

### macOS

- Use Homebrew for pipx and pandoc
- Works with both pip and pipx

```bash
brew install python3 pipx pandoc
```

### Windows

- Use pipx (available via pip)
- Use PowerShell or Git Bash
- Install pandoc from official website

```powershell
# PowerShell
pip install pipx
pipx ensurepath
pipx install zotero-cli
```

---

## Security Best Practices

1. **Don't use `sudo pip install`** - Use pipx or user installation instead
2. **Don't use `--break-system-packages`** - This bypasses system protections
3. **Use virtual environments** - For development projects
4. **Keep packages updated** - Run update commands regularly
5. **Verify API key permissions** - Only grant necessary access
6. **Secure configuration files** - Set appropriate permissions:

```bash
chmod 600 ~/.config/zotcli/config.ini
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check the project README:** https://github.com/jbaiter/zotero-cli
2. **Search existing issues:** https://github.com/jbaiter/zotero-cli/issues
3. **Create a new issue** with detailed information about your problem
4. **Consult the documentation** in SKILL.md for usage information

---

## Summary of Recommendations

| Scenario | Recommended Method |
|----------|-------------------|
| **Most PEP 668 systems** | `pipx install zotero-cli` |
| **Non-PEP 668 systems** | `pip install --user zotero-cli` |
| **Development/Testing** | Editable install with venv |
| **Latest features** | `pipx install git+git://github.com/jbaiter/zotero-cli.git@master` |
| **Minimal footprint** | pipx with auto-upgrade |

---

**Remember:** Always use pipx or virtual environments on PEP 668-compliant systems to avoid conflicts and maintain system stability.
