#!/usr/bin/env node

/**
 * Get detailed breakdown for a Plausible Analytics site
 * Usage: node breakdown.mjs <site-id> <property> [--period day|7d|30d] [--limit N]
 * 
 * Properties:
 *   event:page - Top pages
 *   visit:source - Traffic sources
 *   visit:referrer - Referring URLs
 *   visit:utm_medium, visit:utm_source, visit:utm_campaign - UTM parameters
 *   visit:device - Desktop vs Mobile
 *   visit:browser - Browser breakdown
 *   visit:os - Operating system
 *   visit:country - Countries
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
const property = args[1];

if (!siteId || !property) {
  console.error('Usage: node breakdown.mjs <site-id> <property> [--period day|7d|30d] [--limit N]');
  console.error('\nAvailable properties:');
  console.error('  event:page - Top pages');
  console.error('  visit:source - Traffic sources');
  console.error('  visit:referrer - Referring URLs');
  console.error('  visit:utm_medium, visit:utm_source, visit:utm_campaign - UTM parameters');
  console.error('  visit:device - Desktop vs Mobile');
  console.error('  visit:browser - Browser breakdown');
  console.error('  visit:os - Operating system');
  console.error('  visit:country - Countries');
  process.exit(1);
}

// Parse arguments
let period = 'day';
let limit = 10;

for (let i = 2; i < args.length; i++) {
  if (args[i] === '--period' && args[i + 1]) {
    period = args[i + 1];
    i++;
  } else if (args[i] === '--limit' && args[i + 1]) {
    limit = parseInt(args[i + 1], 10);
    i++;
  }
}

// Build URL
const params = new URLSearchParams({
  site_id: siteId,
  period: period,
  property: property,
  limit: limit.toString()
});

const url = `https://plausible.io/api/v1/stats/breakdown?${params.toString()}`;

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
  console.error(`Failed to fetch breakdown: ${error.message}`);
  process.exit(1);
}
