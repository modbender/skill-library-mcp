#!/usr/bin/env node
// Extract Douban data from browser evaluate results → CSV
// Generates the extraction function to run in browser console

const extractionScript = `
async function extractAllPages(baseUrl, totalExpected) {
  const perPage = 30;
  const results = [];
  const maxPages = Math.ceil(totalExpected / perPage) + 1;

  for (let page = 0; page < maxPages; page++) {
    const start = page * perPage;
    const url = baseUrl + '?start=' + start + '&sort=time&rating=all&filter=all&mode=list';

    try {
      const resp = await fetch(url);
      const html = await resp.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const items = doc.querySelectorAll('.list-view .item');

      if (items.length === 0) break;

      for (const item of items) {
        const t = item.querySelector('.title a');
        const title = t ? t.textContent.trim() : '';
        const link = t ? t.getAttribute('href') : '';
        const d = item.querySelector('.date');
        let date = '', rating = 0;
        if (d) {
          const r = d.querySelector('span[class*="rating"]');
          if (r) { const m = r.className.match(/rating(\\d+)-t/); if (m) rating = parseInt(m[1]); }
          const dm = d.textContent.match(/(\\d{4}-\\d{2}-\\d{2})/);
          if (dm) date = dm[1];
        }
        const c = item.querySelector('.comment');
        results.push({ title, link, date, rating, comment: c ? c.textContent.trim() : '' });
      }

      if (page < maxPages - 1) await new Promise(r => setTimeout(r, 1500));
    } catch (e) {
      console.error('Error fetching page', start, e);
      break;
    }
  }

  return results;
}

// Usage: paste in browser console on douban.com while logged in
// const books = await extractAllPages('https://book.douban.com/people/USER/collect', 400);
// copy(JSON.stringify(books)); // copies to clipboard
`;

console.log(extractionScript);
