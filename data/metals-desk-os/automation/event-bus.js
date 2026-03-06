// ============================================================================
// EVENT BUS — Central Nervous System of metals-desk-os
// ============================================================================
// All engines communicate through this event-driven bus.
// Events flow: PRICE → STRUCTURE → LIQUIDITY → MACRO → RISK → EXECUTION
// ============================================================================

const EventEmitter = require('eventemitter3');
const winston = require('winston');
const fs = require('fs');
const path = require('path');

// --- Logger Setup ---
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      return `[${timestamp}] [${level.toUpperCase()}] ${message} ${Object.keys(meta).length ? JSON.stringify(meta) : ''}`;
    })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: path.join(__dirname, '../data/desk-os.log'), maxsize: 5242880, maxFiles: 5 })
  ]
});

class EventBus extends EventEmitter {
  constructor() {
    super();
    this.eventLog = [];
    this.maxLogSize = 10000;
    this.started = false;
    this.systemMode = 1; // 1=Advisory, 2=Semi, 3=Full, 4=RiskOff

    // --- Register all system events ---
    this.EVENTS = {
      // Price events
      PRICE_UPDATE:        'price.update',
      PRICE_TICK:          'price.tick',

      // Session events
      SESSION_OPEN:        'session.open',
      SESSION_CLOSE:       'session.close',
      SESSION_CHANGE:      'session.change',

      // Structure events
      STRUCTURE_HH:        'structure.hh',
      STRUCTURE_HL:        'structure.hl',
      STRUCTURE_LH:        'structure.lh',
      STRUCTURE_LL:        'structure.ll',
      STRUCTURE_BOS:       'structure.bos',
      STRUCTURE_CHOCH:     'structure.choch',
      STRUCTURE_SHIFT:     'structure.shift',
      STRUCTURE_COMPRESSION: 'structure.compression',
      STRUCTURE_EXPANSION: 'structure.expansion',

      // Liquidity events
      LIQUIDITY_SWEEP:     'liquidity.sweep',
      LIQUIDITY_POOL:      'liquidity.pool.detected',
      LIQUIDITY_EQH:       'liquidity.equal.highs',
      LIQUIDITY_EQL:       'liquidity.equal.lows',

      // Bias events
      BIAS_UPDATE:         'bias.update',
      BIAS_FLIP:           'bias.flip',
      BIAS_CONFLICT:       'bias.conflict',

      // Macro events
      MACRO_UPDATE:        'macro.update',
      MACRO_NEWS_ALERT:    'macro.news.alert',
      MACRO_NEWS_BLOCK:    'macro.news.block',
      MACRO_DXY_SHIFT:     'macro.dxy.shift',

      // Risk events
      RISK_CHECK_PASS:     'risk.check.pass',
      RISK_CHECK_FAIL:     'risk.check.fail',
      RISK_HALT:           'risk.halt',
      RISK_RESUME:         'risk.resume',
      RISK_DRAWDOWN_WARN:  'risk.drawdown.warn',
      RISK_DAILY_LIMIT:    'risk.daily.limit',

      // Volatility events
      VOLATILITY_UPDATE:   'volatility.update',
      VOLATILITY_SPIKE:    'volatility.spike',
      VOLATILITY_LOW:      'volatility.low',

      // Execution events
      EXECUTION_SIGNAL:    'execution.signal',
      EXECUTION_ENTRY:     'execution.entry',
      EXECUTION_REJECTED:  'execution.rejected',

      // Broker/Order events
      ORDER_SENT:          'order.sent',
      ORDER_FILLED:        'order.filled',
      ORDER_REJECTED:      'order.rejected',
      ORDER_PARTIAL_CLOSE: 'order.partial.close',
      ORDER_MOVE_BE:       'order.move.breakeven',
      ORDER_TRAIL:         'order.trail',
      ORDER_CLOSED:        'order.closed',
      ORDER_ERROR:         'order.error',

      // Performance events
      PERFORMANCE_UPDATE:  'performance.update',
      PERFORMANCE_REPORT:  'performance.report',

      // Alert events
      ALERT_TRADE:         'alert.trade',
      ALERT_RISK:          'alert.risk',
      ALERT_SYSTEM:        'alert.system',

      // System events
      SYSTEM_START:        'system.start',
      SYSTEM_STOP:         'system.stop',
      SYSTEM_MODE_CHANGE:  'system.mode.change',
      SYSTEM_ERROR:        'system.error',
      SYSTEM_HEARTBEAT:    'system.heartbeat'
    };

    this._setupInternalListeners();
  }

  // --- Internal Listeners ---
  _setupInternalListeners() {
    // Log every event
    const allEvents = Object.values(this.EVENTS);
    allEvents.forEach(eventName => {
      this.on(eventName, (data) => {
        this._logEvent(eventName, data);
      });
    });

    // Safety: halt on critical events
    this.on(this.EVENTS.RISK_HALT, (data) => {
      logger.warn('RISK HALT TRIGGERED', data);
      this.systemMode = 4; // Force Risk-Off
    });

    this.on(this.EVENTS.SYSTEM_ERROR, (data) => {
      logger.error('SYSTEM ERROR', data);
    });
  }

  // --- Event Logging ---
  _logEvent(eventName, data) {
    const entry = {
      timestamp: new Date().toISOString(),
      event: eventName,
      data: data || {}
    };
    this.eventLog.push(entry);
    if (this.eventLog.length > this.maxLogSize) {
      this.eventLog = this.eventLog.slice(-this.maxLogSize / 2);
    }
    logger.info(`EVENT: ${eventName}`, { data: typeof data === 'object' ? JSON.stringify(data).substring(0, 200) : data });
  }

  // --- Publish (typed emit) ---
  publish(eventName, data = {}) {
    const enrichedData = {
      ...data,
      _ts: Date.now(),
      _mode: this.systemMode
    };
    this.emit(eventName, enrichedData);
  }

  // --- System Mode ---
  setMode(mode) {
    const oldMode = this.systemMode;
    this.systemMode = mode;
    const modeNames = { 1: 'Advisory', 2: 'Semi-Automated', 3: 'Fully-Automated', 4: 'Risk-Off' };
    logger.info(`MODE CHANGE: ${modeNames[oldMode]} → ${modeNames[mode]}`);
    this.publish(this.EVENTS.SYSTEM_MODE_CHANGE, { oldMode, newMode: mode, modeName: modeNames[mode] });
  }

  getMode() {
    return this.systemMode;
  }

  isAutoMode() {
    return this.systemMode === 3;
  }

  isTradingAllowed() {
    return this.systemMode === 2 || this.systemMode === 3;
  }

  // --- Get Recent Events ---
  getRecentEvents(count = 50, filterType = null) {
    let events = this.eventLog;
    if (filterType) {
      events = events.filter(e => e.event.startsWith(filterType));
    }
    return events.slice(-count);
  }

  // --- Health Check ---
  getHealth() {
    return {
      started: this.started,
      mode: this.systemMode,
      totalEvents: this.eventLog.length,
      lastEvent: this.eventLog.length > 0 ? this.eventLog[this.eventLog.length - 1] : null,
      listenerCount: this.eventNames().length,
      uptime: process.uptime()
    };
  }
}

// Singleton
const bus = new EventBus();

module.exports = bus;
module.exports.EventBus = EventBus;
module.exports.EVENTS = bus.EVENTS;
