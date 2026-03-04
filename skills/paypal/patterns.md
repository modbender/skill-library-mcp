# Code Patterns — PayPal Integration

## Create Order (Server)

```javascript
const createOrder = async (amount, currency = 'USD') => {
  const token = await getToken();
  const res = await fetch('https://api.paypal.com/v2/checkout/orders', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      intent: 'CAPTURE',
      purchase_units: [{
        amount: { currency_code: currency, value: amount.toFixed(2) },
        custom_id: 'your-internal-order-id' // For reconciliation
      }]
    })
  });
  return res.json(); // { id, status, links }
};
```

## Capture Payment (After Approval)

```javascript
const captureOrder = async (orderId) => {
  const token = await getToken();
  
  // First verify the order
  const order = await fetch(`https://api.paypal.com/v2/checkout/orders/${orderId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());
  
  if (order.status !== 'APPROVED') {
    throw new Error(`Invalid order status: ${order.status}`);
  }
  
  // Then capture
  const capture = await fetch(`https://api.paypal.com/v2/checkout/orders/${orderId}/capture`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
  });
  return capture.json();
};
```

## Frontend (JavaScript SDK)

```html
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>
<div id="paypal-button-container"></div>
<script>
  paypal.Buttons({
    createOrder: () => {
      return fetch('/api/paypal/create-order', { method: 'POST' })
        .then(res => res.json())
        .then(data => data.id);
    },
    onApprove: (data) => {
      return fetch('/api/paypal/capture-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ orderId: data.orderID })
      }).then(res => res.json())
        .then(details => {
          alert('Payment completed!');
        });
    },
    onError: (err) => {
      console.error('PayPal error:', err);
    }
  }).render('#paypal-button-container');
</script>
```

## Subscription (Billing)

```javascript
// Create product first
const product = await fetch('https://api.paypal.com/v1/catalogs/products', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Premium Plan',
    type: 'SERVICE'
  })
}).then(r => r.json());

// Then create plan
const plan = await fetch('https://api.paypal.com/v1/billing/plans', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    product_id: product.id,
    name: 'Monthly Premium',
    billing_cycles: [{
      frequency: { interval_unit: 'MONTH', interval_count: 1 },
      tenure_type: 'REGULAR',
      sequence: 1,
      total_cycles: 0, // Infinite
      pricing_scheme: { fixed_price: { value: '9.99', currency_code: 'USD' } }
    }],
    payment_preferences: {
      auto_bill_outstanding: true,
      payment_failure_threshold: 3
    }
  })
}).then(r => r.json());
```

## Refund

```javascript
const refundCapture = async (captureId, amount = null) => {
  const token = await getToken();
  const body = amount ? { amount: { value: amount, currency_code: 'USD' } } : {};
  
  return fetch(`https://api.paypal.com/v2/payments/captures/${captureId}/refund`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }).then(r => r.json());
};
```
