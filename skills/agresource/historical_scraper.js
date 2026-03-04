#!/usr/bin/env node
/**
 * AgResource Historical Newsletter Scraper
 *
 * Scrapes past newsletters by finding date entries and their associated content.
 * Each newsletter is scraped once to avoid duplicates.
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

// Configuration
const AGRESOURCE_URL = 'https://agresource.com/dashboard/#/reports/daily';
const AGRESOURCE_EMAIL = process.env.AGRESOURCE_EMAIL || 'brianppetty@yahoo.com';
const AGRESOURCE_PASSWORD = process.env.AGRESOURCE_PASSWORD || '4BrynnElizabeth';
const MEMORY_DIR = path.join(os.homedir(), 'clawd', 'memory', 'agresource');

/**
 * Get current timestamp in Eastern time
 */
function getCurrentTimestamp() {
  const now = new Date();
  const etOffset = -5;
  const etTime = new Date(now.getTime() + etOffset * 60 * 60 * 1000);
  return etTime.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: 'numeric',
    minute: 'numeric',
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
 * Extract text around a keyword
 */
function extractSection(text, keywords) {
  for (const keyword of keywords) {
    const lowerKeyword = keyword.toLowerCase();
    const idx = text.toLowerCase().indexOf(lowerKeyword);
    if (idx !== -1) {
      const start = Math.max(0, idx - 50);
      const end = Math.min(text.length, idx + 500);
      let section = text.substring(start, end);
      section = section.replace(/\s+/g, ' ');
      return section.trim().substring(0, 300);
    }
  }
  return '';
}

/**
 * Extract news items
 */
function extractNewsItems(text) {
  const items = [];

  const patterns = [
    /[•\-\*]\s+([^.!?]+[.!?])/gi,
    /\d+\.\s+([^.!?]+[.!?])/gi,
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null && items.length < 10) {
      items.push(match[1].trim());
    }
  }

  const grainKeywords = ['corn', 'soy', 'wheat', 'grain', 'market', 'price', 'demand',
                      'export', 'weather', 'yield', 'crop', 'harvest', 'planting'];
  return items
    .filter(item => grainKeywords.some(kw => item.toLowerCase().includes(kw)))
    .map(item => item.substring(0, 200));
}

/**
 * Generate summary
 */
function generateSummary(newsItems, weather) {
  if (!newsItems.length && !weather) {
    return 'No significant updates available.';
  }

  const parts = [];
  if (newsItems.length) {
    parts.push(`Key updates include: ${newsItems[0].substring(0, 100)}...`);
  }
  if (weather) {
    parts.push(`Weather conditions: ${weather.substring(0, 100)}...`);
  }
  return parts.join(' ');
}

/**
 * Parse full newsletter page
 */
function parseFullNewsletterPage(bodyText, bodyHtml, dateStr) {
  const text = bodyText.replace(/\s+/g, ' ').trim();

  // Extract title
  const titleMatch = bodyHtml.match(/AgResource\s+(Morning|Noon|Evening|Saturday|Sunday)\s+Commentary[:\s]*([^.]+)/);
  const title = titleMatch ? titleMatch[1].replace(/\s+/g, ' ').trim() : 'Unknown';

  // Extract published time
  const publishedMatch = text.match(/Published\s+at\s+([^]+)/i);
  const published = publishedMatch ? publishedMatch[1] : '';

  // Extract key sections
  const cornAdvice = extractSection(text, ['corn', 'corn sales', 'corn recommendation', 'wheat producers']);
  const soybeanAdvice = extractSection(text, ['soybean', 'soybeans', 'soy', 'soybean sales']);
  const positions = extractSection(text, ['position', 'current position', 'current positioning']);
  const weather = extractSection(text, ['weather', 'temperature', 'precipitation', 'moisture', 'rain']);

  // Extract news items
  const newsItems = extractNewsItems(text);

  return {
    date: dateStr,
    timestamp: `${new Date().toISOString().split('T')[0]} ${published || getCurrentTimestamp().split(',')[1]}`,
    title: title,
    summary: generateSummary(newsItems, weather),
    corn_advice: cornAdvice,
    soybean_advice: soybeanAdvice,
    positions: positions,
    key_news: newsItems,
    weather_info: weather,
    full_content: text,
    html_content: bodyHtml
  };
}

/**
 * Save newsletter summary
 */
async function saveNewsletter(newsletterData) {
  const dateStr = newsletterData.date?.replace(/\s+/g, '_') || new Date().toISOString().split('T')[0];
  const outputFile = path.join(MEMORY_DIR, `${dateStr}.md`);

  const summaryContent = `# AgResource Newsletter - ${newsletterData.timestamp || dateStr}

## Quick Summary
${newsletterData.summary || 'No summary available'}

## Key Newsworthy Items
${newsletterData.key_news?.length > 0
  ? newsletterData.key_news.map(item => `- ${item}`).join('\n')
  : '- No key news items'}

## Sales Advice Status
- Corn: ${newsletterData.corn_advice || 'No specific advice'}
- Soybeans: ${newsletterData.soybean_advice || 'No specific advice'}

## Current Positions
${newsletterData.positions || 'No positioning info available'}

## Weather
${newsletterData.weather_info || 'No weather info available'}

## Full Content
${newsletterData.full_content?.substring(0, 2000) || 'Full content not available'}
`;

  await fs.writeFile(outputFile, summaryContent, 'utf-8');
  console.log(`  Saved: ${outputFile}`);

  // Also save raw content
  const contentFile = path.join(MEMORY_DIR, `${dateStr}-content.txt`);
  await fs.writeFile(contentFile, newsletterData.full_content || '', 'utf-8');
}

/**
 * Scrape newsletters for a date range
 */
async function scrapeHistorical(targetDateCount = 7) {
  console.log(`AgResource Historical Scraper - ${getCurrentTimestamp()}`);
  console.log(`Target: Last ${targetDateCount} newsletters`);
  console.log('Starting browser...');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Login
    console.log(`Navigating to ${AGRESOURCE_URL}`);
    await page.goto(AGRESOURCE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(5000);

    const hasLoginForm = await page.locator('input[type="email"], #email').count() > 0;
    const hasLoginButton = await page.locator('button[type="submit"], button:has-text("Log in")').count() > 0;

    if (hasLoginForm && hasLoginButton) {
      console.log('Login required...');
      await page.locator('input[type="email"], #email').first().fill(AGRESOURCE_EMAIL);
      await page.waitForTimeout(500);
      await page.locator('input[type="password"], #password').first().fill(AGRESOURCE_PASSWORD);
      await page.waitForTimeout(500);
      await page.locator('button[type="submit"], button:has-text("Log in")').first().click();
      console.log('Login submitted, waiting...');
      await page.waitForTimeout(5000);
    }

    const newsletters = [];
    const scrapedDates = new Set();
    let pageCount = 0;
    const maxPages = 20;

    // Navigate through pages to collect newsletters
    while (newsletters.length < targetDateCount && pageCount < maxPages) {
      console.log(`\n--- Page ${pageCount + 1} ---`);

      // Get ALL entries on page
      const allEntries = await page.locator('.reports > div').all();
      console.log(`Found ${allEntries.length} total entries`);

      // Separate date entries from content entries
      const dateEntries = [];
      const contentEntries = [];

      for (const entry of allEntries) {
        const html = await entry.innerHTML();

        // Date entries have <time> tags
        if (html.includes('<time')) {
          dateEntries.push(entry);
        } else {
          contentEntries.push(entry);
        }
      }

      console.log(`  ${dateEntries.length} date entries, ${contentEntries.length} content entries`);

      // Process each date entry to find its associated content
      for (const dateEntry of dateEntries) {
        if (newsletters.length >= targetDateCount) break;

        // Extract date from date entry
        const dateHtml = await dateEntry.innerHTML();
        const monthMatch = dateHtml.match(/<time[^>]*>(January|February|March|April|May|June|July|August|September|October|November|December)<\/time>/);
        const dayMatch = dateHtml.match(/<time[^>]*>(\d{1,2})<\/time>/);

        if (!monthMatch || !dayMatch) {
          console.log('  ⚠ Could not parse date from entry, skipping');
          continue;
        }

        const month = monthMatch[1];
        const day = dayMatch[1].padStart(2, '0');
        const currentYear = new Date().getFullYear();
        let dateStr = '';
        const entryDate = new Date(`${month} ${day}, ${currentYear}`);

        if (entryDate > new Date()) {
          dateStr = `${month} ${day}, ${currentYear - 1}`;
        } else {
          dateStr = `${month} ${day}, ${currentYear}`;
        }

        // Skip if already scraped
        if (scrapedDates.has(dateStr)) {
          console.log(`  ✗ Duplicate: ${dateStr}, skipping`);
          continue;
        }

        // Find content entry immediately following this date
        const dateEntryIndex = allEntries.indexOf(dateEntry);
        let contentEntry = null;

        for (let i = dateEntryIndex + 1; i < allEntries.length; i++) {
          const potentialContent = allEntries[i];
          const potentialHtml = await potentialContent.innerHTML();

          // Skip date entries
          if (potentialHtml.includes('<time>')) continue;

          contentEntry = potentialContent;
          break;
        }

        if (!contentEntry) {
          console.log(`  ⚠ No content found for ${dateStr}, skipping`);
          continue;
        }

        // Click on content entry to navigate to full newsletter
        console.log(`  Scraping: ${dateStr}`);
        await contentEntry.click();
        await page.waitForTimeout(3000);

        // Scrape full newsletter
        const bodyText = await page.textContent('body');
        const bodyHtml = await page.content();

        const newsletter = parseFullNewsletterPage(bodyText, bodyHtml, dateStr);

        if (newsletter.date) {
          newsletters.push(newsletter);
          scrapedDates.add(newsletter.date);
          console.log(`  ✓ ${newsletter.date}: ${newsletter.title.substring(0, 50)}...`);
        }

        // Navigate back to list
        await page.goto(AGRESOURCE_URL, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(2000);
      }

      // Check if there are more pages
      const hasPrev = await page.locator('button:has-text("Previous"), button:has-text("<"), .previous').count() > 0;
      if (!hasPrev || newsletters.length >= targetDateCount) {
        console.log('No more pages or target reached');
        break;
      }

      // Click Previous to go to next page
      console.log('Going to previous page...');
      await page.locator('button:has-text("Previous"), button:has-text("<"), .previous').first().click();
      await page.waitForTimeout(3000);
      pageCount++;
    }

    console.log(`\n✓ Scraped ${newsletters.length} newsletters`);

    // Save each newsletter
    for (const newsletter of newsletters) {
      await saveNewsletter(newsletter);
    }

    await browser.close();
    return { success: true, count: newsletters.length, newsletters };

  } catch (err) {
    console.error(`Error during scraping: ${err}`);
    await browser.close();
    return { success: false, error: err.message };
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    await ensureMemoryDir();

    const args = process.argv.slice(2);
    const targetCount = args[0] ? parseInt(args[0]) : 7;

    console.log(`Usage: node historical_scraper.js [days]`);
    console.log(`Default: 7 days, last 7 newsletters\n`);

    const result = await scrapeHistorical(targetCount);

    if (result.success) {
      console.log(`\n✓ Successfully scraped ${result.count} newsletters`);
      process.exit(0);
    } else {
      console.error(`\n✗ Scraping failed: ${result.error}`);
      process.exit(1);
    }

  } catch (err) {
    console.error('Fatal error:', err);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { scrapeHistorical };
