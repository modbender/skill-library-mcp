# API Reference — Paddle

## Authentication

All requests require an API key in the Authorization header:

```bash
curl https://api.paddle.com/customers \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

**Environment URLs:**
- Sandbox: `https://sandbox-api.paddle.com`
- Production: `https://api.paddle.com`

## Common Endpoints

### Customers

**Create customer:**
```bash
curl -X POST https://api.paddle.com/customers \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe"
  }'
```

**Get customer:**
```bash
curl https://api.paddle.com/customers/ctm_xxx \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

### Subscriptions

**List subscriptions for customer:**
```bash
curl "https://api.paddle.com/subscriptions?customer_id=ctm_xxx" \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

**Cancel subscription:**
```bash
curl -X POST https://api.paddle.com/subscriptions/sub_xxx/cancel \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "effective_from": "next_billing_period"
  }'
```

**Pause subscription:**
```bash
curl -X POST https://api.paddle.com/subscriptions/sub_xxx/pause \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "effective_from": "next_billing_period"
  }'
```

**Resume subscription:**
```bash
curl -X POST https://api.paddle.com/subscriptions/sub_xxx/resume \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "effective_from": "immediately"
  }'
```

### Transactions

**Get transaction:**
```bash
curl https://api.paddle.com/transactions/txn_xxx \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

**List transactions:**
```bash
curl "https://api.paddle.com/transactions?subscription_id=sub_xxx" \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

### Prices

**List prices:**
```bash
curl https://api.paddle.com/prices \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

**Get price:**
```bash
curl https://api.paddle.com/prices/pri_xxx \
  -H "Authorization: Bearer $PADDLE_API_KEY"
```

## Checkout Integration

### Paddle.js Overlay (Recommended)

```html
<script src="https://cdn.paddle.com/paddle/v2/paddle.js"></script>
<script>
  Paddle.Initialize({
    token: 'your_client_side_token',
    environment: 'sandbox' // or 'production'
  });
</script>

<button onclick="openCheckout()">Subscribe</button>

<script>
  function openCheckout() {
    Paddle.Checkout.open({
      items: [{ priceId: 'pri_xxx', quantity: 1 }],
      customer: {
        email: 'user@example.com'
      },
      customData: {
        user_id: 'your_internal_user_id'
      }
    });
  }
</script>
```

### Handling Checkout Events

```javascript
Paddle.Checkout.open({
  items: [{ priceId: 'pri_xxx', quantity: 1 }],
  successCallback: (data) => {
    // Redirect or show success
    // data.transaction_id contains the transaction
  },
  closeCallback: () => {
    // User closed without completing
  }
});
```

## Error Handling

Paddle returns errors in this format:

```json
{
  "error": {
    "type": "request_error",
    "code": "not_found",
    "detail": "Customer not found"
  }
}
```

Common error codes:
- `not_found` — Resource doesn't exist
- `validation_error` — Invalid request data
- `authentication_error` — Invalid API key
- `rate_limit_error` — Too many requests
