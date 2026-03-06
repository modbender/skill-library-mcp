import { PNL_SECTIONS } from './chart-of-accounts.js';

/**
 * Default Stripe fee configuration
 * Can be overridden per-entity via entity_settings table
 */
const DEFAULT_STRIPE_FEE_RATE = 0.029;  // 2.9%
const DEFAULT_STRIPE_FEE_FIXED = 0.30;  // $0.30 per transaction

function generateMonths(startDate, endDate) {
  const months = [];
  const cursor = new Date(startDate + "T00:00:00Z");
  const end = new Date(endDate + "T00:00:00Z");
  cursor.setUTCDate(1);
  while (cursor <= end) {
    const y = cursor.getUTCFullYear();
    const m = String(cursor.getUTCMonth() + 1).padStart(2, "0");
    months.push(`${y}-${m}`);
    cursor.setUTCMonth(cursor.getUTCMonth() + 1);
  }
  return months;
}

/**
 * Apply month offset for accrual basis accounting
 * Mercury posts transactions 1-2 days after the actual transaction date
 * For accrual basis, we shift transactions back by the offset
 */
function applyMonthOffset(postedAt, offsetMonths) {
  if (!offsetMonths || offsetMonths === 0) return postedAt;
  
  const date = new Date(postedAt + "T00:00:00Z");
  date.setUTCMonth(date.getUTCMonth() - offsetMonths);
  return date.toISOString().slice(0, 10);
}

/**
 * Get entity settings from database
 * Settings include: stripe_fee_rate, stripe_fee_fixed, month_offset, accounting_basis
 */
function getEntitySettings(db, entityId) {
  // Ensure settings table exists
  db.exec(`
    CREATE TABLE IF NOT EXISTS entity_settings (
      entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
      stripe_fee_rate REAL DEFAULT 0.029,
      stripe_fee_fixed REAL DEFAULT 0.30,
      month_offset INTEGER DEFAULT 0,
      accounting_basis TEXT DEFAULT 'cash',
      amortization_monthly REAL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
  `);
  
  const settings = db.prepare(`
    SELECT stripe_fee_rate, stripe_fee_fixed, month_offset, accounting_basis, amortization_monthly
    FROM entity_settings WHERE entity_id = ?
  `).get(entityId);
  
  return {
    stripeFeeRate: settings?.stripe_fee_rate ?? DEFAULT_STRIPE_FEE_RATE,
    stripeFeeFixed: settings?.stripe_fee_fixed ?? DEFAULT_STRIPE_FEE_FIXED,
    monthOffset: settings?.month_offset ?? 0,
    accountingBasis: settings?.accounting_basis ?? 'cash',
    amortizationMonthly: settings?.amortization_monthly ?? 0,
  };
}

/**
 * Calculate gross revenue and Stripe fees from net Stripe payouts
 * 
 * For each Stripe payout:
 *   Net = Gross - (Gross * rate + fixed * numTransactions)
 *   
 * Since we don't know numTransactions per payout, we approximate:
 *   Net ≈ Gross * (1 - rate) - avgFixedPerPayout
 *   Gross ≈ Net / (1 - rate)  (simplified when fixed fees are small)
 * 
 * For more accuracy, we calculate fees as: Gross - Net
 */
function calculateStripeGrossUp(transactions, settings) {
  const stripePayouts = transactions.filter(t => 
    t.counterparty?.toLowerCase().includes('stripe') && t.amount > 0
  );
  
  if (stripePayouts.length === 0) {
    return { grossUpAmount: 0, stripeFees: 0, payoutCount: 0 };
  }
  
  const totalNet = stripePayouts.reduce((sum, t) => sum + t.amount, 0);
  const payoutCount = stripePayouts.length;
  
  // Estimate gross: Net = Gross * (1 - rate) - (fixed * estimatedTxCount)
  // Simplified: Gross ≈ Net / (1 - rate)
  const grossEstimate = totalNet / (1 - settings.stripeFeeRate);
  const stripeFees = grossEstimate - totalNet;
  const grossUpAmount = stripeFees; // Amount to add to net to get gross
  
  return { grossUpAmount, stripeFees, payoutCount };
}

/**
 * Build P&L with enhanced features:
 * - Automatic Stripe gross-up (converts net payouts to gross revenue + fees)
 * - Month offset for accrual basis accounting  
 * - Synthetic entries for amortization
 * - Proper handling of global vs entity categorization rules
 */
export function buildPnl(db, entityId, startDate, endDate, options = {}) {
  const settings = getEntitySettings(db, entityId);
  const {
    includeStripeGrossUp = true,
    includeAmortization = true,
    useMonthOffset = settings.accountingBasis === 'accrual',
  } = options;
  
  const connections = db.prepare('SELECT id FROM connections WHERE entity_id = ?').all(entityId);
  const connectionIds = connections.map(c => c.id);
  if (connectionIds.length === 0) return null;

  const accounts = db.prepare(`SELECT id FROM accounts WHERE connection_id IN (${connectionIds.map(() => '?').join(',')})`).all(...connectionIds);
  const accountIds = accounts.map(a => a.id);
  if (accountIds.length === 0) return null;

  const entity = db.prepare('SELECT name FROM entities WHERE id = ?').get(entityId);
  const entityName = entity?.name || 'Unknown Entity';

  const placeholders = accountIds.map(() => '?').join(',');
  const rawTransactions = db.prepare(`
    SELECT t.id, t.posted_at, t.amount, t.counterparty_name, t.bank_description,
           ct.category, ct.subcategory, ct.confidence
    FROM transactions t
    LEFT JOIN categorized_transactions ct ON ct.transaction_id = t.id
    WHERE t.account_id IN (${placeholders})
      AND t.posted_at >= ? AND t.posted_at <= ?
    ORDER BY t.posted_at ASC
  `).all(...accountIds, startDate, endDate);

  if (rawTransactions.length === 0) return null;

  // Apply month offset if using accrual basis
  const monthOffset = useMonthOffset ? settings.monthOffset : 0;
  
  const months = generateMonths(startDate, endDate);
  const categoryMonthly = {};
  let uncategorizedCount = 0;
  const allTransactions = [];
  
  // Track Stripe payouts for gross-up calculation
  const stripePayoutsByMonth = {};

  for (const tx of rawTransactions) {
    const category = tx.category || null;
    const rawMonth = tx.posted_at?.slice(0, 7);
    const adjustedDate = applyMonthOffset(tx.posted_at, monthOffset);
    const month = adjustedDate.slice(0, 7);
    const amount = Number(tx.amount);

    allTransactions.push({
      id: tx.id,
      date: tx.posted_at,
      adjustedDate,
      counterparty: tx.counterparty_name,
      description: tx.bank_description,
      amount,
      category: category || 'Uncategorized',
      subcategory: tx.subcategory || null,
      confidence: tx.confidence ? Number(tx.confidence) : null,
    });

    // Track Stripe payouts for gross-up
    if (tx.counterparty_name?.toLowerCase().includes('stripe') && amount > 0) {
      if (!stripePayoutsByMonth[month]) stripePayoutsByMonth[month] = [];
      stripePayoutsByMonth[month].push({ amount, category });
    }

    if (!category) { uncategorizedCount++; continue; }
    if (!categoryMonthly[category]) categoryMonthly[category] = {};
    categoryMonthly[category][month] = (categoryMonthly[category][month] || 0) + amount;
  }

  // Apply Stripe revenue: prefer actual Stripe data, fall back to gross-up estimate
  let totalStripeGrossUp = 0;
  let totalStripeFees = 0;
  
  // Check if we have actual Stripe balance_transaction data
  const stripeDataByMonth = {};
  try {
    const stripeRows = db.prepare(
      `SELECT month, gross_revenue, refunds, stripe_fees FROM stripe_monthly_revenue WHERE entity_id = ?`
    ).all(entityId);
    for (const row of stripeRows) stripeDataByMonth[row.month] = row;
  } catch { /* table may not exist yet */ }

  if (includeStripeGrossUp) {
    for (const month of months) {
      // Apply month offset: Stripe month X maps to books month X-offset
      // The offset means bookkeeper's month X = Stripe's month X+offset
      // So for a given books month, we look at Stripe month = books month + offset
      const offsetMonth = applyMonthOffset(`${month}-15`, -monthOffset).slice(0, 7);
      const stripeData = stripeDataByMonth[offsetMonth];
      
      if (stripeData) {
        // Use actual Stripe data: replace Mercury Stripe payout with real gross revenue
        const monthPayouts = stripePayoutsByMonth[month] || [];
        const mercuryStripeNet = monthPayouts.reduce((sum, p) => sum + p.amount, 0);
        
        // Remove Mercury Stripe payout from Sales (it was already counted as categorized revenue)
        // and replace with actual Stripe gross revenue
        const grossUp = stripeData.gross_revenue - stripeData.refunds - mercuryStripeNet;
        const fees = stripeData.stripe_fees;
        
        if (!categoryMonthly['Sales/Service Revenue']) categoryMonthly['Sales/Service Revenue'] = {};
        categoryMonthly['Sales/Service Revenue'][month] = (categoryMonthly['Sales/Service Revenue'][month] || 0) + grossUp;
        
        if (!categoryMonthly['Stripe Fees']) categoryMonthly['Stripe Fees'] = {};
        categoryMonthly['Stripe Fees'][month] = (categoryMonthly['Stripe Fees'][month] || 0) - fees;
        
        totalStripeGrossUp += grossUp;
        totalStripeFees += fees;
      } else {
        // Fall back to estimate from Mercury payouts
        const monthPayouts = stripePayoutsByMonth[month] || [];
        if (monthPayouts.length === 0) continue;
        
        const netAmount = monthPayouts.reduce((sum, p) => sum + p.amount, 0);
        const grossAmount = netAmount / (1 - settings.stripeFeeRate);
        const fees = grossAmount - netAmount;
        
        if (!categoryMonthly['Sales/Service Revenue']) categoryMonthly['Sales/Service Revenue'] = {};
        categoryMonthly['Sales/Service Revenue'][month] = (categoryMonthly['Sales/Service Revenue'][month] || 0) + fees;
        
        if (!categoryMonthly['Stripe Fees']) categoryMonthly['Stripe Fees'] = {};
        categoryMonthly['Stripe Fees'][month] = (categoryMonthly['Stripe Fees'][month] || 0) - fees;
        
        totalStripeGrossUp += fees;
        totalStripeFees += fees;
      }
    }
  }
  
  // Add synthetic amortization if configured
  let totalAmortization = 0;
  if (includeAmortization && settings.amortizationMonthly > 0) {
    if (!categoryMonthly['Amortization']) categoryMonthly['Amortization'] = {};
    for (const month of months) {
      categoryMonthly['Amortization'][month] = (categoryMonthly['Amortization'][month] || 0) - settings.amortizationMonthly;
      totalAmortization += settings.amortizationMonthly;
    }
  }

  // Build sections from category totals
  const sections = [];
  for (const sectionDef of PNL_SECTIONS) {
    const isRevenue = sectionDef.name === 'Revenue';
    const categories = [];
    let sectionTotal = 0;

    for (const catName of sectionDef.categories) {
      const monthly = {};
      let catTotal = 0;
      for (const month of months) {
        const raw = categoryMonthly[catName]?.[month] || 0;
        const display = isRevenue ? raw : Math.abs(raw);
        monthly[month] = display;
        catTotal += display;
      }
      if (catTotal === 0) continue;
      categories.push({ name: catName, monthly, total: catTotal });
      sectionTotal += catTotal;
    }

    if (categories.length === 0) continue;
    sections.push({ name: sectionDef.name, categories, sectionTotal });
  }

  const revenue = sections.find(s => s.name === 'Revenue')?.sectionTotal || 0;
  const cogs = sections.find(s => s.name === 'Cost of Goods Sold')?.sectionTotal || 0;
  const grossProfit = revenue - cogs;
  const opex = sections.find(s => s.name === 'Operating Expenses')?.sectionTotal || 0;
  const netIncome = grossProfit - opex;

  return {
    entityName, 
    dateStart: startDate, 
    dateEnd: endDate, 
    months, 
    sections,
    summary: { revenue, cogs, grossProfit, opex, operatingIncome: netIncome, netIncome },
    uncategorizedCount, 
    transactions: allTransactions,
    // Metadata about applied adjustments
    adjustments: {
      stripeGrossUp: totalStripeGrossUp,
      stripeFees: totalStripeFees,
      amortization: totalAmortization,
      monthOffset,
      accountingBasis: settings.accountingBasis,
    },
    settings,
  };
}

/**
 * Update entity settings
 */
export function updateEntitySettings(db, entityId, settings) {
  // Ensure table exists
  db.exec(`
    CREATE TABLE IF NOT EXISTS entity_settings (
      entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
      stripe_fee_rate REAL DEFAULT 0.029,
      stripe_fee_fixed REAL DEFAULT 0.30,
      month_offset INTEGER DEFAULT 0,
      accounting_basis TEXT DEFAULT 'cash',
      amortization_monthly REAL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
  `);
  
  const existing = db.prepare('SELECT 1 FROM entity_settings WHERE entity_id = ?').get(entityId);
  
  if (existing) {
    const updates = [];
    const values = [];
    
    if (settings.stripeFeeRate !== undefined) {
      updates.push('stripe_fee_rate = ?');
      values.push(settings.stripeFeeRate);
    }
    if (settings.stripeFeeFixed !== undefined) {
      updates.push('stripe_fee_fixed = ?');
      values.push(settings.stripeFeeFixed);
    }
    if (settings.monthOffset !== undefined) {
      updates.push('month_offset = ?');
      values.push(settings.monthOffset);
    }
    if (settings.accountingBasis !== undefined) {
      updates.push('accounting_basis = ?');
      values.push(settings.accountingBasis);
    }
    if (settings.amortizationMonthly !== undefined) {
      updates.push('amortization_monthly = ?');
      values.push(settings.amortizationMonthly);
    }
    
    if (updates.length > 0) {
      updates.push("updated_at = datetime('now')");
      values.push(entityId);
      db.prepare(`UPDATE entity_settings SET ${updates.join(', ')} WHERE entity_id = ?`).run(...values);
    }
  } else {
    db.prepare(`
      INSERT INTO entity_settings (entity_id, stripe_fee_rate, stripe_fee_fixed, month_offset, accounting_basis, amortization_monthly)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(
      entityId,
      settings.stripeFeeRate ?? DEFAULT_STRIPE_FEE_RATE,
      settings.stripeFeeFixed ?? DEFAULT_STRIPE_FEE_FIXED,
      settings.monthOffset ?? 0,
      settings.accountingBasis ?? 'cash',
      settings.amortizationMonthly ?? 0
    );
  }
}
