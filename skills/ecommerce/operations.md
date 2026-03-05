# Operations — Stock, Orders, Shipping, Returns

## Inventory Management

### Stock Alerts
Don't alert at zero — alert at reorder point:

```
Reorder Point = (Daily Sales × Lead Time) + Safety Stock
```

**Example:**
- Sell 5 units/day
- Supplier takes 7 days to deliver
- Safety stock: 10 units (2 days buffer)
- Reorder point: (5 × 7) + 10 = 45 units

### Multi-channel Sync
**Problem:** Sell on Amazon + own store, stock out of sync, overselling.

**Solution hierarchy:**
1. **Single source of truth** — One system holds real stock
2. **Sync frequency** — Real-time for <100 SKUs, every 5-15 min for larger
3. **Reserve buffer** — Keep 10-20% reserve to absorb sync delays
4. **Oversell handling** — Automatic notification + refund workflow

### Stock Audit
Monthly check:
- [ ] Physical count vs system count
- [ ] Identify shrinkage (theft, damage, miscounts)
- [ ] Dead stock (no sales in 90+ days)
- [ ] Slow movers (bottom 20% by velocity)

## Order Management

### Order Statuses
Minimum states for visibility:
1. **Pending Payment** — Awaiting confirmation
2. **Processing** — Payment confirmed, preparing
3. **Shipped** — Handed to carrier, tracking available
4. **Delivered** — Carrier confirms delivery
5. **Completed** — Past return window

### Problem Detection
Alert on:
- Orders in "Processing" >24h (business hours)
- Orders in "Pending Payment" >1h (payment timeout)
- Shipping not scanned >48h after ship date
- Multiple failed delivery attempts

### Fraud Signals
Review manually when:
- Shipping ≠ billing address + high value
- Multiple orders same IP, different cards
- Express shipping + first-time buyer + high value
- Email domain doesn't match name pattern
- Shipping to freight forwarder

## Shipping

### Carrier Selection Logic
```
If weight < 1kg AND value < €50:
  Use economy carrier (Correos, GLS)
Else if value > €200:
  Use tracked + insured (SEUR, UPS)
Else if express requested:
  Use fastest available with tracking
Else:
  Use best rate with tracking
```

### Tracking Notifications
**Minimum touchpoints:**
1. Order confirmed (immediate)
2. Shipped (with tracking link)
3. Out for delivery (same day)
4. Delivered (request review)

### Shipping Cost Display
**Pre-checkout:** Show estimate based on cart weight/value
**Checkout:** Calculate exact based on address

**Free shipping threshold formula:**
```
Threshold = Current AOV × 1.25
```
If AOV is €40, free shipping at €50 pushes basket size up.

## Returns & Refunds

### Spain/EU Legal Requirements
- 14 days withdrawal right (no reason needed)
- Starts from delivery date
- Customer pays return shipping (unless you offered free)
- Refund within 14 days of receiving return
- Exceptions: custom items, sealed hygiene products opened

### Return Flow
```
1. Customer requests return (form/email)
2. Generate return label (or instructions)
3. Receive package
4. Inspect within 48h
5. Refund or partial refund (with justification)
6. Update inventory
```

### Handling Abuse
Track return rate per customer:
- <5% → Normal
- 5-15% → Monitor
- >15% → Review history, consider restrictions

**Never:**
- Block returns for legitimate requests
- Delay refunds past 14 days
- Require receipt when you have order history

### Partial Refund Scenarios
| Situation | Action |
|-----------|--------|
| Product damaged by customer | Refund minus repair/depreciation |
| Product used beyond "testing" | Refund minus value reduction |
| Missing parts | Refund minus parts cost |
| Product not returned after 30 days | No refund, email reminder |

## Customer Service

### Response Time Targets
| Channel | First Response | Resolution |
|---------|---------------|------------|
| Email | <4h (business hours) | <24h |
| Chat | <2 min | <15 min |
| Phone | <30 sec answer | <5 min |
| Social | <1h | <4h |

### Escalation Rules
Escalate to human when:
- Order value >€200
- Customer mentions "lawyer", "complaint", "chargeback"
- Third contact about same issue
- Refund request after return window
- Suspected fraud (either direction)

### Compensation Guidelines
| Issue | Compensation |
|-------|-------------|
| Late delivery (1-2 days) | Apology + 5% discount next order |
| Late delivery (3+ days) | Apology + shipping refund |
| Wrong item sent | Free return + correct item + 10% discount |
| Damaged in transit | Full refund or replacement + 10% discount |
| Out of stock after order | Full refund + 15% discount |

**Rule:** Cost of keeping customer < cost of acquiring new one.
