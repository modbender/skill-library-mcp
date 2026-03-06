#!/usr/bin/env node

const https = require('https');
const http = require('http');

const FEEDS = [
  { name: 'NTV', url: 'https://www.ntv.com.tr/son-dakika.rss' },
  { name: 'CNN Türk', url: 'https://www.cnnturk.com/feed/rss/all/news' },
  { name: 'TRT Haber', url: 'https://www.trthaber.com/sondakika.rss' },
  { name: 'Sözcü', url: 'https://www.sozcu.com.tr/rss/all.xml' },
  { name: 'Milliyet', url: 'https://www.milliyet.com.tr/rss/rssnew/gundemrss.xml' },
  { name: 'Habertürk', url: 'https://www.haberturk.com/rss' },
  { name: 'Hürriyet', url: 'https://www.hurriyet.com.tr/rss/anasayfa' },
  { name: 'Sabah', url: 'https://www.sabah.com.tr/rss/anasayfa.xml' },
  { name: 'AA', url: 'https://www.aa.com.tr/tr/rss/default?cat=guncel' },
];

function fetch(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    mod.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 10000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetch(res.headers.location).then(resolve).catch(reject);
      }
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(data));
      res.on('error', reject);
    }).on('error', reject);
  });
}

function parseHTML(html, baseUrl) {
  const items = [];
  const linkRegex = /<a[^>]+href="(\/[^"]+)"[^>]*>([^<]+)<\/a>/gi;
  let match;
  while ((match = linkRegex.exec(html)) !== null && items.length < 15) {
    const href = match[1];
    const title = match[2].trim();
    if (title.length > 20 && !href.includes('/rss') && !href.includes('/iletisim')) {
      const domain = baseUrl.match(/https?:\/\/[^/]+/)[0];
      items.push({ title, link: domain + href, pubDate: '', description: '' });
    }
  }
  return items;
}

function parseXML(xml) {
  return new Promise((resolve, reject) => {
    // Simple regex-based RSS parser (no dependency needed)
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
    let match;
    while ((match = itemRegex.exec(xml)) !== null) {
      const block = match[1];
      const title = (block.match(/<title><!\[CDATA\[(.*?)\]\]>|<title>(.*?)<\/title>/) || [])[1] || 
                    (block.match(/<title><!\[CDATA\[(.*?)\]\]>|<title>(.*?)<\/title>/) || [])[2] || '';
      const link = (block.match(/<link>(.*?)<\/link>/) || [])[1] || '';
      const pubDate = (block.match(/<pubDate>(.*?)<\/pubDate>/) || [])[1] || '';
      const desc = (block.match(/<description><!\[CDATA\[(.*?)\]\]>|<description>(.*?)<\/description>/) || [])[1] ||
                   (block.match(/<description><!\[CDATA\[(.*?)\]\]>|<description>(.*?)<\/description>/) || [])[2] || '';
      if (title) {
        items.push({
          title: title.replace(/<[^>]*>/g, '').trim(),
          link: link.replace(/<[^>]*>/g, '').trim(),
          pubDate,
          description: desc.replace(/<[^>]*>/g, '').substring(0, 200).trim()
        });
      }
    }
    return resolve(items);
  });
}

async function main() {
  const allNews = [];
  const threeHoursAgo = Date.now() - (3 * 60 * 60 * 1000);

  for (const feed of FEEDS) {
    try {
      const raw = await fetch(feed.url);
      const items = feed.type === 'html' ? parseHTML(raw, feed.url) : await parseXML(raw);
      for (const item of items.slice(0, 15)) {
        const date = item.pubDate ? new Date(item.pubDate).getTime() : Date.now();
        allNews.push({
          source: feed.name,
          title: item.title,
          link: item.link,
          description: item.description,
          date,
          recent: date > threeHoursAgo
        });
      }
    } catch (e) {
      console.error(`[${feed.name}] Hata: ${e.message}`);
    }
  }

  // Sort by date, newest first
  allNews.sort((a, b) => b.date - a.date);

  // Output
  console.log(JSON.stringify(allNews.slice(0, 20), null, 2));
}

main();
