---
name: notification-hub
description: Unified notification hub collecting all skill alerts and delivering by priority
author: 무펭이 🐧
---

# notification-hub

**Notification Integration** — Collects all skill notifications centrally and delivers by priority to reduce notification fatigue.

## 🎯 Purpose

Centrally manage diverse notifications from all skills and deliver at appropriate timing and channels based on importance.

## 📥 Notification Sources

Collect all event files from `events/` directory:

```
events/
  ├── health-2026-02-14.json         (health-monitor)
  ├── scrape-result-2026-02-14.json  (data-scraper)
  ├── dm-check-2026-02-14.json       (insta-post)
  ├── competitor-2026-02-14.json     (competitor-watch)
  └── workflow-2026-02-14.json       (skill-composer)
```

## 🚦 Priority Filtering

### 1. `urgent` — Immediate Discord DM

**Conditions:**
- Security issues (abnormal login, suspicious access)
- System errors (OpenClaw down, browser disconnected)
- Cost exceeded (API usage 90%+)
- Critical mentions

**Delivery:**
- Discord DM (channel ID configured in `TOOLS.md`)
- Send immediately (within 1 min)

**Example:**
```
🚨 Urgent: Browser disconnected
Port 18800 not responding. Auto-recovery attempted but failed.
Manual check needed: openclaw browser start
```

### 2. `important` — Include in next heartbeat

**Conditions:**
- New Instagram DMs (unread)
- Trending keyword surge detected
- Competitor launches new service
- Git push needed (10+ unpushed commits)

**Delivery:**
- Include in next heartbeat response (~30 min intervals)
- Bundle multiple notifications in single message

**Example:**
```
📢 3 Updates

📩 2 Instagram DMs (iam.dawn.kim, partner_xyz)
📈 Trend: "AI agent" surging (+150%)
🔄 Git: 12 commits waiting for push
```

### 3. `info` — Include in daily-report only

**Conditions:**
- Regular statistics updates
- Daily token usage
- Completed workflows
- General system logs

**Delivery:**
- Include when daily-report skill executes
- Send summary once daily

**Example:**
```
📊 Daily Report (2026-02-14)

✅ 3 workflows completed
📊 Tokens: 45,230 / 100,000 (45%)
📝 Memory: 3.2 GB
🔧 Health check: OK
```

## 🔕 Duplicate Prevention

Never send notification more than once for same event.

### Duplicate Detection

```json
{
  "event_id": "health-check-2026-02-14-07:00",
  "fingerprint": "sha256(source + type + key_data)",
  "notified_at": "2026-02-14T07:05:00+09:00"
}
```

### History Storage

```
memory/notifications/
  ├── sent-2026-02-14.json
  ├── sent-2026-02-13.json
  └── ...
```

**sent-YYYY-MM-DD.json structure:**
```json
{
  "date": "2026-02-14",
  "notifications": [
    {
      "id": "health-check-2026-02-14-07:00",
      "priority": "info",
      "sent_at": "2026-02-14T07:05:00+09:00",
      "channel": "discord_dm",
      "source": "health-monitor"
    }
  ]
}
```

## 📢 Delivery Channels

### Discord DM
- **Channel ID**: Configure in `TOOLS.md`
- **Purpose**: urgent, important notifications
- **Format**: Markdown (emoji + title + content)

### Heartbeat Response
- **Purpose**: Bundle important notifications
- **Format**: Concise bullet list

### Daily Report
- **Purpose**: info notification summary
- **Format**: Structured section organization

## 🎤 Triggers

Activate skill with these keywords:

- "notification settings"
- "notification"
- "check notifications"
- "anything new"

## 🚀 Usage Examples

### Check Notifications
```
"Anything new?"
→ Immediately summarize important+ notifications
```

### Notification Settings
```
"Set Instagram DMs to immediate notification"
→ Promote dm-check events to urgent
```

### Notification History
```
"Show today's notification history"
→ Read memory/notifications/sent-2026-02-14.json
```

## ⚙️ Implementation Guide

### 1. Collect Events
```javascript
// Scan events/ directory
const events = fs.readdirSync('events/')
  .filter(f => f.endsWith('.json'))
  .map(f => JSON.parse(fs.readFileSync(`events/${f}`)));
```

### 2. Classify by Priority
```javascript
const urgent = events.filter(e => e.priority === 'urgent');
const important = events.filter(e => e.priority === 'important');
const info = events.filter(e => e.priority === 'info');
```

### 3. Duplicate Check
```javascript
const sent = loadSentHistory(today);
const newEvents = events.filter(e => 
  !sent.notifications.some(n => n.id === e.id)
);
```

### 4. Deliver
```javascript
// urgent → Immediate Discord DM
if (urgent.length > 0) {
  await sendDiscordDM(urgent);
}

// important → Add to heartbeat queue
if (important.length > 0) {
  await addToHeartbeatQueue(important);
}

// info → Add to daily-report queue
if (info.length > 0) {
  await addToDailyReportQueue(info);
}
```

### 5. Save History
```javascript
saveSentHistory(today, newlySentNotifications);
```

## 📊 Event Priority Guide

Guide each skill to include `priority` field when creating events:

```json
{
  "timestamp": "2026-02-14T07:58:00+09:00",
  "skill": "health-monitor",
  "priority": "urgent",  // urgent | important | info
  "message": "Browser disconnected",
  "data": { ... }
}
```

---

> 🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
