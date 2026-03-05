export function aggregateBalanceSheet(db, entityId, dateStart, dateEnd, netIncome) {
  const connections = db.prepare('SELECT id FROM connections WHERE entity_id = ?').all(entityId);
  const connectionIds = connections.map(c => c.id);
  if (connectionIds.length === 0) return null;

  const ph = connectionIds.map(() => '?').join(',');
  const accounts = db.prepare(`SELECT id, name FROM accounts WHERE connection_id IN (${ph})`).all(...connectionIds);
  if (accounts.length === 0) return null;

  const accountIds = accounts.map(a => a.id);
  const aph = accountIds.map(() => '?').join(',');

  const cashAccounts = [];
  for (const acct of accounts) {
    const row = db.prepare('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE account_id = ? AND posted_at <= ?').get(acct.id, dateEnd);
    cashAccounts.push({ name: acct.name || 'Account', balance: row.total });
  }
  const totalCash = cashAccounts.reduce((s, a) => s + a.balance, 0);

  let beginningCash = 0;
  for (const acct of accounts) {
    const row = db.prepare('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE account_id = ? AND posted_at < ?').get(acct.id, dateStart);
    beginningCash += row.total;
  }

  // Owner draws
  const drawRows = db.prepare(`
    SELECT t.amount, ct.category FROM transactions t
    JOIN categorized_transactions ct ON ct.transaction_id = t.id
    WHERE t.account_id IN (${aph}) AND t.posted_at >= ? AND t.posted_at <= ?
      AND ct.category = 'Owner Draws/Distributions'
  `).all(...accountIds, dateStart, dateEnd);
  const ownerDraws = drawRows.reduce((s, r) => s + Number(r.amount), 0);

  const beginningEquity = beginningCash;
  const endingEquity = beginningEquity + netIncome + ownerDraws;

  return {
    asOfDate: dateEnd,
    assets: { cash: { total: totalCash, accounts: cashAccounts } },
    liabilities: { total: 0 },
    equity: { beginningBalance: beginningEquity, netIncome, ownerDraws, endingBalance: endingEquity },
  };
}
