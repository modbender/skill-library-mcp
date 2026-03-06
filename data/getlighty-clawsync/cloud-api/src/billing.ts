import Stripe from "stripe";

const stripe = process.env.STRIPE_SECRET_KEY
  ? new Stripe(process.env.STRIPE_SECRET_KEY)
  : null;

const FREE_TIER_BYTES = 50 * 1024 * 1024; // 50 MB

export async function createCustomer(
  email: string,
  vaultId: string
): Promise<string | null> {
  if (!stripe) return null;
  const customer = await stripe.customers.create({
    email,
    metadata: { vault_id: vaultId },
  });
  return customer.id;
}

/**
 * Create a metered subscription when usage exceeds the free tier.
 * Uses the price ID from env (should be a metered price at $0.005/unit where unit = 1 MB).
 */
export async function ensureSubscription(
  customerId: string,
  currentSizeBytes: number
): Promise<string | null> {
  if (!stripe || !process.env.STRIPE_PRICE_ID) return null;
  if (currentSizeBytes <= FREE_TIER_BYTES) return null;

  const subscription = await stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: process.env.STRIPE_PRICE_ID }],
    metadata: { purpose: "clawsync-storage" },
  });
  return subscription.id;
}

/**
 * Report usage to Stripe. Called after each push.
 * Reports the billable MB (total - 50 MB free tier).
 */
export async function reportUsage(
  subscriptionId: string,
  currentSizeBytes: number
): Promise<void> {
  if (!stripe) return;

  const billableBytes = Math.max(0, currentSizeBytes - FREE_TIER_BYTES);
  const billableMb = Math.ceil(billableBytes / (1024 * 1024));

  if (billableMb <= 0) return;

  // Find the subscription item
  const sub = await stripe.subscriptions.retrieve(subscriptionId);
  const itemId = sub.items.data[0]?.id;
  if (!itemId) return;

  await stripe.subscriptionItems.createUsageRecord(itemId, {
    quantity: billableMb,
    action: "set",
  });
}

export function computeBilling(sizeBytes: number) {
  const usedMb = sizeBytes / (1024 * 1024);
  const freeMb = 50;
  const billableMb = Math.max(0, usedMb - freeMb);
  const monthlyCost = billableMb * 0.005;
  return {
    used_bytes: sizeBytes,
    used_mb: Math.round(usedMb * 100) / 100,
    free_mb: freeMb,
    billable_mb: Math.round(billableMb * 100) / 100,
    monthly_cost: Math.round(monthlyCost * 100) / 100,
  };
}
