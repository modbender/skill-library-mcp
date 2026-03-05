/**
 * relevance.js - Smart fact relevance scoring for adaptive context injection
 * Part of Phase 4: Adaptive Context Injection
 */

import fetch from 'node-fetch';

const DEFAULT_OLLAMA_URL = 'http://localhost:11434';
const SCORING_TIMEOUT_MS = 30_000;

/**
 * Score a batch of facts for relevance to a message using local Ollama
 */
async function scoreFactsForRelevance(message, facts, options = {}) {
  const { 
    engine = 'ollama', 
    model, 
    limit = 50, 
    threshold = 0.3,
    ollamaUrl = DEFAULT_OLLAMA_URL
  } = options;

  if (facts.length === 0) return [];

  // For now, implement Ollama scoring. Can add Anthropic/OpenAI later.
  if (engine === 'ollama') {
    return await scoreWithOllama(message, facts, { model, limit, threshold, ollamaUrl });
  }
  
  throw new Error(`Scoring engine "${engine}" not implemented yet`);
}

/**
 * Score facts using Ollama (fast local scoring) with batching
 */
async function scoreWithOllama(message, facts, options) {
  const { model = 'llama3.1:8b', limit, threshold, ollamaUrl } = options;

  // Health check first (learned from earlier failures)
  const healthy = await ollamaHealthCheck(ollamaUrl);
  if (!healthy) {
    throw new Error(`Ollama not responding at ${ollamaUrl}`);
  }

  // Batch facts to avoid huge prompts (max 15 facts per call)
  const BATCH_SIZE = 15;
  const batches = [];
  for (let i = 0; i < facts.length; i += BATCH_SIZE) {
    batches.push(facts.slice(i, i + BATCH_SIZE));
  }

  const allScoredFacts = [];

  for (let batchIdx = 0; batchIdx < batches.length; batchIdx++) {
    const batch = batches[batchIdx];
    
    try {
      const prompt = buildScoringPrompt(message, batch);
      
      const response = await fetch(`${ollamaUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          prompt,
          stream: false,
          options: {
            temperature: 0.1,  // Low temp for consistent scoring
            num_predict: 512,  // Smaller since we're batching
            think: false
          }
        }),
        signal: AbortSignal.timeout(SCORING_TIMEOUT_MS)
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status} (batch ${batchIdx + 1})`);
      }

      const data = await response.json();
      const rawOutput = data.response?.trim();

      if (!rawOutput) {
        console.warn(`Empty response for batch ${batchIdx + 1}, defaulting to 0 scores`);
        continue;
      }

      // Parse scores and merge with original facts
      const scores = parseScores(rawOutput, batch.length);
      const batchScoredFacts = batch.map((fact, idx) => ({
        ...fact,
        relevance_score: scores[idx] || 0
      }));

      allScoredFacts.push(...batchScoredFacts);

    } catch (err) {
      console.warn(`Batch ${batchIdx + 1} failed: ${err.message}, skipping`);
      // Add batch with zero scores
      allScoredFacts.push(...batch.map(fact => ({
        ...fact,
        relevance_score: 0
      })));
    }
  }

  // Apply confidence/decay weighting (T-026)
  const { calculateAccessBoost } = await import('./db.js');
  
  const boostedFacts = allScoredFacts.map(fact => {
    const accessBoost = calculateAccessBoost(fact);
    return {
      ...fact,
      base_relevance_score: fact.relevance_score,
      access_boost: accessBoost,
      relevance_score: Math.min(1.0, fact.relevance_score + accessBoost)
    };
  });

  // Filter, sort, and limit
  const finalFacts = boostedFacts
    .filter(f => f.relevance_score >= threshold)
    .sort((a, b) => b.relevance_score - a.relevance_score)
    .slice(0, limit);

  return finalFacts;
}

/**
 * Build a compact scoring prompt
 */
function buildScoringPrompt(message, facts) {
  const factsList = facts
    .map((f, idx) => `${idx}: ${f.category}/${f.key} = ${f.value}`)
    .join('\n');

  return `Score how relevant each fact is to this message/query on a scale 0.0-1.0:

MESSAGE: "${message}"

FACTS:
${factsList}

Return only a comma-separated list of scores in order, like: 0.8, 0.2, 0.9, 0.1, 0.0
No explanations. Just the scores.`;
}

/**
 * Parse comma-separated scores from Ollama output
 */
function parseScores(output, expectedCount) {
  // Look for comma-separated numbers
  const scoreMatch = output.match(/([\d.,\s]+)/);
  if (!scoreMatch) {
    console.warn('Could not parse scores from:', output.substring(0, 100));
    return new Array(expectedCount).fill(0);
  }

  const scores = scoreMatch[1]
    .split(',')
    .map(s => parseFloat(s.trim()))
    .filter(n => !isNaN(n));

  // Pad or truncate to expected length
  while (scores.length < expectedCount) {
    scores.push(0);
  }
  
  return scores.slice(0, expectedCount);
}

/**
 * Quick Ollama health check
 */
async function ollamaHealthCheck(ollamaUrl, timeoutMs = 5000) {
  try {
    const response = await fetch(`${ollamaUrl}/api/tags`, {
      signal: AbortSignal.timeout(timeoutMs)
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Generate dynamic context injection based on message relevance
 */
async function generateDynamicContext(message, options = {}) {
  const { openDb, trackFactAccess } = await import('./db.js');
  const db = openDb();
  
  try {
    // Get all facts
    const allFacts = db.prepare('SELECT * FROM facts ORDER BY updated DESC').all();
    
    if (allFacts.length === 0) {
      return '# Dynamic Context\n\n(No facts available)\n';
    }

    // Score for relevance
    const scoredFacts = await scoreFactsForRelevance(message, allFacts, {
      ...options,
      limit: options.contextBudget || 20,  // Token budget control
      threshold: options.threshold || 0.4
    });

    // Track access for selected facts (T-027)
    const sessionId = options.sessionId || null;
    for (const fact of scoredFacts) {
      trackFactAccess(db, fact.id, sessionId);
    }

    // Group by category for readability
    const grouped = {};
    for (const fact of scoredFacts) {
      if (!grouped[fact.category]) grouped[fact.category] = [];
      grouped[fact.category].push(fact);
    }

    // Generate markdown
    let context = '# Dynamic Context\n\n';
    
    for (const [category, facts] of Object.entries(grouped)) {
      context += `## ${category}\n`;
      for (const fact of facts) {
        context += `- ${fact.key}: ${fact.value}\n`;
      }
      context += '\n';
    }

    context += `*${scoredFacts.length} relevant fact(s) selected*\n`;
    
    return context;

  } finally {
    db.close();
  }
}

export { 
  scoreFactsForRelevance, 
  generateDynamicContext,
  scoreWithOllama,
  ollamaHealthCheck
};