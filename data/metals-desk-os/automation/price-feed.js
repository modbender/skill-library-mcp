// ============================================================================
// PRICE FEED — Real-Time Price Data Provider
// ============================================================================
// Connects to MT5 via MetaAPI for live tick data and OHLCV candles.
// Emits: price.update, price.tick
// ============================================================================

const bus = require('./event-bus');
const { EVENTS } = bus;

class PriceFeed {
  constructor(config = {}) {
    this.config = {
      instruments: config.instruments || ['XAUUSD', 'XAGUSD'],
      pollingIntervalMs: config.pollingIntervalMs || 1000,
      candleTimeframes: config.candleTimeframes || ['M5', 'M15', 'H1', 'H4', 'D1', 'W1'],
      metaApiToken: config.metaApiToken || process.env.METAAPI_TOKEN || '',
      accountId: config.accountId || process.env.MT5_ACCOUNT_ID || '',
      ...config
    };

    this.connection = null;
    this.account = null;
    this.running = false;
    this.lastPrices = {};
    this.candles = {};       // { XAUUSD: { M5: [...], H1: [...] } }
    this.tickBuffer = {};    // Recent ticks for spread calculation
    this.pollInterval = null;

    // Initialize candle storage
    this.config.instruments.forEach(inst => {
      this.candles[inst] = {};
      this.tickBuffer[inst] = [];
      this.lastPrices[inst] = null;
      this.config.candleTimeframes.forEach(tf => {
        this.candles[inst][tf] = [];
      });
    });
  }

  // --- Initialize MetaAPI Connection ---
  async initialize() {
    try {
      const MetaApi = require('metaapi.cloud-sdk').default;
      const api = new MetaApi(this.config.metaApiToken);
      this.account = await api.metatraderAccountApi.getAccount(this.config.accountId);

      // Wait for deployment
      if (this.account.state !== 'DEPLOYED') {
        await this.account.deploy();
        await this.account.waitDeployed();
      }

      this.connection = this.account.getStreamingConnection();
      await this.connection.connect();
      await this.connection.waitSynchronized();

      // Subscribe to symbols
      for (const symbol of this.config.instruments) {
        await this.connection.subscribeToMarketData(symbol, [
          { type: 'quotes' },
          { type: 'candles', timeframe: '1m' }
        ]);
      }

      bus.publish(EVENTS.ALERT_SYSTEM, { type: 'price_feed', message: 'Price feed connected to MT5' });
      return true;
    } catch (error) {
      console.error('[PRICE-FEED] MetaAPI init failed:', error.message);
      bus.publish(EVENTS.SYSTEM_ERROR, { engine: 'price-feed', error: error.message });
      return false;
    }
  }

  // --- Start Polling Loop ---
  async start() {
    this.running = true;

    // Initial candle load
    await this.loadHistoricalCandles();

    // Polling loop
    this.pollInterval = setInterval(async () => {
      if (!this.running) return;
      await this.poll();
    }, this.config.pollingIntervalMs);

    console.log('[PRICE-FEED] Started polling every', this.config.pollingIntervalMs, 'ms');
  }

  stop() {
    this.running = false;
    if (this.pollInterval) clearInterval(this.pollInterval);
    console.log('[PRICE-FEED] Stopped');
  }

  // --- Poll Current Prices ---
  async poll() {
    try {
      for (const symbol of this.config.instruments) {
        let price = null;

        if (this.connection) {
          // Live from MetaAPI
          const terminalState = this.connection.terminalState;
          const quote = terminalState.price(symbol);
          if (quote) {
            price = {
              symbol,
              bid: quote.bid,
              ask: quote.ask,
              spread: parseFloat((quote.ask - quote.bid).toFixed(symbol === 'XAUUSD' ? 2 : 4)),
              mid: parseFloat(((quote.bid + quote.ask) / 2).toFixed(symbol === 'XAUUSD' ? 2 : 4)),
              timestamp: new Date().toISOString(),
              source: 'metaapi'
            };
          }
        }

        // Fallback: Simulated / Cached
        if (!price) {
          price = this._getSimulatedPrice(symbol);
        }

        if (price) {
          this.lastPrices[symbol] = price;
          this._addToTickBuffer(symbol, price);

          bus.publish(EVENTS.PRICE_TICK, price);
          bus.publish(EVENTS.PRICE_UPDATE, {
            symbol,
            price,
            candles: this.candles[symbol],
            spreadInfo: this.getSpreadStats(symbol)
          });
        }
      }
    } catch (error) {
      bus.publish(EVENTS.SYSTEM_ERROR, { engine: 'price-feed', error: error.message });
    }
  }

  // --- Load Historical Candles ---
  async loadHistoricalCandles() {
    try {
      if (!this.connection) {
        console.log('[PRICE-FEED] No connection, using empty candle data');
        return;
      }

      for (const symbol of this.config.instruments) {
        for (const tf of this.config.candleTimeframes) {
          const metaApiTf = this._mapTimeframe(tf);
          const candles = await this.connection.getCandles(symbol, metaApiTf, new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));

          if (candles && candles.length > 0) {
            this.candles[symbol][tf] = candles.map(c => ({
              time: new Date(c.time).getTime(),
              open: c.open,
              high: c.high,
              low: c.low,
              close: c.close,
              volume: c.tickVolume || 0
            }));
          }
        }
      }
      console.log('[PRICE-FEED] Historical candles loaded');
    } catch (error) {
      console.error('[PRICE-FEED] Historical candle load failed:', error.message);
    }
  }

  // --- Get Latest Price ---
  getPrice(symbol) {
    return this.lastPrices[symbol] || null;
  }

  // --- Get Candles ---
  getCandles(symbol, timeframe, count = 200) {
    const candles = this.candles[symbol]?.[timeframe] || [];
    return candles.slice(-count);
  }

  // --- Spread Statistics ---
  getSpreadStats(symbol) {
    const ticks = this.tickBuffer[symbol] || [];
    if (ticks.length < 2) return { current: 0, avg: 0, max: 0, isWide: false };

    const spreads = ticks.map(t => t.spread);
    const current = spreads[spreads.length - 1];
    const avg = spreads.reduce((a, b) => a + b, 0) / spreads.length;
    const max = Math.max(...spreads);
    const stdDev = Math.sqrt(spreads.reduce((s, v) => s + Math.pow(v - avg, 2), 0) / spreads.length);

    return {
      current,
      avg: parseFloat(avg.toFixed(2)),
      max,
      stdDev: parseFloat(stdDev.toFixed(2)),
      isWide: current > avg + 2 * stdDev,
      sampleSize: ticks.length
    };
  }

  // --- Tick Buffer Management ---
  _addToTickBuffer(symbol, price) {
    this.tickBuffer[symbol].push(price);
    if (this.tickBuffer[symbol].length > 500) {
      this.tickBuffer[symbol] = this.tickBuffer[symbol].slice(-250);
    }
  }

  // --- Simulated Price (for testing / no connection) ---
  _getSimulatedPrice(symbol) {
    const basePrices = { XAUUSD: 5030.00, XAGUSD: 81.00 };
    const base = basePrices[symbol] || 5030;
    const noise = (Math.random() - 0.5) * (symbol === 'XAUUSD' ? 10 : 1.5);
    const decimals = symbol === 'XAUUSD' ? 2 : 4;
    const bid = parseFloat((base + noise).toFixed(decimals));
    const spreadSize = symbol === 'XAUUSD' ? 0.50 : 0.08;
    const ask = parseFloat((bid + spreadSize).toFixed(decimals));

    return {
      symbol,
      bid,
      ask,
      spread: parseFloat((ask - bid).toFixed(decimals)),
      mid: parseFloat(((bid + ask) / 2).toFixed(decimals)),
      timestamp: new Date().toISOString(),
      source: 'simulated'
    };
  }

  // --- Map Timeframe to MetaAPI format ---
  _mapTimeframe(tf) {
    const map = { 'M1': '1m', 'M5': '5m', 'M15': '15m', 'H1': '1h', 'H4': '4h', 'D1': '1d', 'W1': '1w' };
    return map[tf] || '1h';
  }
}

module.exports = PriceFeed;
