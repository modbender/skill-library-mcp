# Payment Providers Comparison

## Full-Service Processors

### Stripe
- **Best for:** Developers, US/global B2C, marketplaces
- **Fees:** 2.9% + $0.30 (US), varies by country
- **Pros:** Best docs, widest payment method support, Stripe Connect for marketplaces
- **Cons:** You handle tax compliance, higher fees for international
- **Merchant of Record:** No (you're the seller)

### Paddle
- **Best for:** SaaS selling globally, avoiding tax complexity
- **Fees:** 5% + $0.50 per transaction
- **Pros:** Handles VAT/GST, chargebacks, invoicing. You're not the merchant.
- **Cons:** Higher fees, less control, slower payouts
- **Merchant of Record:** Yes (they're the seller, you're the vendor)

### LemonSqueezy
- **Best for:** Indie hackers, digital products, simple setup
- **Fees:** 5% + $0.50
- **Pros:** Beautiful checkout, handles taxes, simple dashboard
- **Cons:** Fewer features than Stripe, limited customization
- **Merchant of Record:** Yes

### PayPal
- **Best for:** User trust, older demographics, some regions
- **Fees:** 2.9% + $0.30 (varies)
- **Pros:** Brand recognition, buyer protection, easy disputes
- **Cons:** Account freezes, poor developer experience, dated UX
- **Merchant of Record:** Depends on integration type

---

## Decision Framework

**You should use Stripe if:**
- You want maximum control and customization
- Your team can handle tax compliance (or use Stripe Tax)
- You need Stripe Connect for marketplace splits
- Developer experience matters

**You should use Paddle/LemonSqueezy if:**
- Selling to EU and don't want VAT headaches
- Small team, no finance/legal resources
- Digital products (software, ebooks, courses)
- Want someone else to handle chargebacks

**You should offer PayPal alongside primary processor if:**
- Selling to demographics that trust PayPal
- High cart abandonment without PayPal option
- Markets where PayPal dominates (Germany, some LATAM)

---

## Fee Comparison (Example: $100 charge)

| Provider | Fee | You Keep |
|----------|-----|----------|
| Stripe | $3.20 | $96.80 |
| Paddle | $5.50 | $94.50 |
| LemonSqueezy | $5.50 | $94.50 |
| PayPal | $3.20 | $96.80 |

*Merchant of Record providers are more expensive but include tax handling, invoicing, and chargeback protection.*

---

## Local Payment Methods

Not everyone uses cards. Consider:
- **EU:** SEPA, iDEAL (Netherlands), Bancontact (Belgium), Sofort (Germany)
- **Brazil:** Boleto, Pix
- **Asia:** Alipay, WeChat Pay, GrabPay
- **Crypto:** Coinbase Commerce, BitPay (niche, but growing)

Stripe supports most of these. Research your target market.

---

## High-Risk Industries

Standard processors reject:
- Adult content
- CBD/cannabis
- Gambling
- Firearms
- Nutraceuticals

Specialized processors: CCBill, Epoch, Segpay, Durango Merchant Services.

Expect 5-10% fees, rolling reserves, and slower approvals.
