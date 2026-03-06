# Setup — Daily News Digest

Read this on first use when `~/daily-news-digest/` doesn't exist or is empty.

## Your Attitude

You're setting up a personalized news command center. The user should feel excited about getting perfectly curated news, delivered exactly how and when they want it.

## Priority Order

### 1. First: Understand Activation Preferences

Early in the conversation, ask:
- "Should I jump in whenever you ask about news or current events?"
- "Want automatic briefings at certain times, or only when you ask?"

Save their answer to `~/daily-news-digest/memory.md` in the Context section.

### 2. Then: News Preferences

Ask open questions about what matters to them:

**Topics:**
- "What topics do you most want to stay on top of? Tech, business, politics, local...?"
- "Anything you want to avoid? Sports, celebrity gossip, specific subjects?"

**Format:**
- "Do you prefer quick bullet points, or fuller summaries with context?"
- "Interested in voice briefings you can listen to?"

**Geography:**
- "Where are you based? I'll make sure to include local news."
- "Any other regions you follow closely?"

### 3. Finally: Schedule (if they want automation)

If they express interest in scheduled briefings:
- "When's your ideal time for a morning briefing? 7am? 8am?"
- "Want evening updates too, or just morning?"
- "Which channel should I deliver to?" (if they use multiple)

Create cron job only after they confirm.

## What You're Saving

After each response, update `~/daily-news-digest/memory.md`:

- Integration preference (proactive vs on-demand)
- Topic interests and exclusions
- Format preference (brief/standard/deep)
- Voice enabled or not
- Geography (location, other regions)
- Schedule and delivery channel (if any)

All preferences stay within the skill's folder.

## Feedback After Each Response

Don't just collect information. After they share something:
1. Acknowledge what they said
2. Show how it shapes their experience
3. Then continue

Example:
> User: "I'm mostly interested in tech and AI, but I'm sick of crypto news"
>
> Good: "Got it — tech and AI front and center, crypto filtered out. I'll pull from sources like Hacker News, The Verge, and MIT Tech Review. Skip the crypto noise completely. What about breaking news from other areas — politics, business — or keep it pure tech?"
>
> Bad: "Okay. What time do you want briefings?"

## When "Done"

Once you know:
1. When to activate (integration)
2. Topics they care about
3. Basic format preference

...you're ready to deliver news. Schedule, sources, and voice are optional enhancements they can add anytime.
