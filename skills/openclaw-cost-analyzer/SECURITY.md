# Security Policy

## Security Guarantees

openclaw-cost-optimizer is designed with security as a top priority. This skill is **safe to run** on your local machine.

### ✅ What This Skill Does

1. **Reads session logs** from `~/.openclaw/agents/main/agent/sessions/*.jsonl`
2. **Analyzes token usage** locally using pure JavaScript
3. **Generates reports** saved to `~/.openclaw/workspace/memory/`
4. **Outputs recommendations** to console and file

### ✅ Security Features

- **No network requests**: Script runs entirely offline
- **No external dependencies**: Pure Node.js, no npm packages
- **No subprocess execution**: Does not call shell commands or spawn processes
- **No code execution**: Does not eval() or execute dynamic code
- **Read-only analysis**: Does not modify any configuration files
- **Local data only**: All data stays on your machine

### ✅ File Access

**Read access**:
- `~/.openclaw/agents/main/agent/sessions/*.jsonl` (session logs)

**Write access**:
- `~/.openclaw/workspace/memory/cost-analysis-report.md` (report output)

No other files are accessed or modified.

### ✅ Permissions Required

- Read: Session logs directory
- Write: Memory directory (for report output)

### ✅ Data Privacy

- **No data transmission**: Nothing is sent over the network
- **No logging to external services**: All logs stay local
- **No telemetry**: No usage tracking or analytics
- **No API calls**: Does not connect to any external APIs

### 🔍 Audit Information

- **Script location**: `scripts/cost_analyzer.js`
- **Lines of code**: ~350
- **Language**: Pure JavaScript (Node.js)
- **Dependencies**: None (uses only Node.js built-ins: fs, path, os)

### 🛡️ Verification

You can verify the security claims by:

1. **Reading the source code**: `scripts/cost_analyzer.js` is fully readable
2. **Checking for network calls**: Search for `http`, `https`, `fetch`, `axios` - none exist
3. **Checking for subprocess**: Search for `exec`, `spawn`, `child_process` - none exist
4. **Checking for eval**: Search for `eval`, `Function()` - none exist

### 📋 Security Checklist

- [x] No network requests
- [x] No external dependencies
- [x] No subprocess execution
- [x] No dynamic code execution
- [x] No system modifications
- [x] Read-only analysis
- [x] Local data only
- [x] No telemetry
- [x] No API keys required
- [x] No credentials stored

## Reporting Security Issues

If you discover a security vulnerability, please report it to:
- Open an issue on the skill repository
- Contact via ClawHub community

## Best Practices

When using this skill:

1. **Review the code**: Always review scripts before running
2. **Check permissions**: Ensure file permissions are appropriate (600 for sensitive files)
3. **Monitor output**: Check where reports are saved
4. **Regular updates**: Keep the skill updated for security patches

## Comparison with Similar Tools

Unlike some optimization tools that may:
- ❌ Send data to external APIs
- ❌ Require API keys
- ❌ Modify system configurations
- ❌ Execute arbitrary code

openclaw-cost-optimizer:
- ✅ Runs entirely offline
- ✅ Requires no credentials
- ✅ Only reads and analyzes
- ✅ Transparent and auditable

## License

MIT License - See LICENSE file for details

---

**Last Updated**: 2026-02-26  
**Security Audit**: Self-audited (open for community review)
