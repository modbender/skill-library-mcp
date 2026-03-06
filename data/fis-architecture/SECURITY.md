# Security Considerations - FIS Architecture

> **Version**: 3.2.7  
> **Last Updated**: 2026-02-20

## Overview

FIS (Federal Intelligence System) is a file-based multi-agent workflow framework. This document outlines security considerations when using this skill.

## 🔒 Subprocess Usage

The following Python helper scripts in `lib/` use `subprocess`:

| Script | Subprocess Call | Purpose | Risk Level |
|--------|-----------------|---------|------------|
| `badge_generator_v7.py` | `openclaw --version` | Get version for badge display | 🟢 Low |
| `badge_generator_v7.py` | `python -c <script>` | Generate badge image | 🟢 Low |
| `fis_lifecycle.py` | `python -c <script>` | Generate badge via CLI | 🟢 Low |
| `fis_lifecycle.py` | `openclaw message send` | Send badge to WhatsApp | 🟢 Low |
| `fis_subagent_tool.py` | `python -c <script>` | Generate badge | 🟢 Low |
| `multi_worker_demo.py` | `openclaw message send` | Demo notification | 🟢 Low |

**All subprocess calls**:
- Only execute `openclaw` CLI or `python` interpreter
- Do not download or execute remote code
- Use fixed timeouts (5-30 seconds)
- Capture output, don't shell-out to user input

## 🎫 Ticket Resource Permissions

Tickets can include a `resources` field granting permissions:

```json
{
  "resources": ["file_read", "file_write", "code_execute", "web_search"]
}
```

**⚠️ Security Warning**: 
- `code_execute` allows arbitrary code execution
- `file_write` allows modifying files in allowed directories
- Only grant these to trusted ticket creators
- Review all automated actions before execution

**Best Practice**: Start with minimal permissions (`["file_read"]`), escalate only when necessary.

## 📁 Filesystem Access

### Write Locations
- `~/.openclaw/fis-hub/tickets/active/` - Active tickets
- `~/.openclaw/fis-hub/tickets/completed/` - Completed tickets
- `~/.openclaw/fis-hub/knowledge/` - Shared knowledge
- `~/.openclaw/fis-hub/results/` - Research outputs
- `~/.openclaw/output/badges/` - Generated badge images

### Never Accesses
- Other agents' `MEMORY.md` or `HEARTBEAT.md`
- System directories outside `~/.openclaw/`
- SSH keys, credentials, or sensitive configs

## 🔧 External Dependencies

### Required CLI
- `mcporter` - OpenClaw QMD search CLI
  - Used for: Semantic search across knowledge base
  - Install: Included with OpenClaw

### Optional Python Dependencies
- `Pillow>=9.0.0` - Image generation for badges
- `qrcode>=7.0` - QR code generation

**Note**: Core FIS functionality (ticket files) works without these dependencies.

## 🛡️ Sandboxing Recommendations

Before running Python helpers:

1. **Review the code**:
   ```bash
   cat ~/.openclaw/workspace/skills/fis-architecture/lib/*.py
   ```

2. **Test in isolated environment**:
   ```bash
   # Create test hub
   export FIS_SHARED_HUB=/tmp/test-fis-hub
   mkdir -p $FIS_SHARED_HUB/tickets/{active,completed}
   ```

3. **Verify no network calls**:
   ```bash
   grep -r "requests\|urllib\|http" lib/
   # Should only find "openclaw" CLI calls
   ```

## 🔍 Audit Checklist

Before granting `code_execute` or `file_write` permissions:

- [ ] Review ticket creator trustworthiness
- [ ] Verify task description legitimacy
- [ ] Check output directory is appropriate
- [ ] Confirm no sensitive files in target path
- [ ] Test in isolated environment first

## 🚨 Reporting Issues

If you discover security issues:
1. Check GitHub Issues: https://github.com/MuseLinn/fis-architecture/issues
2. Review code: All Python files are human-readable
3. Enable OpenClaw's execution approval: `channels.discord.execApprovals.enabled: true`

## ✅ Security Guarantees

What FIS **guarantees**:
- ✅ No auto-download of remote code
- ✅ No modification of other skills' files
- ✅ No access to system credentials
- ✅ All file paths are under `~/.openclaw/`

What FIS **cannot** guarantee:
- ❌ Safety of tickets with `code_execute` from untrusted sources
- ❌ Protection against malicious ticket creators
- ❌ Automatic sandboxing of executed code

---

*Use responsibly. When in doubt, review before running.*
