#!/usr/bin/env node

/**
 * Get real-time visitor count for a Plausible Analytics site
 * Usage: node realtime.mjs <site-id>
 * 
 * Requires: PLAUSIBLE_API_KEY environment variable
 */

const apiKey = process.env.PLAUSIBLE_API_KEY;

if (!apiKey) {
  console.error('Missing PLAUSIBLE_API_KEY environment variable');
  process.exit(1);
}

const siteId = process.argv[2] || process.env.PLAUSIBLE_SITE_ID;

if (!siteId) {
  console.error('Usage: node realtime.mjs <site-id>');
  process.exit(1);
}

const url = `https://plausible.io/api/v1/stats/realtime/visitors?site_id=${encodeURIComponent(siteId)}`;

try {
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${apiKey}`
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`API error (${response.status}): ${errorText}`);
    process.exit(1);
  }

  const data = await response.json();
  console.log(JSON.stringify({ visitors: data }, null, 2));
} catch (error) {
  console.error(`Failed to fetch realtime visitors: ${error.message}`);
  process.exit(1);
}
