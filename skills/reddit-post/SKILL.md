# Reddit Post Skill

## Use When
Moving APPROVED drafts to shared/posted/ after Luka has manually posted them. Archiving. Updating active-tasks.md.

## Don't Use When
Anything involving actually submitting content to Reddit — that is Luka's job, always. This skill handles post-posting bookkeeping only.

---

## Workflow

### After Luka Posts

Luka will notify via Telegram with the Reddit URL of the posted content.

When you receive confirmation:
1. Read the corresponding decision file in shared/decisions/ (status: APPROVED)
2. Copy the draft from shared/pending/ to shared/posted/
3. Add the live Reddit URL to the top of the posted file
4. Delete the original from shared/pending/
5. Update shared/memory/active-tasks.md — move from "Pending Decisions" to "Recently Completed"
6. Log to today's daily log: `shared/memory/[YYYY-MM-DD].md`

### Posted File Format

```markdown
---
subreddit: r/thetagang
posted_at: 2026-02-19T10:23:00
reddit_url: https://www.reddit.com/r/thetagang/comments/[id]/[slug]/
approved_by: Luka
---

[Original draft content]
```

---

## Outcome Tracking

When Luka provides feedback after a post (reactions, upvotes, comments, rejections by mods), write a lesson signal to shared/memory/active-tasks.md in this format:

```
LESSON SIGNAL — [date]
Subreddit: r/thetagang
Post: shared/posted/[filename]
Outcome: [approved by mods / removed / X upvotes / strong comments / weak engagement]
Signal: [what this tells us — pattern or anti-pattern]
```

Manager will promote these signals into lessons.md on Sunday curation.

---

## What You Never Do

- Never submit a post to Reddit yourself — Luka posts manually, always
- Never move a draft to posted/ without a Reddit URL from Luka confirming it was posted
- Never delete from pending/ until you have confirmed the file is in posted/
