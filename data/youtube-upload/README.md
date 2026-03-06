# OpenClaw YouTube Upload Skill

A specialized skill for OpenClaw that enables AI agents to securely upload videos to YouTube using the official YouTube Data API v3 and OAuth 2.0.

This skill bypasses the need for fragile browser automation (like Playwright/Puppeteer) by utilizing a robust Python script under the hood, supporting large file uploads (chunking), titles, descriptions, and privacy settings.

## Features

- **Reliable Uploads:** Uses `google-api-python-client` with resumable uploads to handle large video files without crashing.
- **Agent Ready:** Packaged as an OpenClaw `.skill`, allowing agents like Claude Code or Gemini to seamlessly trigger YouTube uploads.
- **Customizable:** Agents can pass `--title`, `--description`, and `--privacy` (public/private/unlisted) arguments.

## Prerequisites

1. **Google Cloud Credentials:**
   You must generate an OAuth 2.0 Client ID (Desktop App) from the Google Cloud Console with the **YouTube Data API v3** enabled.
   Save the downloaded JSON file as `client_secret.json` in the root of the skill folder.

2. **Python Dependencies:**
   The host machine needs Python 3 and the following packages installed:
   ```bash
   pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2
   ```

## Installation for OpenClaw

To install this skill locally in your OpenClaw environment:

```bash
openclaw skills install <path_to_skill_folder_or_.skill_file>
```

## First-time Authentication

On the very first run, the script requires user interaction. The agent will execute the script, which will generate an OAuth URL. The user must click the URL, authenticate with their Google account, and grant YouTube upload permissions. 

Once approved, a `token.pickle` file is generated locally, and all subsequent uploads will run silently and automatically.

## Usage (CLI / Internal)

Agents will internally call the script like this:

```bash
python3 scripts/upload.py \
  --file "/path/to/video.mp4" \
  --title "My Awesome Video" \
  --description "Description goes here" \
  --privacy "unlisted" \
  --secrets "client_secret.json"
```

## Publishing to ClawdHub

*This repository is intended to be published on ClawdHub. Contributions and improvements are welcome.*
