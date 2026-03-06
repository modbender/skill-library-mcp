#!/usr/bin/env node
// ============================================================================
// METALS DESK OS — Main Entry Point & Orchestrator
// ============================================================================
// This file initializes all engines, connects the pipeline, and starts
// the continuous trading loop:
//
// PRICE FEED → STRUCTURE → LIQUIDITY → MACRO → BIAS → VOLATILITY →
// RISK → EXECUTION → BROKER → PERFORMANCE → DASHBOARD → ALERTS
//
// Install: ~/.openclaw/agents/trader/agent/metals-desk-os/
// Run: node index.js
// ============================================================================

require('dotenv').config();
const fs = require('fs');
const path = require('path');

// --- Import Event Bus (Central Nervous System) ---
const bus = require('./automation/event-bus');
const { EVENTS } = bus;

// --- Import Automation ---
const PriceFeed = require('./automation/price-feed');
const SessionEngine = require('./automation/session-engine');
const Scheduler = require('./automation/scheduler');
const NewsMonitor = require('./automation/news-monitor');

// --- Import Core Engines ---
const StructureEngine = require('./core/structure-engine');
const LiquidityEngine = require('./core/liquidity-engine');
const BiasEngine = require('./core/bias-engine');
const MacroEngine = require('./core/macro-engine');
const VolatilityEngine = require('./core/volatility-engine');
const RiskEngine = require('./core/risk-engine');
const ExecutionEngine = require('./core/execution-engine');
const PerformanceEngine = require('./core/performance-engine');

// --- Import Broker ---
const MT5Connector = require('./broker/mt5-connector');
const RiskGuard = require('./broker/risk-guard');
const OrderManager = require('./broker/order-manager');

// --- Import Alerts ---
const WhatsAppAlert = require('./alerts/whatsapp-alert');
const TelegramAlert = require('./alerts/telegram-alert');
const RiskAlert = require('./alerts/risk-alert');

// --- Import Dashboard ---
const WebSocketFeed = require('./dashboard/websocket-feed');

// ============================================================================
// INITIALIZATION
// ============================================================================

class MetalsDeskOS {
  constructor() {
    console.log('');
    console.log('╔══════════════════════════════════════════════════╗');
    console.log('║          METALS DESK OS v1.0.0                  ║');
    console.log('║    Institutional Trading Operating System        ║');
    console.log('║    XAU/USD • XAG/USD                            ║');
    console.log('║    Architecture: Event-Driven, Risk-First       ║');
    console.log('╚══════════════════════════════════════════════════╝');
    console.log('');

    // Load state
    this.stateFile = path.join(__dirname, 'data/state.json');
    this.state = this._loadState();

    // Set system mode
    bus.setMode(this.state.mode || 1);

    // --- Instantiate Engines ---
    this.priceFeed = new PriceFeed();
    this.sessionEngine = new SessionEngine();
    this.scheduler = new Scheduler();
    this.newsMonitor = new NewsMonitor();

    this.structureEngine = new StructureEngine();
    this.liquidityEngine = new LiquidityEngine();
    this.biasEngine = new BiasEngine();
    this.macroEngine = new MacroEngine();
    this.volatilityEngine = new VolatilityEngine();
    this.riskEngine = new RiskEngine();
    this.executionEngine = new ExecutionEngine();
    this.performanceEngine = new PerformanceEngine();

    this.mt5 = new MT5Connector();
    this.riskGuard = new RiskGuard(this.mt5);
    this.orderManager = new OrderManager(this.mt5, this.riskGuard, this.performanceEngine);

    this.whatsApp = new WhatsAppAlert();
    this.telegram = new TelegramAlert();
    this.riskAlert = new RiskAlert(this.whatsApp, this.telegram);

    this.wsFeed = new WebSocketFeed();

    // Loop control
    this.mainLoopInterval = null;
    this.instruments = ['XAUUSD', 'XAGUSD'];
  }

  // --- Start the System ---
  async start() {
    console.log('[METALS-DESK-OS] Starting all engines...');

    // 1. Connect to broker
    const brokerConnected = await this.mt5.connect();
    console.log(`[INIT] MT5 Connector: ${brokerConnected ? '✅ Connected' : '⚠️ Offline (simulated mode)'}`);

    // 2. Initialize price feed
    const feedConnected = await this.priceFeed.initialize();
    console.log(`[INIT] Price Feed: ${feedConnected ? '✅ Live' : '⚠️ Simulated'}`);

    // 3. Start automation layer
    this.priceFeed.start();
    this.sessionEngine.start();
    this.scheduler.start();
    this.newsMonitor.start();
    await this.newsMonitor.loadCalendar();

    // 4. Start broker management
    this.riskGuard.start();
    this.orderManager.start();

    // 5. Start alerts
    this.whatsApp.start();
    this.telegram.start();
    this.riskAlert.start();

    // 6. Start dashboard WebSocket
    this.wsFeed.start(() => this.getFullState());

    // 7. Wire up the main analysis pipeline
    this._setupPipeline();

    // 8. Start main loop
    this.mainLoopInterval = setInterval(() => this._mainLoop(), 5000);

    // 9. Update state
    this.state.startedAt = new Date().toISOString();
    this.state.activeConnections.mt5 = brokerConnected;
    this.state.activeConnections.priceFeed = feedConnected;
    this.state.activeConnections.websocket = true;
    this._saveState();

    // 10. Emit system start
    bus.publish(EVENTS.SYSTEM_START, {
      mode: bus.getMode(),
      instruments: this.instruments,
      timestamp: new Date().toISOString()
    });

    console.log('');
    console.log('[METALS-DESK-OS] ✅ All engines running');
    console.log(`[METALS-DESK-OS] Mode: ${['', 'Advisory', 'Semi-Auto', 'Full-Auto', 'Risk-Off'][bus.getMode()]}`);
    console.log(`[METALS-DESK-OS] Dashboard WebSocket: ws://localhost:${this.wsFeed.config.port}`);
    console.log(`[METALS-DESK-OS] Instruments: ${this.instruments.join(', ')}`);
    console.log('');

    // Update account info
    if (brokerConnected) {
      const accountInfo = await this.mt5.getAccountInfo();
      if (accountInfo) {
        this.riskEngine.updateAccount(accountInfo.balance, accountInfo.equity);
        console.log(`[INIT] Account Balance: $${accountInfo.balance} | Equity: $${accountInfo.equity}`);
      }
    }

    return true;
  }

  // --- Stop the System ---
  stop() {
    console.log('[METALS-DESK-OS] Shutting down...');

    if (this.mainLoopInterval) clearInterval(this.mainLoopInterval);
    this.priceFeed.stop();
    this.sessionEngine.stop();
    this.scheduler.stop();
    this.newsMonitor.stop();
    this.riskGuard.stop();
    this.wsFeed.stop();

    bus.publish(EVENTS.SYSTEM_STOP, { timestamp: new Date().toISOString() });
    this._saveState();

    console.log('[METALS-DESK-OS] ✅ Shutdown complete');
  }

  // ============================================================================
  // MAIN ANALYSIS PIPELINE
  // ============================================================================

  _setupPipeline() {
    // On each price update, run the analysis pipeline
    bus.on(EVENTS.PRICE_UPDATE, (data) => {
      if (!data.price || !data.candles) return;
      this._analyzePipeline(data.symbol || data.price.symbol, data);
    });

    // On daily reset, reset risk counters
    bus.on('scheduler.daily.reset', () => {
      this.riskEngine.resetDaily();
      console.log('[PIPELINE] Daily reset completed');
    });

    // On macro check, update macro engine
    bus.on('scheduler.macro.check', () => {
      // In production, fetch live DXY/yield data here
      console.log('[PIPELINE] Macro check tick');
    });
  }

  _analyzePipeline(symbol, priceData) {
    try {
      const candles = priceData.candles || {};
      const currentPrice = priceData.price;

      // --- 1. Structure Analysis (multi-timeframe) ---
      const structureResults = {};
      for (const tf of ['M15', 'H1', 'H4', 'D1']) {
        const tfCandles = candles[tf];
        if (tfCandles && tfCandles.length > 20) {
          structureResults[tf] = this.structureEngine.analyze(symbol, tf, tfCandles);
        }
      }
      const mtfAlignment = this.structureEngine.getMTFAlignment(symbol);

      // --- 2. Liquidity Analysis ---
      const sessionLevels = this.sessionEngine.getKeyLevels(symbol);
      const h1Candles = candles['H1'] || [];
      const liquidityResult = this.liquidityEngine.analyze(symbol, 'H1', h1Candles, sessionLevels);

      // --- 3. Volatility Analysis ---
      for (const tf of ['M15', 'H1', 'H4', 'D1']) {
        const tfCandles = candles[tf];
        if (tfCandles && tfCandles.length > 20) {
          this.volatilityEngine.analyze(symbol, tf, tfCandles);
        }
      }
      const h1Volatility = this.volatilityEngine.getState(symbol)['H1'] || {};

      // --- 4. News Check ---
      const newsState = this.newsMonitor.getState();
      this.macroEngine.setNewsProximity(newsState.isBlocking || newsState.upcomingCount > 0, newsState.isBlocking);

      // --- 5. Bias Calculation ---
      const sessionState = this.sessionEngine.getState();
      const macroState = this.macroEngine.getState();
      const h1Structure = this.structureEngine.getState(symbol, 'H1');
      const fvgs = h1Structure?.fvgs || [];

      const bias = this.biasEngine.calculate(symbol, {
        structureMTF: mtfAlignment,
        liquidityState: this.liquidityEngine.getLiquidityMap(symbol),
        macroState,
        sessionState,
        volatilityState: h1Volatility,
        fvgs
      });

      // --- 6. Execution Evaluation ---
      if (bus.isTradingAllowed() && !this.riskEngine.isHalted()) {
        const signal = this.executionEngine.evaluate({
          symbol,
          currentPrice,
          bias,
          structure: h1Structure,
          liquidity: liquidityResult,
          macro: macroState,
          volatility: h1Volatility,
          session: sessionState,
          risk: this.riskEngine,
          fvgs,
          orderBlocks: h1Structure?.orderBlocks || []
        });

        // In advisory mode, log the signal
        if (bus.getMode() === 1 && signal.passed) {
          console.log(`[SIGNAL] ${symbol} ${signal.direction?.toUpperCase()} | Entry: ${signal.entry} | SL: ${signal.sl} | Conviction: ${signal.conviction}`);
        }
      }
    } catch (error) {
      bus.publish(EVENTS.SYSTEM_ERROR, { engine: 'pipeline', error: error.message, symbol });
    }
  }

  // --- Main Loop (periodic tasks) ---
  _mainLoop() {
    // Sync account info periodically
    if (this.mt5.isConnected()) {
      this.mt5.getAccountInfo().then(info => {
        if (info) this.riskEngine.updateAccount(info.balance, info.equity);
      }).catch(() => {});

      // Sync open position count
      this.mt5.getPositions().then(positions => {
        this.riskEngine.setOpenPositions(positions.length);
      }).catch(() => {});
    }
  }

  // ============================================================================
  // STATE & API
  // ============================================================================

  getFullState() {
    return {
      system: {
        mode: bus.getMode(),
        modeName: ['', 'Advisory', 'Semi-Auto', 'Full-Auto', 'Risk-Off'][bus.getMode()],
        uptime: process.uptime(),
        health: bus.getHealth()
      },
      bias: {
        XAUUSD: this.biasEngine.getBias('XAUUSD'),
        XAGUSD: this.biasEngine.getBias('XAGUSD')
      },
      prices: {
        XAUUSD: this.priceFeed.getPrice('XAUUSD'),
        XAGUSD: this.priceFeed.getPrice('XAGUSD')
      },
      session: this.sessionEngine.getState(),
      macro: this.macroEngine.getState(),
      risk: this.riskEngine.getState(),
      volatility: {
        XAUUSD: this.volatilityEngine.getState('XAUUSD'),
        XAGUSD: this.volatilityEngine.getState('XAGUSD')
      },
      performance: this.performanceEngine.getMetricsSummary(),
      positions: this.mt5.getOpenOrders(),
      news: this.newsMonitor.getState(),
      liquidity: {
        XAUUSD: this.liquidityEngine.getLiquidityMap('XAUUSD'),
        XAGUSD: this.liquidityEngine.getLiquidityMap('XAGUSD')
      },
      alerts: this.riskAlert.getRecentAlerts(10),
      timestamp: new Date().toISOString()
    };
  }

  setMode(mode) {
    bus.setMode(mode);
    this.state.mode = mode;
    this._saveState();
  }

  _loadState() {
    try {
      return JSON.parse(fs.readFileSync(this.stateFile, 'utf8'));
    } catch (e) {
      return { mode: 1 };
    }
  }

  _saveState() {
    try {
      this.state.lastUpdate = new Date().toISOString();
      fs.writeFileSync(this.stateFile, JSON.stringify(this.state, null, 2));
    } catch (e) { /* silent */ }
  }
}

// ============================================================================
// BOOT
// ============================================================================

const desk = new MetalsDeskOS();

// Graceful shutdown
process.on('SIGINT', () => { desk.stop(); process.exit(0); });
process.on('SIGTERM', () => { desk.stop(); process.exit(0); });

// Start
desk.start().then(() => {
  console.log('[METALS-DESK-OS] 🏛 Desk is operational');
}).catch(err => {
  console.error('[METALS-DESK-OS] FATAL:', err.message);
  process.exit(1);
});

module.exports = MetalsDeskOS;
