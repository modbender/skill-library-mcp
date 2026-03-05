# Webhooks — Stripe API

## Webhook Fundamentals

Webhooks are essential for:
- Async payment confirmation (3D Secure, bank transfers)
- Subscription lifecycle events
- Dispute notifications
- Payout confirmations

**Never rely solely on API responses.** Always confirm with webhooks.

## Create Webhook Endpoint

### Via API
```bash
curl https://api.stripe.com/v1/webhook_endpoints \
  -u "$STRIPE_SECRET_KEY:" \
  -d "url=https://example.com/webhooks/stripe" \
  -d "enabled_events[]=payment_intent.succeeded" \
  -d "enabled_events[]=payment_intent.payment_failed" \
  -d "enabled_events[]=customer.subscription.created" \
  -d "enabled_events[]=customer.subscription.updated" \
  -d "enabled_events[]=customer.subscription.deleted" \
  -d "enabled_events[]=invoice.paid" \
  -d "enabled_events[]=invoice.payment_failed"
```

### Via Dashboard
1. Go to Developers > Webhooks
2. Add endpoint
3. Select events
4. Copy signing secret

## Essential Events

### Payments
| Event | When | Critical |
|-------|------|----------|
| `payment_intent.succeeded` | Payment completed | Yes |
| `payment_intent.payment_failed` | Payment failed | Yes |
| `payment_intent.requires_action` | 3DS needed | Yes |
| `charge.refunded` | Refund processed | Yes |
| `charge.dispute.created` | Chargeback filed | Yes |

### Subscriptions
| Event | When | Critical |
|-------|------|----------|
| `customer.subscription.created` | New subscription | Yes |
| `customer.subscription.updated` | Plan changed | Yes |
| `customer.subscription.deleted` | Canceled | Yes |
| `customer.subscription.trial_will_end` | 3 days before trial ends | Important |
| `customer.subscription.paused` | Paused | Important |

### Invoices
| Event | When | Critical |
|-------|------|----------|
| `invoice.paid` | Payment succeeded | Yes |
| `invoice.payment_failed` | Payment failed | Yes |
| `invoice.upcoming` | Invoice will be created | Informational |
| `invoice.finalized` | Invoice ready to pay | Informational |

### Checkout
| Event | When | Critical |
|-------|------|----------|
| `checkout.session.completed` | Payment successful | Yes |
| `checkout.session.expired` | Session expired | Important |
| `checkout.session.async_payment_succeeded` | Async payment done | Yes |
| `checkout.session.async_payment_failed` | Async payment failed | Yes |

## Signature Verification

### Python
```python
import stripe
import os

stripe.api_key = os.environ['STRIPE_SECRET_KEY']
endpoint_secret = os.environ['STRIPE_WEBHOOK_SECRET']

def handle_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return 400, 'Invalid payload'
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 400, 'Invalid signature'
    
    # Handle event
    return 200, 'OK'
```

### Node.js
```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

app.post('/webhooks/stripe', express.raw({type: 'application/json'}), (req, res) => {
  const sig = req.headers['stripe-signature'];
  
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  // Handle event
  res.json({received: true});
});
```

### Go
```go
import (
    "github.com/stripe/stripe-go/v76/webhook"
)

func handleWebhook(w http.ResponseWriter, req *http.Request) {
    payload, _ := io.ReadAll(req.Body)
    sigHeader := req.Header.Get("Stripe-Signature")
    
    event, err := webhook.ConstructEvent(payload, sigHeader, endpointSecret)
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        return
    }
    
    // Handle event
    w.WriteHeader(http.StatusOK)
}
```

## Event Handling Pattern

```python
def handle_event(event):
    event_type = event['type']
    data = event['data']['object']
    
    handlers = {
        'payment_intent.succeeded': handle_payment_success,
        'payment_intent.payment_failed': handle_payment_failure,
        'customer.subscription.created': handle_subscription_created,
        'customer.subscription.updated': handle_subscription_updated,
        'customer.subscription.deleted': handle_subscription_deleted,
        'invoice.paid': handle_invoice_paid,
        'invoice.payment_failed': handle_invoice_failed,
        'charge.dispute.created': handle_dispute,
    }
    
    handler = handlers.get(event_type)
    if handler:
        handler(data)
    else:
        print(f'Unhandled event type: {event_type}')
```

## Idempotency

Webhooks may be sent multiple times. Always handle idempotently:

```python
def handle_payment_success(payment_intent):
    payment_id = payment_intent['id']
    
    # Check if already processed
    if Order.query.filter_by(stripe_payment_id=payment_id).first():
        return  # Already handled
    
    # Process payment
    order = Order(
        stripe_payment_id=payment_id,
        amount=payment_intent['amount'],
        customer_id=payment_intent['customer']
    )
    db.session.add(order)
    db.session.commit()
```

## Webhook Best Practices

### 1. Return 200 Quickly
```python
def webhook_endpoint(request):
    event = verify_signature(request)
    
    # Queue for async processing
    queue.enqueue(process_event, event)
    
    # Return immediately
    return 200
```

### 2. Handle Retries
Stripe retries for up to 3 days with exponential backoff:
- 1 hour, 2 hours, 4 hours, 8 hours...

### 3. Log Everything
```python
def process_event(event):
    logger.info(f"Processing {event['type']}: {event['id']}")
    try:
        handle_event(event)
        logger.info(f"Success: {event['id']}")
    except Exception as e:
        logger.error(f"Failed: {event['id']}: {e}")
        raise
```

### 4. Test with CLI (Optional)

The Stripe CLI is optional and only for local development testing.

```bash
# If Stripe CLI is installed, use for local testing:
stripe listen --forward-to localhost:3000/webhooks/stripe

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

Note: Stripe CLI installation is not required. Use the Dashboard for webhook testing in production.

## List and Manage Endpoints

### List Endpoints
```bash
curl https://api.stripe.com/v1/webhook_endpoints \
  -u "$STRIPE_SECRET_KEY:"
```

### Update Endpoint
```bash
curl https://api.stripe.com/v1/webhook_endpoints/we_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "enabled_events[]=charge.dispute.created" \
  -d "enabled_events[]=charge.dispute.closed"
```

### Disable Endpoint
```bash
curl https://api.stripe.com/v1/webhook_endpoints/we_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "disabled=true"
```

### Delete Endpoint
```bash
curl -X DELETE https://api.stripe.com/v1/webhook_endpoints/we_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

## Debugging

### View Recent Events
```bash
curl "https://api.stripe.com/v1/events?limit=10" \
  -u "$STRIPE_SECRET_KEY:"
```

### Get Specific Event
```bash
curl https://api.stripe.com/v1/events/evt_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

### Resend Event (via Dashboard)
Dashboard > Developers > Events > Select event > Resend
