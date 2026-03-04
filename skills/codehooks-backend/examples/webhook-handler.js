import { app, Datastore } from 'codehooks-js';
import { verify } from 'webhook-verify';

// Allow webhook endpoint without JWT authentication
app.auth('/webhook/*', (req, res, next) => {
  next();
});

app.post('/webhook/stripe', async (req, res) => {
  // Verify the webhook signature using webhook-verify
  // Supports: stripe, github, shopify, slack, twilio, and more
  const isValid = verify('stripe', req.rawBody, req.headers, process.env.STRIPE_WEBHOOK_SECRET);
  if (!isValid) {
    return res.status(401).send('Invalid signature');
  }

  const conn = await Datastore.open();
  await conn.insertOne('events', {
    ...req.body,
    receivedAt: new Date().toISOString()
  });
  res.json({ received: true });
});

export default app.init();
