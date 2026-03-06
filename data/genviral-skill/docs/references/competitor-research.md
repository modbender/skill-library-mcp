# Competitor Research Guide

Do this BEFORE creating content for a new product. Understanding the competitive landscape shapes every creative decision: hooks, formats, view baselines, gaps to exploit.

This is not optional busywork. If you skip it, you are guessing. Niche context turns generic content into targeted content that actually performs.

---

## When to Run Competitor Research

- First time setting up the skill for a new product
- When content has been underperforming for 2+ weeks
- When entering a new content angle or format
- When the niche or audience shifts

---

## Step 0: Pull a Trend Brief First (Fast Signal)

Before manual competitor browsing, run trend brief for the niche keyword:

```bash
genviral.sh trend-brief --keyword "YOUR NICHE" --range 7d --limit 10
genviral.sh trend-brief --keyword "YOUR NICHE" --range 24h --limit 10
```

Capture these signals as your starting baseline:
- `summary.top_hashtags`
- `summary.top_sounds`
- `summary.top_creators`
- `summary.posting_windows_utc`
- `recommendations.hook_angles`

This gives instant niche intelligence so your manual deep-dive is focused instead of random.

## Step 1: Define the Niche Keywords

Before searching, nail down what niche you are searching in.

Pull from `workspace/context/product.md`:
- What problem does the product solve?
- Who is the target audience?
- What would someone search for if they had this problem?

Write 3-5 search queries. Examples:
- "budget tracking app tiktok"
- "save money tips"
- "personal finance for beginners"
- "how to stop overspending"

---

## Step 2: Search TikTok for the Niche

Use the browser tool to search TikTok. Do not guess what performs well -- look.

```
browser(action="navigate", url="https://www.tiktok.com/search?q=YOUR+KEYWORD")
browser(action="snapshot")
```

For each keyword:
1. Open TikTok search for the query
2. Take a snapshot of results
3. Note the top 5-10 accounts appearing
4. Identify which accounts post regularly (multiple recent videos)

You are looking for accounts that are clearly in this niche and posting content similar to what you will create.

Also check:
```
browser(action="navigate", url="https://www.tiktok.com/@ACCOUNT_USERNAME")
browser(action="snapshot")
```

Look at their top posts (sorted by views if possible). What is getting traction?

---

## Step 3: Analyze 3-5 Competitor Accounts

For each competitor account you find, answer these questions:

**Account overview:**
- Username and platform (TikTok / Instagram)
- Approximate follower count
- Posting frequency (daily / 3x week / sporadic)
- How long have they been active?

**Content format:**
- What format dominates their top posts? (slideshow, video talking head, screen recordings, voiceovers)
- How many slides in their slideshows?
- Aspect ratio used?
- Do they use text overlays? Heavy or minimal?

**Hook analysis:**
- What is the first line of text on their top 5 posts?
- What hook category does each fall into? (person-conflict, relatable-pain, educational, pov, before-after, feature-spotlight)
- Which hook style appears most in their top-performing content?

**View baseline:**
- What is a typical view count for this account?
- What is their best performing post and why does it likely work?
- What is the floor (posts that bombed)? What seems to cause that?

**CTA patterns:**
- What CTA do they use most? (link in bio, search app name, soft mention, no CTA)
- Do they vary CTAs or stick to one?

**Engagement signals:**
- Are comments mostly from discovery (new people) or fans?
- Are saves high relative to views? (indicates utility content)
- Are shares high? (indicates emotionally resonant or shareable content)

---

## Step 4: Gap Analysis

After analyzing 3-5 competitors, identify what nobody is doing.

Ask:
- Which hook categories are overused in this niche? (avoid those, or do them significantly better)
- Which hook categories are barely used? (opportunity)
- What angles is nobody taking? (different audience subsets, different pain points, different tones)
- What format is missing? (if everyone does video, slideshows stand out -- and vice versa)
- Is there an emotional angle nobody is hitting? (humor, frustration, aspiration, nostalgia)
- Are competitors making content errors? (low readability, weak hooks, no CTA) - these are free wins

Write down 2-3 specific gaps you can exploit.

---

## Step 5: Save Findings

Save competitor research to `workspace/performance/competitor-insights.md`.

Use this structure:

```markdown
# Competitor Insights - [PRODUCT NAME]

Last updated: [DATE]

## Niche Keywords Searched
- [keyword 1]
- [keyword 2]

## Trend Brief Snapshot
- Top hashtags: [list]
- Top sounds: [list]
- Top creators: [list]
- Best posting windows (UTC): [list]
- Recommended hook angles: [list]

## Competitors Analyzed

### @[account_name] ([PLATFORM])
- Followers: ~[NUMBER]
- Posting: [FREQUENCY]
- Top format: [FORMAT]
- Top hook categories: [CATEGORIES]
- View baseline: [RANGE]
- Best post: [URL or description]
- Notes: [anything notable]

### @[account_name] ([PLATFORM])
...

## View Baseline for This Niche
- Average performing post: [RANGE]
- Good post: [RANGE]
- Viral for this niche: [RANGE]

## Hook Analysis
- Most common hook category: [CATEGORY]
- Least used hook category: [CATEGORY]
- Hook patterns that consistently work: [EXAMPLES]

## Gaps to Exploit
1. [GAP 1 - specific]
2. [GAP 2 - specific]
3. [GAP 3 - specific]

## Implications for Content Strategy
- Lead with [HOOK CATEGORY] since competitors underuse it
- Avoid [HOOK CATEGORY] unless we do it significantly better
- Target [AUDIENCE SUBSET] that competitors are ignoring
- Use [FORMAT] since competitors mostly use [OTHER FORMAT]
```

---

## Step 6: Use Competitor Data When Creating Content

Every time you write a hook, check `workspace/performance/competitor-insights.md` first:

- Is this hook category already saturated in the niche?
- What view baseline should I expect for this format?
- Am I targeting a gap, or imitating what everyone else does?

When picking a hook from `workspace/hooks/library.json`, prefer hooks that fill a gap over hooks that replicate what competitors already do.

When writing prompts for slideshow generation, mention the competitive context:
> "Competitors in this niche mostly use relatable-pain hooks. This slideshow should use a before-after format to stand out."

---

## Refresh Schedule

Competitor research goes stale. Refresh it:
- Every 4 weeks for active campaigns
- Any time you notice a format or hook suddenly performing differently than expected
- When starting a new content angle

The niche changes. What works today may be saturated in 6 weeks. Stay current.
