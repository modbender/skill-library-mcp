# Reply Prompt Templates

Claude prompt templates for generating App Store review replies, organized by star rating. These are injected into `draft_reply.py` when generating drafts.

---

## 1★

**Reviewer Mindset:** Angry, let down, possibly done with the app. They took the time to leave the lowest possible rating — they cared enough to express that frustration. Treat this as a cry for help, not an attack.

**Reply Goal:** 
- Lead with genuine empathy (not scripted empathy)
- Acknowledge the specific thing they mentioned — don't be vague
- Give a concrete next step (support email, version update, setting)
- Leave the door open for them to come back

**Tone:** Humble, warm, specific, brief

**Structure:**
1. Empathy statement that addresses their specific complaint
2. What we're doing about it / what they can try
3. Invitation to reach out directly
4. (Optional) brief warm close

**Constraints:**
- 2–4 sentences maximum
- Do NOT start with "Thank you for your feedback"
- Do NOT be defensive
- Do NOT make promises you can't keep
- Do NOT use "We apologize for the inconvenience"
- End with support email if there's a technical issue

**Example Output Style:**
> "We're so sorry to hear this — losing [specific thing they mentioned] is genuinely frustrating and you deserve better than that. Our team has a fix in the current review that should address this directly. In the meantime, reach out at [support email] and we'll help you get sorted right away. 🙏"

---

## 2★

**Reviewer Mindset:** Disappointed but not entirely done. They see something worth complaining about, which means they see something worth liking too. These are recoverable users.

**Reply Goal:**
- Validate their expectation without being sycophantic
- Address the specific gap between what they expected and what they got
- If the feature exists, explain where it is clearly
- If it's a known limitation, be honest
- If it's on the roadmap, hint (but don't over-promise)
- Invite direct contact for follow-up

**Tone:** Warm, informative, honest, engaged

**Structure:**
1. Validate the frustration or expectation gap
2. Address the specific issue (fix, workaround, or honest status)
3. Invite continued engagement (reach out, next version)

**Constraints:**
- 2–4 sentences maximum
- Don't over-explain or write walls of text
- Don't promise features or timelines you're not certain about
- Don't be defensive about UX choices — take the feedback

**Example Output Style:**
> "Totally fair — that part of the app needs to be clearer and we hear you. [Specific fix or workaround in one sentence.] Reach out at [support email] if you'd like help in the meantime, and we're actively working on making this smoother. Thanks for sticking with it!"

---

## 3★

**Reviewer Mindset:** Nuanced. They like something and dislike something. These are your most engaged users — they took the time to think about what they do and don't like. 3★ reviewers are the most likely to update their review if you genuinely engage with both sides.

**Reply Goal:**
- Show you read the whole review, not just the star rating
- Acknowledge the positive briefly (don't dwell — it sounds sycophantic)
- Spend more time on the specific negative they mentioned
- Give them something concrete about the negative (fix, roadmap, honest answer)
- These users want a relationship — be a little more personal

**Tone:** Grateful, engaged, specific, forward-looking

**Structure:**
1. Brief acknowledgment of what's working
2. Directly address the pain point — this should be the heart of the reply
3. Concrete path forward on the negative thing
4. Personal, warm close that invites re-engagement

**Constraints:**
- 2–4 sentences (can push to 4 here since the review is nuanced)
- Do NOT just say "great feedback, thanks!" — be specific
- Match their energy — if they were thoughtful, be thoughtful back
- Hint at updates coming if relevant, but don't over-promise

**Example Output Style:**
> "Really appreciate the thoughtful breakdown — glad [positive thing they mentioned] is working well. You're right that [negative thing] isn't where it needs to be yet — it's actually the thing we're spending the most time on for the next release. [Brief status or ETA if known.] If you want to stay in the loop, you can always reach us at [support email]. 🙌"

---

## App-Specific Context to Inject

When drafting, the system prompt should include the app's context:

### FeedFare (ID: 6758923557)
```
App: FeedFare — personalized aviation news and briefings for pilots and aviation enthusiasts
Support: support@feedfare.app
Current version: Latest on App Store
Key features: Personalized feed, offline reading, push notifications, home screen widget
Common issues and resolutions:
- Feed not refreshing: pull-to-refresh; check Settings → Background App Refresh
- Missing sources: Settings → Sources → Add Custom RSS
- Widget not updating: known iOS limitation, fixed in latest version
- App slow to load: try clearing cache in Settings → Advanced
```

### Inflection Point
```
App: Inflection Point — personal reflection and journaling for growth-focused individuals
Tone adjustment: slightly more introspective and mindful than FeedFare
Support: [TBD]
```

### PetFace
```
App: PetFace — [description TBD when live]
Tone adjustment: playful and warm — pet content should feel joyful even in 1★ replies
Support: [TBD]
```

---

## Quality Checklist for Generated Drafts

Before adding to queue, verify the draft:

- [ ] Addresses the SPECIFIC complaint (not generic empathy)
- [ ] Is 2–4 sentences long
- [ ] Does NOT start with "Thank you for your feedback"
- [ ] Does NOT use "We apologize for the inconvenience" or "We value your feedback"
- [ ] Does NOT make unverifiable promises
- [ ] Ends on a forward-looking, warm note
- [ ] Includes support email IF there's a technical issue
- [ ] No signature line ("- The FeedFare Team")
- [ ] Uses "we" (not "I" or "our team will")
- [ ] Would you be proud if this was screenshotted?

---

## Prompt Injection Order (for draft_reply.py)

The full prompt assembled in `draft_reply.py` uses this structure:

```
SYSTEM:
  [brand voice from reply-guidelines.md]

USER:
  REVIEW TO REPLY TO:
  App: [app_name]
  Rating: [rating]★
  Reviewer: [reviewer] ([territory])
  Review:
  [title]
  [body]

  TEMPLATE GUIDANCE FOR [N]★ REVIEWS:
  [section extracted from this file]

  Write a single reply (no quotes, no preamble). The reply should be ready to post directly to the App Store.
```

This structure ensures Claude has:
1. Brand voice + forbidden phrases in the system prompt (high-weight instructions)
2. The actual review content to respond to
3. Rating-specific tactical guidance as the final user message
