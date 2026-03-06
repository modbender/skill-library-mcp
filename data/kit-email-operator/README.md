# Kit Email Marketing Operator

**AI-powered email marketing for Kit (ConvertKit)**

Transform your email marketing with AI that writes like you, sends through Kit's API, and follows best practices automatically.

---

## What This Does

**Email Generation:**
- Writes complete emails matching your brand voice
- Creates 3 subject line options for every email
- Follows proven email marketing best practices
- Uses Kit personalization tags (first name, custom fields)

**Kit Integration:**
- Creates and schedules broadcasts via API
- Targets specific tags and segments
- Tracks campaign performance
- Manages drafts and scheduled sends

**Voice Matching:**
- Learns from your past emails (optional)
- Writes in your style and tone
- Maintains consistency across campaigns

---

## Quick Start

### 1. Install the Skill

```bash
# Copy to your OpenClaw workspace
cp -r kit-email-operator /data/.openclaw/workspace/skills/
```

### 2. Get Your Kit API Credentials

1. Log into your Kit account
2. Go to Settings → API Keys
3. Copy your **API Key** (v4) and **API Secret**

### 3. Run Setup

Just ask OpenClaw to help with email marketing:

```
"I want to send an email to my list"
```

OpenClaw will guide you through setup:
- Enter Kit API credentials (encrypted and stored securely)
- Optional: Paste 3-5 past emails for voice training
- Provide business context (niche, audience, offers)

Done! Now you can generate and send emails.

---

## How to Use

### Generate an Email

**Simple request:**
```
"Write a welcome email for new subscribers"
```

**Detailed request:**
```
"Write a sales email for my new course launch. It's about email marketing, costs $97, launches Friday, targeting entrepreneurs."
```

OpenClaw will:
1. Ask clarifying questions
2. Generate 3 subject line options + preview text + body
3. Show you the draft
4. Revise based on your feedback
5. Send/schedule via Kit when you're ready

### Send Strategies

**Save as draft:**
```
"Save this as a draft in Kit"
```

**Schedule for later:**
```
"Schedule this for Thursday at 10 AM"
```

**Send to specific tag:**
```
"Send this to my 'Premium Members' tag"
```

**Send to everyone:**
```
"Send this to my entire list"
```

### View Performance

```
"Show me stats for my last campaign"
```

You'll get:
- Recipients count
- Open rate
- Click rate
- Unsubscribe rate
- Performance insights

---

## Voice Training (Optional)

For emails that truly sound like you, provide 3-5 past emails during setup.

**What it learns:**
- Your tone and style
- Sentence structure
- Vocabulary and phrases
- Formatting preferences
- Signature style

**Example:**

If you write casually with short sentences, emojis, and personal stories, the AI will match that. If you write formally with data and structure, it'll match that too.

---

## Email Types You Can Generate

### Welcome Emails
- Introduce yourself
- Set expectations
- Deliver first value
- Build relationship

### Nurture Emails
- Share valuable content
- Tell stories
- Build trust
- No hard sell

### Sales Emails
- Launch products/services
- Overcome objections
- Create urgency
- Drive conversions

### Announcement Emails
- Share news
- Celebrate milestones
- Inform subscribers
- Build excitement

### Re-engagement Emails
- Win back inactive subscribers
- Remind of value
- Clean your list
- Rebuild connection

### Educational Emails
- Teach concepts
- Share tutorials
- Position as expert
- Deliver pure value

---

## Best Practices Built In

**Subject Lines:**
- 27-73 characters (optimal for all email clients)
- Curiosity, urgency, or benefit-driven
- Personalization when appropriate
- No spam triggers

**Email Body:**
- Short paragraphs (2-3 sentences)
- Strong hook in first sentence
- One clear call to action
- Scannable format (bold, bullets, white space)
- Conversational tone
- Mobile-optimized

**Sending Strategy:**
- Always draft first
- Test send recommended
- Segment when relevant
- Respect subscriber preferences
- Track and optimize

---

## Examples

### Example 1: Product Launch Email

**Your request:**
```
"Write a sales email for my new course. It's called 'Email Marketing Mastery', costs $97, launches Monday. Target audience is small business owners who struggle with email."
```

**What you get:**

**Subject Lines:**
1. [Name], your inbox is about to get a lot more profitable
2. The email course that pays for itself in 1 campaign
3. Small businesses are making $10k/month with this (you're next)

**Email:**
```
Hey [Name],

Quick question: how much money are you leaving on the table with your email list?

If you're like most small business owners, the answer is probably "a lot."

Here's the thing: you built that list for a reason. But if you're not emailing them consistently (or at all), it's just sitting there.

That changes Monday.

I'm launching Email Marketing Mastery - a no-BS course that shows you exactly how to turn your list into revenue.

No theory. No fluff. Just the 7 emails every small business needs + the templates to write them.

$97. One time. Lifetime access.

Early bird pricing ends Monday at midnight.

[Get instant access here →]

Talk soon,
[Your Name]

P.S. - This course has already helped 247 small businesses add an extra $2k-$10k/month in revenue. You're next.
```

### Example 2: Welcome Email

**Your request:**
```
"Write a welcome email. Tell them they'll get weekly tips on productivity, no spam, and link them to my best article."
```

**What you get:**

**Subject Lines:**
1. Welcome to [Your List Name] (start here)
2. [Name], you're in (here's what happens next)
3. Thanks for joining - your first productivity win is inside

**Email:**
```
Hey [Name],

Welcome! You're officially on the list.

Here's what you can expect:
- One email per week (usually Thursday mornings)
- Practical productivity tips you can use today
- No spam, no sales pitches, just value

To get you started, here's my most popular article:

[The 3-Minute Morning Routine That Changed Everything →]

It's helped over 10,000 people reclaim their mornings. Hope it helps you too.

Talk next week,
[Your Name]

P.S. - Hit reply anytime. I read every email.
```

---

## Technical Details

### Security
- API credentials encrypted with AES-256-GCM
- Never logged or displayed
- Stored locally in your workspace
- File permissions: 600 (owner only)

### API Integration
- Built on Kit API v4 (modern, reliable)
- Automatic rate limiting and retries
- Error handling and validation
- Supports broadcasts, tags, segments

### Requirements
- OpenClaw installed
- Kit (ConvertKit) account
- Node.js 18+ (for scripts)

---

## Troubleshooting

### "Can't find credentials"
Run setup again. OpenClaw will guide you through entering your Kit API key.

### "Email failed to send"
Check:
1. Kit credentials are correct
2. You have permission to send broadcasts
3. Tag IDs are valid (if targeting specific tags)

### "Voice doesn't sound like me"
Provide more email samples (3-5 minimum, longer emails work better).

### "Subject lines feel off"
Tell OpenClaw what you want:
- "Make them more casual"
- "Add more curiosity"
- "Remove the urgency"

### "Low open rates"
Ask OpenClaw: "Why are my open rates low?"

It'll analyze your:
- Subject lines
- Sending times
- From name
- List health

---

## Support

**Need help?**
- Ask OpenClaw: "How do I use the Kit email skill?"
- Read SETUP.md for detailed setup instructions
- Check examples/ folder for more templates

**Found a bug?**
Contact the skill maintainer through the Skool community.

---

## What Makes This Premium

**Not just templates** - AI writes original content for YOUR business

**Brand voice matching** - Sounds like you, not a robot

**Direct API integration** - No copy-paste, no manual work

**Strategic guidance** - Follows best practices automatically

**Production-ready** - Secure, tested, professional

**Comprehensive** - Email generation + sending + tracking + optimization

---

## License

**Distribution:** Private ClawHub (Premium Skool members only)

This skill is provided exclusively to premium members of The Operator Vault Skool community. Do not redistribute.

---

**Ready to transform your email marketing? Let's go.** 🚀
