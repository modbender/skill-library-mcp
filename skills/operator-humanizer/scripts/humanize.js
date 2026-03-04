#!/usr/bin/env node

/**
 * AI Humanizer CLI
 * Command-line tool for detecting and removing AI writing patterns
 */

const fs = require('fs');
const path = require('path');

// Tier 1 AI vocabulary (dead giveaways)
const TIER1_WORDS = [
  'bustling', 'catalyst', 'cornerstone', 'crucial', 'comprehensive',
  'delve', 'delving', 'embark', 'empower', 'enduring', 'groundbreaking',
  'harness', 'indelible', 'invaluable', 'leverage', 'meticulous',
  'multifaceted', 'myriad', 'nestled', 'paramount', 'pivotal',
  'realm', 'reimagine', 'robust', 'seamless', 'synergy',
  'tapestry', 'testament', 'transformative', 'vibrant'
];

// Tier 1 phrases
const TIER1_PHRASES = [
  'delve into', 'embark on a journey', 'harness the power',
  'in the realm of', 'serves as a testament', 'stands as a testament',
  'marking a pivotal moment', 'plays a crucial role',
  'the evolving landscape', 'the intricate tapestry',
  'in today\'s digital age', 'in today\'s fast-paced',
  'without further ado', 'it is worth noting'
];

// Tier 2 AI vocabulary (suspicious)
const TIER2_WORDS = [
  'additionally', 'align', 'bolster', 'catalyze', 'cultivate',
  'disrupt', 'elevate', 'encompass', 'facilitate', 'foster',
  'garner', 'holistic', 'illuminate', 'innovative', 'intricate',
  'juxtapose', 'nuanced', 'optimize', 'paradigm', 'proactive',
  'profound', 'quintessential', 'scalable', 'streamline',
  'synergize', 'ubiquitous', 'underscore', 'utilize'
];

// Filler phrases to remove
const FILLER_PHRASES = [
  'in order to', 'due to the fact that', 'at this point in time',
  'in the event that', 'for the purpose of', 'in spite of the fact that',
  'with regard to', 'in light of the fact that'
];

// Chatbot artifacts
const CHATBOT_PHRASES = [
  'i hope this helps', 'great question', 'certainly!', 'of course!',
  'you\'re absolutely right', 'would you like', 'let me know',
  'here is a', 'here are some'
];

/**
 * Calculate burstiness (sentence length variation)
 */
function calculateBurstiness(text) {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const lengths = sentences.map(s => s.trim().split(/\s+/).length);
  
  if (lengths.length < 2) return { burstiness: 0, mean: 0, stdDev: 0 };
  
  const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const variance = lengths.reduce((sum, len) => sum + Math.pow(len - mean, 2), 0) / lengths.length;
  const stdDev = Math.sqrt(variance);
  
  const burstiness = (stdDev - mean) / (stdDev + mean);
  
  return { burstiness, mean, stdDev, sentenceCount: lengths.length };
}

/**
 * Calculate Type-Token Ratio (vocabulary diversity)
 */
function calculateTTR(text) {
  const words = text.toLowerCase()
    .replace(/[^a-z\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 0);
  
  const uniqueWords = new Set(words);
  const ttr = words.length > 0 ? uniqueWords.size / words.length : 0;
  
  return { ttr, totalWords: words.length, uniqueWords: uniqueWords.size };
}

/**
 * Calculate Sentence Length Coefficient of Variation
 */
function calculateCoV(text) {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const lengths = sentences.map(s => s.trim().split(/\s+/).length);
  
  if (lengths.length < 2) return { cov: 0, mean: 0, stdDev: 0 };
  
  const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const variance = lengths.reduce((sum, len) => sum + Math.pow(len - mean, 2), 0) / lengths.length;
  const stdDev = Math.sqrt(variance);
  
  const cov = (stdDev / mean) * 100;
  
  return { cov, mean, stdDev, min: Math.min(...lengths), max: Math.max(...lengths) };
}

/**
 * Detect AI vocabulary (Tier 1 & 2)
 */
function detectAIVocabulary(text) {
  const lowerText = text.toLowerCase();
  
  const tier1Matches = TIER1_WORDS.filter(word => 
    new RegExp(`\\b${word}\\b`, 'i').test(text)
  );
  
  const tier1PhraseMatches = TIER1_PHRASES.filter(phrase =>
    lowerText.includes(phrase)
  );
  
  const tier2Matches = TIER2_WORDS.filter(word =>
    new RegExp(`\\b${word}\\b`, 'i').test(text)
  );
  
  return {
    tier1Words: tier1Matches,
    tier1Phrases: tier1PhraseMatches,
    tier2Words: tier2Matches
  };
}

/**
 * Detect chatbot artifacts
 */
function detectChatbotArtifacts(text) {
  const lowerText = text.toLowerCase();
  return CHATBOT_PHRASES.filter(phrase => lowerText.includes(phrase));
}

/**
 * Detect em dash overuse
 */
function detectEmDashes(text) {
  const matches = text.match(/—/g) || [];
  return matches.length;
}

/**
 * Detect filler phrases
 */
function detectFillerPhrases(text) {
  const lowerText = text.toLowerCase();
  return FILLER_PHRASES.filter(phrase => lowerText.includes(phrase));
}

/**
 * Calculate composite AI score
 */
function calculateAIScore(text) {
  const burstiness = calculateBurstiness(text);
  const ttr = calculateTTR(text);
  const cov = calculateCoV(text);
  const vocab = detectAIVocabulary(text);
  const chatbot = detectChatbotArtifacts(text);
  const emDashes = detectEmDashes(text);
  const filler = detectFillerPhrases(text);
  
  // Score individual components (0-100)
  const bScore = burstiness.burstiness < 0.2 ? 100 : 
                 burstiness.burstiness < 0.4 ? 50 : 0;
  
  const tScore = ttr.ttr < 0.35 ? 100 :
                 ttr.ttr < 0.5 ? 30 :
                 ttr.ttr > 0.7 ? 80 : 0;
  
  const cScore = cov.cov < 30 ? 100 :
                 cov.cov < 50 ? 50 : 0;
  
  const vocabScore = (vocab.tier1Words.length * 20) + 
                     (vocab.tier1Phrases.length * 15) +
                     (vocab.tier2Words.length * 5);
  
  const chatbotScore = chatbot.length * 30;
  const emDashScore = emDashes > 5 ? 50 : emDashes > 2 ? 25 : 0;
  const fillerScore = filler.length * 10;
  
  // Weighted composite
  const composite = Math.min(100, 
    bScore * 0.15 +
    tScore * 0.10 +
    cScore * 0.15 +
    vocabScore * 0.30 +
    chatbotScore * 0.15 +
    emDashScore * 0.05 +
    fillerScore * 0.10
  );
  
  return {
    score: Math.round(composite),
    components: {
      burstiness: { value: burstiness.burstiness.toFixed(2), score: bScore },
      ttr: { value: ttr.ttr.toFixed(2), score: tScore },
      cov: { value: cov.cov.toFixed(1) + '%', score: cScore },
      vocabulary: { tier1: vocab.tier1Words.length, tier2: vocab.tier2Words.length, score: Math.min(100, vocabScore) },
      chatbot: { count: chatbot.length, score: Math.min(100, chatbotScore) },
      emDashes: { count: emDashes, score: emDashScore },
      filler: { count: filler.length, score: Math.min(100, fillerScore) }
    },
    details: {
      burstiness,
      ttr,
      cov,
      vocab,
      chatbot,
      filler
    }
  };
}

/**
 * Generate humanization suggestions
 */
function generateSuggestions(analysis) {
  const suggestions = [];
  
  if (analysis.details.chatbot.length > 0) {
    suggestions.push({
      priority: 'HIGH',
      category: 'Chatbot Artifacts',
      issue: `Found ${analysis.details.chatbot.length} chatbot phrase(s): ${analysis.details.chatbot.join(', ')}`,
      fix: 'Remove these completely. They\'re dead giveaways.'
    });
  }
  
  if (analysis.details.vocab.tier1Words.length > 0) {
    suggestions.push({
      priority: 'HIGH',
      category: 'Tier 1 Vocabulary',
      issue: `Found ${analysis.details.vocab.tier1Words.length} Tier 1 word(s): ${analysis.details.vocab.tier1Words.join(', ')}`,
      fix: 'Replace with simpler alternatives (e.g., "leverage" → "use", "delve" → "explore")'
    });
  }
  
  if (analysis.details.vocab.tier1Phrases.length > 0) {
    suggestions.push({
      priority: 'HIGH',
      category: 'Tier 1 Phrases',
      issue: `Found ${analysis.details.vocab.tier1Phrases.length} Tier 1 phrase(s): ${analysis.details.vocab.tier1Phrases.join(', ')}`,
      fix: 'Rewrite these sections with direct language'
    });
  }
  
  if (analysis.details.filler.length > 0) {
    suggestions.push({
      priority: 'MEDIUM',
      category: 'Filler Phrases',
      issue: `Found ${analysis.details.filler.length} filler phrase(s): ${analysis.details.filler.join(', ')}`,
      fix: 'Simplify (e.g., "in order to" → "to", "due to the fact that" → "because")'
    });
  }
  
  if (analysis.components.cov.score > 50) {
    suggestions.push({
      priority: 'MEDIUM',
      category: 'Sentence Rhythm',
      issue: `Low sentence variation (CoV: ${analysis.components.cov.value})`,
      fix: 'Vary sentence length. Mix short punchy sentences with longer ones.'
    });
  }
  
  if (analysis.components.burstiness.score > 50) {
    suggestions.push({
      priority: 'MEDIUM',
      category: 'Burstiness',
      issue: `Low burstiness (${analysis.components.burstiness.value})`,
      fix: 'Sentences are too uniform. Write more naturally—short, then long, then short.'
    });
  }
  
  if (analysis.details.vocab.tier2Words.length > 5) {
    suggestions.push({
      priority: 'LOW',
      category: 'Tier 2 Vocabulary',
      issue: `Found ${analysis.details.vocab.tier2Words.length} Tier 2 words (suspicious density)`,
      fix: 'Reduce usage. Use simpler alternatives where possible.'
    });
  }
  
  if (analysis.components.emDashes.count > 2) {
    suggestions.push({
      priority: 'LOW',
      category: 'Em Dashes',
      issue: `Found ${analysis.components.emDashes.count} em dashes (—)`,
      fix: 'Replace with commas, periods, or parentheses'
    });
  }
  
  return suggestions;
}

/**
 * Print analysis report
 */
function printReport(analysis) {
  console.log('\n=== AI DETECTION REPORT ===\n');
  console.log(`Overall AI Score: ${analysis.score}/100`);
  
  let likelihood;
  if (analysis.score < 20) likelihood = '✅ Very likely HUMAN';
  else if (analysis.score < 40) likelihood = '🟢 Probably HUMAN';
  else if (analysis.score < 60) likelihood = '🟡 MIXED/Uncertain';
  else if (analysis.score < 80) likelihood = '🟠 Probably AI';
  else likelihood = '🔴 Very likely AI';
  
  console.log(`Likelihood: ${likelihood}\n`);
  
  console.log('--- Statistical Metrics ---');
  console.log(`Burstiness: ${analysis.components.burstiness.value} (${analysis.components.burstiness.score}/100)`);
  console.log(`Type-Token Ratio: ${analysis.components.ttr.value} (${analysis.components.ttr.score}/100)`);
  console.log(`Sentence CoV: ${analysis.components.cov.value} (${analysis.components.cov.score}/100)\n`);
  
  console.log('--- Pattern Detection ---');
  console.log(`Tier 1 Vocabulary: ${analysis.components.vocabulary.tier1} words (${Math.min(100, analysis.components.vocabulary.tier1 * 20)}/100)`);
  console.log(`Tier 2 Vocabulary: ${analysis.components.vocabulary.tier2} words (${Math.min(100, analysis.components.vocabulary.tier2 * 5)}/100)`);
  console.log(`Chatbot Artifacts: ${analysis.components.chatbot.count} (${analysis.components.chatbot.score}/100)`);
  console.log(`Filler Phrases: ${analysis.components.filler.count} (${Math.min(100, analysis.components.filler.score)}/100)`);
  console.log(`Em Dashes: ${analysis.components.emDashes.count} (${analysis.components.emDashes.score}/100)\n`);
}

/**
 * Print suggestions
 */
function printSuggestions(suggestions) {
  console.log('=== HUMANIZATION SUGGESTIONS ===\n');
  
  const high = suggestions.filter(s => s.priority === 'HIGH');
  const medium = suggestions.filter(s => s.priority === 'MEDIUM');
  const low = suggestions.filter(s => s.priority === 'LOW');
  
  if (high.length > 0) {
    console.log('🔴 HIGH PRIORITY:\n');
    high.forEach((s, i) => {
      console.log(`${i + 1}. [${s.category}] ${s.issue}`);
      console.log(`   Fix: ${s.fix}\n`);
    });
  }
  
  if (medium.length > 0) {
    console.log('🟠 MEDIUM PRIORITY:\n');
    medium.forEach((s, i) => {
      console.log(`${i + 1}. [${s.category}] ${s.issue}`);
      console.log(`   Fix: ${s.fix}\n`);
    });
  }
  
  if (low.length > 0) {
    console.log('🟡 LOW PRIORITY:\n');
    low.forEach((s, i) => {
      console.log(`${i + 1}. [${s.category}] ${s.issue}`);
      console.log(`   Fix: ${s.fix}\n`);
    });
  }
  
  if (suggestions.length === 0) {
    console.log('✅ No major issues detected. Text appears human-like.\n');
  }
}

/**
 * Main CLI
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help' || command === '--help' || command === '-h') {
    console.log(`
AI Humanizer CLI

Usage:
  node humanize.js <command> [options]

Commands:
  score <text>           Calculate AI likelihood score (0-100)
  analyze [options]      Full analysis with breakdown
  suggest [options]      Generate humanization suggestions
  help                   Show this help message

Options:
  -f, --file <path>      Read text from file
  --json                 Output as JSON

Examples:
  node humanize.js score "Your text here"
  node humanize.js analyze -f article.txt
  node humanize.js suggest -f draft.md --json
    `);
    return;
  }
  
  let text = '';
  
  // Check for file input
  const fileIndex = args.indexOf('-f') !== -1 ? args.indexOf('-f') : args.indexOf('--file');
  if (fileIndex !== -1 && args[fileIndex + 1]) {
    const filePath = args[fileIndex + 1];
    try {
      text = fs.readFileSync(filePath, 'utf8');
    } catch (err) {
      console.error(`Error reading file: ${err.message}`);
      process.exit(1);
    }
  } else if (args[1]) {
    text = args.slice(1).join(' ');
  } else {
    console.error('Error: No text provided. Use -f <file> or provide text as argument.');
    process.exit(1);
  }
  
  const jsonOutput = args.includes('--json');
  
  if (command === 'score') {
    const analysis = calculateAIScore(text);
    if (jsonOutput) {
      console.log(JSON.stringify({ score: analysis.score }, null, 2));
    } else {
      console.log(`AI Score: ${analysis.score}/100`);
      if (analysis.score < 20) console.log('✅ Very likely HUMAN');
      else if (analysis.score < 40) console.log('🟢 Probably HUMAN');
      else if (analysis.score < 60) console.log('🟡 MIXED/Uncertain');
      else if (analysis.score < 80) console.log('🟠 Probably AI');
      else console.log('🔴 Very likely AI');
    }
  } else if (command === 'analyze') {
    const analysis = calculateAIScore(text);
    if (jsonOutput) {
      console.log(JSON.stringify(analysis, null, 2));
    } else {
      printReport(analysis);
    }
  } else if (command === 'suggest') {
    const analysis = calculateAIScore(text);
    const suggestions = generateSuggestions(analysis);
    if (jsonOutput) {
      console.log(JSON.stringify({ score: analysis.score, suggestions }, null, 2));
    } else {
      printReport(analysis);
      printSuggestions(suggestions);
    }
  } else {
    console.error(`Unknown command: ${command}`);
    console.error('Run "node humanize.js help" for usage information.');
    process.exit(1);
  }
}

main();
