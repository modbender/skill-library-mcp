/**
 * Generate the sales pipeline report as Markdown.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @returns {string} The Markdown report string.
 */
export function generatePipelineReport(db) {
  // Active deals (open stages)
  const openStages = ['prospect', 'qualified', 'proposal', 'negotiation'];
  const activeDealsStmt = db.prepare(`SELECT COUNT(*) as count FROM deals WHERE stage IN (${openStages.map(() => '?').join(',')})`);
  const activeDeals = activeDealsStmt.get(...openStages).count;

  const totalValueStmt = db.prepare(`SELECT SUM(value) as total FROM deals WHERE stage IN (${openStages.map(() => '?').join(',')})`);
  const totalValue = totalValueStmt.get(...openStages).total || 0;

  const avgSize = activeDeals > 0 ? Math.round(totalValue / activeDeals) : 0;

  // Overdue follow-ups for open deals
  const overdueStmt = db.prepare(`
    SELECT COUNT(*) as count 
    FROM follow_ups f 
    JOIN deals d ON f.deal_id = d.id 
    WHERE f.completed = 0 AND f.due_date < datetime('now') AND d.stage IN (${openStages.map(() => '?').join(',')})
  `);
  const overdue = overdueStmt.get(...openStages).count;

  // By stage breakdown (all stages)
  const allStages = ['prospect', 'qualified', 'proposal', 'negotiation', 'closed-won', 'closed-lost'];
  let byStageTable = '| Stage | Count | Value | Avg Age (days) |\n|-------|-------|-------|----------------|\n';
  for (const stage of allStages) {
    const stageStmt = db.prepare(`
      SELECT 
        COUNT(*) as count, 
        COALESCE(SUM(value), 0) as value, 
        ROUND(AVG(julianday('now') - julianday(created_at))) as avg_age 
      FROM deals 
      WHERE stage = ?
    `);
    const res = stageStmt.get(stage);
    byStageTable += `| ${stage} | ${res.count} | $${res.value.toLocaleString()} | ${res.avg_age || 0} |\n`;
  }

  // Top open deals
  const topDealsStmt = db.prepare(`
    SELECT title, value, stage 
    FROM deals 
    WHERE stage IN (${openStages.map(() => '?').join(',')}) 
    ORDER BY value DESC 
    LIMIT 5
  `);
  const topDeals = topDealsStmt.all(...openStages);
  let topList = '### Top Deals\n';
  if (topDeals.length === 0) {
    topList += '- No active deals\n';
  } else {
    topDeals.forEach(deal => {
      topList += `- **${deal.title}**: $${deal.value.toLocaleString()} (${deal.stage})\n`;
    });
  }

  const report = `# Sales Pipeline

## Quick Stats
- **Active Deals:** ${activeDeals}
- **Total Pipeline Value:** $${totalValue.toLocaleString()}
- **Avg Deal Size:** $${avgSize.toLocaleString()}
- **Overdue Follow-ups:** ${overdue}

## By Stage
${byStageTable}

${topList}`;

  return report;
}