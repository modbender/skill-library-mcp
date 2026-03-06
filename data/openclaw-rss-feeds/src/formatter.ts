// @elvatis/openclaw-rss-feeds - HTML digest builder
import type { FeedResult, CveEntry, FirmwareEntry } from './types';

interface DigestMetadata {
  startDate: Date;
  endDate: Date;
  generatedAt?: Date;
}

// Escape HTML entities for safe embedding
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Format a date as "Month YYYY" (e.g. "January 2026")
function formatMonthYear(d: Date): string {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];
  return `${months[d.getMonth()]} ${d.getFullYear()}`;
}

// Format short date "DD.MM.YYYY"
function formatDate(d: Date): string {
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// Format CVE description: optionally highlight product names and break on "allows attacker"
function formatCveDescription(desc: string, productHighlightPattern?: string): string {
  let result = desc;

  // Highlight product names if a pattern is configured
  if (productHighlightPattern) {
    try {
      const re = new RegExp(`\\b(${productHighlightPattern})\\b`, 'g');
      result = result.replace(re, '<strong>$1</strong>');
    } catch {
      // Invalid regex - skip highlighting
    }
  }

  // Break before "allows ... attacker"
  result = result.replace(
    /\s+(allows\s+(?:an?\s+)?(?:remote\s+)?attacker)/gi,
    '<br><br>$1'
  );
  return result;
}

function buildSummaryHeader(
  feedResults: FeedResult[],
  metadata: DigestMetadata
): string {
  const totalFirmware = feedResults.reduce((acc, fr) => acc + fr.firmware.length, 0);
  const totalCves = feedResults.reduce((acc, fr) => acc + fr.cves.length, 0);
  const generatedAt = metadata.generatedAt ?? new Date();

  return `
<div style="background:#f8f9fa;border-left:4px solid #1976d2;padding:16px;margin-bottom:24px;font-family:sans-serif;">
  <h3 style="margin:0 0 8px 0;color:#1976d2;">📋 Digest Summary</h3>
  <p style="margin:4px 0;">Period: <strong>${formatDate(metadata.startDate)}</strong> – <strong>${formatDate(metadata.endDate)}</strong></p>
  <p style="margin:4px 0;">Feeds monitored: <strong>${feedResults.length}</strong></p>
  <p style="margin:4px 0;">Firmware updates: <strong>${totalFirmware}</strong></p>
  <p style="margin:4px 0;">CVEs (above threshold): <strong>${totalCves}</strong></p>
  <p style="margin:4px 0;font-size:0.8em;color:#888;">Generated: ${generatedAt.toISOString()}</p>
</div>`;
}

function buildFirmwareSection(firmware: FirmwareEntry[], feedName: string): string {
  if (firmware.length === 0) {
    return `<p style="color:#666;font-style:italic;">No firmware updates for this period.</p>`;
  }

  const rows = firmware
    .map(fw => {
      const typeBg =
        fw.type === 'Major' ? '#e3f2fd' : fw.type === 'Feature' ? '#e8f5e9' : '#fff3e0';
      const typeColor =
        fw.type === 'Major' ? '#1565c0' : fw.type === 'Feature' ? '#2e7d32' : '#e65100';

      const docsCell = fw.docsUrl
        ? `<a href="${escapeHtml(fw.docsUrl)}" target="_blank" style="color:#1976d2;text-decoration:none;">Documentation</a>`
        : `<span style="color:#aaa;">-</span>`;

      return `<tr style="border-bottom:1px solid #eee;">
  <td style="padding:8px;vertical-align:middle;"><strong>${escapeHtml(fw.product)}</strong></td>
  <td style="padding:8px;vertical-align:middle;font-family:monospace;">${escapeHtml(fw.version)}</td>
  <td style="padding:8px;vertical-align:middle;text-align:center;">
    <span style="background:${typeBg};color:${typeColor};padding:2px 8px;border-radius:4px;font-size:0.85em;font-weight:bold;">${fw.type}</span>
  </td>
  <td style="padding:8px;vertical-align:middle;">${docsCell}</td>
</tr>`;
    })
    .join('\n');

  return `<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:0.9em;margin-bottom:8px;">
<thead style="background:#f5f5f5;">
  <tr>
    <th style="padding:8px;text-align:left;border-bottom:2px solid #ddd;">Product</th>
    <th style="padding:8px;text-align:left;border-bottom:2px solid #ddd;">Version</th>
    <th style="padding:8px;text-align:center;border-bottom:2px solid #ddd;">Type</th>
    <th style="padding:8px;text-align:left;border-bottom:2px solid #ddd;">Documentation</th>
  </tr>
</thead>
<tbody>
${rows}
</tbody>
</table>`;
}

function buildCveSection(cves: CveEntry[], cvssThreshold: number, productHighlightPattern?: string): string {
  if (cves.length === 0) {
    return `<p style="color:#666;font-style:italic;">No CVEs above the CVSS threshold (${cvssThreshold}) for this period.</p>`;
  }

  const rows = cves
    .map(cve => {
      const score = cve.score;
      const scoreColor = score >= 9.0 ? '#b71c1c' : score >= 7.0 ? '#d32f2f' : '#e65100';
      const scoreBg = score >= 9.0 ? '#ffcdd2' : score >= 7.0 ? '#ffebee' : '#fff3e0';

      return `<tr style="border-bottom:1px solid #ffebee;">
  <td style="padding:8px;vertical-align:top;white-space:nowrap;">
    <a href="${escapeHtml(cve.url)}" target="_blank" style="color:#d32f2f;font-weight:bold;text-decoration:none;">${escapeHtml(cve.id)}</a>
  </td>
  <td style="padding:8px;vertical-align:top;text-align:center;">
    <span style="background:${scoreBg};color:${scoreColor};padding:2px 8px;border-radius:4px;font-weight:bold;">${score.toFixed(1)}</span>
  </td>
  <td style="padding:8px;vertical-align:top;font-size:0.88em;line-height:1.5;">${formatCveDescription(escapeHtml(cve.description), productHighlightPattern)}</td>
</tr>`;
    })
    .join('\n');

  return `<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:0.9em;margin-bottom:8px;">
<thead style="background:#ffebee;">
  <tr>
    <th style="padding:8px;text-align:left;border-bottom:2px solid #ffcdd2;width:15%;">CVE ID</th>
    <th style="padding:8px;text-align:center;border-bottom:2px solid #ffcdd2;width:10%;">Score</th>
    <th style="padding:8px;text-align:left;border-bottom:2px solid #ffcdd2;">Description</th>
  </tr>
</thead>
<tbody>
${rows}
</tbody>
</table>`;
}

function buildFeedSection(feedResult: FeedResult, cvssThreshold: number): string {
  const hasFirmware = feedResult.firmware.length > 0;
  const hasCves = feedResult.cves.length > 0 && feedResult.enrichCve !== false;

  let section = `<div style="margin-bottom:40px;">
<h2 style="color:#333;border-bottom:2px solid #1976d2;padding-bottom:8px;">📡 ${escapeHtml(feedResult.feedName)}</h2>`;

  if (feedResult.error) {
    section += `<div style="background:#fff3e0;border-left:4px solid #ff9800;padding:12px;margin-bottom:16px;">
  <strong>⚠️ Feed Error:</strong> ${escapeHtml(feedResult.error)}
</div>`;
  }

  // Firmware section
  section += `<h3 style="color:#555;">📦 Firmware Updates</h3>`;
  section += buildFirmwareSection(feedResult.firmware, feedResult.feedName);

  // Items without version (general news items)
  const nonFirmwareItems = feedResult.items.filter(item => !item.version);
  if (nonFirmwareItems.length > 0) {
    section += `<h3 style="color:#555;">📰 Feed Items</h3><ul style="font-size:0.9em;line-height:1.8;">`;
    for (const item of nonFirmwareItems) {
      section += `<li><a href="${escapeHtml(item.link)}" target="_blank" style="color:#1976d2;">${escapeHtml(item.title)}</a>`;
      section += ` <span style="color:#999;font-size:0.85em;">(${formatDate(item.pubDate)})</span></li>`;
    }
    section += `</ul>`;
  }

  if (!hasFirmware && nonFirmwareItems.length === 0 && !feedResult.error) {
    section += `<p style="color:#666;font-style:italic;">No items found for this feed in the selected period.</p>`;
  }

  // CVE section (only if enrichCve is enabled for this feed)
  if (hasCves || feedResult.cveError) {
    section += `<h3 style="color:#555;">⚠️ Security Advisories (CVEs)</h3>`;
    if (feedResult.cveError) {
      section += `<div style="background:#fff3e0;border-left:4px solid #ff9800;padding:12px;margin-bottom:16px;">
  <strong>⚠️ CVE Fetch Warning:</strong> ${escapeHtml(feedResult.cveError)}
</div>`;
    }
    section += buildCveSection(feedResult.cves, cvssThreshold, feedResult.productHighlightPattern);
  }

  section += `</div>`;
  return section;
}

export function formatDigest(
  feedResults: FeedResult[],
  metadata: DigestMetadata,
  cvssThreshold = 6.5
): string {
  const monthYear = formatMonthYear(metadata.startDate);

  // Collect all CVEs across all feeds for the global summary section
  const allCves = feedResults.flatMap(fr => fr.cves);
  allCves.sort((a, b) => b.score - a.score);

  let html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height:1.6; color:#333; max-width:960px; margin:0 auto; padding:20px; }
    a { color:#1976d2; }
    h1 { color:#1a1a1a; }
  </style>
</head>
<body>
<h1>🛡️ Security &amp; Firmware Digest | ${escapeHtml(monthYear)}</h1>
`;

  html += buildSummaryHeader(feedResults, metadata);

  // Per-feed sections
  for (const feedResult of feedResults) {
    html += buildFeedSection(feedResult, cvssThreshold);
  }

  // Global CVE summary (if multiple feeds had CVEs)
  if (feedResults.length > 1 && allCves.length > 0) {
    html += `<div style="margin-top:40px;padding-top:20px;border-top:2px solid #eee;">
<h2 style="color:#333;">🔐 All CVEs - Combined View</h2>
<p style="color:#666;font-size:0.9em;">All CVEs from all feeds above the CVSS threshold (${cvssThreshold}), sorted by severity:</p>
${buildCveSection(allCves, cvssThreshold)}
</div>`;
  }

  html += `\n</body>\n</html>`;
  return html;
}

// Also export a plain-body variant (without full HTML document wrapper) for Ghost
export function formatDigestBody(
  feedResults: FeedResult[],
  metadata: DigestMetadata,
  cvssThreshold = 6.5
): string {
  const monthYear = formatMonthYear(metadata.startDate);
  const allCves = feedResults.flatMap(fr => fr.cves);
  allCves.sort((a, b) => b.score - a.score);

  let html = `<h1>🛡️ Security &amp; Firmware Digest | ${escapeHtml(monthYear)}</h1>\n`;
  html += buildSummaryHeader(feedResults, metadata);

  for (const feedResult of feedResults) {
    html += buildFeedSection(feedResult, cvssThreshold);
  }

  if (feedResults.length > 1 && allCves.length > 0) {
    html += `<div style="margin-top:40px;padding-top:20px;border-top:2px solid #eee;">
<h2 style="color:#333;">🔐 All CVEs - Combined View</h2>
${buildCveSection(allCves, cvssThreshold)}
</div>`;
  }

  return html;
}

// Re-export type for index.ts
export type { DigestMetadata };
