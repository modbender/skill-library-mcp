const fs = require('fs').promises;
const { getResourcePaths, ensureResources } = require('./resources');

/**
 * Positions repository
 * - Manages position state machine:
 *   FLAT -> ENTRY_PENDING -> OPEN -> EXIT_PENDING -> CLOSED
 */

const POSITIONS_FILE = getResourcePaths().positionsFile;

class PositionsRepo {
  async load() {
    await ensureResources().catch(() => {});
    try {
      const data = await fs.readFile(POSITIONS_FILE, 'utf8');
      const parsed = JSON.parse(data);
      if (!parsed || typeof parsed !== 'object') return { positions: [] };
      if (!Array.isArray(parsed.positions)) parsed.positions = [];
      return parsed;
    } catch {
      return { positions: [] };
    }
  }

  async save(data) {
    await ensureResources().catch(() => {});
    await fs.writeFile(POSITIONS_FILE, JSON.stringify(data, null, 2), 'utf8');
  }

  async createEntryPending(market, strategy, budget) {
    const data = await this.load();
    const newPos = {
      id: `pos_${Date.now()}`,
      market,
      state: 'ENTRY_PENDING',
      entry: { budgetKRW: budget, createdAt: new Date().toISOString() },
      meta: { strategy },
    };
    data.positions.push(newPos);
    await this.save(data);
    return newPos;
  }

  async updateToOpen(market, orderResult) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'ENTRY_PENDING');
    if (!pos) return;
    pos.state = 'OPEN';
    pos.entry.orderUuid = orderResult.uuid;
    // NOTE:
    // For market-buy (ord_type='price'), Upbit returns `price` as the KRW amount field, not the filled average price.
    // The true avg fill price should be derived from /order(trades) or /accounts(avg_buy_price).
    // We keep this field as a best-effort hint only.
    pos.entry.avgFillPrice = Number(orderResult?.avgFillPrice || orderResult?.trade_price || 0);
    pos.entry.openedAt = new Date().toISOString();

    // trailing state
    pos.exit = pos.exit || {};
    const base = Number(pos.entry.avgFillPrice || 0);
    pos.exit.peakPrice = Number.isFinite(Number(pos.exit.peakPrice)) ? pos.exit.peakPrice : base;
    pos.exit.trailingActive = !!pos.exit.trailingActive;

    await this.save(data);
  }

  /**
   * Import an OPEN position from /accounts.
   * - This allows the monitor/worker to manage assets bought outside this bot
   *   (manual trades, previous runs, partial fills, etc.).
   */
  async importOpenFromAccounts(market, avgBuyPrice, meta = {}) {
    const data = await this.load();
    const exists = data.positions.find(p => p.market === market && (p.state === 'OPEN' || p.state === 'ENTRY_PENDING' || p.state === 'EXIT_PENDING'));
    if (exists) return exists;

    const newPos = {
      id: `pos_import_${Date.now()}`,
      market,
      state: 'OPEN',
      entry: {
        budgetKRW: null,
        orderUuid: null,
        avgFillPrice: Number(avgBuyPrice || 0),
        openedAt: null,
        importedAt: new Date().toISOString(),
      },
      meta: { strategy: 'imported', ...meta },
      exit: { peakPrice: Number(avgBuyPrice || 0), trailingActive: false },
    };

    data.positions.push(newPos);
    await this.save(data);
    return newPos;
  }

  async updatePeak(market, currentPrice, opts = {}) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'OPEN');
    if (!pos) return;

    pos.exit = pos.exit || {};
    const peak = Number(pos.exit.peakPrice || pos.entry?.avgFillPrice || 0);
    if (!Number.isFinite(peak) || peak <= 0) {
      pos.exit.peakPrice = currentPrice;
    } else if (currentPrice > peak) {
      pos.exit.peakPrice = currentPrice;
    }
    if (opts.activate === true) pos.exit.trailingActive = true;

    await this.save(data);
  }

  async updateToExitPending(market, reason) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'OPEN');
    if (!pos) return;
    pos.state = 'EXIT_PENDING';
    pos.exit = { ...(pos.exit || {}), reason, triggeredAt: new Date().toISOString() };
    await this.save(data);
  }

  async updateToClosed(market, orderResult) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'EXIT_PENDING');
    if (!pos) return;
    pos.state = 'CLOSED';
    pos.exit = { ...(pos.exit || {}), orderUuid: orderResult.uuid, closedAt: new Date().toISOString() };
    await this.save(data);
  }

  /**
   * Record a partial exit (reduce-only) without closing the position.
   * - Used for aggressive SELL_PRESSURE_HIT partial sells.
   */
  async recordPartialExit(market, orderResult, reason, ratio, meta = {}) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'OPEN');
    if (!pos) return;

    pos.exit = pos.exit || {};
    pos.exit.partials = Array.isArray(pos.exit.partials) ? pos.exit.partials : [];
    pos.exit.partials.push({
      reason,
      ratio: Number(ratio || 0),
      orderUuid: orderResult?.uuid || null,
      volume: orderResult?.volume || null,
      createdAt: new Date().toISOString(),
      meta,
    });
    pos.exit.lastPartialAt = new Date().toISOString();
    pos.exit.lastPartialReason = reason;

    await this.save(data);
  }
}

module.exports = new PositionsRepo();
