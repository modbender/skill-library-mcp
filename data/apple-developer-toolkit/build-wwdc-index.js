#!/usr/bin/env node

/**
 * WWDC Index Builder
 * Scrapes Apple's developer.apple.com/videos/ pages
 * and builds a local JSON index of all WWDC sessions.
 *
 * Run: node build-wwdc-index.js
 * Output: data/wwdc/ directory with JSON files
 */

import { mkdirSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data', 'wwdc');

const YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];

const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
};

const TOPICS = [
  { name: 'Accessibility', slug: 'accessibility' },
  { name: 'App Store & Distribution', slug: 'app-store-distribution' },
  { name: 'Audio & Video', slug: 'audio-video' },
  { name: 'Augmented Reality', slug: 'augmented-reality' },
  { name: 'Design', slug: 'design' },
  { name: 'Developer Tools', slug: 'developer-tools' },
  { name: 'Extensions', slug: 'extensions' },
  { name: 'Graphics & Games', slug: 'graphics-games' },
  { name: 'Health & Fitness', slug: 'health-fitness' },
  { name: 'Machine Learning & AI', slug: 'machine-learning-ai' },
  { name: 'Maps & Location', slug: 'maps-location' },
  { name: 'Networking', slug: 'networking' },
  { name: 'Privacy & Security', slug: 'privacy-security' },
  { name: 'Safari & Web', slug: 'safari-web' },
  { name: 'Swift', slug: 'swift' },
  { name: 'SwiftUI & UI Frameworks', slug: 'swiftui-ui-frameworks' },
  { name: 'System Services', slug: 'system-services' },
  { name: 'Testing', slug: 'testing' },
  { name: 'visionOS', slug: 'visionos' },
  { name: 'Widgets & App Intents', slug: 'widgets-app-intents' },
];

// Map Apple's data-category values to our topic names
const CATEGORY_MAP = {
  'accessibility': 'Accessibility',
  'accessibility-&-inclusion': 'Accessibility',
  'app-store-distribution': 'App Store & Distribution',
  'app-store-&-distribution': 'App Store & Distribution',
  'audio-&-video': 'Audio & Video',
  'audio-video': 'Audio & Video',
  'media': 'Audio & Video',
  'augmented-reality': 'Augmented Reality',
  'ar-vr': 'Augmented Reality',
  'design': 'Design',
  'developer-tools': 'Developer Tools',
  'tools': 'Developer Tools',
  'extensions': 'Extensions',
  'graphics-&-games': 'Graphics & Games',
  'graphics-games': 'Graphics & Games',
  'games': 'Graphics & Games',
  'health-&-fitness': 'Health & Fitness',
  'health-fitness': 'Health & Fitness',
  'machine-learning-&-ai': 'Machine Learning & AI',
  'machine-learning': 'Machine Learning & AI',
  'ml-ai': 'Machine Learning & AI',
  'maps-&-location': 'Maps & Location',
  'maps-location': 'Maps & Location',
  'networking': 'Networking',
  'privacy-&-security': 'Privacy & Security',
  'privacy-security': 'Privacy & Security',
  'security': 'Privacy & Security',
  'safari-&-web': 'Safari & Web',
  'safari-web': 'Safari & Web',
  'web': 'Safari & Web',
  'swift': 'Swift',
  'swiftui': 'SwiftUI & UI Frameworks',
  'swiftui-&-ui-frameworks': 'SwiftUI & UI Frameworks',
  'ui-frameworks': 'SwiftUI & UI Frameworks',
  'system-services': 'System Services',
  'system': 'System Services',
  'testing': 'Testing',
  'visionos': 'visionOS',
  'spatial-computing': 'visionOS',
  'widgets-&-app-intents': 'Widgets & App Intents',
  'widgets': 'Widgets & App Intents',
  'app-intents': 'Widgets & App Intents',
  'siri-&-voice': 'Widgets & App Intents',
  'business-&-enterprise': 'System Services',
  'distribution-&-monetization': 'App Store & Distribution',
  'general': 'General',
  'featured': 'General',
};

function parseDuration(raw) {
  if (!raw) return null;
  const match = raw.match(/(\d+):(\d+)/);
  if (!match) return null;
  return parseInt(match[1]) * 60 + parseInt(match[2]);
}

function mapCategory(category) {
  if (!category) return ['General'];
  // Handle multiple categories separated by commas or spaces
  const cats = category.split(/[,&]/).map(c => c.trim().toLowerCase());
  const mapped = new Set();

  for (const cat of cats) {
    const normalized = cat.replace(/\s+/g, '-');
    if (CATEGORY_MAP[normalized]) {
      mapped.add(CATEGORY_MAP[normalized]);
    } else {
      // Try partial match
      for (const [key, value] of Object.entries(CATEGORY_MAP)) {
        if (normalized.includes(key) || key.includes(normalized)) {
          mapped.add(value);
          break;
        }
      }
    }
  }

  return mapped.size > 0 ? [...mapped] : ['General'];
}

async function fetchYearVideos(year) {
  const url = `https://developer.apple.com/videos/wwdc${year}/`;
  console.log(`  Fetching WWDC${year}...`);

  const resp = await fetch(url, { headers: HEADERS });
  if (!resp.ok) {
    console.log(`  Warning: HTTP ${resp.status} for WWDC${year}`);
    return [];
  }

  const html = await resp.text();
  const videos = [];
  const seen = new Set();

  // Apple's HTML structure (2024-2025):
  // <a href="/videos/play/wwdc{YEAR}/{ID}/" class="vc-card ..." data-category="...">
  //   <img ... alt="TITLE" ...>
  //   <span class="vc-card__duration">MM:SS</span>
  //   <h5 class="vc-card__title">TITLE</h5>
  // </a>

  // Extract each video card as a block
  const cardRegex = /<a[^>]+href="\/videos\/play\/wwdc(\d{4})\/(\d+)\/?\"[^>]*>([\s\S]*?)<\/a>/gi;
  let cardMatch;

  while ((cardMatch = cardRegex.exec(html)) !== null) {
    const videoYear = parseInt(cardMatch[1]);
    const id = cardMatch[2];
    const cardHtml = cardMatch[0] + cardMatch[3]; // include full tag

    if (seen.has(id)) continue;
    seen.add(id);

    // Extract title from h5.vc-card__title, h4, or img alt
    let title = null;
    const h5Match = cardHtml.match(/<h[345][^>]*class="[^"]*vc-card__title[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/h[345]>/i);
    if (h5Match) {
      title = h5Match[1].replace(/<[^>]*>/g, '').trim();
    }
    if (!title) {
      const altMatch = cardHtml.match(/alt="([^"]+)"/i);
      if (altMatch) title = altMatch[1].trim();
    }
    if (!title) {
      // Fallback: any heading inside the card
      const hMatch = cardHtml.match(/<h[1-6][^>]*>([\s\S]*?)<\/h[1-6]>/i);
      if (hMatch) title = hMatch[1].replace(/<[^>]*>/g, '').trim();
    }
    if (!title) title = `Session ${id}`;

    // Extract duration
    const durMatch = cardHtml.match(/vc-card__duration[^>]*>\s*(\d+:\d+)/i) ||
                    cardHtml.match(/(\d+:\d+)/);
    const duration = durMatch ? durMatch[1] : null;

    // Extract category from data-category attribute
    const catMatch = cardMatch[0].match(/data-category="([^"]+)"/i);
    const category = catMatch ? catMatch[1] : null;
    const topics = mapCategory(category);

    videos.push({
      id,
      year: videoYear,
      title,
      duration,
      durationSeconds: parseDuration(duration),
      url: `https://developer.apple.com/videos/play/wwdc${videoYear}/${id}/`,
      topics,
      ...(category ? { category } : {}),
    });
  }

  // Fallback for older pages with different HTML structure
  if (videos.length === 0) {
    const linkRegex = /href="\/videos\/play\/wwdc(\d{4})\/(\d+)\/?"/gi;
    let m;
    const positions = [];

    while ((m = linkRegex.exec(html)) !== null) {
      const id = m[2];
      if (seen.has(id)) continue;
      seen.add(id);
      positions.push({ year: parseInt(m[1]), id, index: m.index });
    }

    for (const pos of positions) {
      const chunk = html.substring(Math.max(0, pos.index - 200), pos.index + 800);

      // Try multiple title extraction patterns
      const titleMatch = chunk.match(/<h[2-6][^>]*>\s*([^<]+?)\s*<\/h[2-6]>/i) ||
                         chunk.match(/alt="([^"]+)"/i) ||
                         chunk.match(/title="([^"]+)"/i);

      const durMatch = chunk.match(/(\d+:\d+)/);

      videos.push({
        id: pos.id,
        year: pos.year,
        title: titleMatch ? titleMatch[1].trim() : `Session ${pos.id}`,
        duration: durMatch ? durMatch[1] : null,
        durationSeconds: parseDuration(durMatch ? durMatch[1] : null),
        url: `https://developer.apple.com/videos/play/wwdc${pos.year}/${pos.id}/`,
        topics: ['General'],
      });
    }
  }

  console.log(`  Found ${videos.length} videos for WWDC${year}`);
  const titled = videos.filter(v => !v.title.startsWith('Session ')).length;
  const untitled = videos.length - titled;
  if (untitled > 0) {
    console.log(`  (${titled} with titles, ${untitled} need title from video page)`);
  }

  return videos;
}

async function enrichMissingTitles(videos) {
  const needsTitle = videos.filter(v => v.title.startsWith('Session '));
  if (needsTitle.length === 0) return videos;

  console.log(`\n  Enriching ${needsTitle.length} videos with missing titles...`);

  let enriched = 0;
  for (const video of needsTitle) {
    try {
      const resp = await fetch(video.url, { headers: HEADERS });
      if (!resp.ok) continue;
      const html = await resp.text();

      // Try multiple title sources
      const titleMatch = html.match(/<h1[^>]*>\s*([\s\S]*?)\s*<\/h1>/i) ||
                         html.match(/<meta[^>]+property="og:title"[^>]+content="([^"]+)"/i) ||
                         html.match(/<title>\s*([^<|]+)/i);

      if (titleMatch) {
        const title = titleMatch[1].replace(/<[^>]*>/g, '').trim();
        if (title && !title.includes('Apple Developer') && title.length > 3) {
          video.title = title;
          enriched++;
        }
      }

      // Also grab description while we're here
      const descMatch = html.match(/<meta[^>]+name="description"[^>]+content="([^"]+)"/i);
      if (descMatch) video.description = descMatch[1];

      // Rate limit
      await new Promise(r => setTimeout(r, 200));
    } catch {
      // skip
    }
  }

  console.log(`  Enriched ${enriched}/${needsTitle.length} titles`);
  return videos;
}

async function main() {
  console.log('Building WWDC Index from developer.apple.com\n');

  mkdirSync(join(DATA_DIR, 'by-year'), { recursive: true });
  mkdirSync(join(DATA_DIR, 'by-topic'), { recursive: true });

  let allVideos = [];
  const byYear = {};

  // Fetch all years
  for (const year of YEARS) {
    let videos = await fetchYearVideos(year);

    // Enrich missing titles by fetching individual pages
    videos = await enrichMissingTitles(videos);

    byYear[year] = videos;
    allVideos.push(...videos);

    writeFileSync(
      join(DATA_DIR, 'by-year', `${year}.json`),
      JSON.stringify({ year, count: videos.length, videos }, null, 2)
    );

    await new Promise(r => setTimeout(r, 300));
  }

  // Build topic index
  const byTopic = {};
  for (const topic of TOPICS) {
    const topicVideos = allVideos.filter(v =>
      v.topics?.includes(topic.name)
    );
    byTopic[topic.slug] = {
      name: topic.name,
      slug: topic.slug,
      count: topicVideos.length,
      videos: topicVideos.map(v => ({
        id: v.id,
        year: v.year,
        title: v.title,
        duration: v.duration,
        url: v.url,
      })),
    };

    writeFileSync(
      join(DATA_DIR, 'by-topic', `${topic.slug}.json`),
      JSON.stringify(byTopic[topic.slug], null, 2)
    );
  }

  // Build main index
  const index = {
    builtAt: new Date().toISOString(),
    source: 'developer.apple.com',
    totalVideos: allVideos.length,
    years: YEARS.map(y => ({
      year: y,
      count: byYear[y]?.length || 0,
    })),
    topics: TOPICS.map(t => ({
      ...t,
      count: byTopic[t.slug]?.count || 0,
    })),
  };

  writeFileSync(join(DATA_DIR, 'index.json'), JSON.stringify(index, null, 2));

  writeFileSync(
    join(DATA_DIR, 'all-videos.json'),
    JSON.stringify({
      builtAt: index.builtAt,
      totalVideos: allVideos.length,
      videos: allVideos,
    }, null, 2)
  );

  writeFileSync(join(DATA_DIR, 'topics.json'), JSON.stringify(TOPICS, null, 2));

  // Stats
  const titled = allVideos.filter(v => !v.title.startsWith('Session ')).length;
  const categorized = allVideos.filter(v => !v.topics?.includes('General') || v.topics.length > 1).length;

  console.log(`\nDone.`);
  console.log(`  Total: ${allVideos.length} videos across ${YEARS.length} years`);
  console.log(`  Titled: ${titled}/${allVideos.length}`);
  console.log(`  Categorized: ${categorized}/${allVideos.length}`);
  console.log(`  Data saved to: ${DATA_DIR}`);
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
