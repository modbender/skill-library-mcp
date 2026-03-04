---
name: openclaw-diary
version: 1.0.0
description: |
  Set up and manage OpenClaw auto learning diary. Used for:
  (1) Help users fork OpenClaw-Diary repository
  (2) Connect the forked repo to OpenClaw
  (3) Configure daily cron task to auto-write diary
  (4) Deploy to GitHub Pages
---

# 🦞 OpenClaw-Diary Setup Guide

Help users set up OpenClaw auto learning diary with this complete workflow.

## ⚠️ Important: Language Response

**Always respond in the same language as the user is speaking!**
- If user writes in Chinese → respond in Chinese
- If user writes in English → respond in English
- Detect language from user's message and match it

## Trigger Conditions

Activate when user mentions:
- "setup diary" / "设置日记"
- "fork OpenClaw-Diary"
- "auto write diary" / "自动写日记"
- "daily learning log" / "每日学习记录"
- "let AI write diary" / "让 AI 写日记"

## Complete Workflow

### Step 1: Guide User to Fork the Repo

Tell user to fork on GitHub:

```
Please fork the repo:
1. Visit https://github.com/YAI-Lab/OpenClaw-Diary
2. Click "Fork" button
3. Select your account, complete fork
```

### Step 2: Get User's Fork URL

Ask for the forked repo URL, format:
```
https://github.com/your-username/OpenClaw-Diary
```

### Step 3: Modify index.html for Personalization (IMPORTANT!)

**After cloning the repo, MUST modify:**

1. **Change page title**: Replace OpenClaw-Diary with user's desired name
2. **Replace robot Logo**: Change 🤖 to 🦞
3. **Change robot name**: Replace with user's robot name

```bash
# Clone repo
git clone https://github.com/username/OpenClaw-Diary.git
cd OpenClaw-Diary

# Replace robot name (based on user input)
sed -i 's/OpenClaw/YourRobotName/g' index.html

# Replace emoji
sed -i 's/🤖/🦞/g' index.html
```

**Example modification:**
```html
<!-- Before -->
<title>OpenClaw-Diary</title>
<h1>🤖 OpenClaw's Learning Diary</h1>

<!-- After -->
<title>MyAI Diary</title>
<h1>🦞 小龙的学习日记</h1>
```

### Step 4: Get GitHub Token

If GitHub token not configured, user needs to create:

1. Visit https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Check `repo` permission
4. Generate and save token

**Important**: Must tell user the purpose when getting token, and how to revoke.

### Step 5: Configure Daily Cron Task

Use cron or heartbeat to configure daily task:

**Method A: Cron Task**
```bash
# Run daily at UTC 1:00 (9:00 Beijing time)
openclaw cron add "0 1 * * *" "Daily Learning Diary" "Read latest AI news, track GitHub stars, generate report and push to OpenClaw-Diary repo"
```

**Method B: Heartbeat Task**
Add to HEARTBEAT.md:
```markdown
## Daily Learning Report
- Research latest AI/tech/politics news
- Track GitHub repo stars growth (if user has repos)
- Generate report in user's language
- Push to OpenClaw-Diary
```

### Track GitHub Stars Growth

As part of the daily report, optionally track GitHub stars:

```bash
# Get current stars
curl -s https://api.github.com/repos/owner/repo | jq '.stargazers_count'

# Track daily growth
# Store in a simple JSON file or append to diary
```

### Step 6: Push to Repo

```bash
# Add remote
git remote add user https://github.com/username/OpenClaw-Diary.git

# Commit changes
git add index.html
git commit -m "docs: $(date '+%Y-%m-%d') learning diary"
git push user main
```

### Step 7: Enable GitHub Pages

1. Go to user's forked repo
2. Settings → Pages
3. Source: Deploy from a branch
4. Branch: main, folder: / (root)
5. Save, wait for deployment

## Daily Diary Content Template

Content format to push:

```html
<!-- Date Navigation -->
<div class="date-tabs">
  <button onclick="showDate('2026-03-03')">📅 2026-03-03</button>
</div>

<!-- Daily Content -->
<div class="screen" id="screen-2026-03-03">
  <div class="entry">
    <div class="entry-bar">
      <span class="entry-filename">~/2026-03-03/learning.md</span>
    </div>
    <div class="entry-body">
      <div class="quote-box">
        <div class="quote-title">💡 Today's Learning</div>
        <p>Today's learning content...</p>
      </div>
      <div class="quote-box">
        <div class="quote-title">⭐ GitHub Stars Growth</div>
        <ul>
          <li>openclaw/openclaw: 1200 ⬆️ (+15 this week)</li>
          <li>YAI-Lab/OpenClaw-Diary: 45 ⬆️ (+5 today)</li>
        </ul>
      </div>
    </div>
  </div>
</div>
```

## Privacy Protection (MUST FOLLOW)

**Strictly prohibit leaking:**
- User's real name, ID card, phone number
- User's password, API Key, Token
- User's private conversation content

**Operating principles:**
- All content must be published with user consent
- When uncertain, ask user first

## Configuration

| Config | Description | How to Get |
|--------|-------------|------------|
| FORK_URL | User's forked repo | User provides |
| GITHUB_TOKEN | GitHub PAT | User creates |
| CRON_SCHEDULE | Task schedule | Default UTC 1:00 |

## Checklist

After setup, confirm:
- [ ] User forked repo
- [ ] Got fork URL
- [ ] Modified index.html (replaced 🦞)
- [ ] Got GitHub Token
- [ ] Configured daily task
- [ ] GitHub Pages enabled
- [ ] Test push successful
