# Quick Start - Clawdbot for VCs

Get running in 30 minutes.

---

## Prerequisites

- Clawdbot installed
- Gmail account
- Google Calendar
- Affinity CRM account

---

## 5-Minute Overview

**What this does:**
- Auto-triages 50+ emails/day
- Drafts pass emails for clear no-gos
- Logs companies to Affinity CRM
- Generates investment memos
- Manages calendar with booking links
- Daily briefing of what matters

**Philosophy:** Your AI proposes, you approve. Safe by default.

---

## Setup (30 minutes)

### 1. Install gog CLI (5 min)

```bash
# Install Go if needed: https://go.dev/doc/install
go install github.com/martynsmith/gog@latest
export PATH="$PATH:$(go env GOPATH)/bin"

# Authenticate
gog auth
# Follow browser prompts for Gmail + Calendar

# Set keyring password
echo "YourPassword123" | base64  # Save output
export GOG_KEYRING_PASSWORD=$(echo "OUTPUT_HERE" | base64 -d)

# Test
gog gmail messages list --max 1 --account your.email@firm.com
```

### 2. Set Up Affinity (5 min)

```bash
# Get API key: Affinity Settings → API
export AFFINITY_API_KEY="your_key_here"

# Test
curl -u ":$AFFINITY_API_KEY" https://api.affinity.co/auth
# Should return: {"success": true}

# Find your Person ID
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/persons?term=YourName" | jq

# Find your Deal Pipeline List ID
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/lists" | jq
```

### 3. Create Gmail Labels (2 min)

```bash
# Create triage labels
for label in "Triage/Priority" "Triage/Review" "Triage/Auto-Respond" "Triage/Archive" "Triage/Pending-Response" "Triage/Draft-Pending"; do
  gog gmail labels create "$label" --account your.email@firm.com
done

# Get label IDs
gog gmail labels list --account your.email@firm.com
```

### 4. Set Up Booking Pages (10 min)

1. Go to [Google Calendar Settings](https://calendar.google.com/calendar/u/0/r/settings)
2. Click "Appointment schedules"
3. Create these 6 booking pages:

| Type | Duration | Buffer |
|------|----------|--------|
| Intro Call | 30 min | 15 min |
| Follow Up | 30 min | 15 min |
| Diligence | 60 min | 15 min |
| Portfolio | 30 min | 10 min |
| Network Investors | 30 min | 15 min |
| Priority | 30 min | 0 min |

4. Copy all booking links

### 5. Configure Clawdbot (8 min)

```bash
cd ~/clawd

# Copy templates
cp skills/clawdbot-for-vcs/templates/USER.md.example USER.md
cp skills/clawdbot-for-vcs/templates/TOOLS.md.example TOOLS.md

# Edit USER.md
# - Add your name, email, timezone
# - Add your investment thesis keywords

# Edit TOOLS.md
# - Add booking links
# - Add Gmail label IDs
# - Add Affinity Person ID and List ID
# - Add field IDs for Deal Stage, Owner, One Liner

# Add to AGENTS.md (append to existing file)
cat skills/clawdbot-for-vcs/templates/AGENTS.md.example >> AGENTS.md
```

---

## First Use (5 minutes)

### Test Email Triage

Message your AI:
```
"Check my email and triage"
```

Should return:
- Priority emails (warm intros)
- Review emails (need decisions)
- Auto-respond candidates

### Approve a Draft

```
"Draft a pass email for [founder email]"
```

AI will show you the draft. Reply:
```
"send"
```

Draft appears in Gmail for final review.

### Generate a Memo

```
"Generate memo for [Company Name]"
```

AI will auto-search Gmail and Affinity, then generate comprehensive memo.

### Check Calendar

```
"What's on my calendar today?"
```

### Daily Briefing

```
"What's my daily briefing?"
```

---

## Configuration Quick Reference

### Add to ~/.bashrc or ~/.zshrc

```bash
export GOG_KEYRING_PASSWORD=$(echo "YOUR_BASE64_PASSWORD" | base64 -d)
export AFFINITY_API_KEY="your_affinity_key"
export PATH="$PATH:$(go env GOPATH)/bin"
```

Then: `source ~/.bashrc`

---

## Common Commands

**Email:**
```bash
# Search
gog gmail search "QUERY" --account your.email@firm.com

# Create draft
gog gmail drafts create --to "email@example.com" \
  --subject "Subject" --body-html "<p>Body</p>" \
  --account your.email@firm.com
```

**Affinity:**
```bash
# Search company
curl -u ":$AFFINITY_API_KEY" \
  "https://api.affinity.co/organizations?term=CompanyName"

# Create note
curl -u ":$AFFINITY_API_KEY" -X POST \
  "https://api.affinity.co/notes" \
  -H "Content-Type: application/json" \
  -d '{"organization_ids": [ORG_ID], "content": "Note text"}'
```

**Calendar:**
```bash
# View events
gog calendar events --from $(date +%Y-%m-%d) \
  --to $(date -d "+7 days" +%Y-%m-%d) \
  --account your.email@firm.com
```

---

## Example Workflows

### Morning Routine (5 min)

```
You: "What's my daily briefing?"

AI: [Shows Priority emails, today's calendar, suggested actions]

You: "Draft intro responses for both Priority emails"

AI: [Creates drafts with booking links]

You: "send both"

AI: ✓ Drafts created in Gmail
```

### Pass Email (30 sec)

```
You: "Pass on email from founder@startup.com"

AI: [Shows draft pass email]
    Should I log to Affinity?

You: "yes"

AI: ✓ Draft created
    ✓ Added to Affinity (Stage: Passed)
    ✓ Email archived
```

### Memo Generation (10 min)

```
You: "Generate memo for DataCorp"

AI: [Searches Gmail + Affinity]
    Found: 1 pitch deck, intro email, 2 Affinity notes
    Ready to generate?

You: "yes"

AI: ✓ Memo saved to ~/memos/datacorp.md
    Completeness: Medium (60%)
    Push to Affinity?

You: "yes"

AI: ✓ Memo added to Affinity as note
```

---

## Troubleshooting

### "gog command not found"
```bash
export PATH="$PATH:$(go env GOPATH)/bin"
```

### "Affinity API 401"
```bash
echo $AFFINITY_API_KEY  # Should print your key
curl -u ":$AFFINITY_API_KEY" https://api.affinity.co/auth
```

### "Gmail drafts not appearing"
```bash
gog gmail drafts list --account your.email@firm.com
```

### "AI is creating duplicate emails"
Your AI should check for existing sent messages first. Verify this is in your AGENTS.md workflow.

---

## Next Steps

**Week 1:**
- ✅ Use morning triage daily
- ✅ Approve all drafts before sending
- ✅ Track what works and what doesn't

**Week 2:**
- Enable daily briefings at set time
- Let AI auto-respond to clear passes (with review)
- Refine email classification rules

**Month 2+:**
- Increase autonomy for proven workflows
- Customize templates to match your voice
- Integrate with additional tools

---

## Full Documentation

- **[BOOTSTRAP.md](./BOOTSTRAP.md)** - Detailed setup guide
- **[SKILL.md](./SKILL.md)** - Complete workflow documentation
- **[README.md](./README.md)** - Overview and examples

---

## Support

- Issues: [GitHub Issues](https://github.com/clawdhub/clawdbot-for-vcs/issues)
- Questions: [GitHub Discussions](https://github.com/clawdhub/clawdbot-for-vcs/discussions)
- Email: lindsay@villageglobal.com

---

**Time to value:** Should be triaging email and creating drafts within 1 hour of setup completion.

Good luck! 🚀
