# Code Traps — Ecommerce Production Failures

## 1. Payment Idempotency

**Problem:** Webhook arrives twice (retry), order processes twice, customer charged twice.

**Wrong:**
```javascript
app.post('/webhook', async (req, res) => {
  const order = await createOrder(req.body);
  await chargePayment(order);
  res.sendStatus(200);
});
```

**Correct:**
```javascript
app.post('/webhook', async (req, res) => {
  const paymentIntentId = req.body.data.object.id;
  
  // Check if already processed
  const existing = await db.orders.findOne({ paymentIntentId });
  if (existing) return res.sendStatus(200);
  
  // Process with unique constraint as backup
  await db.orders.create({ paymentIntentId, ...orderData });
  res.sendStatus(200);
});
```

## 2. Inventory Race Conditions

**Problem:** Two users buy last item simultaneously, both succeed, stock goes negative.

**Wrong:**
```javascript
const product = await db.products.findById(id);
if (product.stock > 0) {
  await db.products.update(id, { stock: product.stock - 1 });
}
```

**Correct:**
```sql
UPDATE products 
SET stock = stock - 1 
WHERE id = $1 AND stock > 0
RETURNING stock;
-- Check rowsAffected/returning to confirm success
```

## 3. Frontend Price Trust

**Problem:** User modifies JavaScript, sends total: €0.01, backend trusts it.

**Rule:** Backend calculates everything from scratch:
- Fetch product prices from DB (not request)
- Apply discounts from DB rules (not request)
- Calculate shipping from weight/destination (not request)
- Sum taxes from jurisdiction rules (not request)
- Compare final total — reject if client total differs

## 4. Webhook Signature Verification

**Problem:** Anyone can POST to `/webhook`, mark orders as paid.

**Wrong:**
```javascript
app.post('/webhook', (req, res) => {
  if (req.body.type === 'payment_intent.succeeded') {
    markOrderPaid(req.body.data.object.id);
  }
});
```

**Correct:**
```javascript
app.post('/webhook', (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  // Now safe to process event
});
```

## 5. Stock Validation Timing

**Problem:** User adds to cart, waits 2 hours, pays — product sold out meanwhile.

**Correct flow:**
1. Add to cart — soft reserve (optional) or just allow
2. Begin checkout — verify stock, show warning if low
3. Create payment intent — **atomic stock decrement with transaction**
4. Payment fails — rollback stock
5. Payment succeeds — stock already decremented

## 6. Email Queue Failures

**Problem:** Email service down → checkout fails or email lost silently.

**Wrong:**
```javascript
const order = await createOrder(data);
await sendConfirmationEmail(order); // If this fails, what happens?
return order;
```

**Correct:**
```javascript
const order = await createOrder(data);
await emailQueue.add('order-confirmation', { orderId: order.id });
// Queue handles retries with exponential backoff
return order;
```

## 7. SEO Gaps

**Checklist for every product page:**
- [ ] Canonical URL (prevent duplicate content from filters/params)
- [ ] Schema.org Product markup (price, availability, reviews)
- [ ] Unique meta description with product name + key features
- [ ] Product in XML sitemap with lastmod date
- [ ] Image alt text with product name

**Structured data minimum:**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "image": "https://...",
  "offers": {
    "@type": "Offer",
    "price": "29.99",
    "priceCurrency": "EUR",
    "availability": "https://schema.org/InStock"
  }
}
```
