# Changelog

## 2026-01-26 - Initial Release

### ✅ Completed Features

- **Auto-approver script** - Detects and handles Claude Code approval prompts
  - Handles "Do you want..." prompts
  - Handles "Do you trust..." folder prompts
  - Uses arrow keys + Enter for TUI navigation
  
- **Wingman script** - Complete automation wrapper
  - Spawns Claude Code in named tmux sessions
  - Starts auto-approver in background
  - Reliable prompt submission (double-tap Enter)
  - Trust prompt detection and handling
  - Optional monitoring and wait modes

### ✅ Real-World Testing

- **Test 1:** Simple file creation (test2.txt, test3.txt, test5.txt) ✅
- **Test 2:** AWS VM connectivity check (VSR project) ✅
  - SSH connection verified
  - vLLM server status checked
  - API health confirmed
  - Multiple SSH commands auto-approved without human intervention

### 🎯 Proven Benefits

- **Cost savings:** Uses work's free Claude Code API instead of $20/month Anthropic budget
- **Zero intervention:** Runs completely hands-off after initial folder trust
- **Parallel sessions:** Can run multiple tasks simultaneously
- **Full transparency:** Can attach to any session anytime to see progress

### 🐛 Known Issues

- Trust prompt appears first time in new directory (one-time approval needed)
- Enter key timing occasionally requires double-tap
- Auto-approver doesn't log when prompts are handled instantly

### 📝 Next Steps

- [ ] Package as Clawdbot skill
- [ ] Push to GitHub
- [ ] Add more examples
- [ ] Improve trust prompt automation
