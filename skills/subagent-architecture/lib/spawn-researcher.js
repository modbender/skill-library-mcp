/**
 * @fileoverview Researcher specialist pattern implementation for multi-perspective research
 * @module subagent-architecture/lib/spawn-researcher
 * @license MIT
 * 
 * Implements multi-source validation, credibility scoring, contradiction handling
 * Features: Domain expertise, skeptical analysis, structured output
 */

/**
 * Trusted domain classifications for source credibility
 * Based on Agent Smith recommendations (2026-02-22)
 */
const TRUSTED_DOMAINS = [
  // Academic
  'arxiv.org', 'ieee.org', 'acm.org', 'scholar.google.com',
  // Official documentation
  'docs.python.org', 'developer.mozilla.org', 'nodejs.org',
  // Standards bodies
  'ietf.org', 'w3.org', 'iso.org',
  // Established tech journalism
  'arstechnica.com', 'lwn.net', 'nature.com', 'science.org'
];

const BLOG_DOMAINS = [
  'medium.com', 'dev.to', 'hashnode.com', 'substack.com',
  'wordpress.com', 'blogspot.com'
];

const VENDOR_DOMAINS = [
  // Cloud providers (marketing bias)
  'aws.amazon.com/blogs', 'cloud.google.com/blog', 'azure.microsoft.com/blog',
  // Framework authors (hype bias)
  'blog.react.dev', 'blog.angular.io', 'vuejs.org/blog'
];

/**
 * Assess source credibility (0-100 scale)
 * 
 * @param {Object} source - Source metadata
 * @param {string} source.url - Source URL
 * @param {string} source.domain - Extracted domain
 * @param {Date} source.publish_date - Publication date
 * @param {boolean} [source.author_verified=false] - Author credentials verified
 * @param {number} [source.author_citations=0] - Citation count
 * @returns {number} Credibility score (0-100)
 * @private
 */
function assessSourceCredibility(source) {
  let score = 50;  // Start neutral
  
  const domain = source.domain || extractDomain(source.url);
  
  // Domain reputation
  if (TRUSTED_DOMAINS.some(d => domain.includes(d))) {
    score += 30;
  } else if (BLOG_DOMAINS.some(d => domain.includes(d))) {
    score -= 10;
  } else if (VENDOR_DOMAINS.some(d => domain.includes(d))) {
    score -= 20;  // Marketing bias
  }
  
  // Recency (if publish_date provided)
  if (source.publish_date) {
    const age_days = (Date.now() - source.publish_date.getTime()) / (1000 * 60 * 60 * 24);
    if (age_days < 90) {
      score += 10;  // Recent
    } else if (age_days > 730) {
      score -= 15;  // Outdated (2+ years)
    }
  }
  
  // Author credentials
  if (source.author_verified) score += 10;
  if (source.author_citations > 100) score += 5;
  
  return Math.max(0, Math.min(100, score));
}

/**
 * Extract domain from URL
 * @private
 */
function extractDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return '';
  }
}

/**
 * Spawn researcher specialist for multi-source research
 * 
 * @param {Object} config - Researcher configuration
 * @param {string} config.domain - Research domain (e.g., "AI hardware", "web frameworks")
 * @param {string} config.question - Research question
 * @param {string} [config.perspective='neutral'] - Research bias: 'optimist', 'pessimist', 'pragmatist', 'neutral'
 * @param {number} [config.min_sources=3] - Minimum sources per claim
 * @param {number} [config.timeout_minutes=15] - Max execution time
 * @param {string} [config.model='sonnet'] - Model to use
 * @param {number} [config.credibility_threshold=40] - Minimum credibility score for sources
 * @param {Function} [config.spawn_fn] - Custom spawn function (for testing/mocking)
 * @returns {Promise<Object>} Research findings with sources and confidence
 * 
 * @example
 * const findings = await spawnResearcher({
 *   domain: "Web frameworks",
 *   question: "Should we adopt FrameworkX for production?",
 *   perspective: "pragmatist",
 *   min_sources: 3
 * });
 * // Returns: { findings: {...}, sources: [...], confidence: 0.8, cost: 0.55 }
 */
async function spawnResearcher(config) {
  const {
    domain,
    question,
    perspective = 'neutral',
    min_sources = 3,
    timeout_minutes = 15,
    model = 'sonnet',
    credibility_threshold = 40,
    spawn_fn = null
  } = config;

  // Validate required fields
  if (!domain) throw new Error('domain is required');
  if (!question) throw new Error('question is required');

  // Build personality based on perspective
  const personalities = {
    optimist: 'Optimistic analyst focused on opportunities and best-case scenarios. Highlights benefits and success stories. Still evidence-based.',
    pessimist: 'Skeptical analyst focused on risks and failure modes. Highlights downsides and known issues. Calls out hype and unverified claims.',
    pragmatist: 'Pragmatic analyst focused on current reality and real-world adoption. Data-driven, no speculation. Balanced view of trade-offs.',
    neutral: 'Objective analyst presenting all perspectives. Multi-source validation, contradictions addressed. No inherent bias.'
  };

  const personality = personalities[perspective] || personalities.neutral;

  // Build research task
  const task = `
RESEARCH TASK: ${question}

DOMAIN: ${domain}

PERSPECTIVE: ${perspective}

REQUIREMENTS:
1. Multi-source validation (minimum ${min_sources} independent sources per major claim)
2. Source credibility assessment (only cite sources with credibility > ${credibility_threshold})
3. Recency validation (prefer sources < 12 months old, note if using older)
4. Contradiction handling (address conflicting claims, don't ignore)
5. Evidence-backed (no speculation, mark uncertainties as "unclear")
6. Vendor claim validation (verify marketing claims with benchmarks/data)

OUTPUT FORMAT:
{
  "executive_summary": "3-5 sentence overview",
  "key_findings": [
    {
      "claim": "Specific finding",
      "evidence": ["Source 1 URL", "Source 2 URL", "Source 3 URL"],
      "confidence": "high|medium|low",
      "contradictions": "Any conflicting data found"
    }
  ],
  "recommendations": [
    {
      "action": "What to do",
      "rationale": "Why",
      "trade_offs": "Downsides/risks",
      "priority": "high|medium|low"
    }
  ],
  "data_gaps": ["What information is missing or unclear"],
  "sources": [
    {
      "url": "https://...",
      "title": "Source title",
      "date": "YYYY-MM-DD",
      "credibility": "assessed score 0-100",
      "key_points": ["What this source says"]
    }
  ]
}

QUALITY STANDARDS:
- Every claim has ≥${min_sources} sources
- Contradictions explicitly addressed
- No unsourced speculation
- Trade-offs included in recommendations
- Data gaps acknowledged
`.trim();

  // Spawn configuration
  const spawn_config = {
    label: `researcher-${domain.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}`,
    task: task,
    model: model,
    timeout_minutes: timeout_minutes,
    personality: personality
  };

  // Spawn researcher (use custom spawn_fn if provided)
  let result;
  try {
    if (spawn_fn) {
      result = await spawn_fn(spawn_config);
    } else {
      // In production, this would use actual sessions_spawn
      throw new Error('spawn_fn not provided - in production, use actual sessions_spawn');
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      cost: 0
    };
  }

  // Parse and validate output
  let parsed_output;
  try {
    parsed_output = typeof result.output === 'string' 
      ? JSON.parse(result.output) 
      : result.output;
  } catch (error) {
    return {
      success: false,
      error: 'Failed to parse research output as JSON',
      raw_output: result.output,
      cost: result.cost || 0
    };
  }

  // Assess source credibility
  if (parsed_output.sources) {
    parsed_output.sources = parsed_output.sources.map(source => {
      const credibility = assessSourceCredibility({
        url: source.url,
        domain: extractDomain(source.url),
        publish_date: source.date ? new Date(source.date) : null,
        author_verified: source.author_verified || false,
        author_citations: source.author_citations || 0
      });
      
      return {
        ...source,
        credibility_score: credibility,
        trusted: credibility >= credibility_threshold
      };
    });
  }

  // Calculate overall confidence
  const confidence = calculateConfidence(parsed_output, min_sources);

  return {
    success: true,
    findings: {
      executive_summary: parsed_output.executive_summary,
      key_findings: parsed_output.key_findings,
      recommendations: parsed_output.recommendations,
      data_gaps: parsed_output.data_gaps
    },
    sources: parsed_output.sources || [],
    confidence: confidence,
    cost: result.cost || 0,
    metadata: {
      domain: domain,
      perspective: perspective,
      model: model,
      timestamp: new Date().toISOString()
    }
  };
}

/**
 * Calculate overall research confidence based on source quality and coverage
 * 
 * @param {Object} output - Parsed research output
 * @param {number} min_sources - Required sources per claim
 * @returns {number} Confidence score (0-1)
 * @private
 */
function calculateConfidence(output, min_sources) {
  let confidence = 0.5;  // Start neutral
  
  // Check source count
  const source_count = (output.sources || []).length;
  if (source_count >= min_sources * 3) {
    confidence += 0.2;  // Many sources
  } else if (source_count < min_sources) {
    confidence -= 0.2;  // Too few sources
  }
  
  // Check source credibility
  if (output.sources) {
    const avg_credibility = output.sources.reduce((sum, s) => 
      sum + (s.credibility_score || 50), 0) / output.sources.length;
    
    if (avg_credibility > 70) {
      confidence += 0.2;  // High credibility
    } else if (avg_credibility < 40) {
      confidence -= 0.2;  // Low credibility
    }
  }
  
  // Check for contradictions addressed
  if (output.key_findings) {
    const has_contradictions = output.key_findings.some(f => 
      f.contradictions && f.contradictions.trim() !== ''
    );
    if (has_contradictions) {
      confidence += 0.1;  // Bonus for addressing contradictions
    }
  }
  
  // Check for data gaps acknowledged
  if (output.data_gaps && output.data_gaps.length > 0) {
    confidence += 0.05;  // Honest about limitations
  }
  
  return Math.max(0, Math.min(1, confidence));
}

/**
 * Spawn multiple researchers with different perspectives (multi-perspective pattern)
 * 
 * @param {Object} config - Multi-researcher configuration
 * @param {string} config.domain - Research domain
 * @param {string} config.question - Research question
 * @param {Array<string>} [config.perspectives=['optimist','pessimist','pragmatist']] - Perspectives to spawn
 * @param {Object} [config.options] - Options passed to each researcher
 * @returns {Promise<Object>} Synthesized findings from all perspectives
 * 
 * @example
 * const synthesis = await spawnMultiPerspective({
 *   domain: "Cloud databases",
 *   question: "Should we migrate to DatabaseX?",
 *   perspectives: ['optimist', 'pessimist', 'pragmatist']
 * });
 */
async function spawnMultiPerspective(config) {
  const {
    domain,
    question,
    perspectives = ['optimist', 'pessimist', 'pragmatist'],
    options = {}
  } = config;

  // Spawn all researchers in parallel
  const researchers = perspectives.map(perspective =>
    spawnResearcher({
      domain,
      question,
      perspective,
      ...options
    })
  );

  const results = await Promise.all(researchers);

  // Synthesize findings
  const all_findings = results.flatMap(r => r.findings?.key_findings || []);
  const all_sources = results.flatMap(r => r.sources || []);
  const all_recommendations = results.flatMap(r => r.findings?.recommendations || []);
  
  // Deduplicate sources by URL
  const unique_sources = [];
  const seen_urls = new Set();
  for (const source of all_sources) {
    if (!seen_urls.has(source.url)) {
      seen_urls.add(source.url);
      unique_sources.push(source);
    }
  }

  // Calculate aggregated confidence
  const avg_confidence = results.reduce((sum, r) => sum + (r.confidence || 0), 0) / results.length;
  const total_cost = results.reduce((sum, r) => sum + (r.cost || 0), 0);

  return {
    success: true,
    synthesis: {
      perspectives: perspectives,
      findings_by_perspective: results.map((r, i) => ({
        perspective: perspectives[i],
        executive_summary: r.findings?.executive_summary,
        confidence: r.confidence
      })),
      all_findings: all_findings,
      all_recommendations: all_recommendations,
      consensus: identifyConsensus(all_recommendations),
      divergence: identifyDivergence(all_findings)
    },
    sources: unique_sources,
    confidence: avg_confidence,
    cost: total_cost,
    metadata: {
      domain: domain,
      perspectives_used: perspectives,
      timestamp: new Date().toISOString()
    }
  };
}

/**
 * Identify consensus across multiple perspectives
 * @private
 */
function identifyConsensus(all_recommendations) {
  // Group recommendations by action
  const action_counts = {};
  
  for (const rec of all_recommendations) {
    const action = rec.action.toLowerCase();
    action_counts[action] = (action_counts[action] || 0) + 1;
  }
  
  // Find actions recommended by majority
  const threshold = all_recommendations.length / 2;
  const consensus = [];
  
  for (const [action, count] of Object.entries(action_counts)) {
    if (count > threshold) {
      consensus.push({
        action: action,
        agreement: `${count}/${all_recommendations.length} perspectives`,
        strength: count / all_recommendations.length
      });
    }
  }
  
  return consensus;
}

/**
 * Identify divergent findings across perspectives
 * @private
 */
function identifyDivergence(all_findings) {
  // Find findings with contradictions
  const divergent = all_findings.filter(f => 
    f.contradictions && f.contradictions.trim() !== ''
  );
  
  return divergent.map(f => ({
    claim: f.claim,
    contradiction: f.contradictions
  }));
}

module.exports = {
  spawnResearcher,
  spawnMultiPerspective,
  assessSourceCredibility,
  TRUSTED_DOMAINS,
  BLOG_DOMAINS,
  VENDOR_DOMAINS
};
