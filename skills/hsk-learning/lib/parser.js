const fs = require('fs');
const path = require('path');
const { loadWordLevels } = require('./mastery.js');

/**
 * Parse a quiz‑performance.md file and extract vocabulary with correctness.
 * Returns array of {word, level, correct, source}
 */
function parseQuizLog(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  
  const results = [];
  let currentSection = null;
  let currentCorrect = true; // assume correct unless we see ❌
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Detect section headers
    if (line.startsWith('## ')) {
      currentSection = line.substring(3).toLowerCase();
      // Reset correctness assumption for new section
      currentCorrect = true;
    }
    
    // Look for grade indicators
    if (line.includes('Grade:')) {
      if (line.includes('✅') || line.includes('Correct') || line.includes('⚠️ corrected')) {
        currentCorrect = true;
      } else if (line.includes('❌') || line.includes('Incorrect')) {
        currentCorrect = false;
      }
    }
    
    // Look for vocabulary lists
    // Pattern: "- **喝茶** (drink tea) – HSK 2"
    // Pattern: "**喝茶** (drink tea) – HSK 2"
    // Pattern: "New HSK 1 words practiced: 妈妈, 喜欢"
    // Pattern: "Known words reinforced: 我, 在, 家, 她, 看, 书"
    
    // Handle bullet points with bold Chinese
    const bulletMatch = line.match(/^[*-]\s+\*\*([^*]+)\*\*\s*\([^)]+\)\s*–\s*HSK\s*(\d+)/i);
    if (bulletMatch) {
      const word = bulletMatch[1].trim();
      const level = parseInt(bulletMatch[2], 10);
      results.push({ word, level, correct: currentCorrect, source: 'bullet' });
      continue;
    }
    
    // Handle inline bold without bullet
    const inlineMatch = line.match(/\*\*([^*]+)\*\*\s*\([^)]+\)\s*–\s*HSK\s*(\d+)/i);
    if (inlineMatch && !line.startsWith('-') && !line.startsWith('*')) {
      const word = inlineMatch[1].trim();
      const level = parseInt(inlineMatch[2], 10);
      results.push({ word, level, correct: currentCorrect, source: 'inline' });
      continue;
    }
    
    // Handle "New HSK X words practiced:" lines (with optional bullet and bold)
    if (line.includes('New HSK') && line.includes('words practiced')) {
      // Extract level and word list
      const levelMatch = line.match(/New HSK (\d+) words practiced/);
      if (levelMatch) {
        const level = parseInt(levelMatch[1], 10);
        // Get part after colon (or after "practiced:")
        const colonIdx = line.indexOf(':', line.indexOf('practiced'));
        if (colonIdx !== -1) {
          const wordsStr = line.substring(colonIdx + 1).trim();
          // Remove any trailing ** or punctuation
          const cleanStr = wordsStr.replace(/\*\*/g, '').replace(/[.,]$/, '');
          const words = cleanStr.split(/[,\s]+/).filter(w => w.length > 0);
          for (const word of words) {
            results.push({ word, level, correct: currentCorrect, source: 'new' });
          }
        }
      }
      continue;
    }
    
    // Handle "Known words reinforced:" lines
    if (line.includes('Known words reinforced')) {
      const colonIdx = line.indexOf(':');
      if (colonIdx !== -1) {
        const wordsStr = line.substring(colonIdx + 1).trim();
        const cleanStr = wordsStr.replace(/\*\*/g, '').replace(/[.,]$/, '');
        const words = cleanStr.split(/[,\s]+/).filter(w => w.length > 0);
        for (const word of words) {
          results.push({ word, level: 0, correct: currentCorrect, source: 'known' });
        }
      }
      continue;
    }
    
    // Handle "Vocabulary Practiced" section (lines after it)
    if (line.includes('Vocabulary Practiced') || line.includes('Vocabulary practiced')) {
      // Next few lines may contain bullet points
      for (let j = i + 1; j < lines.length && lines[j].trim() !== ''; j++) {
        const vocabLine = lines[j].trim();
        const vocabMatch = vocabLine.match(/^[*-]\s+\*\*([^*]+)\*\*\s*\([^)]+\)\s*–\s*HSK\s*(\d+)/i);
        if (vocabMatch) {
          const word = vocabMatch[1].trim();
          const level = parseInt(vocabMatch[2], 10);
          results.push({ word, level, correct: currentCorrect, source: 'vocab' });
        }
      }
    }
  }
  
  // Deduplicate: keep first occurrence (but combine correctness? if any incorrect, mark incorrect?)
  const seen = new Map();
  for (const item of results) {
    const key = item.word;
    if (seen.has(key)) {
      const existing = seen.get(key);
      // If either is incorrect, mark incorrect
      if (!item.correct) existing.correct = false;
    } else {
      seen.set(key, { ...item });
    }
  }
  
  return Array.from(seen.values());
}

/**
 * Get word level from HSK database (word-to-level mapping)
 */
function getWordLevel(word) {
  const levels = loadWordLevels();
  return levels[word] || 0;
}

/**
 * Process quiz log and update mastery (higher-level function)
 */
function processQuizLog(filePath) {
  const items = parseQuizLog(filePath);
  const enhancedItems = items.map(item => {
    if (item.level === 0) {
      item.level = getWordLevel(item.word);
    }
    return item;
  });
  return enhancedItems;
}

module.exports = {
  parseQuizLog,
  getWordLevel,
  processQuizLog
};