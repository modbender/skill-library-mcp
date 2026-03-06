---
name: tweet-composer
description: >
  Score and optimize tweets based on X's real open-source ranking algorithm.
  Analyzes draft tweets against the actual ranking code — not generic tips.
  Use when: composing tweets, optimizing drafts for reach, planning threads,
  analyzing why a tweet performed well/poorly, or asking for posting strategy advice.
---

# Tweet Composer

Score and optimize tweets using rules derived from X's open-source ranking algorithm.

## How It Works

X's "For You" feed is ranked by a Grok-based transformer (Phoenix) that predicts 19 engagement
actions for every candidate tweet. The final score is a weighted sum of these predictions.
This skill encodes the structural rules from that pipeline into a scoring system.

For the full algorithm breakdown, read `references/algorithm-rules.md`.

## Scoring a Draft Tweet

When a user asks to score or optimize a tweet draft:

1. Read `references/algorithm-rules.md` for the complete rules engine
2. Analyze the draft against all rules
3. Output the score card in this format:

```
🐦 Tweet Composer — Score: XX/100

[Category scores with ✅ ⚠️ ❌ indicators]

📊 Predicted Action Boost:
├─ P(reply): [assessment]
├─ P(favorite): [assessment]  
├─ P(share): [assessment]
├─ P(dwell): [assessment]
└─ P(not_interested): [assessment]

💡 Suggestions:
→ [actionable improvements]

✏️ Optimized version:
"[rewritten tweet]"
```

## Scoring Rubric (Quick Reference)

Score 0-100 based on weighted categories:

| Category | Weight | What to check |
|----------|--------|---------------|
| Reply potential | 25 | Questions, opinions, CTAs that drive replies |
| Media | 20 | Native image/video attached (not link previews) |
| Shareability | 15 | Would someone DM this or copy the link? |
| Dwell time | 15 | Length that makes people stop scrolling |
| Content quality | 10 | Clear, original, not generic |
| Format | 10 | No links in body, no hashtags, good length |
| Negative signals | 5 | Risk of not_interested/mute/block |

## Thread Optimization

When composing threads:
- First tweet = strongest hook (DedupConversationFilter keeps only the best per conversation)
- 3-6 tweets max (short threads > mega-threads)
- Each tweet self-contained (many see only the first)
- Media on tweet 1 or 2 for photo_expand boost
- CTA in last tweet

## Quick Rules (No Reference File Needed)

- **Links:** Always in reply, never in body (learned penalty from lower engagement)
- **Hashtags:** Zero. The model learns they reduce engagement
- **Length:** 100-200 chars sweet spot for single tweets
- **Media:** Native image/video = separate P(photo_expand) and P(video_quality_view) predictions
- **Video:** Must exceed minimum duration threshold for VQV weight to apply
- **Timing:** Post when your audience is active — engagement velocity in first 30 min is critical
- **Frequency:** AuthorDiversityScorer penalizes exponentially: 2nd post ~55% score, 3rd ~33%. Max 3-4 strong tweets/day
- **Quote tweets:** P(quote) has dedicated weight — QTs with added value outperform plain retweets
- **Engagement bait:** Questions/polls drive P(reply). "What would you add?" > "Like if you agree"
