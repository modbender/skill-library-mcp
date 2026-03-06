const fs = require('fs');
const path = require('path');

// Paths relative to skill directory
const DATA_DIR = path.join(__dirname, '..', 'data');
const MASTERY_DB_PATH = path.join(DATA_DIR, 'hsk-mastery-db.json');
const HSK_WORD_TO_LEVEL_PATH = path.join(DATA_DIR, 'hsk-word-to-level.json');
const HSK_DATABASE_PATH = path.join(DATA_DIR, 'hsk-database.json');

const DEFAULT_PARAMS = {
  initialEase: 2.5,
  initialInterval: 1, // days
  masteryThreshold: 3,
  easeIncrement: 0.1,
  easeDecrement: 0.2,
  minEase: 1.3,
  maxInterval: 365 // days
};

let WORD_LEVEL_CACHE = null;
let HSK_DB_CACHE = null;

function loadWordLevels() {
  if (!WORD_LEVEL_CACHE) {
    const data = fs.readFileSync(HSK_WORD_TO_LEVEL_PATH, 'utf8');
    WORD_LEVEL_CACHE = JSON.parse(data);
  }
  return WORD_LEVEL_CACHE;
}

function loadHSKDatabase() {
  if (!HSK_DB_CACHE) {
    const data = fs.readFileSync(HSK_DATABASE_PATH, 'utf8');
    HSK_DB_CACHE = JSON.parse(data);
  }
  return HSK_DB_CACHE;
}

function loadMasteryDB() {
  const data = fs.readFileSync(MASTERY_DB_PATH, 'utf8');
  return JSON.parse(data);
}

function saveMasteryDB(db) {
  db.updatedAt = new Date().toISOString();
  fs.writeFileSync(MASTERY_DB_PATH, JSON.stringify(db, null, 2), 'utf8');
}

function getWordEntry(db, word) {
  if (!db.words[word]) {
    // Initialize new word entry (should not happen for HSK words)
    const levels = loadWordLevels();
    const level = levels[word] || 0;
    db.words[word] = {
      level,
      mastery: 'unknown',
      encountered: false,
      frequency: 0,
      repetition: 0,
      interval: 0,
      ease: DEFAULT_PARAMS.initialEase,
      nextReview: null,
      lastReviewed: null,
      correctStreak: 0,
      totalCorrect: 0,
      totalAttempts: 0,
      lastUpdated: new Date().toISOString()
    };
  }
  return db.words[word];
}

function updateMasteryForWord(db, word, correct, date = new Date()) {
  const entry = getWordEntry(db, word);
  const params = db.parameters || DEFAULT_PARAMS;
  
  // Ensure date is a valid Date object
  const reviewDate = date instanceof Date ? date : new Date(date);
  if (isNaN(reviewDate.getTime())) {
    // If date is invalid, use current date
    reviewDate = new Date();
  }
  
  entry.totalAttempts++;
  if (correct) entry.totalCorrect++;
  
  // Mark as encountered if not already
  if (!entry.encountered) {
    entry.encountered = true;
    entry.mastery = 'learning';
  }
  
  // Update repetition count
  entry.repetition++;
  
  // Update ease factor and interval based on correctness
  if (correct) {
    entry.correctStreak++;
    // Increase ease slightly
    entry.ease = Math.max(params.minEase, entry.ease + params.easeIncrement);
    
    // Calculate new interval
    if (entry.repetition === 1) {
      entry.interval = params.initialInterval;
    } else if (entry.repetition === 2) {
      entry.interval = 6; // 6 days after second correct
    } else {
      entry.interval = Math.min(params.maxInterval, Math.round(entry.interval * entry.ease));
    }
    
    // Check if mastered
    if (entry.correctStreak >= params.masteryThreshold && entry.interval >= 30) {
      entry.mastery = 'mastered';
    }
  } else {
    // Incorrect answer
    entry.correctStreak = 0;
    entry.ease = Math.max(params.minEase, entry.ease - params.easeDecrement);
    entry.interval = params.initialInterval;
    entry.mastery = 'learning'; // demote if was mastered
  }
  
  // Update next review date
  const nextReviewMs = reviewDate.getTime() + entry.interval * 24 * 60 * 60 * 1000;
  entry.nextReview = new Date(nextReviewMs).toISOString();
  entry.lastReviewed = reviewDate.toISOString();
  entry.lastUpdated = reviewDate.toISOString();
  
  return entry;
}

function getWordsDueForReview(db, date = new Date()) {
  // Ensure date is a valid Date object
  const checkDate = date instanceof Date ? date : new Date(date);
  if (isNaN(checkDate.getTime())) {
    checkDate = new Date();
  }
  
  const due = [];
  for (const [word, entry] of Object.entries(db.words)) {
    if (entry.nextReview && new Date(entry.nextReview) <= checkDate) {
      due.push({ word, ...entry });
    }
  }
  // Sort by priority: unknown > learning > mastered, then by nextReview
  due.sort((a, b) => {
    const priority = { unknown: 0, learning: 1, mastered: 2 };
    if (priority[a.mastery] !== priority[b.mastery]) {
      return priority[a.mastery] - priority[b.mastery];
    }
    return new Date(a.nextReview) - new Date(b.nextReview);
  });
  return due;
}

function getMasteryStats(db) {
  const stats = {
    total: Object.keys(db.words).length,
    unknown: 0,
    learning: 0,
    mastered: 0,
    byLevel: {}
  };
  
  for (const entry of Object.values(db.words)) {
    stats[entry.mastery]++;
    const level = entry.level;
    if (!stats.byLevel[level]) {
      stats.byLevel[level] = { total: 0, unknown: 0, learning: 0, mastered: 0 };
    }
    stats.byLevel[level].total++;
    stats.byLevel[level][entry.mastery]++;
  }
  
  return stats;
}

function getHSKLevelCounts() {
  const db = loadHSKDatabase();
  return db.counts || { level1: 497, level2: 761, level3: 953, total: 2211 };
}

module.exports = {
  loadMasteryDB,
  saveMasteryDB,
  updateMasteryForWord,
  getWordsDueForReview,
  getMasteryStats,
  getHSKLevelCounts,
  loadWordLevels,
  DEFAULT_PARAMS,
  DATA_DIR,
  MASTERY_DB_PATH
};