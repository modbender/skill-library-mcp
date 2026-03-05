# Kit Email Marketing Operator

**AI-powered email marketing for Kit (ConvertKit)**

Version: 1.0.0  
Distribution: Private ClawHub (Premium Skool members only)

---

## Purpose

This skill enables OpenClaw to write, manage, and send professional email campaigns through Kit (ConvertKit). It combines AI-powered content generation with direct API integration to handle the complete email marketing workflow.

**Core capabilities:**
- Generate email copy matching user's brand voice
- Create subject lines and preview text
- Schedule broadcasts via Kit API
- Target specific segments and tags
- Track campaign performance
- Follow email marketing best practices

---

## Setup Process

### First Run

When a user requests email marketing help for the first time, initiate the setup wizard:

1. **Check for credentials**
   ```javascript
   const credsPath = '/data/.openclaw/workspace/.kit-credentials';
   ```
   If missing, run setup.

2. **Setup wizard flow**
   - Welcome and explain what you'll collect
   - Request Kit API credentials (v4 key + secret)
   - Store encrypted using `scripts/credentials.js`
   - Optional: voice training (analyze 3-5 past emails)
   - Optional: database integration (point to voice guide files)
   - Collect business context (niche, audience, offers, links)
   - Fetch Kit custom fields for future personalization
   - Confirm setup complete

3. **Voice training (if provided)**
   - Analyze provided email samples
   - Extract: tone, structure, vocabulary, sentence patterns
   - Save voice profile to `/data/.openclaw/workspace/.kit-voice-profile.json`
   - Use this profile for all future email generation

4. **Database integration (if configured)**
   - Ask for path to voice guide (e.g., `content/writing-rules/VOICE-GUIDE.md`)
   - Ask for path to memory files (e.g., `MEMORY.md`)
   - Store paths in credentials file
   - Read these before generating emails

---

## Email Generation Workflow

### Step 1: Clarifying Questions

Before writing any email, ask these questions:

**Required:**
- **Goal:** What's the purpose? (nurture/sell/announce/educate/re-engage/onboard)
- **Audience:** Who's receiving this? (all subscribers/specific tag/specific segment)
- **Main message:** What's the core point you want to communicate?
- **Call to action:** What should readers do? (click link/reply/take action)

**Optional:**
- **Links to include:** Any specific URLs to feature?
- **Tone preference:** (if not using voice training)
- **Personalization:** Should we use first name? Custom fields?
- **Timing:** Send now, schedule, or save as draft?

**Example questioning flow:**
```
I can help you write that email. A few quick questions:

1. What's the goal? (nurture relationship / make a sale / announce something / educate)
2. Who's this going to? (all subscribers / a specific tag / a segment)
3. What's the main message or value you want to communicate?
4. What action should they take after reading?
5. Any links you want me to include?
6. Should I personalize with first names?
```

### Step 2: Generate Content

**Subject Lines (provide 3 options):**
- Use formulas from `references/subject-line-formulas.md`
- Keep 27-73 characters
- Tap into curiosity, urgency, benefit, or social proof
- Avoid spam triggers (all caps, excessive punctuation)

**Preview Text:**
- 40-70 characters
- Complements subject line
- Teases value inside

**Email Body:**
- Follow structure from `references/email-best-practices.md`
- Match user's voice (if trained) or requested tone
- Include personalization tags if requested
- Strong hook in first sentence
- Clear value proposition
- Natural CTA placement
- Keep scannable (short paragraphs, white space)

**Personalization Tags:**
Reference `references/kit-personalization.md` for available tags:
- `{{ subscriber.first_name }}` - Subscriber's first name
- `{{ subscriber.email_address }}` - Email address
- Custom fields: `{{ subscriber.YOUR_FIELD_NAME }}`

**Example generation output:**
```markdown
## Subject Line Options

1. [Name], here's what 80% of email marketers get wrong
2. The 3-minute email hack that doubled my opens
3. Your subscribers are telling you something (listen closely)

## Preview Text

Most people ignore this signal. Here's how to spot it.

## Email Body

Hey {{ subscriber.first_name }},

Quick question: when was the last time you checked your email open rates?

[rest of email...]

**Call to Action:**
[Read the full guide here →](https://example.com/guide)

Talk soon,
[Your Name]
```

### Step 3: Review & Refine

Present the email to the user and ask:
- "How does this sound?"
- "Want me to adjust the tone?"
- "Should I try a different angle?"
- "Ready to send, or should we save as draft?"

Make revisions based on feedback.

### Step 4: Send via Kit API

Once approved, use `scripts/kit-api.js` to:

**Create broadcast:**
```javascript
const { KitAPI } = require('./scripts/kit-api.js');
const kit = new KitAPI();

const broadcast = await kit.createBroadcast({
  subject: "Chosen subject line",
  content: "Email HTML content",
  description: "Internal description",
  send_at: "2026-02-17T10:00:00Z", // or null for draft
  public: false,
  tag_ids: [123, 456] // if targeting specific tags
});
```

**Options:**
- **Draft:** `send_at: null` - save for review later
- **Schedule:** `send_at: "ISO timestamp"` - schedule for future
- **Send now:** Don't include `send_at` (immediately publishes)

**Targeting:**
- **All subscribers:** Don't include `tag_ids` or `segment_ids`
- **Specific tags:** `tag_ids: [123, 456]`
- **Specific segments:** `segment_ids: [789]`

Confirm with user before sending.

---

## Campaign Management

### View Campaign Stats

After sending, users can request performance data:

```javascript
const stats = await kit.getBroadcastStats(broadcastId);
```

**Present stats in readable format:**
```
📊 Campaign Performance: "Your Subject Line"

📤 Recipients: 1,234
📬 Opens: 456 (37%)
🖱️ Clicks: 89 (19.5% of opens)
🚪 Unsubscribes: 5 (0.4%)
```

**Provide insights:**
- Compare to benchmarks (see `references/email-best-practices.md`)
- Suggest improvements for next campaign
- Identify what worked well

### Manage Drafts

Users can:
- List saved drafts: `kit.listBroadcasts({ status: 'draft' })`
- Update drafts: `kit.updateBroadcast(id, changes)`
- Delete drafts: `kit.deleteBroadcast(id)`
- Schedule drafts: `kit.updateBroadcast(id, { send_at: timestamp })`

---

## Best Practices (Always Follow)

### Email Content

✅ **DO:**
- Write conversational, authentic copy
- Use short paragraphs (2-3 sentences max)
- Include one clear CTA
- Personalize when possible
- Make it scannable (bold, bullets, white space)
- Match user's brand voice
- Lead with value, not pitch

❌ **DON'T:**
- Use spam trigger words (free, guarantee, act now)
- Write long blocks of text
- Include multiple conflicting CTAs
- Sound robotic or corporate
- Make unsubscribing difficult
- Oversell or hype

### Subject Lines

✅ **DO:**
- Keep 27-73 characters
- Use curiosity, urgency, or benefit
- Personalize when appropriate
- A/B test different approaches
- Avoid spam triggers

❌ **DON'T:**
- Use all caps or excessive punctuation
- Mislead about content inside
- Use spammy words
- Be too vague or too long

### Sending Strategy

✅ **DO:**
- Send drafts first (review before scheduling)
- Test send to yourself
- Check deliverability (SPF, DKIM, DMARC)
- Segment your list when relevant
- Track performance
- Clean your list regularly

❌ **DON'T:**
- Send without review
- Blast entire list with sales pitch
- Ignore unsubscribes or complaints
- Send too frequently (respect inbox)
- Ignore performance data

---

## Technical Reference

### File Locations

- **Credentials:** `/data/.openclaw/workspace/.kit-credentials`
- **Voice Profile:** `/data/.openclaw/workspace/.kit-voice-profile.json`
- **API Client:** `skills/kit-email-operator/scripts/kit-api.js`
- **Credential Manager:** `skills/kit-email-operator/scripts/credentials.js`

### Available Functions

**From `scripts/kit-api.js`:**
```javascript
// Broadcasts
kit.createBroadcast(data)
kit.updateBroadcast(id, data)
kit.deleteBroadcast(id)
kit.getBroadcast(id)
kit.listBroadcasts(options)
kit.getBroadcastStats(id)

// Tags
kit.listTags()
kit.tagSubscriber(email, tagId)

// Subscribers
kit.listSubscribers()
kit.getSubscriber(id)

// Custom Fields
kit.listCustomFields()
```

### Security

- All credentials stored encrypted (AES-256-GCM)
- Never log or display API keys
- File permissions set to 600 (owner read/write only)
- Credentials file excluded from version control

---

## Example Workflows

### Workflow 1: Welcome Email

**User:** "Write a welcome email for new subscribers"

**You:**
```
I can help you write that welcome email. A few quick questions:

1. What should new subscribers know about you/your business?
2. What value will they get from being on your list?
3. Should I include a first resource or action for them?
4. Any specific link to send them to?
```

**After answers, generate:**
- 3 subject line options (welcoming, clear value)
- Preview text
- Email body (introduce yourself, set expectations, deliver value, clear next step)

**Then:** Create as draft in Kit, ask for review, schedule or send.

### Workflow 2: Product Launch

**User:** "I'm launching a new course. Write a sales email."

**You:**
```
Got it. Sales email for course launch. Let me ask:

1. What's the course about? (the transformation it provides)
2. Who's it for? (ideal student)
3. Price point?
4. Launch date and any urgency? (early bird, limited spots, etc.)
5. Link to sales page?
6. Should I emphasize social proof, bonuses, or scarcity?
```

**After answers, generate:**
- 3 subject lines (curiosity + urgency)
- Preview text (benefit-driven)
- Email body (problem → solution → transformation → offer → CTA)

**Then:** Review together, refine, send to specific tag or segment.

### Workflow 3: Re-engagement Campaign

**User:** "I want to re-engage subscribers who haven't opened in 60 days"

**You:**
```
Smart move. Re-engagement campaign. Quick questions:

1. What made you valuable to them when they first subscribed?
2. What's changed or improved since then?
3. Should we give them an option to unsubscribe (clean list)?
4. What's the main value proposition to bring them back?
```

**After answers, generate:**
- 3 subject lines (pattern interrupt, personal, curiosity)
- Preview text (direct and honest)
- Email body (acknowledge absence, remind of value, simple ask, easy opt-out)

**Then:** Target specific segment in Kit (inactive subscribers), send as test first.

---

## Voice Matching

If user provided email samples during setup, reference the voice profile:

**Voice Profile Structure:**
```json
{
  "tone": "casual and direct",
  "sentence_length": "short, punchy sentences mixed with longer ones",
  "vocabulary": ["honestly", "let's be real", "here's the thing"],
  "patterns": [
    "Uses questions to engage",
    "Includes parenthetical asides",
    "Admits limitations honestly"
  ],
  "formatting": [
    "Short paragraphs (1-3 sentences)",
    "Bold for emphasis",
    "Emoji occasionally"
  ],
  "signature": "Ship it,\nKevin"
}
```

**Apply these elements to generated emails.**

---

## Troubleshooting

### Setup Issues

**Problem:** User doesn't have Kit credentials  
**Solution:** Guide them to Kit dashboard → Settings → API Keys

**Problem:** Voice training samples too short  
**Solution:** Ask for longer emails (300+ words each)

**Problem:** Can't find Kit custom fields  
**Solution:** Verify credentials, check Kit account has custom fields created

### Sending Issues

**Problem:** Broadcast fails to create  
**Solution:** Check credentials, verify content format, ensure valid tag_ids

**Problem:** Email looks broken  
**Solution:** Check HTML formatting, test send to yourself first

**Problem:** Low open rates  
**Solution:** Review subject lines, check sending time, analyze from name

### API Issues

**Problem:** Rate limiting  
**Solution:** API client has automatic retry with exponential backoff

**Problem:** Invalid credentials  
**Solution:** Re-run setup, verify credentials in Kit dashboard

---

## Reference Files

**For subject lines:**
Read `references/subject-line-formulas.md` (50+ proven templates)

**For email structure:**
Read `references/email-best-practices.md` (comprehensive guide)

**For personalization:**
Read `references/kit-personalization.md` (all available Kit tags)

**For sequences:**
Read `references/sequence-templates.md` (welcome, nurture, sales, onboarding)

**For examples:**
Check `examples/` folder for complete email templates

---

## Quality Standards

This is a **premium skill**. Every interaction should feel:
- **Professional** - polished, error-free, well-structured
- **Helpful** - anticipate needs, guide decisions, educate
- **Efficient** - minimize back-and-forth, smart defaults
- **Secure** - protect credentials, never expose sensitive data
- **Human** - conversational, not robotic

Users are paying for this. Make it worth it.

---

**This skill represents the highest quality email marketing automation available for OpenClaw. Maintain that standard.**
