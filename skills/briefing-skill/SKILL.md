---
name: briefing
description: Automatically track creator channels and transcribe new videos (YouTube, Bilibili, TikTok) with zero token cost during the pipeline. Use memory-based updates to skip already processed items and avoid duplicate downloads.
metadata: {"openclaw":{"emoji":"📺","requires":{"os":["linux","darwin"]},"install":[{"id":"bundled","kind":"bundled","bins":"briefing"}]}}
---

# Briefing Operator

This skill operates the `briefing` CLI tool.

## Available Commands

- Run update pipeline:
  `briefing`

- Add tracking URL:
  `briefing -add <source_url>`

- Delete tracking URL:
  `briefing -delete <source_url>`

- Set config key:
  `briefing -set <KEY> <VALUE>`

- Show config:
  `briefing -show`

---

## Execution Rules (Strict)

1. **Bootstrap Check**: 
   Before any execution, if the `briefing` binary is missing from PATH:
   - Check if `{skillDir}/install.sh` exists.
   - If found, execute `bash {skillDir}/install.sh` to initialize the environment.
   - If initialization fails or script is missing, report: "briefing CLI not found. Please run the install script manually." and stop.

2. **Bash Tool Requirement**:
   Always execute the CLI command using bash/exec. If bash is disabled, report: "bash tool is disabled. Enable commands.bash=true." and stop.

3. **Absolute Path Fallback**:
   If `briefing` is not in global PATH, try executing via `{skillDir}/briefing` (if the installer symlinks it there).

---

## After Running `briefing`

1. Parse stdout.
2. Detect lines matching:

   `[WHISPER DONE] <filename>`

3. For each `<filename>`, read:

   `output/<filename>/whisper.txt`

4. Return the extracted whisper content.
5. If no `[WHISPER DONE]` appears, report:
   "No new whisper output generated in this run."

6. If a whisper file is missing, report the exact missing path.

---

## Fallback

If `briefing` is not available on PATH:

- Attempt execution using an absolute path if known.
- If still unavailable, report and stop.

Do not manually edit config.json.
Always use CLI commands.