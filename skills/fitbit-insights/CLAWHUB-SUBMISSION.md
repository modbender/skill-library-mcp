# Fitbit Fitness Insights - ClawHub Submission

## Basic Info

**Skill Name:** Fitbit Fitness Insights  
**Category:** Health & Fitness / Productivity  
**Version:** 1.0.0  
**Author:** Ryan Burns (@poisondminds)  
**License:** MIT

## Short Description (1 line)

AI-powered Fitbit insights with natural language Q&A - ask about your fitness, get intelligent answers.

## Long Description

Fitbit Fitness Insights brings AI-powered analysis to your fitness data. Instead of checking graphs and numbers in the Fitbit app, simply ask questions and get conversational insights.

**Key Features:**
- 🤖 Natural language Q&A - "How did I sleep?" "Did I hit my goals?"
- 📊 Activity insights - Steps, calories, active minutes, distance
- 💓 Heart rate analysis - Resting HR, zones, workout intensity
- 😴 Sleep tracking - Duration, efficiency, wake-ups, sleep stages
- 🏃 Workout analysis - Logged activities, duration, calories
- 📈 Trend detection - Week-over-week, patterns, achievements

**How It Works:**
1. Ask your AI assistant fitness questions
2. Skill fetches data from Fitbit API
3. AI analyzes and generates insights
4. Get conversational answers, not just numbers

**Example Conversations:**

*"How did I sleep last night?"*
→ "You slept 7.9 hours with 96% efficiency. Only woke up twice for 2 minutes total. That's excellent sleep quality! 😴"

*"How active was I this week?"*
→ "You averaged 8,234 steps/day (up 12% from last week!). Hit your 10k goal 4/7 days. CrossFit 3x with 156 very active minutes. Solid week! 💪"

**Perfect for:**
- Fitness enthusiasts who want deeper insights
- People tracking health goals
- Anyone tired of checking the Fitbit app constantly
- Those who prefer conversational data over charts

## Screenshots/Demo

(Text example conversation - see Long Description above)

## Requirements

**Platform:**
- Clawdbot with messaging integration

**Dependencies:**
- Fitbit account with syncing device
- Fitbit OAuth credentials (free developer account)
- Python 3 (standard library only)

**Setup Time:** ~5 minutes (one-time OAuth setup)

## Installation Instructions

1. **Install skill:**
   ```bash
   clawdbot skills install fitbit.skill
   ```

2. **Set up Fitbit OAuth:**
   - Register app at https://dev.fitbit.com/apps (2 minutes)
   - Get OAuth tokens
   - Configure `fitbit-config.json`

3. **Start asking:**
   - "How did I do this week?"
   - "Did I exercise today?"
   - "What was my sleep like?"

Full setup guide included in download (SETUP.md).

## Tags/Keywords

fitbit, fitness, health, sleep, activity, heart-rate, workouts, ai-insights, oauth, wellness, tracking, goals, natural-language, qa, conversational

## Technical Details

**Data Accessed:**
- Activity (steps, distance, calories, active minutes)
- Heart rate (resting, zones)
- Sleep (duration, efficiency, stages)
- Workouts (logged activities)

**Security:**
- OAuth 2.0 authentication
- Read-only access
- Auto-refreshing tokens
- No data storage/caching
- Queries on-demand only

**Performance:**
- Real-time data fetching
- 1-2 second response time
- 150 requests/hour limit (Fitbit API)

## Support

**Documentation:** Included in skill package  
**Issues:** https://github.com/poisondminds/clawdbot-fitbit-insights  
**Community:** https://discord.com/invite/clawd  

## File

**Filename:** fitbit.skill  
**Size:** 9.6 KB  
**Format:** .skill (Clawdbot skill package)

## Why This Skill?

The Fitbit app shows data, but no AI analysis. This skill:
- Answers questions conversationally
- Identifies trends you'd miss
- Compares week-over-week automatically  
- Provides motivation via insights
- No app checking needed - just ask!

**Result:** Smarter fitness tracking with AI-powered insights! 🏋️✨

---

## Submission Checklist

- [x] Skill file ready (fitbit.skill)
- [x] Description complete
- [x] Demo conversation provided
- [x] Installation instructions clear
- [x] Dependencies listed
- [x] Support links included
- [x] Tags/keywords added
- [x] No sensitive data in package
- [x] Tested and working

**Status:** Ready to submit! ✅
