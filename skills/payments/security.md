# Payment Security

## PCI Compliance Basics

**PCI DSS** = Payment Card Industry Data Security Standard. Required if you handle card data.

### Compliance Levels

| Level | Criteria | Requirements |
|-------|----------|--------------|
| SAQ-A | Hosted checkout, no card data touches your server | Self-assessment questionnaire |
| SAQ-A-EP | Embedded elements, card data in your page (tokenized) | Longer questionnaire |
| SAQ-D | Full card processing on your server | Full audit, very expensive |

**Stay at SAQ-A if possible.** Use hosted checkout or provider elements.

### What You Must Never Do

❌ Store CVV/CVC (ever, anywhere, for any reason)
❌ Log full card numbers
❌ Store unencrypted card data
❌ Transmit card data without TLS
❌ Give developers access to production card data

### What You Should Do

✅ Use provider's hosted fields or checkout
✅ Tokenize immediately (card → token → charge token)
✅ Serve payment pages over HTTPS only
✅ Monitor for suspicious patterns
✅ Keep payment logic isolated from main codebase

---

## Fraud Prevention

### Red Flags

| Signal | Risk Level |
|--------|------------|
| Mismatched billing/shipping address | Medium |
| Free email with high-value order | Medium |
| Multiple failed attempts, then success | High |
| VPN/proxy from high-risk country | High |
| Velocity (many orders in short time) | High |
| Address verification failed (AVS) | Medium |
| CVC mismatch | High |

### Tools

- **Stripe Radar:** Built-in ML fraud detection
- **Sift:** Third-party fraud platform
- **Manual review:** Flag high-value or suspicious orders

### 3D Secure (3DS)

Extra authentication step ("Verified by Visa", "Mastercard SecureCode").

**Pros:**
- Liability shift to bank (you win chargebacks)
- Reduces fraud significantly

**Cons:**
- Adds friction (conversion drop 5-15%)
- Not all cards support it

**Recommendation:** Enable for high-risk transactions, new customers, high-value orders.

---

## Chargebacks

Customer disputes charge with their bank. You lose money + $15-25 fee.

### Chargeback Reasons

| Reason | What Happened |
|--------|---------------|
| Fraudulent | Stolen card used |
| Product not received | Delivery failed or claimed failed |
| Product not as described | Expectation mismatch |
| Duplicate | Charged twice |
| Subscription not canceled | User claims they canceled |

### Prevention

- Clear billing descriptor (customer recognizes charge)
- Delivery confirmation with signature
- Clear refund policy
- Easy cancellation process
- Proactive customer service

### Fighting Chargebacks

You can submit evidence to dispute:
- Proof of delivery
- Customer communication
- Terms of service acceptance
- Usage logs (for digital products)
- 3DS authentication proof

Win rates vary: ~30% for physical goods, ~50% for digital with good evidence.

---

## Refund Best Practices

**When to refund (no questions):**
- Within your stated refund window
- Duplicate charge
- Product genuinely not delivered

**When to partial refund:**
- Service partially rendered
- Usage occurred but customer unhappy

**When to deny:**
- Outside refund window with clear policy
- Obvious abuse pattern
- Fraud attempt

**Process:**
1. Refund via provider dashboard/API (not by creating negative charge)
2. Transaction fees usually not refunded to you
3. Document reason for records

---

## Data Protection

### What to Store

✅ Customer ID (provider's, not yours)
✅ Subscription status
✅ Payment method type (last 4 digits okay for display)
✅ Invoice/receipt links

### What Never to Store

❌ Full card numbers
❌ CVV/CVC
❌ Expiration dates (if not tokenized)
❌ PIN numbers
❌ Sensitive authentication data

### Encryption

- TLS 1.2+ for all payment pages
- Encrypt payment tokens at rest
- Separate database for payment data (if applicable)
- Audit access logs regularly

---

## Incident Response

If you suspect a breach:

1. **Contain:** Disable affected systems immediately
2. **Assess:** What data was exposed? Card data? Tokens only?
3. **Notify:** Provider (they may help), legal counsel
4. **Report:** PCI council if card data exposed, potentially customers
5. **Remediate:** Fix vulnerability, rotate keys
6. **Document:** Timeline, actions taken, improvements

**Card data breach = mandatory reporting and potential fines.** Another reason to never touch raw card data.
