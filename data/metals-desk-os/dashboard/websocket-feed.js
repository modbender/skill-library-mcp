// ============================================================================
// WEBSOCKET FEED — Real-Time Dashboard Data Broadcaster
// ============================================================================
// Broadcasts system state to connected dashboard clients via WebSocket.
// Provides live: prices, bias, positions, risk, performance metrics.
// ============================================================================

const WebSocket = require('ws');
const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class WebSocketFeed {
  constructor(config = {}) {
    this.config = {
      port: config.port || 3078,
      broadcastIntervalMs: config.broadcastIntervalMs || 2000,
      ...config
    };

    this.wss = null;
    this.clients = new Set();
    this.latestState = {};
    this.broadcastInterval = null;
  }

  start(systemState) {
    this.wss = new WebSocket.Server({ port: this.config.port });

    this.wss.on('connection', (ws) => {
      this.clients.add(ws);
      console.log(`[WS-FEED] Client connected. Total: ${this.clients.size}`);

      // Send current state on connect
      ws.send(JSON.stringify({ type: 'snapshot', data: this.latestState }));

      ws.on('close', () => {
        this.clients.delete(ws);
      });

      ws.on('message', (msg) => {
        try {
          const cmd = JSON.parse(msg);
          if (cmd.action === 'setMode') {
            bus.setMode(cmd.mode);
          }
        } catch (e) { /* ignore */ }
      });
    });

    // Subscribe to key events and broadcast
    const broadcastEvents = [
      EVENTS.PRICE_UPDATE,
      EVENTS.BIAS_UPDATE,
      EVENTS.STRUCTURE_SHIFT,
      EVENTS.LIQUIDITY_SWEEP,
      EVENTS.MACRO_UPDATE,
      EVENTS.RISK_HALT,
      EVENTS.RISK_RESUME,
      EVENTS.ORDER_FILLED,
      EVENTS.ORDER_CLOSED,
      EVENTS.PERFORMANCE_UPDATE,
      EVENTS.VOLATILITY_UPDATE,
      EVENTS.SESSION_CHANGE,
      EVENTS.SYSTEM_HEARTBEAT
    ];

    broadcastEvents.forEach(event => {
      bus.on(event, (data) => {
        this._broadcast({ type: 'event', event, data, timestamp: Date.now() });
      });
    });

    // Periodic full state broadcast
    this.broadcastInterval = setInterval(() => {
      if (systemState) {
        this.latestState = typeof systemState === 'function' ? systemState() : systemState;
        this._broadcast({ type: 'state', data: this.latestState });
      }
    }, this.config.broadcastIntervalMs);

    console.log(`[WS-FEED] Started on port ${this.config.port}`);
  }

  stop() {
    if (this.broadcastInterval) clearInterval(this.broadcastInterval);
    if (this.wss) this.wss.close();
    this.clients.clear();
  }

  _broadcast(data) {
    const msg = JSON.stringify(data);
    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(msg);
      }
    }
  }

  getClientCount() { return this.clients.size; }
}

module.exports = WebSocketFeed;
