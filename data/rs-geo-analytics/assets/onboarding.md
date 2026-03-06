# Rankscale GEO Analytics — First-Run Onboarding

## No Rankscale Account Yet?

**Visit:** https://rankscale.ai/dashboard/signup

Click **Start Free Trial** to sign up (14 days, no credit card).

After email verification, you'll land on your Dashboard.

---

## Step 1: Add Your Brand (Dashboard)

From your Dashboard:

  **1. Click "+ Add Brand"** (top right)

  **2. Fill in brand details:**
     - Brand Name (e.g., "Acme SaaS")
     - Domain (e.g., acmesaas.com)
     - Description (optional)
     - Product Names (optional)
     - Default Country & Language

  **3. Click "Create Brand"**

Rankscale begins collecting data. Initial report: 24-48 hours.

Your Brand ID appears in the brand card and dashboard URL:
  https://rankscale.ai/dashboard/brands/<YOUR_BRAND_ID>

---

## Step 2: Generate Your API Key (Settings)

Go to **Settings** (bottom left sidebar) →
**Integrations** section

Scroll to the bottom: **REST API** box

  **1. Click "Generate New Key"**

  **2. Copy your API Key**
     (format: `rk_...`)

  ⚠️  **Save this key immediately — it won't be shown again.**

---

## Step 3: Configure Your AI Assistant

Set environment variables in your shell or .env:

  export RANKSCALE_API_KEY="rk_..."
  export RANKSCALE_BRAND_ID="<YOUR_BRAND_ID>"

Or pass on command line:

  node rankscale-skill.js \
    --api-key rk_... \
    --brand-id <YOUR_BRAND_ID>

> ⚠️ **Security Warning:** Do not store plaintext secrets in ~/.zshrc. Use .env with chmod 600 or configure via OpenClaw Gateway env.

To persist credentials, use a .env file:

  echo 'RANKSCALE_API_KEY="rk_..."' >> .env
  echo 'RANKSCALE_BRAND_ID="..."' >> .env
  chmod 600 .env

---

## Step 4: Test the Skill

Ask your AI assistant:

  "Run a Rankscale GEO report"
  "Show my AI search visibility"
  "What's my GEO score?"

Or run directly:

  node rankscale-skill.js

You'll see your GEO Analytics report with:
- GEO Score (0–100)
- Citation Rate & Industry Average
- Sentiment Breakdown
- Top AI Search Terms
- Actionable GEO Insights

---

## Questions?

- **Docs:** https://docs.rankscale.ai
- **Support:** support@rankscale.ai
- **Discord:** https://discord.gg/rankscale

Once configured, your AI assistant can pull live GEO analytics
on demand. Just ask!
