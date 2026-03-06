// ============================================================================
// MT5 CONNECTOR — MetaAPI Broker Integration
// ============================================================================
// Capabilities: Open position, Partial close, Move to break-even,
//               Trail by structure, Close all on risk event
// Failsafe: API error → cancel retry, Order rejected → alert + log
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class MT5Connector {
  constructor(config = {}) {
    this.config = {
      metaApiToken: config.metaApiToken || process.env.METAAPI_TOKEN || '',
      accountId: config.accountId || process.env.MT5_ACCOUNT_ID || '',
      maxRetries: config.maxRetries || 1,  // Failsafe: minimal retries
      retryDelayMs: config.retryDelayMs || 2000,
      slippage: config.slippage || 10,     // Max slippage in points
      ...config
    };

    this.connection = null;
    this.account = null;
    this.connected = false;
    this.openOrders = new Map();
  }

  // --- Initialize Connection ---
  async connect() {
    try {
      const MetaApi = require('metaapi.cloud-sdk').default;
      const api = new MetaApi(this.config.metaApiToken);
      this.account = await api.metatraderAccountApi.getAccount(this.config.accountId);

      if (this.account.state !== 'DEPLOYED') {
        await this.account.deploy();
        await this.account.waitDeployed();
      }

      this.connection = this.account.getRPCConnection();
      await this.connection.connect();
      await this.connection.waitSynchronized();
      this.connected = true;

      bus.publish(EVENTS.ALERT_SYSTEM, { type: 'broker', message: 'MT5 Connector: Connected' });
      return true;
    } catch (error) {
      console.error('[MT5-CONNECTOR] Connection failed:', error.message);
      this.connected = false;
      bus.publish(EVENTS.ORDER_ERROR, { error: error.message, action: 'connect' });
      return false;
    }
  }

  // --- Open Position ---
  async openPosition(params) {
    const { symbol, direction, lots, stopLoss, takeProfits, comment } = params;

    if (!this.connected) {
      const err = { error: 'Not connected to MT5', params };
      bus.publish(EVENTS.ORDER_ERROR, err);
      return err;
    }

    try {
      const actionType = direction === 'long' ? 'ORDER_TYPE_BUY' : 'ORDER_TYPE_SELL';

      // Use TP1 as the initial TP (we manage partials ourselves)
      const tp1 = takeProfits && takeProfits.length > 0 ? takeProfits[0].price : undefined;

      const result = await this.connection.createMarketBuyOrder(
        symbol,
        lots,
        stopLoss,
        tp1,
        {
          comment: comment || 'metals-desk-os',
          clientId: `MDO_${Date.now()}`,
          slippage: this.config.slippage
        }
      );

      if (result && result.orderId) {
        const order = {
          orderId: result.orderId,
          positionId: result.positionId,
          symbol,
          direction,
          lots,
          entryPrice: result.openPrice,
          stopLoss,
          takeProfits,
          currentTP: 0, // Index of current TP target
          openTime: new Date().toISOString(),
          status: 'open',
          partialCloses: []
        };

        this.openOrders.set(result.positionId || result.orderId, order);

        bus.publish(EVENTS.ORDER_FILLED, order);
        bus.publish(EVENTS.ALERT_TRADE, {
          type: 'TRADE_OPENED',
          ...order
        });

        return order;
      } else {
        const rejection = { error: 'Order not filled', result };
        bus.publish(EVENTS.ORDER_REJECTED, rejection);
        return rejection;
      }
    } catch (error) {
      const err = { error: error.message, action: 'openPosition', params };
      bus.publish(EVENTS.ORDER_ERROR, err);
      bus.publish(EVENTS.ALERT_RISK, { type: 'ORDER_ERROR', message: `Order failed: ${error.message}` });
      return err;
    }
  }

  // --- Partial Close ---
  async partialClose(positionId, closePercent) {
    try {
      const order = this.openOrders.get(positionId);
      if (!order) return { error: 'Position not found' };

      const closeLots = parseFloat((order.lots * closePercent).toFixed(2));
      if (closeLots < 0.01) return { error: 'Close size too small' };

      const result = await this.connection.closePositionPartially(positionId, closeLots);

      order.lots -= closeLots;
      order.partialCloses.push({
        lots: closeLots,
        time: new Date().toISOString(),
        percent: closePercent
      });

      bus.publish(EVENTS.ORDER_PARTIAL_CLOSE, {
        positionId,
        closedLots: closeLots,
        remainingLots: order.lots,
        tpLevel: order.currentTP
      });

      return { success: true, closedLots: closeLots, remainingLots: order.lots };
    } catch (error) {
      bus.publish(EVENTS.ORDER_ERROR, { error: error.message, action: 'partialClose', positionId });
      return { error: error.message };
    }
  }

  // --- Move Stop to Break-Even ---
  async moveToBreakeven(positionId, buffer = 1) {
    try {
      const order = this.openOrders.get(positionId);
      if (!order) return { error: 'Position not found' };

      const newSL = order.direction === 'long'
        ? order.entryPrice + buffer
        : order.entryPrice - buffer;

      await this.connection.modifyPosition(positionId, newSL, order.takeProfits?.[order.currentTP]?.price);

      order.stopLoss = newSL;

      bus.publish(EVENTS.ORDER_MOVE_BE, {
        positionId,
        newSL,
        entryPrice: order.entryPrice
      });

      return { success: true, newSL };
    } catch (error) {
      bus.publish(EVENTS.ORDER_ERROR, { error: error.message, action: 'moveToBreakeven', positionId });
      return { error: error.message };
    }
  }

  // --- Trail Stop by Structure ---
  async trailStop(positionId, newStopLevel) {
    try {
      const order = this.openOrders.get(positionId);
      if (!order) return { error: 'Position not found' };

      // Only trail in favorable direction
      if (order.direction === 'long' && newStopLevel <= order.stopLoss) return { skip: true };
      if (order.direction === 'short' && newStopLevel >= order.stopLoss) return { skip: true };

      await this.connection.modifyPosition(positionId, newStopLevel);

      const oldSL = order.stopLoss;
      order.stopLoss = newStopLevel;

      bus.publish(EVENTS.ORDER_TRAIL, {
        positionId,
        oldSL,
        newSL: newStopLevel,
        direction: order.direction
      });

      return { success: true, newSL: newStopLevel };
    } catch (error) {
      bus.publish(EVENTS.ORDER_ERROR, { error: error.message, action: 'trailStop', positionId });
      return { error: error.message };
    }
  }

  // --- Close All Positions (Risk Emergency) ---
  async closeAll(reason = 'risk_event') {
    const results = [];
    for (const [posId, order] of this.openOrders) {
      try {
        await this.connection.closePosition(posId);
        order.status = 'closed';
        order.closeReason = reason;
        results.push({ positionId: posId, status: 'closed' });
        bus.publish(EVENTS.ORDER_CLOSED, { positionId: posId, reason });
      } catch (error) {
        results.push({ positionId: posId, error: error.message });
      }
    }
    this.openOrders.clear();
    bus.publish(EVENTS.ALERT_RISK, { type: 'ALL_CLOSED', reason, count: results.length });
    return results;
  }

  // --- Get Account Info ---
  async getAccountInfo() {
    if (!this.connected) return null;
    try {
      const info = await this.connection.getAccountInformation();
      return {
        balance: info.balance,
        equity: info.equity,
        margin: info.margin,
        freeMargin: info.freeMargin,
        leverage: info.leverage,
        currency: info.currency
      };
    } catch (error) {
      return null;
    }
  }

  // --- Get Open Positions ---
  async getPositions() {
    if (!this.connected) return [];
    try {
      return await this.connection.getPositions();
    } catch (error) {
      return [];
    }
  }

  getOpenOrders() { return Array.from(this.openOrders.values()); }
  isConnected() { return this.connected; }
}

module.exports = MT5Connector;
