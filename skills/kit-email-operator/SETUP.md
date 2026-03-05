# Kit Email Operator - Setup Guide

**Get up and running in 5 minutes**

---

## Prerequisites

- OpenClaw installed and running
- Kit (ConvertKit) account
- Node.js 18+ (for scripts)

---

## Step 1: Get Your Kit API Credentials

1. Log into your Kit account: https://app.kit.com
2. Navigate to **Settings** → **Advanced Settings** → **API Keys**
3. Copy your:
   - **API Key (v4)** - starts with `kit_`
   - **API Secret** - long alphanumeric string

Keep these handy for the next step.

---

## Step 2: Install the Skill

**Option A: Already installed (Premium Skool members)**

The skill should already be in your OpenClaw workspace at:
```
/data/.openclaw/workspace/skills/kit-email-operator/
```

**Option B: Manual installation**

```bash
cd /data/.openclaw/workspace/skills/
# Extract kit-email-operator.zip here
```

---

## Step 3: Run Setup

Just ask OpenClaw for help with email marketing:

```
"I want to send an email campaign"
```

or

```
"Help me write an email to my list"
```

OpenClaw will detect the skill and guide you through setup.

### Interactive Setup Flow

**1. Credentials**
```
Enter your Kit API credentials:

API Key (v4): kit_abc123...
API Secret: Exe_abc123...
```

Credentials are encrypted with AES-256-GCM and stored locally in:
```
/data/.openclaw/workspace/.kit-credentials
```

**2. Voice Training (Optional)**

If you want emails that sound like YOU, paste 3-5 past emails.

```
Paste email 1:
[Your email content]

Paste email 2:
[Your email content]

...
```

OpenClaw will analyze:
- Tone and style
- Sentence structure
- Vocabulary patterns
- Formatting preferences

Saved to: `/data/.openclaw/workspace/.kit-voice-profile.json`

**3. Database Integration (Optional)**

If you have a voice guide or memory files, point to them:

```
Voice guide path: /data/.openclaw/workspace/content/writing-rules/VOICE-GUIDE.md
Memory file path: /data/.openclaw/workspace/MEMORY.md
```

OpenClaw will read these before generating emails.

**4. Business Context**

```
What's your niche? content marketing for small businesses
Who's your audience? entrepreneurs with email lists under 5k
What do you offer? courses, coaching, and templates
Main website: https://yoursite.com
```

**5. Test Connection**

OpenClaw will test the connection and fetch your tags/custom fields.

```
✅ Connected to Kit
✅ Found 12 tags
✅ Found 3 custom fields
✅ Setup complete!
```

---

## Step 4: Send Your First Email

```
"Write a welcome email for new subscribers"
```

OpenClaw will:
1. Ask clarifying questions
2. Generate 3 subject line options + email body
3. Show you the draft
4. Send/schedule via Kit when approved

---

## Alternative: Command-Line Setup

If you prefer CLI setup:

```bash
cd /data/.openclaw/workspace/skills/kit-email-operator/scripts
node credentials.js setup
```

Follow the prompts.

**Test connection:**
```bash
node kit-api.js test
```

---

## Troubleshooting

### "Can't find credentials"

Run setup again:
```bash
node scripts/credentials.js setup
```

### "Invalid API key format"

Make sure you copied the **v4 API key** (starts with `kit_`), not the v3 key.

### "Connection failed"

Check:
1. API credentials are correct
2. Kit account is active
3. You have permission to create broadcasts

### "Voice profile seems off"

Re-train with longer emails (300+ words each work best).

---

## Security Notes

- Credentials are encrypted with AES-256-GCM
- File permissions set to 600 (owner read/write only)
- Keys never logged or displayed
- Stored locally (never sent to external servers)

---

## What Happens After Setup?

You can now:
- Generate emails matching your brand voice
- Send broadcasts via Kit API
- Target specific tags and segments
- Schedule campaigns
- Track performance
- Manage drafts

Just ask OpenClaw naturally:
- "Write a sales email for my course launch"
- "Send a re-engagement email to inactive subscribers"
- "Show me stats for my last campaign"

---

**Setup complete! Start writing better emails in seconds.**
