// ============================================================================
// SESSION ENGINE — Trading Session Awareness
// ============================================================================
// Tracks Asian, London, and New York sessions.
// Emits: session.open, session.close, session.change
// Key for execution filtering: only trade during London + NY overlap
// ============================================================================

const bus = require('./event-bus');
const { EVENTS } = bus;

class SessionEngine {
  constructor(config = {}) {
    this.config = {
      // Session times in UTC
      sessions: {
        Asian:  { open: 0,  close: 8,  label: 'Asian',  color: '#FFD700' },
        London: { open: 7,  close: 16, label: 'London', color: '#4169E1' },
        NewYork: { open: 12, close: 21, label: 'New York', color: '#DC143C' }
      },
      // Key trading windows
      killZones: {
        AsianKZ:     { start: 0,  end: 3,   label: 'Asian Kill Zone' },
        LondonOpen:  { start: 7,  end: 10,  label: 'London Open KZ' },
        NYOpen:      { start: 12, end: 15,  label: 'NY Open KZ' },
        LondonClose: { start: 14, end: 16,  label: 'London Close KZ' }
      },
      ...config
    };

    this.currentSession = null;
    this.currentKillZone = null;
    this.sessionHighs = {};  // { London: { XAUUSD: 5045 } }
    this.sessionLows = {};
    this.previousDayHigh = {};
    this.previousDayLow = {};
    this.previousWeekHigh = {};
    this.previousWeekLow = {};
    this.checkInterval = null;
  }

  // --- Start Session Monitoring ---
  start() {
    // Check every 30 seconds
    this.checkInterval = setInterval(() => this.evaluate(), 30000);
    this.evaluate(); // Immediate check

    // Listen for price updates to track session highs/lows
    bus.on(EVENTS.PRICE_UPDATE, (data) => this._trackSessionHL(data));

    console.log('[SESSION-ENGINE] Started');
  }

  stop() {
    if (this.checkInterval) clearInterval(this.checkInterval);
    console.log('[SESSION-ENGINE] Stopped');
  }

  // --- Evaluate Current Session ---
  evaluate() {
    const now = new Date();
    const utcHour = now.getUTCHours();
    const utcMinute = now.getUTCMinutes();
    const utcDecimal = utcHour + utcMinute / 60;

    // Determine active sessions
    const activeSessions = [];
    for (const [name, sess] of Object.entries(this.config.sessions)) {
      if (utcDecimal >= sess.open && utcDecimal < sess.close) {
        activeSessions.push(name);
      }
    }

    // Determine active kill zones
    const activeKillZones = [];
    for (const [name, kz] of Object.entries(this.config.killZones)) {
      if (utcDecimal >= kz.start && utcDecimal < kz.end) {
        activeKillZones.push({ name, label: kz.label });
      }
    }

    // Primary session (priority: NY > London > Asian)
    let primarySession = null;
    if (activeSessions.includes('NewYork')) primarySession = 'NewYork';
    else if (activeSessions.includes('London')) primarySession = 'London';
    else if (activeSessions.includes('Asian')) primarySession = 'Asian';

    // Detect session change
    if (primarySession !== this.currentSession) {
      const oldSession = this.currentSession;

      // Close old session
      if (oldSession) {
        bus.publish(EVENTS.SESSION_CLOSE, {
          session: oldSession,
          highs: this.sessionHighs[oldSession] || {},
          lows: this.sessionLows[oldSession] || {}
        });
      }

      // Open new session
      this.currentSession = primarySession;
      if (primarySession) {
        this.sessionHighs[primarySession] = {};
        this.sessionLows[primarySession] = {};
        bus.publish(EVENTS.SESSION_OPEN, { session: primarySession, activeSessions, activeKillZones });
      }

      bus.publish(EVENTS.SESSION_CHANGE, {
        from: oldSession,
        to: primarySession,
        activeSessions,
        activeKillZones,
        isOverlap: activeSessions.length > 1,
        utcHour,
        utcMinute
      });
    }

    // Update kill zone
    this.currentKillZone = activeKillZones.length > 0 ? activeKillZones[0] : null;

    return this.getState();
  }

  // --- Track Session Highs/Lows ---
  _trackSessionHL(data) {
    if (!data.price || !this.currentSession) return;

    const symbol = data.symbol || data.price.symbol;
    const mid = data.price.mid;

    if (!this.sessionHighs[this.currentSession]) this.sessionHighs[this.currentSession] = {};
    if (!this.sessionLows[this.currentSession]) this.sessionLows[this.currentSession] = {};

    const currHigh = this.sessionHighs[this.currentSession][symbol];
    const currLow = this.sessionLows[this.currentSession][symbol];

    if (!currHigh || mid > currHigh) this.sessionHighs[this.currentSession][symbol] = mid;
    if (!currLow || mid < currLow) this.sessionLows[this.currentSession][symbol] = mid;
  }

  // --- Update Previous Day/Week Levels ---
  updateDailyLevels(symbol, high, low) {
    this.previousDayHigh[symbol] = high;
    this.previousDayLow[symbol] = low;
  }

  updateWeeklyLevels(symbol, high, low) {
    this.previousWeekHigh[symbol] = high;
    this.previousWeekLow[symbol] = low;
  }

  // --- State Getters ---
  getState() {
    return {
      currentSession: this.currentSession,
      currentKillZone: this.currentKillZone,
      sessionHighs: this.sessionHighs,
      sessionLows: this.sessionLows,
      previousDayHigh: this.previousDayHigh,
      previousDayLow: this.previousDayLow,
      previousWeekHigh: this.previousWeekHigh,
      previousWeekLow: this.previousWeekLow,
      isLondon: this.currentSession === 'London',
      isNY: this.currentSession === 'NewYork',
      isAsian: this.currentSession === 'Asian',
      isKillZone: this.currentKillZone !== null,
      isLondonNYOverlap: this.currentSession === 'NewYork' && this._isInRange(12, 16)
    };
  }

  isValidTradingSession() {
    return this.currentSession === 'London' || this.currentSession === 'NewYork';
  }

  isKillZoneActive() {
    return this.currentKillZone !== null;
  }

  _isInRange(start, end) {
    const h = new Date().getUTCHours();
    return h >= start && h < end;
  }

  // --- Get Key Levels ---
  getKeyLevels(symbol) {
    const levels = [];

    // Previous day
    if (this.previousDayHigh[symbol]) levels.push({ type: 'PDH', price: this.previousDayHigh[symbol] });
    if (this.previousDayLow[symbol]) levels.push({ type: 'PDL', price: this.previousDayLow[symbol] });

    // Previous week
    if (this.previousWeekHigh[symbol]) levels.push({ type: 'PWH', price: this.previousWeekHigh[symbol] });
    if (this.previousWeekLow[symbol]) levels.push({ type: 'PWL', price: this.previousWeekLow[symbol] });

    // Session highs/lows
    for (const [session, highs] of Object.entries(this.sessionHighs)) {
      if (highs[symbol]) levels.push({ type: `${session}H`, price: highs[symbol] });
    }
    for (const [session, lows] of Object.entries(this.sessionLows)) {
      if (lows[symbol]) levels.push({ type: `${session}L`, price: lows[symbol] });
    }

    return levels.sort((a, b) => b.price - a.price);
  }
}

module.exports = SessionEngine;
