// neuroboost-elixir/src/cusum.mjs
// Sentinel Diagnostics — CUSUM Change-Point Detection + Self-Diagnosis

export class SentinelDiagnostics {
  constructor() {
    this.turns = []; // [{timestamp, cost, reward, error, model, strategy, hadEffect}]
  }

  recordTurn(data) {
    this.turns.push({ t: Date.now(), ...data });
    if (this.turns.length > 5000) this.turns.shift();
  }

  // CUSUM change-point detection on a binary series
  static cusum(series, threshold = 3) {
    if (series.length < 5) return { detected: false, cumSum: 0 };
    const mean = series.reduce((s, v) => s + v, 0) / series.length;
    let cumSum = 0, maxSum = 0, changeIdx = -1;
    for (let i = 0; i < series.length; i++) {
      cumSum = Math.max(0, cumSum + (series[i] - mean));
      if (cumSum > maxSum) { maxSum = cumSum; changeIdx = i; }
    }
    return { detected: maxSum > threshold, maxSum, changeIdx };
  }

  // Full diagnosis
  diagnose(windowHours = 24) {
    const cutoff = Date.now() - windowHours * 3600 * 1000;
    const recent = this.turns.filter(t => t.t >= cutoff);
    if (recent.length === 0) return { status: 'NO_DATA', actions: [] };

    const report = { timestamp: new Date().toISOString(), actions: [] };

    // 1. Cost efficiency
    const totalCost = recent.reduce((s, t) => s + (t.cost || 0), 0);
    const useful = recent.filter(t => t.hadEffect).length;
    report.totalCost = totalCost;
    report.totalTurns = recent.length;
    report.usefulTurns = useful;
    report.wasteRatio = ((recent.length - useful) / recent.length * 100).toFixed(1) + '%';
    report.costPerUseful = useful > 0 ? (totalCost / useful).toFixed(4) : 'N/A';

    if ((recent.length - useful) / recent.length > 0.3) {
      report.actions.push('REDUCE_FREQUENCY: ' + report.wasteRatio + ' turns are wasteful');
    }

    // 2. Error rate + CUSUM
    const errors = recent.map(t => t.error ? 1 : 0);
    report.errorRate = (errors.reduce((s, v) => s + v, 0) / errors.length * 100).toFixed(1) + '%';
    const cusumResult = SentinelDiagnostics.cusum(errors);
    report.errorTrend = cusumResult.detected ? 'CHANGE_DETECTED' : 'stable';

    if (cusumResult.detected) {
      report.actions.push('CHECK_APIS: error rate change detected at turn ' + cusumResult.changeIdx);
    }
    if (parseFloat(report.errorRate) > 10) {
      report.actions.push('HIGH_ERROR_RATE: ' + report.errorRate + ' > 10%');
    }

    // 3. Strategy ROI ranking
    const stratMap = new Map();
    for (const t of recent) {
      if (!t.strategy) continue;
      if (!stratMap.has(t.strategy)) stratMap.set(t.strategy, { returns: 0, costs: 0, count: 0 });
      const s = stratMap.get(t.strategy);
      s.returns += t.reward || 0;
      s.costs += t.cost || 0;
      s.count++;
    }
    report.strategies = [...stratMap.entries()]
      .map(([name, s]) => ({
        name, trials: s.count,
        roi: s.costs > 0 ? (((s.returns - s.costs) / s.costs) * 100).toFixed(1) + '%' : 'N/A'
      }))
      .sort((a, b) => parseFloat(b.roi || 0) - parseFloat(a.roi || 0));

    // 4. Model cost ranking
    const modelMap = new Map();
    for (const t of recent) {
      if (!t.model) continue;
      if (!modelMap.has(t.model)) modelMap.set(t.model, { cost: 0, count: 0, rewards: 0 });
      const m = modelMap.get(t.model);
      m.cost += t.cost || 0;
      m.count++;
      m.rewards += t.reward || 0;
    }
    report.models = [...modelMap.entries()]
      .map(([name, m]) => ({
        name, calls: m.count,
        avgCost: (m.cost / m.count).toFixed(4),
        efficiency: m.cost > 0 ? (m.rewards / m.cost).toFixed(2) : 'N/A'
      }))
      .sort((a, b) => parseFloat(a.avgCost) - parseFloat(b.avgCost));

    // 5. Status line
    report.status = report.actions.length === 0 ? 'HEALTHY' : 'NEEDS_ATTENTION';
    report.summary = `[DIAG] turns=${recent.length}, cost=$${totalCost.toFixed(2)}, waste=${report.wasteRatio}, errors=${report.errorRate}, status=${report.status}`;

    return report;
  }
}
