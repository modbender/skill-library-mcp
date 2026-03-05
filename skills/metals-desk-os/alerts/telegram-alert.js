// ============================================================================
// TELEGRAM ALERT — Trade & Risk Notifications via Telegram Bot
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class TelegramAlert {
  constructor(config = {}) {
    this.config = {
      botToken: config.botToken || process.env.TELEGRAM_BOT_TOKEN || '',
      chatId: config.chatId || process.env.TELEGRAM_CHAT_ID || '',
      enabled: config.enabled !== undefined ? config.enabled : true,
      ...config
    };
  }

  start() {
    if (!this.config.enabled || !this.config.botToken) {
      console.log('[TELEGRAM-ALERT] Disabled or not configured');
      return;
    }

    bus.on(EVENTS.ALERT_TRADE, (data) => this.send(this._formatTrade(data)));
    bus.on(EVENTS.ALERT_RISK, (data) => this.send(this._formatRisk(data)));
    bus.on(EVENTS.EXECUTION_SIGNAL, (data) => this.send(this._formatSignal(data)));
    bus.on(EVENTS.PERFORMANCE_REPORT, (data) => this.send(`📊 Performance report: ${data.type}`));
    bus.on(EVENTS.RISK_HALT, (data) => this.send(`🛑 RISK HALT: ${data.reason}`));

    console.log('[TELEGRAM-ALERT] Started');
  }

  _formatTrade(data) {
    return `🔔 <b>TRADE OPENED</b>\n` +
      `Pair: ${data.symbol}\n` +
      `Direction: ${data.direction}\n` +
      `Entry: ${data.entryPrice}\n` +
      `SL: ${data.stopLoss}\n` +
      `Lots: ${data.lots}`;
  }

  _formatRisk(data) {
    return `🛑 <b>${data.type}</b>\n${data.message}`;
  }

  _formatSignal(data) {
    return `📡 <b>SIGNAL</b>\n` +
      `${data.symbol} ${data.direction?.toUpperCase()}\n` +
      `Entry: ${data.entry}\n` +
      `SL: ${data.sl}\n` +
      `TPs: ${data.tp?.map(t => t.price).join(' / ')}\n` +
      `Conviction: ${data.conviction}/100`;
  }

  async send(text) {
    if (!this.config.enabled || !this.config.botToken) return;
    try {
      const axios = require('axios');
      await axios.post(`https://api.telegram.org/bot${this.config.botToken}/sendMessage`, {
        chat_id: this.config.chatId,
        text,
        parse_mode: 'HTML'
      }, { timeout: 10000 });
    } catch (error) {
      console.error('[TELEGRAM-ALERT] Send failed:', error.message);
    }
  }
}

module.exports = TelegramAlert;
