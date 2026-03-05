# Analytics Feedback Loop

The genviral skill has full analytics built in. Use it. This document explains how to pull data, cross-reference it with `workspace/performance/hook-tracker.json`, and make decisions that improve content over time.

---

## The Core Idea

Every post is a data point. After enough posts, patterns emerge: certain hook categories consistently outperform others, certain CTAs drive more engagement, certain formats hit better in certain niches.

The job is to close the loop. Post content, track what happens, adjust based on results. This is not complicated -- it just requires discipline to actually do it.---

## Available Analytics Commands

### KPI Summary
```bash
genviral.sh analytics-summary --range 30d
genviral.sh analytics-summary --range 7d --platforms tiktok
genviral.sh analytics-summary --start 2026-01-01 --end 2026-01-31 --json
```

Use this for high-level trends:
- Are views trending up or down week over week?
- Is engagement rate improving?
- How many posts published in the period?
- Which platform is performing better?

### Per-Post Metrics
```bash
genviral.sh analytics-posts --range 30d --sort-by views --sort-order desc --limit 50
genviral.sh analytics-posts --range 7d --platforms tiktok --json
```

Use this to see individual post performance. Sort by views descending to immediately surface winners.

The output gives you per-post: views, likes, comments, shares, saves, and published timestamp.

Cross-reference the post IDs here with entries in `workspace/performance/hook-tracker.json` to connect metrics back to the specific hook, hook category, and CTA used.

---

## Pulling and Cross-Referencing Data

**Step 1: Pull post-level analytics**
```bash
genviral.sh analytics-posts --range 30d --sort-by views --sort-order desc --json
```

Save or parse the output. For each post, note:
- `post_id`
- `views`
- `likes`
- `comments`
- `shares`
- `saves`

**Step 2: Match to hook-tracker**

Open `workspace/performance/hook-tracker.json`. Find each post by `post_id`. Update the `metrics` block:
```json
{
  "views": 47200,
  "likes": 1340,
  "comments": 89,
  "shares": 230,
  "saves": 410,
  "last_checked": "2026-02-17T10:00:00Z"
}
```

Set `status` to `tracking` (data collected, not yet reviewed) or `reviewed` (reviewed in a weekly session).

**Step 3: Calculate engagement rate**

Engagement rate = (likes + comments + shares + saves) / views

This is the key signal for whether content resonates beyond just getting served by the algorithm.

---

## The Diagnostic Framework

Once you have views and engagement rate for a post, apply this framework:

**High views + High engagement rate**
The hook stopped the scroll AND the content delivered. This is the combination to scale.
Action: Make 3 variations of this hook. Keep the same hook category, same CTA type, try different angles within it.

**High views + Low engagement rate**
The hook is working (algorithm is serving it, people are clicking in). But the content itself or the CTA is not landing.
Action: Keep the hook. Fix the content arc or swap the CTA. Try a different CTA type and see if engagement improves.

**Low views + High engagement rate**
The people who see it love it. But the hook is not stopping the scroll, so the algorithm is not amplifying it.
Action: The content is good. The hook needs reworking. Try a more pattern-interrupting or emotionally direct hook for the same content angle.

**Low views + Low engagement rate**
Neither the hook nor the content is working. This angle is not resonating with this audience on this platform.
Action: Drop this angle. Try something radically different. Do not keep iterating on something that is failing at both signals.

---

## Decision Rules

Apply these rules when deciding what to do with a post after checking metrics:

| Views | Action |
|-------|--------|
| 50K+ | Double down. Make 3 variations of this hook immediately. Move to `rules.double_down` in hook-tracker. |
| 10K - 50K | Keep in rotation. This is working. Keep posting similar content while improving it gradually. Move to `rules.keep_rotating`. |
| 1K - 10K | Test one more variation. Give it another shot with a tweak. Move to `rules.testing`. |
| Under 1K (twice) | Drop it. If a hook fails twice with low views, it is not an algorithm problem, it is a content problem. Move to `rules.dropped`. |

"Views" here means TikTok/Instagram native views -- what the analytics-posts command returns.

Note: "twice" means you tested this hook category or specific hook type in two separate posts and both failed. A single post can have a bad day. Two posts with the same pattern failing is a signal.

---

## Updating hook-tracker.json

After reviewing a post's metrics, update its entry in `workspace/performance/hook-tracker.json`:

1. Fill in the `metrics` block with current data
2. Set `status` to `reviewed`
3. Based on the decision rules above, add the `hook_text` to the appropriate `rules` array:
   - `rules.double_down` - hooks over 50K views
   - `rules.keep_rotating` - hooks in 10K-50K range
   - `rules.testing` - hooks in 1K-10K, being tested again
   - `rules.dropped` - hooks that failed twice

4. Update the aggregate data in `hook_categories`:
   - Increment `total_posts` for the relevant category
   - Recalculate `avg_views` (rolling average is fine)
   - Update `best_post_id` if this post beats the current best

5. Update `cta_performance` for the CTA used:
   - Increment `times_used`
   - Add to `total_views`
   - Recalculate `avg_engagement_rate`

---

## Weekly Review Process

Run this every Monday (or the first day of your content week).

**1. Pull the last 7 days of analytics**
```bash
genviral.sh analytics-summary --range 7d
genviral.sh analytics-posts --range 7d --sort-by views --sort-order desc --json
```

**2. Update hook-tracker with fresh metrics**
For every post from the past week, fill in current views, likes, comments, shares, saves in `hook-tracker.json`.

**3. Categorize each post**
Apply the decision rules. Move hooks to `double_down`, `keep_rotating`, `testing`, or `dropped` based on actual numbers.

**4. Identify the week's winners and losers**
- Top 3 posts by views: what hook categories? What CTAs?
- Bottom 3 posts by views: what patterns do they share?

**5. Look for patterns across categories**
Check `hook_categories` aggregate data in `hook-tracker.json`. After 10+ posts, patterns become clear:
- Which category has the highest `avg_views`?
- Which CTA type in `cta_performance` has the highest `avg_engagement_rate`?

**6. Decide next week's content strategy**
Based on the data:
- Lead with the top-performing hook category
- Make 3 variations of any hook that crossed 50K
- Rotate CTAs for hooks in the testing range to find what converts
- If a category has 3+ posts in `dropped`, stop testing it for now
- Reference `workspace/performance/competitor-insights.md` for niche context

**7. Write a brief review**
Append to `workspace/performance/weekly-review.md`:
```markdown
## Week of [DATE]

**Posts published:** [N]
**Total views this week:** [N]
**Avg views per post:** [N]
**Top performer:** [POST ID] - [VIEWS] views - [HOOK CATEGORY] hook

**What worked:**
- [Hook category / CTA / angle that performed]

**What didn't:**
- [Hook category / format that underperformed]

**Next week's focus:**
- [2-3 specific decisions based on data]
```

---

## Common Mistakes to Avoid

**Checking analytics too early.** TikTok posts can take 24-72 hours to fully distribute. Check at 48 hours minimum, ideally 7 days for a full picture.

**Optimizing on too little data.** One viral post does not make a hook a winner. One failed post does not make it a loser. You need 3+ posts in a category before drawing conclusions.

**Ignoring engagement rate in favor of views.** A post with 100K views and 0.5% engagement is worse long-term than 20K views and 5% engagement. The algorithm learns from engagement signals, not just reach.

**Never updating hook-tracker.** The tracker is only useful if it actually has data. Update it after every performance check.

**Posting without checking what is already in `dropped`.** Do not repeat hooks that already failed twice. Check `rules.dropped` before finalizing a content plan.
