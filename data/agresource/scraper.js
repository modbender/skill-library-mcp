#!/usr/bin/env node
/**
 * AgResource Newsletter Scraper
 *
 * Logs in to AgResource dashboard and scrapes daily newsletter content.
 * Uses Playwright directly to handle JavaScript-rendered content.
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const AGRESOURCE_URL = 'https://agresource.com/dashboard/#/reports/daily';
const AGRESOURCE_EMAIL = process.env.AGRESOURCE_EMAIL || 'brianppetty@yahoo.com';
const AGRESOURCE_PASSWORD = process.env.AGRESOURCE_PASSWORD || '4BrynnElizabeth';
const MEMORY_DIR = path.join(require('os').homedir(), 'clawd', 'memory', 'agresource');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const params = { type: 'morning' }; // Default to morning

  for (const arg of args) {
    if (arg.startsWith('--type=')) {
      params.type = arg.split('=')[1].toLowerCase();
    }
  }

  return params;
}

// Valid newsletter types
const VALID_TYPES = ['morning', 'noon', 'evening', 'saturday', 'sunday'];

/**
 * Get current timestamp in Eastern time
 */
function getCurrentTimestamp() {
  const now = new Date();
  const etOffset = -5; // Eastern is UTC-5 (simplified)
  const etTime = new Date(now.getTime() + etOffset * 60 * 60 * 1000);
  return etTime.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

/**
 * Ensure memory directory exists
 */
async function ensureMemoryDir() {
  try {
    await fs.mkdir(MEMORY_DIR, { recursive: true });
  } catch (err) {
    console.error(`Failed to create memory directory: ${err}`);
  }
}

/**
 * Click on the correct newsletter tab
 */
async function selectNewsletterTab(page, type) {
  const tabMap = {
    'morning': 'Morning',
    'noon': 'Noon',
    'evening': 'Evening',
    'saturday': 'Saturday',
    'sunday': 'Sunday'
  };

  const tabName = tabMap[type];
  if (!tabName) {
    throw new Error(`Invalid newsletter type: ${type}. Valid types: ${VALID_TYPES.join(', ')}`);
  }

  console.log(`Selecting ${tabName} tab...`);

  // Click on the tab
  await page.locator(`.tab:has-text("${tabName}")`).click();

  // Wait for the content to load after switching tabs
  await page.waitForTimeout(2000);

  console.log(`${tabName} tab selected`);
}

/**
 * Scrape AgResource newsletter
 * @param {string} type - Newsletter type: morning, noon, evening, saturday, sunday
 */
async function scrapeNewsletter(type = 'morning') {
  console.log(`AgResource Newsletter Scraper - ${getCurrentTimestamp()}`);
  console.log(`Newsletter type: ${type}`);
  console.log('Starting browser...');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log(`Navigating to ${AGRESOURCE_URL}`);
    await page.goto(AGRESOURCE_URL, { waitUntil: 'networkidle', timeout: 30000 });

    // Wait for React app to fully load
    await page.waitForTimeout(5000);

    // Check if login page is present by looking for login form elements
    const hasLoginForm = await page.locator('input[type="email"], #email').count() > 0;
    const hasLoginButton = await page.locator('button[type="submit"], button:has-text("Log in")').count() > 0;

    const needsLogin = hasLoginForm && hasLoginButton;

    if (needsLogin) {
      console.log('Login required, submitting credentials...');

      // Find and fill email field
      try {
        const emailField = await page.locator('input[type="email"], input[name="email"], #email').first();
        await emailField.fill(AGRESOURCE_EMAIL);
        await page.waitForTimeout(500);

        // Find and fill password field
        const passwordField = await page.locator('input[type="password"], input[name="password"], #password').first();
        await passwordField.fill(AGRESOURCE_PASSWORD);
        await page.waitForTimeout(500);

        // Find and click login button
        const loginButton = await page.locator('button[type="submit"], button:has-text("Log in"), button:has-text("Sign in"), .login-button').first();
        await loginButton.click();
        console.log('Login submitted, waiting for dashboard...');

        // Wait for navigation to complete
        await page.waitForLoadState('networkidle', { timeout: 10000 });
        await page.waitForTimeout(3000);
      } catch (err) {
        console.log(`Login attempt had issues: ${err.message}`);
      }
    } else {
      console.log('Already logged in or login not required');
    }

    // Select the correct newsletter tab
    await selectNewsletterTab(page, type);

    // Click on the most recent newsletter to open it
    console.log('Clicking on most recent newsletter...');
    try {
      // Wait for the newsletter list to load
      await page.waitForSelector('.reports.mostRecent, .reports', { timeout: 10000 });

      // Check if we're on the list view (has multiple reports) or already on detail view
      const reportCount = await page.locator('.reports').count();

      if (reportCount > 1) {
        // We're on the list view - click the first (most recent) newsletter
        console.log(`Found ${reportCount} reports, clicking most recent...`);
        await page.locator('.reports.mostRecent').first().click();
        // Wait for the detail view to load
        await page.waitForTimeout(3000);
      } else {
        console.log('Already on detail view or only one report found');
      }
    } catch (err) {
      console.log(`Could not click newsletter: ${err.message}, continuing with current view`);
    }

    // Get page content
    console.log('Extracting newsletter content...');
    const htmlContent = await page.content();
    const textContent = await page.textContent('body');

    // Take screenshot for reference
    const dateStr = new Date().toISOString().split('T')[0];
    const screenshotPath = path.join(MEMORY_DIR, `${dateStr}-screenshot.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`Screenshot saved to ${screenshotPath}`);

    // Parse newsletter content
    const newsletter = parseNewsletterContent(textContent, htmlContent);

    await browser.close();
    return newsletter;

  } catch (err) {
    console.error(`Error during scraping: ${err}`);
    await browser.close();
    return getErrorResult(err.message);
  }
}

/**
 * Parse newsletter content from page text/HTML
 */
function parseNewsletterContent(text, html) {
  const textLower = text.toLowerCase();

  // Extract Farm Marketing Advice section (contains commodity-specific advice)
  const farmMarketingAdvice = extractFarmMarketingAdvice(text);

  // Extract CBOT Grain Prices section
  const grainPrices = extractGrainPrices(text);

  // Extract Speculative/Fund Positioning section (CFTC CoT report)
  const speculativePositioning = extractSpeculativePositioning(text);

  // Extract weather information
  const weather = extractWeatherSection(text);

  // Extract news items
  const newsItems = extractNewsItems(text);

  return {
    timestamp: getCurrentTimestamp(),
    title: 'AgResource Daily Newsletter',
    summary: generateSummary(newsItems, weather),
    corn_advice: farmMarketingAdvice.corn || grainPrices,
    soybean_advice: farmMarketingAdvice.soybeans || grainPrices,
    positions: grainPrices,
    speculative_positioning: speculativePositioning, // NEW: Fund/speculative positioning
    key_news: newsItems,
    weather_info: weather,
    full_content: text.substring(0, 15000), // Increased for more complete content
    html_content: html.substring(0, 5000)
  };
}

/**
 * Extract Farm Marketing Advice section - contains specific sales advice by commodity
 */
function extractFarmMarketingAdvice(text) {
  const advice = {
    wheat: '',
    corn: '',
    soybeans: ''
  };

  // Look for "AgResource Farm Marketing Advice" section
  // Format: "AgResource Farm Marketing Advice for Friday: 1/ Wheat Producers: Sell..."
  // The text may be all on one line, so we need to handle that
  const marketingAdviceRegex = /AgResource Farm Marketing Advice[^:]*:\s*([\s\S]*?)(?=\n\s*AgResource|\s+CBOT|\nParís|$)/i;
  const marketingMatch = text.match(marketingAdviceRegex);

  if (marketingMatch) {
    let marketingText = marketingMatch[1];

    // Extract individual commodity advice (format: "1/ Wheat Producers: ...")
    // Wheat advice
    const wheatMatch = marketingText.match(/\/?\s*\d*\/?\s*Wheat[^:]*:\s*([^\n]*?(?=\n\/|\n\s*\d|AgResource|CBOT|$))/i);
    if (wheatMatch) {
      advice.wheat = wheatMatch[1].trim();
    }

    // Corn advice
    const cornMatch = marketingText.match(/\/?\s*\d*\/?\s*Corn[^:]*:\s*([^\n]*?(?=\n\/|\n\s*\d|AgResource|CBOT|$))/i);
    if (cornMatch) {
      advice.corn = cornMatch[1].trim();
    }

    // Soybean advice
    const soyMatch = marketingText.match(/\/?\s*\d*\/?\s*Soybean[^:]*:\s*([^\n]*?(?=\n\/|\n\s*\d|AgResource|CBOT|$))/i);
    if (soyMatch) {
      advice.soybeans = soyMatch[1].trim();
    }

    // If we didn't get structured advice, try to get the whole section
    if (!advice.wheat && !advice.corn && !advice.soybeans) {
      advice.general = marketingText.trim().substring(0, 300);
    }
  }

  return advice;
}

/**
 * Extract CBOT Grain Prices section
 */
function extractGrainPrices(text) {
  // Look for CBOT Grain Prices section - extract the price data
  // Handle "CBOT Grain Prices as of 6:30 AM CT: March soybeans..."
  // Use negative lookbehind or split differently
  const lines = text.split('\n');
  for (const line of lines) {
    if (line.includes('CBOT Grain Prices')) {
      // Extract the whole price line
      const pricesMatch = line.match(/CBOT Grain Prices.*/);
      if (pricesMatch) {
        return pricesMatch[0];
      }
    }
  }

  return '';
}

/**
 * Extract Weather section - focuses on South American weather
 */
function extractWeatherSection(text) {
  // Look for South American Weather Headlines section
  const weatherRegex = /South American Weather[^:]*:(.*?)(?=\n\n|AgResource|AgResource|$)/is;
  const match = text.match(weatherRegex);

  if (match) {
    return match[1].trim().substring(0, 800);
  }

  // Fallback to any weather section
  const fallbackRegex = /Weather[^:]*:(.*?)(?=\n\n|AgResource|$)/is;
  const fallbackMatch = text.match(fallbackRegex);

  if (fallbackMatch) {
    return fallbackMatch[1].trim().substring(0, 800);
  }

  return '';
}

/**
 * Extract Speculative/Fund Positioning section (CFTC CoT report data)
 * This contains fund/speculator positions that may be relevant for trading
 */
function extractSpeculativePositioning(text) {
  const positioning = {
    summary: '',
    corn: '',
    soybeans: '',
    wheat: '',
    funds_net_short: '',
    index_fund_rebalance: ''
  };

  // Look for CFTC CoT report section
  const cotRegex = /CFTC[^:]*?:[\s\S]*?(?=South American|París|Malaysian|$)/i;
  const cotMatch = text.match(cotRegex);

  if (cotMatch) {
    const cotText = cotMatch[0];

    // Extract overall summary
    const summaryMatch = cotText.match(/The report showed[^\.]*\./i);
    if (summaryMatch) {
      positioning.summary = summaryMatch[0].trim();
    }

    // Extract corn positioning
    const cornMatch = cotText.match(/corn[^:]*?:[^\.]*?\.(?:\s[^\.]*?\.|)/i);
    if (cornMatch) {
      positioning.corn = cornMatch[0].trim();
    }

    // Extract soybean positioning
    const soyMatch = cotText.match(/soybean[^:]*?:[^\.]*?\.(?:\s[^\.]*?\.|)/i);
    if (soyMatch) {
      positioning.soybeans = soyMatch[0].trim();
    }

    // Extract wheat positioning (Chicago, MN, KC)
    const wheatMatch = cotText.match(/wheat[^:]*?:[^\.]*?\.(?:\s[^\.]*?\.|)/i);
    if (wheatMatch) {
      positioning.wheat = wheatMatch[0].trim();
    }

    // Check if funds are net short
    const netShortMatch = cotText.match(/Funds were net short[^\.]*\./i);
    if (netShortMatch) {
      positioning.funds_net_short = netShortMatch[0].trim();
    }
  }

  // Look for index fund rebalance information (even if no CFTC data)
  const rebalanceRegex = /Index Fund rebalance[^\.]*\./i;
  const rebalanceMatch = text.match(rebalanceRegex);
  if (rebalanceMatch) {
    positioning.index_fund_rebalance = rebalanceMatch[0].trim();
  }

  // Look for fund selling/buying activity
  const fundActivityRegex = /fund (?:selling|buying|short covering|liquidation)[^\.]*\./gi;
  const fundActivityMatches = text.match(fundActivityRegex);
  if (fundActivityMatches && fundActivityMatches.length > 0) {
    positioning.fund_activity = fundActivityMatches.join('; ').trim();
  }

  // Return empty string if no data found at all
  const hasAnyData = positioning.summary || positioning.corn || positioning.soybeans ||
                      positioning.wheat || positioning.funds_net_short ||
                      positioning.index_fund_rebalance || positioning.fund_activity;

  if (!hasAnyData) {
    return '';
  }

  return positioning;
}

/**
 * Extract news items looking for bullet points or numbered lists
 */
function extractNewsItems(text) {
  const items = [];

  // Look for bullet patterns
  const patterns = [
    /[•\-\*]\s+([^.!?]+[.!?])/gi,
    /\d+\.\s+([^.!?]+[.!?])/gi,
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null && items.length < 5) {
      items.push(match[1].trim());
    }
  }

  // Filter to grain-relevant items
  const grainKeywords = ['corn', 'soy', 'wheat', 'grain', 'market', 'price', 'demand',
                         'export', 'weather', 'yield', 'crop', 'harvest', 'planting', 'production'];

  const filteredItems = items
    .filter(item => grainKeywords.some(kw => item.toLowerCase().includes(kw)))
    .map(item => item.substring(0, 200)) // Limit length
    .slice(0, 10); // Return max 10 items

  return filteredItems;
}

/**
 * Generate a brief summary from news and weather
 */
function generateSummary(newsItems, weather) {
  if (!newsItems.length && !weather) {
    return 'No significant updates available.';
  }

  const summaryParts = [];

  if (newsItems.length) {
    summaryParts.push(`Key updates include: ${newsItems[0].substring(0, 100)}...`);
  }

  if (weather) {
    summaryParts.push(`Weather conditions: ${weather.substring(0, 100)}...`);
  }

  return summaryParts.join(' ');
}

/**
 * Return error result
 */
function getErrorResult(message) {
  return {
    timestamp: getCurrentTimestamp(),
    title: 'AgResource Daily Newsletter',
    summary: `Error: ${message}`,
    corn_advice: '',
    soybean_advice: '',
    positions: '',
    key_news: [],
    weather_info: '',
    full_content: `Scraping failed: ${message}`,
    error: true
  };
}

/**
 * Save newsletter summary to markdown file
 */
async function saveSummary(newsletterData, type = 'morning') {
  const dateStr = new Date().toISOString().split('T')[0];
  const timeSuffix = type !== 'morning' ? `-${type}` : '';
  const outputFile = path.join(MEMORY_DIR, `${dateStr}${timeSuffix}.md`);

  let summaryContent = `# AgResource Newsletter - ${newsletterData.timestamp}

## Quick Summary
${newsletterData.summary || 'No summary available'}

## Key Newsworthy Items
${newsletterData.key_news.length > 0
  ? newsletterData.key_news.map(item => `- ${item}`).join('\n')
  : '- No key news items'}

## Sales Advice Status
- Corn: ${newsletterData.corn_advice || 'No specific advice'}
- Soybeans: ${newsletterData.soybean_advice || 'No specific advice'}

## Current Positions
${newsletterData.positions || 'No positioning info available'}
`;

  // Add speculative/fund positioning section if available
  if (newsletterData.speculative_positioning) {
    const spec = newsletterData.speculative_positioning;
    summaryContent += `
## Speculative/Fund Positioning (CFTC CoT Report)
`;
    if (spec.summary) {
      summaryContent += `- ${spec.summary}\n`;
    }
    if (spec.index_fund_rebalance) {
      summaryContent += `- ${spec.index_fund_rebalance}\n`;
    }
    if (spec.fund_activity) {
      summaryContent += `- Fund Activity: ${spec.fund_activity}\n`;
    }
    if (spec.corn) {
      summaryContent += `- Corn: ${spec.corn}\n`;
    }
    if (spec.soybeans) {
      summaryContent += `- Soybeans: ${spec.soybeans}\n`;
    }
    if (spec.wheat) {
      summaryContent += `- Wheat: ${spec.wheat}\n`;
    }
    if (spec.funds_net_short) {
      summaryContent += `- ${spec.funds_net_short}\n`;
    }
    summaryContent += `\n`;
  }

  summaryContent += `## Weather
${newsletterData.weather_info || 'No weather info available'}

## Full Content
${newsletterData.full_content?.substring(0, 2000) || 'Full content not available'}
`;

  await fs.writeFile(outputFile, summaryContent, 'utf-8');
  return outputFile;
}

/**
 * Update sentiment history JSON file
 */
async function updateSentimentHistory(sentimentData) {
  const sentimentFile = path.join(MEMORY_DIR, 'sentiment_history.json');

  let data;
  try {
    const existing = await fs.readFile(sentimentFile, 'utf-8');
    data = JSON.parse(existing);
  } catch (err) {
    data = { last_updated: null, sentiment_history: [] };
  }

  // Add new sentiment entry
  data.last_updated = new Date().toISOString();
  data.sentiment_history.push(sentimentData);

  // Keep only last 20 entries
  if (data.sentiment_history.length > 20) {
    data.sentiment_history = data.sentiment_history.slice(-20);
  }

  await fs.writeFile(sentimentFile, JSON.stringify(data, null, 2));
  return data;
}

/**
 * Run sentiment analysis on newsletter content
 * Focused on PRICE IMPACT
 */
function analyzeSentiment(text) {
  const textLower = text.toLowerCase();

  // BULLISH = Prices expected to go UP
  const bullishKeywords = [
    // Direct price signals
    'prices advancing', 'prices rally', 'price strength', 'higher prices',
    'support', 'rally', 'gains', 'upward trend', 'strength', 'bullish',

    // Demand signals (more demand = higher prices)
    'demand strong', 'export demand rising', 'strong demand', 'demand solid',
    'china buying', 'china purchases', 'china advancing', 'chinese imports',
    'record demand', 'export sales', 'new sales', 'flash sales',

    // Supply constraints (less supply = higher prices)
    'production cuts', 'production issues', 'supply concerns',
    'tight supplies', 'tight stocks', 'stock drawdown', 'inventory tight',

    // Weather stress on crops (less yield = higher prices)
    'drought', 'drought stress', 'heat stress', 'excessive heat',
    'dry conditions', 'moisture stress', 'weather concerns',
    'weather damage', 'crop stress', 'yield pressure', 'yield concerns',

    // Geopolitical/Supply chain
    'tariff threats', 'supply disruptions', 'logistics issues',

    // Index fund activity
    'index fund buying', 'fund buying', 'speculative buying',
  ];

  // BEARISH = Prices expected to go DOWN
  const bearishKeywords = [
    // Direct price signals
    'prices declining', 'price weakness', 'lower prices',
    'resistance', 'sell-off', 'losses', 'downward trend', 'weakness', 'bearish',

    // Demand weakness (less demand = lower prices)
    'weak demand', 'demand concerns', 'lackluster demand',
    'export concerns', 'export weakness', 'china auctioning', 'china selling',

    // Supply glut (more supply = lower prices)
    'record crop', 'record production', 'large crop', 'bumper crop',
    'production increasing', 'supply ample', 'supplies adequate',
    'stock buildup', 'inventory building', 'production on track for record',
    'harvest record', 'record.*crop', 'record.*production',

    // Favorable weather (more yield = lower prices)
    'favorable weather', 'ideal conditions', 'timely rains',
    'adequate moisture', 'beneficial rainfall', 'normal weather',
    'good growing conditions', 'improved weather', 'weather improving',
    'rain starting to fall', 'rains.*starting', 'rainfall.*slated',

    // Trade/tariff issues reducing exports
    'tariff concerns', 'trade uncertainty', 'trade barriers',
    'export competition', 'south america', 'brazil', 'argentina production',

    // Index fund activity
    'index fund selling', 'fund selling', 'speculative selling',
    'fund rebalance', 'index fund rebalance',
  ];

  // Weather that's positive for crops (BEARISH for prices)
  const weatherPositiveForCrops = [
    'favorable', 'beneficial', 'improving', 'adequate moisture',
    'timely rains', 'ideal conditions', 'normal', 'good weather'
  ];

  // Weather that's negative for crops (BULLISH for prices)
  const weatherNegativeForCrops = [
    'drought', 'excessive', 'flooding', 'heat stress',
    'dry conditions', 'moisture stress', 'weather concerns',
    'hot and dry', 'below normal moisture', 'stress'
  ];

  // Detect explicit bias statements from AgResource (AUTHORITATIVE)
  // These should dominate sentiment determination over simple keyword counting
  const explicitBiasKeywords = {
    bullish: [
      // Direct bias statements
      'bullish bias', 'bullish bias maintained', 'bullish outlook',
      'favorable bias', 'positive bias',

      // Hold/No sales = BULLISH (expecting higher prices)
      'no sales recommended', 'not advised', 'hold grain', 'hold old crop',
      'wait to sell', 'wait for higher prices', 'hold for better prices',

      // Expert buying recommendations (BULLISH for prices)
      'buyers should be aggressive', 'recommended to buy', 'advise buying',
      'increase sales', 'aggressive selling', 'make sales', 'new crop sales',
      'forward contracting', 'pricing opportunities'

      // Note: "sales" in AgResource context means farmers SELLING grain
      // When they recommend selling, it's because prices are HIGH (bullish)
      // When they say "catch up sales", it means sell NOW before prices drop (bearish)
      // When they say "catch up sales NOT advised", it means HOLD (bullish)
    ],
    bearish: [
      // Direct bias statements
      'bearish bias', 'bearish bias maintained', 'bearish outlook',
      'negative bias', 'unfavorable bias',

      // Expert selling urgency phrases (BEARISH - sell before prices drop further)
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

  // HIGHEST PRIORITY: "Catch up sales" with negation is BULLISH (hold = prices rising)
  if ((textLower.includes('catch up') || textLower.includes('catch-up')) &&
      (textLower.includes('not advised') || textLower.includes('not recommended'))) {
    marketMood = 'bullish';
    biasSource = 'catch up sales not advised';
  }
  // "Catch up sales" WITHOUT negation is extremely bearish - sell before prices drop
  // This overrides ALL other signals as it's AgResource's strongest selling urgency
  else if (textLower.includes('catch up') || textLower.includes('catch-up')) {
    marketMood = 'bearish';
    biasSource = 'catch up sales';
  }
  // If explicit bias exists, it dominates
  else if (explicitBullish.length > 0 && explicitBearish.length === 0) {
    marketMood = 'bullish';
    biasSource = explicitBullish[0];
  } else if (explicitBearish.length > 0 && explicitBullish.length === 0) {
    marketMood = 'bearish';
    biasSource = explicitBearish[0];
  } else if (explicitBullish.length > 0 && explicitBearish.length > 0) {
    // Conflicting explicit statements - use last mentioned
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
    // No explicit bias - fall back to keyword counting
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

  // Detect weather impact on PRODUCTION (not prices)
  const weatherPos = weatherPositiveForCrops.filter(kw => textLower.includes(kw)).length;
  const weatherNeg = weatherNegativeForCrops.filter(kw => textLower.includes(kw)).length;

  let weatherImpact;
  if (weatherPos > weatherNeg) {
    weatherImpact = 'positive_for_crops';  // Good for crops = BEARISH for prices
  } else if (weatherNeg > weatherPos) {
    weatherImpact = 'negative_for_crops';  // Bad for crops = BULLISH for prices
  } else if (weatherPos > 0 || weatherNeg > 0) {
    weatherImpact = 'mixed';
  } else {
    weatherImpact = 'neutral';
  }

  // Detect production outlook (PRICE IMPACT inverted)
  // Optimistic production = more supply = BEARISH for prices
  const optimisticWords = ['optimistic', 'positive', 'improving', 'good'];
  const cautiousWords = ['cautious', 'concerns', 'uncertain', 'wait'];

  const optCount = optimisticWords.filter(w => textLower.includes(w)).length;
  const caCount = cautiousWords.filter(w => textLower.includes(w)).length;

  let productionOutlook;
  if (optCount > caCount) {
    productionOutlook = 'optimistic';  // More supply = BEARISH price implication
  } else if (caCount > optCount) {
    productionOutlook = 'cautious';  // Supply concerns = BULLISH price implication
  } else {
    productionOutlook = 'uncertain';
  }

  // Detect sales advice
  // IMPORTANT: In AgResource context, "no sales" or "hold" = BULLISH (expecting higher prices)
  // "Catch up sales" = BEARISH (sell before prices drop)
  // "Catch up sales NOT advised" = BULLISH (hold, prices going up)
  let salesAdvice;
  if (textLower.includes('catch up') && !textLower.includes('not advised') && !textLower.includes("not advised")) {
    salesAdvice = 'Catch up sales recommended';
  } else if (textLower.includes('no sales recommended') || textLower.includes('hold')) {
    salesAdvice = 'No sales recommended at this time';
  } else if (textLower.includes('buy') || textLower.includes('sell') || textLower.includes('recommend')) {
    salesAdvice = 'New sales advice detected';
  } else {
    salesAdvice = 'Position status unchanged';
  }

  // Extract key phrases (order by position in text, except explicit bias goes first)
  const keyPhrases = [];

  // Add explicit bias statement first if found
  if (explicitBullish.length > 0 || explicitBearish.length > 0) {
    const biasPhrases = explicitBullish.length > 0 ? explicitBullish : explicitBearish;
    for (const bp of biasPhrases) {
      if (!keyPhrases.includes(bp)) {
        keyPhrases.push(bp);
      }
    }
  }

  // Add other phrases, ordered by their position in text
  const phrasePositions = [];
  const allKeywords = [...bullishKeywords, ...bearishKeywords];
  for (const kw of allKeywords) {
    if (textLower.includes(kw) && !keyPhrases.includes(kw)) {  // Don't duplicate bias statements
      const pos = textLower.indexOf(kw);
      phrasePositions.push([pos, kw]);
    }
  }

  // Sort by position and extract phrases
  phrasePositions.sort((a, b) => a[0] - b[0]);
  for (const [pos, kw] of phrasePositions) {
    keyPhrases.push(kw);
  }

  // Determine confidence based on unique signals
  const uniqueBullish = new Set(bullishKeywords.filter(kw => textLower.includes(kw))).size;
  const uniqueBearish = new Set(bearishKeywords.filter(kw => textLower.includes(kw))).size;
  const uniqueWeather = new Set([...weatherPositiveForCrops, ...weatherNegativeForCrops]
    .filter(kw => textLower.includes(kw))).size;

  // Variables already declared at lines 451-452
  const uniqueProduction = new Set([...optimisticWords, ...cautiousWords]
    .filter(w => textLower.includes(w))).size;

  const totalUniqueSignals = uniqueBullish + uniqueBearish + uniqueWeather + uniqueProduction;
  let confidence;
  if (totalUniqueSignals >= 8) {
    confidence = 'high';
  } else if (totalUniqueSignals >= 5) {
    confidence = 'medium';
  } else {
    confidence = 'low';
  }

  return {
    market_mood: marketMood,
    weather_impact: weatherImpact,
    production_outlook: productionOutlook,
    sales_advice: salesAdvice,
    key_phrases: keyPhrases,
    confidence: confidence,
    bias_source: biasSource  // What determined the sentiment
  };
}

/**
 * Load sentiment history from file
 */
async function loadSentimentHistory() {
  try {
    const content = await fs.readFile(
      path.join(MEMORY_DIR, 'sentiment_history.json'),
      'utf8'
    );
    return JSON.parse(content);
  } catch (err) {
    return { sentiment_history: [] };
  }
}

/**
 * Save sentiment history to file
 */
async function saveSentimentHistory(data) {
  await fs.writeFile(
    path.join(MEMORY_DIR, 'sentiment_history.json'),
    JSON.stringify(data, null, 2),
    'utf8'
  );
}

/**
 * Generate daily sentiment summary
 */
function generateDailySummary(entries, date) {
  if (!entries || entries.length === 0) {
    return null;
  }

  // Aggregate sentiment data for the day
  const bullishCount = entries.filter(e => e.market_mood === 'bullish').length;
  const bearishCount = entries.filter(e => e.market_mood === 'bearish').length;
  const neutralCount = entries.filter(e => e.market_mood === 'neutral').length;

  const total = entries.length;
  const bullishPct = total > 0 ? Math.round((bullishCount / total) * 100) : 0;
  const bearishPct = total > 0 ? Math.round((bearishCount / total) * 100) : 0;
  const neutralPct = total > 0 ? Math.round((neutralCount / total) * 100) : 0;

  // Determine dominant mood
  let dominantMood = 'neutral';
  if (bullishCount > bearishCount && bullishCount > neutralCount) {
    dominantMood = 'bullish';
  } else if (bearishCount > bullishCount && bearishCount > neutralCount) {
    dominantMood = 'bearish';
  }

  // Get unique key phrases
  const allPhrases = entries.flatMap(e => e.key_phrases || []);
  const uniquePhrases = [...new Set(allPhrases)].slice(0, 10);

  // Check sales advice
  const salesAdviceEntries = entries.filter(e =>
    e.sales_advice && e.sales_advice.includes('New sales advice')
  );
  const hasNewSalesAdvice = salesAdviceEntries.length > 0;

  return {
    date: date,
    entry_count: total,
    dominant_mood: dominantMood,
    distribution: {
      bullish: bullishCount,
      bearish: bearishCount,
      neutral: neutralCount,
      bullish_pct: bullishPct,
      bearish_pct: bearishPct,
      neutral_pct: neutralPct
    },
    key_phrases: uniquePhrases,
    has_new_sales_advice: hasNewSalesAdvice,
    sales_advice_count: salesAdviceEntries.length
  };
}

/**
 * Generate weekly sentiment summary
 */
function generateWeeklySummary(entries, weekStart, weekEnd) {
  if (!entries || entries.length === 0) {
    return null;
  }

  const daily = {};
  entries.forEach(e => {
    const date = e.date;
    if (!daily[date]) {
      daily[date] = { bullish: 0, bearish: 0, neutral: 0, sales: 0 };
    }
    if (e.market_mood === 'bullish') daily[date].bullish++;
    if (e.market_mood === 'bearish') daily[date].bearish++;
    if (e.market_mood === 'neutral') daily[date].neutral++;
    if (e.sales_advice && e.sales_advice.includes('New sales advice')) {
      daily[date].sales++;
    }
  });

  // Calculate weekly totals
  let totalBullish = 0, totalBearish = 0, totalNeutral = 0, totalSales = 0;
  Object.values(daily).forEach(day => {
    totalBullish += day.bullish;
    totalBearish += day.bearish;
    totalNeutral += day.neutral;
    totalSales += day.sales;
  });

  const totalEntries = entries.length;
  const weeklyMood = totalBullish > totalBearish ? 'bullish' :
                     totalBearish > totalBullish ? 'bearish' : 'neutral';

  // Trend calculation
  const sortedDates = Object.keys(daily).sort();
  const firstHalf = sortedDates.slice(0, Math.ceil(sortedDates.length / 2));
  const secondHalf = sortedDates.slice(Math.ceil(sortedDates.length / 2));

  let firstHalfBullish = 0, firstHalfBearish = 0;
  let secondHalfBullish = 0, secondHalfBearish = 0;

  firstHalf.forEach(date => {
    firstHalfBullish += daily[date].bullish;
    firstHalfBearish += daily[date].bearish;
  });

  secondHalf.forEach(date => {
    secondHalfBullish += daily[date].bullish;
    secondHalfBearish += daily[date].bearish;
  });

  let trend = 'stable';
  if (secondHalfBullish > firstHalfBullish + 1) {
    trend = 'improving';
  } else if (secondHalfBearish > firstHalfBearish + 1) {
    trend = 'declining';
  }

  return {
    week_start: weekStart,
    week_end: weekEnd,
    entry_count: totalEntries,
    weekly_mood: weeklyMood,
    trend: trend,
    totals: {
      bullish: totalBullish,
      bearish: totalBearish,
      neutral: totalNeutral,
      new_sales_advice: totalSales
    },
    daily_breakdown: daily
  };
}

/**
 * Generate monthly sentiment summary
 */
function generateMonthlySummary(entries, year, month) {
  if (!entries || entries.length === 0) {
    return null;
  }

  // Aggregate by mood
  const bullishCount = entries.filter(e => e.market_mood === 'bullish').length;
  const bearishCount = entries.filter(e => e.market_mood === 'bearish').length;
  const neutralCount = entries.filter(e => e.market_mood === 'neutral').length;

  const total = entries.length;
  const monthlyMood = bullishCount > bearishCount ? 'bullish' :
                     bearishCount > bullishCount ? 'bearish' : 'neutral';

  // Sales advice count
  const salesAdviceCount = entries.filter(e =>
    e.sales_advice && e.sales_advice.includes('New sales advice')
  ).length;

  // Get all unique key phrases for the month
  const allPhrases = entries.flatMap(e => e.key_phrases || []);
  const phraseCounts = {};
  allPhrases.forEach(p => {
    phraseCounts[p] = (phraseCounts[p] || 0) + 1;
  });

  // Top phrases by frequency
  const topPhrases = Object.entries(phraseCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)
    .map(([phrase, count]) => `${phrase} (${count})`);

  return {
    year: year,
    month: month,
    entry_count: total,
    monthly_mood: monthlyMood,
    sentiment_distribution: {
      bullish: bullishCount,
      bearish: bearishCount,
      neutral: neutralCount
    },
    new_sales_advice_count: salesAdviceCount,
    top_key_phrases: topPhrases
  };
}

/**
 * Update sentiment summaries (daily, weekly, monthly)
 */
async function updateSentimentSummaries() {
  const history = await loadSentimentHistory();
  const entries = history.sentiment_history || [];

  if (entries.length === 0) {
    console.log('No sentiment entries to summarize');
    return;
  }

  const today = new Date().toISOString().split('T')[0];
  const todayEntries = entries.filter(e => e.date === today);

  // Generate daily summary
  if (todayEntries.length > 0) {
    const dailySummary = generateDailySummary(todayEntries, today);
    if (dailySummary) {
      const dailyFile = path.join(MEMORY_DIR, `sentiment-daily-${today}.json`);
      await fs.writeFile(dailyFile, JSON.stringify(dailySummary, null, 2), 'utf8');
      console.log(`Daily sentiment summary saved to: ${dailyFile}`);
    }
  }

  // Generate weekly summary (last 7 days)
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const weekStart = sevenDaysAgo.toISOString().split('T')[0];
  const weekEntries = entries.filter(e => e.date >= weekStart);

  if (weekEntries.length > 0) {
    const weeklySummary = generateWeeklySummary(weekEntries, weekStart, today);
    if (weeklySummary) {
      const weeklyFile = path.join(MEMORY_DIR, `sentiment-weekly-latest.json`);
      await fs.writeFile(weeklyFile, JSON.stringify(weeklySummary, null, 2), 'utf8');
      console.log(`Weekly sentiment summary saved to: ${weeklyFile}`);
    }
  }

  // Generate monthly summary (current month)
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth(); // 0-indexed
  const monthEntries = entries.filter(e => {
    const entryDate = new Date(e.date);
    return entryDate.getFullYear() === currentYear && entryDate.getMonth() === currentMonth;
  });

  if (monthEntries.length > 0) {
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'];
    const monthlySummary = generateMonthlySummary(monthEntries, currentYear, currentMonth);
    if (monthlySummary) {
      const monthlyFile = path.join(MEMORY_DIR, `sentiment-monthly-${currentYear}-${currentMonth + 1}.json`);
      await fs.writeFile(monthlyFile, JSON.stringify(monthlySummary, null, 2), 'utf8');
      console.log(`Monthly sentiment summary saved to: ${monthlyFile}`);
    }
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    // Parse command line arguments
    const params = parseArgs();
    const { type } = params;

    // Validate type
    if (!VALID_TYPES.includes(type)) {
      console.error(`Invalid type: ${type}. Valid types: ${VALID_TYPES.join(', ')}`);
      process.exit(1);
    }

    await ensureMemoryDir();

    // Scrape newsletter
    const newsletter = await scrapeNewsletter(type);

    // Save summary
    const summaryFile = await saveSummary(newsletter, type);
    console.log(`\nSaved summary to: ${summaryFile}`);

    // Analyze sentiment
    const sentiment = analyzeSentiment(newsletter.full_content || '');

    const sentimentData = {
      date: new Date().toISOString().split('T')[0],
      time: getCurrentTimestamp().split(' ').slice(-2).join(' '),
      trend_direction: 'stable',
      previous_mood: null,
      ...sentiment
    };

    await updateSentimentHistory(sentimentData);

    // Generate daily/weekly/monthly sentiment summaries
    await updateSentimentSummaries();

    const result = {
      summary_file: summaryFile,
      newsletter: newsletter,
      sentiment: sentimentData,
      alert_needed: sentimentData.sales_advice.includes('New sales advice') ||
                     sentimentData.sales_advice.includes('Catch up')
    };

    console.log('\nResult:', JSON.stringify(result, null, 2));
    return result;

  } catch (err) {
    console.error('Fatal error:', err);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main, scrapeNewsletter, analyzeSentiment };
