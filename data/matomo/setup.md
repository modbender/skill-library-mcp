# Setup — Matomo Analytics

Read this when `~/matomo/` doesn't exist or is empty.

## Your Attitude

You're helping someone unlock insights from their own analytics data. Matomo users chose self-hosting for privacy and control — respect that. Be enthusiastic about what they can learn from their data.

## Priority Order

### 1. First: Understand Their Setup

Ask about their Matomo environment:
- "What sites are you tracking?" (get names and rough purposes)
- "What metrics matter most to you?" (traffic? conversions? engagement?)
- "Any specific goals you're tracking?"

Don't ask for technical details yet — understand the business context first.

### 2. Then: Connection Details

When they're ready to actually query data:
- Ask for their Matomo URL
- Guide them to create an API token (Settings → Personal → Security → Auth tokens)
- Help them store it securely (env var or keychain)

**Token security:** Recommend storing in env var `MATOMO_TOKEN` or system keychain. Never store tokens in plain text files.

### 3. Finally: Integration

Ask how they want to use the skill:
- "Should I help with analytics whenever you mention traffic or metrics?"
- "Want weekly reports, or just on-demand queries?"

## What You're Saving

In `~/matomo/memory.md`:
- Site names and their idSite numbers
- Which metrics they care about
- Default site for quick queries
- Credential reference name (not the actual token)

## Feedback After Each Response

After they share something:
1. Reflect what you understood
2. Connect it to what insights you can provide
3. Then continue

Example:
> User: "I run an e-commerce site, about 10k visitors/month, I care most about conversion rate"
>
> Good: "E-commerce with 10k monthly visitors — solid base. Conversion rate is the lever that matters most at your scale. I'll focus on that whenever we look at data. What's your current conversion rate, roughly?"
