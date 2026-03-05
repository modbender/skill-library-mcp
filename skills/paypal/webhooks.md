# Webhook Events — PayPal Integration

## Essential Events to Subscribe

| Event | When | Action |
|-------|------|--------|
| `PAYMENT.CAPTURE.COMPLETED` | Payment captured successfully | Fulfill order |
| `PAYMENT.CAPTURE.DENIED` | Capture failed | Cancel order, notify user |
| `PAYMENT.CAPTURE.REFUNDED` | Refund processed | Update order status |
| `CHECKOUT.ORDER.APPROVED` | User approved in PayPal | Capture the payment |
| `BILLING.SUBSCRIPTION.ACTIVATED` | Subscription started | Enable premium access |
| `BILLING.SUBSCRIPTION.CANCELLED` | User cancelled | Disable at period end |
| `BILLING.SUBSCRIPTION.SUSPENDED` | Payment failed | Notify user, retry |
| `CUSTOMER.DISPUTE.CREATED` | Dispute opened | Alert team immediately |
| `CUSTOMER.DISPUTE.RESOLVED` | Dispute closed | Update records |

## Webhook Handler Structure

```javascript
app.post('/webhooks/paypal', async (req, res) => {
  const headers = req.headers;
  const body = req.body;
  
  // 1. Verify signature (MANDATORY)
  const verified = await verifyWebhook(headers, body);
  if (!verified) {
    return res.status(401).send('Invalid signature');
  }
  
  // 2. Check idempotency
  const exists = await db.webhooks.findOne({ eventId: body.id });
  if (exists) {
    return res.status(200).send('Already processed');
  }
  
  // 3. Process by event type
  switch (body.event_type) {
    case 'PAYMENT.CAPTURE.COMPLETED':
      await handleCaptureCompleted(body.resource);
      break;
    case 'CUSTOMER.DISPUTE.CREATED':
      await handleDisputeCreated(body.resource);
      break;
    // ... other events
  }
  
  // 4. Record processing
  await db.webhooks.insert({ eventId: body.id, processedAt: new Date() });
  
  res.status(200).send('OK');
});
```

## Dispute Handling

Disputes have strict deadlines:

| Stage | Deadline | Action Required |
|-------|----------|-----------------|
| INQUIRY | 20 days | Respond or escalates to CLAIM |
| CLAIM | 10 days | Provide evidence or lose |
| APPEAL | 10 days | Final chance if lost |

```javascript
const handleDisputeCreated = async (dispute) => {
  const deadline = new Date(dispute.create_time);
  deadline.setDate(deadline.getDate() + 10);
  
  await notifyTeam({
    type: 'DISPUTE',
    priority: 'HIGH',
    disputeId: dispute.dispute_id,
    amount: dispute.dispute_amount.value,
    reason: dispute.reason,
    deadline: deadline
  });
  
  // Gather evidence automatically
  const order = await db.orders.findOne({ 
    paypalOrderId: dispute.disputed_transactions[0].reference_id 
  });
  
  if (order.trackingNumber) {
    // You can submit evidence via API
    // POST /v1/customer/disputes/{dispute_id}/provide-evidence
  }
};
```

## Testing Webhooks (Sandbox)

PayPal provides webhook simulator in sandbox:
1. Go to Developer Dashboard → Webhooks
2. Click "Simulate Event"
3. Select event type
4. Your endpoint receives test payload

Or use ngrok for local development:
```bash
ngrok http 3000
# Configure webhook URL: https://abc123.ngrok.io/webhooks/paypal
```
