# Troubleshooting Claude Code Launcher

## Common Issues & Solutions

### Issue: "peekaboo not found"

**Cause:** Peekaboo CLI is not installed

**Solution:**
```bash
brew install steipete/tap/peekaboo
```

**Verify:**
```bash
peekaboo --version
```

---

### Issue: "claude CLI not found"

**Cause:** Claude Code CLI is not installed

**Solution:**
```bash
npm install -g @anthropic-ai/claude-cli
```

Or if using Homebrew:
```bash
brew tap anthropic-ai/claude
brew install claude
```

**Verify:**
```bash
which claude
claude --version
```

---

### Issue: Terminal window doesn't open

**Cause:** Terminal.app may not have focus or required permissions

**Solution:**

1. **Check Screen Recording permission:**
   ```bash
   peekaboo permissions
   ```

2. **Grant permissions in System Settings:**
   - Go to: System Settings → Privacy & Security → Screen Recording
   - Add OpenClaw/Terminal app to the allowed list
   - May need to grant Accessibility permissions too

3. **Try manually:**
   - Open Terminal.app first
   - Then run the skill

---

### Issue: "Project path does not exist"

**Cause:** Invalid or non-existent project directory

**Solution:**

1. **Verify the path exists:**
   ```bash
   ls -la ~/dev/proposal-generator
   ```

2. **Check for typos:**
   - `/dev/proposal-generator` (missing home prefix)
   - Incorrect project name

3. **List available projects:**
   ```bash
   ls ~/dev/
   ```

4. **Use full path:**
   ```bash
   claude-code-launcher /Users/qusaiabushanap/dev/proposal-generator
   ```

---

### Issue: Claude Code hangs after startup

**Cause:** Slow system performance or MCP server connectivity issues

**Solution:**

1. **Wait longer** (default is 5 seconds, may need 10-15 on slow systems)

2. **Check system resources:**
   ```bash
   vm_stat | head -5  # Check available memory
   top -l 1 -n 5      # Check CPU usage
   ```

3. **Close unused applications:**
   - Arc browser with many tabs
   - Telegram/WhatsApp Desktop
   - Other Claude Code instances

4. **Check MCP servers:**
   Inside Claude Code, run:
   ```
   /mcp
   ```
   Look for errors like "MCP servers failed"

---

### Issue: Remote Control command fails to register

**Cause:** Claude Code interface not fully loaded or UI not recognized

**Solution:**

1. **Increase wait time** - Edit the script to use `sleep 8` instead of `sleep 5`

2. **Check Claude Code version:**
   ```bash
   claude --version
   ```
   Ensure it's v2.1.50 or newer

3. **Manual activation:**
   - In Claude Code, type: `/remote-control`
   - Press Enter
   - Select "Continue"

4. **Check for prompt interference:**
   - If Claude is generating code, `/remote-control` won't execute
   - Press `Escape` first, then try again

---

### Issue: "No write permission for: /path/to/project"

**Cause:** Permission denied on the target directory

**Solution:**

1. **Check permissions:**
   ```bash
   ls -ld ~/dev/proposal-generator
   ```

2. **Fix permissions:**
   ```bash
   chmod u+w ~/dev/proposal-generator
   ```

3. **If it's a Git repo, check Git permissions:**
   ```bash
   cd ~/dev/proposal-generator
   git status  # Will show if there are permission issues
   ```

---

### Issue: Terminal commands seem to be typed too fast

**Cause:** Peekaboo typing speed is too aggressive for the system

**Solution:**

1. **Add delays in the script** - Modify these lines:
   ```bash
   sleep 1  # After each command
   ```
   Change to:
   ```bash
   sleep 2  # Or longer if needed
   ```

2. **Use human cadence typing:**
   The script already uses `--wpm 140` (human typing speed)

3. **Check if Terminal is in focus:**
   Some keypresses may be sent to wrong app if focus lost

---

### Issue: Screenshot is blank or doesn't show Claude Code

**Cause:** Screenshot captured before UI fully rendered or wrong window

**Solution:**

1. **Increase wait time before screenshot:**
   In script, change:
   ```bash
   sleep 3  # After confirming Remote Control
   ```
   To:
   ```bash
   sleep 6
   ```

2. **Verify Terminal window is in foreground:**
   ```bash
   peekaboo window focus --app Terminal
   ```

3. **Manual screenshot test:**
   ```bash
   peekaboo image --mode screen --path ~/test-screenshot.png
   ```

---

### Issue: Peekaboo click/type commands don't work

**Cause:** Peekaboo commands may need fresh permissions or Terminal not accessible

**Solution:**

1. **Test Peekaboo:**
   ```bash
   peekaboo permissions  # Should show Screen Recording enabled
   ```

2. **Enable Screen Recording:**
   - System Settings → Privacy & Security → Screen Recording
   - Make sure OpenClaw/Terminal has access

3. **Restart Terminal:**
   ```bash
   pkill -f Terminal
   sleep 1
   open -a Terminal
   ```

4. **Try a simple Peekaboo command:**
   ```bash
   peekaboo list apps  # Should list running applications
   ```

---

### Issue: Multiple Claude Code instances conflict

**Cause:** Running launcher while another Claude Code session is active

**Solution:**

1. **Each Terminal window has its own Claude Code session**
   - This is intentional and supported
   - Use different terminal tabs/windows for different projects

2. **If you want to limit concurrent sessions:**
   ```bash
   # Kill all Claude Code instances
   pkill -f "claude code"
   
   # Or kill specific one
   pkill -f "claude code" -signal TERM  # Graceful
   ```

3. **Check active processes:**
   ```bash
   ps aux | grep claude
   ```

---

### Issue: Remote Control session URL not visible

**Cause:** Script captured screenshot before URL appeared or Terminal not scrolled

**Solution:**

1. **Manually view in Terminal:**
   The URL should be visible. Scroll up in Terminal if needed.

2. **Extract from logs:**
   ```bash
   grep "session_" ~/.openclaw/workspace/logs/claude-code-launcher/*.log | tail -1
   ```

3. **Show QR code in Terminal:**
   In Claude Code, press spacebar to toggle QR code display

---

### Issue: "Network connectivity issue" error

**Cause:** Claude trying to connect to API but network is slow

**Solution:**

1. **Check internet connection:**
   ```bash
   curl -I https://api.anthropic.com
   ```

2. **Wait for reconnection** - Script automatically waits up to 10 seconds

3. **Check API status:**
   Visit https://status.anthropic.com

4. **Try again after network stabilizes:**
   The Remote Control will auto-reconnect

---

## Getting Help

### View logs:
```bash
cat ~/.openclaw/workspace/logs/claude-code-launcher/launch-*.log
```

### Run in verbose mode:
```bash
VERBOSE=1 ./launch_claude_code.sh ~/dev/proposal-generator
```

### Test Peekaboo:
```bash
peekaboo see --app Terminal --annotate --path ~/peekaboo-debug.png
```

### Check OpenClaw status:
```bash
openclaw status
```

---

## Known Limitations

1. **macOS only** - Requires Terminal.app and system automation APIs
2. **Single window at a time** - Creates one new Terminal per invocation
3. **Focus required** - Terminal window must be frontmost for input
4. **Requires permissions** - Screen Recording + Accessibility must be enabled

---

## Performance Tips

- **Close unused tabs in Arc** - Reduces memory pressure on system
- **Disconnect Telegram Desktop** - Saves system resources
- **Restart Terminal regularly** - Clears accumulated state
- **Use solid internet connection** - Critical for Claude Code API calls

---

## Still Stuck?

If none of these solutions work:

1. **Collect debug info:**
   ```bash
   echo "=== Environment ===" 
   uname -a
   echo "=== CLI Versions ==="
   claude --version
   peekaboo --version
   echo "=== Logs ==="
   tail -50 ~/.openclaw/workspace/logs/claude-code-launcher/launch-*.log
   ```

2. **Check system permissions:**
   ```bash
   peekaboo permissions
   ```

3. **Try manual process** - Do each step manually in Terminal to identify failure point

4. **Report issue with debug info** - Include output from above commands
