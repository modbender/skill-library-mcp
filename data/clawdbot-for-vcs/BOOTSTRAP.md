# Bootstrap Guide - Clawdbot for VCs

Get your VC investment workflow AI assistant up and running in under 30 minutes.

## Prerequisites

- Clawdbot installed and running (see main Clawdbot documentation)
- Gmail account with labels support
- Google Calendar
- Affinity CRM account with API access
- Basic command line familiarity

---

## Step 1: Install Required Tools

### 1.1 Install gog CLI (Gmail/Calendar access)

```bash
# Install Go if not already installed
# See: https://go.dev/doc/install

# Install gog
go install github.com/martynsmith/gog@latest

# Add to PATH (add to ~/.bashrc or ~/.zshrc for persistence)
export PATH="$PATH:$(go env GOPATH)/bin"

# Verify installation
gog --version
```

### 1.2 Authenticate gog with Google

```bash
# Start OAuth flow
gog auth

# Follow the browser prompts to authorize Gmail and Calendar access
# You'll need to grant these scopes:
# - https://www.googleapis.com/auth/gmail.modify
# - https://www.googleapis.com/auth/calendar
```

### 1.3 Set up gog keyring password

```bash
# Create a password for the gog keyring
# Store this somewhere safe (e.g., password manager)

# Set environment variable (add to ~/.bashrc or ~/.zshrc)
export GOG_KEYRING_PASSWORD=$(echo "YOUR_BASE64_PASSWORD" | base64 -d)
```

**Tip:** Generate a base64 password:
```bash
echo "YourSecurePassword123!" | base64
# Output: WW91clNlY3VyZVBhc3N3b3JkMTIzIQo=
# Use this in your config (decode with | base64 -d)
```

### 1.4 Test gog

```bash
# List recent emails
gog gmail messages list --max 5 --account your.email@firm.com

# List calendar events
gog calendar events --from $(date +%Y-%m-%d) --to $(date -d "+7 days" +%Y-%m-%d) --account your.email@firm.com
```

---

## Step 2: Set Up Affinity CRM

### 2.1 Get API Key

1. Log into Affinity
2. Go to Settings → API
3. Generate a new API key
4. Copy the key (you won't see it again!)

### 2.2 Set Environment Variable

```bash
# Add to ~/.bashrc or ~/.zshrc
export AFFINITY_API_KEY="your_api_key_here"

# Reload shell config
source ~/.bashrc  # or source ~/.zshrc
```

### 2.3 Test API Access

```bash
# Verify authentication
curl -u ":$AFFINITY_API_KEY" https://api.affinity.co/auth

# Should return: {"success": true}
```

### 2.4 Identify Your Field IDs

You need to find the field IDs in your Affinity instance:

```bash
# Method 1: Get fields from an existing org
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/organizations/YOUR_ORG_ID/field-values" | jq

# Method 2: Search for a company and examine fields
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/organizations?term=YourCompanyName" | jq
```

**Fields you need to identify:**

| Field Name | Your Field ID | Notes |
|------------|---------------|-------|
| Deal Stage | _____________ | Dropdown with pipeline stages |
| HQ Owner   | _____________ | Person field (deal champion) |
| One Liner  | _____________ | Text field for company tagline |

**Deal Stage Options** (note the option IDs for each stage):

| Stage Name | Your Option ID |
|------------|----------------|
| Passed | _____________ |
| Diligence | _____________ |
| Deep Diligence | _____________ |
| Consideration | _____________ |
| Invested | _____________ |

### 2.5 Get Your Person ID

```bash
# Search for yourself
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/persons?term=YourName" | jq

# Note your person ID for setting HQ Owner field
```

### 2.6 Get Your Deal Pipeline List ID

```bash
# List all lists
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/lists" | jq

# Find your Deal Pipeline list and note the list_id
```

---

## Step 3: Configure Gmail Labels

Create these labels in Gmail for email triage:

1. Go to Gmail → Settings → Labels
2. Create the following labels:

```
Triage/Priority
Triage/Review
Triage/Auto-Respond
Triage/Archive
Triage/Pending-Response
Triage/Draft-Pending
```

**Tip:** You can create nested labels by using the `/` separator.

### Get Label IDs

```bash
# List all labels
gog gmail labels list --account your.email@firm.com

# Note the IDs for the labels you created
```

---

## Step 4: Set Up Google Calendar Booking Pages

### 4.1 Create Appointment Schedules

1. Go to [Google Calendar](https://calendar.google.com)
2. Click Settings (gear icon) → Settings
3. Select "Appointment schedules" from the left menu
4. Click "Create" for each meeting type

### 4.2 Create These Booking Pages

| Meeting Type | Duration | Availability | Buffer |
|--------------|----------|--------------|--------|
| Intro Call | 30 min | Mon-Fri 9am-5pm | 15 min before |
| Follow Up | 30 min | Mon-Fri 9am-5pm | 15 min before |
| Diligence | 60 min | Mon-Fri 9am-5pm | 15 min before |
| Portfolio | 30 min | Mon-Fri 9am-5pm | 10 min before |
| Investor Network | 30 min | Mon-Thu 9am-5pm | 15 min before |
| Priority | 30 min | Mon-Fri 8am-6pm | 0 min buffer |

**For each:**
1. Set meeting title (e.g., "Intro Call with [Your Name]")
2. Set location to "Google Meet"
3. Configure your availability windows
4. Set minimum scheduling notice (e.g., 4 hours)
5. Copy the booking link

### 4.3 Save Your Booking Links

Copy all the booking links to a temporary file for later use in your config:

```
Intro Call: https://calendar.app.google/YOUR_LINK_1
Follow Up: https://calendar.app.google/YOUR_LINK_2
Diligence: https://calendar.app.google/YOUR_LINK_3
Portfolio: https://calendar.app.google/YOUR_LINK_4
Network Investors: https://calendar.app.google/YOUR_LINK_5
Priority: https://calendar.app.google/YOUR_LINK_6
```

---

## Step 5: Configure Your Clawdbot Workspace

### 5.1 Copy Template Files

```bash
# Navigate to your Clawdbot workspace
cd ~/clawd  # or wherever your workspace is

# Copy the skill
cp -r skills/clawdbot-for-vcs/templates/* .

# Or create from scratch using the templates below
```

### 5.2 Customize USER.md

Edit `USER.md` with your information:

```markdown
# USER.md - About Your Human

- **Name:** Your Full Name
- **What to call them:** Your Preferred Name
- **Timezone:** Your Timezone (e.g., Pacific, Eastern)
- **Email:** your.email@firm.com

## Work

- **Role:** Investment Partner
- **Firm:** Your VC Firm Name
- **Focus areas:** [Your investment thesis - e.g., data infrastructure, ML/AI, devtools]
- **Tools:** Affinity CRM, Gmail via gog, Google Calendar

## Workflow

- Triages inbound founder emails daily
- Uses Affinity to track deals and companies
- Booking links for different meeting types
- Prefers draft emails for approval before sending (never send directly!)

## Context

*(Your AI will build this over time)*
```

### 5.3 Customize TOOLS.md

Edit `TOOLS.md` with your specific IDs:

```markdown
# TOOLS.md - Local Notes

## Booking Links

| Meeting Type | Link |
|--------------|------|
| Intro Call | https://calendar.app.google/YOUR_INTRO_LINK |
| Follow Up | https://calendar.app.google/YOUR_FOLLOWUP_LINK |
| Diligence | https://calendar.app.google/YOUR_DILIGENCE_LINK |
| Portfolio | https://calendar.app.google/YOUR_PORTFOLIO_LINK |
| Network Investors | https://calendar.app.google/YOUR_INVESTOR_LINK |
| Priority | https://calendar.app.google/YOUR_PRIORITY_LINK |

## Gmail Labels

| Label | Label ID |
|-------|----------|
| Triage/Priority | YOUR_LABEL_ID |
| Triage/Review | YOUR_LABEL_ID |
| Triage/Auto-Respond | YOUR_LABEL_ID |
| Triage/Archive | YOUR_LABEL_ID |
| Triage/Pending-Response | YOUR_LABEL_ID |
| Triage/Draft-Pending | YOUR_LABEL_ID |

## Affinity CRM

### Your IDs
- **Person ID:** YOUR_PERSON_ID
- **Deal Pipeline List ID:** YOUR_LIST_ID

### Field IDs
- **Deal Stage:** YOUR_FIELD_ID
- **HQ Owner:** YOUR_FIELD_ID
- **One Liner:** YOUR_FIELD_ID

### Deal Stage Options
- **Passed:** YOUR_OPTION_ID
- **Diligence:** YOUR_OPTION_ID
- **Deep Diligence:** YOUR_OPTION_ID
- **Consideration:** YOUR_OPTION_ID
- **Invested:** YOUR_OPTION_ID

## Environment Variables

```bash
export GOG_KEYRING_PASSWORD=$(echo YOUR_BASE64_PASSWORD | base64 -d)
export AFFINITY_API_KEY="YOUR_API_KEY"
```

## Trusted VC Domains

Customize this list based on your network:

```
a16z.com, accel.com, benchmark.com, gv.com, greylock.com, sequoiacap.com,
[add your trusted sources...]
```

## Investment Thesis Keywords

Keywords for email triage:

- Your focus area 1 (e.g., "data infrastructure", "data platform")
- Your focus area 2 (e.g., "ML infrastructure", "MLOps")
- Your focus area 3 (e.g., "developer tools", "devtools")
```

### 5.4 Update AGENTS.md

Add your VC-specific instructions. See `templates/AGENTS.md.example` for a full template.

Key additions:
```markdown
## Email Triage

Check email 2-4 times per day:
- Morning (9am)
- Midday (1pm)
- Afternoon (4pm)
- Evening (7pm) - optional

For each session:
1. Search for unlabeled emails in inbox
2. Classify and label appropriately
3. Draft pass emails for Auto-Respond
4. Add companies to Affinity
5. Generate briefing if significant activity

## Message Format

[Add your preferred formatting - e.g., emoji markers, etc.]
```

---

## Step 6: Test Your Setup

### 6.1 Test Email Triage

```bash
# Manually trigger a triage check
# (Talk to your AI via your primary channel)

"Check my email and triage"
```

Your AI should:
1. Search for recent emails
2. Classify them
3. Report findings

### 6.2 Test Affinity Integration

```bash
# Ask your AI to test Affinity
"Search Affinity for [a company you know exists]"
```

Your AI should return company details and notes.

### 6.3 Test Calendar Access

```bash
"What's on my calendar today?"
```

Your AI should list your events.

### 6.4 Test Pass Email Draft

Find a cold outreach email and say:
```
"Draft a pass email for this"
```

Your AI should:
1. Check if you've already replied (avoid duplicates)
2. Create a draft pass email
3. Ask for approval

---

## Step 7: First Day Usage

### Morning Routine

1. **Generate briefing:** "What's my daily briefing?"
2. **Review Priority emails:** Respond to warm intros
3. **Approve drafts:** Review and send pass emails
4. **Check calendar:** Confirm meetings for the day

### During the Day

- Let your AI auto-triage incoming email
- Ask for memo generation when you get new pitch decks
- Use booking links when scheduling with founders

### Evening Review

- "What did I miss today?"
- Review auto-responded emails
- Check Affinity for logged companies

---

## Step 8: Iteration & Trust Building

### Start Conservative

In your first week:
- **Always review drafts** before sending
- **Confirm actions** before your AI logs to Affinity
- **Check AI decisions** on email classification

### Build Trust Gradually

As your AI proves reliable:
- Enable auto-archive for certain email types
- Allow auto-logging of clear passes to Affinity
- Increase autonomy for routine tasks

### Track Mistakes

Create a `memory/mistake-log.json` file to track:
- Misclassified emails
- Incorrect Affinity entries
- Poor draft quality

Use this to refine rules and improve over time.

---

## Common Issues & Solutions

### Issue: "gog command not found"

**Solution:** Add gog to your PATH:
```bash
export PATH="$PATH:$(go env GOPATH)/bin"
source ~/.bashrc
```

### Issue: "Affinity API returns 401"

**Solution:** Check your API key:
```bash
echo $AFFINITY_API_KEY  # Should print your key
curl -u ":$AFFINITY_API_KEY" https://api.affinity.co/auth
```

### Issue: "Gmail drafts not appearing"

**Solution:** Check account name:
```bash
gog gmail drafts list --account your.email@firm.com
```

Ensure you're using the exact email address from `gog auth`.

### Issue: "AI is drafting duplicate emails"

**Solution:** Your AI should check for existing sent messages first. Add this to your workflow:
```bash
gog gmail messages search "to:founder@company.com" --account your.email@firm.com
# Only draft if no SENT messages found
```

### Issue: "Too many false positives in triage"

**Solution:** Refine your trusted VC domain list and thesis keywords in `TOOLS.md`. Start conservative and expand.

---

## Next Steps

### Week 1: Foundation
- ✅ Complete all setup steps
- ✅ Test each workflow manually
- ✅ Build trust with your AI

### Week 2: Automation
- Enable daily briefings at a set time
- Let AI auto-respond to clear passes (with review)
- Start tracking metrics (emails triaged, drafts created, etc.)

### Week 3: Optimization
- Refine email classification rules
- Customize email templates to match your voice
- Add custom Affinity workflows

### Month 2+: Advanced
- Auto-generate memos when pitch decks arrive
- Integrate with additional tools (Slack, Twitter, etc.)
- Share learnings and improvements with the community

---

## Getting Help

**Documentation:**
- Read `SKILL.md` for detailed workflow documentation
- Check `templates/` for example configs

**Debugging:**
- Enable verbose logging in your AI config
- Check `~/clawd/logs/` for error messages
- Review `~/clawd/memory/YYYY-MM-DD.md` for daily activity logs

**Community:**
- Share feedback and improvements
- Report bugs or edge cases
- Contribute to the skill

---

## Security Checklist

Before going live:

- [ ] API keys stored securely (not in git)
- [ ] GOG_KEYRING_PASSWORD set and working
- [ ] AI configured to NEVER send emails without approval
- [ ] AI configured to NEVER message anyone except you
- [ ] Prompt injection protection enabled
- [ ] Private data stays private (no exfiltration)

---

## Success Criteria

You'll know setup is complete when:

1. ✅ Your AI can read and triage Gmail
2. ✅ Your AI can create draft emails
3. ✅ Your AI can log companies to Affinity
4. ✅ Your AI can generate investment memos
5. ✅ Your AI can check your calendar and share booking links
6. ✅ You receive a useful daily briefing

**Time to value:** Should be handling real workflows within 1 hour of setup completion.

---

## Congratulations! 🎉

Your VC workflow AI assistant is ready. Start with morning triage, build trust gradually, and iterate based on real usage.

Remember: Ship fast, learn from mistakes, stay focused on what saves you time.

For questions or improvements, see README.md.
