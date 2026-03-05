// ============================================================================
// MACRO ENGINE — DXY, Yields, Risk Sentiment, News Proximity
// ============================================================================
const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class MacroEngine {
  constructor(config = {}) {
    this.config = {
      dxyBearishThreshold: -0.3,
      dxyBullishThreshold: 0.3,
      yieldDropThreshold: -0.02,
      yieldRiseThreshold: 0.02,
      newsBlockMinutes: 20,
      ...config
    };
    this.state = {
      dxy: { value: null, change: 0, trend: 'neutral', lastUpdate: null },
      us10y: { value: null, change: 0, trend: 'neutral', lastUpdate: null },
      riskSentiment: 'neutral',
      vix: { value: null, trend: 'neutral' },
      macro_bias: 'neutral',
      macro_risk: 'low',
      newsProximity: false,
      newsBlockActive: false,
      lastUpdate: null,
      components: {}
    };
  }

  updateDXY(value, previousValue) {
    const change = previousValue ? ((value - previousValue) / previousValue) * 100 : 0;
    let trend = 'neutral';
    if (change < this.config.dxyBearishThreshold) trend = 'falling';
    if (change > this.config.dxyBullishThreshold) trend = 'rising';
    const prevTrend = this.state.dxy.trend;
    this.state.dxy = { value: parseFloat(value.toFixed(3)), change: parseFloat(change.toFixed(3)), trend, lastUpdate: new Date().toISOString() };
    if (prevTrend !== trend && trend !== 'neutral') {
      bus.publish(EVENTS.MACRO_DXY_SHIFT, { from: prevTrend, to: trend, value, change });
    }
    this._recalculate();
  }

  updateYield(value, previousValue) {
    const change = previousValue ? value - previousValue : 0;
    let trend = 'neutral';
    if (change < this.config.yieldDropThreshold) trend = 'falling';
    if (change > this.config.yieldRiseThreshold) trend = 'rising';
    this.state.us10y = { value: parseFloat(value.toFixed(3)), change: parseFloat(change.toFixed(4)), trend, lastUpdate: new Date().toISOString() };
    this._recalculate();
  }

  updateRiskSentiment(sentiment) {
    this.state.riskSentiment = sentiment; // 'risk_on' | 'risk_off' | 'neutral'
    this._recalculate();
  }

  updateVIX(value) {
    let trend = 'neutral';
    if (value > 25) trend = 'elevated';
    if (value > 35) trend = 'extreme';
    this.state.vix = { value, trend };
    this._recalculate();
  }

  setNewsProximity(isNear, isBlocking = false) {
    this.state.newsProximity = isNear;
    this.state.newsBlockActive = isBlocking;
    this._recalculate();
  }

  _recalculate() {
    const { dxy, us10y, riskSentiment, vix, newsBlockActive } = this.state;
    let bullishPoints = 0;
    let bearishPoints = 0;
    let riskLevel = 0;
    const components = {};

    // DXY analysis (inverse correlation with gold)
    if (dxy.trend === 'falling') { bullishPoints += 3; components.dxy = 'bullish_gold'; }
    else if (dxy.trend === 'rising') { bearishPoints += 3; components.dxy = 'bearish_gold'; }
    else { components.dxy = 'neutral'; }

    // Yields analysis (inverse correlation with gold)
    if (us10y.trend === 'falling') { bullishPoints += 2; components.yields = 'bullish_gold'; }
    else if (us10y.trend === 'rising') { bearishPoints += 2; components.yields = 'bearish_gold'; }
    else { components.yields = 'neutral'; }

    // Risk sentiment (risk_off = bullish gold as safe haven)
    if (riskSentiment === 'risk_off') { bullishPoints += 2; components.risk = 'bullish_gold'; }
    else if (riskSentiment === 'risk_on') { bearishPoints += 1; components.risk = 'bearish_gold'; }
    else { components.risk = 'neutral'; }

    // VIX (high VIX = uncertainty = bullish gold)
    if (vix.trend === 'extreme') { bullishPoints += 2; riskLevel += 2; components.vix = 'bullish_gold'; }
    else if (vix.trend === 'elevated') { bullishPoints += 1; riskLevel += 1; components.vix = 'mildly_bullish'; }
    else { components.vix = 'neutral'; }

    // News proximity adds risk
    if (newsBlockActive) { riskLevel += 3; components.news = 'blocking'; }
    else if (this.state.newsProximity) { riskLevel += 1; components.news = 'nearby'; }
    else { components.news = 'clear'; }

    // Determine macro bias
    let macro_bias = 'neutral';
    if (bullishPoints > bearishPoints + 1) macro_bias = 'bullish_gold';
    else if (bearishPoints > bullishPoints + 1) macro_bias = 'bearish_gold';

    // Determine macro risk
    let macro_risk = 'low';
    if (riskLevel >= 4) macro_risk = 'high';
    else if (riskLevel >= 2) macro_risk = 'medium';

    this.state.macro_bias = macro_bias;
    this.state.macro_risk = macro_risk;
    this.state.components = components;
    this.state.lastUpdate = new Date().toISOString();

    bus.publish(EVENTS.MACRO_UPDATE, { ...this.state });
  }

  getState() { return { ...this.state }; }
  getMacroBias() { return this.state.macro_bias; }
  getMacroRisk() { return this.state.macro_risk; }
  isTradingSafe() { return this.state.macro_risk !== 'high' && !this.state.newsBlockActive; }
}

module.exports = MacroEngine;
