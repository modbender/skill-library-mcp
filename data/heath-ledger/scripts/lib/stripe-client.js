const STRIPE_BASE_URL = "https://api.stripe.com/v1";

export async function stripeRequest(token, path, params = {}) {
  const url = new URL(`${STRIPE_BASE_URL}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Stripe API error (${response.status}): ${errorText}`);
  }

  return response.json();
}

/**
 * Fetch all balance transactions for a date range, handling pagination.
 * Returns arrays of charges, refunds with amounts in DOLLARS (not cents).
 */
export async function getBalanceTransactions(token, startDate, endDate) {
  const startUnix = Math.floor(new Date(startDate + "T00:00:00Z").getTime() / 1000);
  const endUnix = Math.floor(new Date(endDate + "T00:00:00Z").getTime() / 1000);

  const allTransactions = [];
  let startingAfter = null;
  let hasMore = true;

  while (hasMore) {
    const params = {
      "created[gte]": startUnix,
      "created[lt]": endUnix,
      limit: 100,
    };
    if (startingAfter) params.starting_after = startingAfter;

    const response = await stripeRequest(token, "/balance_transactions", params);
    const data = response.data || [];
    allTransactions.push(...data);

    hasMore = response.has_more;
    if (data.length > 0) {
      startingAfter = data[data.length - 1].id;
    } else {
      hasMore = false;
    }
  }

  // Separate by type and convert cents to dollars
  const charges = [];
  const refunds = [];
  let totalFees = 0;

  for (const tx of allTransactions) {
    if (tx.type === "charge" || tx.type === "payment") {
      charges.push({
        id: tx.id,
        amount: tx.amount / 100,
        fee: tx.fee / 100,
        net: tx.net / 100,
        created: tx.created,
        description: tx.description,
      });
      totalFees += tx.fee / 100;
    } else if (tx.type === "refund") {
      refunds.push({
        id: tx.id,
        amount: Math.abs(tx.amount) / 100,
        fee: tx.fee / 100,
        net: tx.net / 100,
        created: tx.created,
        description: tx.description,
      });
    }
  }

  const grossRevenue = charges.reduce((sum, c) => sum + c.amount, 0);
  const totalRefunds = refunds.reduce((sum, r) => sum + r.amount, 0);

  return {
    charges,
    refunds,
    fees: totalFees,
    grossRevenue,
    totalRefunds,
    netRevenue: grossRevenue - totalRefunds,
    transactionCount: allTransactions.length,
  };
}

/**
 * Get monthly revenue summary for a specific month.
 * Month is 1-indexed (1=January).
 */
export async function getMonthlyRevenue(token, year, month) {
  const startDate = `${year}-${String(month).padStart(2, "0")}-01`;
  const nextMonth = month === 12 ? 1 : month + 1;
  const nextYear = month === 12 ? year + 1 : year;
  const endDate = `${nextYear}-${String(nextMonth).padStart(2, "0")}-01`;

  const result = await getBalanceTransactions(token, startDate, endDate);

  return {
    grossRevenue: result.grossRevenue,
    refunds: result.totalRefunds,
    netRevenue: result.netRevenue,
    stripeFees: result.fees,
    transactionCount: result.charges.length + result.refunds.length,
  };
}
