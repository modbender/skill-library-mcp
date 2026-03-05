---
id: nlp-toolkit
version: 1.0.0
name: NLP Toolkit
description: Advanced NLP with perplexity scoring, burstiness analysis, and entropy calculation
author: NeoClaw Team
category: detection
tags:
  - nlp
  - perplexity
  - burstiness
  - entropy
dependencies: []
---

# NLP Toolkit

Advanced NLP analysis for AI content detection using statistical measures.

## Implementation

```javascript
/**
 * Analyze text using NLP metrics
 * @param {string} text - Text to analyze
 * @param {object} options - Configuration options
 * @returns {object} NLP analysis results
 */
async function analyzeText(text, options = {}) {
  const {
    perplexityThreshold = 45.0,
    burstinessThreshold = 0.35,
    minTextLength = 50
  } = options;

  if (text.length < minTextLength) {
    return {
      error: 'Text too short for analysis',
      minLength: minTextLength
    };
  }

  // Calculate perplexity (simplified)
  const perplexity = calculatePerplexity(text);

  // Calculate burstiness
  const burstiness = calculateBurstiness(text);

  // Calculate entropy
  const entropy = calculateEntropy(text);

  // Token distribution analysis
  const tokenStats = analyzeTokenDistribution(text);

  // Determine if AI-generated
  const isAI = perplexity < perplexityThreshold && burstiness < burstinessThreshold;
  const confidence = calculateConfidence(perplexity, burstiness, entropy);

  return {
    isAI,
    confidence: Math.round(confidence * 100),
    metrics: {
      perplexity: Math.round(perplexity * 100) / 100,
      burstiness: Math.round(burstiness * 100) / 100,
      entropy: Math.round(entropy * 100) / 100
    },
    tokenStats,
    thresholds: {
      perplexity: perplexityThreshold,
      burstiness: burstinessThreshold
    },
    explanation: isAI ? 
      'Low perplexity and uniform burstiness suggest AI generation' :
      'Natural variation in metrics suggests human writing'
  };
}

/**
 * Calculate perplexity score (simplified)
 */
function calculatePerplexity(text) {
  const words = text.toLowerCase().split(/\s+/);
  const uniqueWords = new Set(words);
  
  // Simplified perplexity: ratio of unique words to total
  // Real perplexity requires language model
  const ratio = uniqueWords.size / words.length;
  const perplexity = 100 / ratio; // Inverse relationship
  
  return Math.min(perplexity, 100);
}

/**
 * Calculate burstiness (variation in sentence length)
 */
function calculateBurstiness(text) {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim());
  if (sentences.length < 2) return 0;

  const lengths = sentences.map(s => s.split(/\s+/).length);
  const avg = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const variance = lengths.reduce((sum, len) => sum + Math.pow(len - avg, 2), 0) / lengths.length;
  const stdDev = Math.sqrt(variance);

  // Burstiness: coefficient of variation
  const burstiness = stdDev / avg;

  return Math.min(burstiness, 1.0);
}

/**
 * Calculate Shannon entropy
 */
function calculateEntropy(text) {
  const chars = text.toLowerCase().split('');
  const freq = {};

  // Count character frequencies
  for (const char of chars) {
    freq[char] = (freq[char] || 0) + 1;
  }

  // Calculate entropy
  let entropy = 0;
  const total = chars.length;

  for (const count of Object.values(freq)) {
    const p = count / total;
    entropy -= p * Math.log2(p);
  }

  return entropy;
}

/**
 * Analyze token distribution
 */
function analyzeTokenDistribution(text) {
  const words = text.toLowerCase().split(/\s+/);
  const uniqueWords = new Set(words);

  return {
    totalWords: words.length,
    uniqueWords: uniqueWords.size,
    vocabularyRichness: Math.round((uniqueWords.size / words.length) * 100) / 100
  };
}

/**
 * Calculate overall confidence
 */
function calculateConfidence(perplexity, burstiness, entropy) {
  // Lower perplexity = more AI-like
  const perplexityScore = Math.max(0, 1 - (perplexity / 100));
  
  // Lower burstiness = more AI-like
  const burstinessScore = Math.max(0, 1 - (burstiness / 0.5));
  
  // Moderate entropy expected for AI
  const entropyScore = (entropy > 3.5 && entropy < 5.0) ? 0.8 : 0.4;

  const confidence = (perplexityScore + burstinessScore + entropyScore) / 3;
  return Math.min(confidence, 1.0);
}

// Export for OpenClaw
module.exports = {
  analyzeText,
  calculatePerplexity,
  calculateBurstiness,
  calculateEntropy
};
```

## Usage

```javascript
const result = await skills.nlpToolkit.analyzeText(text, {
  perplexityThreshold: 45.0,
  burstinessThreshold: 0.35
});

console.log(`AI Detection: ${result.isAI} (${result.confidence}% confidence)`);
console.log(`Perplexity: ${result.metrics.perplexity}`);
console.log(`Burstiness: ${result.metrics.burstiness}`);
```

## Configuration

```json
{
  "perplexityThreshold": 45.0,
  "burstinessThreshold": 0.35,
  "minTextLength": 50
}
```
