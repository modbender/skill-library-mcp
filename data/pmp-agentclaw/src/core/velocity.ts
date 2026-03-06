/**
 * Sprint Velocity Calculator
 * Agile/Scrum metrics and forecasting
 */

export interface VelocityInput {
  sprintPoints: number[];  // Array of completed points per sprint
  remainingPoints?: number; // For forecasting
  velocityWindow?: number;  // Rolling average window (default: 3)
}

export interface VelocityOutput {
  sprints: number;
  totalPoints: number;
  averageVelocity: number;
  rollingAverage: number;
  velocityWindow: number;
  remainingPoints?: number;
  sprintsToComplete?: number;
  completionDate?: string;
  trend: 'improving' | 'stable' | 'declining' | 'insufficient-data';
}

/**
 * Calculate sprint velocity metrics
 */
export function calculateVelocity(input: VelocityInput): VelocityOutput {
  const { sprintPoints, remainingPoints, velocityWindow = 3 } = input;
  const sprints = sprintPoints.length;
  const totalPoints = sprintPoints.reduce((a, b) => a + b, 0);
  
  if (sprints === 0) {
    throw new Error('At least one sprint velocity is required');
  }
  
  // Calculate average velocity
  const averageVelocity = Number((totalPoints / sprints).toFixed(1));
  
  // Calculate rolling average (last N sprints)
  let rollingAverage: number;
  if (sprints >= velocityWindow) {
    const lastN = sprintPoints.slice(-velocityWindow);
    rollingAverage = Number((lastN.reduce((a, b) => a + b, 0) / velocityWindow).toFixed(1));
  } else {
    rollingAverage = averageVelocity;
  }
  
  // Determine trend
  let trend: VelocityOutput['trend'];
  if (sprints >= 3) {
    const firstHalf = sprintPoints.slice(0, Math.floor(sprints / 2));
    const secondHalf = sprintPoints.slice(Math.floor(sprints / 2));
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    
    if (secondAvg > firstAvg * 1.1) {
      trend = 'improving';
    } else if (secondAvg < firstAvg * 0.9) {
      trend = 'declining';
    } else {
      trend = 'stable';
    }
  } else {
    trend = 'insufficient-data';
  }
  
  // Forecast completion if remaining points provided
  let sprintsToComplete: number | undefined;
  let completionDate: string | undefined;
  
  if (remainingPoints !== undefined && rollingAverage > 0) {
    sprintsToComplete = Number((remainingPoints / rollingAverage).toFixed(1));
    
    // Estimate completion date (assuming 2-week sprints)
    const weeksToComplete = sprintsToComplete * 2;
    const completion = new Date();
    completion.setDate(completion.getDate() + weeksToComplete * 7);
    completionDate = completion.toISOString().split('T')[0];
  }
  
  return {
    sprints,
    totalPoints,
    averageVelocity,
    rollingAverage,
    velocityWindow,
    remainingPoints,
    sprintsToComplete,
    completionDate,
    trend,
  };
}

/**
 * Format velocity as Markdown
 */
export function formatVelocityMarkdown(result: VelocityOutput): string {
  const trendEmoji = {
    'improving': '📈',
    'stable': '➡️',
    'declining': '📉',
    'insufficient-data': '❓',
  }[result.trend];
  
  let md = `# Sprint Velocity Report\n\n`;
  md += `**Sprints analyzed:** ${result.sprints}\n\n`;
  md += `**Total points completed:** ${result.totalPoints}\n\n`;
  md += `**Average velocity:** ${result.averageVelocity} points/sprint\n\n`;
  md += `**${result.velocityWindow}-sprint rolling average:** ${result.rollingAverage} points/sprint\n\n`;
  md += `**Trend:** ${trendEmoji} ${result.trend}\n\n`;
  
  if (result.remainingPoints !== undefined) {
    md += `## Forecast\n\n`;
    md += `**Remaining points:** ${result.remainingPoints}\n\n`;
    md += `**Estimated sprints to complete:** ${result.sprintsToComplete}\n\n`;
    if (result.completionDate) {
      md += `**Estimated completion:** ${result.completionDate}\n\n`;
    }
  }
  
  return md;
}

/**
 * Format velocity as JSON
 */
export function formatVelocityJson(result: VelocityOutput): string {
  return JSON.stringify(result, null, 2);
}
