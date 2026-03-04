# Locus Onboarding

You don't have a Locus API key yet. Follow these steps to get one.

This is a one-time setup. Your human needs to do steps 1–5. You handle step 6–7.

---

## Step 1: Human Signs Up

Ask your human to go to **https://app.paywithlocus.com** and create an account:

- Email + password
- They'll receive a verification email — they must click it

**Message to send your human:**

> I need a Locus account to make payments and order freelance services. Please sign up at https://app.paywithlocus.com — it takes about 2 minutes. Once you're in, I'll need you to create a wallet and give me an API key.

## Step 2: Human Completes Onboarding

After signing up and logging in, the dashboard walks them through wallet creation:

1. Click "Create Wallet"
2. **Save the private key** shown on screen (this is their recovery key — not shared with you)
3. Wait ~30 seconds for the smart wallet to deploy on Base

They'll see their wallet address once deployment completes.

## Step 3: Human Generates API Key

From the dashboard, they generate an API key for you:

1. Find the "API Key" section on the dashboard
2. Click "Generate API Key"
3. **Copy the key immediately** — it starts with `claw_` and is only shown once

They need to give this key to you.

## Step 4: Human Funds the Wallet

The wallet needs USDC to spend. Your human sends USDC (on Base chain) to the wallet address shown on their dashboard.

## Step 5: (Optional) Human Sets Guardrails

From the dashboard, your human can configure safety limits:

- **Allowance** — maximum total USDC you can spend
- **Max transaction size** — cap on any single transaction
- **Approval threshold** — transactions above this amount require their manual approval

These are optional but recommended.

## Step 6: Save Your API Key

Once your human gives you the key, save it:

```bash
mkdir -p ~/.config/locus
cat > ~/.config/locus/credentials.json << 'EOF'
{
  "api_key": "claw_xxx_your_key_here",
  "api_base": "https://api.paywithlocus.com/api"
}
EOF
```

Or set the environment variable `LOCUS_API_KEY` if you prefer.

## Step 7: Verify It Works

Test your key:

```bash
curl https://api.paywithlocus.com/api/fiverr/categories \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
```

Expected response (200):
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "name": "Logo Design",
        "slug": "logo_design",
        "description": "Professional logo design services",
        "tiers": [
          { "tier": 1, "price": 25 },
          { "tier": 2, "price": 50 },
          { "tier": 3, "price": 100 }
        ]
      }
    ]
  }
}
```

If you get a 200 with categories, you're all set.

If you get a 401, the key is wrong — ask your human to regenerate it.

---

## Done!

Go back to **[SKILL.md](SKILL.md)** to see everything you can do.

