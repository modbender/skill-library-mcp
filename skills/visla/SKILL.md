---
name: visla
description: Creates AI-generated videos from text scripts, URLs, or PPT/PDF documents using Visla. Use when the user asks to generate a video, turn a webpage into a video, or convert a PPT/PDF into a video, or when the user asks to check Visla account credits/balance.
argument-hint: <script|url|doc|account> [script|URL|file]
metadata:
  clawdbot:
    emoji: ""
    requires:
      env: ["VISLA_API_KEY", "VISLA_API_SECRET"]
    primaryEnv: "VISLA_API_KEY"
    files: ["scripts/*"]
---

# Visla Video Generation

**Version: 260218-1410**

Create AI-generated videos from text scripts, web URLs, or documents (PPT/PDF) using Visla's OpenAPI.

## Before You Start

**Credentials** (NEVER output API keys/secrets in responses):

**IMPORTANT**: Only read local credential files with explicit user consent.

1. Ask the user for permission before reading `~/.config/visla/.credentials`
2. If permission is granted and the file exists with valid credentials, use `--credentials-file ~/.config/visla/.credentials` with the **Python** CLI. The **Bash** CLI does not support `--credentials-file`, so use environment variables instead.
3. If permission is denied, missing, or invalid, ask the user for credentials

Only process local files (scripts/docs) explicitly provided by the user, and remind users to avoid uploading sensitive data.
- Tell the user: this is a one-time setup (once configured, they won't need to do this again)
- Tell the user: get API Key and Secret from https://www.visla.us/visla-api
- Ask for the API key/secret explicitly (or ask the user to update the file and confirm). Do not repeat the secrets back in the response.

Credential validity check (practical):

- If credentials exist but running `account` fails with `VISLA_CLI_ERROR_CODE=missing_credentials` or `VISLA_CLI_ERROR_CODE=auth_failed`, treat credentials as invalid and ask the user to provide real ones.

File format (bash/zsh):
```bash
export VISLA_API_KEY="your_key"
export VISLA_API_SECRET="your_secret"
```

For PowerShell (temporary session):
```powershell
$env:VISLA_API_KEY = "your_key"
$env:VISLA_API_SECRET = "your_secret"
```

**Scripts**: `scripts/visla_cli.py` (Python), `scripts/visla_cli.sh` (Bash)

## Platform Execution

Default strategy:

- Prefer **Bash** on macOS when dependencies are available (the Bash CLI avoids Python SSL-stack issues on some macOS setups).
- Prefer **Python** when you're already using a well-configured Python (or when Bash dependencies are missing).

**Bash (recommended on macOS; also works on Linux-like environments)**:
```bash
# With user consent, you may source ~/.config/visla/.credentials
export VISLA_API_KEY="your_key"
export VISLA_API_SECRET="your_secret"
./scripts/visla_cli.sh <command>
```

**Python (cross-platform)**:
```bash
python3 scripts/visla_cli.py --key "your_key" --secret "your_secret" <command>
# Or, with user consent:
python3 scripts/visla_cli.py --credentials-file ~/.config/visla/.credentials <command>
```

**Windows native** (PowerShell/CMD without Bash; Python):
```powershell
# PowerShell
$env:VISLA_API_KEY = "your_key"
$env:VISLA_API_SECRET = "your_secret"
python scripts/visla_cli.py <command>
```

Windows note:

- The agent should prefer running the **Python CLI** on Windows unless it has verified a Bash environment (WSL/Git Bash) is available.
- For simple scripts, pass directly: `python scripts/visla_cli.py script "Scene 1: ..."`
- For multi-line or complex scripts, use stdin with `-` (recommended, no temp files):
  ```powershell
  @"
  Scene 1: ...
  Scene 2: ...
  "@ | python scripts/visla_cli.py script -
  ```
- If you have Python Launcher installed, `py -3 scripts/visla_cli.py <command>` may work better than `python`.
- Credentials:
  - The Python CLI only reads a credentials file if `--credentials-file` is explicitly provided.
  - On Windows the default path is typically: `%USERPROFILE%\\.config\\visla\\.credentials`.

Note: do not print credentials. Prefer environment variables or `--credentials-file` with explicit user consent.

## Commands

| Command | Description |
|---------|-------------|
| `/visla script <script-or-@file>` | Create video from a script (text or a local file) |
| `/visla url <URL>` | Create video from web page URL |
| `/visla doc <file>` | Create video from document (PPT/PDF) |
| `/visla account` | Show account info and credit balance |

Source of truth for the exact CLI surface: run `scripts/visla_cli.sh --help` or `python3 scripts/visla_cli.py --help`.

## Script Format

```
**Scene 1** (0-10 sec):
**Visual:** A futuristic calendar flipping to 2025 with digital patterns.
**Narrator:** "AI is evolving rapidly! Here are 3 game-changing AI trends."

**Scene 2** (10-25 sec):
**Visual:** Text: "Trend #1: Generative AI Everywhere." Show tools like ChatGPT.
**Narrator:** "Generative AI is dominating industries—creating content and images."
```

## Workflow

The `script`, `url`, and `doc` commands execute the complete flow automatically:
1. Create project
2. Poll until generation completes (may take a few minutes)
3. Auto-export and return download link

**Execution Instructions**:
- Inform user that video generation takes some time
- Report progress status periodically during polling

### Timeout Guidance

- This workflow typically takes **3-10 minutes**, but can take **up to ~30 minutes** in the worst case. Set the task/command `timeout` to **>= 30 minutes** (Windows defaults are often ~10 minutes and need to be increased). If you cannot change the timeout, warn the user up front and, on timeout, ask whether to continue or switch to a step-by-step run.
- If timeout occurs, the CLI returns `project_uuid` in the output. Inform the user they can manually check project status and continue later using the Visla web interface or API.

## Examples

```
/visla script @myscript.txt
/visla script "Scene 1: ..."
/visla url https://blog.example.com/article
/visla doc presentation.pptx
/visla account
```

## Supported Document Formats

- **PowerPoint**: `.pptx`, `.ppt`
- **PDF**: `.pdf`

## Output Format

- **Start**: Display "Visla Skill v260218-1410" when skill begins
- **End**: Display "Visla Skill v260218-1410 completed" when skill finishes
