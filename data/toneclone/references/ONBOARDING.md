# ToneClone Onboarding Guide

Guided setup for new users. Focus on getting ONE persona working first, then expand.

## Onboarding Principles

1. **Install automatically** — offer to run the install command, don't make users do it manually
2. **One persona first** — don't overwhelm with options; get one use case working, then offer to add more
3. **Low barrier to start** — minimum 2-3 samples to begin, target 10-15, max 30-50
4. **Explain concepts** — introduce knowledge cards before using the term
5. **Handle rate limits gracefully** — upload with delays, explain if issues occur

## Onboarding Flow

1. Installation (offer to do it automatically)
2. Authentication
3. Discovery (pick ONE use case to start)
4. Create ONE persona
5. Training data collection (with consent)
6. Knowledge card creation (explain what they are first)
7. Wait for training (use time productively)
8. Test generation
9. Offer to add more personas/cards
10. StyleGuard & Typos (optional)
11. Workflow integration

---

## Step 1: Installation

Check if ToneClone CLI is installed:
```bash
which toneclone
```

If not installed, **offer to install via Homebrew**:

"ToneClone CLI isn't installed yet. Want me to install it for you?"

```bash
brew tap toneclone/toneclone && brew install toneclone
```

For non-macOS or manual install, direct them to: https://github.com/toneclone/cli

---

## Step 2: Authentication

Check if already authenticated:
```bash
toneclone auth status
```

If not authenticated, **you'll need an API key**. 

**Say something like**: "To use ToneClone, you'll need an API key. You can get one free at https://app.toneclone.ai — go to Settings → API Keys after signing up. Want me to open that for you, or do you already have a key?"

Once they have a key:
```bash
toneclone auth login --key <their-api-key>
```

Or if they prefer a browser flow:
```bash
toneclone auth login
```

---

## Step 3: Discovery (ONE Use Case)

**Don't list all the options at once.** Ask a simple, focused question:

"What's ONE type of message you'd like me to help draft for you? For example:
- Quick chat replies
- Work emails
- Social posts

Pick whichever you use most often — we can always add more later."

**Wait for their answer.** Don't overwhelm with follow-up questions about multiple personas yet.

---

## Step 4: Create ONE Persona

Based on their answer, create a single persona:

```bash
toneclone personas create --name="Chat"
```

Explain briefly: "I created a 'Chat' persona. This will learn your casual chat style. Now I need some examples of how you write."

---

## Step 5: Training Data Collection

### Training Sample Guidelines

**Communicate approachable numbers:**
- Minimum: 2-3 samples (enough to get started)
- Target: 10-15 samples (good quality)
- Maximum to start: 30-50 (more isn't always better initially)

**Say something like**: "I need a few examples of your writing to learn your style. Even 2-3 messages is enough to start, though 10-15 would be better. Don't worry about finding tons — we can always add more later."

### Check What's Available

Review what training sources you have access to:

| Source | How to Check |
|--------|--------------|
| OpenClaw chat history | Session history access |
| Messaging channels | Telegram/Signal/Discord configured? |
| Email | IMAP access configured? |
| Workspace files | Check user's workspace/documents |
| Public writing | Ask user for blog/social URLs |

### Present Options

"I can pull from a few sources. Here's what I found:
- [X] messages from our chat history
- [X] files in your workspace

Want me to use some of these? I won't train without your approval."

### Get Consent

**Never train without explicit user consent.**

### Upload with Rate Limit Handling

**Important**: When uploading multiple samples, add delays between uploads to avoid rate limits.

```bash
# Upload with 2-second delays between files
for file in samples/*.txt; do
  toneclone training add --file="$file" --persona="Chat"
  sleep 2
done
```

**If rate limited**: Explain to the user: "Hit a rate limit — I'll slow down and continue uploading. This is normal when adding many samples at once."

For single uploads:
```bash
toneclone training add --file=sample1.txt --persona="Chat"
```

For direct text (add delays between multiple):
```bash
toneclone training add --text="Message content" --persona="Chat" --filename="sample1.txt"
sleep 2
toneclone training add --text="Another message" --persona="Chat" --filename="sample2.txt"
```

### Training Data Rules

- **One sample per file** — keep samples separate, don't combine
- **No secrets** — remove API keys, passwords, tokens before uploading
- **Match the target style** — casual samples for casual persona, formal for formal

---

## Step 6: Knowledge Cards (Explain First!)

### Introduce the Concept

**Before mentioning "knowledge cards", explain what they are:**

"While your persona trains, let me explain something useful: I can store context that helps me write better messages for you — things like your name, timezone, calendar link, or common info you share. This way I don't have to ask every time.

These are called 'knowledge cards' — think of them as reference notes I can pull from when drafting messages."

### Then Offer to Create

"I already know a few things about you:
- Name: [name]
- Timezone: [timezone]

Want me to save these so I can use them when writing for you? You can also add things like:
- Email address
- Calendar/booking link
- Common links you share"

### Create Cards (with consent)

```bash
toneclone knowledge create --name="About Me" \
  --instructions="Name: [name]. Timezone: [tz]. Email: [email]."
```

### Associate with Persona

```bash
toneclone knowledge associate --knowledge="About Me" --persona="Chat"
```

### Security Note

No secrets (API keys, passwords, tokens) in knowledge cards.

---

## Step 7: Wait for Training

Training takes 1-5 minutes. 

### Check Status
```bash
toneclone personas get <persona-id> --format=json
```
Poll every 30s. Look for `trainingStatus: READY`.

### Use the Wait Time

While waiting, you can:
- Create knowledge cards (Step 6)
- Discuss what messages they want help with
- Explain how to use ToneClone once it's ready

---

## Step 8: Test Generation

Once training is complete:

```bash
toneclone write --persona="Chat" \
  --prompt="Quick message to a friend about weekend plans"
```

### Feedback Loop

"Does this sound like you? What would you change?"

If not right:
- Wrong style → Add more training samples
- Missing context → Add knowledge cards
- Too formal/casual → Check persona selection

---

## Step 9: Offer to Add More

**Only after the first persona is working**, offer to expand:

"Now that your Chat persona is set up, would you like to create another one? For example:
- A more professional style for emails
- A different voice for social media

Or we can stop here and add more later whenever you want."

---

## Step 10: StyleGuard & Typos (Optional)

### StyleGuard
"Want me to auto-replace AI-sounding phrases like 'delve', em-dashes, etc.?"

```bash
toneclone personas style-guard bundle apply --persona <persona> --type comprehensive
```

### Typos (FingerPrint)
"Want subtle typos to make output feel more natural/human?"

```bash
toneclone personas typos set <persona> --enable --intensity subtle --protected urls,emails
```

---

## Step 11: Workflow Integration

"When should I use ToneClone automatically vs only when you ask?"

Record preferences in OpenClaw memory:
```
ToneClone preferences:
- Use "Chat" persona for Telegram messages
- Skip ToneClone for technical discussions
```

---

## Onboarding Complete

Summarize what was set up:
- ✅ Persona: [name] — trained and ready
- ✅ Knowledge cards: [list]
- ✅ Workflow preferences: [summary]

Remind them:
- "You can add more personas anytime"
- "I can update knowledge cards whenever you want"
- "Just tell me if you want to adjust when I use ToneClone"

---

## Quick Reference

| Need | Action |
|------|--------|
| Different writing style | Create new persona |
| Different context (same style) | Create/use knowledge card |
| AI needs to "remember" something | Add to knowledge card |
| Change when ToneClone is used | Update workflow preferences |
