# ProductAI Integration - Questions for Users

This document contains the key questions to ask users when setting up ProductAI integration, along with the easiest setup flow.

---

## Pre-Integration Questions

### 1. Do you have a ProductAI account?

**If NO:**
- Direct them to: **[https://www.productai.photo](https://www.productai.photo)**
- They need to sign up and choose a plan (Basic, Standard, or Pro)
- Wait for them to complete signup

**If YES:**
- Proceed to question 2

---

### 2. Do you have a ProductAI API key?

**If NO:**
- Guide them: "Go to ProductAI Studio → **API Access** → Generate API Key"
- Wait for them to copy the key
- **Important:** Remind them to keep it secret!

**If YES:**
- Ask them to have it ready (they'll paste it in setup)

---

### 3. What plan are you on?

Options:
- **Basic** ($8/month) — 70 + 20 free credits
- **Standard** ($16/month) — 250 + 20 free credits
- **Pro** ($49/month) — 950 + 20 free credits

This helps set expectations for token usage.

---

### 4. What will you use ProductAI for?

Common answers:
- E-commerce product photos (clean backgrounds, lifestyle shots)
- Marketing campaigns (hero images, social media)
- Batch processing product catalogs
- Creative compositing (multi-image scenes)
- Image upscaling for print/high-res

This helps recommend the right model and workflow.

---

## Super Easy Setup Flow

### Step 1: Verify They Have an API Key

```
Agent: "To use ProductAI, you'll need an API key. Do you have one?"

User: "No" → Guide to productai.photo, wait
User: "Yes" → Proceed
```

---

### Step 2: Run Setup

**Option A: Interactive (User runs script)**

```bash
cd ~/.openclaw/workspace/productai
./scripts/setup.py
```

The script asks:
1. **API Key:** User pastes key
2. **API Endpoint:** [Press Enter for default]
3. **Default Model:** [Press Enter for nanobanana]
4. **Default Resolution:** [Press Enter for 1024x1024]
5. **Your Plan:** basic / standard / pro

**Option B: Agent-Driven (Programmatic)**

```python
# Agent collects API key in conversation
api_key = user_message  # e.g., "sk_prod_abc123..."

# Agent creates config
import json
from pathlib import Path

config = {
    "api_key": api_key,
    "api_endpoint": "https://api.productai.photo/v1",
    "default_model": "nanobanana",
    "default_resolution": "1024x1024",
    "plan": "standard"  # Or ask user
}

config_path = Path.home() / '.openclaw' / 'workspace' / 'productai' / 'config.json'
config_path.parent.mkdir(parents=True, exist_ok=True)

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

config_path.chmod(0o600)

# Confirm to user
print("✓ ProductAI configured! Your API key is saved securely.")
```

---

### Step 3: Test It Immediately

**Run a quick test to confirm setup works:**

```bash
./scripts/generate_photo.py \
  --image "https://i.imgur.com/sample.jpg" \
  --prompt "white background" \
  --output test.png
```

**If successful:**
```
✓ Job created: 12345
Waiting for completion...
✓ Generation complete!
Downloading image to test.png...
✓ Saved to test.png
```

**If failed:**
- `401 Unauthorized` → Invalid API key (ask user to regenerate)
- `OUT_OF_TOKENS` → No credits left (ask user to purchase more)
- Other errors → Check error message and guide user

---

## Making API Key Input Super Easy

### Best Practices

**✅ DO:**
1. **Provide direct link:** "Get your key here: [https://www.productai.photo/api-access](https://www.productai.photo)"
2. **Show exactly where to find it:** "Look for **API Access** in your dashboard"
3. **Auto-validate:** Test the API key immediately after setup
4. **Give clear feedback:** "✓ API key valid!" or "❌ Invalid key, please check and try again"
5. **Secure it automatically:** Set file permissions to 600 (user-only read/write)

**❌ DON'T:**
1. Ask for info you can auto-detect (API endpoint, default model)
2. Show raw JSON or complex config formats
3. Leave users wondering if setup worked (always test!)
4. Display the API key in logs or responses (security!)

---

## Sample Conversation Flow

```
Agent: "Ready to set up ProductAI! Do you have an API key?"

User: "No"

Agent: "No problem! Here's what to do:

1. Visit https://www.productai.photo
2. Log in (or sign up if you're new)
3. Go to **API Access**
4. Copy your API key

Let me know when you have it!"

---

User: "Got it: sk_prod_abc123xyz"

Agent: "Perfect! Setting that up now..."
[Creates config.json programmatically]

Agent: "✓ API key saved securely!

Want to test it? Send me a product image URL and I'll generate 
a version with a clean white background."

---

User: "https://example.com/watch.jpg"

Agent: [Runs generate_photo.py]
"Here's your product with a white studio background! 🎨
[Sends generated image]

Cost: 3 tokens (Nano Banana model)

What else would you like to create?"
```

---

## Error Recovery

### Invalid API Key (401)

```
Agent: "Hmm, that API key didn't work. Here's what to check:

1. Make sure you copied the full key (starts with 'sk_prod_')
2. Verify it's active in ProductAI Studio → API Access
3. Try regenerating a new key if needed

Want to try again?"
```

---

### Out of Tokens

```
Agent: "You're out of tokens! Here's how to get more:

- **Purchase tokens:** Visit productai.photo
- **Upgrade plan:** Get more monthly credits with Standard or Pro

Your current plan: [plan]

Let me know when you're ready to continue!"
```

---

### Rate Limited (429)

```
Agent: "ProductAI has a rate limit of 15 requests/minute. 
Let's wait a moment before trying again..."

[Auto-retry after 10 seconds]
```

---

## Key Takeaways

1. **Minimize friction:** Only ask what you absolutely need (API key, plan)
2. **Validate immediately:** Test the API key right after setup
3. **Provide clear guidance:** Direct links, step-by-step, screenshots
4. **Handle errors gracefully:** Clear messages + recovery steps
5. **Make it conversational:** Feel like talking to a helpful human

---

**Goal:** User gets from "I want to use ProductAI" to "Here's my first generated image" in under 2 minutes.
