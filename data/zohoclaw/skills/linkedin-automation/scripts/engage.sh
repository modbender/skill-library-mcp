#!/bin/bash
# LinkedIn Engagement Automation
# Usage: ./engage.sh [--limit 10] [--topic keyword]

LIMIT="${1:-10}"
TOPIC="${2:-}"

cat << EOF
🤝 LINKEDIN ENGAGEMENT WORKFLOW
═══════════════════════════════════════

Engage with $LIMIT posts in your feed.

## Workflow Steps (via browser):

1. Navigate to https://www.linkedin.com/feed/

2. Scroll through feed and identify high-quality posts:
   - From people in your network
   - Related to your industry/interests
   $([ -n "$TOPIC" ] && echo "- Containing keyword: $TOPIC")

3. For each qualifying post (up to $LIMIT):

   a) **Like the post** (always do this)
      - Click the Like button (thumbs up)
      - Or use reactions: Celebrate 🎉, Love ❤️, Insightful 💡
   
   b) **Leave a thoughtful comment** (on best posts)
      - Add value, not just "Great post!"
      - Ask a question
      - Share your experience
      - Disagree respectfully (engagement gold)

4. Track engagement:
   - Note who you engaged with
   - They'll likely reciprocate
   - Builds algorithm favor for your content

## Comment Templates:

**Adding perspective:**
"This resonates. In my experience, [related insight]. Have you found [question]?"

**Respectful disagreement:**
"Interesting take. I'd push back slightly on [point] because [reason]. What do you think about [alternative]?"

**Asking questions:**
"Love this. Curious - how did you handle [specific challenge] when [scenario]?"

**Sharing experience:**
"Went through something similar. The game-changer for me was [insight]. [Brief elaboration]."

## Best Practices:

✅ Engage with posts 1-3 hours old (algorithm boost)
✅ Mix reactions (don't just Like everything)
✅ Comment on posts from people slightly ahead of you
✅ Reply to comments on your own posts within 1 hour
✅ Engage before AND after posting your own content

❌ Don't comment "Great post!" (looks like a bot)
❌ Don't mass-like 50 posts in 2 minutes
❌ Don't only engage with huge accounts
❌ Don't copy-paste the same comment

## Rate Limits:
- Comments: 20-30/day max
- Likes: 100/day max
- Space out over several hours
EOF
