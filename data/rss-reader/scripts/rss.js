#!/usr/bin/env node
/**
 * RSS Feed Reader CLI
 * Monitor RSS/Atom feeds for content research and trend tracking
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const CONFIG_DIR = path.join(__dirname, '..', 'data');
const FEEDS_FILE = path.join(CONFIG_DIR, 'feeds.json');

// Ensure config directory exists
if (!fs.existsSync(CONFIG_DIR)) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
}

// Default config
const DEFAULT_CONFIG = {
  feeds: [],
  settings: {
    maxItemsPerFeed: 10,
    maxAgeDays: 7,
    summaryEnabled: true
  }
};

// Load config
function loadConfig() {
  try {
    if (fs.existsSync(FEEDS_FILE)) {
      return JSON.parse(fs.readFileSync(FEEDS_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('Error loading config:', e.message);
  }
  return { ...DEFAULT_CONFIG };
}

// Save config
function saveConfig(config) {
  fs.writeFileSync(FEEDS_FILE, JSON.stringify(config, null, 2));
}

// Simple HTTP(S) fetch
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, { 
      headers: { 'User-Agent': 'Clawdbot-RSS/1.0' },
      timeout: 10000
    }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        // Follow redirect
        return fetchUrl(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

// Simple XML parser (no dependencies)
function parseXML(xml) {
  const items = [];
  const feedTitle = xml.match(/<title[^>]*>([^<]+)<\/title>/i)?.[1] || 'Unknown Feed';
  
  // Match RSS items or Atom entries
  const itemRegex = /<(item|entry)[^>]*>([\s\S]*?)<\/\1>/gi;
  let match;
  
  while ((match = itemRegex.exec(xml)) !== null) {
    const itemXml = match[2];
    
    // Extract title
    const title = itemXml.match(/<title[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/i)?.[1]?.trim() || 'Untitled';
    
    // Extract link (RSS vs Atom)
    let link = itemXml.match(/<link[^>]*>([^<]+)<\/link>/i)?.[1];
    if (!link) {
      link = itemXml.match(/<link[^>]*href=["']([^"']+)["'][^>]*\/?>/i)?.[1];
    }
    
    // Extract date
    const pubDate = itemXml.match(/<(pubDate|published|updated|dc:date)[^>]*>([^<]+)<\/\1>/i)?.[2];
    
    // Extract description/summary
    let description = itemXml.match(/<(description|summary|content)[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/\1>/i)?.[2] || '';
    description = description.replace(/<[^>]+>/g, '').trim().slice(0, 500);
    
    items.push({
      title: decodeEntities(title),
      link: link?.trim(),
      date: pubDate ? new Date(pubDate) : new Date(),
      description: decodeEntities(description)
    });
  }
  
  return { title: decodeEntities(feedTitle), items };
}

// Decode HTML entities
function decodeEntities(str) {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
}

// Format relative time
function timeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// Commands
async function addFeed(url, options = {}) {
  const config = loadConfig();
  
  // Check if already exists
  if (config.feeds.find(f => f.url === url)) {
    console.log(`Feed already exists: ${url}`);
    return;
  }
  
  // Try to fetch and parse to validate
  console.log(`Validating feed: ${url}`);
  try {
    const xml = await fetchUrl(url);
    const parsed = parseXML(xml);
    
    const feed = {
      url,
      name: options.name || parsed.title,
      category: options.category || 'general',
      enabled: true,
      lastChecked: null,
      lastItemDate: null
    };
    
    config.feeds.push(feed);
    saveConfig(config);
    console.log(`✓ Added: "${feed.name}" (${parsed.items.length} items) [${feed.category}]`);
  } catch (e) {
    console.error(`✗ Failed to add feed: ${e.message}`);
  }
}

async function removeFeed(url) {
  const config = loadConfig();
  const idx = config.feeds.findIndex(f => f.url === url || f.name.toLowerCase() === url.toLowerCase());
  
  if (idx === -1) {
    console.log(`Feed not found: ${url}`);
    return;
  }
  
  const removed = config.feeds.splice(idx, 1)[0];
  saveConfig(config);
  console.log(`✓ Removed: "${removed.name}"`);
}

function listFeeds() {
  const config = loadConfig();
  
  if (config.feeds.length === 0) {
    console.log('No feeds configured. Add one with: node rss.js add <url>');
    return;
  }
  
  console.log(`\n📰 RSS Feeds (${config.feeds.length}):\n`);
  
  // Group by category
  const byCategory = {};
  for (const feed of config.feeds) {
    const cat = feed.category || 'general';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(feed);
  }
  
  for (const [category, feeds] of Object.entries(byCategory)) {
    console.log(`[${category}]`);
    for (const feed of feeds) {
      const status = feed.enabled ? '✓' : '✗';
      const lastChecked = feed.lastChecked ? timeAgo(new Date(feed.lastChecked)) : 'never';
      console.log(`  ${status} ${feed.name}`);
      console.log(`    ${feed.url}`);
      console.log(`    Last checked: ${lastChecked}`);
    }
    console.log();
  }
}

async function checkFeeds(options = {}) {
  const config = loadConfig();
  const feeds = config.feeds.filter(f => f.enabled);
  
  if (feeds.length === 0) {
    console.log('No feeds to check. Add one with: node rss.js add <url>');
    return;
  }
  
  // Filter by category if specified
  const feedsToCheck = options.category 
    ? feeds.filter(f => f.category === options.category)
    : feeds;
  
  // Calculate since date
  let sinceDate = null;
  if (options.since) {
    const match = options.since.match(/^(\d+)(h|d)$/);
    if (match) {
      const [, num, unit] = match;
      sinceDate = new Date();
      if (unit === 'h') sinceDate.setHours(sinceDate.getHours() - parseInt(num));
      if (unit === 'd') sinceDate.setDate(sinceDate.getDate() - parseInt(num));
    }
  }
  
  const allItems = [];
  
  for (const feed of feedsToCheck) {
    try {
      const xml = await fetchUrl(feed.url);
      const parsed = parseXML(xml);
      
      let items = parsed.items.slice(0, config.settings.maxItemsPerFeed);
      
      // Filter by date if specified
      if (sinceDate) {
        items = items.filter(i => i.date > sinceDate);
      }
      
      // Filter by keywords if specified
      if (options.keywords) {
        const kw = options.keywords.toLowerCase().split(',');
        items = items.filter(i => {
          const text = (i.title + ' ' + i.description).toLowerCase();
          return kw.some(k => text.includes(k.trim()));
        });
      }
      
      for (const item of items) {
        allItems.push({
          ...item,
          feedName: feed.name,
          category: feed.category
        });
      }
      
      // Update last checked
      feed.lastChecked = new Date().toISOString();
      if (parsed.items[0]?.date) {
        feed.lastItemDate = parsed.items[0].date.toISOString();
      }
    } catch (e) {
      console.error(`✗ ${feed.name}: ${e.message}`);
    }
  }
  
  saveConfig(config);
  
  // Sort by date
  allItems.sort((a, b) => b.date - a.date);
  
  // Output based on format
  if (options.format === 'json') {
    console.log(JSON.stringify(allItems, null, 2));
  } else if (options.format === 'ideas') {
    outputIdeas(allItems);
  } else {
    outputList(allItems);
  }
  
  return allItems;
}

function outputList(items) {
  if (items.length === 0) {
    console.log('No new items found.');
    return;
  }
  
  console.log(`\n📰 Found ${items.length} items:\n`);
  
  for (const item of items) {
    console.log(`[${item.category}] ${item.feedName} - "${item.title}" (${timeAgo(item.date)})`);
    if (item.link) console.log(`  ${item.link}`);
  }
}

function outputIdeas(items) {
  if (items.length === 0) {
    console.log('No new items found.');
    return;
  }
  
  console.log(`\n## Content Ideas from RSS\n`);
  
  // Group by category
  const byCategory = {};
  for (const item of items) {
    const cat = item.category || 'general';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(item);
  }
  
  for (const [category, catItems] of Object.entries(byCategory)) {
    console.log(`### ${category.charAt(0).toUpperCase() + category.slice(1)}\n`);
    
    for (const item of catItems.slice(0, 5)) {
      console.log(`- **"${item.title}"** - [${item.feedName}]`);
      if (item.description) {
        console.log(`  ${item.description.slice(0, 200)}...`);
      }
      if (item.link) console.log(`  ${item.link}`);
      console.log();
    }
  }
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

// Parse options
const options = {};
for (let i = 1; i < args.length; i++) {
  if (args[i] === '--category' && args[i + 1]) {
    options.category = args[++i];
  } else if (args[i] === '--name' && args[i + 1]) {
    options.name = args[++i];
  } else if (args[i] === '--since' && args[i + 1]) {
    options.since = args[++i];
  } else if (args[i] === '--format' && args[i + 1]) {
    options.format = args[++i];
  } else if (args[i] === '--keywords' && args[i + 1]) {
    options.keywords = args[++i];
  } else if (!args[i].startsWith('--')) {
    options.url = args[i];
  }
}

switch (command) {
  case 'add':
    if (!options.url) {
      console.log('Usage: node rss.js add <url> [--category <cat>] [--name <name>]');
      process.exit(1);
    }
    addFeed(options.url, options);
    break;
    
  case 'remove':
  case 'rm':
    if (!options.url) {
      console.log('Usage: node rss.js remove <url-or-name>');
      process.exit(1);
    }
    removeFeed(options.url);
    break;
    
  case 'list':
  case 'ls':
    listFeeds();
    break;
    
  case 'check':
    checkFeeds(options);
    break;
    
  default:
    console.log(`
RSS Feed Reader

Commands:
  add <url>      Add a new feed
  remove <url>   Remove a feed
  list           List all feeds
  check          Check feeds for new items

Options:
  --category <cat>   Filter/set category
  --name <name>      Set feed name
  --since <time>     Filter items (e.g., 24h, 7d)
  --format <fmt>     Output format (list, ideas, json)
  --keywords <kw>    Filter by keywords (comma-separated)

Examples:
  node rss.js add "https://news.ycombinator.com/rss" --category tech
  node rss.js check --since 24h --format ideas
  node rss.js check --keywords "AI,agents" --format json
`);
}
