#!/usr/bin/env node

/**
 * Get aggregate statistics for a Plausible Analytics site
 * Usage: node stats.mjs <site-id> [--period day|7d|30d|month|6mo|12mo] [--date YYYY-MM-DD]
 * 
 * Requires: PLAUSIBLE_API_KEY environment variable
 */

const apiKey = process.env.PLAUSIBLE_API_KEY;

if (!apiKey) {
  console.error('Missing PLAUSIBLE_API_KEY environment variable');
  process.exit(1);
}

const args = process.argv.slice(2);
const siteId = args[0] || process.env.PLAUSIBLE_SITE_ID;

if (!siteId) {
  console.error('Usage: node stats.mjs <site-id> [--period day|7d|30d|month|6mo|12mo] [--date YYYY-MM-DD]');
  process.exit(1);
}

// Parse arguments
let period = 'day';
let date = null;

for (let i = 1; i < args.length; i++) {
  if (args[i] === '--period' && args[i + 1]) {
    period = args[i + 1];
    i++;
  } else if (args[i] === '--date' && args[i + 1]) {
    date = args[i + 1];
    i++;
  }
}

// Build URL
const params = new URLSearchParams({
  site_id: siteId,
  period: period,
  metrics: 'visitors,pageviews,bounce_rate,visit_duration'
});

if (date) {
  params.append('date', date);
}

const url = `https://plausible.io/api/v1/stats/aggregate?${params.toString()}`;

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
  console.log(JSON.stringify({ results: data.results }, null, 2));
} catch (error) {
  console.error(`Failed to fetch stats: ${error.message}`);
  process.exit(1);
}
