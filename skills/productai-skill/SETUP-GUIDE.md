# ProductAI Integration Setup Guide

**Goal:** Make getting your ProductAI API key and integrating it with OpenClaw as easy as possible.

## For End Users: Getting Started

### Step 1: Get Your ProductAI API Key

**Option A: If you already have a ProductAI account**

1. Go to **[https://www.productai.photo](https://www.productai.photo)**
2. Log in to your account
3. Navigate to **API Access** (in the dashboard/settings)
4. You'll see your API key displayed — copy it
5. If no key exists, click **Generate API Key**

**Option B: If you're new to ProductAI**

1. Go to **[https://www.productai.photo](https://www.productai.photo)**
2. Sign up for an account
3. Choose a plan (Basic, Standard, or Pro)
4. Once logged in, go to **API Access**
5. Generate your first API key

**⚠️ Important:** Keep your API key secret! Don't share it publicly or commit it to version control.

### Step 2: Run the Setup Script

Open your terminal and run:

```bash
cd ~/.openclaw/workspace/productai
./scripts/setup.py
```

The script will ask you a few questions:

**Q: API Key:**
Paste the key you copied from ProductAI Studio.

**Q: API Endpoint:**
Just press Enter (uses default: `https://api.productai.photo/v1`)

**Q: Default Model:**
Press Enter (uses `nanobanana` — good balance of speed and quality)

**Q: Default Resolution:**
Press Enter (uses `1024x1024`)

**Q: Your Plan:**
Enter `basic`, `standard`, or `pro` depending on your ProductAI subscription.

**That's it!** Your configuration is saved and secured.

### Step 3: Test It

Run a quick test to make sure everything works:

```bash
./scripts/generate_photo.py \
  --image "https://example.com/test-product.jpg" \
  --prompt "white background" \
  --output test.png
```

If you see:
```
✓ Job created: 12345
  Status: RUNNING

Waiting for completion...

✓ Generation complete!
Image URL: https://...
Downloading image to test.png...
✓ Saved to test.png
```

**You're all set!** 🎉

---

## For Skill Creators: Integration Checklist

When building a ProductAI integration for OpenClaw users, here's what to prepare:

### Pre-Integration Questions to Ask

**1. Account Status**
- Do you have a ProductAI account? (Yes / No)
- If yes, which plan? (Basic / Standard / Pro)

**2. API Access**
- Have you generated an API key? (Yes / No)
- If yes, do you have it handy?

**3. Use Case**
- What will you use ProductAI for?
  - E-commerce product photos?
  - Marketing campaigns?
  - Social media content?
  - Other?

### Setup Flow

**Path A: User has API key already**
```
1. Run setup script
2. Paste API key
3. Test with sample generation
4. Done!
```

**Path B: User needs to get API key**
```
1. Direct to productai.photo
2. Guide through signup/login
3. Navigate to API Access
4. Copy key
5. Run setup script
6. Paste key
7. Test
8. Done!
```

### Making It "Super Easy"

**✅ DO:**
- Provide direct links to API Access page
- Show screenshots of where to find the key
- Auto-detect common issues (missing config, invalid key)
- Test API key immediately after setup
- Give clear success/failure messages
- Provide example commands users can copy-paste

**❌ DON'T:**
- Ask for information you can auto-detect (endpoint URL, default model)
- Require manual JSON editing
- Show raw error messages without explanation
- Leave users wondering if setup worked

### Sample Setup Conversation Flow

```
Agent: "Hey! To use ProductAI, I'll need your API key. Do you have one?"

User: "No"

Agent: "No problem! Here's how to get one:

1. Visit https://www.productai.photo
2. Sign up or log in
3. Go to API Access
4. Copy your API key

Let me know when you have it!"

User: "Got it: sk_prod_abc123..."

Agent: "Perfect! Setting that up now..."
[Runs setup script programmatically]

Agent: "✓ API key saved and tested! Want to try generating an image?"

User: "Sure"

Agent: "Great! Send me a product image URL and tell me what background you want."

User: "https://example.com/watch.jpg — modern office desk"

Agent: [Runs generate_photo.py]
"Here's your result! [image]"
```

### Error Handling

**Invalid API Key (401)**
```
Agent: "Hmm, that API key didn't work. Double-check it in ProductAI Studio → API Access. 
Want to try again or regenerate a new key?"
```

**Out of Tokens**
```
Agent: "Looks like you're out of tokens. You can:
- Purchase more tokens at productai.photo
- Upgrade your plan for more monthly credits

Let me know when you're ready to try again!"
```

**Rate Limited (429)**
```
Agent: "ProductAI has a rate limit of 15 requests/minute. Let's wait a bit before trying again."
[Auto-retry after delay]
```

---

## Technical Implementation Notes

### Config File Structure

```json
{
  "api_key": "sk_prod_...",
  "api_endpoint": "https://api.productai.photo/v1",
  "default_model": "nanobanana",
  "default_resolution": "1024x1024",
  "plan": "standard"
}
```

- Stored at: `~/.openclaw/workspace/productai/config.json`
- Permissions: `600` (user read/write only)
- Never log or display the API key

### Testing the API Key

After setup, immediately test with a simple API call:

```python
import requests

response = requests.get(
    "https://api.productai.photo/v1/api/job/1",  # Dummy job ID
    headers={"x-api-key": api_key}
)

if response.status_code == 401:
    print("❌ Invalid API key")
elif response.status_code in [200, 404]:
    print("✓ API key valid!")
else:
    print(f"⚠️ Unexpected response: {response.status_code}")
```

### Programmatic Setup (For Agents)

Agents can run setup programmatically instead of interactively:

```python
import json
from pathlib import Path

config = {
    "api_key": user_provided_key,
    "api_endpoint": "https://api.productai.photo/v1",
    "default_model": "nanobanana",
    "default_resolution": "1024x1024",
    "plan": user_plan or "standard"
}

config_path = Path.home() / '.openclaw' / 'workspace' / 'productai' / 'config.json'
config_path.parent.mkdir(parents=True, exist_ok=True)

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

config_path.chmod(0o600)
```

---

## FAQ

**Q: Do I need to install anything?**
A: Python dependencies are auto-installed. Just run the setup script.

**Q: Can I change my API key later?**
A: Yes! Just run `./scripts/setup.py` again and it will overwrite the old config.

**Q: Where is my API key stored?**
A: In `~/.openclaw/workspace/productai/config.json` (secured with 600 permissions).

**Q: Can I use this with multiple ProductAI accounts?**
A: You can only have one API key configured at a time. To switch accounts, run setup again.

**Q: What if I run out of tokens?**
A: Visit ProductAI Studio to purchase more or upgrade your plan.

**Q: How do I know how many tokens I have left?**
A: Check your ProductAI Studio dashboard for current balance.

---

**Questions or issues?** Check [SKILL.md](SKILL.md) or [API.md](references/API.md) for more details.
