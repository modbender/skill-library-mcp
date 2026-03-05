/**
 * @fileoverview Quality scoring for subagent outputs using 8-dimension rubric
 * @module subagent-architecture/lib/quality-scorer
 * @license MIT
 * 
 * Implements objective quality assessment framework
 * Target score: 7+ for production use
 */

// Lazy-load failure tracer to avoid hard dep if lib/ isn't present
let _failureTracer = null;
function getFailureTracer() {
  if (_failureTracer !== null) return _failureTracer;
  try {
    _failureTracer = require('../../../lib/failure-tracer');
  } catch (_) {
    _failureTracer = false; // Not available — skip trace capture
  }
  return _failureTracer;
}

/**
 * 8-dimension quality rubric definitions
 * Each dimension scored 1-10
 */
const RUBRIC_DIMENSIONS = {
  specificity: {
    name: 'Specificity',
    description: 'Concrete details vs vague generalizations',
    poor: 'Vague generalizations, no concrete details',
    good: 'Some concrete details mixed with generalizations',
    excellent: 'Precise, actionable specifics with examples'
  },
  actionability: {
    name: 'Actionability',
    description: 'Clear next steps provided',
    poor: 'No clear next steps or implementation guidance',
    good: 'Suggestions provided but not step-by-step',
    excellent: 'Step-by-step implementation plan with examples'
  },
  evidence: {
    name: 'Evidence',
    description: 'Claims backed by sources',
    poor: 'Unsourced claims, speculation',
    good: 'Some citations, key claims sourced',
    excellent: 'Every claim sourced with URLs and dates'
  },
  structure: {
    name: 'Structure',
    description: 'Organization and scannability',
    poor: 'Stream-of-consciousness, hard to navigate',
    good: 'Basic organization with headings',
    excellent: 'Scannable hierarchy with summaries'
  },
  completeness: {
    name: 'Completeness',
    description: 'Coverage of key aspects',
    poor: 'Missing key aspects or requirements',
    good: 'Most areas covered, minor gaps',
    excellent: 'Comprehensive, gaps explicitly documented'
  },
  clarity: {
    name: 'Clarity',
    description: 'Writing quality and comprehension',
    poor: 'Confusing, requires multiple reads',
    good: 'Mostly clear, some ambiguity',
    excellent: 'Crystal clear, unambiguous language'
  },
  relevance: {
    name: 'Relevance',
    description: 'Addresses the actual question',
    poor: 'Tangential or off-topic content',
    good: 'Addresses question with some tangents',
    excellent: 'Laser-focused on exact question asked'
  },
  efficiency: {
    name: 'Efficiency',
    description: 'Value per token/cost',
    poor: 'Verbose, low information density',
    good: 'Reasonable density, some fluff',
    excellent: 'High information density, no waste'
  }
};

/**
 * Default scoring weights (all equal)
 * Can be customized per use case
 */
const DEFAULT_WEIGHTS = {
  specificity: 1.0,
  actionability: 1.0,
  evidence: 1.0,
  structure: 1.0,
  completeness: 1.0,
  clarity: 1.0,
  relevance: 1.0,
  efficiency: 1.0
};

/**
 * Score subagent output against quality rubric
 * 
 * @param {string|Object} output - Output text or structured result
 * @param {Object} [rubric] - Custom rubric overrides
 * @param {Object} [options] - Scoring options
 * @param {Object} [options.weights] - Custom dimension weights
 * @param {boolean} [options.auto_score=false] - Use heuristics for automatic scoring
 * @returns {Object} Quality assessment with scores and recommendations
 * 
 * @example
 * const score = scoreSubagentOutput(researcherOutput, null, { auto_score: true });
 * console.log(`Overall: ${score.overall_score}/10`);
 * if (score.overall_score < 7) {
 *   console.log('Recommendations:', score.recommendations);
 * }
 */
function scoreSubagentOutput(output, rubric = null, options = {}) {
  const {
    weights = DEFAULT_WEIGHTS,
    auto_score = false,
    label = null,           // Optional: subagent label for trace capture
    workspaceRoot = null    // Optional: workspace root for trace capture
  } = options;

  const dimensions = rubric || RUBRIC_DIMENSIONS;
  const dimension_scores = {};
  
  if (auto_score) {
    // Heuristic-based automatic scoring
    const text = typeof output === 'string' ? output : JSON.stringify(output);
    
    dimension_scores.specificity = scoreSpecificity(text);
    dimension_scores.actionability = scoreActionability(text);
    dimension_scores.evidence = scoreEvidence(text);
    dimension_scores.structure = scoreStructure(text);
    dimension_scores.completeness = scoreCompleteness(text);
    dimension_scores.clarity = scoreClarity(text);
    dimension_scores.relevance = scoreRelevance(text);
    dimension_scores.efficiency = scoreEfficiency(text);
  } else {
    // Manual scoring (return template)
    for (const dim of Object.keys(dimensions)) {
      dimension_scores[dim] = null;  // Requires manual input
    }
  }

  // Calculate weighted overall score
  let overall_score = null;
  if (auto_score) {
    const total_weight = Object.values(weights).reduce((sum, w) => sum + w, 0);
    const weighted_sum = Object.entries(dimension_scores).reduce((sum, [dim, score]) => {
      return sum + (score * (weights[dim] || 1.0));
    }, 0);
    overall_score = weighted_sum / total_weight;
  }

  // Generate recommendations
  const recommendations = generateRecommendations(dimension_scores, dimensions);

  const result = {
    overall_score: overall_score ? Math.round(overall_score * 10) / 10 : null,
    dimension_scores: dimension_scores,
    recommendations: recommendations,
    rubric: dimensions,
    pass: overall_score ? overall_score >= 7.0 : null
  };

  // Capture failure trace when score < 7 (auto_score mode only)
  if (auto_score && overall_score !== null && overall_score < 7) {
    const tracer = getFailureTracer();
    if (tracer) {
      const text = typeof output === 'string' ? output : JSON.stringify(output);
      // Only trace if output has tool call indicators or is notably bad
      const hasToolHints = /tool_use|function_call|exec\(|browser\(|actions?\s*:\s*\[/i.test(text);
      if (hasToolHints || overall_score < 5) {
        const traceLabel = label || 'unlabeled';
        try {
          tracer.captureFailureTrace(traceLabel, overall_score, output, workspaceRoot);
        } catch (_) {
          // Never let trace capture crash the scorer
        }
      }
    }
  }

  return result;
}

/**
 * Heuristic scoring functions (auto_score mode)
 */

function scoreSpecificity(text) {
  // Check for concrete details: numbers, specific names, examples
  let score = 5;  // Start neutral
  
  // Has numbers/metrics
  if (/\d+%|\d+\.\d+|\$\d+/.test(text)) score += 1;
  
  // Has specific examples (e.g., "For example", "Such as")
  if (/for example|such as|e\.g\.|specifically/i.test(text)) score += 1;
  
  // Has code blocks or commands
  if (/```|`[^`]+`/.test(text)) score += 1;
  
  // Avoids vague words
  const vague_words = /\b(might|maybe|possibly|perhaps|generally|usually)\b/gi;
  const vague_count = (text.match(vague_words) || []).length;
  const word_count = text.split(/\s+/).length;
  if (vague_count / word_count < 0.01) score += 1;
  
  // Has specific tools/technologies mentioned
  if (/[A-Z][a-z]+\.(js|py|rb|go|rs)|npm|pip|cargo|git/i.test(text)) score += 1;
  
  return Math.min(10, Math.max(1, score));
}

function scoreActionability(text) {
  let score = 5;
  
  // Has step-by-step instructions (numbered or bulleted)
  if (/^\s*[-*\d]+[\.)]\s+/m.test(text)) score += 2;
  
  // Has action verbs
  const action_verbs = /\b(install|run|execute|create|modify|delete|update|configure)\b/gi;
  const action_count = (text.match(action_verbs) || []).length;
  if (action_count > 5) score += 2;
  
  // Has code snippets or commands
  if (/```|`[^`]+`/.test(text)) score += 1;
  
  return Math.min(10, Math.max(1, score));
}

function scoreEvidence(text) {
  let score = 5;
  
  // Has URLs
  const url_count = (text.match(/https?:\/\/[^\s)]+/g) || []).length;
  if (url_count > 0) score += 1;
  if (url_count > 3) score += 1;
  
  // Has dates (suggests temporal awareness)
  if (/20\d{2}-\d{2}-\d{2}|20\d{2}\/\d{2}\/\d{2}/.test(text)) score += 1;
  
  // Has source citations (Author, Year) or "Source:"
  if (/\(([A-Z][a-z]+,?\s+)+20\d{2}\)|Source:/i.test(text)) score += 1;
  
  // Avoids speculation keywords
  if (!/\b(I think|I believe|probably|likely)\b/i.test(text)) score += 1;
  
  return Math.min(10, Math.max(1, score));
}

function scoreStructure(text) {
  let score = 5;
  
  // Has markdown headings
  const heading_count = (text.match(/^#{1,3}\s+/gm) || []).length;
  if (heading_count > 2) score += 2;
  if (heading_count > 5) score += 1;
  
  // Has summary section
  if (/## ?(Summary|Executive Summary|Overview)/i.test(text)) score += 1;
  
  // Has table of contents or clear sections
  if (/## ?Table of Contents|^#{2,3}\s+\d+\./m.test(text)) score += 1;
  
  return Math.min(10, Math.max(1, score));
}

function scoreCompleteness(text) {
  let score = 7;  // Assume complete unless red flags
  
  // Check for explicit gap documentation
  if (/\b(unknown|unclear|missing|gap|limitation|not covered)\b/i.test(text)) {
    score += 1;  // Bonus for acknowledging gaps
  }
  
  // Penalize very short outputs (likely incomplete)
  const word_count = text.split(/\s+/).length;
  if (word_count < 100) score -= 3;
  else if (word_count < 300) score -= 1;
  
  return Math.min(10, Math.max(1, score));
}

function scoreClarity(text) {
  let score = 7;  // Assume clear unless problems
  
  // Check for jargon overload
  const word_count = text.split(/\s+/).length;
  const complex_words = text.match(/\b\w{12,}\b/g) || [];
  if (complex_words.length / word_count > 0.05) score -= 1;
  
  // Check for overly long sentences
  const sentences = text.split(/[.!?]+/);
  const avg_sentence_length = word_count / sentences.length;
  if (avg_sentence_length > 30) score -= 1;
  
  // Bonus for explanations
  if (/\(i\.e\.|i\.e\.,|that is,|in other words/i.test(text)) score += 1;
  
  return Math.min(10, Math.max(1, score));
}

function scoreRelevance(text) {
  // This requires context (original question) - default to neutral
  // In practice, manual scoring recommended for this dimension
  return 7;  // Assume relevant unless manual review says otherwise
}

function scoreEfficiency(text) {
  let score = 7;
  
  // Check information density
  const word_count = text.split(/\s+/).length;
  const info_markers = (text.match(/\d+|https?:\/\/|```|#{1,3}\s+/g) || []).length;
  const density = info_markers / (word_count / 100);  // Markers per 100 words
  
  if (density > 5) score += 1;  // High density
  if (density < 2) score -= 1;  // Low density
  
  // Penalize excessive length (>2000 words without good reason)
  if (word_count > 2000 && info_markers / word_count < 0.02) {
    score -= 2;  // Long and low-density = inefficient
  }
  
  return Math.min(10, Math.max(1, score));
}

/**
 * Generate improvement recommendations based on scores
 * 
 * @param {Object} scores - Dimension scores
 * @param {Object} rubric - Rubric definitions
 * @returns {Array} Recommendations list
 * @private
 */
function generateRecommendations(scores, rubric) {
  const recommendations = [];
  
  for (const [dimension, score] of Object.entries(scores)) {
    if (score === null) continue;  // Manual scoring mode
    
    if (score < 7) {
      const def = rubric[dimension];
      recommendations.push({
        dimension: def.name,
        current_score: score,
        target_score: 7,
        improvement: def.excellent,
        priority: score < 5 ? 'high' : 'medium'
      });
    }
  }
  
  // Sort by priority (high first) then score (lowest first)
  recommendations.sort((a, b) => {
    if (a.priority === 'high' && b.priority !== 'high') return -1;
    if (a.priority !== 'high' && b.priority === 'high') return 1;
    return a.current_score - b.current_score;
  });
  
  return recommendations;
}

/**
 * Create manual scoring template for human review
 * 
 * @param {Object} [customRubric] - Custom rubric overrides
 * @returns {Object} Template with scoring instructions
 * 
 * @example
 * const template = createScoringTemplate();
 * // Fill in scores manually, then call scoreSubagentOutput with completed scores
 */
function createScoringTemplate(customRubric = null) {
  const rubric = customRubric || RUBRIC_DIMENSIONS;
  const template = {};
  
  for (const [key, def] of Object.entries(rubric)) {
    template[key] = {
      name: def.name,
      description: def.description,
      score: null,  // Fill in 1-10
      notes: '',    // Optional reviewer notes
      scale: {
        '1-3': def.poor,
        '4-6': def.good,
        '7-10': def.excellent
      }
    };
  }
  
  return template;
}

/**
 * Self-audit checklist for subagent outputs
 * 
 * @param {string|Object} output - Output to audit
 * @returns {Object} Checklist with pass/fail items
 */
function selfAuditChecklist(output) {
  const text = typeof output === 'string' ? output : JSON.stringify(output);
  
  return {
    every_claim_sourced: {
      pass: /https?:\/\//.test(text),
      details: 'At least one URL citation found'
    },
    contradictions_addressed: {
      pass: /\b(contradiction|conflict|however|but|alternatively)\b/i.test(text),
      details: 'Contrasting viewpoints mentioned'
    },
    tradeoffs_included: {
      pass: /\b(trade-?off|downside|limitation|risk|disadvantage)\b/i.test(text),
      details: 'Acknowledges trade-offs or limitations'
    },
    cost_estimate_provided: {
      pass: /\$\d+|\d+\s*(hour|minute|day)/i.test(text),
      details: 'Contains cost or time estimate'
    },
    integration_documented: {
      pass: /\b(integrat|interface|api|endpoint|hook)\b/i.test(text),
      details: 'Mentions integration points'
    },
    rollback_strategy: {
      pass: /\b(rollback|revert|undo|restore|backup)\b/i.test(text),
      details: 'Includes rollback or recovery strategy'
    },
    success_criteria: {
      pass: /\b(success|criteria|metric|measure|verify|validate)\b/i.test(text),
      details: 'Defines success criteria or validation'
    },
    limitations_listed: {
      pass: /\b(limitation|constraint|gap|caveat|assumption)\b/i.test(text),
      details: 'Explicitly lists limitations'
    }
  };
}

module.exports = {
  scoreSubagentOutput,
  createScoringTemplate,
  selfAuditChecklist,
  RUBRIC_DIMENSIONS,
  DEFAULT_WEIGHTS
};
