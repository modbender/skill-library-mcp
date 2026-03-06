#!/usr/bin/env node
import puppeteer from 'puppeteer-core';
import { parseArgs } from 'node:util';
import { readFileSync } from 'node:fs';

const { values, positionals } = parseArgs({
  options: {
    o: { type: 'string', default: '/tmp/table.png' },
    title: { type: 'string', default: '' },
    width: { type: 'string', default: '800' },
    dark: { type: 'boolean', default: false },
  },
  allowPositionals: true,
  strict: false,
});

// Get markdown from positional arg or stdin
let md = positionals[0] || '';
if (!md && !process.stdin.isTTY) {
  md = readFileSync('/dev/stdin', 'utf-8');
}
if (!md) {
  console.error('Usage: render.mjs "markdown" -o output.png');
  process.exit(1);
}

// Simple markdown table → HTML converter
function mdToHtml(markdown) {
  const lines = markdown.trim().split('\n');
  let html = '';
  let inTable = false;
  let headerDone = false;

  for (const line of lines) {
    const trimmed = line.trim();
    
    // Table row
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      const cells = trimmed.slice(1, -1).split('|').map(c => c.trim());
      
      // Skip separator row
      if (cells.every(c => /^[-:]+$/.test(c))) {
        headerDone = true;
        continue;
      }
      
      if (!inTable) {
        html += '<table>';
        inTable = true;
      }
      
      const tag = !headerDone ? 'th' : 'td';
      html += '<tr>' + cells.map(c => `<${tag}>${formatCell(c)}</${tag}>`).join('') + '</tr>';
      
      if (!headerDone) headerDone = false; // will be set by separator
    } else {
      if (inTable) {
        html += '</table>';
        inTable = false;
        headerDone = false;
      }
      // Handle headers
      const hMatch = trimmed.match(/^(#{1,6})\s+(.+)/);
      if (hMatch) {
        const level = hMatch[1].length;
        html += `<h${level}>${hMatch[2]}</h${level}>`;
      } else if (trimmed === '') {
        html += '<br>';
      } else {
        html += `<p>${formatCell(trimmed)}</p>`;
      }
    }
  }
  if (inTable) html += '</table>';
  return html;
}

function formatCell(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/~~(.+?)~~/g, '<del>$1</del>');
}

const isDark = values.dark;
const bg = isDark ? '#1e1e2e' : '#ffffff';
const fg = isDark ? '#cdd6f4' : '#1e1e2e';
const headerBg = isDark ? '#313244' : '#e8f4f8';
const borderColor = isDark ? '#45475a' : '#d0d7de';
const altRowBg = isDark ? '#262637' : '#f6f8fa';

const htmlContent = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
    background: ${bg}; color: ${fg};
    padding: 24px; display: inline-block; min-width: 100%;
  }
  h1, h2, h3 { margin-bottom: 12px; color: ${isDark ? '#89b4fa' : '#0969da'}; }
  h2 { font-size: 1.3em; }
  p { margin-bottom: 8px; line-height: 1.5; }
  table {
    border-collapse: collapse; width: 100%;
    margin: 12px 0; border-radius: 8px; overflow: hidden;
    border: 1px solid ${borderColor};
  }
  th {
    background: ${headerBg}; font-weight: 600;
    padding: 10px 16px; text-align: left;
    border-bottom: 2px solid ${borderColor};
    font-size: 0.9em; white-space: nowrap;
  }
  td {
    padding: 8px 16px; border-bottom: 1px solid ${borderColor};
    font-size: 0.9em;
  }
  tr:nth-child(even) td { background: ${altRowBg}; }
  tr:last-child td { border-bottom: none; }
  code {
    background: ${isDark ? '#313244' : '#eff1f3'}; padding: 2px 6px;
    border-radius: 4px; font-size: 0.85em;
  }
  .title {
    font-size: 1.4em; font-weight: 700; margin-bottom: 16px;
    color: ${isDark ? '#89b4fa' : '#0969da'};
    border-bottom: 2px solid ${isDark ? '#89b4fa' : '#0969da'};
    padding-bottom: 8px;
  }
</style></head><body>
${values.title ? `<div class="title">${values.title}</div>` : ''}
${mdToHtml(md)}
</body></html>`;

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});

const page = await browser.newPage();
await page.setViewport({ width: parseInt(values.width), height: 100 });
await page.setContent(htmlContent, { waitUntil: 'networkidle0' });

// Auto-size to content
const bodyHandle = await page.$('body');
const { width, height } = await bodyHandle.boundingBox();
await page.setViewport({ width: Math.ceil(width) + 2, height: Math.ceil(height) + 2 });

await page.screenshot({ path: values.o, fullPage: true, type: 'png' });
await browser.close();
console.log(values.o);
