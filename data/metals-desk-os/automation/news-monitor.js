// ============================================================================
// NEWS MONITOR — Economic Calendar & News Event Tracking
// ============================================================================
// Monitors upcoming high-impact events (FOMC, NFP, CPI, etc.)
// Blocks execution when high-impact news is within 20 minutes
// Emits: macro.news.alert, macro.news.block
// ============================================================================

const bus = require('./event-bus');
const { EVENTS } = bus;

class NewsMonitor {
  constructor(config = {}) {
    this.config = {
      blockMinutesBefore: config.blockMinutesBefore || 20,
      blockMinutesAfter: config.blockMinutesAfter || 10,
      checkIntervalMs: config.checkIntervalMs || 60000,
      newsApiKey: config.newsApiKey || process.env.NEWS_API_KEY || '',
      ...config
    };

    this.upcomingEvents = [];
    this.isBlocking = false;
    this.blockReason = null;
    this.checkInterval = null;

    // --- High Impact Events (static fallback calendar) ---
    this.highImpactKeywords = [
      'FOMC', 'Fed Rate Decision', 'Non-Farm Payrolls', 'NFP',
      'CPI', 'Core CPI', 'PPI', 'PCE', 'Core PCE',
      'GDP', 'Unemployment Rate', 'Jobless Claims',
      'ISM Manufacturing', 'ISM Services', 'Retail Sales',
      'Jackson Hole', 'ECB Rate Decision', 'BOE Rate Decision',
      'Powell Speech', 'Lagarde Speech'
    ];

    // Metals-specific events
    this.metalsImpactKeywords = [
      'Gold Reserve', 'PBOC Gold', 'Central Bank Gold',
      'Silver Fix', 'LBMA', 'COMEX Delivery',
      'Treasury Auction', 'Bond Auction'
    ];
  }

  // --- Start Monitoring ---
  start() {
    this.checkInterval = setInterval(() => this.evaluate(), this.config.checkIntervalMs);
    this.evaluate(); // Immediate check
    console.log('[NEWS-MONITOR] Started, blocking window:', this.config.blockMinutesBefore, 'min before,', this.config.blockMinutesAfter, 'min after');
  }

  stop() {
    if (this.checkInterval) clearInterval(this.checkInterval);
    console.log('[NEWS-MONITOR] Stopped');
  }

  // --- Load Calendar (API or manual) ---
  async loadCalendar() {
    try {
      // Try fetching from Forex Factory or similar API
      if (this.config.newsApiKey) {
        const axios = require('axios');
        // Example endpoint — replace with your actual calendar API
        const resp = await axios.get('https://nfs.faireconomy.media/ff_calendar_thisweek.json', {
          timeout: 5000
        });

        if (resp.data && Array.isArray(resp.data)) {
          this.upcomingEvents = resp.data
            .filter(e => e.impact === 'High' || e.impact === 'Holiday')
            .map(e => ({
              title: e.title,
              country: e.country,
              impact: e.impact,
              date: new Date(e.date),
              forecast: e.forecast,
              previous: e.previous,
              isMetalsRelevant: this._isMetalsRelevant(e.title)
            }));
          console.log('[NEWS-MONITOR] Loaded', this.upcomingEvents.length, 'high-impact events');
          return;
        }
      }
    } catch (error) {
      console.warn('[NEWS-MONITOR] Calendar API failed, using manual events:', error.message);
    }

    // Fallback: empty (user can manually add events)
    this.upcomingEvents = [];
  }

  // --- Add Manual Event ---
  addEvent(title, dateTime, impact = 'High') {
    this.upcomingEvents.push({
      title,
      date: new Date(dateTime),
      impact,
      country: 'USD',
      isMetalsRelevant: this._isMetalsRelevant(title)
    });
    this.upcomingEvents.sort((a, b) => a.date - b.date);
  }

  // --- Evaluate News Proximity ---
  evaluate() {
    const now = Date.now();
    const blockBefore = this.config.blockMinutesBefore * 60 * 1000;
    const blockAfter = this.config.blockMinutesAfter * 60 * 1000;

    let shouldBlock = false;
    let blockEvent = null;

    for (const event of this.upcomingEvents) {
      const eventTime = event.date.getTime();
      const timeDiff = eventTime - now;

      // Within blocking window
      if (timeDiff > -blockAfter && timeDiff < blockBefore) {
        shouldBlock = true;
        blockEvent = event;
        break;
      }

      // Alert: upcoming in next 60 minutes
      if (timeDiff > 0 && timeDiff < 60 * 60 * 1000) {
        const minutesAway = Math.round(timeDiff / 60000);
        bus.publish(EVENTS.MACRO_NEWS_ALERT, {
          event: event.title,
          minutesAway,
          impact: event.impact,
          isMetalsRelevant: event.isMetalsRelevant
        });
      }
    }

    // State change: blocking
    if (shouldBlock && !this.isBlocking) {
      this.isBlocking = true;
      this.blockReason = blockEvent;
      bus.publish(EVENTS.MACRO_NEWS_BLOCK, {
        event: blockEvent.title,
        reason: `High-impact event within ${this.config.blockMinutesBefore} minutes`,
        blockUntil: new Date(blockEvent.date.getTime() + blockAfter).toISOString()
      });
      bus.publish(EVENTS.ALERT_RISK, {
        type: 'news_block',
        message: `TRADING BLOCKED: ${blockEvent.title} imminent`
      });
    }

    // State change: unblocking
    if (!shouldBlock && this.isBlocking) {
      this.isBlocking = false;
      this.blockReason = null;
      bus.publish(EVENTS.ALERT_SYSTEM, {
        type: 'news_clear',
        message: 'News block lifted — trading resumed'
      });
    }

    // Clean up past events
    this.upcomingEvents = this.upcomingEvents.filter(e => e.date.getTime() > now - 3600000);

    return this.getState();
  }

  // --- Check if event is metals-relevant ---
  _isMetalsRelevant(title) {
    const combined = [...this.highImpactKeywords, ...this.metalsImpactKeywords];
    return combined.some(kw => title.toLowerCase().includes(kw.toLowerCase()));
  }

  // --- State ---
  getState() {
    return {
      isBlocking: this.isBlocking,
      blockReason: this.blockReason ? this.blockReason.title : null,
      upcomingCount: this.upcomingEvents.length,
      nextEvent: this.upcomingEvents.length > 0 ? {
        title: this.upcomingEvents[0].title,
        date: this.upcomingEvents[0].date.toISOString(),
        minutesAway: Math.round((this.upcomingEvents[0].date.getTime() - Date.now()) / 60000)
      } : null
    };
  }

  isTradingBlocked() {
    return this.isBlocking;
  }
}

module.exports = NewsMonitor;
