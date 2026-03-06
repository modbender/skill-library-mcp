// neuroboost-elixir/src/thompson.mjs
// Bayesian Optimizer — Thompson Sampling Strategy Selection

// Simple Beta distribution sampler using Jöhnk's algorithm
function betaSample(alpha, beta) {
  // For small alpha/beta, use inverse CDF approximation
  let u, v, x, y;
  do {
    u = Math.random();
    v = Math.random();
    x = Math.pow(u, 1 / alpha);
    y = Math.pow(v, 1 / beta);
  } while (x + y > 1);
  return x / (x + y);
}

export class BayesianOptimizer {
  constructor() {
    this.strategies = new Map();
  }

  addStrategy(name) {
    this.strategies.set(name, {
      alpha: 1, beta: 1, // Beta(1,1) = uniform prior
      totalReturn: 0, totalCost: 0, trials: 0
    });
  }

  removeStrategy(name) {
    this.strategies.delete(name);
  }

  select() {
    let best = null, bestSample = -1;
    for (const [name, s] of this.strategies) {
      const sample = betaSample(s.alpha, s.beta);
      if (sample > bestSample) { bestSample = sample; best = name; }
    }
    return best;
  }

  update(name, success, returnAmount = 0, cost = 0) {
    const s = this.strategies.get(name);
    if (!s) return;
    s.trials++;
    if (success) s.alpha += 1;
    else s.beta += 1;
    s.totalReturn += returnAmount;
    s.totalCost += cost;
  }

  // Kelly Criterion optimal fraction
  kellyFraction(name, avgWin = 1, avgLoss = 1) {
    const s = this.strategies.get(name);
    if (!s || s.trials < 5) return 0; // not enough data
    const p = s.alpha / (s.alpha + s.beta);
    const b = avgWin / avgLoss;
    const kelly = (p * b - (1 - p)) / b;
    return Math.max(0, Math.min(kelly * 0.5, 0.25)); // half-Kelly, cap 25%
  }

  report() {
    const rows = [];
    for (const [name, s] of this.strategies) {
      const winRate = s.alpha / (s.alpha + s.beta);
      const roi = s.totalCost > 0 ? ((s.totalReturn - s.totalCost) / s.totalCost * 100) : 0;
      rows.push({
        strategy: name,
        trials: s.trials,
        winRate: (winRate * 100).toFixed(1) + '%',
        roi: roi.toFixed(1) + '%',
        kelly: (this.kellyFraction(name) * 100).toFixed(1) + '%'
      });
    }
    return rows.sort((a, b) => parseFloat(b.roi) - parseFloat(a.roi));
  }

  // Auto-kill strategies with negative ROI after enough samples
  prune(minTrials = 20) {
    const killed = [];
    for (const [name, s] of this.strategies) {
      if (s.trials >= minTrials && s.totalReturn < s.totalCost) {
        killed.push(name);
        this.strategies.delete(name);
      }
    }
    return killed;
  }
}
