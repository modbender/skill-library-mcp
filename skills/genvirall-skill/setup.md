# Setup Guide

This guide is for agents helping users get started with Genviral. Read this during onboarding and walk your human through it conversationally.

## What to Tell Your Human First

Before anything else, explain:

> Everything you do through this skill (posts, slideshows, image packs, scheduled content) shows up in the Genviral dashboard at genviral.io. You can always see, edit, or manage things in the UI. The agent and the dashboard are two views of the same system.

This is important. People worry about agents doing things they can't see or control. Reassure them.

## Step 1: API Key

Get your API key from https://www.genviral.io (Settings > API Keys), then set it:

```bash
export GENVIRAL_API_KEY="your_public_id.your_secret"
```

Add it to your environment file to persist across sessions.

**Test it works:**
```bash
genviral.sh accounts
```

If this returns your connected accounts, you're good.

## Step 2: Pick Your Account(s)

List all connected accounts:

```bash
genviral.sh accounts
```

Ask your human which account(s) they want to post to. Could be one, could be several. Set the IDs in `config.md`:

```yaml
posting:
  default_account_ids: "ACCOUNT_ID_1"  # comma-separated for multiple
```

## Step 3: Images (Let the User Decide)

This is where it gets flexible. **Do NOT hardcode a default pack.** Instead, explain the options:

### Option A: Use an existing image pack
```bash
genviral.sh list-packs
```
Show them what's available (their own packs + community packs). If they like one, great. Set it in config or pass it per-slideshow.

### Option B: Create a new pack
Ask what kind of images fit their brand. Then either:
- Help them upload images: `genviral.sh create-pack --name "My Pack"` then `genviral.sh add-pack-image --pack-id X --url "https://..."`
- Suggest they create one in the Genviral UI (drag and drop is easier for bulk uploads)

### Option C: Generate images per post
The agent can generate images (via OpenAI, etc.) for each slideshow instead of pulling from a pack. No pack needed. More variety, but costs per image and less visual consistency.

### Option D: Mix and match
Use a pack for some posts, generate fresh images for others. The agent can decide based on the content.

**The key message:** Packs are a convenience, not a requirement. The agent can work with or without them.

## Step 4: Product Context (Optional but Recommended)

Ask your human about their product. Fill in `context/product.md` together:
- What's the product?
- Who's it for?
- What are the key features?
- What's the website?

Then fill in `context/brand-voice.md`:
- How should content sound? (casual, professional, witty?)
- Any words or phrases to avoid?
- Example captions they like?

These files make the agent's content way more relevant. But they're optional. The agent can start posting with just an account and some images.

## Step 5: First Post

Walk them through creating their first slideshow:

```bash
genviral.sh generate --prompt "Your prompt here"
genviral.sh render --slideshow-id SLIDESHOW_ID
genviral.sh create-post --caption "your caption" --media-type slideshow --slideshow-id SLIDESHOW_ID --accounts ACCOUNT_ID
```

Or use the full pipeline command if they want it all in one go.

**Remind them:** For TikTok, posting as a draft lets them add trending music before publishing. That's often the best workflow.

## What's Next?

Once they're posting, the agent can:
- Set up a daily content cron (see `cron-setup.md`)
- Track performance via analytics
- Build a hook library based on what works
- Run weekly strategy reviews

The skill self-improves over time. The more it posts and tracks, the better it gets at picking hooks and timing.

## Onboarding Tone

Be helpful, not overwhelming. Don't dump all 42 commands on them. Start with:
1. "Let's get your API key set up"
2. "Which account do you want to post to?"
3. "Do you have images ready, or want me to help with that?"
4. "Let's make your first post together"

That's it. Everything else comes naturally as they use the skill.
