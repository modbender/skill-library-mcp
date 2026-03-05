// ============================================================================
// RISK ALERT — Centralized Risk Alert Dispatcher
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class RiskAlert {
  constructor(whatsApp, telegram, config = {}) {
    this.whatsApp = whatsApp;
    this.telegram = telegram;
    this.config = config;
    this.alertHistory = [];
  }

  start() {
    // Critical risk events → both channels immediately
    bus.on(EVENTS.RISK_HALT, (data) => {
      this._dispatch('critical', `🛑 RISK HALT\nReason: ${data.reason}\nDaily PnL: ${data.dailyPnL}\nConsecutive Losses: ${data.consecutiveLosses}`);
    });

    bus.on(EVENTS.RISK_DAILY_LIMIT, (data) => {
      this._dispatch('critical', `⛔ DAILY LIMIT REACHED\nPnL: $${data.dailyPnL?.toFixed(2)}\nPercent: ${(data.percent * 100).toFixed(1)}%`);
    });

    bus.on(EVENTS.RISK_DRAWDOWN_WARN, (data) => {
      this._dispatch('warning', `⚠️ DRAWDOWN WARNING\nCurrent: ${data.drawdown}%\nPeak: $${data.peak}\nEquity: $${data.current}`);
    });

    bus.on(EVENTS.VOLATILITY_SPIKE, (data) => {
      if (data.severity === 'extreme') {
        this._dispatch('warning', `⚡ EXTREME VOLATILITY\n${data.symbol} ${data.timeframe}\nRange Ratio: ${data.rangeRatio}x ATR`);
      }
    });

    bus.on(EVENTS.MACRO_NEWS_BLOCK, (data) => {
      this._dispatch('info', `📰 NEWS BLOCK ACTIVE\nEvent: ${data.event}\n${data.reason}`);
    });

    bus.on(EVENTS.ORDER_ERROR, (data) => {
      this._dispatch('warning', `❌ ORDER ERROR\n${data.error}\nAction: ${data.action}`);
    });

    bus.on(EVENTS.SYSTEM_ERROR, (data) => {
      this._dispatch('critical', `💥 SYSTEM ERROR\nEngine: ${data.engine}\n${data.error}`);
    });

    console.log('[RISK-ALERT] Started');
  }

  _dispatch(severity, message) {
    const alert = {
      severity,
      message,
      timestamp: new Date().toISOString()
    };
    this.alertHistory.push(alert);
    if (this.alertHistory.length > 200) this.alertHistory = this.alertHistory.slice(-100);

    console.log(`[RISK-ALERT][${severity.toUpperCase()}]`, message.replace(/\n/g, ' | '));

    // Route by severity
    if (severity === 'critical') {
      if (this.whatsApp) this.whatsApp._send(message);
      if (this.telegram) this.telegram.send(message);
    } else if (severity === 'warning') {
      if (this.telegram) this.telegram.send(message);
    }
    // 'info' level: logged only
  }

  getRecentAlerts(count = 20) { return this.alertHistory.slice(-count); }
}

module.exports = RiskAlert;
