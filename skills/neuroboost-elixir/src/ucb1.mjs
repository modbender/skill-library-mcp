// neuroboost-elixir/src/ucb1.mjs
// Cortex Router — UCB1 Adaptive Model Selection

export class CortexRouter {
  constructor(models) {
    // models: [{name, costPerCall}]
    this.models = models;
    this.stats = new Map();
    for (const m of models) {
      this.stats.set(m.name, { trials: 0, totalReward: 0, totalCost: 0 });
    }
    this.totalTrials = 0;
  }

  select() {
    this.totalTrials++;
    let best = null, bestScore = -Infinity;

    for (const m of this.models) {
      const s = this.stats.get(m.name);
      if (s.trials === 0) return m; // explore untried

      const avgEfficiency = s.totalReward / s.totalCost; // reward per dollar
      const exploration = Math.sqrt(2 * Math.log(this.totalTrials) / s.trials);
      const score = avgEfficiency + exploration;

      if (score > bestScore) { bestScore = score; best = m; }
    }
    return best;
  }

  update(modelName, reward, cost) {
    const s = this.stats.get(modelName);
    if (!s) return;
    s.trials++;
    s.totalReward += reward;
    s.totalCost += cost;
  }

  report() {
    const rows = [];
    for (const m of this.models) {
      const s = this.stats.get(m.name);
      rows.push({
        model: m.name,
        trials: s.trials,
        avgReward: s.trials > 0 ? (s.totalReward / s.trials).toFixed(3) : 'N/A',
        avgCost: s.trials > 0 ? (s.totalCost / s.trials).toFixed(4) : 'N/A',
        efficiency: s.totalCost > 0 ? (s.totalReward / s.totalCost).toFixed(2) : 'N/A'
      });
    }
    return rows;
  }
}
