#!/usr/bin/env node
// Lightweight DuckDuckGo websearch script
// Usage: node ddg_search.js "search query"

const https = require('https');
const http = require('http');
const { parse } = require('node-html-parser');
const qs = require('querystring');

function instantAnswer(query, cb) {
  const u = 'https://api.duckduckgo.com/?' + qs.stringify({ q: query, format: 'json', no_html: 1, no_redirect: 1 });
  https.get(u, res => {
    let data = '';
    res.on('data', c => data += c);
    res.on('end', () => {
      try {
        const j = JSON.parse(data);
        cb(null, j);
      } catch (e) { cb(e); }
    });
  }).on('error', cb);
}

function serpFallback(query, cb) {
  const u = 'https://duckduckgo.com/html/?' + qs.stringify({ q: query });
  https.get(u, res => {
    let data = '';
    res.on('data', c => data += c);
    res.on('end', () => {
      try {
        const root = parse(data);
        const results = [];
        // DuckDuckGo HTML uses .result__a for links in modern markup; fallback scanning
        const anchors = root.querySelectorAll('a.result__a');
        if (anchors.length === 0) {
          // older/simple HTML pages
          const items = root.querySelectorAll('.result');
          for (const it of items.slice(0, 10)) {
            const a = it.querySelector('a');
            if (!a) continue;
            const title = a.text.trim();
            const url = a.getAttribute('href');
            const snippetEl = it.querySelector('.result__snippet') || it.querySelector('.snippet') || null;
            const snippet = snippetEl ? snippetEl.text.trim() : '';
            results.push({ title, url, snippet });
          }
        } else {
          for (const a of anchors.slice(0, 10)) {
            const title = a.text.trim();
            const url = a.getAttribute('href');
            // try to find snippet nearby
            const parent = a.parentNode;
            let snippet = '';
            const s = parent.querySelector('.result__snippet');
            if (s) snippet = s.text.trim();
            results.push({ title, url, snippet });
          }
        }
        cb(null, results.slice(0,5));
      } catch (e) { cb(e); }
    });
  }).on('error', cb);
}

function toOutput(query, ia, serp) {
  const out = { query, summary: '', links: [], source: '', notes: '' };
  if (ia && (ia.AbstractText || (ia.RelatedTopics && ia.RelatedTopics.length))) {
    out.summary = (ia.AbstractText || '').trim();
    if (!out.summary && ia.RelatedTopics && ia.RelatedTopics.length) {
      out.summary = ia.RelatedTopics.slice(0,2).map(t => (t.Text||t).toString()).join('\n');
    }
    out.source = 'instant-answer';
    if (ia.Results && ia.Results.length) {
      for (const r of ia.Results.slice(0,5)) {
        out.links.push({ title: r.Text, url: r.FirstURL, snippet: '' });
      }
    }
  }
  if (serp && serp.length && out.links.length < 5) {
    for (const r of serp) {
      if (out.links.length >=5) break;
      out.links.push({ title: r.title, url: r.url, snippet: r.snippet });
    }
    if (!out.source) out.source = 'serp-fallback';
  }
  return out;
}

function run(query) {
  instantAnswer(query, (err, ia) => {
    if (err) ia = null;
    serpFallback(query, (err2, serp) => {
      if (err2) serp = null;
      const out = toOutput(query, ia, serp);
      console.log(JSON.stringify(out, null, 2));
    });
  });
}

if (require.main === module) {
  const q = process.argv.slice(2).join(' ').trim();
  if (!q) { console.error('Usage: ddg_search.js "query"'); process.exit(2); }
  run(q);
}
