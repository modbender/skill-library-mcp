import Stripe from 'stripe';
import { config } from '../config';
import { addBalance, getKeyInfoById } from './api-keys';

let _stripe: Stripe | null = null;
function getStripe(): Stripe {
  if (!_stripe) {
    if (!config.stripeSecretKey) {
      throw new Error('Stripe secret key not configured. Set STRIPE_SECRET_KEY env var.');
    }
    _stripe = new Stripe(config.stripeSecretKey);
  }
  return _stripe;
}

const TOP_UP_AMOUNTS = [
  { amount: 500, label: '$5' },
  { amount: 1000, label: '$10' },
  { amount: 2500, label: '$25' },
  { amount: 5000, label: '$50' },
];

/** Create a Stripe Checkout session for top-up. Amount in cents. */
export async function createCheckoutSession(params: {
  keyId: number;
  amountCents: number;
  successUrl: string;
  cancelUrl: string;
}): Promise<{ url: string; sessionId: string }> {
  const { keyId, amountCents, successUrl, cancelUrl } = params;

  // Validate amount
  const validAmount = TOP_UP_AMOUNTS.find(a => a.amount === amountCents);
  if (!validAmount) {
    throw new Error(`Invalid amount. Choose from: ${TOP_UP_AMOUNTS.map(a => a.label).join(', ')}`);
  }

  // Verify key exists
  const keyInfo = getKeyInfoById(keyId);
  if (!keyInfo) throw new Error('API key not found');

  const session = await getStripe().checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: 'usd',
        product_data: {
          name: `Windfall API Credit — ${validAmount.label}`,
          description: `Top up API key ${keyInfo.keyPrefix} with ${validAmount.label} inference credit`,
        },
        unit_amount: amountCents,
      },
      quantity: 1,
    }],
    mode: 'payment',
    success_url: successUrl,
    cancel_url: cancelUrl,
    metadata: {
      key_id: keyId.toString(),
      amount_usd: (amountCents / 100).toFixed(2),
    },
  });

  return { url: session.url!, sessionId: session.id };
}

/** Handle Stripe webhook event. Returns true if balance was credited. */
export async function handleWebhook(payload: Buffer, signature: string): Promise<{
  handled: boolean;
  event?: string;
  keyId?: number;
  amountUsd?: number;
}> {
  let event: Stripe.Event;

  if (config.stripeWebhookSecret) {
    event = getStripe().webhooks.constructEvent(payload, signature, config.stripeWebhookSecret);
  } else {
    throw new Error('Stripe webhook secret not configured. Set STRIPE_WEBHOOK_SECRET env var.');
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object as Stripe.Checkout.Session;

    if (session.payment_status === 'paid' && session.metadata?.key_id) {
      const keyId = parseInt(session.metadata.key_id, 10);
      const amountUsd = parseFloat(session.metadata.amount_usd || '0');

      if (keyId && amountUsd > 0) {
        addBalance(keyId, amountUsd);
        console.log(`[stripe] Credited $${amountUsd} to key #${keyId}`);
        return { handled: true, event: event.type, keyId, amountUsd };
      }
    }
  }

  return { handled: false, event: event.type };
}

export { TOP_UP_AMOUNTS };
