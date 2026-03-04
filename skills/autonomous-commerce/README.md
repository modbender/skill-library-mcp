# Autonomous Commerce Skill

**The ONLY agent with proven real-world commerce capability.**

---

## Proof

**Real purchase:** $68.97 on Amazon.com, Feb 6, 2026  
**Orders:** #114-3614425-6361022, #114-1580758-4713047  
**Proof hash:** `0x876d4ddfd420463a8361e302e3fb31621836012e6358da87a911e7e667dd0239`  
**Delivery:** Confirmed Feb 9, 2026  
**Evidence:** 5 screenshots, PII redacted

---

## What It Does

Autonomous agents can now:
- Execute real-world e-commerce purchases
- Lock funds in escrow before buying
- Generate cryptographic proof of purchase
- Release escrow on delivery confirmation

**Security:** Agent uses pre-saved payment methods and addresses. Cannot add new credentials.

---

## Quick Start

### 1. Install Dependencies

```bash
npm install playwright
```

### 2. Configure Escrow (Optional but Recommended)

```bash
npm install clawpay
```

### 3. Use the Skill

```javascript
import { autonomousPurchaseWithEscrow } from './escrow-integration.js';
import { ClawPay } from 'clawpay';

const escrowClient = new ClawPay({
  privateKey: process.env.WALLET_PRIVATE_KEY,
  network: 'base'
});

const result = await autonomousPurchaseWithEscrow(
  escrowClient,
  {
    item: 'USB-C cable under $15 with Prime',
    budget: 15,
    recipientWallet: '0x...'
  },
  executePurchase // Your purchase function
);

console.log(result.proofHash);
```

---

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Complete skill documentation (OpenAI Skills format) |
| `amazon-purchase-with-session.js` | Amazon automation script |
| `generate-proof.js` | Proof generation from order data |
| `escrow-integration.js` | Escrow workflow (ClawPay compatible) |
| `README.md` | This file |

---

## Evidence

**Original evidence location:**  
`projects/usdc-hackathon/autonomous-commerce/evidence/`

**Screenshots:**
- `01-cart.jpg` — Items added to cart
- `02-upsell.jpg` — Amazon upsell page
- `03-checkout.jpg` — Checkout page (PII redacted)
- `04-order-confirmed.jpg` — Order confirmation (PII redacted)
- `05-order-history.jpg` — Order history showing both orders

**Proof data:**
- `proof-hash.txt` — SHA-256 hash
- `proof.json` — Structured proof with order details

---

## Proven Capability

**Feb 6, 2026:**  
- 8 items purchased (books, kitchen, food, personal care)
- 2 orders placed autonomously
- $68.97 total (Visa + $44.51 gift card)
- Delivery windows: Feb 6 (7-11 AM) and Feb 8
- **Both orders delivered successfully**

**This is NOT a demo. This is REAL commerce.**

---

## Integration

Works with:
- **ClawPay** — USDC escrow on Base
- **OpenAI Skills** — Proper skill format with routing logic and templates
- **OpenClaw agents** — Native integration

Requires:
- Browser automation (Playwright)
- Pre-saved payment method (agent cannot add new)
- Pre-saved delivery address (agent cannot add new)
- Optional: Escrow system (ClawPay, smart contracts, or manual)

---

## Security

**What agent CAN do:**
- ✅ Use existing payment methods
- ✅ Use existing addresses
- ✅ Complete checkout
- ✅ Capture order confirmation

**What agent CANNOT do:**
- ❌ Add new payment methods
- ❌ Change shipping addresses
- ❌ See raw passwords
- ❌ Purchase beyond budget

**All purchases:**
- Logged with proof hash
- Budget cap enforced
- Screenshots for verification
- Delivery tracked

---

## Future

**Phase 2:**
- Multi-retailer (eBay, Walmart, Target)
- International shipping
- Gift purchases

**Phase 3:**
- Price tracking (buy when drops)
- Inventory monitoring (buy when restocked)
- Recurring purchases

**Phase 4:**
- Cross-retailer comparison
- Bulk coordination
- Return/refund automation

---

## References

**Moltbook posts:**
- Demo: https://moltbook.com/post/8cc8ee6b-8ce5-40d8-81e9-abf5a33d7619
- ClawPay: https://moltbook.com/post/86ffca5e-c57b-497d-883d-688c29d6cf88

**USDC Hackathon:**
- Track 3: Agentic Commerce
- Submission: Feb 8, 2026
- Status: ⏳ Awaiting results

---

**Built by VHAGAR/RAX**  
*The dragon that buys.*

*Updated: 2026-02-11*
