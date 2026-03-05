# Welcome Email Template

**Email Type:** Onboarding / Relationship Building  
**Goal:** Set expectations, deliver first value, build trust  
**Send:** Immediately after signup (automated sequence)

---

## Subject Line Options

1. "Welcome to [Your List Name] (start here)"
2. "[Name], you're in (here's what happens next)"
3. "Thanks for joining - your first [benefit] is inside"

**Chosen:** #2 (personalized + clear next step)

---

## Preview Text

"What to expect + your first resource inside"

---

## Email Body

```
Subject: {{ subscriber.first_name | default: "Friend" }}, you're in (here's what happens next)

---

{% if subscriber.first_name %}
Hey {{ subscriber.first_name }},
{% else %}
Hey there,
{% endif %}

Welcome! You're officially on the list.

Here's what you can expect from me:

**Weekly emails** (usually Thursday mornings)  
**Practical tips** you can use today  
**No spam** - I respect your inbox  
**Easy unsubscribe** - no hard feelings if you leave

I'm [Your Name], and I help [your audience] with [your niche]. I've been doing this for [X years], worked with [social proof], and I'm here to help you [specific outcome].

**Your first resource:**

I wrote this guide specifically for people just getting started:

[The Complete Beginner's Guide to [Your Topic]]
→ [https://yoursite.com/guide]

It covers:
- The #1 mistake beginners make (and how to avoid it)
- My 3-step framework for [result]
- Resources and tools I actually use

Read it, try it, let me know what you think.

**Quick favor:**

Hit reply and tell me: What's your biggest challenge with [your niche] right now?

I read every email, and your answer helps me write better content for you.

Talk next week,
[Your Name]

P.S. - If you didn't mean to sign up, no worries. [Unsubscribe here]({{ unsubscribe_url }}) and you won't hear from me again.

---

[Your Company Name]
[Optional: Physical Address for CAN-SPAM compliance]

[Unsubscribe]({{ unsubscribe_url }}) | [View in browser]({{ browser_url }})
```

---

## Why This Works

### 1. Sets Clear Expectations
- Frequency (weekly)
- Day/time (Thursday mornings)
- Type of content (practical tips)
- Easy exit (no hard feelings)

**Why:** Reduces unsubscribes later. People know what they signed up for.

### 2. Delivers Immediate Value
- First resource linked
- Specific, actionable content
- Relevant to why they subscribed

**Why:** Proves you're worth paying attention to. First impression matters.

### 3. Builds Personal Connection
- Brief intro (who you are, why you're credible)
- Two-way conversation (asks for reply)
- Human tone (not corporate marketing speak)

**Why:** People buy from people they trust. Start building trust immediately.

### 4. Establishes Response Behavior
- Asks for reply in first email
- Shows you read responses
- Creates expectation of dialogue

**Why:** Engaged subscribers are profitable subscribers.

### 5. Respects the Reader
- Easy unsubscribe (no shaming)
- Acknowledges accidental signups
- Honest about what's coming

**Why:** Trust and respect = long-term relationship.

---

## Customization Points

**Tone:**
- Casual version: "Hey! You're in. Here's what's up..."
- Professional version: "Thank you for subscribing. Here's what you can expect..."
- Friendly version: "Welcome, friend! So glad you're here."

**Content Focus:**
- Resource-heavy: Multiple links, guides, tools
- Relationship-heavy: More about you, your story, why you do this
- Action-heavy: One clear next step, minimal distraction

**Length:**
- Short version: 150-200 words (mobile-friendly, scannable)
- Medium version: 300-400 words (what's shown above)
- Long version: 500+ words (story-driven, builds deep connection)

**Personalization Level:**
- Basic: First name only
- Medium: First name + subscription source (form, lead magnet)
- Advanced: First name + company + pain point (from custom fields)

---

## A/B Test Ideas

**Subject Line:**
- Test personalized vs non-personalized
- Test curiosity vs direct benefit
- Test emoji vs no emoji

**Preview Text:**
- Test value-focused vs expectation-setting
- Test question vs statement

**Email Body:**
- Test short vs long
- Test one CTA vs multiple CTAs
- Test with story vs without story
- Test asking for reply vs not asking

**Always track:** Open rate, click rate, reply rate, unsubscribe rate

---

## Follow-Up Sequence

This welcome email should be part of a sequence:

**Email 1 (Day 0):** Welcome + first resource ← YOU ARE HERE  
**Email 2 (Day 2):** Best content roundup + story  
**Email 3 (Day 5):** Case study / success story  
**Email 4 (Day 7):** Offer (free or paid) + social proof  
**Email 5 (Day 10):** Final value email before joining regular list

---

## Deliverability Checklist

Before sending to new subscribers:

- [ ] From name is recognizable (your name or company name)
- [ ] From email is professional (not noreply@)
- [ ] Subject line isn't spammy (no all caps, excessive punctuation)
- [ ] Body has good text-to-image ratio (not image-only)
- [ ] Unsubscribe link is present and functional
- [ ] Physical address included (CAN-SPAM requirement)
- [ ] Tested on multiple email clients (Gmail, Outlook, Apple Mail)
- [ ] Tested on mobile (60%+ will open on phone)
- [ ] No broken links
- [ ] Personalization tags tested (fallbacks work)

---

## Common Mistakes to Avoid

❌ **Too salesy too soon**
Don't pitch products in welcome email. Build trust first.

❌ **No clear CTA**
Tell them what to do next. One clear action.

❌ **Generic and boring**
"Thanks for subscribing" → bland. Make it memorable.

❌ **All about you**
Balance "about me" with "here's value for you."

❌ **Overwhelming**
Too many links, too much info. Keep it focused.

❌ **No personality**
Sounds like corporate marketing. Write like a human.

---

## Success Metrics

**Good benchmarks for welcome emails:**
- **Open rate:** 50-70% (higher than regular broadcasts)
- **Click rate:** 20-40% (people are engaged)
- **Reply rate:** 2-10% (if you asked for replies)
- **Unsubscribe rate:** <1% (if it's high, your lead magnet might be misleading)

**Track over time:**
- Which subscribers who got this email became customers?
- How does this welcome email impact long-term engagement?

---

**This template is a starting point. Adapt to your brand voice, audience, and goals.**
