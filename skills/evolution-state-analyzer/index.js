const fs = require('fs');
const path = require('path');
const readline = require('readline');

/**
 * Analyzes the evolution state from memory graph.
 * @param {string} graphPath - Path to memory_graph.jsonl
 * @returns {Promise<Object>} Analysis report
 */
async function analyzeState(graphPath) {
  const defaultPath = path.resolve(__dirname, '../../memory/evolution/memory_graph.jsonl');
  const targetPath = graphPath || defaultPath;

  if (!fs.existsSync(targetPath)) {
    return { error: `Graph file not found: ${targetPath}` };
  }

  const events = [];
  const genes = {};
  const failurePatterns = {};
  let lastEvent = null;
  let streak = 0;
  let stagnation = false;

  const fileStream = fs.createReadStream(targetPath);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });

  for await (const line of rl) {
    if (!line.trim()) continue;
    try {
      const node = JSON.parse(line);
      
      // Adapt to MemoryGraphEvent schema
      let event = null;
      if (node.type === 'EvolutionEvent') {
        event = node;
      } else if (node.type === 'MemoryGraphEvent' && node.kind === 'outcome') {
        // Construct a virtual EvolutionEvent from outcome node
        event = {
          type: 'EvolutionEvent',
          id: node.id,
          intent: node.mutation ? node.mutation.category : 'unknown',
          genes_used: node.gene ? [node.gene.id] : [],
          outcome: node.outcome
        };
      }

      if (event) {
        events.push(event);
        
        // Track genes
        if (event.genes_used && Array.isArray(event.genes_used)) {
          for (const geneId of event.genes_used) {
            if (!genes[geneId]) genes[geneId] = { used: 0, success: 0 };
            genes[geneId].used++;
            if (event.outcome && event.outcome.status === 'success') {
              genes[geneId].success++;
            }
          }
        }

        // Track failures
        if (event.outcome && event.outcome.status !== 'success') {
          const reason = event.outcome.reason || 'unknown';
          failurePatterns[reason] = (failurePatterns[reason] || 0) + 1;
        }

        // Stagnation detection
        if (lastEvent && lastEvent.outcome && event.outcome && 
            lastEvent.outcome.status === event.outcome.status &&
            lastEvent.intent === event.intent && 
            JSON.stringify(lastEvent.genes_used) === JSON.stringify(event.genes_used)) {
          streak++;
        } else {
          streak = 0;
        }
        lastEvent = event;
      }
    } catch (e) {
      // Ignore parse errors
    }
  }

  if (streak >= 3) stagnation = true;

  const successCount = events.filter(e => e.outcome && e.outcome.status === 'success').length;
  const successRate = events.length > 0 ? successCount / events.length : 0;

  const topGenes = Object.entries(genes)
    .map(([id, stats]) => ({
      id,
      used: stats.used,
      success_rate: stats.used > 0 ? stats.success / stats.used : 0
    }))
    .sort((a, b) => b.success_rate - a.success_rate)
    .slice(0, 5);

  const topFailures = Object.entries(failurePatterns)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([reason, count]) => ({ reason, count }));

  const recommendations = [];
  if (stagnation) {
    recommendations.push("DETECTED STAGNATION: Switch INTENT or GENE immediately.");
  }
  if (successRate < 0.5) {
    recommendations.push("LOW SUCCESS RATE: Focus on REPAIR intent.");
  }
  
  // Recent trend (last 5)
  const recentEvents = events.slice(-5);
  const recentSuccess = recentEvents.filter(e => e.outcome && e.outcome.status === 'success').length;
  const recentRate = recentEvents.length > 0 ? recentSuccess / recentEvents.length : 0;

  return {
    total_cycles: events.length,
    overall_success_rate: parseFloat(successRate.toFixed(2)),
    recent_success_rate: parseFloat(recentRate.toFixed(2)),
    stagnation_detected: stagnation,
    stagnation_streak: streak,
    top_genes: topGenes,
    top_failures: topFailures,
    recommendations
  };
}

// CLI
if (require.main === module) {
  analyzeState().then(report => console.log(JSON.stringify(report, null, 2)));
}

module.exports = { analyzeState };
