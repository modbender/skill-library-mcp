# MILKEE Skill - Complete Package

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Date**: 2026-01-17  

---

## 📦 Package Contents

This ZIP contains everything you need to use the MILKEE skill with Clawdbot.

```
├── milkee.skill              ← The skill (upload to Skill Hub)
├── README.md                 ← This file
└── INSTALLATION_GUIDE.md     ← Setup instructions
```

---

## 🚀 Quick Start

### Option A: Upload to Skill Hub (Recommended)

1. Extract `milkee.skill` from this ZIP
2. Go to your Skill Hub
3. Click "Upload New Skill"
4. Select `milkee.skill`
5. Fill metadata:
   - **Name**: `milkee`
   - **Category**: `Accounting / Time Tracking`
   - **Tags**: `time-tracking, accounting, projects, swiss`
6. Publish!

### Option B: Manual Installation

1. Extract to `~/.clawdbot/skills/milkee/`
2. Configure in `~/.clawdbot/clawdbot.json`:
   ```json
   {
     "skills": {
       "milkee": {
         "env": {
           "MILKEE_API_TOKEN": "USER_ID|API_KEY",
           "MILKEE_COMPANY_ID": "YOUR_COMPANY_ID"
         }
       }
     }
   }
   ```
3. Test: `python3 scripts/milkee.py list_projects`

See `INSTALLATION_GUIDE.md` for details.

---

## ✨ Features

- ⏱️ Time tracking with smart fuzzy project matching
- 👥 Customer management
- 📋 Project management
- ✅ Task management
- 📦 Product management
- 📊 Daily time summaries
- 🚀 No external dependencies

---

## 📖 Documentation

Inside `milkee.skill` you'll find:
- **SKILL.md** - Complete documentation
- **scripts/milkee.py** - CLI tool
- **references/configuration.md** - Setup guide
- **references/api-endpoints.md** - API reference

---

## 🔧 Configuration

Get credentials from MILKEE:
1. Log in to MILKEE (https://app.milkee.ch)
2. Settings → API Settings
3. Copy: User ID | API Key
4. Check URL for Company ID

See `INSTALLATION_GUIDE.md` for step-by-step instructions.

---

## 💡 Usage

```bash
# Start timer
python3 scripts/milkee.py start_timer "ProjectName" "What you're working on"

# Stop timer
python3 scripts/milkee.py stop_timer

# View today's times
python3 scripts/milkee.py list_times_today
```

See inside `milkee.skill` for complete command reference.

---

## 📚 Official Documentation

- MILKEE API: https://apidocs.milkee.ch/api
- Authentication: https://apidocs.milkee.ch/api/authentifizierung.html

---

## 👤 Created By

**Seal** 🦭 | 2026-01-17

**Happy time tracking!** ⏱️🚀
