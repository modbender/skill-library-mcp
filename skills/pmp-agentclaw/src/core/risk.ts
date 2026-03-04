/**
 * Risk Management Calculations
 * PMBOK 7th Edition — Risk Management
 */

export type ProbabilityScore = 1 | 2 | 3 | 4 | 5;
export type ImpactScore = 1 | 2 | 3 | 4 | 5;
export type RiskZone = 'GREEN' | 'AMBER' | 'RED';

export interface RiskInput {
  id: string;
  description: string;
  category?: string;
  probability: ProbabilityScore;
  impact: ImpactScore;
  owner?: string;
  responseStrategy?: string;
}

export interface RiskOutput extends RiskInput {
  score: number;        // Probability × Impact (1-25)
  zone: RiskZone;
  action: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface RiskMatrix {
  probabilityScale: Array<{
    score: ProbabilityScore;
    label: string;
    range: string;
  }>;
  impactScale: Array<{
    score: ImpactScore;
    label: string;
    description: string;
  }>;
  zones: {
    low: { range: [number, number]; color: string; action: string };
    medium: { range: [number, number]; color: string; action: string };
    high: { range: [number, number]; color: string; action: string };
  };
  responseStrategies: {
    threats: string[];
    opportunities: string[];
  };
}

// Default 5×5 Risk Matrix (PMBOK standard)
export const DEFAULT_RISK_MATRIX: RiskMatrix = {
  probabilityScale: [
    { score: 1, label: 'Rare', range: '<10%' },
    { score: 2, label: 'Unlikely', range: '10-30%' },
    { score: 3, label: 'Possible', range: '30-50%' },
    { score: 4, label: 'Likely', range: '50-70%' },
    { score: 5, label: 'Almost Certain', range: '>70%' },
  ],
  impactScale: [
    { score: 1, label: 'Insignificant', description: 'Negligible effect on objectives' },
    { score: 2, label: 'Minor', description: '<5% schedule/cost impact' },
    { score: 3, label: 'Moderate', description: '5-10% schedule/cost impact' },
    { score: 4, label: 'Major', description: '10-25% schedule/cost impact' },
    { score: 5, label: 'Catastrophic', description: '>25% impact or project viability threatened' },
  ],
  zones: {
    low: { range: [1, 4], color: 'green', action: 'Accept and monitor' },
    medium: { range: [5, 12], color: 'amber', action: 'Mitigate with contingency plan' },
    high: { range: [15, 25], color: 'red', action: 'Immediate response required' },
  },
  responseStrategies: {
    threats: ['Avoid', 'Mitigate', 'Transfer', 'Accept'],
    opportunities: ['Exploit', 'Enhance', 'Share', 'Accept'],
  },
};

/**
 * Score a single risk
 */
export function scoreRisk(risk: RiskInput, matrix?: RiskMatrix): RiskOutput {
  const m = matrix || DEFAULT_RISK_MATRIX;
  const score = risk.probability * risk.impact;
  
  // Determine zone
  let zone: RiskZone;
  let action: string;
  
  if (score >= m.zones.high.range[0]) {
    zone = 'RED';
    action = m.zones.high.action;
  } else if (score >= m.zones.medium.range[0]) {
    zone = 'AMBER';
    action = m.zones.medium.action;
  } else {
    zone = 'GREEN';
    action = m.zones.low.action;
  }
  
  // Determine priority
  let priority: 'Low' | 'Medium' | 'High' | 'Critical';
  if (score >= 20) priority = 'Critical';
  else if (score >= 15) priority = 'High';
  else if (score >= 8) priority = 'Medium';
  else priority = 'Low';
  
  return {
    ...risk,
    score,
    zone,
    action,
    priority,
  };
}

/**
 * Score multiple risks
 */
export function scoreRisks(risks: RiskInput[], matrix?: RiskMatrix): RiskOutput[] {
  return risks.map(r => scoreRisk(r, matrix)).sort((a, b) => b.score - a.score);
}

/**
 * Get risk matrix as formatted table
 */
export function getRiskMatrixTable(matrix?: RiskMatrix): string {
  const m = matrix || DEFAULT_RISK_MATRIX;
  let table = '# 5×5 Probability × Impact Matrix\n\n';
  table += '| | ' + m.impactScale.map(i => `${i.label} (${i.score})`).join(' | ') + ' |\n';
  table += '|--|' + m.impactScale.map(() => '---').join('|') + '|\n';
  
  // Generate rows (reverse probability for display)
  for (let p = 5; p >= 1; p--) {
    const prob = m.probabilityScale.find(x => x.score === p)!;
    let row = `| **${prob.label} (${p})** |`;
    for (let i = 1; i <= 5; i++) {
      const score = p * i;
      let emoji = '🟢';
      if (score >= 15) emoji = '🔴';
      else if (score >= 5) emoji = '🟡';
      row += ` ${score} ${emoji} |`;
    }
    table += row + '\n';
  }
  
  return table;
}

/**
 * Calculate risk statistics
 */
export function calculateRiskStats(risks: RiskOutput[]): {
  total: number;
  open: number;
  closed: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  criticalCount: number;
  averageScore: number;
} {
  const total = risks.length;
  const highCount = risks.filter(r => r.zone === 'RED').length;
  const mediumCount = risks.filter(r => r.zone === 'AMBER').length;
  const lowCount = risks.filter(r => r.zone === 'GREEN').length;
  const criticalCount = risks.filter(r => r.priority === 'Critical').length;
  const averageScore = total === 0 ? 0 : Number((risks.reduce((sum, r) => sum + r.score, 0) / total).toFixed(1));
  
  return {
    total,
    open: total, // Assuming all are open unless status field added
    closed: 0,
    highCount,
    mediumCount,
    lowCount,
    criticalCount,
    averageScore,
  };
}

/**
 * Format risk matrix as Markdown (alias for getRiskMatrixTable)
 */
export function formatRiskMatrixMarkdown(matrix?: RiskMatrix): string {
  return getRiskMatrixTable(matrix);
}
