---
name: obverse-payments
description: End-to-end stablecoin payments — links, invoices, receipts, dashboards — across Telegram, WhatsApp, Discord
homepage: https://www.obverse.cc
user-invocable: true
metadata:
  openclaw:
    requires:
      env: ["OBVERSE_API_KEY"]
    primaryEnv: "OBVERSE_API_KEY"
---

# Obverse - Stablecoin Payments for AI Agents

**One generic payment link. Multiple use cases.**

Accept Stablecoin (USDC) payments on Solana and Monad for any purpose: selling products, fundraising, invoicing, or simple payments.

## What This Skill Does

✅ **Create Payment Links** - One flexible payment link for all use cases
✅ **Collect Customer Data** - Gather email, name, phone, or ANY custom fields you need
✅ **Dashboard Analytics** - Get detailed payment stats, customer lists, and charts
✅ **Accept Stablecoin Payments** - USDC on Solana and Monad blockchains
✅ **Track Everything** - Sales analytics, fundraising progress, payment history
✅ **Multi-Platform** - Works via Telegram, WhatsApp, Discord, and more
✅ **Low Fees** - 0.5-1.5% per transaction (vs 2.9% for Stripe)
✅ **Instant Settlement** - Funds in your wallet within minutes

---

## Quick Setup

### 1. Register & Get API Key

```bash
# Register from any platform (no Telegram required!)
curl -X POST https://obverse.onrender.com/api-keys/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-agent-name"}'

# With your own wallet:
curl -X POST https://obverse.onrender.com/api-keys/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-agent-name", "walletAddress": "YOUR_WALLET", "chain": "solana"}'
```

Response includes your API key (`obv_sk_...`) and wallet address. **Save the key — it's shown only once!**

### 2. Set Environment Variables

```bash
export OBVERSE_API_KEY="obv_sk_your_key_here"
export OBVERSE_API_URL="https://obverse.onrender.com"  # optional, this is the default
```

### 3. Start Using

```bash
# Create a payment link
obverse-cli create-link 50 USDC solana "My first payment"
```

---

## Three Main Use Cases

### 1. 🛍️ **Product/Service Sales** (Merchant Sales)

Sell products or services to anyone with a payment link. **Automatically collects customer email and name for your mailing list!**

**Example: Selling Running Shoes**

```bash
# Create product payment link (auto-collects email & name)
obverse-cli create-product-link "Premium Running Shoes" 120 USDC solana "High-performance shoes"

# Returns:
{
  "paymentUrl": "https://www.obverse.cc/pay/shoe-xyz",
  "linkCode": "shoe-xyz",
  "type": "product_sale",
  "title": "Premium Running Shoes",
  "amount": 120,
  "token": "USDC",
  "customFields": [
    { "fieldName": "email", "fieldType": "email", "required": true },
    { "fieldName": "name", "fieldType": "text", "required": true }
  ],
  "message": "Collects customer email and name!"
}

# Generate dashboard link to view all customer data
obverse-cli generate-dashboard shoe-xyz

# Returns:
{
  "dashboardUrl": "https://www.obverse.cc/dashboard",
  "credentials": {
    "username": "@yourname",
    "password": "AbC123XyZ456"
  },
  "instructions": [
    "1. Open dashboard: https://www.obverse.cc/dashboard",
    "2. Login with your credentials",
    "3. View customer emails, names, and payment details!"
  ]
}

# Check sales analytics
obverse-cli get-analytics shoe-xyz

# List all customers with their data
obverse-cli list-contributors shoe-xyz 50
```

**Perfect For:**
- Physical products (clothing, gadgets, merch)
- Digital products (ebooks, courses, templates)
- Services (consulting, development, design)
- Event tickets, subscriptions, pre-orders

---

### 2. 💰 **Crowdfunding/Fundraising**

Raise money from multiple contributors for a shared goal.

**Example: Funding AI Development**

```bash
# Create fundraising campaign
obverse-cli create-fundraiser "AI Development Fund" 5000 USDC monad "Building advanced AI agents"

# Returns:
{
  "paymentUrl": "https://www.obverse.cc/pay/fund-xyz",
  "linkCode": "fund-xyz",
  "type": "crowdfunding",
  "goalAmount": 5000
}

# Check fundraising progress
obverse-cli check-progress fund-xyz 5000

# Returns:
{
  "fundraising": {
    "goalAmount": 5000,
    "raisedAmount": 3450,
    "remainingAmount": 1550,
    "progressPercent": "69.0",
    "contributors": 23
  }
}

# List all contributors
obverse-cli list-contributors fund-xyz
```

**Perfect For:**
- Agent development funding
- Product launches
- Community projects
- Research funding
- Open source projects
- Bounty programs

---

### 3. 💳 **Simple Payments & Invoicing**

Accept one-time payments or create invoices for clients.

**Example: Consulting Invoice**

```bash
# Generic payment link (one-time use)
obverse-cli create-link 750 USDC solana "Consulting Services - 5 hours"

# Check if paid
obverse-cli check-payment xyz123

# List all payments
obverse-cli list-payments xyz123
```

**Or use formal invoicing:**

```bash
# Create invoice with recipient details
obverse-cli create-invoice john@example.com 750 USDC monad
```

**Perfect For:**
- Freelance work
- Professional services
- One-time payments
- Tips and donations

---

## 🎯 NEW: Data Collection & Dashboard Features

### Collect Customer Data with Payment Links

**Every payment link can now collect custom data from customers!** Perfect for building mailing lists, gathering customer info, and invoicing.

```bash
# Simple example: Collect email and phone number
obverse-cli create-link 50 USDC solana "Consultation Fee" '[{"fieldName":"email","fieldType":"email","required":true},{"fieldName":"phone","fieldType":"tel","required":false}]' true

# Product sales automatically collect email & name
obverse-cli create-product-link "Digital Course" 299 USDC monad

# Fundraising automatically collects optional contributor info
obverse-cli create-fundraiser "Community Project" 10000 USDC solana
```

**Custom fields you can collect:**
- Email addresses (`fieldType: "email"`)
- Names (`fieldType: "text"`)
- Phone numbers (`fieldType: "tel"`)
- Messages (`fieldType: "textarea"`)
- Company names, addresses, or ANY text field you need!

### Dashboard Analytics

**Get a full dashboard with payment analytics and customer data!**

```bash
# Generate dashboard credentials for any payment link
obverse-cli generate-dashboard shoe-xyz

# Returns login credentials:
{
  "dashboardUrl": "https://www.obverse.cc/dashboard",
  "credentials": {
    "username": "@yourname",
    "password": "AbC123XyZ456",  // Valid for 2 hours
    "expiresAt": "2024-01-15T12:30:00.000Z"
  },
  "instructions": [
    "1. Open dashboard",
    "2. Login with credentials",
    "3. View analytics, customer emails, payment history, charts"
  ]
}
```

**What you get in the dashboard:**
- 📊 Payment statistics (total revenue, count, success rate)
- 📧 Customer data (emails, names, all collected fields)
- 📈 Charts and trends over time
- 🔍 Searchable payment history
- 💾 Export customer lists

---

## Core Commands

### Creating Payment Links

```bash
# Generic payment link with optional custom fields
obverse-cli create-link <amount> [currency] [chain] [description] [customFieldsJson] [isReusable]

# Example: Simple payment
obverse-cli create-link 50 USDC solana "Payment for services"

# Example: With data collection
obverse-cli create-link 100 USDC monad "Consultation" '[{"fieldName":"email","fieldType":"email","required":true}]' true
```

### Convenience Wrappers (Auto-collect customer data!)

```bash
# For product/service sales (auto-collects email & name)
obverse-cli create-product-link <title> <price> [currency] [chain] [description] [customFieldsJson]

# For crowdfunding (auto-collects optional email & name)
obverse-cli create-fundraiser <title> <goalAmount> [currency] [chain] [description] [customFieldsJson]

# For invoicing (formal)
obverse-cli create-invoice <recipient> <amount> [currency] [chain] [dueDate]
```

### Dashboard & Analytics

```bash
# Generate dashboard credentials
obverse-cli generate-dashboard <linkCode>

# Get analytics (sales/fundraising stats)
obverse-cli get-analytics <linkCode>

# Check payment link status
obverse-cli check-payment <linkCode>

# List all payments for a link
obverse-cli list-payments <linkCode> [limit]

# Check fundraising progress toward goal
obverse-cli check-progress <linkCode> <goalAmount>

# List all contributors/customers
obverse-cli list-contributors <linkCode> [limit]

# Check wallet balance
obverse-cli balance <userId> [chain]
```

---

## Complete Workflow Examples

### Workflow 1: Selling Digital Products (with Customer Data Collection)

```bash
# Step 1: Create product link (auto-collects email & name)
obverse-cli create-product-link "AI Course Bundle" 299 USDC solana

# Step 2: Share the link
# https://www.obverse.cc/pay/course-xyz
# Customers pay AND provide their email/name automatically!

# Step 3: Generate dashboard to view all customer data
obverse-cli generate-dashboard course-xyz
# Returns: Login credentials for full analytics dashboard

# Step 4: Check sales analytics
obverse-cli get-analytics course-xyz

# Step 5: Export customer email list for marketing
obverse-cli list-contributors course-xyz 100
# Now you have customer emails to send course access links!
```

### Workflow 2: Running a Fundraising Campaign

```bash
# Step 1: Create fundraiser
obverse-cli create-fundraiser "Open Source AI Project" 10000 USDC monad

# Step 2: Share campaign link
# https://www.obverse.cc/pay/project-xyz

# Step 3: Track progress
obverse-cli check-progress project-xyz 10000

# Step 4: Thank top contributors
obverse-cli list-contributors project-xyz
```

### Workflow 3: Freelance Consulting

```bash
# Step 1: Create payment link
obverse-cli create-link 1500 USDC solana "Smart Contract Development"

# Step 2: Send link to client
# https://www.obverse.cc/pay/work-xyz

# Step 3: Check if paid
obverse-cli check-payment work-xyz

# Step 4: Verify payment
obverse-cli list-payments work-xyz
```

---

## Agent Usage Patterns

### Via Telegram

```
User: "Create payment link to sell my AI course for $299"

Agent: ✅ Product Payment Link Created!
       Product: AI Course Bundle
       Price: $299 USDC
       Link: https://www.obverse.cc/pay/course-xyz

       Share this link to start selling!
```

```
User: "How many courses have I sold?"

Agent: 📊 Sales Analytics
       Total Sales: 47
       Revenue: $14,053 USDC
       Customers: 47
       Average: $299.00
```

### Via WhatsApp

```
User: "Start a fundraiser for $5000"

Agent: 🚀 Fundraising Campaign Created!
       Goal: $5,000 USDC
       Link: https://www.obverse.cc/pay/fund-xyz
```

```
User: "How much have we raised?"

Agent: 💰 Fundraising Progress
       Goal: $5,000 USDC
       Raised: $3,450 (69%)
       Remaining: $1,550
       Contributors: 23
```

### Via Discord

```
User: "Bill the client for $750"

Agent: 💳 Payment Link Created
       Amount: $750 USDC
       Link: https://www.obverse.cc/pay/work-xyz
```

```
User: "Did they pay?"

Agent: ✅ PAYMENT RECEIVED!
       Amount: $750 USDC
       Transaction: 0x8a9b7c...
       Time: 15 minutes ago
```

### NEW: Data Collection & Dashboard Examples

```
User: "Create a payment link for my course and collect customer emails"

Agent: ✅ Product Link Created with Data Collection!
       Product: Online Course
       Price: $299 USDC
       Link: https://www.obverse.cc/pay/course-xyz

       📧 Automatically collects:
       • Customer email
       • Customer name

       Share this link to sell and build your email list!
```

```
User: "Show me who bought my course"

Agent: 📊 Generating Dashboard Access...

       🔐 Dashboard Credentials:
       URL: https://www.obverse.cc/dashboard
       Username: @yourname
       Password: AbC123XyZ456

       ⏰ Valid for: 2 hours

       View all customer emails, names, payments, and analytics!
```

```
User: "I want to collect phone numbers too"

Agent: ✅ Custom Payment Link Created!
       Link: https://www.obverse.cc/pay/custom-xyz

       Collecting:
       • Email (required)
       • Name (required)
       • Phone (optional)

       Perfect for building your customer database!
```

---

## Default Behavior

- **Default chain**: Solana
- **Default currency**: USDC (most widely used)
- **Settlement**: Funds arrive in 2-5 minutes
- **Fees**: 0.5-1.5% per transaction

---

## Supported Chains

| Chain | Currencies | Fees |
|-------|-----------|------|
| **Solana** | USDC | low |
| Monad | USDC | low |

---

## Error Handling

### Common Errors

**"Invalid API key"**
```bash
# Check your API key
echo $OBVERSE_API_KEY
# Register for a new key:
curl -X POST https://obverse.onrender.com/api-keys/register \
  -H 'Content-Type: application/json' \
  -d '{"username": "your-agent-name"}'

**"Payment link not found"**
```bash
# Check if link code is correct
obverse-cli check-payment <linkCode>
```

**"Rate limit exceeded"**
```bash
# Wait 60 seconds and retry
```

---

## API Rate Limits

| Plan | Requests/min | Monthly Txns |
|------|--------------|--------------|
| Free | 10 | 100 |
| Starter | 60 | 500 |
| Pro | 300 | 2,000 |

---

## Getting Help

- **API Docs**: [obverse.onrender.com/api-docs](https://obverse.onrender.com/api-docs)
- **Support**: obverse.ccc@gmail.com

---

## Key Takeaway

**One generic payment link. Multiple use cases.**

Whether you're selling products, raising funds, or invoicing clients - it's all the same flexible payment link system. The convenience commands just make it easier to use.

No complex setup. No multiple endpoints. Just simple, flexible payments. 💙

---

**Made with ❤️ by the Obverse Team**
