# Setup Guide

## 1. Install dependency

```bash
npm install @wenyan-md/core
```

## 2. Configure credentials

**Option A — Environment variables (recommended for CI/cron):**
```bash
export WECHAT_APP_ID=your_appid
export WECHAT_APP_SECRET=your_appsecret
export WECHAT_AUTHOR="Your Name"  # optional, shown as article author
```

**Option B — Credentials file:**
```bash
mkdir -p ~/.config/wechat-mp
cat > ~/.config/wechat-mp/credentials.json << 'EOF'
{
  "appId": "your_appid",
  "appSecret": "your_appsecret"
}
EOF
```

## 3. Whitelist your server IP

In WeChat MP backend → Development → Basic Config → IP Whitelist → add your server IP.

Check your IP: `curl ifconfig.me`

## 4. Basic usage

```bash
# Push single article to draft box
node publish.mjs article.md

# Push main article + sub-article (combined draft)
node publish.mjs deep-article.md quick-news.md

# Dry run (HTML preview, no upload)
node publish.mjs article.md --dry-run

# Push draft AND publish immediately
node publish.mjs article.md --publish

# Publish an existing draft by media_id
node publish.mjs --media-id=xxx
```

## 5. Cron automation example

```bash
# Daily push at 6am (Beijing)
# crontab -e
0 22 * * * cd /your/project && node publish.mjs articles/deep.md articles/news.md >> /var/log/wechat-push.log 2>&1
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ip not in whitelist` | Add your server IP to WeChat MP whitelist |
| `invalid credential` | Check appId / appSecret |
| `Cover fetch failed` | Normal — fallback covers activate automatically |
| `renderStyledContent is not a function` | Run `npm install @wenyan-md/core` |
