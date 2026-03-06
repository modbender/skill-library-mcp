/**
 * Screenshot-based CAPTCHA relay (fallback for domain-locked CAPTCHAs)
 * Takes screenshot, overlays numbered grid, sends to human via Telegram
 */
const { CdpSession, getCdpWsUrl } = require('../lib/cdp');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

/**
 * Detect grid dimensions from CAPTCHA iframe
 */
const GRID_DETECT_SCRIPT = `
(() => {
  // Try reCAPTCHA bframe
  const bframe = document.querySelector('iframe[src*="recaptcha/api2/bframe"]');
  if (bframe) {
    try {
      const doc = bframe.contentDocument;
      const tds = doc.querySelectorAll('td[role="button"]');
      const rows = doc.querySelectorAll('tr').length;
      const cols = tds.length / rows;
      const prompt = doc.querySelector('.rc-imageselect-desc-no-canonical')?.textContent ||
                     doc.querySelector('.rc-imageselect-desc')?.textContent || '';
      const table = doc.querySelector('table.rc-imageselect-table');
      const rect = table ? table.getBoundingClientRect() : null;
      const frameRect = bframe.getBoundingClientRect();
      return {
        found: true, rows, cols, prompt,
        gridClip: rect ? {
          x: Math.round(frameRect.x + rect.x),
          y: Math.round(frameRect.y + rect.y),
          w: Math.round(rect.width),
          h: Math.round(rect.height)
        } : null
      };
    } catch(e) {
      return { found: true, rows: 3, cols: 3, prompt: '', gridClip: null, error: e.message };
    }
  }
  return { found: false };
})()
`;

async function captureAndAnnotate(cdpPort = 18800) {
  const wsUrl = await getCdpWsUrl(cdpPort);
  const session = new CdpSession(wsUrl);
  await session.connect();

  try {
    // Detect grid
    const gridInfo = await session.send('Runtime.evaluate', {
      expression: GRID_DETECT_SCRIPT,
      returnByValue: true,
    });
    const grid = gridInfo.result.value;

    // Take screenshot
    const screenshotResult = await session.send('Page.captureScreenshot', {
      format: 'png',
      clip: grid.gridClip ? {
        x: grid.gridClip.x,
        y: grid.gridClip.y,
        width: grid.gridClip.w,
        height: grid.gridClip.h,
        scale: 1,
      } : undefined,
    });

    const imgBuffer = Buffer.from(screenshotResult.data, 'base64');
    const metadata = await sharp(imgBuffer).metadata();
    const { width, height } = metadata;
    const rows = grid.rows || 3;
    const cols = grid.cols || 3;

    // Create SVG overlay with numbered cells
    const cellW = Math.floor(width / cols);
    const cellH = Math.floor(height / rows);
    const fontSize = Math.min(cellW, cellH) * 0.3;

    let svgParts = [`<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">`];
    let cellNum = 1;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cx = c * cellW + cellW / 2;
        const cy = r * cellH + cellH / 2;
        // Number circle
        svgParts.push(`<circle cx="${cx}" cy="${cy}" r="${fontSize * 0.7}" fill="rgba(0,0,0,0.6)" stroke="white" stroke-width="2"/>`);
        svgParts.push(`<text x="${cx}" y="${cy + fontSize * 0.35}" text-anchor="middle" fill="white" font-size="${fontSize}" font-family="Arial" font-weight="bold">${cellNum}</text>`);
        // Grid lines
        if (c > 0) svgParts.push(`<line x1="${c * cellW}" y1="0" x2="${c * cellW}" y2="${height}" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>`);
        if (r > 0) svgParts.push(`<line x1="0" y1="${r * cellH}" x2="${width}" y2="${r * cellH}" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>`);
        cellNum++;
      }
    }
    svgParts.push('</svg>');

    const annotated = await sharp(imgBuffer)
      .composite([{ input: Buffer.from(svgParts.join('')), top: 0, left: 0 }])
      .png()
      .toBuffer();

    const outPath = path.join('/tmp', `captcha-grid-${Date.now()}.png`);
    fs.writeFileSync(outPath, annotated);

    return {
      imagePath: outPath,
      imageBuffer: annotated,
      prompt: grid.prompt || 'Select the correct images',
      rows,
      cols,
      totalCells: rows * cols,
    };
  } finally {
    session.close();
  }
}

/**
 * Inject cell clicks into reCAPTCHA grid
 */
async function injectGridClicks(cells, cdpPort = 18800) {
  const wsUrl = await getCdpWsUrl(cdpPort);
  const session = new CdpSession(wsUrl);
  await session.connect();

  try {
    const script = `
      (() => {
        const cells = ${JSON.stringify(cells)};
        const bframe = document.querySelector('iframe[src*="recaptcha/api2/bframe"]');
        if (!bframe) return 'no-bframe';
        const doc = bframe.contentDocument;
        const tds = doc.querySelectorAll('td[role="button"]');
        cells.forEach(c => { if (tds[c - 1]) tds[c - 1].click(); });
        // Click verify after a short delay
        setTimeout(() => {
          const verify = doc.querySelector('#recaptcha-verify-button');
          if (verify) verify.click();
        }, 500);
        return 'clicked-' + cells.join(',');
      })()
    `;
    const result = await session.send('Runtime.evaluate', {
      expression: script,
      returnByValue: true,
    });
    return result.result.value;
  } finally {
    session.close();
  }
}

module.exports = { captureAndAnnotate, injectGridClicks };
