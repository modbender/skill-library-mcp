const fs = require('fs');
const path = require('path');
const { loadWordLevels, getHSKLevelCounts } = require('./mastery.js');

/**
 * Scan memory files for CJK tokens and categorize by HSK level
 */
class VocabTracker {
  constructor() {
    this.wordLevels = loadWordLevels();
    this.levelCounts = getHSKLevelCounts();
  }
  
  extractCJK(text) {
    const re = /[\u4e00-\u9fff]+/g;
    const matches = text.match(re) || [];
    return matches;
  }
  
  categorizeToken(token) {
    // Exact word match
    if (this.wordLevels[token]) {
      return this.wordLevels[token];
    }
    
    // Token not in HSK word list
    // For multi-character tokens, they might be compounds beyond HSK
    return 0;
  }
  
  scanDirectory(dirPath) {
    const files = fs.readdirSync(dirPath)
      .filter(f => f.endsWith('.md'))
      .map(f => path.join(dirPath, f));
    
    const tokenCounts = new Map();
    
    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        const tokens = this.extractCJK(content);
        for (const token of tokens) {
          tokenCounts.set(token, (tokenCounts.get(token) || 0) + 1);
        }
      } catch (err) {
        console.warn(`Could not read ${file}:`, err.message);
      }
    }
    
    return tokenCounts;
  }
  
  generateReport(tokenCounts) {
    const categorized = {
      hsk1: [], hsk2: [], hsk3: [], beyond: [], unknown: []
    };
    
    // Convert Map to array for sorting
    const entries = Array.from(tokenCounts.entries())
      .map(([token, count]) => ({ token, count }))
      .sort((a, b) => b.count - a.count);
    
    // Categorize
    for (const entry of entries) {
      const level = this.categorizeToken(entry.token);
      switch(level) {
        case 1: categorized.hsk1.push(entry); break;
        case 2: categorized.hsk2.push(entry); break;
        case 3: categorized.hsk3.push(entry); break;
        case 0:
          if (entry.token.length > 1) {
            categorized.beyond.push(entry);
          } else {
            categorized.unknown.push(entry);
          }
          break;
      }
    }
    
    // Generate report text
    const report = [];
    report.push('# HSK Vocabulary Tracker (Word-Based)');
    report.push(`Generated: ${new Date().toISOString()}`);
    report.push('');
    
    // Summary
    const totalTokens = entries.length;
    const hsk1Count = categorized.hsk1.length;
    const hsk2Count = categorized.hsk2.length;
    const hsk3Count = categorized.hsk3.length;
    const beyondCount = categorized.beyond.length;
    const unknownCount = categorized.unknown.length;
    
    report.push('## Summary');
    report.push(`- Total distinct CJK tokens: ${totalTokens}`);
    report.push(`- HSK 1 words recognized: ${hsk1Count}/${this.levelCounts.level1} (${Math.round(hsk1Count/this.levelCounts.level1*100)}%)`);
    report.push(`- HSK 2 words recognized: ${hsk2Count}/${this.levelCounts.level2} (${Math.round(hsk2Count/this.levelCounts.level2*100)}%)`);
    report.push(`- HSK 3 words recognized: ${hsk3Count}/${this.levelCounts.level3} (${Math.round(hsk3Count/this.levelCounts.level3*100)}%)`);
    report.push(`- Beyond HSK 3 (multi‑char phrases): ${beyondCount}`);
    report.push(`- Unknown/Non‑HSK (single chars): ${unknownCount}`);
    report.push('');
    
    // Character-level analysis (simplified)
    const uniqueChars = new Set();
    entries.forEach(e => {
      for (const char of e.token) {
        uniqueChars.add(char);
      }
    });
    report.push('## Character-Level Analysis');
    report.push(`- Unique Chinese characters: ${uniqueChars.size}`);
    report.push('');
    
    // Detailed lists
    const formatSection = (title, items, limit = 50) => {
      report.push(`## ${title}`);
      report.push(`Total: ${items.length}`);
      const display = items.slice(0, limit);
      display.forEach(item => {
        report.push(`${item.token} — ${item.count}`);
      });
      if (items.length > limit) {
        report.push(`... and ${items.length - limit} more`);
      }
      report.push('');
    };
    
    if (hsk1Count > 0) formatSection('HSK 1 Words', categorized.hsk1);
    if (hsk2Count > 0) formatSection('HSK 2 Words', categorized.hsk2);
    if (hsk3Count > 0) formatSection('HSK 3 Words', categorized.hsk3);
    if (beyondCount > 0) formatSection('Beyond HSK 3', categorized.beyond, 20);
    if (unknownCount > 0) formatSection('Unknown/Non‑HSK', categorized.unknown, 20);
    
    return {
      reportText: report.join('\n'),
      categorized,
      stats: {
        totalTokens,
        hsk1: hsk1Count,
        hsk2: hsk2Count,
        hsk3: hsk3Count,
        beyond: beyondCount,
        unknown: unknownCount,
        uniqueChars: uniqueChars.size
      }
    };
  }
  
  updateVocabReport(memoryDir = path.join(__dirname, '..', '..', 'memory')) {
    const tokenCounts = this.scanDirectory(memoryDir);
    const result = this.generateReport(tokenCounts);
    
    // Save to memory directory
    const reportPath = path.join(memoryDir, 'hsk-word-report.md');
    fs.writeFileSync(reportPath, result.reportText, 'utf8');
    
    return {
      success: true,
      reportPath,
      stats: result.stats,
      categorized: result.categorized
    };
  }
}

module.exports = VocabTracker;