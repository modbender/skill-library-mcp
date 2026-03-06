---
name: whop-cli
version: 1.0.0
description: "Manage Whop digital products store — create products, plans, track payments, manage memberships. Use when: selling digital products, managing Whop store. Don't use when: non-Whop payment platforms."
metadata:
  openclaw:
    emoji: "🏪"
    requires:
      bins: []
      env: ["WHOP_API_KEY", "WHOP_COMPANY_ID"]
    install:
      - id: npm-sdk
        kind: command
        command: "npm install -g @whop/sdk"
        label: "Install Whop SDK"
---

# Whop Store Management

Manage your Whop digital products store via API.

## Setup

1. Get API key from Whop dashboard → Settings → Developer
2. Set environment variables:
   ```bash
   export WHOP_API_KEY="apik_..."
   export WHOP_COMPANY_ID="biz_..."
   ```

## Usage

```javascript
import { default as Whop } from '@whop/sdk';
const client = new Whop();
const CID = process.env.WHOP_COMPANY_ID;

// List products
const products = await client.products.list({ company_id: CID });

// Create product
const product = await client.products.create({
  company_id: CID,
  title: 'My Product'
});

// Create pricing plan
const plan = await client.plans.create({
  product_id: product.id,
  company_id: CID,
  plan_type: 'one_time', // or 'renewal'
  initial_price: 29,
  base_currency: 'usd'
});
// plan.purchase_url = checkout link

// Check payments
const payments = await client.payments.list({ company_id: CID });

// Check memberships
const members = await client.memberships.list({ company_id: CID });
```

## Available Resources

products, plans, payments, memberships, experiences, files, webhooks,
promoCodes, courses, forums, chatChannels, checkoutConfigurations,
reviews, leads, notifications

## Built by Versatly

Store: https://whop.com/versatly-holdings/
Products: https://store.versatlygroup.com
