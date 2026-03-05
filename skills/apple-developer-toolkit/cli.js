#!/usr/bin/env node

/**
 * Apple Docs CLI - Query Apple Developer Documentation and WWDC Videos
 *
 * Direct integration with Apple's developer documentation APIs.
 * WWDC data indexed locally from developer.apple.com (see build-wwdc-index.js).
 * No external dependencies or third-party packages.
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WWDC_DATA_DIR = join(__dirname, 'data', 'wwdc');

// ============ APPLE API CONSTANTS ============

const APPLE_URLS = {
  BASE: 'https://developer.apple.com',
  SEARCH: 'https://developer.apple.com/search/',
  DOCUMENTATION: 'https://developer.apple.com/documentation/',
  TUTORIALS_DATA: 'https://developer.apple.com/tutorials/data/',
  TECHNOLOGIES_JSON: 'https://developer.apple.com/tutorials/data/documentation/technologies.json',
  UPDATES_JSON: 'https://developer.apple.com/tutorials/data/documentation/Updates.json',
  TECHNOLOGY_OVERVIEWS_JSON: 'https://developer.apple.com/tutorials/data/documentation/TechnologyOverviews.json',
  SAMPLE_CODE_JSON: 'https://developer.apple.com/tutorials/data/documentation/SampleCode.json',
};

// ============ HTTP CLIENT ============

async function httpFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
      'Accept': 'text/html,application/json,application/xhtml+xml',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response;
}

async function fetchJson(url) {
  const response = await httpFetch(url);
  return response.json();
}

async function fetchText(url) {
  const response = await httpFetch(url);
  return response.text();
}

// ============ LOCAL WWDC DATA ============

function loadJsonFile(path) {
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function loadWwdcIndex() {
  return loadJsonFile(join(WWDC_DATA_DIR, 'index.json'));
}

function loadAllVideos() {
  return loadJsonFile(join(WWDC_DATA_DIR, 'all-videos.json'));
}

function loadWwdcTopics() {
  return loadJsonFile(join(WWDC_DATA_DIR, 'topics.json'));
}

function loadYearVideos(year) {
  return loadJsonFile(join(WWDC_DATA_DIR, 'by-year', `${year}.json`));
}

function loadTopicVideos(slug) {
  return loadJsonFile(join(WWDC_DATA_DIR, 'by-topic', `${slug}.json`));
}

// ============ SEARCH ============

async function searchAppleDocs(query, limit = 10) {
  const url = `${APPLE_URLS.SEARCH}?q=${encodeURIComponent(query)}`;
  const html = await fetchText(url);
  return parseSearchResults(html, limit);
}

function parseSearchResults(html, limit) {
  const results = [];
  const seen = new Set();

  const docRegex = /<a[^>]+href="(\/documentation\/[^"]+)"[^>]*>([^<]+)<\/a>/gi;
  let match;
  while ((match = docRegex.exec(html)) !== null && results.length < limit) {
    const url = match[1];
    const title = match[2].trim().replace(/<[^>]*>/g, '');
    if (seen.has(url)) continue;
    seen.add(url);
    if (url.includes('/design/human-interface-guidelines/')) continue;
    if (url.includes('/download/')) continue;

    const frameworkMatch = url.match(/\/documentation\/([^/]+)\//);
    results.push({
      title: title || url.split('/').pop(),
      url: `https://developer.apple.com${url}`,
      framework: frameworkMatch ? frameworkMatch[1] : null,
      type: 'documentation'
    });
  }

  return results;
}

// ============ SYMBOL SEARCH ============

async function searchFrameworkSymbols(query, limit = 20) {
  return await searchAppleDocs(query, limit);
}

// ============ FETCH DOC CONTENT ============

async function getAppleDocContent(url) {
  let jsonUrl = url;
  if (!url.includes('.json')) {
    const path = url.replace('https://developer.apple.com', '');
    jsonUrl = `https://developer.apple.com/tutorials/data${path}.json`;
  }

  try {
    const data = await fetchJson(jsonUrl);
    return formatDocContent(data);
  } catch {
    const html = await fetchText(url);
    return extractDocFromHtml(html, url);
  }
}

function formatDocContent(data) {
  let output = [];
  output.push(`# ${data.title || 'Documentation'}`);
  if (data.framework) output.push(`\nFramework: ${data.framework}`);
  if (data.platforms) output.push(`\nPlatforms: ${data.platforms.join(', ')}`);
  output.push('\n');

  if (data.description) output.push(`${data.description}\n`);
  if (data.content) output.push(`\n${extractTextFromContent(data.content)}`);

  if (data.topics?.length) {
    output.push('\n\nTopics:\n');
    data.topics.forEach(t => output.push(`  - ${t}`));
  }

  if (data.relationships?.length) {
    output.push('\n\nRelationships:\n');
    data.relationships.forEach(r => {
      output.push(`  - ${r.type}: ${r.name || r.url}`);
    });
  }

  return output.join('\n');
}

function extractDocFromHtml(html, url) {
  const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
  const title = titleMatch ? titleMatch[1] : 'Apple Documentation';

  const descMatch = html.match(/<meta[^>]+name="description"[^>]+content="([^"]+)"/i) ||
                   html.match(/<p[^>]+class="description"[^>]*>([^<]+)/i);
  const description = descMatch ? descMatch[1] : '';

  return `# ${title}\n\nURL: ${url}\n\n${description}`;
}

function extractTextFromContent(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) return content.map(c => extractTextFromContent(c)).join('\n');
  if (content.text) return content.text;
  return JSON.stringify(content);
}

// ============ LIST TECHNOLOGIES ============

async function listTechnologies() {
  return await fetchJson(APPLE_URLS.TECHNOLOGIES_JSON);
}

// ============ RELATED APIS ============

async function getRelatedApis(symbolName) {
  return await searchAppleDocs(symbolName, 5);
}

// ============ PLATFORM COMPATIBILITY ============

async function getPlatformCompatibility(symbolName) {
  return await searchAppleDocs(`${symbolName} platform compatibility`, 5);
}

// ============ SIMILAR APIS ============

async function findSimilarApis(symbolName) {
  return await searchAppleDocs(`${symbolName} alternative replacement`, 5);
}

// ============ DOCUMENTATION UPDATES ============

async function getDocumentationUpdates(limit = 10) {
  try {
    const data = await fetchJson(APPLE_URLS.UPDATES_JSON);
    return (data.updates || data.slice(0, limit));
  } catch {
    return [{ error: 'Could not fetch updates' }];
  }
}

// ============ TECHNOLOGY OVERVIEWS ============

async function getTechnologyOverviews(technology) {
  try {
    const data = await fetchJson(APPLE_URLS.TECHNOLOGY_OVERVIEWS_JSON);
    return data.filter(t =>
      t.name?.toLowerCase().includes(technology.toLowerCase()) ||
      t.title?.toLowerCase().includes(technology.toLowerCase())
    );
  } catch {
    return [{ error: 'Could not fetch technology overviews' }];
  }
}

// ============ SAMPLE CODE ============

async function getSampleCode(technology, limit = 10) {
  try {
    const data = await fetchJson(APPLE_URLS.SAMPLE_CODE_JSON);
    return (data.sampleCode || data)
      .filter(s => s.title?.toLowerCase().includes(technology.toLowerCase()))
      .slice(0, limit);
  } catch {
    return [{ error: 'Could not fetch sample code' }];
  }
}

// ============ WWDC - LOCAL INDEX ============

function searchWwdcVideos(query, year = null, topic = null, limit = 10) {
  const data = loadAllVideos();
  if (!data) {
    console.error('WWDC index not found. Run: node build-wwdc-index.js');
    return [];
  }

  let videos = data.videos || [];

  // Filter by year
  if (year) {
    videos = videos.filter(v => v.year === parseInt(year));
  }

  // Filter by topic
  if (topic) {
    const t = topic.toLowerCase();
    videos = videos.filter(v =>
      v.topics?.some(tp => tp.toLowerCase().includes(t))
    );
  }

  // Search by query
  if (query) {
    const q = query.toLowerCase();
    const terms = q.split(/\s+/);

    // Score-based search for better results
    videos = videos
      .map(v => {
        let score = 0;
        const title = (v.title || '').toLowerCase();
        const desc = (v.description || '').toLowerCase();
        const topics = (v.topics || []).join(' ').toLowerCase();

        for (const term of terms) {
          if (title.includes(term)) score += 10;
          if (topics.includes(term)) score += 5;
          if (desc.includes(term)) score += 3;
        }

        // Exact phrase match bonus
        if (title.includes(q)) score += 20;

        return { ...v, _score: score };
      })
      .filter(v => v._score > 0)
      .sort((a, b) => b._score - a._score);
  }

  return videos.slice(0, limit).map(v => ({
    id: v.id,
    year: v.year,
    title: v.title,
    duration: v.duration,
    topics: v.topics,
    url: v.url,
    ...(v.description ? { description: v.description } : {}),
  }));
}

async function getWwdcVideoDetails(videoId, includeTranscript = true) {
  // Parse video ID (format: "2024-100" or "2024 100")
  const match = videoId.match(/(\d{4})[-_\s]?(\d+)/);
  if (!match) {
    return { error: 'Invalid video ID format. Use format: YYYY-NNN (e.g., 2024-100)' };
  }

  const year = match[1];
  const id = match[2];

  // First, get data from local index
  const data = loadAllVideos();
  const localVideo = data?.videos?.find(v => v.id === id && v.year === parseInt(year));

  // Then fetch the Apple video page for additional details
  const url = `https://developer.apple.com/videos/play/wwdc${year}/${id}/`;
  let output = [];

  try {
    const html = await fetchText(url);

    // Extract title
    const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i) ||
                      html.match(/<title>([^<|]+)/i);
    const title = titleMatch ? titleMatch[1].trim() : (localVideo?.title || `WWDC${year} Session ${id}`);

    output.push(`# ${title}`);
    output.push(`\nYear: ${year} | Session: ${id}`);
    if (localVideo?.duration) output.push(`Duration: ${localVideo.duration}`);
    if (localVideo?.topics?.length) output.push(`Topics: ${localVideo.topics.join(', ')}`);
    output.push(`URL: ${url}`);

    // Extract description
    const descMatch = html.match(/<meta[^>]+name="description"[^>]+content="([^"]+)"/i);
    if (descMatch) {
      output.push(`\n## Description\n${descMatch[1]}`);
    }

    // Extract related videos
    const relatedLinks = [];
    const relatedRegex = /href="(\/videos\/play\/wwdc(\d{4})\/(\d+)\/?)"[^>]*>/gi;
    const seen = new Set([`${year}-${id}`]);
    let m;
    while ((m = relatedRegex.exec(html)) !== null) {
      const key = `${m[2]}-${m[3]}`;
      if (!seen.has(key)) {
        seen.add(key);
        // Look up title from local index
        const relatedVideo = data?.videos?.find(v => v.id === m[3] && v.year === parseInt(m[2]));
        relatedLinks.push({
          title: relatedVideo?.title || `Session ${m[3]}`,
          year: m[2],
          id: m[3],
          url: `https://developer.apple.com${m[1]}`,
        });
      }
    }

    if (relatedLinks.length > 0) {
      output.push(`\n## Related Sessions`);
      relatedLinks.forEach(r => output.push(`  - ${r.title} (WWDC${r.year} ${r.id})`));
    }

    // Look for transcript
    if (includeTranscript) {
      const transcriptMatch = html.match(/<section[^>]+class="[^"]*transcript[^"]*"[^>]*>([\s\S]*?)<\/section>/i);
      if (transcriptMatch) {
        const transcript = transcriptMatch[1]
          .replace(/<[^>]*>/g, ' ')
          .replace(/\s+/g, ' ')
          .trim();
        if (transcript) {
          output.push(`\n## Transcript\n${transcript.substring(0, 3000)}...`);
          output.push(`\n[Full transcript at: ${url}]`);
        }
      }
    }

    // Extract download links
    const downloadLinks = [];
    const dlRegex = /href="([^"]+\.(mp4|pdf|zip|key))[^"]*"/gi;
    let dlMatch;
    while ((dlMatch = dlRegex.exec(html)) !== null) {
      downloadLinks.push(dlMatch[1]);
    }
    if (downloadLinks.length > 0) {
      output.push(`\n## Downloads`);
      downloadLinks.forEach(d => output.push(`  - ${d}`));
    }

  } catch (err) {
    // Fallback to local data only
    if (localVideo) {
      output.push(`# ${localVideo.title}`);
      output.push(`\nYear: ${year} | Session: ${id}`);
      if (localVideo.duration) output.push(`Duration: ${localVideo.duration}`);
      if (localVideo.topics?.length) output.push(`Topics: ${localVideo.topics.join(', ')}`);
      output.push(`URL: ${url}`);
      if (localVideo.description) output.push(`\n## Description\n${localVideo.description}`);
      output.push(`\n(Could not fetch live page: ${err.message})`);
    } else {
      return { error: `Video ${year}-${id} not found` };
    }
  }

  return output.join('\n');
}

function listWwdcTopics() {
  const topics = loadWwdcTopics();
  if (!topics) return [];

  // Enrich with counts from index
  const index = loadWwdcIndex();
  if (index?.topics) {
    return index.topics;
  }

  return topics;
}

function listWwdcYears() {
  const index = loadWwdcIndex();
  if (index) {
    return {
      totalVideos: index.totalVideos,
      years: index.years,
    };
  }

  // Fallback
  return {
    totalVideos: 0,
    years: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025].map(y => ({ year: y, count: 0 })),
  };
}

function getWwdcByTopic(topicSlug, limit = 20) {
  const data = loadTopicVideos(topicSlug);
  if (!data) return [];

  return (data.videos || []).slice(0, limit);
}

function getWwdcByYear(year) {
  const data = loadYearVideos(year);
  if (!data) return [];

  return data.videos || [];
}

// ============ OUTPUT FORMATTING ============

const colors = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m',
  red: '\x1b[31m', cyan: '\x1b[36m', magenta: '\x1b[35m', white: '\x1b[37m'
};

function log(text = '', color = 'reset') {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

function logError(text) {
  console.error(`${colors.red}Error: ${text}${colors.reset}`);
}

function outputJson(data) {
  console.log(JSON.stringify(data, null, 2));
}

function outputResults(results, title) {
  if (!results || results.length === 0) {
    log('\nNo results found.', 'yellow');
    return;
  }

  log(`\n${title}`, 'bright');
  log('='.repeat(50), 'dim');

  results.forEach((r, i) => {
    if (r.title || r.name) {
      log(`\n${i + 1}. ${r.title || r.name}`, 'cyan');
      if (r.framework) log(`   Framework: ${r.framework}`, 'dim');
      if (r.year) log(`   Year: ${r.year}`, 'dim');
      if (r.duration) log(`   Duration: ${r.duration}`, 'dim');
      if (r.topics) log(`   Topics: ${(Array.isArray(r.topics) ? r.topics.join(', ') : r.topics)}`, 'dim');
      if (r.count !== undefined) log(`   Videos: ${r.count}`, 'dim');
      if (r.slug) log(`   Slug: ${r.slug}`, 'dim');
      if (r.url) log(`   URL: ${r.url}`, 'dim');
    } else {
      log(`\n${JSON.stringify(r)}`);
    }
  });
}

// ============ COMMANDS ============

async function cmdSearch(query, options = {}) {
  if (!query) {
    logError('Search query required');
    log('Usage: apple-docs search "SwiftUI animation"');
    process.exit(1);
  }

  log(`\nSearching Apple docs for: "${query}"`, 'bright');
  const results = await searchAppleDocs(query, options.limit || 10);
  outputResults(results, 'Search Results');
}

async function cmdSymbols(query, options = {}) {
  if (!query) {
    logError('Symbol query required');
    log('Usage: apple-docs symbols "UITableView"');
    process.exit(1);
  }

  log(`\nSearching for symbols: "${query}"`, 'bright');
  const results = await searchFrameworkSymbols(query, options.limit || 20);
  outputResults(results, 'Symbol Results');
}

async function cmdDoc(path) {
  if (!path) {
    logError('Documentation path required');
    log('Usage: apple-docs doc "/documentation/swiftui/view"');
    process.exit(1);
  }

  // Validate: only allow Apple developer documentation URLs (SSRF protection)
  let url;
  if (path.startsWith('http')) {
    const parsed = new URL(path);
    const allowedHosts = ['developer.apple.com', 'sosumi.ai'];
    if (!allowedHosts.includes(parsed.hostname)) {
      logError(`Only Apple documentation URLs are allowed (developer.apple.com, sosumi.ai). Got: ${parsed.hostname}`);
      process.exit(1);
    }
    url = path;
  } else {
    // Path-only input: must start with / and contain no protocol markers
    if (path.includes('://') || path.includes('..')) {
      logError('Invalid documentation path. Use a path like "/documentation/swiftui/view"');
      process.exit(1);
    }
    url = `https://developer.apple.com${path}`;
  }

  log(`\nFetching documentation: ${url}`, 'bright');
  const content = await getAppleDocContent(url);
  log(`\n${content}`);
}

async function cmdTech() {
  log('\nListing Apple technologies...', 'bright');
  const data = await listTechnologies();
  outputJson(data);
}

async function cmdApis(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs apis "UIViewController"');
    process.exit(1);
  }

  log(`\nFinding related APIs for: "${symbol}"`, 'bright');
  const results = await getRelatedApis(symbol);
  outputResults(results, 'Related APIs');
}

async function cmdPlatform(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs platform "UIScrollView"');
    process.exit(1);
  }

  log(`\nChecking platform compatibility for: "${symbol}"`, 'bright');
  const results = await getPlatformCompatibility(symbol);
  outputResults(results, 'Platform Compatibility');
}

async function cmdSimilar(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs similar "UIPickerView"');
    process.exit(1);
  }

  log(`\nFinding similar/alternative APIs for: "${symbol}"`, 'bright');
  const results = await findSimilarApis(symbol);
  outputResults(results, 'Similar APIs');
}

async function cmdUpdates(options = {}) {
  log('\nFetching documentation updates...', 'bright');
  const updates = await getDocumentationUpdates(options.limit || 10);
  outputJson(updates);
}

async function cmdOverview(technology) {
  if (!technology) {
    logError('Technology name required');
    log('Usage: apple-docs overview "SwiftUI"');
    process.exit(1);
  }

  log(`\nFetching technology overview: ${technology}`, 'bright');
  const overviews = await getTechnologyOverviews(technology);
  outputJson(overviews);
}

async function cmdSamples(technology, options = {}) {
  if (!technology) {
    logError('Technology name required');
    log('Usage: apple-docs samples "SwiftUI"');
    process.exit(1);
  }

  log(`\nSearching sample code for: ${technology}`, 'bright');
  const samples = await getSampleCode(technology, options.limit || 10);
  outputJson(samples);
}

async function cmdWwdcSearch(query, options = {}) {
  if (!query) {
    logError('WWDC search query required');
    log('Usage: apple-docs wwdc-search "async await"');
    process.exit(1);
  }

  log(`\nSearching WWDC videos for: "${query}"`, 'bright');
  const results = searchWwdcVideos(query, options.year, options.topic, options.limit || 10);
  outputResults(results, 'WWDC Videos');
}

async function cmdWwdcVideo(id, options = {}) {
  if (!id) {
    logError('WWDC video ID required');
    log('Usage: apple-docs wwdc-video 2024-100');
    process.exit(1);
  }

  log(`\nFetching WWDC video details: ${id}`, 'bright');
  const details = await getWwdcVideoDetails(id, options.transcript !== false);
  if (typeof details === 'string') {
    log(`\n${details}`);
  } else {
    outputJson(details);
  }
}

async function cmdWwdcTopics() {
  log('\nWWDC Topic Categories:', 'bright');
  const topics = listWwdcTopics();
  outputResults(topics, 'WWDC Topics');
}

async function cmdWwdcYears() {
  const data = listWwdcYears();

  log(`\nWWDC Years (${data.totalVideos} total videos):`, 'bright');
  log('='.repeat(40), 'dim');

  data.years.forEach(y => {
    const year = y.year || y;
    const count = y.count !== undefined ? ` (${y.count} videos)` : '';
    log(`  ${year}${count}`, 'cyan');
  });
}

async function cmdWwdcTopic(topicSlug, options = {}) {
  if (!topicSlug) {
    logError('Topic slug required');
    log('Usage: apple-docs wwdc-topic "swift"');
    log('Run: apple-docs wwdc-topics  to see available topics');
    process.exit(1);
  }

  log(`\nWWDC videos for topic: "${topicSlug}"`, 'bright');
  const results = getWwdcByTopic(topicSlug, options.limit || 20);
  outputResults(results, `Topic: ${topicSlug}`);
}

async function cmdWwdcYear(year) {
  if (!year) {
    logError('Year required');
    log('Usage: apple-docs wwdc-year 2024');
    process.exit(1);
  }

  log(`\nWWDC${year} Videos:`, 'bright');
  const results = getWwdcByYear(parseInt(year));
  outputResults(results, `WWDC${year}`);
}

// ============ HELP ============

function showHelp() {
  log(`
${colors.bright}Apple Docs CLI${colors.reset} - Query Apple Developer Documentation and WWDC Videos
${colors.dim}Direct integration with developer.apple.com | 1,260+ WWDC sessions indexed${colors.reset}

${colors.bright}SETUP:${colors.reset}
  No setup required - works out of the box.
  To rebuild WWDC index: node build-wwdc-index.js

${colors.bright}SEARCH COMMANDS:${colors.reset}
  apple-docs search "query"              Search Apple Developer Documentation
  apple-docs symbols "UIView"            Search framework classes, structs, protocols
  apple-docs doc "/path/to/doc"          Get detailed documentation by path

${colors.bright}API EXPLORATION:${colors.reset}
  apple-docs apis "UIViewController"     Find related APIs
  apple-docs platform "UIScrollView"     Check platform compatibility
  apple-docs similar "UIPickerView"      Find similar/recommended alternatives

${colors.bright}TECHNOLOGY BROWSING:${colors.reset}
  apple-docs tech                        List all Apple technologies
  apple-docs overview "SwiftUI"          Get technology overview guide
  apple-docs samples "SwiftUI"           Find sample code projects
  apple-docs updates                     Latest documentation updates

${colors.bright}WWDC VIDEOS:${colors.reset}
  apple-docs wwdc-search "async"         Search WWDC sessions (2014-2025)
  apple-docs wwdc-video 2024-100         Get video details and transcript
  apple-docs wwdc-topics                 List WWDC topic categories
  apple-docs wwdc-topic "swift"          List videos by topic slug
  apple-docs wwdc-years                  List available WWDC years with counts
  apple-docs wwdc-year 2024              List all videos for a specific year

${colors.bright}OPTIONS:${colors.reset}
  --limit <n>       Limit results (default varies)
  --category        Filter by technology category
  --framework       Filter by framework name
  --year            Filter WWDC by year
  --topic           Filter WWDC by topic
  --no-transcript   Skip transcript for WWDC videos

${colors.bright}EXAMPLES:${colors.reset}
  ${colors.dim}# Search for SwiftUI animations${colors.reset}
  apple-docs search "SwiftUI animation"

  ${colors.dim}# Find UITableView delegate methods${colors.reset}
  apple-docs symbols "UITableViewDelegate"

  ${colors.dim}# Search WWDC for Swift concurrency${colors.reset}
  apple-docs wwdc-search "swift concurrency"

  ${colors.dim}# Get specific WWDC video${colors.reset}
  apple-docs wwdc-video 2024-10169

  ${colors.dim}# List all 2025 sessions${colors.reset}
  apple-docs wwdc-year 2025

  ${colors.dim}# Browse SwiftUI topic${colors.reset}
  apple-docs wwdc-topic "swiftui-ui-frameworks"
  `);
}

// ============ MAIN ============

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === 'help' || command === '-h') {
    showHelp();
    return;
  }

  // Parse options
  const options = {};
  let query = null;
  let i = 1;

  while (i < args.length) {
    const arg = args[i];

    if (arg.startsWith('--')) {
      const key = arg.substring(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const valueOptions = ['limit', 'category', 'framework', 'year', 'topic'];
      if (valueOptions.includes(key)) {
        options[key] = args[i + 1];
        i += 2;
      } else if (key === 'noTranscript') {
        options.transcript = false;
        i++;
      } else {
        options[key] = true;
        i++;
      }
    } else if (!arg.startsWith('-') && !['search', 'symbols', 'wwdc-search'].includes(command)) {
      if (command === 'doc') {
        options.path = arg;
      } else if (['apis', 'platform', 'similar'].includes(command)) {
        options.symbol = arg;
      } else if (['tech', 'overview'].includes(command)) {
        options.technology = arg;
      } else if (command === 'samples') {
        options.technology = arg;
      } else if (command === 'wwdc-video') {
        options.id = arg;
      } else if (command === 'wwdc-topic') {
        options.topicSlug = arg;
      } else if (command === 'wwdc-year') {
        options.yearArg = arg;
      }
      i++;
    } else {
      i++;
    }
  }

  // Handle positional query for search commands
  if (['search', 'symbols', 'wwdc-search'].includes(command)) {
    query = args.slice(1).find(a => !a.startsWith('-')) || '';
  }

  try {
    switch (command) {
      case 'search': await cmdSearch(query, options); break;
      case 'doc': await cmdDoc(options.path, options); break;
      case 'tech': await cmdTech(options); break;
      case 'symbols': await cmdSymbols(query, options); break;
      case 'apis': await cmdApis(options.symbol, options); break;
      case 'platform': await cmdPlatform(options.symbol, options); break;
      case 'similar': await cmdSimilar(options.symbol, options); break;
      case 'updates': await cmdUpdates(options); break;
      case 'overview': await cmdOverview(options.technology, options); break;
      case 'samples': await cmdSamples(options.technology, options); break;
      case 'wwdc-search': await cmdWwdcSearch(query, options); break;
      case 'wwdc-video': await cmdWwdcVideo(options.id, options); break;
      case 'wwdc-topics': await cmdWwdcTopics(); break;
      case 'wwdc-topic': await cmdWwdcTopic(options.topicSlug, options); break;
      case 'wwdc-years': await cmdWwdcYears(); break;
      case 'wwdc-year': await cmdWwdcYear(options.yearArg); break;
      default:
        logError(`Unknown command: ${command}`);
        log('Run: apple-docs --help');
        process.exit(1);
    }
  } catch (err) {
    logError(err.message);
    process.exit(1);
  }
}

main().catch(err => {
  logError(err.message);
  process.exit(1);
});
