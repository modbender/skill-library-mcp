/**
 * Card Image Generator
 *
 * Screenshots the "View Full Card" from the Bloom dashboard
 * and uploads to IPFS via Pinata for use as SBT token image.
 */

import * as fs from 'fs';
import * as path from 'path';

interface CardImageResult {
  ipfsHash: string;
  ipfsUrl: string;
  gatewayUrl: string;
}

/**
 * Screenshot the Bloom dashboard card and upload to IPFS.
 *
 * @param dashboardUrl - The agent's dashboard URL (e.g. https://preflight.bloomprotocol.ai/agents/123)
 * @param personalityType - e.g. "The Visionary"
 * @returns IPFS URLs for the card image
 */
export async function captureAndUploadCardImage(
  dashboardUrl: string,
  personalityType: string,
): Promise<CardImageResult | null> {
  const apiKey = process.env.PINATA_API_KEY;
  const apiSecret = process.env.PINATA_API_SECRET;

  if (!apiKey || !apiSecret) {
    console.debug('Pinata keys not set, skipping card image upload');
    return null;
  }

  let browser: any = null;

  try {
    // Dynamic import — puppeteer is a devDependency
    const puppeteer = require('puppeteer');

    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 900, deviceScaleFactor: 2 });

    // Load dashboard
    await page.goto(dashboardUrl, { waitUntil: 'networkidle0', timeout: 20000 });
    await new Promise((r: any) => setTimeout(r, 3000));

    // Click "View Full Card"
    const clicked = await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button'))
        .find((b: any) => b.textContent?.includes('View Full Card'));
      if (btn) { (btn as any).click(); return true; }
      return false;
    });

    if (!clicked) {
      console.debug('View Full Card button not found');
      return null;
    }

    await new Promise((r: any) => setTimeout(r, 2000));

    // Find the card element bounding box
    const cardBox = await page.evaluate(() => {
      const allDivs = Array.from(document.querySelectorAll('div'));
      for (const div of allDivs) {
        const rect = div.getBoundingClientRect();
        if (rect.width > 250 && rect.width < 500 && rect.height > 400 && rect.height < 700) {
          const text = div.textContent || '';
          if (text.includes('Conviction') && text.includes('Intuition')) {
            return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
          }
        }
      }
      return null;
    });

    if (!cardBox) {
      console.debug('Card element not found on page');
      return null;
    }

    // Screenshot just the card
    const pngBuffer = await page.screenshot({
      clip: cardBox,
      encoding: 'binary',
    });

    await browser.close();
    browser = null;

    // Upload to Pinata
    const result = await uploadToPinata(pngBuffer, personalityType, apiKey, apiSecret);
    return result;

  } catch (error) {
    console.debug('Card image capture failed:', error instanceof Error ? error.message : error);
    return null;
  } finally {
    if (browser) {
      try { await browser.close(); } catch {}
    }
  }
}

/**
 * Upload a PNG buffer to Pinata IPFS.
 */
async function uploadToPinata(
  pngBuffer: Buffer,
  personalityType: string,
  apiKey: string,
  apiSecret: string,
): Promise<CardImageResult> {
  const typeSlug = personalityType.replace(/^The /, '').toLowerCase();
  const fileName = `bloom-taste-card-${typeSlug}-${Date.now()}.png`;

  // Build multipart form data manually (no external deps)
  const boundary = '----PinataFormBoundary' + Math.random().toString(36).slice(2);

  const metadataJson = JSON.stringify({
    name: fileName,
    keyvalues: {
      type: 'bloom-taste-card',
      personality: personalityType,
    },
  });

  // Construct multipart body
  const parts: Buffer[] = [];

  // Metadata part
  parts.push(Buffer.from(
    `--${boundary}\r\n` +
    `Content-Disposition: form-data; name="pinataMetadata"\r\n` +
    `Content-Type: application/json\r\n\r\n` +
    `${metadataJson}\r\n`
  ));

  // File part
  parts.push(Buffer.from(
    `--${boundary}\r\n` +
    `Content-Disposition: form-data; name="file"; filename="${fileName}"\r\n` +
    `Content-Type: image/png\r\n\r\n`
  ));
  parts.push(pngBuffer);
  parts.push(Buffer.from(`\r\n--${boundary}--\r\n`));

  const body = Buffer.concat(parts);

  const response = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
    method: 'POST',
    headers: {
      'pinata_api_key': apiKey,
      'pinata_secret_api_key': apiSecret,
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
    },
    body,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Pinata upload failed: HTTP ${response.status} — ${text}`);
  }

  const result: any = await response.json();
  const ipfsHash = result.IpfsHash;

  return {
    ipfsHash,
    ipfsUrl: `ipfs://${ipfsHash}`,
    gatewayUrl: `https://gateway.pinata.cloud/ipfs/${ipfsHash}`,
  };
}
