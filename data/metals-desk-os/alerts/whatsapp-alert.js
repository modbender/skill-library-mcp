// ============================================================================
// WHATSAPP ALERT — Trade & Risk Notifications via WhatsApp
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class WhatsAppAlert {
  constructor(config = {}) {
    this.config = {
      apiUrl: config.apiUrl || process.env.WHATSAPP_API_URL || '',
      token: config.token || process.env.WHATSAPP_TOKEN || '',
      phone: config.phone || process.env.WHATSAPP_PHONE || '',
      enabled: config.enabled !== undefined ? config.enabled : true,
      ...config
    };
  }

  start() {
    if (!this.config.enabled || !this.config.apiUrl) {
      console.log('[WHATSAPP-ALERT] Disabled or not configured');
      return;
    }

    bus.on(EVENTS.ALERT_TRADE, (data) => this.sendTradeAlert(data));
    bus.on(EVENTS.ALERT_RISK, (data) => this.sendRiskAlert(data));
    bus.on(EVENTS.PERFORMANCE_REPORT, (data) => this.sendPerformanceReport(data));
    bus.on(EVENTS.ORDER_FILLED, (data) => this.sendOrderFilled(data));

    console.log('[WHATSAPP-ALERT] Started');
  }

  async sendTradeAlert(data) {
    const msg = `🔔 *TRADE ${data.type || 'ALERT'}*\n` +
      `Pair: ${data.symbol}\n` +
      `Direction: ${data.direction}\n` +
      `Entry: ${data.entryPrice}\n` +
      `SL: ${data.stopLoss}\n` +
      `TP1: ${data.takeProfits?.[0]?.price || 'N/A'}\n` +
      `Risk: ${data.lots} lots\n` +
      `Time: ${new Date().toLocaleTimeString('en-GB', { timeZone: 'UTC' })} UTC`;
    await this._send(msg);
  }

  async sendRiskAlert(data) {
    const msg = `🛑 *RISK ALERT*\n` +
      `Type: ${data.type}\n` +
      `${data.message}\n` +
      `Time: ${new Date().toLocaleTimeString('en-GB', { timeZone: 'UTC' })} UTC`;
    await this._send(msg);
  }

  async sendOrderFilled(data) {
    const msg = `✅ *ORDER FILLED*\n` +
      `${data.symbol} ${data.direction?.toUpperCase()}\n` +
      `Entry: ${data.entryPrice}\n` +
      `Lots: ${data.lots}`;
    await this._send(msg);
  }

  async sendPerformanceReport(data) {
    const msg = `📊 *${(data.type || 'EOD').toUpperCase()} PERFORMANCE REPORT*\n` +
      `Generated: ${new Date().toISOString()}`;
    await this._send(msg);
  }

  async _send(message) {
    if (!this.config.enabled || !this.config.apiUrl) return;
    try {
      const axios = require('axios');
      await axios.post(this.config.apiUrl, {
        messaging_product: 'whatsapp',
        to: this.config.phone,
        type: 'text',
        text: { body: message }
      }, {
        headers: {
          'Authorization': `Bearer ${this.config.token}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });
    } catch (error) {
      console.error('[WHATSAPP-ALERT] Send failed:', error.message);
    }
  }
}

module.exports = WhatsAppAlert;
