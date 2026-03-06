---
name: trendyol-admin
description: Comprehensive management of Trendyol marketplace via API v2.0. Includes product lifecycle (create, update, delete, archive), stock/price management, order processing (status updates, shipping), returns, and customer questions. Use this skill as a knowledge base to construct correct API requests.
---

# Trendyol Admin (AI Knowledge Base)

This skill provides a comprehensive reference for the Trendyol Marketplace API v2.0. It contains all necessary endpoints, authorization requirements, and payload schemas to manage a Trendyol store.

## 🛠 Usage for AI Agents

1. **Authentication**: Always use Basic Auth.
   - Username: `API_KEY`
   - Password: `API_SECRET`
   - Generate Header (One-liner): `echo -n "YOUR_API_KEY:YOUR_API_SECRET" | base64`
2. **Mandatory Headers**: Every request MUST include:
   - `Authorization: Basic <base64>`
   - `User-Agent: <SupplierId> - SelfIntegration`
   - `storeFrontCode`: **This is the mandatory parameter to switch national markets.**
     - `AE`: United Arab Emirates (AED)
     - `SA`: Saudi Arabia (SAR)
     - `QA`: Qatar (QAR)
     - `KW`: Kuwait (KWD)
     - `BH`: Bahrain (BHD)
     - `OM`: Oman (OMR)
     - `DE`: Germany (EUR)
     - `AZ`: Azerbaijan (AZN)
     - `RO`: Romania (RON)
     - `CZ`: Czech Republic (CZK)
     - `HU`: Hungary (HUF)
     - `SK`: Slovakia (EUR)
     - `BG`: Bulgaria (BGN)
     - `GR`: Greece (EUR)
3. **Endpoints**: Refer to [references/api_reference.md](references/api_reference.md) to find the correct URL for the task (Product, Inventory, Order, etc.).
4. **Execution**: Since there are no pre-built scripts, use `curl` or inline Node.js/Python code to execute requests as defined in the reference.

## 📖 Key Sections in Reference

- **Authorization**: Header construction and error codes.
- **Product Integration**: Full lifecycle management of items.
- **Order Integration**: From creation to delivery status updates.
- **Webhooks**: Real-time notification models.
- **API Reference File**: [references/api_reference.md](references/api_reference.md)

## ⚠️ Important Rules

- **Base URL (Prod)**: `https://apigw.trendyol.com/integration/`
- **Rate Limit**: 50 requests per 10 seconds.
- **Image Requirements**: 1200x1800 px, HTTPS URLs.
- **JSON Only**: All payloads must be valid JSON.
