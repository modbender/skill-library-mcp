// ============================================================================
// ORDER MANAGER — High-Level Order Orchestration
// ============================================================================
// Bridges ExecutionEngine signals with MT5Connector.
// Handles the full lifecycle: signal → validate → execute → manage → close
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class OrderManager {
  constructor(mt5Connector, riskGuard, performanceEngine, config = {}) {
    this.mt5 = mt5Connector;
    this.riskGuard = riskGuard;
    this.performance = performanceEngine;
    this.config = config;
    this.orderHistory = [];
  }

  // --- Start Listening for Execution Signals ---
  start() {
    // Auto-execute in Mode 3
    bus.on(EVENTS.EXECUTION_ENTRY, async (signal) => {
      if (!bus.isAutoMode()) return;
      await this.executeSignal(signal);
    });

    // Handle order closed events
    bus.on(EVENTS.ORDER_CLOSED, (data) => {
      this._onOrderClosed(data);
    });

    // Listen for structure shifts to trail positions
    bus.on(EVENTS.STRUCTURE_SHIFT, (data) => {
      this._onStructureShift(data);
    });

    console.log('[ORDER-MANAGER] Started');
  }

  // --- Execute a Signal ---
  async executeSignal(signal) {
    try {
      console.log(`[ORDER-MANAGER] Executing ${signal.direction} ${signal.symbol} @ ${signal.entry}`);

      const result = await this.mt5.openPosition({
        symbol: signal.symbol,
        direction: signal.direction,
        lots: signal.positionSize?.lots || 0.01,
        stopLoss: signal.sl,
        takeProfits: signal.tp,
        comment: `MDO|${signal.direction}|C${signal.conviction}`
      });

      if (result.error) {
        bus.publish(EVENTS.ORDER_REJECTED, { signal, error: result.error });
        return result;
      }

      // Track in history
      this.orderHistory.push({
        signal,
        order: result,
        openTime: new Date().toISOString()
      });

      return result;
    } catch (error) {
      bus.publish(EVENTS.ORDER_ERROR, { error: error.message, signal });
      return { error: error.message };
    }
  }

  // --- On Order Closed ---
  _onOrderClosed(data) {
    // Find in history and record performance
    const historyEntry = this.orderHistory.find(h =>
      h.order && (h.order.positionId === data.positionId || h.order.orderId === data.positionId)
    );

    if (historyEntry && data.pnl !== undefined) {
      const entryPrice = historyEntry.order.entryPrice;
      const stopDistance = Math.abs(entryPrice - historyEntry.signal.sl);
      const rMultiple = stopDistance > 0 ? data.pnl / (stopDistance * (historyEntry.signal.positionSize?.pipValue || 1)) : 0;

      this.performance.recordTrade({
        symbol: historyEntry.signal.symbol,
        direction: historyEntry.signal.direction,
        entryPrice,
        exitPrice: data.exitPrice,
        stopLoss: historyEntry.signal.sl,
        lots: historyEntry.signal.positionSize?.lots || 0.01,
        pnl: data.pnl,
        rMultiple,
        session: historyEntry.signal.checks?.session?.current || 'unknown',
        openTime: historyEntry.openTime,
        closeTime: new Date().toISOString(),
        closeReason: data.reason || 'unknown'
      });
    }
  }

  // --- On Structure Shift: Trail Stops ---
  async _onStructureShift(data) {
    if (!data.symbol) return;
    const openOrders = this.mt5.getOpenOrders().filter(o => o.symbol === data.symbol && o.status === 'open');

    for (const order of openOrders) {
      // Trail longs on bullish structure (use HL as new SL)
      if (order.direction === 'long' && data.newTrend === 'bullish' && data.level) {
        await this.riskGuard.trailByStructure(order.positionId || order.orderId, data.level);
      }
      // Trail shorts on bearish structure (use LH as new SL)
      if (order.direction === 'short' && data.newTrend === 'bearish' && data.level) {
        await this.riskGuard.trailByStructure(order.positionId || order.orderId, data.level);
      }
    }
  }

  getOrderHistory(count = 20) { return this.orderHistory.slice(-count); }
}

module.exports = OrderManager;
