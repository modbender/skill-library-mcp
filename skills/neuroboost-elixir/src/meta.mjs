// neuroboost-elixir/src/meta.mjs
// Meta Cortex — Learning to Learn

export class MetaCortex {
  constructor() {
    this.adjustments = []; // [{type, params, improvement, costSaving, timestamp}]
  }

  record(type, params, before, after) {
    this.adjustments.push({
      type,
      params,
      improvement: (after.roi || 0) - (before.roi || 0),
      costSaving: (before.cost || 0) - (after.cost || 0),
      timestamp: Date.now()
    });
    if (this.adjustments.length > 500) this.adjustments.shift();
  }

  // Rank adjustment types by effectiveness
  rank() {
    const byType = new Map();
    for (const adj of this.adjustments) {
      if (!byType.has(adj.type)) byType.set(adj.type, []);
      byType.get(adj.type).push(adj);
    }
    return [...byType.entries()]
      .map(([type, adjs]) => ({
        type,
        count: adjs.length,
        avgImprovement: (adjs.reduce((s, a) => s + a.improvement, 0) / adjs.length).toFixed(3),
        avgCostSaving: (adjs.reduce((s, a) => s + a.costSaving, 0) / adjs.length).toFixed(4),
      }))
      .sort((a, b) => parseFloat(b.avgImprovement) - parseFloat(a.avgImprovement));
  }

  // Suggest best adjustment for current situation
  suggest() {
    const ranked = this.rank();
    return ranked.length > 0 ? ranked[0].type : 'model_downgrade';
  }

  report() {
    return {
      totalAdjustments: this.adjustments.length,
      ranking: this.rank(),
      suggestion: this.suggest()
    };
  }
}
