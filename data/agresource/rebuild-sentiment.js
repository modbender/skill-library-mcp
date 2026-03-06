#!/usr/bin/env node
/**
 * Rebuild sentiment analysis from existing newsletter files
 * Useful for:
 * 1. Testing improved sentiment logic on historical data
 * 2. Backfilling sentiment when logic changes
 * 3. Re-analyzing after keyword/bias updates
 */

const fs = require('fs').promises;
const path = require('path');
const { chromium } = require('playwright');

const MEMORY_DIR = path.join(require('os').homedir(), 'clawd', 'memory', 'agresource');
const SENTIMENT_HISTORY_FILE = path.join(MEMORY_DIR, 'sentiment_history.json');

// Copy sentiment analysis logic from scraper.js
function analyzeSentiment(text) {
  const textLower = text.toLowerCase();

  // Bullish keywords (prices going UP)
  const bullishKeywords = [
    // Price gains
    'rally', 'rallies', 'gained', 'higher', 'surged', 'jumped', 'soared',
    'uptick', 'recovery', 'bounced', 'strength', 'firming', 'support',

    // Demand strength
    'china buying', 'export sales', 'strong demand', 'demand good',
    'flash sales', 'export activity', 'new demand', 'buyer interest',

    // Supply concerns (BULLISH for prices)
    'crop stress', 'weather concerns', 'drought', 'dry weather',
    'excessive heat', 'freeze', 'frost damage', 'crop reduced',
    'production concerns', 'yield loss', 'harvest delays',

    // General bullish
    'bullish', 'upside', 'positive', 'optimistic', 'favorable',
  ];

  // Bearish keywords (prices going DOWN)
  const bearishKeywords = [
    // Price losses
    'declined', 'dropped', 'fell', 'weak', 'lower', 'pressure',
    'selling', 'decline', 'losses', 'bearish', 'resistance',

    // Demand weakness
    'export concerns', 'export weakness', 'china auctioning', 'china selling',
    'demand concerns', 'lack of demand', 'demand slow',

    // Supply glut (more supply = lower prices)
    'record crop', 'record production', 'large crop', 'bumper crop',
    'production increasing', 'supply ample', 'supplies adequate',

    // Favorable weather (more yield = lower prices)
    'favorable weather', 'ideal conditions', 'timely rains',
    'adequate moisture', 'beneficial rainfall', 'normal weather',

    // Trade/tariff issues
    'tariff concerns', 'trade uncertainty', 'trade barriers',
    'south america', 'brazil', 'argentina production',

    // Index fund activity
    'index fund selling', 'fund selling', 'speculative selling',
    'fund rebalance', 'index fund rebalance',
  ];

  // Weather impact detection
  const weatherPositiveForCrops = [
    'favorable', 'beneficial', 'improving', 'adequate moisture',
    'timely rains', 'ideal conditions', 'normal', 'good weather'
  ];

  const weatherNegativeForCrops = [
    'drought', 'excessive', 'flooding', 'heat stress',
    'dry conditions', 'moisture stress', 'weather concerns',
    'hot and dry', 'below normal moisture', 'stress'
  ];

  // Explicit bias statements (AUTHORITATIVE)
  const explicitBiasKeywords = {
    bullish: [
      'bullish bias', 'bullish bias maintained', 'bullish outlook',
      'favorable bias', 'positive bias',
      'no sales recommended', 'not advised', 'hold grain', 'hold old crop',
      'wait to sell', 'wait for higher prices', 'hold for better prices',
      'buyers should be aggressive', 'recommended to buy', 'advise buying',
      'increase sales', 'aggressive selling', 'make sales', 'new crop sales',
      'forward contracting', 'pricing opportunities'
    ],
    bearish: [
      'bearish bias', 'bearish bias maintained', 'bearish outlook',
      'negative bias', 'unfavorable bias',
      'catch up sales', 'catch up', 'catch-up sales', 'catch-up',
      'prices are vulnerable', 'price weakness expected', 'downside risk',
      'selling pressure', 'prices to decline', 'lower prices expected',
      'price downside', 'technical weakness', 'fund selling pressure'
    ]
  };

  const explicitBullish = explicitBiasKeywords.bullish.filter(kw => textLower.includes(kw));
  const explicitBearish = explicitBiasKeywords.bearish.filter(kw => textLower.includes(kw));

  let marketMood;
  let biasSource;

  // HIGHEST PRIORITY: "Catch up sales" with negation is BULLISH
  if ((textLower.includes('catch up') || textLower.includes('catch-up')) &&
      (textLower.includes('not advised') || textLower.includes('not recommended'))) {
    marketMood = 'bullish';
    biasSource = 'catch up sales not advised';
  }
  else if (textLower.includes('catch up') || textLower.includes('catch-up')) {
    marketMood = 'bearish';
    biasSource = 'catch up sales';
  }
  else if (explicitBullish.length > 0 && explicitBearish.length === 0) {
    marketMood = 'bullish';
    biasSource = explicitBullish[0];
  } else if (explicitBearish.length > 0 && explicitBullish.length === 0) {
    marketMood = 'bearish';
    biasSource = explicitBearish[0];
  } else if (explicitBullish.length > 0 && explicitBearish.length > 0) {
    const lastBullish = Math.max(...explicitBullish.map(kw => textLower.indexOf(kw)));
    const lastBearish = Math.max(...explicitBearish.map(kw => textLower.indexOf(kw)));
    if (lastBearish > lastBullish) {
      marketMood = 'bearish';
      biasSource = explicitBearish[0];
    } else {
      marketMood = 'bullish';
      biasSource = explicitBullish[0];
    }
  } else {
    const bullishCount = bullishKeywords.filter(kw => textLower.includes(kw)).length;
    const bearishCount = bearishKeywords.filter(kw => textLower.includes(kw)).length;

    if (bullishCount > bearishCount + 2) {
      marketMood = 'bullish';
      biasSource = 'keyword analysis';
    } else if (bearishCount > bullishCount + 1) {
      marketMood = 'bearish';
      biasSource = 'keyword analysis';
    } else {
      marketMood = 'neutral';
      biasSource = 'keyword analysis';
    }
  }

  // Weather impact
  const weatherPos = weatherPositiveForCrops.filter(kw => textLower.includes(kw)).length;
  const weatherNeg = weatherNegativeForCrops.filter(kw => textLower.includes(kw)).length;

  let weatherImpact;
  if (weatherPos > weatherNeg) {
    weatherImpact = 'positive_for_crops';
  } else if (weatherNeg > weatherPos) {
    weatherImpact = 'negative_for_crops';
  } else if (weatherPos > 0 || weatherNeg > 0) {
    weatherImpact = 'mixed';
  } else {
    weatherImpact = 'neutral';
  }

  // Production outlook
  const optimisticWords = ['optimistic', 'positive', 'improving', 'good'];
  const cautiousWords = ['cautious', 'concerns', 'uncertain', 'wait'];

  const optCount = optimisticWords.filter(w => textLower.includes(w)).length;
  const caCount = cautiousWords.filter(w => textLower.includes(w)).length;

  let productionOutlook;
  if (optCount > caCount) {
    productionOutlook = 'optimistic';
  } else if (caCount > optCount) {
    productionOutlook = 'cautious';
  } else {
    productionOutlook = 'uncertain';
  }

  // Sales advice
  let salesAdvice;
  if (textLower.includes('catch up') && !textLower.includes('not advised')) {
    salesAdvice = 'Catch up sales recommended';
  } else if (textLower.includes('no sales recommended') || textLower.includes('hold')) {
    salesAdvice = 'No sales recommended at this time';
  } else if (textLower.includes('buy') || textLower.includes('sell') || textLower.includes('recommend')) {
    salesAdvice = 'New sales advice detected';
  } else {
    salesAdvice = 'Position status unchanged';
  }

  // Key phrases
  const keyPhrases = [];
  if (explicitBullish.length > 0 || explicitBearish.length > 0) {
    const biasPhrases = explicitBullish.length > 0 ? explicitBullish : explicitBearish;
    for (const bp of biasPhrases) {
      if (!keyPhrases.includes(bp)) {
        keyPhrases.push(bp);
      }
    }
  }

  const phrasePositions = [];
  const allKeywords = [...bullishKeywords, ...bearishKeywords];
  for (const kw of allKeywords) {
    if (textLower.includes(kw) && !keyPhrases.includes(kw)) {
      const pos = textLower.indexOf(kw);
      phrasePositions.push([pos, kw]);
    }
  }

  phrasePositions.sort((a, b) => a[0] - b[0]);
  for (const [pos, kw] of phrasePositions.slice(0, 15)) {
    keyPhrases.push(kw);
  }

  // Confidence
  const uniqueBullish = new Set(bullishKeywords.filter(kw => textLower.includes(kw))).size;
  const uniqueBearish = new Set(bearishKeywords.filter(kw => textLower.includes(kw))).size;
  const uniqueWeather = new Set([...weatherPositiveForCrops, ...weatherNegativeForCrops]
    .filter(kw => textLower.includes(kw))).size;

  let confidence;
  if (explicitBullish.length > 0 || explicitBearish.length > 0) {
    confidence = 'high';
  } else if (uniqueBullish + uniqueBearish > 5) {
    confidence = 'high';
  } else if (uniqueBullish + uniqueBearish > 2) {
    confidence = 'medium';
  } else {
    confidence = 'low';
  }

  return {
    market_mood: marketMood,
    weather_impact: weatherImpact,
    production_outlook: productionOutlook,
    sales_advice: salesAdvice,
    key_phrases: keyPhrases.slice(0, 15),
    confidence: confidence,
    bias_source: biasSource
  };
}

/**
 * Extract date and time from newsletter content
 */
function extractDateTime(content, filename) {
  // Try to extract from filename first
  const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
  if (dateMatch) {
    const date = dateMatch[1];

    // Try to extract time from content
    const timeMatch = content.match(/(\d{1,2}:\d{2}\s*(AM|PM))/i);
    const time = timeMatch ? timeMatch[1] : '12:00 AM';

    return { date, time };
  }

  // Try alternative date formats
  const altMatch = content.match(/(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})/i);
  if (altMatch) {
    const monthMap = {
      'January': '01', 'February': '02', 'March': '03', 'April': '04',
      'May': '05', 'June': '06', 'July': '07', 'August': '08',
      'September': '09', 'October': '10', 'November': '11', 'December': '12'
    };
    const month = monthMap[altMatch[1]];
    const day = altMatch[2].padStart(2, '0');
    const year = altMatch[3];
    const date = `${year}-${month}-${day}`;

    const timeMatch = content.match(/(\d{1,2}:\d{2}\s*(AM|PM))/i);
    const time = timeMatch ? timeMatch[1] : '12:00 AM';

    return { date, time };
  }

  return null;
}

/**
 * Main rebuild function
 */
async function rebuildSentiment() {
  console.log('Rebuilding sentiment analysis from existing newsletters...\n');

  try {
    await fs.mkdir(MEMORY_DIR, { recursive: true });

    // Read all markdown files
    const files = await fs.readdir(MEMORY_DIR);
    const mdFiles = files.filter(f => f.endsWith('.md') &&
      !f.includes('summary') && !f.includes('fix') && !f.includes('cleanup'));

    console.log(`Found ${mdFiles.length} newsletter files to analyze:\n`);

    const sentimentHistory = [];

    for (const file of mdFiles) {
      const filePath = path.join(MEMORY_DIR, file);
      const content = await fs.readFile(filePath, 'utf8');

      const dateTime = extractDateTime(content, file);
      if (!dateTime) {
        console.log(`Skipping ${file} - could not extract date`);
        continue;
      }

      console.log(`Analyzing ${file} (${dateTime.date} ${dateTime.time})...`);

      const sentiment = analyzeSentiment(content);

      sentimentHistory.push({
        date: dateTime.date,
        time: dateTime.time,
        trend_direction: 'stable', // Will be calculated separately
        previous_mood: null, // Will be calculated separately
        ...sentiment
      });
    }

    // Sort by date and time
    sentimentHistory.sort((a, b) => {
      const dtA = new Date(`${a.date} ${a.time}`);
      const dtB = new Date(`${b.date} ${b.time}`);
      return dtA - dtB;
    });

    // Calculate trend direction
    for (let i = 1; i < sentimentHistory.length; i++) {
      const current = sentimentHistory[i];
      const previous = sentimentHistory[i - 1];
      current.previous_mood = previous.market_mood;

      if (current.market_mood === previous.market_mood) {
        current.trend_direction = 'stable';
      } else if (
        (current.market_mood === 'bullish' && previous.market_mood === 'bearish') ||
        (current.market_mood === 'bullish' && previous.market_mood === 'neutral') ||
        (current.market_mood === 'neutral' && previous.market_mood === 'bearish')
      ) {
        current.trend_direction = 'improving';
      } else {
        current.trend_direction = 'declining';
      }
    }

    // Save sentiment history
    const historyData = {
      last_updated: new Date().toISOString(),
      sentiment_history: sentimentHistory
    };

    await fs.writeFile(SENTIMENT_HISTORY_FILE, JSON.stringify(historyData, null, 2), 'utf8');
    console.log(`\n✓ Sentiment history saved: ${sentimentHistory.length} entries`);

    // Print summary
    console.log('\n--- Sentiment Summary ---');
    const bullish = sentimentHistory.filter(e => e.market_mood === 'bullish').length;
    const bearish = sentimentHistory.filter(e => e.market_mood === 'bearish').length;
    const neutral = sentimentHistory.filter(e => e.market_mood === 'neutral').length;

    console.log(`Bullish: ${bullish}`);
    console.log(`Bearish: ${bearish}`);
    console.log(`Neutral: ${neutral}`);
    console.log(`Total: ${sentimentHistory.length}`);

    console.log('\nMost recent entries:');
    sentimentHistory.slice(-5).forEach(entry => {
      console.log(`  ${entry.date} ${entry.time} - ${entry.market_mood.toUpperCase()} (${entry.bias_source})`);
    });

  } catch (error) {
    console.error('Error rebuilding sentiment:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  rebuildSentiment();
}

module.exports = { rebuildSentiment, analyzeSentiment };
