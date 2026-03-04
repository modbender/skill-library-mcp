const path = require('path');
const fs = require('fs');
const { loadMasteryDB, saveMasteryDB, getMasteryStats, getWordsDueForReview, updateMasteryForWord, getHSKLevelCounts } = require('./lib/mastery.js');
const { parseQuizLog, processQuizLog, getWordLevel } = require('./lib/parser.js');
const VocabTracker = require('./lib/vocab-tracker.js');

/**
 * HSK Learning Skill - Main entry point
 */
module.exports = {
  /**
   * Update HSK vocabulary tracker by scanning memory files
   */
  async hsk_update_vocab_tracker({ force = false }) {
    try {
      const tracker = new VocabTracker();
      const memoryDir = path.join(__dirname, '..', '..', 'memory');
      
      // Check if recent scan exists (within 1 day)
      const reportPath = path.join(memoryDir, 'hsk-word-report.md');
      if (!force && fs.existsSync(reportPath)) {
        const stats = fs.statSync(reportPath);
        const ageMs = Date.now() - stats.mtimeMs;
        if (ageMs < 24 * 60 * 60 * 1000) {
          return {
            success: true,
            skipped: true,
            message: 'Recent scan exists (less than 24 hours old). Use force=true to override.',
            reportPath
          };
        }
      }
      
      const result = tracker.updateVocabReport(memoryDir);
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  },
  
  /**
   * Update mastery database from quiz performance logs
   */
  async hsk_update_mastery_from_quiz({ date = 'all' }) {
    try {
      const memoryDir = path.join(__dirname, '..', '..', 'memory');
      const db = loadMasteryDB();
      let updatedCount = 0;
      
      // Find quiz log files
      const files = fs.readdirSync(memoryDir)
        .filter(f => f.includes('quiz-performance') && f.endsWith('.md'))
        .map(f => path.join(memoryDir, f));
      
      // Filter by date if specified
      let filteredFiles = files;
      if (date !== 'all') {
        const targetDate = date.replace(/-/g, '');
        filteredFiles = files.filter(f => f.includes(targetDate));
      }
      
      // Process each file
      for (const file of filteredFiles) {
        const items = processQuizLog(file);
        for (const item of items) {
          if (item.level === 0) continue; // Skip non-HSK words
          updateMasteryForWord(db, item.word, item.correct);
          updatedCount++;
        }
      }
      
      // Save updated DB
      saveMasteryDB(db);
      
      return {
        success: true,
        updated: updatedCount,
        filesProcessed: filteredFiles.length,
        totalFiles: files.length
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  },
  
  /**
   * Get mastery statistics summary
   */
  async hsk_get_mastery_stats({ format = 'text' }) {
    try {
      const db = loadMasteryDB();
      const stats = getMasteryStats(db);
      const levelCounts = getHSKLevelCounts();
      
      if (format === 'json') {
        return { success: true, stats, levelCounts };
      }
      
      // Text format
      let message = `📊 HSK Mastery Statistics\n`;
      message += `Total HSK words: ${stats.total}\n`;
      message += `• Unknown: ${stats.unknown} (${Math.round(stats.unknown/stats.total*100)}%)\n`;
      message += `• Learning: ${stats.learning} (${Math.round(stats.learning/stats.total*100)}%)\n`;
      message += `• Mastered: ${stats.mastered} (${Math.round(stats.mastered/stats.total*100)}%)\n\n`;
      
      // By level
      message += `By HSK level:\n`;
      for (const level of [1, 2, 3, 4, 5, 6]) {
        if (stats.byLevel[level]) {
          const levelStats = stats.byLevel[level];
          const totalForLevel = levelCounts[`level${level}`] || levelStats.total;
          message += `HSK ${level}: ${levelStats.learning} learning, ${levelStats.mastered} mastered / ${totalForLevel} total\n`;
        }
      }
      
      // Markdown format
      if (format === 'markdown') {
        message = `# HSK Mastery Statistics\n\n${message.replace(/\n/g, '\n\n')}`;
      }
      
      return { success: true, message, stats };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  },
  
  /**
   * Get words due for review based on spaced repetition
   */
  async hsk_get_due_words({ limit = 20, level = 0 }) {
    try {
      const db = loadMasteryDB();
      const due = getWordsDueForReview(db);
      
      // Filter by level if specified
      const filtered = level > 0 
        ? due.filter(item => item.level === level)
        : due;
      
      // Apply limit
      const result = filtered.slice(0, limit);
      
      // Format response
      const byLevel = {};
      result.forEach(item => {
        if (!byLevel[item.level]) byLevel[item.level] = [];
        byLevel[item.level].push(item);
      });
      
      let message = `📝 Words Due for Review: ${result.length} total\n`;
      for (const [lvl, items] of Object.entries(byLevel).sort()) {
        message += `\nHSK ${lvl} (${items.length}):\n`;
        items.forEach((item, i) => {
          const status = item.mastery === 'mastered' ? '★' : item.mastery === 'learning' ? '↻' : '?';
          const days = item.interval ? `(every ${item.interval}d)` : '';
          message += `  ${i + 1}. ${item.word} ${status} ${days}\n`;
        });
      }
      
      return {
        success: true,
        count: result.length,
        words: result,
        byLevel,
        message
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  },
  
  /**
   * Generate adaptive HSK quiz based on mastery level
   * Note: This is a simplified version; full implementation would use GPT
   */
  async hsk_generate_quiz({ difficulty = 'mixed', format = 'simple' }) {
    try {
      // For now, return a template quiz
      // In the future, this would:
      // 1. Get due words from mastery system
      // 2. Select appropriate words based on difficulty
      // 3. Generate passage and questions using GPT
      // 4. Format according to requested format
      
      const db = loadMasteryDB();
      const due = getWordsDueForReview(db);
      
      // Select words based on difficulty
      let selectedWords = [];
      if (difficulty === 'review') {
        // Words due for review
        selectedWords = due.slice(0, 5).map(w => w.word);
      } else if (difficulty === 'learning') {
        // Words in learning state
        const learning = due.filter(w => w.mastery === 'learning');
        selectedWords = learning.slice(0, 5).map(w => w.word);
      } else if (difficulty === 'new') {
        // Unknown words (not encountered)
        const allWords = Object.entries(db.words);
        const unknown = allWords.filter(([word, data]) => data.mastery === 'unknown');
        selectedWords = unknown.slice(0, 5).map(([word]) => word);
      } else { // mixed
        const mixed = due.slice(0, 3).map(w => w.word);
        const allWords = Object.entries(db.words);
        const unknown = allWords.filter(([word, data]) => data.mastery === 'unknown');
        if (unknown.length > 0) {
          mixed.push(unknown[0][0]); // Add one new word
        }
        selectedWords = mixed;
      }
      
      // Generate simple quiz template
      const quiz = {
        difficulty,
        format,
        selectedWords,
        passage: `请使用这些词写一个段落: ${selectedWords.join('、')}`,
        question: "这个段落是什么意思？",
        instructions: "请用中文回答。"
      };
      
      return {
        success: true,
        quiz,
        message: `📝 HSK Quiz (${difficulty}, ${format})\n\nPassage: ${quiz.passage}\n\nQuestion: ${quiz.question}\n\nInstructions: ${quiz.instructions}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  },
  
  /**
   * Parse a quiz performance log file and extract vocabulary
   */
  async hsk_parse_quiz_log({ filePath }) {
    try {
      const absolutePath = path.isAbsolute(filePath) 
        ? filePath 
        : path.join(__dirname, '..', '..', filePath);
      
      if (!fs.existsSync(absolutePath)) {
        return {
          success: false,
          error: `File not found: ${absolutePath}`
        };
      }
      
      const items = parseQuizLog(absolutePath);
      const enhancedItems = items.map(item => ({
        ...item,
        level: item.level === 0 ? getWordLevel(item.word) : item.level
      }));
      
      return {
        success: true,
        filePath: absolutePath,
        items: enhancedItems,
        count: enhancedItems.length,
        summary: `Parsed ${enhancedItems.length} vocabulary items from ${path.basename(absolutePath)}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack
      };
    }
  }
};