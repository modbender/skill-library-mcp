# Lead Gen Operator - Complete Setup Guide

## What You Get

A fully automated lead generation assistant that:
- Finds companies matching your criteria
- Enriches them with contact info
- Scores them based on funding & size
- Writes personalized outreach emails
- Tracks status from new to closed

**Price:** $19 (one-time)

---

## Step 1: Purchase

1. Go to Claw Mart
2. Search "Lead Gen Operator"
3. Click Buy for $19
4. Download the template package

---

## Step 2: Extract Files

```bash
cd ~/Downloads
unzip lead-gen-operator.zip
cd lead-gen-operator
```

You'll see:
```
lead-gen-operator/
├── SOUL.md           # Agent definition
├── memory-manager/    # Lead management tool
├── prompts/          # Optional prompts
└── README.md
```

---

## Step 3: Copy to OpenClaw Workspace

```bash
cp -r lead-gen-operator/* ~/.openclaw/workspace/
```

---

## Step 4: Test the Tool

### Find Your First Leads

```bash
# Find SaaS companies in USA (example)
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  add-lead leads.json "CompanyName" "" "" "11-50" "SaaS" "Series A"
```

Or search manually and add leads:

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  add-lead leads.json "Stripe" "" "" "100+" "Fintech" "$1.2B Series G"
```

### Score Leads

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  score-lead leads.json "Stripe"
```

### List All Leads

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  list leads.json
```

---

## Step 5: Write Outreach

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  write-outreach leads.json "Stripe"
```

This generates a personalized email and saves it to the lead.

### View the Outreach

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  get-outreach leads.json "Stripe"
```

---

## Step 6: Send Emails (Optional)

For email sending, you need Gmail connected. This is optional.

**Setup:**
1. Ensure you have Gmail via gog skill
2. When ready to send, say "Send to [company]" - I'll send via Gmail

---

## Step 7: Track Progress

### Update Status

```bash
# When you send email
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  update-status leads.json "Stripe" "sent"

# When they reply
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  update-status leads.json "Stripe" "replied"

# When they become a customer
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  update-status leads.json "Stripe" "closed"
```

### View Stats

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  stats leads.json
```

### Follow Up

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  get-followups leads.json
```

### Export to CSV

```bash
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js \
  export-csv leads.json
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Add lead | `add-lead leads.json "Name" "" "" "size" "industry" "funding"` |
| Score lead | `score-lead leads.json "Name"` |
| Write outreach | `write-outreach leads.json "Name"` |
| Get outreach | `get-outreach leads.json "Name"` |
| Update status | `update-status leads.json "Name" "sent"` |
| List leads | `list leads.json` |
| View stats | `stats leads.json` |
| Export CSV | `export-csv leads.json` |
| Follow ups | `get-followups leads.json` |

---

## Status Flow

```
new → enriched → drafted → sent → replied → closed
                      ↓
                    lost
```

---

## Tips

1. **Score first** - Higher score = better lead
2. **Write outreach before sending** - Review and edit as needed
3. **Follow up** - Use `get-followups` to see who needs attention
4. **Track everything** - Update status as deals progress

---

## Troubleshooting

**Command not found:**
```bash
export PATH="$HOME/.openclaw/workspace/skills/memory-manager:$PATH"
```

**No leads found:**
- Make sure you're in the right directory
- Check the filename matches (leads.json)

**Need help?**
- Check SOUL.md for agent instructions
- Ask for help in Discord
