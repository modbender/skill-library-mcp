---
name: Google Business Optimizer
description: "Small business owners waste 5-10 hours per week manually managing
  their Google Business Profile:"
---

# Google Business Optimizer

**Automate your Google Business Profile and save 5-10 hours every week.**

---

## The Problem

Small business owners waste 5-10 hours per week manually managing their Google Business Profile:

- **Responding to reviews** - Checking daily, crafting responses, monitoring ratings
- **Updating business info** - Holiday hours, special events, temporary closures
- **Tracking competitors** - Manual research to see how you stack up
- **Monitoring rankings** - Checking where you appear in local search results

**That's 20-40 hours per month** spent on tasks that could be automated.

---

## The Solution

Google Business Optimizer automates your entire Google Business Profile workflow:

### ✨ What It Does

| Feature | What You Get |
|---------|--------------|
| **Review Automation** | Auto-respond to reviews, get alerts for new reviews, track sentiment trends |
| **Smart Updates** | Bulk update hours, post updates, sync across multiple locations |
| **Competitor Intel** | Track competitor ratings, reviews, and ranking changes |
| **Rank Tracking** | Monitor your position for key local search terms |

---

## Commands

### `reviews`
Manage and respond to customer reviews automatically.

```bash
# Check for new reviews
google-business-optimizer reviews --check

# Auto-respond to all new reviews
google-business-optimizer reviews --respond --template=professional

# Get review analytics
google-business-optimizer reviews --stats --last-30-days

# List reviews needing response
google-business-optimizer reviews --pending
```

**Templates:** `professional`, `friendly`, `short`, `detailed`

---

### `update-hours`
Update business hours and special hours in bulk.

```bash
# Set regular hours
google-business-optimizer update-hours --location="Main St" \
  --monday="9:00-17:00" --tuesday="9:00-17:00" ...

# Set holiday hours
google-business-optimizer update-hours --holiday --date="2024-12-25" --closed

# Set special hours for event
google-business-optimizer update-hours --special --date="2024-07-04" --hours="10:00-14:00"

# Apply to all locations
google-business-optimizer update-hours --all-locations --holiday --date="2024-01-01" --closed
```

---

### `competitors`
Monitor your competitors' Google Business Profiles.

```bash
# Add competitors to track
google-business-optimizer competitors --add "Competitor Business Name"

# Run competitor analysis
google-business-optimizer competitors --analyze

# Get weekly report
google-business-optimizer competitors --report --format=email

# Compare ratings
google-business-optimizer competitors --compare --metric=rating
```

---

### `rank-track`
Track your ranking for local search keywords.

```bash
# Add keywords to track
google-business-optimizer rank-track --add "coffee shop near me"
google-business-optimizer rank-track --add "best pizza downtown"

# Check current rankings
google-business-optimizer rank-track --check

# View ranking history
google-business-optimizer rank-track --history --days=30

# Get ranking report
google-business-optimizer rank-track --report --keyword="coffee shop near me"
```

---

## Setup

### 1. Get Your Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Business Profile API**
4. Create OAuth 2.0 credentials
5. Download your `credentials.json`

### 2. Configure the Skill

```bash
google-business-optimizer config --credentials=/path/to/credentials.json
google-business-optimizer config --location-id="YOUR_LOCATION_ID"
```

### 3. Authorize

```bash
google-business-optimizer auth --login
```

---

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| **FREE** | $0 | 1 location, 50 reviews/month, basic responses |
| **PRO** | $19/mo | 5 locations, unlimited reviews, AI responses, competitor tracking (5) |
| **AGENCY** | $49/mo | Unlimited locations, unlimited reviews, white-label reports, API access, priority support |

---

## Automation (HEARTBEAT)

This skill integrates with OpenClaw's heartbeat system for hands-off automation:

- **Daily**: Check for new reviews and auto-respond
- **Weekly**: Competitor analysis report
- **Monthly**: Ranking report with trend analysis

See `HEARTBEAT.md` for configuration.

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GBP_API_KEY` | Google Business Profile API key | Yes |
| `GBP_LOCATION_ID` | Your business location ID | Yes |
| `GBP_ACCOUNT_ID` | Your Google account ID | Yes |
| `OPENAI_API_KEY` | For AI-generated responses (PRO+) | No |
| `SLACK_WEBHOOK` | For notifications | No |
| `EMAIL_TO` | For report delivery | No |

---

## Examples

### Auto-Respond to All New Reviews

```bash
google-business-optimizer reviews --respond-all --template=friendly
```

### Set Holiday Hours for All Locations

```bash
google-business-optimizer update-hours --all-locations \
  --holiday --date="2024-12-25" --date="2024-12-26" --date="2025-01-01" --closed
```

### Weekly Competitor Report

```bash
google-business-optimizer competitors --report --format=pdf --email=owner@business.com
```

### Track 10 Local Keywords

```bash
for keyword in "coffee shop" "cafe near me" "best espresso" "latte art" "pastry shop"; do
  google-business-optimizer rank-track --add "$keyword"
done
```

---

## Support

- 📧 Email: support@google-business-optimizer.local
- 📖 Docs: https://docs.google-business-optimizer.local
- 💬 Discord: https://discord.gg/gbp-optimizer

---

## Changelog

### v1.0.0
- Initial release
- Review automation with templates
- Business hours management
- Competitor tracking
- Rank tracking
- HEARTBEAT automation support
