#!/usr/bin/env node
/**
 * table.mjs - Generate table images from JSON data
 * 
 * Usage:
 *   node table.mjs --data '[{"Name":"Alice","Score":95}]' --output table.png
 *   echo '[{"a":1}]' | node table.mjs --output table.png
 */

import sharp from 'sharp';
import { writeFileSync, readFileSync } from 'fs';
import { segmentText, hasEmoji, precacheEmojis } from './emoji.mjs';

// Parse CLI args
function parseArgs(args) {
  const opts = {
    output: 'table.png',
    maxWidth: 800,
    fontSize: 14,
    headerColor: '#e63946',
    stripe: true,
    dark: false,
    compact: false,
    rtl: false,
    wrap: true,
    maxLines: 3,
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];
    
    switch (arg) {
      case '--data': opts.data = JSON.parse(next); i++; break;
      case '--data-file': opts.data = JSON.parse(readFileSync(next, 'utf8')); i++; break;
      case '--output': opts.output = next; i++; break;
      case '--title': opts.title = next; i++; break;
      case '--dark': opts.dark = true; break;
      case '--columns': opts.columns = next.split(',').map(s => s.trim()); i++; break;
      case '--headers': opts.headers = next.split(',').map(s => s.trim()); i++; break;
      case '--max-width': opts.maxWidth = parseInt(next); i++; break;
      case '--font-size': opts.fontSize = parseInt(next); i++; break;
      case '--header-color': opts.headerColor = next; i++; break;
      case '--no-stripe': opts.stripe = false; break;
      case '--stripe': opts.stripe = true; break;
      case '--align': opts.align = next.split(',').map(s => s.trim().toLowerCase()); i++; break;
      case '--compact': opts.compact = true; break;
      case '--rtl': opts.rtl = true; break;
      case '--no-wrap': opts.wrap = false; break;
      case '--max-lines': opts.maxLines = parseInt(next); i++; break;
      case '--subtitle': opts.subtitle = next; i++; break;
      case '-o': opts.output = next; i++; break;
      case '--help':
        console.log(`
table.mjs - Generate table images from JSON data

Usage:
  node table.mjs --data '[{"Name":"Alice"}]' --output table.png

Options:
  --data          JSON array of row objects (required, or use --data-file/stdin)
  --data-file     Read JSON data from a file (avoids shell quoting issues)
  --output        Output file path (default: table.png)
  --title         Table title
  --dark          Dark mode (Discord-friendly)
  --columns       Column order/subset (comma-separated)
  --headers       Custom header names (comma-separated)
  --max-width     Maximum table width (default: 800)
  --font-size     Font size in pixels (default: 14)
  --header-color  Header background color (default: #e63946)
  --no-stripe     Disable alternating row colors
  --align         Column alignments: l,r,c (comma-separated)
  --compact       Reduce padding
  --rtl           Force RTL layout (auto-detected for Hebrew/Arabic)
  --no-wrap       Disable word wrapping (truncate instead)
  --max-lines N   Max lines per cell when wrapping (default: 3)
`);
        process.exit(0);
    }
  }
  
  return opts;
}

// Estimate text width (rough approximation for sans-serif fonts)
function estimateTextWidth(text, fontSize) {
  // Average character width is roughly 0.6 * fontSize for sans-serif
  // Add some buffer for safety
  return String(text).length * fontSize * 0.65;
}

// Truncate text to fit width
function truncateText(text, maxWidth, fontSize) {
  const str = String(text);
  const charWidth = fontSize * 0.55;
  const maxChars = Math.floor(maxWidth / charWidth);
  if (str.length <= maxChars) return str;
  return str.slice(0, maxChars - 1) + '…';
}

// Word-wrap text into lines that fit within maxWidth
function wrapText(text, maxWidth, fontSize, maxLines = 3) {
  const str = String(text);
  const charWidth = fontSize * 0.55;
  const maxChars = Math.floor(maxWidth / charWidth);
  
  if (str.length <= maxChars) return [str];
  
  const words = str.split(/(\s+)/); // Keep whitespace as separate tokens
  const lines = [];
  let currentLine = '';
  
  for (const word of words) {
    const testLine = currentLine + word;
    if (testLine.length > maxChars && currentLine.length > 0) {
      lines.push(currentLine.trimEnd());
      if (lines.length >= maxLines) {
        // Truncate last line
        lines[lines.length - 1] = lines[lines.length - 1].slice(0, maxChars - 1) + '…';
        return lines;
      }
      currentLine = word.trimStart();
    } else {
      currentLine = testLine;
    }
  }
  
  if (currentLine.trim()) {
    if (lines.length >= maxLines) {
      lines[lines.length - 1] = lines[lines.length - 1].slice(0, maxChars - 1) + '…';
    } else {
      lines.push(currentLine.trimEnd());
    }
  }
  
  return lines;
}

// Detect if value looks numeric
function isNumeric(val) {
  if (typeof val === 'number') return true;
  if (typeof val !== 'string') return false;
  const cleaned = val.replace(/[$,%+\-\s]/g, '');
  return !isNaN(parseFloat(cleaned)) && isFinite(cleaned);
}

// Detect if text contains RTL characters (Hebrew, Arabic, etc.)
function containsRtl(text) {
  return /[\u0590-\u05FF\u0600-\u06FF\u0700-\u074F\uFB50-\uFDFF\uFE70-\uFEFF]/.test(String(text));
}

// Auto-detect RTL from data and column names
function autoDetectRtl(data, columns) {
  for (const row of data) {
    for (const col of columns) {
      if (containsRtl(row[col] ?? '')) return true;
    }
  }
  for (const col of columns) {
    if (containsRtl(col)) return true;
  }
  return false;
}

// Escape XML special characters
function escapeXml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

// Render a cell that may contain emoji as mixed text+image SVG elements
function renderCell(text, x, y, anchor, cssClass, fontSize, emojiCache) {
  const str = String(text);
  if (!emojiCache || !hasEmoji(str)) {
    // Simple text rendering
    return `\n  <text x="${x}" y="${y}" text-anchor="${anchor}" class="${cssClass}">${escapeXml(str)}</text>`;
  }
  
  // Mixed emoji + text rendering
  const segments = segmentText(str);
  const emojiSize = fontSize * 1.15;
  let svgParts = '';
  
  // For proper positioning, we need to know total width
  // We'll use a <g> group and position segments left-to-right
  // Then offset the group based on anchor
  const charWidth = fontSize * 0.6;
  let totalWidth = 0;
  const segWidths = segments.map(seg => {
    if (seg.type === 'emoji') return emojiSize;
    return seg.value.length * charWidth;
  });
  totalWidth = segWidths.reduce((a, b) => a + b, 0);
  
  // Calculate group start X based on anchor
  let startX;
  if (anchor === 'end') startX = x - totalWidth;
  else if (anchor === 'middle') startX = x - totalWidth / 2;
  else startX = x;
  
  let curX = startX;
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    if (seg.type === 'emoji') {
      const dataUri = emojiCache.get(seg.value);
      if (dataUri) {
        svgParts += `\n  <image href="${dataUri}" x="${curX}" y="${y - emojiSize + 2}" width="${emojiSize}" height="${emojiSize}"/>`;
      } else {
        svgParts += `\n  <text x="${curX}" y="${y}" class="${cssClass}">${escapeXml(seg.value)}</text>`;
      }
      curX += emojiSize;
    } else {
      svgParts += `\n  <text x="${curX}" y="${y}" text-anchor="start" class="${cssClass}">${escapeXml(seg.value)}</text>`;
      curX += segWidths[i];
    }
  }
  
  return svgParts;
}

// Generate SVG table
async function generateTableSvg(data, opts) {
  if (!data || data.length === 0) {
    throw new Error('No data provided');
  }
  
  // Pre-cache emoji SVGs from all text in the table
  const allTexts = [];
  data.forEach(row => Object.values(row).forEach(v => allTexts.push(String(v))));
  if (opts.title) allTexts.push(opts.title);
  const emojiCache = await precacheEmojis(allTexts);
  
  // Determine columns
  let columns = opts.columns || Object.keys(data[0]);
  let headers = opts.headers || [...columns];
  
  // Auto-detect RTL if not explicitly set via --rtl flag
  const isRtl = opts.rtl || autoDetectRtl(data, columns);
  
  // For RTL: reverse column order so the layout reads right-to-left
  if (isRtl) {
    columns = [...columns].reverse();
    headers = [...headers].reverse();
    if (opts.align) opts.align = [...opts.align].reverse();
  }
  
  // Theme colors
  const theme = opts.dark ? {
    bg: '#2f3136',        // Discord dark bg
    headerBg: opts.headerColor,
    headerText: '#ffffff',
    rowBg: '#36393f',     // Discord darker
    rowAltBg: '#2f3136',  // Discord dark
    text: '#dcddde',      // Discord text
    border: '#40444b',    // Discord border
  } : {
    bg: '#ffffff',
    headerBg: opts.headerColor,
    headerText: '#ffffff',
    rowBg: '#ffffff',
    rowAltBg: '#f8f9fa',
    text: '#212529',
    border: '#dee2e6',
  };
  
  const padding = opts.compact ? { x: 8, y: 4 } : { x: 12, y: 8 };
  const fontSize = opts.fontSize;
  const lineHeight = fontSize * 1.4;
  const rowHeight = lineHeight + padding.y * 2;
  
  // Calculate column widths
  const minColWidth = fontSize * 4; // Minimum column width
  const colWidths = columns.map((col, i) => {
    const headerWidth = estimateTextWidth(headers[i] || col, fontSize);
    const maxDataWidth = Math.max(...data.map(row => 
      estimateTextWidth(row[col] ?? '', fontSize)
    ));
    return Math.max(headerWidth, maxDataWidth, minColWidth) + padding.x * 2;
  });
  
  // Constrain to max width — when wrapping is on, be smarter about distribution
  let totalWidth = colWidths.reduce((a, b) => a + b, 0);
  if (totalWidth > opts.maxWidth) {
    if (opts.wrap) {
      // Smart distribution: ensure headers fit, shrink wide columns proportionally
      const headerWidths = columns.map((col, i) => 
        estimateTextWidth(headers[i] || col, fontSize) + padding.x * 2
      );
      const minWidths = headerWidths.map((hw, i) => Math.max(hw, minColWidth));
      const totalMin = minWidths.reduce((a, b) => a + b, 0);
      const excess = opts.maxWidth - totalMin;
      
      if (excess > 0) {
        // Distribute extra space proportionally to how much each col wants beyond its min
        const wants = colWidths.map((w, i) => Math.max(0, w - minWidths[i]));
        const totalWant = wants.reduce((a, b) => a + b, 0);
        colWidths.forEach((w, i) => {
          if (totalWant > 0) {
            colWidths[i] = Math.floor(minWidths[i] + (wants[i] / totalWant) * excess);
          } else {
            colWidths[i] = Math.floor(minWidths[i] + excess / columns.length);
          }
        });
      } else {
        // Not enough space even for headers — scale everything
        const scale = opts.maxWidth / totalMin;
        colWidths.forEach((w, i) => colWidths[i] = Math.floor(minWidths[i] * scale));
      }
    } else {
      const scale = opts.maxWidth / totalWidth;
      colWidths.forEach((w, i) => colWidths[i] = Math.floor(w * scale));
    }
    totalWidth = colWidths.reduce((a, b) => a + b, 0);
    // Adjust last column to match maxWidth exactly
    colWidths[colWidths.length - 1] += opts.maxWidth - totalWidth;
    totalWidth = opts.maxWidth;
  }
  
  // Determine alignments
  const alignments = columns.map((col, i) => {
    if (opts.align && opts.align[i]) {
      const a = opts.align[i];
      if (a === 'l' || a === 'left') return 'start';
      if (a === 'r' || a === 'right') return 'end';
      if (a === 'c' || a === 'center') return 'middle';
    }
    // Auto-detect alignment: right-align numbers, and right-align text in RTL mode
    const hasNumbers = data.some(row => isNumeric(row[col]));
    if (hasNumbers) return 'end';
    if (isRtl) return 'end';
    return 'start';
  });
  
  // Pre-compute wrapped lines for each cell and row heights
  const wrappedData = data.map(row => {
    const cells = {};
    let maxLines = 1;
    columns.forEach((col, i) => {
      const val = String(row[col] ?? '');
      const availWidth = colWidths[i] - padding.x * 2;
      if (opts.wrap) {
        const lines = wrapText(val, availWidth, fontSize, opts.maxLines);
        cells[col] = lines;
        maxLines = Math.max(maxLines, lines.length);
      } else {
        cells[col] = [truncateText(val, availWidth, fontSize)];
      }
    });
    return { cells, height: lineHeight * maxLines + padding.y * 2 };
  });
  
  // Calculate dimensions
  const titleHeight = opts.title ? fontSize * 2 + (opts.subtitle ? fontSize * 1.3 : 0) : 0;
  const headerHeight = rowHeight;
  const bodyHeight = wrappedData.reduce((sum, r) => sum + r.height, 0);
  const totalHeight = titleHeight + headerHeight + bodyHeight;
  
  // Build SVG
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="${totalHeight}">
  <style>
    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: ${fontSize}px; }
    .title { font-weight: 600; font-size: ${fontSize * 1.2}px; }
    .header { font-weight: 600; fill: ${theme.headerText}; }
    .cell { fill: ${theme.text}; }
  </style>
  <rect width="100%" height="100%" fill="${theme.bg}"/>`;
  
  let y = 0;
  
  // Title & subtitle
  if (opts.title) {
    svg += `
  <text x="${totalWidth / 2}" y="${fontSize * 1.3}" text-anchor="middle" class="title cell">${escapeXml(opts.title)}</text>`;
    if (opts.subtitle) {
      svg += `
  <text x="${totalWidth / 2}" y="${fontSize * 2.5}" text-anchor="middle" class="cell" style="font-size:${fontSize * 0.85}px;opacity:0.65">${escapeXml(opts.subtitle)}</text>`;
    }
    y = titleHeight;
  }
  
  // Header row
  svg += `
  <rect x="0" y="${y}" width="${totalWidth}" height="${headerHeight}" fill="${theme.headerBg}"/>`;
  
  let x = 0;
  columns.forEach((col, i) => {
    const textX = alignments[i] === 'end' ? x + colWidths[i] - padding.x :
                  alignments[i] === 'middle' ? x + colWidths[i] / 2 :
                  x + padding.x;
    const anchor = alignments[i] === 'end' ? 'end' :
                   alignments[i] === 'middle' ? 'middle' : 'start';
    const headerText = truncateText(headers[i] || col, colWidths[i] - padding.x * 2, fontSize);
    svg += renderCell(headerText, textX, y + rowHeight / 2 + fontSize / 3, anchor, 'header', fontSize, emojiCache);
    x += colWidths[i];
  });
  
  y += headerHeight;
  
  // Data rows
  wrappedData.forEach((wrappedRow, rowIndex) => {
    const thisRowHeight = wrappedRow.height;
    const rowBg = opts.stripe && rowIndex % 2 === 1 ? theme.rowAltBg : theme.rowBg;
    svg += `
  <rect x="0" y="${y}" width="${totalWidth}" height="${thisRowHeight}" fill="${rowBg}"/>`;
    
    // Add subtle border between rows
    svg += `
  <line x1="0" y1="${y}" x2="${totalWidth}" y2="${y}" stroke="${theme.border}" stroke-width="0.5"/>`;
    
    let x = 0;
    columns.forEach((col, i) => {
      const lines = wrappedRow.cells[col];
      const textX = alignments[i] === 'end' ? x + colWidths[i] - padding.x :
                    alignments[i] === 'middle' ? x + colWidths[i] / 2 :
                    x + padding.x;
      const anchor = alignments[i] === 'end' ? 'end' :
                     alignments[i] === 'middle' ? 'middle' : 'start';
      
      // Vertically center the text block within the row
      const textBlockHeight = lines.length * lineHeight;
      const startY = y + (thisRowHeight - textBlockHeight) / 2 + fontSize;
      
      lines.forEach((line, lineIdx) => {
        const lineY = startY + lineIdx * lineHeight;
        svg += renderCell(line, textX, lineY, anchor, 'cell', fontSize, emojiCache);
      });
      
      x += colWidths[i];
    });
    
    y += thisRowHeight;
  });
  
  // Bottom border
  svg += `
  <line x1="0" y1="${y}" x2="${totalWidth}" y2="${y}" stroke="${theme.border}" stroke-width="0.5"/>`;
  
  svg += `
</svg>`;
  
  return svg;
}

// Main
async function main() {
  const opts = parseArgs(process.argv.slice(2));
  
  // Read data from stdin if not provided
  if (!opts.data) {
    const stdin = readFileSync(0, 'utf8').trim();
    if (stdin) {
      opts.data = JSON.parse(stdin);
    }
  }
  
  if (!opts.data || opts.data.length === 0) {
    console.error('Error: No data provided. Use --data or pipe JSON to stdin.');
    process.exit(1);
  }
  
  // Generate SVG
  const svg = await generateTableSvg(opts.data, opts);
  
  // Convert to PNG
  const pngBuffer = await sharp(Buffer.from(svg))
    .png()
    .toBuffer();
  
  writeFileSync(opts.output, pngBuffer);
  console.log(`Table saved to ${opts.output}`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
