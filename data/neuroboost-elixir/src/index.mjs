// neuroboost-elixir/src/index.mjs
// NeuroBoost Elixir v2.1 — Main Entry

import { CortexRouter } from './ucb1.mjs';
import { BayesianOptimizer } from './thompson.mjs';
import { HomeostasisController } from './pid.mjs';
import { SentinelDiagnostics } from './cusum.mjs';
import { MetaCortex } from './meta.mjs';

export class NeuroBoost {
  constructor(config = {}) {
    const models = config.models || [
      { name: 'gpt-4o-mini', costPerCall: 0.003 },
      { name: 'gpt-4o', costPerCall: 0.015 },
      { name: 'gpt-5.2', costPerCall: 0.05 },
    ];

    this.router = new CortexRouter(models);
    this.optimizer = new BayesianOptimizer();
    this.controller = new HomeostasisController(config.targetBurnRate || 0.02);
    this.sentinel = new SentinelDiagnostics();
    this.meta = new MetaCortex();
    this.startTime = Date.now();
  }

  // Before each turn: get recommended model and strategy
  beforeTurn() {
    const model = this.router.select();
    const strategy = this.optimizer.select();
    const mode = this.controller.mode();
    return { model, strategy, mode };
  }

  // After each turn: record results
  afterTurn({ model, strategy, cost, reward, error, hadEffect }) {
    this.router.update(model, reward || 0, cost || 0);
    if (strategy) this.optimizer.update(strategy, !error && hadEffect, reward || 0, cost || 0);
    this.controller.record(this.controller.history.at(-1)?.balance || 0, cost || 0);
    this.sentinel.recordTurn({ model, strategy, cost, reward, error, hadEffect });
  }

  // Update balance (call after checking credits)
  updateBalance(balance) {
    this.controller.record(balance, 0);
  }

  // Full diagnosis
  diagnose() {
    return {
      timestamp: new Date().toISOString(),
      uptime: ((Date.now() - this.startTime) / 3600000).toFixed(1) + 'h',
      resource: this.controller.report(),
      models: this.router.report(),
      strategies: this.optimizer.report(),
      diagnostics: this.sentinel.diagnose(),
      meta: this.meta.report()
    };
  }

  // One-line status
  status() {
    const r = this.controller.report();
    const d = this.sentinel.diagnose();
    return `[NB] ${r.mode} | burn=${r.currentBurnRate} | runway=${r.runwayHours} | trend=${r.trend} | ${d.status || 'OK'}`;
  }
}

// Re-export modules
export { CortexRouter } from './ucb1.mjs';
export { BayesianOptimizer } from './thompson.mjs';
export { HomeostasisController } from './pid.mjs';
export { SentinelDiagnostics } from './cusum.mjs';
export { MetaCortex } from './meta.mjs';
