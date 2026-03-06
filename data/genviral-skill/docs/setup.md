# Setup Guide

This guide is for agents helping users get started with Genviral. Read this during onboarding and walk your human through it conversationally.

## What to Tell Your Human First

Before anything else, explain:

> Everything you do through this skill (posts, slideshows, image packs, scheduled content) shows up in the Genviral dashboard at genviral.io. You can always see, edit, or manage things in the UI. The agent and the dashboard are two views of the same system.

This is important. People worry about agents doing things they can't see or control. Reassure them.

---

## Onboarding Flow

Follow these phases in order. Each phase is conversational -- ask questions, listen, then move forward. Do not dump a checklist on them.

### Phase 1: Get to Know Their Product

Before touching any config or API, understand what you are working with.

Ask these questions naturally (not all at once -- let it be a conversation):

- "What's the product? Give me the one-sentence pitch."
- "Who is it for? What kind of person downloads or buys it?"
- "What problem does it solve? What is the pain before they find this product?"
- "What are the 2-3 features people actually care about?"
- "Do you have any social media presence already? What's worked before, if anything?"
- "What's the website or app store link?"

As they answer, fill in `workspace/context/product.md` and `workspace/context/brand-voice.md`. You are building the foundation that every piece of content will reference.

Do not rush this phase. A weak product brief produces weak content. A good one makes everything downstream easier.

### Phase 2: Competitor Research

Before creating any content, understand the competitive landscape. This takes 15-20 minutes and saves weeks of guessing.

Read `docs/references/competitor-research.md` for the full process. The short version:

1. Run `genviral.sh trend-brief --keyword "NICHE" --range 7d --limit 10` (and optionally `24h`) for fast niche intelligence.
2. Ask: "Who else is making content for this niche? Any accounts you admire or follow?"
3. Use the browser tool to search TikTok (and Instagram if relevant) for the niche keywords.
4. Find 3-5 accounts posting in this space.
5. Analyze their top content: what hooks work, what formats dominate, what view baseline looks like.
6. Identify gaps: what is nobody doing?

Save findings to `workspace/performance/competitor-insights.md`.

Tell your human what you found: "In this niche, most content uses relatable-pain hooks and talking-head videos. Nobody is doing educational slideshows. That is our opening."

This research shapes every creative decision from here on.

### Phase 3: Image and Content Strategy

Now figure out the visual approach.

**First, set up API access:**

Get the API key from https://www.genviral.io (Settings > API Keys), then:

```bash
export GENVIRAL_API_KEY="your_public_id.your_secret"
```

Test it:
```bash
genviral.sh accounts
```

If this returns connected accounts, you are good.

**Then, discuss image strategy.** Do NOT hardcode a pack without asking. Explain the options:

**Option A: Use an existing image pack**
```bash
genviral.sh list-packs
```
Show them what is available. If they like one, great. Set it in config or pass it per-slideshow.

**Option B: Create a new pack**
Ask what kind of images fit their brand. Then either:
- Help them upload images: `genviral.sh create-pack --name "My Pack"` then `genviral.sh add-pack-image --pack-id X --image-url "https://..."`
- Suggest they create one in the Genviral UI (easier for bulk uploads)

**Option C: Generate images per post**
The agent can generate images (via OpenAI, etc.) for each slideshow instead of pulling from a pack. No pack needed. More variety, less visual consistency.

**Option D: Mix and match**
Use a pack for some posts, generate fresh images for others. The agent decides based on content needs.

Set the account IDs in `defaults.yaml`:
```yaml
posting:
  default_account_ids: "ACCOUNT_ID_1"  # comma-separated for multiple
```

### Phase 4: First Test Slideshow

Make the first post together. This is iterative -- do not aim for perfect on the first try.

1. Pick a hook from `workspace/hooks/library.json` or brainstorm one based on competitor research
2. Pick a template from `docs/prompts/slideshow.md`
3. Generate the slideshow, review the slides together, refine until it looks right
4. Post as a TikTok draft (so they can add trending audio before publishing)

```bash
genviral.sh generate --prompt "Your prompt here" --pack-id PACK_ID --slides 5
genviral.sh render --id SLIDESHOW_ID
genviral.sh create-post --caption "your caption" --media-type slideshow --media-urls "url1,url2,..." --accounts ACCOUNT_ID --tiktok-post-mode MEDIA_UPLOAD --tiktok-privacy SELF_ONLY
```

After posting, log the hook text, category, and CTA to `workspace/performance/hook-tracker.json`. This is the start of the feedback loop.

Remind them: for TikTok, posting as a draft lets them add trending music before publishing. That is usually the best workflow.

### Phase 5: Set Up the Feedback Loop

The skill gets smarter over time, but only if you actually track results.

After the first post goes live (give it 48-72 hours minimum before checking):

1. Pull analytics: `genviral.sh analytics-posts --range 7d --sort-by views --sort-order desc`
2. Update `workspace/performance/hook-tracker.json` with the actual view and engagement numbers
3. Apply the diagnostic framework (see `docs/references/analytics-loop.md`)
4. Set up a weekly review routine -- every Monday, check the previous week's posts and adjust the content plan

Explain this to your human:
> "We will check how each post performs after a few days and use that data to figure out what hooks and formats to double down on. It takes a few weeks to build enough data to see patterns, but once we do, the content gets measurably better."

---

## TikTok Account Warmup (New Accounts Only)

If your human is using a brand-new TikTok account, do NOT post immediately. New accounts need to warm up first or the algorithm will suppress content.

**Warmup period: 7-14 days of normal usage before any posting.**

What to do during warmup:
- Scroll the For You page normally for 10-15 minutes per day
- Like content sparingly (about 1 in every 10 videos, not every single one)
- Follow 5-10 accounts in the niche
- Leave a few genuine, non-spammy comments per day
- Do NOT post, do NOT go to the profile repeatedly, do NOT make the account look like a bot

**Signal that the account is ready:** The For You page starts showing mostly niche-relevant content (the algorithm has figured out the account's interests). When 70%+ of recommended content matches the target niche, the account is warmed up.

Tell your human: "A new account that starts posting immediately gets worse distribution. Give it 1-2 weeks of normal usage first. We can use that time to get content ready."

**Skip warmup entirely for established accounts** (any account with existing followers and posting history). This only applies to brand-new accounts.

---

## What's Next?

Once they are posting, the agent can:
- Set up a daily content cron (see **Cron Setup** section below)
- Track performance via analytics and update `workspace/performance/hook-tracker.json`
- Run weekly strategy reviews (see `docs/references/analytics-loop.md`)
- Build and refine the hook library based on what actually works
- Research competitors periodically to stay ahead of niche trends

The skill self-improves over time. The more it posts and tracks, the better it gets at picking hooks, timing, and format.

---

## Onboarding Tone

Be helpful, not overwhelming. Do not dump all 42 commands on them. The conversation should feel like:

1. "Tell me about your product and who it's for."
2. "Let me look at what's working in your niche right now."
3. "What kind of images do you want to use?"
4. "Let's make your first post together."
5. "Here's how we'll track what works."

That's it. Everything else comes naturally as they use the skill.

---

## Cron Setup

Automate the content pipeline with OpenClaw cron jobs so content gets generated, posted, and reviewed without manual intervention.

### Recommended Schedule

| Job | Frequency | What it does |
|-----|-----------|-------------|
| **Daily Content** | Every day at 9:00 AM | Generate, render, review, and post a slideshow |
| **Performance Check** | Every day at 6:00 PM | Pull analytics, log metrics for recent posts |
| **Weekly Review** | Every Sunday at 10:00 AM | Analyze the week, update hook weights, plan next week |

### 0. Daily Skill Update (run first)

Keep the skill itself current automatically:

```bash
openclaw cron add \
  --name "Genviral: Daily Skill Update" \
  --cron "0 6 * * *" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the genviral skill self-updater: bash scripts/update-skill.sh. It will check for updates to SKILL.md, scripts/, and docs/ from the upstream repo and apply them. Never touches workspace/. Report what was updated or confirm already up to date." \
  --announce
```

### 1. Daily Content Generation

Replace `YOUR_TIMEZONE` (e.g. `Europe/Brussels`, `America/New_York`).

```bash
openclaw cron add \
  --name "Genviral: Daily Content" \
  --cron "0 9 * * *" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the Genviral daily content pipeline. Read the genviral SKILL.md, then: 1) Pick a topic from workspace/content/scratchpad.md or generate a new one based on workspace/performance/insights.md. 2) Generate a slideshow with a strong hook using pinned_images. 3) Render all slides. 4) Review each slide visually — if any slide is below quality, fix it before continuing. 5) Post to the default account. 6) Log the post in workspace/performance/log.json and tag the hook in workspace/performance/hook-tracker.json." \
  --announce
```

### 2. Daily Performance Check

```bash
openclaw cron add \
  --name "Genviral: Performance Check" \
  --cron "0 18 * * *" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the Genviral performance check. Read the genviral SKILL.md, then: 1) Run analytics-summary to get overall stats. 2) Run analytics-posts to get individual post metrics. 3) Update workspace/performance/log.json with latest metrics for posts older than 24h. 4) Update workspace/performance/hook-tracker.json with real view/engagement numbers. 5) If any post significantly outperformed or underperformed, note why in workspace/performance/insights.md. 6) Report a brief summary." \
  --announce
```

### 3. Weekly Strategy Review

```bash
openclaw cron add \
  --name "Genviral: Weekly Review" \
  --cron "0 10 * * 0" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the Genviral weekly review. Read the genviral SKILL.md, then: 1) Analyze all posts from the past 7 days in workspace/performance/log.json. 2) Identify top 3 and bottom 3 performers. 3) Update hook weights in workspace/hooks/library.json (increase for high engagement, decrease for underperformers). 4) Update workspace/performance/insights.md with this week's learnings. 5) Generate 5 new content ideas for next week in workspace/content/scratchpad.md. 6) Write the weekly review in workspace/performance/weekly-review.md." \
  --announce
```

### Customization

- **2 posts/day:** Change daily cron to `0 9,15 * * *` (9 AM and 3 PM)
- **Platform targeting:** Add platform-specific instructions to the message (e.g. "Post to TikTok vertical format" or "Instagram 4:5")
- **Content themes:** Add a theme schedule to `workspace/content/calendar.json` and reference it in the daily message

### Verify Setup

```bash
openclaw cron list                    # list all jobs
openclaw cron run <job-id> --force    # test a job manually
openclaw cron runs --id <job-id>      # check run history
```


## Without OpenClaw

If you're using the skill outside OpenClaw, you can still automate with system cron jobs or any scheduler/orchestrator:

- Run `scripts/genviral.sh` commands directly in your own cron jobs
- Or run an agent runner with the same prompts used above
- Keep the same guardrails: pinned_images, visual review gate, and performance logging in `workspace/performance/log.json`

