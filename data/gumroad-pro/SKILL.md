---
name: gumroad-pro
description: "Comprehensive Gumroad merchant management for Products, Sales, Licenses, Discounts, Payouts, and Webhooks. Use when Claude needs to: (1) Manage digital or physical inventory, (2) Oversee transactions and process refunds/shipping, (3) Verify or rotate license keys, (4) Manage offer codes, or (5) Monitor payout history and store webhooks."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node"], "env": ["GUMROAD_ACCESS_TOKEN", "API_KEY"], "config": [] },
        "primaryEnv": "GUMROAD_ACCESS_TOKEN"
      }
  }
---

# Gumroad Pro

## 🛑 AI PROTOCOL
1. **PRIORITIZE HANDLER**: Always attempt to use the interactive button-based GUI (handled by `handler.js`) for the best merchant experience.
2. **CLI AS FALLBACK**: Only use `scripts/gumroad-pro.js` via the CLI for complex data retrieval or specific actions not available in the GUI.
3. **USE --json**: When using the CLI, **ALWAYS** use the `--json` flag and check for `"success": true`.
4. **REDUCE SPAM**: Use `action: 'edit'` in `renderResponse` for all menu transitions and state updates. Only use `action: 'send'` for the initial menu or when the context fundamentally changes.
5. **HANDLE ERRORS**: Read the `"error"` field in JSON responses to inform the user of failures.

## ❓ Navigation & Data
- **Primary Interaction**: Use the adaptive logic in `handler.js`. See [handler-guide.md]({baseDir}/references/handler-guide.md) for interaction patterns, [ui-rendering.md]({baseDir}/references/ui-rendering.md) for rendering protocols, and [changelog.md]({baseDir}/references/changelog.md) for version history. Respond with button callback data (e.g., `gp:products`) or digits (1, 2, 3) where applicable.
- **Secondary Interaction**: Use `scripts/gumroad-pro.js` for direct actions. See [api-reference.md]({baseDir}/references/api-reference.md) for command specs.

## 🔑 Authentication
The skill requires a **Gumroad API Key**. It looks for the following environment variables (in order of preference):
1. `GUMROAD_ACCESS_TOKEN`
2. `API_KEY`

### Configuration
You can set this in your `~/.openclaw/openclaw.json` using the `apiKey` convenience field:
```json
{
  "skills": {
    "entries": {
      "gumroad-pro": {
        "enabled": true,
        "apiKey": "YOUR_GUMROAD_TOKEN"
      }
    }
  }
}
```
The platform will automatically inject your `apiKey` into the preferred `GUMROAD_ACCESS_TOKEN` variable.

## 🛠️ Workflows

### Product Inventory
- List all digital assets to monitor sales and availability.
- Toggle publication status or delete obsolete items.
- View [detailed product commands]({baseDir}/references/api-reference.md#1-products).

### Sales & Fulfillment
- Search transactions by email.
- Process refunds or mark physical goods as shipped.
- View [detailed sales commands]({baseDir}/references/api-reference.md#2-sales).

### Licensing
- Verify keys for software distribution.
- Manage usage counts or rotate keys for security.
- View [detailed license commands]({baseDir}/references/api-reference.md#3-licenses).

### Offer Management
- Create, list, or remove discount codes for marketing campaigns.
- View [detailed discount commands]({baseDir}/references/api-reference.md#4-discounts-offer-codes).

---
Developed for the OpenClaw community by [Abdul Karim Mia](https://github.com/abdul-karim-mia).
