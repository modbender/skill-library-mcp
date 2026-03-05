// ============================================================================
// RISK GUARD — Active Position Monitoring & Management
// ============================================================================
// Monitors live positions for: TP hits, partial close triggers,
// break-even moves, trailing stops, and emergency closes.
// Works with MT5Connector and emits events on state changes.
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class RiskGuard {
  constructor(mt5Connector, config = {}) {
    this.mt5 = mt5Connector;
    this.config = {
      checkIntervalMs: config.checkIntervalMs || 2000,
      breakEvenBuffer: config.breakEvenBuffer || { XAUUSD: 2.0, XAGUSD: 0.15 },
      trailByStructure: config.trailByStructure || true,
      moveToBreakevenAtTP: config.moveToBreakevenAtTP || 1, // Move SL to BE when TP1 hit
      ...config
    };

    this.monitorInterval = null;
    this.positions = new Map(); // Track managed positions
  }

  // --- Start Monitoring ---
  start() {
    this.monitorInterval = setInterval(() => this.checkPositions(), this.config.checkIntervalMs);

    // Listen for risk halt → close all
    bus.on(EVENTS.RISK_HALT, async (data) => {
      console.log('[RISK-GUARD] Risk halt detected, closing all positions');
      await this.mt5.closeAll(data.reason || 'risk_halt');
    });

    // Listen for price updates for trailing
    bus.on(EVENTS.PRICE_UPDATE, (data) => this._onPriceUpdate(data));

    console.log('[RISK-GUARD] Started monitoring every', this.config.checkIntervalMs, 'ms');
  }

  stop() {
    if (this.monitorInterval) clearInterval(this.monitorInterval);
    console.log('[RISK-GUARD] Stopped');
  }

  // --- Check All Open Positions ---
  async checkPositions() {
    const openOrders = this.mt5.getOpenOrders();

    for (const order of openOrders) {
      if (order.status !== 'open') continue;
      // Sync with internal tracking
      this.positions.set(order.positionId || order.orderId, order);
    }
  }

  // --- On Price Update: Check TP Levels and Trail ---
  async _onPriceUpdate(data) {
    if (!data.price) return;
    const { symbol, price } = data;
    const currentPrice = price.mid;

    const openOrders = this.mt5.getOpenOrders();

    for (const order of openOrders) {
      if (order.symbol !== symbol || order.status !== 'open') continue;
      if (!order.takeProfits || order.takeProfits.length === 0) continue;

      const posId = order.positionId || order.orderId;

      // Check each TP level
      for (let i = order.currentTP; i < order.takeProfits.length; i++) {
        const tp = order.takeProfits[i];
        const hit = order.direction === 'long'
          ? currentPrice >= tp.price
          : currentPrice <= tp.price;

        if (hit) {
          // Partial close at this TP
          const closePercent = tp.closePercent || 0.33;
          console.log(`[RISK-GUARD] TP${tp.level} hit for ${posId}, closing ${(closePercent * 100).toFixed(0)}%`);

          if (bus.isAutoMode() || bus.getMode() === 2) {
            await this.mt5.partialClose(posId, closePercent);
          }

          order.currentTP = i + 1;

          // Move to BE at TP1
          if (i + 1 === this.config.moveToBreakevenAtTP) {
            const buffer = this.config.breakEvenBuffer[symbol] || 1.0;
            if (bus.isAutoMode() || bus.getMode() === 2) {
              await this.mt5.moveToBreakeven(posId, buffer);
            }
          }
        }
      }
    }
  }

  // --- Trail Stop by Structure Level ---
  async trailByStructure(positionId, structureLevel) {
    if (!this.config.trailByStructure) return;

    const order = this.mt5.getOpenOrders().find(o =>
      (o.positionId || o.orderId) === positionId
    );
    if (!order || order.currentTP < 1) return; // Only trail after first TP

    const buffer = this.config.breakEvenBuffer[order.symbol] || 1.0;
    const newSL = order.direction === 'long'
      ? structureLevel - buffer
      : structureLevel + buffer;

    if (bus.isAutoMode()) {
      await this.mt5.trailStop(positionId, newSL);
    }
  }

  // --- Emergency Close All ---
  async emergencyClose(reason) {
    return await this.mt5.closeAll(reason);
  }

  getTrackedPositions() {
    return Array.from(this.positions.values());
  }
}

module.exports = RiskGuard;
