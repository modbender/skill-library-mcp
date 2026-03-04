---
name: youtube-upload
description: "Uploads a video to YouTube using the official YouTube Data API v3 and OAuth 2.0. Use this skill when the user asks to upload a video to YouTube. It supports titles, descriptions, privacy settings (public, private, unlisted), and large file chunking. Requires a Google Cloud 'client_secret.json' file."
metadata:
  openclaw:
    emoji: "📺"
    requires:
      bins: ["python3", "pip3"]
---

# YouTube Upload Skill

This skill allows you to securely upload videos to YouTube via the official API, bypassing the need for fragile browser automation.

## Prerequisites

1. The Google API Python Client and OAuth libraries must be installed:
   ```bash
   pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2
   ```
2. A `client_secret.json` file is required. The user must generate an OAuth 2.0 Client ID (Desktop App) from the Google Cloud Console with the YouTube Data API v3 enabled.

## Usage

Use the provided Python script to upload the video:

```bash
python3 scripts/upload.py \
  --file "/path/to/video.mp4" \
  --title "My Video Title" \
  --description "My Video Description" \
  --privacy "unlisted" \
  --secrets "/path/to/client_secret.json"
```

### First Run (Authentication)
On the very first run, the script will output a URL or open a browser window for the user to authenticate and grant permission to their YouTube account. Instruct the user to complete the login flow. Once approved, a `token.pickle` file is generated locally, and subsequent uploads will run silently.

## Troubleshooting

- **Token Expired / Revoked:** If the token becomes invalid, delete `token.pickle` and re-run to trigger the auth flow again.
- **Quota Exceeded:** The YouTube API has a daily upload quota. If this is hit, the user must wait until the quota resets.
