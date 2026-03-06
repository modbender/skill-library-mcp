const path = require('path');
const fs = require('fs');
const { loadMasteryDB, saveMasteryDB, getMasteryStats, getWordsDueForReview, updateMasteryForWord, getHSKLevelCounts } = require('./lib/mastery.js');
const { parseQuizLog, processQuizLog, getWordLevel } = require('./lib/parser.js');
const VocabTracker = require('./lib/vocab-tracker.js');

// Helper functions for quiz generation
function generateSimpleQuiz(words, difficulty) {
  // Basic vocabulary knowledge for common HSK words
  const wordMeanings = {
    '我': 'I/me', '你': 'you', '他': 'he/him', '她': 'she/her', '是': 'is/am/are',
    '不': 'not', '在': 'at/in', '有': 'have', '人': 'person', '这': 'this',
    '那': 'that', '个': 'measure word', '了': 'completed action', '的': 'possessive',
    '一': 'one', '二': 'two', '三': 'three', '四': 'four', '五': 'five',
    '六': 'six', '七': 'seven', '八': 'eight', '九': 'nine', '十': 'ten',
    '吃': 'eat', '喝': 'drink', '水': 'water', '饭': 'rice/meal', '茶': 'tea',
    '书': 'book', '学习': 'study', '学校': 'school', '老师': 'teacher', '学生': 'student',
    '家': 'home/family', '朋友': 'friend', '喜欢': 'like', '看': 'look/watch', '听': 'listen',
    '说': 'speak', '读': 'read', '写': 'write', '大': 'big', '小': 'small',
    '好': 'good', '坏': 'bad', '多': 'many', '少': 'few', '上': 'up/on',
    '下': 'down/under', '中': 'middle', '国': 'country', '中国': 'China', '美国': 'America',
    '今天': 'today', '明天': 'tomorrow', '昨天': 'yesterday', '年': 'year', '月': 'month',
    '日': 'day', '时间': 'time', '现在': 'now', '以后': 'later', '以前': 'before'
  };
  
  let quiz = `📚 Vocabulary: ${words.join(', ')}\n`;
  quiz += '='.repeat(40) + '\n\n';
  
  // Section 1: Multiple Choice (English to Chinese)
  quiz += '1. Multiple Choice (Choose the correct Chinese word):\n';
  words.slice(0, Math.min(3, words.length)).forEach((word, i) => {
    const meaning = wordMeanings[word] || 'unknown';
    const options = getDistractors(word, Object.keys(wordMeanings));
    quiz += `   ${i + 1}. "${meaning}" = ?\n`;
    quiz += `      A) ${options[0]}  B) ${options[1]}  C) ${options[2]}  D) ${word}\n`;
  });
  
  // Section 2: Fill in the blank
  quiz += '\n2. Fill in the blank (Complete the sentences):\n';
  const sentences = [
    { template: '我___中国。', word: words[0] || '喜欢' },
    { template: '这是___书。', word: words[1] || '我的' },
    { template: '他___学校学习。', word: words[2] || '在' }
  ];
  sentences.forEach((item, i) => {
    const blanked = item.template.replace('___', '_____');
    quiz += `   ${i + 1}. ${blanked} (Use: ${item.word})\n`;
  });
  
  // Section 3: True/False
  quiz += '\n3. True or False (Mark ✅ or ❌):\n';
  const tfStatements = [
    `"${words[0] || '我'}" means "I/me".`,
    `"${words[1] || '书'}" is a type of food.`,
    `"${words[2] || '学习'}" means "to study".`
  ];
  tfStatements.forEach((stmt, i) => {
    quiz += `   ${i + 1}. ${stmt}\n`;
  });
  
  // Section 4: Sentence translation
  quiz += '\n4. Translate to Chinese:\n';
  const translations = [];
  
  if (words[0] && words[1]) {
    translations.push({ 
      english: `I ${wordMeanings[words[0]] || 'like'} ${words[1] || 'books'}.`, 
      hint: `Use: ${words[0]}, ${words[1]}` 
    });
  }
  if (words[2] && words[3]) {
    translations.push({ 
      english: `This is ${wordMeanings[words[2]] || 'my'} ${words[3] || 'friend'}.`, 
      hint: `Use: ${words[2]}, ${words[3]}` 
    });
  }
  if (words[4] && words[5]) {
    translations.push({ 
      english: `We ${wordMeanings[words[4]] || 'study'} at ${words[5] || 'school'}.`, 
      hint: `Use: ${words[4]}, ${words[5]}` 
    });
  }
  
  if (translations.length === 0) {
    // Fallback translations
    translations.push({ english: 'I am a student.', hint: 'Use: 我, 是, 学生' });
    translations.push({ english: 'This is a book.', hint: 'Use: 这, 是, 书' });
  }
  
  translations.forEach((item, i) => {
    quiz += `   ${i + 1}. "${item.english}" (${item.hint})\n`;
  });
  
  return quiz;
}

function generateListeningQuiz(words) {
  let quiz = `🎧 Listening Practice (Imagine the audio):\n`;
  quiz += '='.repeat(40) + '\n\n';
  
  quiz += 'Listen to each sentence and choose the correct picture:\n\n';
  
  const listeningItems = [
    { sentence: `我${words[0] || '喝'}水。`, options: ['🍎', '💧', '📚', '🏠'], correct: 1 },
    { sentence: `我去${words[1] || '学校'}。`, options: ['🏠', '🏫', '🛒', '🏥'], correct: 1 },
    { sentence: `我喜欢${words[2] || '看'}书。`, options: ['📖', '🎵', '🏃', '🍽️'], correct: 0 },
    { sentence: `这是${words[3] || '我的'}${words[4] || '朋友'}。`, options: ['👤', '👥', '🤝', '💬'], correct: 1 }
  ];
  
  listeningItems.forEach((item, i) => {
    quiz += `${i + 1}. Audio: "${item.sentence}"\n`;
    quiz += `   A) ${item.options[0]}  B) ${item.options[1]}  C) ${item.options[2]}  D) ${item.options[3]}\n`;
  });
  
  quiz += '\nFor actual audio, use TTS with these sentences.';
  return quiz;
}

function generateReadingQuiz(words) {
  let quiz = `📖 Reading Comprehension:\n`;
  quiz += '='.repeat(40) + '\n\n';
  
  // Create a simple passage using the words
  const passage = `我是${words[0] || '学生'}。我${words[1] || '在'}${words[2] || '学校'}${words[3] || '学习'}中文。我${words[4] || '喜欢'}${words[5] || '中国'}文化。我的${words[6] || '老师'}很好。`;
  
  quiz += `Passage:\n"${passage}"\n\n`;
  
  quiz += 'Questions:\n';
  quiz += '1. What is the person?\n';
  quiz += '   A) Teacher  B) Student  C) Doctor  D) Engineer\n\n';
  
  quiz += '2. Where does the person study?\n';
  quiz += '   A) At home  B) At school  C) At work  D) In a park\n\n';
  
  quiz += '3. What does the person like?\n';
  quiz += '   A) Japanese culture  B) Chinese culture  C) American culture  D) French culture\n\n';
  
  quiz += '4. How is the teacher?\n';
  quiz += '   A) Bad  B) Good  C) Strict  D) Funny\n';
  
  return quiz;
}

function generateWritingQuiz(words) {
  let quiz = `✍️ Writing Practice:\n`;
  quiz += '='.repeat(40) + '\n\n';
  
  quiz += `Use these words in sentences: ${words.slice(0, 5).join(', ')}\n\n`;
  
  quiz += '1. Write a sentence using 2 of the words:\n';
  quiz += '   ________________________________________\n\n';
  
  quiz += '2. Write a question using 2 different words:\n';
  quiz += '   ________________________________________\n\n';
  
  quiz += '3. Write a short paragraph (3-4 sentences) using at least 3 words:\n';
  quiz += '   ________________________________________\n';
  quiz += '   ________________________________________\n';
  quiz += '   ________________________________________\n';
  
  return quiz;
}

function getDistractors(targetWord, allWords) {
  // Get 3 random words that are not the target word
  const filtered = allWords.filter(w => w !== targetWord);
  const shuffled = filtered.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 3);
}

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
   * Now with actual question generation instead of templates
   */
  async hsk_generate_quiz({ difficulty = 'mixed', format = 'simple' }) {
    try {
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
      
      // If no words selected, use some common HSK 1 words as fallback
      if (selectedWords.length === 0) {
        selectedWords = ['我', '你', '他', '是', '不'];
      }
      
      // Generate actual quiz based on format
      let quizContent = '';
      let quizTitle = `📝 HSK Quiz (${difficulty}, ${format})`;
      
      if (format === 'simple' || format === 'full') {
        quizContent = generateSimpleQuiz(selectedWords, difficulty);
      } else if (format === 'listening') {
        quizContent = generateListeningQuiz(selectedWords);
      } else if (format === 'reading') {
        quizContent = generateReadingQuiz(selectedWords);
      } else if (format === 'writing') {
        quizContent = generateWritingQuiz(selectedWords);
      }
      
      const quiz = {
        difficulty,
        format,
        selectedWords,
        content: quizContent,
        instructions: "请完成所有题目，完成后发送'答案'查看正确答案。"
      };
      
      return {
        success: true,
        quiz,
        message: `${quizTitle}\n\n${quizContent}\n\n${quiz.instructions}`
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