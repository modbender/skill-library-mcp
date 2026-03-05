# Skill: WordPress Remote News Publisher

> Automated news article generation and publishing to WordPress via SSH and WP-CLI.

---

## Folder Structure

```
WordPress-Remote-News-Publisher/
  SKILL.md
  config.json
  scripts/
    download_cover.py
    optimize_image.sh
    upload_media_remote.sh
    publish_wp_remote.sh
```

---

## Metadata

```yaml
---
name: wordpress-remote-news-publisher
description: |
  Automatically generates and publishes news articles to a remote WordPress 
  installation via SSH using public key authentication. Downloads and optimizes 
  cover images from Unsplash, transfers them via SCP, and publishes articles 
  with SEO metadata (Yoast).
user-invocable: true
triggers:
  - cron: "0 10 * * 1-5"  # Weekdays at 10:00
  - cron: "0 16 * * 1-5"  # Weekdays at 16:00
  - manual: "/wordpress-remote-news-publisher [topic]"
metadata:
  emoji: "📰"
  version: "1.0.0"
  author: "ClawHub Community"
  license: "MIT"
  openclaw:
    requires:
      bins:
        - ssh
        - scp
        - python3
        - curl
        - convert
      env:
        - WP_SSH_HOST
        - WP_SSH_USER
        - WP_SSH_KEY
        - WP_SSH_PORT
        - WP_REMOTE_PATH
        - WP_REMOTE_TMP
        - WP_AUTHOR_ID
        - UNSPLASH_ACCESS_KEY
---
```

---

## Overview

This skill enables automated news content creation and publication to WordPress websites hosted on remote servers. It leverages SSH with public key authentication for secure, passwordless connections, and WP-CLI for all WordPress operations on the server side.

### Key Features

- **Remote Execution**: All WP-CLI operations run on the remote server via SSH
- **Automated Topic Selection**: Round-robin rotation through configured topics
- **Journalistic Writing Style**: Senior journalist quality content with lede, body, and attribution
- **Image Pipeline**: Unsplash download → local optimization → SCP transfer → WordPress import
- **SEO Integration**: Yoast SEO meta description and focus keyword support
- **Cron Scheduling**: Automated execution on weekdays

---

## Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `WP_SSH_HOST` | Remote server hostname or IP | Yes | `203.0.113.10` or `example.com` |
| `WP_SSH_USER` | SSH username on remote server | Yes | `deploy`, `www-data`, `wpcli` |
| `WP_SSH_KEY` | Absolute path to SSH private key | Yes | `/home/user/.ssh/id_ed25519_wp` |
| `WP_SSH_PORT` | SSH port (default: 22) | No | `22` |
| `WP_REMOTE_PATH` | Absolute path to WordPress installation | Yes | `/var/www/html/wordpress` |
| `WP_REMOTE_TMP` | Writable temp directory on remote | No | `/tmp` |
| `WP_AUTHOR_ID` | WordPress author ID for posts | Yes | `1` |
| `UNSPLASH_ACCESS_KEY` | Unsplash API access key | Yes | `AbC123...` |

---

## Editorial Philosophy

Every article MUST adhere to these rules:

1. **Write like a senior journalist**, not an AI assistant
2. **Use variable sentence length**: Alternate short periods with complex constructions
3. **Lead with a clear thesis** in the first paragraph (lede)
4. **Include attributed quotes** from real sources when available
5. **Avoid AI-sounding phrases**: Never use "it's important to note," "in the digital age," "in today's world," "in conclusion," "obviously," "clearly," or similar formulas
6. **Specific titles**: No clickbait. The title must contain the main fact

---

## Complete Procedure

### Phase 1: Topic Selection

If no topic is provided as argument:

1. Read `config.json` for the configured topic list
2. Select the topic with the oldest publication date (round-robin)
3. Use that topic for content generation

### Phase 2: SSH Connection Verification

Before any operation, verify SSH connectivity:

```bash
ssh -i "$WP_SSH_KEY" -p "${WP_SSH_PORT:-22}" \
    -o StrictHostKeyChecking=no \
    -o BatchMode=yes \
    -o ConnectTimeout=10 \
    "$WP_SSH_USER@$WP_SSH_HOST" \
    "wp --info --path=$WP_REMOTE_PATH"
```

If this fails, abort and notify via Telegram with error details.

### Phase 3: Research and Fact Gathering

1. **Web Search**: Query "[topic] latest news [current month]" and English equivalents for international sources

2. **Fact Collection** (only verifiable facts):
   - Numerical data with source attribution
   - Statements from real people with name and role
   - Specific dates and events
   - Avoid unattributed speculation

3. **Store Facts**: Save to `/tmp/wp_facts.json`

### Phase 4: Article Generation

#### Mandatory Editorial Structure

**TITLE** (max 65 characters)
- Specific, not generic. Contains the main fact.
- ✅ Good: "Meta cuts 3,600 jobs: farewell to Base AI teams"
- ❌ Bad: "Meta takes important step for the future"

**LEDE** (first paragraph, 40-60 words)
- Answers: Who? What? When? Where? Why?
- The most important news in dense, precise form
- Never starts with "In the world of..." or "In recent years..."

**BODY** (600-900 total words)
- Paragraph 2: Context and background
- Paragraphs 3-4: Main development with data and citations
- Paragraph 5: Reactions and positions from key players
- Paragraph 6: Implications and prospects (attributed to experts)
- Final paragraph: Narrative closing element

**META DESCRIPTION** (max 155 characters)
**SEO TAGS** (3-5 tags, without #)
**PRIMARY KEYWORD** (1 keyword)

#### Output Format

Save to `/tmp/wp_article.json`:
```json
{
  "title": "...",
  "content": "...",
  "excerpt": "...",
  "tags": ["..."],
  "meta_desc": "...",
  "keyword": "...",
  "topic": "..."
}
```

### Phase 5: Cover Image

1. **Determine Visual Keyword**: Derive from article topic (e.g., "server room technology")

2. **Download from Unsplash** (local machine):
   ```bash
   python3 {baseDir}/scripts/download_cover.py '[keyword]' /tmp/cover.jpg
   ```

3. **Optimize Locally**:
   ```bash
   bash {baseDir}/scripts/optimize_image.sh /tmp/cover.jpg /tmp/cover_opt.jpg
   ```

4. **Transfer and Import**:
   ```bash
   bash {baseDir}/scripts/upload_media_remote.sh /tmp/cover_opt.jpg
   ```
   → Media ID saved to `/tmp/wp_media_id.txt`

### Phase 6: Publishing to Remote WordPress

1. **Create Draft Post**:
   ```bash
   bash {baseDir}/scripts/publish_wp_remote.sh
   ```

2. **Verify Status**: Wait 30 seconds, check via SSH

3. **Publish**:
   ```bash
   ssh -i "$WP_SSH_KEY" -p "${WP_SSH_PORT:-22}" "$WP_SSH_USER@$WP_SSH_HOST" \
     "wp post update $(cat /tmp/wp_post_id.txt) \
      --post_status=publish --path=$WP_REMOTE_PATH"
   ```

4. **Retrieve Published URL**:
   ```bash
   ssh -i "$WP_SSH_KEY" -p "${WP_SSH_PORT:-22}" "$WP_SSH_USER@$WP_SSH_HOST" \
     "wp post get $(cat /tmp/wp_post_id.txt) --field=url --path=$WP_REMOTE_PATH"
   ```

5. **Send Telegram Confirmation**: Title, URL, word count, keyword

### Phase 7: Update Registry

Update `config.json` with the current timestamp for the published topic to ensure proper rotation.

---

## SSH Key Setup (One-Time)

Before using this skill, configure public key authentication:

```bash
# 1. Generate a dedicated key pair (ed25519 recommended)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_wp \
    -C "openclaw-wp-publisher" -N ""

# 2. Copy public key to remote server
ssh-copy-id -i ~/.ssh/id_ed25519_wp.pub -p 22 deploy@203.0.113.10

# 3. Verify passwordless connection
ssh -i ~/.ssh/id_ed25519_wp -o BatchMode=yes \
    deploy@203.0.113.10 "wp --info"

# 4. (Optional) Restrict key in ~/.ssh/authorized_keys
command="wp --allow-root",no-port-forwarding,no-X11-forwarding \
    ssh-ed25519 AAAA... openclaw-wp-publisher
```

> **Security Tip**: Use a dedicated SSH user (`deploy` or `wpcli`) with minimal server permissions. Never use `root`. If WP-CLI needs write access to `/var/www`, add the user to the `www-data` group.

---

## Remote Server Requirements

| Component | Requirement | Verification |
|-----------|-------------|--------------|
| WP-CLI | Installed and in PATH | `wp --info` |
| PHP | ≥ 7.4 (8.x recommended) | `php --version` |
| Python 3 | For JSON parsing | `python3 --version` |
| Permissions | SSH user writes to `WP_REMOTE_PATH` | `ls -la /var/www/html/wordpress` |
| SSH Port | Open in firewall | `ufw status` |

---

## Local Machine Requirements (OpenClaw)

| Component | Requirement | Installation |
|-----------|-------------|--------------|
| ssh, scp | In PATH | Pre-installed on Linux/macOS |
| ImageMagick | `convert` command | `apt install imagemagick` |
| Python 3 | With `requests` library | `pip install requests` |

---

## Configuration Example

### OpenClaw Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "wordpress-remote-news-publisher": {
        "env": {
          "WP_SSH_HOST": "203.0.113.10",
          "WP_SSH_USER": "deploy",
          "WP_SSH_KEY": "/home/user/.ssh/id_ed25519_wp",
          "WP_SSH_PORT": "22",
          "WP_REMOTE_PATH": "/var/www/html/wordpress",
          "WP_REMOTE_TMP": "/tmp",
          "WP_AUTHOR_ID": "1",
          "UNSPLASH_ACCESS_KEY": "your-unsplash-access-key"
        }
      }
    }
  },
  "cron": {
    "jobs": [
      {
        "id": "wp-morning-news",
        "schedule": "0 10 * * 1-5",
        "prompt": "Execute wordpress-remote-news-publisher. Select topic from rotation.",
        "channel": "telegram"
      },
      {
        "id": "wp-afternoon-news",
        "schedule": "0 16 * * 1-5",
        "prompt": "Execute wordpress-remote-news-publisher for afternoon edition.",
        "channel": "telegram"
      }
    ]
  }
}
```

---

## Summary

This skill enables fully automated WordPress publishing without requiring WP-CLI on the local machine. All WordPress operations execute remotely via SSH, images process locally and transfer via SCP, and the connection uses public key authentication for security and automation.
