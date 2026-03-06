# Fitbit Fitness Insights - Clawdbot Skill

🏋️ AI-powered insights from your Fitbit data!

## What It Does

Ask your AI assistant questions about your fitness data and get intelligent insights:

- 📊 **Activity insights** - "How did I do this week?"
- 💓 **Heart rate analysis** - "What was my heart rate during workouts?"
- 😴 **Sleep tracking** - "How did I sleep last night?"
- 🏃 **Workout analysis** - "Did I exercise today?"
- 📈 **Trend analysis** - "Am I more active on weekdays or weekends?"
- 🎯 **Goal tracking** - "Did I hit my step goal this week?"

## Example Conversations

**You:** "How did I sleep last night?"

**AI:** "You slept 7.9 hours with 96% efficiency. Only woke up twice for 2 minutes total. That's excellent sleep quality! 😴"

---

**You:** "How active was I this week?"

**AI:** "You averaged 8,234 steps/day this week (up 12% from last week!). Hit your 10k goal 4 out of 7 days. You logged CrossFit 3 times with 156 very active minutes total. Solid week! 💪"

## Features

- **Natural language Q&A** - Ask questions naturally, get conversational answers
- **AI-powered insights** - Smart analysis, not just raw numbers
- **Trend detection** - Spots patterns, week-over-week changes
- **No app needed** - Works via Fitbit API directly
- **Privacy-focused** - Read-only access, your data stays private

## Installation

1. **Install the skill:**
   ```bash
   clawdbot skills install fitbit.skill
   ```

2. **Set up Fitbit OAuth** (takes 5 minutes):
   - Register app at https://dev.fitbit.com/apps
   - Get OAuth tokens
   - Configure `fitbit-config.json`

3. **Start asking questions!**
   - "How did I do this week?"
   - "Did I exercise today?"
   - "What was my sleep like?"

Full setup guide included in the skill package.

## What Data You Can Query

- **Activity:** Steps, distance, calories, active minutes, floors
- **Heart Rate:** Resting HR, heart rate zones, workout intensity
- **Sleep:** Duration, efficiency, wake-ups, sleep stages
- **Workouts:** Logged activities, duration, calories burned
- **Trends:** Week-over-week comparisons, patterns, achievements

## Requirements

- Fitbit account with data syncing
- Fitbit OAuth credentials (free developer account)
- Clawdbot with Telegram or other messaging platform
- Python 3 (included with Clawdbot)

## Security & Privacy

- ✅ **Read-only access** - Never writes to your Fitbit account
- ✅ **OAuth 2.0** - Secure token-based authentication
- ✅ **Auto-refresh** - Tokens refresh automatically
- ✅ **No data storage** - Queries on-demand, nothing saved
- ✅ **Your data** - Stays in your Fitbit account, never shared

## Setup Time

- **5 minutes** for OAuth setup (one-time)
- **Auto-refresh** - Tokens managed automatically
- **Zero maintenance** - Just ask questions!

## Use Cases

- Track fitness goals and progress
- Analyze workout effectiveness
- Monitor sleep quality
- Compare activity patterns
- Spot correlations (sleep vs performance)
- Get motivated by achievements

## Technical Details

- **Fitbit Web API integration**
- **OAuth 2.0 with auto-refresh**
- **Python 3** (standard library only, no pip packages)
- **Config-based** token management
- **AI-powered** insight generation

## What's Included

- `fitbit.skill` - Complete skill package
- `README.md` - This file
- `SETUP.md` - Step-by-step OAuth setup guide
- Inside skill:
  - SKILL.md - Full documentation
  - fitbit_api.py - API client
  - refresh_token.py - Auto-refresh system
  - fitbit-oauth-setup.md - OAuth guide

## Support

- **Issues:** https://github.com/clawdbot/clawdbot/issues
- **Community:** https://discord.com/invite/clawd
- **Docs:** https://docs.clawd.bot
- **Fitbit API:** https://dev.fitbit.com/build/reference/web-api/

---

**Ready to get AI-powered fitness insights?** 🏋️✨

Download `fitbit.skill` and start asking questions about your fitness data!

---

*Made with ❤️ for Fitbit users who want smarter fitness tracking*
