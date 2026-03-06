# Terminal Killer - Testing Guide

This guide explains how to test the Terminal Killer skill.

## Quick Start

```bash
cd /Users/cosper/MyFolder/git/31.openclaw/terminal-killer

# Run the full test suite
node scripts/test-detector.js

# Test a specific command
node scripts/detect-command.js "ls -la"
node scripts/detect-command.js "help me write code"

# Test with custom tools (loads ~/.zshrc)
node scripts/detect-command.js "adb devices"
node scripts/detect-command.js "kubectl version"
```

## Environment Loading

Terminal Killer automatically loads your shell environment:

- ✅ Sources `~/.zshrc`, `~/.bash_profile`, `~/.bashrc`
- ✅ Inherits full PATH (including Android SDK, Homebrew, etc.)
- ✅ Preserves all environment variables
- ✅ Works with custom tools like `adb`, `kubectl`, `docker`, etc.

This ensures commands work exactly as they do in your interactive terminal!

## Test Categories

### 1. Unit Tests (Automated)

Run the automated test suite:

```bash
node scripts/test-detector.js
```

This tests:
- ✅ Clear commands (should EXECUTE)
- ✅ Clear tasks (should LLM)
- ✅ Borderline cases (might ASK)
- ✅ Dangerous commands (should ASK)

### 2. Manual Testing

Test individual commands interactively:

```bash
# Test various commands
node scripts/detect-command.js "git status"
node scripts/detect-command.js "npm install --save"
node scripts/detect-command.js "find . -name '*.js' | xargs grep test"

# Test natural language
node scripts/detect-command.js "can you help me"
node scripts/detect-command.js "what is the weather"
```

Expected output format:
```json
{
  "input": "ls -la",
  "decision": "EXECUTE",
  "confidence": "HIGH",
  "score": 8,
  "dangerous": false,
  "platform": "darwin",
  "timestamp": "2026-02-28T12:00:00.000Z"
}
```

### 3. Integration Testing

To test with actual OpenClaw:

1. **Package the skill:**
   ```bash
   # If you have openclaw CLI
   openclaw skills check
   ```

2. **Install locally:**
   ```bash
   # Copy to your OpenClaw skills directory
   cp -r terminal-killer ~/.openclaw/skills/
   ```

3. **Test in conversation:**
   - Type `ls -la` → Should execute directly
   - Type `help me write code` → Should trigger LLM

### 4. Platform-Specific Testing

Test on different platforms:

**macOS:**
```bash
node scripts/detect-command.js "mdfind query"
node scripts/detect-command.js "open ."
node scripts/detect-command.js "say hello"
```

**Linux:**
```bash
node scripts/detect-command.js "systemctl status"
node scripts/detect-command.js "apt update"
node scripts/detect-command.js "journalctl -f"
```

**Windows (PowerShell):**
```bash
node scripts/detect-command.js "Get-Process"
node scripts/detect-command.js "Invoke-WebRequest"
node scripts/detect-command.js "Start-Service"
```

## Test Checklist

### Command Detection

- [ ] Common commands detected (ls, cd, git, npm)
- [ ] Commands with flags detected (ls -la, npm install --save)
- [ ] Piped commands detected (cat file | grep)
- [ ] Commands with variables detected (echo $HOME)
- [ ] Commands with paths detected (cd ~/projects)

### Task Detection

- [ ] Questions routed to LLM (what, how, why)
- [ ] Help requests routed to LLM (help me, can you)
- [ ] Code generation routed to LLM (write, create, build)
- [ ] Explanations routed to LLM (explain, tell me)

### Edge Cases

- [ ] Single word commands (ls, pwd, whoami)
- [ ] Very long commands
- [ ] Commands with special characters
- [ ] Ambiguous inputs (run, build, deploy)

### Safety

- [ ] Dangerous commands flagged (rm -rf, sudo, dd)
- [ ] Destructive patterns detected
- [ ] Network download + execute detected (curl | sh)

### Performance

- [ ] Detection completes in < 100ms
- [ ] History check doesn't block
- [ ] PATH check doesn't block

## Debugging

Enable verbose output:

```bash
# Add console.log statements to detect-command.js
# Or run with NODE_DEBUG
NODE_DEBUG=terminal-killer node scripts/detect-command.js "test"
```

Check which rules are triggering:

```javascript
// Temporarily add to detect-command.js
console.log('Builtin:', isBuiltinCommand(input));
console.log('In PATH:', existsInPath(firstWord));
console.log('History:', matchesHistory(input));
console.log('Operators:', hasShellOperators(input));
console.log('Question:', isQuestion(input));
```

## Adding Test Cases

Add new test cases to `scripts/test-detector.js`:

```javascript
const TEST_CASES = [
  // Add your test case here
  { 
    input: 'your command here', 
    expected: 'EXECUTE',  // or 'LLM' or 'ASK'
    description: 'What this tests' 
  },
];
```

## Reporting Issues

When reporting detection issues, include:

1. The input that was misclassified
2. Expected decision (EXECUTE/LLM/ASK)
3. Actual decision
4. Platform (macOS/Linux/Windows)
5. Score from detect-command.js output

Example:
```
Input: "npm test"
Expected: EXECUTE
Actual: LLM
Platform: darwin
Score: 2 (too low)
```

## Continuous Testing

Run tests before committing changes:

```bash
# Quick test
node scripts/test-detector.js

# Test specific command
node scripts/detect-command.js "your-test-command"
```

---

**Last Updated:** 2026-02-28  
**Version:** 1.0.0
