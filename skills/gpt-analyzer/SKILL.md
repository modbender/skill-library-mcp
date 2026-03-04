---
id: gpt-analyzer
version: 1.0.0
name: GPT Analyzer
description: GPT-specific pattern detection with model fingerprinting and version identification
author: NeoClaw Team
category: detection
tags:
  - ai-detection
  - gpt
  - pattern-matching
  - model-fingerprinting
dependencies: []
---

# GPT Analyzer

Specialized detection for GPT-generated content with model-specific pattern recognition.

## Implementation

```javascript
/**
 * Analyze text for GPT-specific patterns and fingerprints
 * @param {string} text - Text to analyze
 * @param {object} options - Configuration options
 * @returns {object} Analysis result with model identification
 */
async function analyzeGPTContent(text, options = {}) {
  const {
    detectVersion = true,
    checkWatermarks = true,
    minConfidence = 0.7
  } = options;

  const normalizedText = text.toLowerCase();
  const wordCount = text.split(/\s+/).length;

  // GPT-specific phrases (stronger indicators)
  const gptPhrases = {
    'gpt-4': [
      'delve into', 'landscape of', 'realm of', 'it\'s important to note',
      'multifaceted', 'nuanced', 'comprehensive', 'holistic approach'
    ],
    'gpt-3.5': [
      'as an ai language model', 'i don\'t have personal', 'i apologize for',
      'certainly', 'absolutely', 'furthermore', 'moreover'
    ],
    'common': [
      'it\'s worth noting', 'keep in mind', 'in conclusion',
      'to summarize', 'in summary', 'navigate the', 'tapestry of'
    ]
  };

  // Model fingerprinting
  let gpt4Score = 0;
  let gpt35Score = 0;
  let commonScore = 0;
  const foundPhrases = [];

  // Check GPT-4 specific patterns
  for (const phrase of gptPhrases['gpt-4']) {
    if (normalizedText.includes(phrase)) {
      gpt4Score += 0.2;
      foundPhrases.push({ phrase, model: 'gpt-4' });
    }
  }

  // Check GPT-3.5 specific patterns
  for (const phrase of gptPhrases['gpt-3.5']) {
    if (normalizedText.includes(phrase)) {
      gpt35Score += 0.2;
      foundPhrases.push({ phrase, model: 'gpt-3.5' });
    }
  }

  // Check common GPT patterns
  for (const phrase of gptPhrases['common']) {
    if (normalizedText.includes(phrase)) {
      commonScore += 0.1;
      foundPhrases.push({ phrase, model: 'common' });
    }
  }

  // Structure analysis
  const hasNumberedLists = (text.match(/\n\d+\./g) || []).length >= 3;
  const hasBulletPoints = (text.match(/\n[•\-\*]/g) || []).length >= 3;
  const structureScore = (hasNumberedLists || hasBulletPoints) ? 0.15 : 0;

  // Sentence uniformity
  const sentences = text.split(/[.!?]+/).filter(s => s.trim());
  const avgLength = sentences.reduce((sum, s) => sum + s.length, 0) / sentences.length;
  const variance = sentences.reduce((sum, s) => sum + Math.pow(s.length - avgLength, 2), 0) / sentences.length;
  const uniformityScore = variance < 500 ? 0.1 : 0;

  // Calculate confidence
  const totalScore = gpt4Score + gpt35Score + commonScore + structureScore + uniformityScore;
  const confidence = Math.min(totalScore, 1.0);

  // Determine model
  let detectedModel = 'unknown';
  if (gpt4Score > gpt35Score && gpt4Score > 0) {
    detectedModel = 'gpt-4';
  } else if (gpt35Score > gpt4Score && gpt35Score > 0) {
    detectedModel = 'gpt-3.5';
  } else if (commonScore > 0) {
    detectedModel = 'gpt-family';
  }

  const isGPT = confidence >= minConfidence;

  return {
    isGPT,
    confidence: Math.round(confidence * 100),
    detectedModel: isGPT ? detectedModel : 'not-gpt',
    scores: {
      gpt4: Math.round(gpt4Score * 100) / 100,
      gpt35: Math.round(gpt35Score * 100) / 100,
      common: Math.round(commonScore * 100) / 100,
      structure: Math.round(structureScore * 100) / 100,
      uniformity: Math.round(uniformityScore * 100) / 100
    },
    indicators: {
      foundPhrases: foundPhrases.length,
      hasStructure: hasNumberedLists || hasBulletPoints,
      avgSentenceLength: Math.round(avgLength),
      sentenceVariance: Math.round(variance)
    },
    recommendation: confidence >= 0.85 ? 'Very likely GPT' :
                     confidence >= 0.70 ? 'Likely GPT' :
                     confidence >= 0.50 ? 'Possibly GPT' :
                     'Unlikely GPT or human-written'
  };
}

// Export for OpenClaw
module.exports = {
  analyzeGPTContent
};
```

## Usage

```javascript
const result = await skills.gptAnalyzer.analyzeGPTContent(text);

if (result.isGPT) {
  console.log(`GPT detected: ${result.detectedModel} (${result.confidence}% confidence)`);
}
```

## Configuration

```json
{
  "detectVersion": true,
  "minConfidence": 0.7
}
```
