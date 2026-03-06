---
name: Social Media Suite
description: Automate social media posting to Instagram and YouTube. Schedule and publish images, videos, and content automatically. Social media automation tool for content creators, marketers, and businesses. Free alternative to Buffer and Hootsuite.
metadata: {"openclaw": {"emoji": "🚀"}}
---

# 🚀 Social Media Suite - Automated Posting

**Post to Instagram and YouTube automatically.** Schedule and publish content without manual uploads. The free alternative to expensive tools like Buffer or Hootsuite – pay only for AI tokens, no monthly fees.

## Use Cases
- **Content Creators**: Automate daily posting to grow your audience
- **Marketing Teams**: Schedule campaigns across multiple platforms
- **Business Owners**: Maintain consistent social presence without daily effort
- **Agencies**: Manage multiple client accounts efficiently

**Key Features**: Instagram image posting, YouTube video uploads, caption management, privacy settings, hashtag support, OAuth authentication.

Currently supported platforms:
- Instagram
- YouTube

---

## 1. Setup

Before you can use this skill, you need to set up credentials for each platform you want to use.

### 1.1 Instagram Setup

1.  **Prerequisites**:
    - An Instagram account with **Creator** or **Business** status.
    - A Facebook Page connected to your Instagram account.
    - A Facebook App with the necessary permissions: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
    - A long-lived **User Access Token** from your Facebook App.

2.  **Credential Files**:
    Create the following files inside the `{baseDir}/credentials/` directory:
    - `instagram_user_access_token`: Paste your long-lived User Access Token into this file.
    - `instagram_account_id`: Paste your Instagram Account ID into this file.

### 1.2 YouTube Setup

1.  **Prerequisites**:
    - A Google Cloud Platform project with the **YouTube Data API v3** enabled.
    - OAuth 2.0 credentials (client ID and client secret).

2.  **Authentication**:
    Run the one-time authentication command to authorize the skill and generate your initial credentials:

    ```bash
    bash {baseDir}/run.sh auth --platform youtube
    ```

    Follow the on-screen instructions to log in with your Google account and grant permission. This will create a `youtube_credentials.json` file in the `{baseDir}/credentials/` directory.

---

## 2. Usage

The primary command is `post`, which takes a platform and platform-specific arguments.

### 2.1 Post to Instagram

This command posts a single image with a caption to your Instagram account.

**Command:**
```bash
bash {baseDir}/run.sh post --platform instagram --image-url <url_to_image> --caption "Your caption here"
```

**Parameters:**
- `--platform instagram`: Specifies that the target is Instagram.
- `--image-url <url_to_image>`: **Required**. A public URL to the image you want to post. The image must be accessible from the internet.
- `--caption "<text>"`: **Required**. The text caption for your post.

**Example:**
```bash
bash {baseDir}/run.sh post --platform instagram \
  --image-url "https://i.imgur.com/removed.png" \
  --caption "Just chilling with my OpenClaw agent! 🤖 #OpenClaw #AI #automation"
```

### 2.2 Post to YouTube

This command uploads a video file to your YouTube channel.

**Command:**
```bash
bash {baseDir}/run.sh post --platform youtube --file <path_to_video> --title "Title" --description "Description" [options]
```

**Parameters:**
- `--platform youtube`: Specifies that the target is YouTube.
- `--file <path>`: **Required**. The local path to the video file you want to upload.
- `--title "<text>"`: **Required**. The title of the video (max 100 characters).
- `--description "<text>"`: **Required**. The description of the video.
- `--privacy <status>`: *Optional*. The privacy status of the video. Can be `public`, `unlisted`, or `private`. (Default: `private`)
- `--tags "<tag1,tag2>"`: *Optional*. Comma-separated list of tags for the video.

**Example:**
```bash
bash {baseDir}/run.sh post --platform youtube \
  --file "/home/user/videos/my_awesome_video.mp4" \
  --title "My First AI-Generated Video" \
  --description "Check out this cool video that my OpenClaw agent helped me create!" \
  --privacy "public" \
  --tags "AI,OpenClaw,automation,tech"
```

---

## 3. Credential Management

### Refresh YouTube Token

The YouTube access token expires periodically. The script attempts to refresh it automatically, but you can also trigger a manual refresh if needed.

```bash
bash {baseDir}/run.sh auth --platform youtube --refresh
```

---
## 4. Scripts (for implementation)

This `SKILL.md` is the user-facing documentation. The actual logic would be implemented in a `run.sh` script that parses the arguments and calls the appropriate platform-specific logic.

A simplified `run.sh` might look like this:

```bash
#!/bin/bash
set -e

PLATFORM=""

# Parse platform first
if [ "$1" == "--platform" ]; then
    PLATFORM="$2"
    shift 2
fi

case $PLATFORM in
    instagram)
        # Execute instagram logic with remaining args: "$@"
        echo "Calling Instagram script with: $@"
        # ./instagram_poster.sh "$@"
        ;;
    youtube)
        # Execute youtube logic with remaining args: "$@"
        echo "Calling YouTube script with: $@"
        # ./youtube_uploader.sh "$@"
        ;;
    *)
        echo "Error: Unknown or missing platform. Use --platform [instagram|youtube]"
        exit 1
        ;;
esac
```
