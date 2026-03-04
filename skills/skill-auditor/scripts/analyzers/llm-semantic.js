/**
 * LLM Semantic Analyzer - Advanced semantic understanding of skill behavior
 * Uses OpenClaw's API to evaluate findings against skill description
 */

const path = require('path');

// Check if node-fetch is available (Node.js < 18 compatibility)
let fetch;
try {
  fetch = require('node-fetch');
} catch (e) {
  if (typeof globalThis.fetch !== 'undefined') {
    fetch = globalThis.fetch;
  } else {
    fetch = null;
  }
}

// ─── OpenClaw API integration ──────────────────────────────────────

class SemanticAnalyzer {
  constructor(options = {}) {
    this.gatewayUrl = options.gatewayUrl || 'http://localhost:18789';
    this.model = options.model || 'anthropic/claude-haiku-4-20250201'; // Fast & cheap for semantic checks
    this.timeout = options.timeout || 30000;
  }

  async analyzeFindings(skillMeta, findings) {
    if (!fetch) {
      throw new Error('Fetch not available — use Node.js 18+ or install node-fetch');
    }

    // Group findings by category for batch analysis
    const categories = this.groupFindingsByCategory(findings);
    const results = [];

    for (const [category, categoryFindings] of Object.entries(categories)) {
      try {
        const analysis = await this.analyzeFindingCategory(skillMeta, category, categoryFindings);
        results.push(...analysis);
      } catch (e) {
        // Add error finding for failed analysis
        results.push({
          id: 'llm-semantic-error',
          category: 'Analysis Error',
          severity: 'low',
          file: '',
          line: 0,
          snippet: '',
          explanation: `LLM semantic analysis failed for ${category}: ${e.message}`,
          analyzer: 'llm-semantic'
        });
      }
    }

    return results;
  }

  groupFindingsByCategory(findings) {
    const groups = {};
    for (const finding of findings) {
      if (!groups[finding.category]) {
        groups[finding.category] = [];
      }
      groups[finding.category].push(finding);
    }
    return groups;
  }

  async analyzeFindingCategory(skillMeta, category, findings) {
    const prompt = this.buildSemanticPrompt(skillMeta, category, findings);
    
    try {
      const response = await fetch(`${this.gatewayUrl}/api/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: this.model,
          messages: [
            {
              role: 'system', 
              content: 'You are a security analyst evaluating whether detected code patterns match a skill\'s stated purpose. Be precise and objective.'
            },
            { 
              role: 'user', 
              content: prompt 
            }
          ],
          temperature: 0.1,
          max_tokens: 1000
        }),
        timeout: this.timeout
      });

      if (!response.ok) {
        throw new Error(`OpenClaw API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const analysisText = data.choices[0].message.content;
      
      return this.parseLLMAnalysis(analysisText, category, findings);
      
    } catch (e) {
      throw new Error(`OpenClaw API request failed: ${e.message}`);
    }
  }

  buildSemanticPrompt(skillMeta, category, findings) {
    const findingDescriptions = findings.map((f, i) => 
      `${i+1}. ${f.explanation} (File: ${f.file}:${f.line})`
    ).join('\n');

    return `# Skill Security Analysis

**Skill Name:** ${skillMeta.name}
**Description:** ${skillMeta.description}

**Detected Behavior Category:** ${category}
**Specific Findings:**
${findingDescriptions}

**Question:** Do these detected behaviors legitimately match the skill's stated purpose and description?

For each finding, evaluate:
1. **Legitimate** - The behavior directly supports the stated purpose
2. **Questionable** - The behavior might be related but seems excessive 
3. **Suspicious** - The behavior doesn't match the description and could be malicious

Provide your analysis in this format:
\`\`\`
Finding 1: [LEGITIMATE/QUESTIONABLE/SUSPICIOUS]
Reasoning: [Brief explanation]

Finding 2: [LEGITIMATE/QUESTIONABLE/SUSPICIOUS] 
Reasoning: [Brief explanation]

Overall Assessment: [LEGITIMATE/QUESTIONABLE/SUSPICIOUS]
Confidence: [HIGH/MEDIUM/LOW]
\`\`\`

Be conservative — when in doubt, mark as QUESTIONABLE.`;
  }

  parseLLMAnalysis(analysisText, category, findings) {
    const results = [];
    
    // Extract overall assessment and confidence
    const overallMatch = analysisText.match(/Overall Assessment:\s*(LEGITIMATE|QUESTIONABLE|SUSPICIOUS)/i);
    const confidenceMatch = analysisText.match(/Confidence:\s*(HIGH|MEDIUM|LOW)/i);
    
    const overallAssessment = overallMatch ? overallMatch[1].toUpperCase() : 'QUESTIONABLE';
    const confidence = confidenceMatch ? confidenceMatch[1].toUpperCase() : 'MEDIUM';

    // Parse individual finding assessments
    const findingMatches = [...analysisText.matchAll(/Finding (\d+):\s*(LEGITIMATE|QUESTIONABLE|SUSPICIOUS)\s*\nReasoning:\s*([^\n]+)/gi)];
    
    for (let i = 0; i < findings.length; i++) {
      const findingNumber = i + 1;
      const match = findingMatches.find(m => parseInt(m[1]) === findingNumber);
      
      let assessment = overallAssessment; // Fallback to overall
      let reasoning = 'LLM semantic analysis completed';
      
      if (match) {
        assessment = match[2].toUpperCase();
        reasoning = match[3].trim();
      }

      // Convert LLM assessment to severity adjustment
      const originalSeverity = findings[i].severity;
      let newSeverity = originalSeverity;
      let explanation = findings[i].explanation;
      
      switch (assessment) {
        case 'LEGITIMATE':
          newSeverity = this.downgradeSeverity(originalSeverity, 2); // Significant downgrade
          explanation += ` 🤖 LLM Analysis: Legitimate behavior matching skill purpose (${confidence.toLowerCase()} confidence)`;
          break;
        
        case 'QUESTIONABLE':
          newSeverity = this.downgradeSeverity(originalSeverity, 1); // Minor downgrade
          explanation += ` 🤖 LLM Analysis: Questionable behavior - review recommended (${confidence.toLowerCase()} confidence)`;
          break;
        
        case 'SUSPICIOUS':
          // Keep original severity or upgrade if low
          if (originalSeverity === 'low') newSeverity = 'medium';
          explanation += ` 🤖 LLM Analysis: Suspicious behavior not matching stated purpose (${confidence.toLowerCase()} confidence)`;
          break;
      }

      results.push({
        ...findings[i],
        severity: newSeverity,
        originalSeverity: originalSeverity !== newSeverity ? originalSeverity : findings[i].originalSeverity,
        explanation: explanation,
        llmAnalysis: {
          assessment: assessment,
          confidence: confidence,
          reasoning: reasoning,
          analyzer: 'llm-semantic'
        }
      });
    }

    return results;
  }

  downgradeSeverity(severity, levels = 1) {
    const severityLevels = ['low', 'medium', 'high', 'critical'];
    const currentIndex = severityLevels.indexOf(severity);
    if (currentIndex === -1) return severity;
    
    const newIndex = Math.max(0, currentIndex - levels);
    return severityLevels[newIndex];
  }
}

// ─── Main scanner function ─────────────────────────────────────────

async function analyzeFindings(skillMeta, findings, options = {}) {
  if (!options.useLLM) {
    // Add info notice that LLM analysis is available but not enabled
    return [{
      id: 'llm-not-enabled',
      category: 'Info',
      severity: 'info',
      file: '',
      line: 0,
      snippet: '',
      explanation: 'LLM semantic analysis available but not enabled. Use --use-llm flag for advanced intent matching',
      analyzer: 'llm-semantic'
    }];
  }

  try {
    const analyzer = new SemanticAnalyzer(options);
    return await analyzer.analyzeFindings(skillMeta, findings);
  } catch (e) {
    return [{
      id: 'llm-analysis-error',
      category: 'Error',
      severity: 'medium',
      file: '',
      line: 0,
      snippet: '',
      explanation: `LLM semantic analysis failed: ${e.message}`,
      analyzer: 'llm-semantic'
    }];
  }
}

// ─── Capability detection ──────────────────────────────────────────

function checkCapability() {
  const hasFetch = !!fetch;
  
  return {
    available: hasFetch,
    dependencies: fetch ? [] : ['node-fetch (for Node.js < 18)'],
    requirements: [
      'OpenClaw gateway running on localhost:18789',
      'Internet connection (for LLM API)',
      'Valid API key configured in OpenClaw'
    ],
    installCommand: hasFetch ? 'Start OpenClaw gateway' : 'npm install node-fetch',
    description: 'Semantic analysis of findings using LLM to understand intent vs behavior',
    status: {
      fetch: hasFetch ? 'available' : 'missing'
    }
  };
}

module.exports = {
  analyzeFindings,
  checkCapability,
  SemanticAnalyzer
};