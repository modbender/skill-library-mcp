import { ACCOUNT_CLASSIFICATIONS } from './chart-of-accounts.js';

const classificationMap = new Map(ACCOUNT_CLASSIFICATIONS.map(c => [c.name, c]));

export function aggregateCashFlow(db, entityId, dateStart, dateEnd) {
  const connections = db.prepare('SELECT id FROM connections WHERE entity_id = ?').all(entityId);
  const connectionIds = connections.map(c => c.id);
  if (connectionIds.length === 0) return null;

  const ph = connectionIds.map(() => '?').join(',');
  const accounts = db.prepare(`SELECT id FROM accounts WHERE connection_id IN (${ph})`).all(...connectionIds);
  const accountIds = accounts.map(a => a.id);
  if (accountIds.length === 0) return null;

  const aph = accountIds.map(() => '?').join(',');
  const rows = db.prepare(`
    SELECT t.amount, ct.category FROM transactions t
    JOIN categorized_transactions ct ON ct.transaction_id = t.id
    WHERE t.account_id IN (${aph}) AND t.posted_at >= ? AND t.posted_at <= ?
    ORDER BY t.posted_at ASC
  `).all(...accountIds, dateStart, dateEnd);

  const operating = {}, financing = {};
  for (const tx of rows) {
    if (!tx.category) continue;
    const cls = classificationMap.get(tx.category);
    if (!cls?.cashFlowSection) continue;
    const amount = Number(tx.amount);
    if (cls.cashFlowSection === 'Operating') operating[tx.category] = (operating[tx.category] || 0) + amount;
    else if (cls.cashFlowSection === 'Financing') financing[tx.category] = (financing[tx.category] || 0) + amount;
  }

  const operatingItems = Object.entries(operating).map(([name, amount]) => ({ name, amount }));
  const operatingTotal = operatingItems.reduce((s, i) => s + i.amount, 0);
  const financingItems = Object.entries(financing).map(([name, amount]) => ({ name, amount }));
  const financingTotal = financingItems.reduce((s, i) => s + i.amount, 0);
  const netChange = operatingTotal + financingTotal;

  let beginningCash = 0;
  for (const id of accountIds) {
    const row = db.prepare('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE account_id = ? AND posted_at < ?').get(id, dateStart);
    beginningCash += row.total;
  }

  return {
    dateStart, dateEnd,
    operating: { items: operatingItems, total: operatingTotal },
    investing: { items: [], total: 0 },
    financing: { items: financingItems, total: financingTotal },
    netChange, beginningCash, endingCash: beginningCash + netChange,
  };
}
