# Listing Swarm - Complete Documentation

## Overview

Listing Swarm is a Clawdbot skill that helps you submit your AI product to 70+ AI tool directories. Your agent automates the tedious form-filling; you handle captchas and verification.

---

## What Problem Does This Solve?

Getting your AI product listed on directories is valuable but tedious:
- 70+ directories to submit to
- Each has different forms, fields, and requirements
- Many have captchas
- Takes 10+ hours to do manually

This skill lets your Clawdbot agent do the repetitive work while you handle the parts that need a human.

---

## How It Works (Step by Step)

### Step 1: You Provide Product Info

You give the agent your product details:
```
- Product name
- Website URL
- Tagline (short description)
- Full description
- Category
- Pricing model
- Logo URL
- Screenshot URL
- Contact email
```

### Step 2: Agent Loads Directory List

The skill includes `directories.json` with 70+ AI directories:
```json
{
  "name": "Futurepedia",
  "url": "https://futurepedia.io",
  "submitUrl": "https://futurepedia.io/submit-tool",
  "domainRating": 68,
  "monthlyVisits": "1.5M",
  "pricing": "Free"
}
```

### Step 3: Agent Visits Each Directory

For each directory, the agent:
1. Opens the submit URL in browser
2. Identifies the form fields
3. Fills in your product info
4. Handles captcha (using your API key)
5. Submits the form
6. Records the result

### Step 4: Captcha Handling

When the agent encounters a captcha:
- **If you have a captcha API key**: Agent sends to 2captcha/similar, waits for solution, enters it
- **If no API key**: Agent flags you: "Need you to solve this captcha"

### Step 5: Human-in-the-Loop

Some things the agent can't handle alone:
- "This directory requires creating an account first"
- "This one wants payment for featured listing"
- "Captcha keeps failing, can you try?"
- "Email verification needed - check your inbox"

You handle it, tell agent to continue.

### Step 6: Tracking

Every submission is logged:
```json
{
  "directory": "Futurepedia",
  "status": "submitted",
  "submitted_at": "2026-02-09T15:00:00Z",
  "listing_url": null,
  "notes": "Pending review, usually 3-5 days"
}
```

---

## What the Agent Does

| Action | Automated? | Notes |
|--------|------------|-------|
| Load directory list | ✅ Yes | From directories.json |
| Visit submit pages | ✅ Yes | Uses browser tool |
| Fill form fields | ✅ Yes | Maps your product info to fields |
| Upload logo/screenshots | ✅ Yes | If URLs provided |
| Solve captchas | ⚡ With API key | You provide 2captcha key |
| Email verification | ⚡ With IMAP | You provide email access |
| Create accounts | ❌ No | Flags you |
| Make payments | ❌ No | Flags you |
| Track submissions | ✅ Yes | Saves to submissions.json |

---

## What You Need to Provide

### Required
1. **Product information** (name, URL, description, etc.)
2. **Time to help** when agent gets stuck

### Highly Recommended  
3. **Your own captcha API key** from [2captcha.com](https://2captcha.com)
   - ⚠️ **You must get your own key** - skill does not include one
   - Sign up at 2captcha.com → Add $3 → Copy your API key
   - Without it, you'll solve 70+ captchas manually (tedious)

4. **Logo and screenshot URLs**
   - Most directories require these
   - Should be publicly accessible URLs

---

## Data & Privacy

### What data does this skill access?

| Data | Access | Why |
|------|--------|-----|
| Your product info | Read | To fill directory forms |
| Directory list | Read | To know where to submit |
| Browser | Control | To visit and fill forms |
| Captcha API | External call | To solve captchas (your key) |
| Submissions log | Read/Write | To track progress |

### What data is NOT accessed?

- Your personal accounts (unless you share credentials)
- Your email inbox
- Your payment methods
- Any data outside the skill's files

### What goes to external services?

- **Captcha images** → Your captcha service (2captcha, etc.)
- **Your product info** → Each directory you submit to (that's the point)
- **Nothing else** goes anywhere

---

## Directory List Details

The skill includes 70+ directories. Each entry has:

| Field | Description |
|-------|-------------|
| `name` | Directory name |
| `url` | Main website |
| `submitUrl` | Direct link to submission form |
| `domainRating` | Ahrefs DR (authority score) |
| `monthlyVisits` | Estimated traffic |
| `pricing` | Free / Paid / Freemium |
| `experience` | Good / Okay / Poor (submission experience) |

### Sample Directories

| Directory | DR | Traffic | Pricing |
|-----------|-----|---------|---------|
| There's An AI For That | 75 | 5M | Paid |
| Futurepedia | 68 | 1.5M | Free |
| OpenTools | 69 | 3M | Paid |
| TopAI.tools | 65 | 800k | Free |
| AI Tool Guru | 55 | 200k | Free |
| Product Hunt | 91 | 10M+ | Free |
| + 65 more... | | | |

---

## Captcha Integration

### ⚠️ You Must Get Your Own API Key

**This skill does NOT include a captcha API key. You must get your own.**

### How to Get a Key

1. Go to **[2Captcha.com](https://2captcha.com)** (recommended)
2. Click "Register" and create account
3. Add funds: **$3 is enough** for all 70 directories
4. Go to Dashboard → Copy your API key
5. Add to your environment: `export CAPTCHA_API_KEY="your-key"`

### Supported Services

| Service | Website | Cost | Get Key |
|---------|---------|------|---------|
| 2Captcha | 2captcha.com | ~$3/1000 | [Sign up](https://2captcha.com) |
| Anti-Captcha | anti-captcha.com | ~$2/1000 | [Sign up](https://anti-captcha.com) |
| CapSolver | capsolver.com | ~$2.50/1000 | [Sign up](https://capsolver.com) |

### How It Works

1. Agent encounters captcha on a directory
2. Extracts captcha type (reCAPTCHA, hCaptcha, image)
3. Sends to **YOUR** captcha service via **YOUR** API key
4. Service returns solution (takes 10-60 seconds)
5. Agent enters solution and continues

### If No API Key

Agent will flag you for each captcha:
> "I hit a captcha on Futurepedia. Can you solve it? [shows screenshot or link]"

You solve it manually, agent continues. This works but takes longer.

---

## Email Verification (Optional)

Most directories send verification emails. Your agent can handle these automatically.

### Why Set This Up?

Without it: Agent submits → Directory sends email → Agent says "check your email" → You click link → Repeat 70 times

With it: Agent submits → Agent checks email → Agent clicks link → Done automatically

### Setup: Create a Dedicated Email

**Recommended:** Don't use your personal email. Create one for submissions:
```
yourproduct.listings@gmail.com
```

### Setup: Gmail App Password

1. **Create/use a Gmail account** for submissions
2. **Enable 2-Factor Auth:**
   - Go to Google Account → Security
   - Turn on 2-Step Verification
3. **Create App Password:**
   - Google Account → Security → App passwords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Listing Swarm" 
   - Click Generate
   - Copy the 16-character password (looks like: `xxxx xxxx xxxx xxxx`)

4. **Set environment variables:**
```bash
export IMAP_USER="yourproduct.listings@gmail.com"
export IMAP_PASSWORD="xxxx xxxx xxxx xxxx"  # App password, NOT your real password
export IMAP_HOST="imap.gmail.com"
```

### Other Email Providers

| Provider | IMAP Host |
|----------|-----------|
| Gmail | imap.gmail.com |
| Outlook | imap-mail.outlook.com |
| Yahoo | imap.mail.yahoo.com |
| Custom domain | Check with your provider |

### How It Works

1. Agent submits to directory using your submission email
2. Directory sends verification email
3. Agent connects to your email via IMAP (read-only)
4. Agent finds the verification email
5. Agent extracts the verification link
6. Agent clicks the link in browser
7. Verification complete!

### If No Email Access

Agent will flag you:
> "Check your email for a verification link from futurepedia.io"

You check, click the link, tell agent to continue.

---

## Safety Considerations

### ✅ Safe

- **No stored credentials** - You provide info each session
- **No payments** - Agent flags paid directories, doesn't pay
- **No account creation** - Agent flags, you create if desired
- **Local tracking** - Submission log stays in your workspace
- **You control the pace** - Can stop anytime

### ⚠️ Be Aware

- **Directory ToS** - Some directories don't allow automated submission. The agent fills forms like a human would, but technically it's automation.
- **Captcha costs** - If using paid captcha service, ~$3 per 70 directories
- **Email volume** - You'll get 70+ verification/confirmation emails
- **Approval times** - Most directories have review periods (1-14 days)

---

## Example Session

**You:** "Use listing-swarm to submit my product. Here's my info:
- Name: CoolAI
- URL: https://coolai.app
- Tagline: AI that does cool stuff
- Description: [full description]
- My 2captcha key is in CAPTCHA_API_KEY env var"

**Agent:** "Got it. I'll start submitting CoolAI to 70 directories. I'll let you know when I need help."

*[Agent works through directories...]*

**Agent:** "Submitted to 12 directories so far. Futurepedia needs you to verify your email - check your inbox for a link from them."

**You:** "Done, verified."

**Agent:** "Thanks! Continuing... ProductHunt requires an account. Want me to skip it or do you want to create one?"

**You:** "Skip for now."

**Agent:** "Completed 45/70. Here's the status so far: [shows table]"

---

## Files in This Skill

```
listing-swarm/
├── SKILL.md           # Quick reference for agent
├── DOCS.md            # This file (full documentation)  
├── directories.json   # 70+ directories with submit URLs
├── submissions.json   # Tracks your submission status
├── captcha.js         # Captcha solver integration (BYOK)
└── email.js           # Email verification via IMAP (optional)
```

---

## FAQ

**Q: Will this get me banned from directories?**
A: The agent fills forms like a human would. It's not scraping or doing anything the form doesn't allow. That said, mass automated submission is a grey area - use your judgment.

**Q: How long does it take?**
A: With captcha API: ~2-3 hours for all 70. Without: longer, since you solve each captcha.

**Q: Do I need to pay for directory listings?**
A: Many are free. Agent will flag paid ones and let you decide.

**Q: What if a directory changes their form?**
A: Agent adapts using browser + AI understanding. If it can't figure it out, it flags you.

**Q: Can I add more directories?**
A: Yes, edit directories.json. Follow the same format.

---

## Support

Part of [LinkSwarm](https://linkswarm.ai) - the AI visibility network.

Questions? Issues? https://github.com/Heyw00d/linkswarm/issues
