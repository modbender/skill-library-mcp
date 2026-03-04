#!/usr/bin/env node

/**
 * AI Customer Service Knowledge Base Builder
 * Extracts FAQ from documents/websites and builds searchable knowledge base
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Default configuration
const DEFAULT_CONFIG = {
  language: 'zh-CN',
  minConfidence: 0.7,
  maxResults: 3,
  fallbackMessage: '抱歉，我没有找到相关答案。请联系人工客服。'
};

// Load configuration
function loadConfig(configPath = './config.json') {
  try {
    if (fs.existsSync(configPath)) {
      return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(configPath, 'utf8')) };
    }
  } catch (err) {
    console.warn(`Warning: Could not load config from ${configPath}, using defaults`);
  }
  return DEFAULT_CONFIG;
}

// Extract text from file
function extractFromFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Simple text extraction (for .txt, .md files)
  if (['.txt', '.md'].includes(ext)) {
    return content;
  }
  
  // For other formats, return raw content with warning
  console.warn(`Warning: ${ext} files may need preprocessing. Treating as plain text.`);
  return content;
}

// Parse FAQ from text
function parseFAQ(text) {
  const entries = [];
  let idCounter = 1;
  
  // Pattern 1: Q: ... A: ...
  const qaPattern = /Q[：:]\s*(.+?)\s*A[：:]\s*(.+?)(?=Q[：:]|$)/gs;
  let match;
  
  while ((match = qaPattern.exec(text)) !== null) {
    entries.push({
      id: `q${String(idCounter++).padStart(3, '0')}`,
      question: match[1].trim(),
      answer: match[2].trim(),
      keywords: extractKeywords(match[1]),
      category: 'general'
    });
  }
  
  // Pattern 2: Numbered questions (1. ... 答: ...)
  if (entries.length === 0) {
    const numberedPattern = /\d+[\.、]\s*(.+?)\s*[答回][：:]\s*(.+?)(?=\d+[\.、]|$)/gs;
    while ((match = numberedPattern.exec(text)) !== null) {
      entries.push({
        id: `q${String(idCounter++).padStart(3, '0')}`,
        question: match[1].trim(),
        answer: match[2].trim(),
        keywords: extractKeywords(match[1]),
        category: 'general'
      });
    }
  }
  
  return entries;
}

// Extract keywords from question
function extractKeywords(question) {
  // Remove common words and extract meaningful terms
  const stopWords = ['如何', '怎么', '什么', '哪里', '为什么', '是否', '可以', '能否', '的', '了', '吗', '呢', '有', '是'];
  // Split by character for Chinese, keep meaningful 2+ char words
  const chars = question.split('');
  const words = [];
  
  // Extract 2-char and 3-char combinations
  for (let i = 0; i < chars.length - 1; i++) {
    const word2 = chars[i] + chars[i + 1];
    if (word2.length === 2 && !stopWords.includes(word2)) {
      words.push(word2);
    }
    if (i < chars.length - 2) {
      const word3 = chars[i] + chars[i + 1] + chars[i + 2];
      if (word3.length === 3 && !stopWords.includes(word3)) {
        words.push(word3);
      }
    }
  }
  
  return [...new Set(words)].slice(0, 8);
}

// Scrape FAQ from URL
async function scrapeFromURL(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    
    client.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        // Simple HTML text extraction
        const text = data
          .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
          .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
          .replace(/<[^>]+>/g, ' ')
          .replace(/&nbsp;/g, ' ')
          .replace(/\s+/g, ' ')
          .trim();
        resolve(text);
      });
    }).on('error', reject);
  });
}

// Search knowledge base
function searchKB(kb, query, config) {
  const queryLower = query.toLowerCase();
  const queryKeywords = extractKeywords(query);
  
  const results = kb.entries.map(entry => {
    let score = 0;
    
    // Exact match in question
    if (entry.question.toLowerCase().includes(queryLower)) {
      score += 1.0;
    }
    
    // Keyword matching
    const matchedKeywords = entry.keywords.filter(k => 
      queryKeywords.some(qk => k.includes(qk) || qk.includes(k))
    );
    score += matchedKeywords.length * 0.3;
    
    // Partial match in answer
    if (entry.answer.toLowerCase().includes(queryLower)) {
      score += 0.2;
    }
    
    return { ...entry, score };
  })
  .filter(r => r.score >= config.minConfidence)
  .sort((a, b) => b.score - a.score)
  .slice(0, config.maxResults);
  
  return results;
}

// Export to different formats
function exportKB(kb, format, outputPath) {
  switch (format.toLowerCase()) {
    case 'csv':
      const csv = ['ID,Question,Answer,Keywords,Category']
        .concat(kb.entries.map(e => 
          `"${e.id}","${e.question}","${e.answer}","${e.keywords.join(';')}","${e.category}"`
        ))
        .join('\n');
      fs.writeFileSync(outputPath, csv, 'utf8');
      break;
      
    case 'markdown':
    case 'md':
      const md = ['# FAQ Knowledge Base', '']
        .concat(kb.entries.map(e => 
          `## ${e.question}\n\n${e.answer}\n\n**Keywords:** ${e.keywords.join(', ')}\n`
        ))
        .join('\n');
      fs.writeFileSync(outputPath, md, 'utf8');
      break;
      
    case 'json':
    default:
      fs.writeFileSync(outputPath, JSON.stringify(kb, null, 2), 'utf8');
  }
  
  console.log(`✓ Exported to ${outputPath}`);
}

// Main CLI
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help') {
    console.log(`
AI Customer Service Knowledge Base Builder

Usage:
  node kb-builder.js extract --file <path> --output <path>
  node kb-builder.js scrape --url <url> --output <path>
  node kb-builder.js test --kb <path> --query <question>
  node kb-builder.js export --kb <path> --format <csv|md|json> --output <path>
  node kb-builder.js interactive --kb <path>

Examples:
  node kb-builder.js extract --file ./faq.txt --output ./kb.json
  node kb-builder.js test --kb ./kb.json --query "如何退货？"
    `);
    return;
  }
  
  const getArg = (flag) => {
    const idx = args.indexOf(flag);
    return idx !== -1 ? args[idx + 1] : null;
  };
  
  const config = loadConfig();
  
  try {
    switch (command) {
      case 'extract': {
        const filePath = getArg('--file');
        const outputPath = getArg('--output') || './kb.json';
        
        if (!filePath) {
          console.error('Error: --file is required');
          process.exit(1);
        }
        
        console.log(`Extracting FAQ from ${filePath}...`);
        const text = extractFromFile(filePath);
        const entries = parseFAQ(text);
        
        const kb = {
          version: '1.0',
          language: config.language,
          createdAt: new Date().toISOString(),
          entries
        };
        
        fs.writeFileSync(outputPath, JSON.stringify(kb, null, 2), 'utf8');
        console.log(`✓ Extracted ${entries.length} Q&A pairs to ${outputPath}`);
        break;
      }
      
      case 'scrape': {
        const url = getArg('--url');
        const outputPath = getArg('--output') || './kb.json';
        
        if (!url) {
          console.error('Error: --url is required');
          process.exit(1);
        }
        
        console.log(`Scraping FAQ from ${url}...`);
        const text = await scrapeFromURL(url);
        const entries = parseFAQ(text);
        
        const kb = {
          version: '1.0',
          language: config.language,
          source: url,
          createdAt: new Date().toISOString(),
          entries
        };
        
        fs.writeFileSync(outputPath, JSON.stringify(kb, null, 2), 'utf8');
        console.log(`✓ Scraped ${entries.length} Q&A pairs to ${outputPath}`);
        break;
      }
      
      case 'test': {
        const kbPath = getArg('--kb');
        const query = getArg('--query');
        
        if (!kbPath || !query) {
          console.error('Error: --kb and --query are required');
          process.exit(1);
        }
        
        const kb = JSON.parse(fs.readFileSync(kbPath, 'utf8'));
        const results = searchKB(kb, query, config);
        
        console.log(`\nQuery: ${query}\n`);
        if (results.length === 0) {
          console.log(config.fallbackMessage);
        } else {
          results.forEach((r, i) => {
            console.log(`[${i + 1}] (confidence: ${r.score.toFixed(2)})`);
            console.log(`Q: ${r.question}`);
            console.log(`A: ${r.answer}\n`);
          });
        }
        break;
      }
      
      case 'export': {
        const kbPath = getArg('--kb');
        const format = getArg('--format') || 'json';
        const outputPath = getArg('--output') || `./kb.${format}`;
        
        if (!kbPath) {
          console.error('Error: --kb is required');
          process.exit(1);
        }
        
        const kb = JSON.parse(fs.readFileSync(kbPath, 'utf8'));
        exportKB(kb, format, outputPath);
        break;
      }
      
      case 'interactive': {
        const kbPath = getArg('--kb');
        if (!kbPath) {
          console.error('Error: --kb is required');
          process.exit(1);
        }
        
        const kb = JSON.parse(fs.readFileSync(kbPath, 'utf8'));
        const readline = require('readline');
        const rl = readline.createInterface({
          input: process.stdin,
          output: process.stdout
        });
        
        console.log('Interactive mode. Type your questions (or "exit" to quit):\n');
        
        rl.on('line', (query) => {
          if (query.toLowerCase() === 'exit') {
            rl.close();
            return;
          }
          
          const results = searchKB(kb, query, config);
          if (results.length === 0) {
            console.log(config.fallbackMessage + '\n');
          } else {
            console.log(`\nTop answer (confidence: ${results[0].score.toFixed(2)}):`);
            console.log(results[0].answer + '\n');
          }
        });
        
        break;
      }
      
      default:
        console.error(`Unknown command: ${command}`);
        console.error('Run "node kb-builder.js help" for usage');
        process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { parseFAQ, searchKB, extractKeywords };
