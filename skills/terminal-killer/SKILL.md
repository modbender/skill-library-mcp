---
name: terminal-killer
description: Intelligent shell command detector and executor for OpenClaw. Automatically identifies terminal commands (system builtins, $PATH executables, history matches, command patterns) and executes directly without LLM overhead. Cross-platform support (macOS/Linux/Windows). Use when user input appears to be a shell command to skip AI processing and run immediately.
author: Cosper
contact: cosperypf@163.com
---

# Terminal Killer

🚀 Smart command router that executes shell commands directly, bypassing LLM for instant terminal operations.

## Quick Start

Terminal Killer automatically activates when user input matches command patterns. No special syntax needed — just type commands naturally:

```
ls -la              # → Direct exec
git status          # → Direct exec  
npm install         # → Direct exec
"help me code"      # → LLM handles normally
```

## How It Works

### Detection Pipeline

```
User Input → Command Detector → Decision
                                      ├── Command → exec (direct)
                                      └── Task → LLM (normal)
```

### Environment Loading

Terminal Killer automatically loads your shell environment before executing commands:

1. **Detects your shell** (zsh, bash, etc.)
2. **Sources init files** (`~/.zshrc`, `~/.bash_profile`, `~/.bashrc`, etc.)
3. **Inherits full PATH** - including custom paths like Android SDK, Homebrew, etc.
4. **Preserves environment variables** - all your `export VAR=value` settings

This ensures commands like `adb`, `kubectl`, `docker`, etc. work exactly as they do in your terminal!

### Detection Rules (in order)

1. **System Builtins** - Check against OS-specific builtin commands
2. **PATH Executables** - Scan `$PATH` for matching executables
3. **History Match** - Compare against recent shell history
4. **Command Pattern** - Heuristic analysis (operators, paths, etc.)
5. **Confidence Score** - Combine signals for final decision

## Detection Details

### 1. System Builtins

Checks input against known builtin commands for the current OS:

| macOS/Linux | Windows (PowerShell) | Windows (CMD) |
|-------------|---------------------|---------------|
| `cd`, `pwd`, `ls` | `cd`, `pwd`, `ls` | `cd`, `dir`, `cls` |
| `echo`, `cat` | `echo`, `cat` | `echo`, `type` |
| `mkdir`, `rm`, `cp` | `mkdir`, `rm`, `cp` | `mkdir`, `del`, `copy` |
| `grep`, `find` | `grep`, `find` | `findstr` |
| `git`, `npm`, `node` | `git`, `npm`, `node` | `git`, `npm`, `node` |

See `references/builtins/` for complete lists.

### 2. PATH Executable Check

Scans `$PATH` directories to verify if the first word is an executable:

```bash
# Uses `which` (Unix) or `Get-Command` (PowerShell)
which <command>    # Returns path if exists
```

### 3. History Matching

Compares input against recent shell history (`~/.zsh_history`, `~/.bash_history`, PowerShell history):

- Exact match → High confidence
- Similar prefix → Medium confidence
- No match → Continue checking

### 4. Command Pattern Analysis

Heuristic scoring based on command characteristics:

| Pattern | Score | Example |
|---------|-------|---------|
| Starts with known command | +3 | `git status` |
| Contains shell operators | +2 | `ls | grep` |
| Contains path references | +2 | `cd ~/projects` |
| Contains flags/args | +1 | `npm install --save` |
| Contains `$` variables | +2 | `echo $HOME` |
| Contains redirection | +2 | `cat file > out` |
| Looks like natural language | -3 | "please help me" |
| Contains question marks | -2 | "how do I...?" |

### 5. Confidence Threshold

```
Score >= 5  → EXECUTE (high confidence command)
Score 3-4   → ASK (uncertain, confirm with user)
Score < 3   → LLM (likely a task/request)
```

## Usage

### Automatic Activation

Terminal Killer triggers automatically when:
- User input starts with a verb-like word
- Input is short (< 20 words typically)
- No question words (what, how, why, etc.)

### Interactive Commands

Terminal Killer automatically detects and handles interactive shell commands:

**Detected Patterns:**
- `adb shell` - Opens new terminal with adb shell
- `ssh user@host` - Opens SSH session in new window
- `docker exec -it container bash` - Opens container shell
- `mysql -u root -p` - Opens MySQL client
- `python`, `node`, `bash` - Opens REPL in new window

**Behavior:**
- ✅ Automatically opens new Terminal window (macOS)
- ✅ Loads your full shell environment (~/.zshrc, etc.)
- ✅ Keeps main session free for other tasks

### Manual Override

Force command execution:
```
!ls -la          # Force exec even if uncertain
```

Force LLM handling:
```
?? explain git   # Force LLM even if looks like command
```

## Safety Features

### Dangerous Command Detection

Automatically flags potentially dangerous operations:

- `rm -rf /` or similar destructive patterns
- `sudo` commands (requires explicit approval)
- `dd`, `mkfs`, `chmod 777`
- Network operations to suspicious hosts
- Commands modifying system files

### Approval Workflow

```
Dangerous command detected!

Command: rm -rf ./important-folder
Risk: HIGH - Recursive delete

[Approve] [Deny] [Edit]
```

### Audit Logging

All executed commands are logged to:
```
~/.openclaw/logs/terminal-killer.log
```

Log format:
```json
{
  "timestamp": "2026-02-28T12:00:00Z",
  "command": "ls -la",
  "confidence": 8,
  "execution_time_ms": 45,
  "output_lines": 12,
  "status": "success"
}
```

## Configuration

### Settings

Add to your OpenClaw config:

```yaml
terminal-killer:
  enabled: true
  confidence_threshold: 5
  require_approval_for:
    - "rm -rf"
    - "sudo"
    - "dd"
    - "mkfs"
  log_executions: true
  max_history_check: 100  # How many history entries to check
```

### Platform Detection

Automatically detects OS and adjusts detection rules:

```bash
# Auto-detected at runtime
uname -s  # Darwin, Linux, etc.
```

## Implementation

### Core Script

See `scripts/detect-command.js` for the main detection logic.

### Helper Scripts

- `scripts/check-path.js` - Verify executable in PATH
- `scripts/check-history.js` - Match against shell history
- `scripts/score-command.js` - Calculate confidence score
- `scripts/safety-check.js` - Detect dangerous patterns

## Testing

See `references/TESTING.md` for comprehensive test guide.

Quick test:
```bash
# Run the test suite
node scripts/test-detector.js

# Test specific commands
node scripts/detect-command.js "ls -la"
node scripts/detect-command.js "help me write code"
```

## Limitations

- Requires shell access (won't work in sandboxed environments)
- History check needs read access to shell history files
- Windows support requires PowerShell or WSL for full functionality
- Some commands may have false positives (natural language that looks like commands)

## Contributing

To add new builtin commands for your platform:

1. Edit `references/builtins/<platform>.txt`
2. Test with `scripts/test-detector.js`
3. Submit PR with platform verification

---

## 👤 About the Creator

**Author:** Cosper  
**Contact:** [cosperypf@163.com](mailto:cosperypf@163.com)  
**License:** MIT

### 📬 Get in Touch

Interested in this skill? Have suggestions, bug reports, or want to collaborate?

- 📧 **Email:** cosperypf@163.com
- 💡 **Suggestions:** Always welcome!
- 🐛 **Bug Reports:** Please include platform, OpenClaw version, and example inputs
- 🤝 **Collaboration:** Open to contributions and improvements

### 🙏 Acknowledgments

Built for the OpenClaw community. Thanks to everyone contributing to the ecosystem!

---

## 📝 Changelog

### v1.1.0 (2026-02-28)

**🎯 Core Improvements:**

1. **✅ Faithful Command Execution**
   - Commands are executed exactly as input
   - No modifications, no optimizations, no additions
   - Raw output preserved (including progress bars, special characters, etc.)

2. **🪟 Interactive Shell Detection**
   - Automatically detects interactive commands (`adb shell`, `ssh`, `docker exec -it`, etc.)
   - Opens new Terminal window for interactive sessions
   - Keeps main session free for other tasks
   - Loads full shell environment (~/.zshrc, etc.)

3. **📜 Long Output Handling**
   - Detects output longer than 2000 bytes
   - Shows 200-character preview
   - Prompts user to open in new Terminal window
   - Prevents interface rendering issues with long content

**📦 Files Updated:**
- `scripts/index.js` - Long output detection + interactive command handling
- `scripts/interactive.js` - New Terminal window opener
- `SKILL.md` - Updated documentation
- `README.md` - Usage examples
- `clawhub.json` - Version bump to 1.1.0

---

### v1.0.0 (2026-02-28)

**Initial Release:**
- Smart command detection (system builtins, PATH, history, patterns)
- Cross-platform support (macOS/Linux/Windows)
- Environment variable loading (~/.zshrc, etc.)
- Dangerous command detection
- Confidence scoring system

---

**Version:** 1.1.0  
**Created:** 2026-02-28  
**Last Updated:** 2026-02-28
