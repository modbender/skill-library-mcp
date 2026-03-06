# Server-Side Receipt Verification

## Why Server Verification

Client-side validation is bypassable. Server verification:
- Prevents receipt forgery
- Enables refund handling
- Provides source of truth for entitlements
- Required for subscription management

## iOS: App Store Server API

### Verify Transaction

```javascript
// Node.js example
const jwt = require('jsonwebtoken');
const axios = require('axios');

async function verifyiOSTransaction(signedTransactionInfo) {
  // Decode JWS to get transactionId
  const decoded = jwt.decode(signedTransactionInfo, { complete: true });
  const transactionId = decoded.payload.transactionId;
  
  // Verify with App Store Server API
  const token = generateAppStoreJWT();
  
  const response = await axios.get(
    `https://api.storekit.itunes.apple.com/inApps/v1/transactions/${transactionId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  
  return response.data;
}

function generateAppStoreJWT() {
  const payload = {
    iss: 'YOUR_ISSUER_ID',
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600,
    aud: 'appstoreconnect-v1',
    bid: 'com.your.app'
  };
  
  return jwt.sign(payload, PRIVATE_KEY, {
    algorithm: 'ES256',
    keyid: 'YOUR_KEY_ID'
  });
}
```

### Get Subscription Status

```javascript
async function getSubscriptionStatus(transactionId) {
  const token = generateAppStoreJWT();
  
  const response = await axios.get(
    `https://api.storekit.itunes.apple.com/inApps/v1/subscriptions/${transactionId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  
  // Returns subscription group status
  return response.data;
}
```

### Server Notifications V2

Configure in App Store Connect to receive:

```javascript
// Webhook endpoint
app.post('/apple/webhook', (req, res) => {
  const { signedPayload } = req.body;
  
  // Verify JWT signature
  const decoded = verifyAppleJWT(signedPayload);
  
  switch (decoded.notificationType) {
    case 'SUBSCRIBED':
      grantAccess(decoded.data.transactionInfo);
      break;
    case 'DID_RENEW':
      extendAccess(decoded.data.transactionInfo);
      break;
    case 'EXPIRED':
    case 'REFUND':
      revokeAccess(decoded.data.transactionInfo);
      break;
    case 'GRACE_PERIOD_EXPIRED':
      revokeAccess(decoded.data.transactionInfo);
      break;
  }
  
  res.sendStatus(200);
});
```

## Android: Google Play Developer API

### Setup

```javascript
const { google } = require('googleapis');

const auth = new google.auth.GoogleAuth({
  keyFile: 'service-account.json',
  scopes: ['https://www.googleapis.com/auth/androidpublisher']
});

const androidPublisher = google.androidpublisher({
  version: 'v3',
  auth
});
```

### Verify Purchase

```javascript
async function verifyAndroidPurchase(packageName, productId, purchaseToken) {
  const response = await androidPublisher.purchases.products.get({
    packageName,
    productId,
    token: purchaseToken
  });
  
  const purchase = response.data;
  
  // Check purchase state
  // 0 = purchased, 1 = canceled
  if (purchase.purchaseState !== 0) {
    throw new Error('Purchase not valid');
  }
  
  // Check consumption state for consumables
  // 0 = not consumed, 1 = consumed
  
  return {
    valid: true,
    orderId: purchase.orderId,
    purchaseTime: purchase.purchaseTimeMillis
  };
}
```

### Verify Subscription

```javascript
async function verifyAndroidSubscription(packageName, subscriptionId, purchaseToken) {
  const response = await androidPublisher.purchases.subscriptions.get({
    packageName,
    subscriptionId,
    token: purchaseToken
  });
  
  const sub = response.data;
  
  return {
    valid: true,
    expiryTime: parseInt(sub.expiryTimeMillis),
    autoRenewing: sub.autoRenewing,
    cancelReason: sub.cancelReason, // 0 = user, 1 = billing
    paymentState: sub.paymentState // 0 = pending, 1 = received, 2 = free trial, 3 = pending deferred
  };
}
```

### Real-Time Developer Notifications (RTDN)

Configure Pub/Sub in Google Cloud:

```javascript
const { PubSub } = require('@google-cloud/pubsub');

const pubsub = new PubSub();
const subscription = pubsub.subscription('play-rtdn');

subscription.on('message', async (message) => {
  const data = JSON.parse(Buffer.from(message.data, 'base64').toString());
  
  if (data.subscriptionNotification) {
    const { notificationType, purchaseToken, subscriptionId } = data.subscriptionNotification;
    
    switch (notificationType) {
      case 1: // RECOVERED
      case 2: // RENEWED
        await extendSubscription(purchaseToken);
        break;
      case 3: // CANCELED
      case 13: // EXPIRED
        await revokeSubscription(purchaseToken);
        break;
      case 5: // ON_HOLD (payment issue)
        await handlePaymentIssue(purchaseToken);
        break;
    }
  }
  
  message.ack();
});
```

## Database Schema

```sql
CREATE TABLE purchases (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  platform ENUM('ios', 'android') NOT NULL,
  product_id VARCHAR(255) NOT NULL,
  transaction_id VARCHAR(255) UNIQUE NOT NULL,
  purchase_token TEXT, -- Android only
  original_transaction_id VARCHAR(255), -- iOS subscription family
  purchased_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP, -- For subscriptions
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE entitlements (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  entitlement_key VARCHAR(255) NOT NULL, -- e.g., 'premium', 'credits'
  source_purchase_id UUID REFERENCES purchases(id),
  granted_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  UNIQUE(user_id, entitlement_key)
);
```

## Security Best Practices

1. **Always verify server-side** — never trust client
2. **Idempotent processing** — handle duplicate notifications
3. **Store raw receipts** — for dispute resolution
4. **Rate limit verification** — prevent abuse
5. **Use webhooks** — don't poll for status changes
6. **Log everything** — purchases are money, audit trail is essential
