#!/usr/bin/env node
/**
 * Initialize HSK Mastery Database
 * 
 * This script creates a fresh mastery database for a new user.
 * Run this after installing the skill to set up personal tracking.
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const HSK_WORD_TO_LEVEL_PATH = path.join(DATA_DIR, 'hsk-word-to-level.json');
const MASTERY_DB_PATH = path.join(DATA_DIR, 'hsk-mastery-db.json');

// Default parameters for spaced repetition
const DEFAULT_PARAMS = {
  initialEase: 2.5,
  initialInterval: 1, // days
  masteryThreshold: 3,
  easeIncrement: 0.1,
  easeDecrement: 0.2,
  minEase: 1.3,
  maxInterval: 365 // days
};

function initializeMasteryDB() {
  console.log('📚 Initializing HSK Mastery Database...');
  
  // Check if mastery DB already exists
  if (fs.existsSync(MASTERY_DB_PATH)) {
    console.log('⚠️  Mastery database already exists at:', MASTERY_DB_PATH);
    const backupPath = MASTERY_DB_PATH + '.backup-' + Date.now();
    fs.copyFileSync(MASTERY_DB_PATH, backupPath);
    console.log('📋 Created backup at:', backupPath);
  }
  
  // Load HSK word list
  if (!fs.existsSync(HSK_WORD_TO_LEVEL_PATH)) {
    console.error('❌ HSK word-to-level mapping not found at:', HSK_WORD_TO_LEVEL_PATH);
    console.error('Please ensure the skill data files are properly installed.');
    process.exit(1);
  }
  
  const wordLevels = JSON.parse(fs.readFileSync(HSK_WORD_TO_LEVEL_PATH, 'utf8'));
  const words = Object.keys(wordLevels);
  
  console.log(`📖 Found ${words.length} HSK words to initialize`);
  
  // Create mastery database structure
  const masteryDB = {
    version: '1.0',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    parameters: DEFAULT_PARAMS,
    words: {}
  };
  
  // Initialize each word
  for (const word of words) {
    const level = wordLevels[word];
    masteryDB.words[word] = {
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
  
  // Write to file
  fs.writeFileSync(
    MASTERY_DB_PATH,
    JSON.stringify(masteryDB, null, 2),
    'utf8'
  );
  
  console.log('✅ Mastery database initialized successfully!');
  console.log(`📊 Total words: ${words.length}`);
  console.log(`📁 Location: ${MASTERY_DB_PATH}`);
  console.log('\n🎯 Next steps:');
  console.log('1. Run your first HSK quiz');
  console.log('2. Use hsk_update_mastery_from_quiz to process quiz logs');
  console.log('3. Check mastery stats with hsk_get_mastery_stats');
}

// Run initialization
initializeMasteryDB();