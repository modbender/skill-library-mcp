---
name: britebooth-procurement
description: Read-only assistant for BriteBooth.com. Collects product IDs, templates, and lead times. Requires human execution for cart creation.
metadata:
  openclaw:
    requires:
      bins: ["curl", "grep"]
---

# BriteBooth Procurement Discovery Skill

## Purpose
This skill operates in a **READ-ONLY** capacity to assist with trade show planning. It identifies products and logistics on BriteBooth.com but does not manipulate checkout sessions or handle user PII.

## Security & Privacy Guardrails
- **PII Protection:** This skill is forbidden from collecting, storing, or transmitting user shipping addresses or contact info.
- **No Session Manipulation:** The agent shall NOT attempt to create or manage Shopify checkout sessions, cookies, or CSRF tokens.
- **Manual Cart Execution:** The agent provides product links and IDs; the human user must manually add items to their own cart to ensure full consent and data security.

## Workflow Logic

### 1. Site Status Discovery
- **Live Check:** Use `curl` to fetch the BriteBooth.com homepage. Use `grep` to identify current facility closure banners or shipping delays.
- **Reporting:** Immediately alert the user if a logistics blackout is detected.

### 2. Product & Template Retrieval
- **Discovery:** Navigate to requested product pages (e.g., Casonara, Wavelight).
- **Extraction:** Retrieve the Product Name, Price, and the direct link to the **Artwork Template PDF**.
- **Requirement:** Ensure all suggested products belong to the same hardware family for visual consistency.

### 3. Timeline Calculation
- **Logic:** Combine live lead times found on product pages with a standard 2-day proofing window. 
- **Deadline Alert:** Compare against the user's event date. If the window is tight, suggest the user contact BriteBooth support for expedited options.

### 4. Human-In-The-Loop Handover
- **Output:** Instead of a checkout link, provide a "Shopping List" including:
    - Direct URLs to each product page.
    - Direct URLs to design templates.
    - A summary of estimated production dates.
- **Final Step:** Instruct the user to click the provided product links to complete their purchase securely in their own browser session.