# Yatta! Skill for OpenClaw

> Manage Yatta! tasks, projects, contexts, and productivity tracking from OpenClaw (Clawdbot/Moltbot)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This skill enables OpenClaw agents to interact with [Yatta!](https://yattadone.com), a time-aware task management system. Manage tasks, track delegation, monitor capacity, and get productivity insights—all via API.

**Status:** ✅ **Tested and Verified** (Feb 10, 2026)  
**Real-time Sync:** ✅ API changes appear in UI immediately

## Features

✅ **Full Task Management** - Create, update, complete, and archive tasks  
✅ **Project Organization** - Group related tasks into projects  
✅ **Context Tagging** - Tag tasks with contexts (@work, @home, etc.)  
✅ **Delegation Tracking** - Delegate tasks with automated follow-up reminders  
✅ **Calendar Integration** - View calendar events and capacity  
✅ **Capacity Monitoring** - Track daily capacity and avoid overbooking  
✅ **Analytics** - Get productivity insights, velocity metrics, and streaks  
✅ **Matrix View** - Eisenhower Matrix (do-first, schedule, delegate, eliminate)

## Security

**This skill includes comprehensive security controls:**

- **🔒 Autonomous invocation disabled** - Requires explicit user commands
- **📋 Capability declarations** - Clear documentation of destructive operations
- **🔑 Credential documentation** - API key requirements and security best practices
- **📚 Operation classification** - 24 read-only, 12 destructive operations documented
- **⚠️ Security warnings** - Prominent warnings about data-modifying operations
- **📖 Comprehensive docs** - [API-REFERENCE.md](API-REFERENCE.md) with side effects, undo procedures

**API Key Access:**
- Your Yatta! API key provides full account access
- Store securely (1Password CLI, environment variables)
- Rotate regularly (every 90 days recommended)
- Never commit keys to version control

See [SKILL.md](SKILL.md) for detailed security information and [API-REFERENCE.md](API-REFERENCE.md) for operation-by-operation documentation.

## Installation

### Via ClawdHub (Recommended) ✅

```bash
clawdhub install yatta
```

**Published:** February 10, 2026  
**Version:** 0.1.0  
**Status:** Production-ready

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/chrisagiddings/openclaw-yatta-skill.git
cd openclaw-yatta-skill

# Copy to OpenClaw skills directory
cp -r . ~/.local/share/mise/installs/node/*/lib/node_modules/clawdbot/skills/yatta/
```

## Setup

1. **Get your Yatta! API key:**
   - Log into [Yatta! app](https://app.yatta.com)
   - Go to Settings → API Keys
   - Create new key (e.g., "OpenClaw Integration")
   - Copy the `yatta_...` key

2. **Configure environment variables:**
   ```bash
   export YATTA_API_KEY="yatta_your_key_here"
   export YATTA_API_URL="https://zunahvofybvxpptjkwxk.supabase.co/functions/v1"  # Default
   ```
   
   > **Note:** Currently using direct Supabase URL for reliability. Branded URLs coming in future release.

3. **Test the connection:**
   ```bash
   curl -s "$YATTA_API_URL/tasks" \
     -H "Authorization: Bearer $YATTA_API_KEY" \
     | jq '.[:3]'
   ```

## Quick Start

### List Tasks

```bash
# All tasks
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY"

# Filter by priority
curl -s "$YATTA_API_URL/tasks?priority=high" \
  -H "Authorization: Bearer $YATTA_API_KEY"

# Filter by status
curl -s "$YATTA_API_URL/tasks?status=todo" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

### Create Task

```bash
curl -s "$YATTA_API_URL/tasks" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Finish report",
    "priority": "high",
    "due_date": "2026-02-15",
    "effort_points": 5
  }'
```

### Get Today's Follow-Ups

```bash
curl -s "$YATTA_API_URL/follow-ups" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

### Check Capacity

```bash
curl -s "$YATTA_API_URL/capacity/today" \
  -H "Authorization: Bearer $YATTA_API_KEY"
```

## API Coverage

### ✅ All APIs Fully Functional (9/9)

- [x] **Tasks API** - Full CRUD, filtering, pagination, batch operations ✅
- [x] **Projects API** - Manage projects and project tasks ✅
- [x] **Contexts API** - Tag tasks with contexts ✅
- [x] **Comments API** - Add progress notes to tasks ✅
- [x] **Follow-Ups API** - Track delegated tasks with reminders ✅
- [x] **Calendar API** - Manage calendar subscriptions and events ✅
- [x] **Capacity API** - Monitor daily capacity and utilization ✅
- [x] **Analytics API** - Get insights, velocity, distribution, streaks ✅
- [x] **Matrix API** - Eisenhower Matrix view ✅

**Status:** 100% API coverage verified (Feb 10, 2026)

**Documentation:** 36 operations documented (24 read-only, 12 destructive) - see [API-REFERENCE.md](API-REFERENCE.md)

### Future Enhancements 🚧

- [ ] **Batch Operations** - Batch create, batch assign contexts
- [ ] **API Key Scopes** - Read-only keys, resource-level permissions
- [ ] **Webhooks** - Real-time notifications for task events
- [ ] **Rate Limit Tiers** - Custom rate limits per key

## Documentation

Full documentation available in [`SKILL.md`](./SKILL.md), including:

- Complete API reference for all endpoints
- Request/response examples with `curl` and `jq`
- Common automation patterns
- Error handling and rate limits
- Tips and best practices

## Use Cases

### Daily Briefing

Get your morning overview:
```bash
echo "=== Today's Tasks ==="
curl -s "$YATTA_API_URL/tasks?status=todo&due_date_lte=$(date +%Y-%m-%d)" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "- [\(.priority)] \(.title)"'

echo ""
echo "=== Follow-Ups Due ==="
curl -s "$YATTA_API_URL/follow-ups" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "- \(.title) (delegated to: \(.delegated_to))"'

echo ""
echo "=== Capacity Status ==="
curl -s "$YATTA_API_URL/capacity/today" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '"Utilization: \(.utilization_percent)% - \(.status)"'
```

### Weekly Planning

Review your week:
```bash
WEEK_START=$(date -v+mon "+%Y-%m-%d")
WEEK_END=$(date -v+sun "+%Y-%m-%d")

curl -s "$YATTA_API_URL/capacity?start=$WEEK_START&end=$WEEK_END" \
  -H "Authorization: Bearer $YATTA_API_KEY" \
  | jq -r '.[] | "\(.date): \(.status) (\(.utilization_percent)%)"'
```

### Task Import

Bulk import from CSV or other systems using the API.

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Issues

Found a bug or have a feature request?

- **GitHub Issues:** https://github.com/chrisagiddings/openclaw-yatta-skill/issues
- **Yatta! API Issues:** https://github.com/chrisagiddings/yatta-71c3065c/issues

## License

MIT License - see [LICENSE](./LICENSE) for details

## Links

- **Yatta! App:** https://yattadone.com
- **Yatta! API Docs:** https://yattadone.com/docs/api
- **ClawdHub:** https://clawdhub.com
- **OpenClaw (Clawdbot):** https://github.com/clawdbot/clawdbot

---

**Made with ✅ for OpenClaw**
