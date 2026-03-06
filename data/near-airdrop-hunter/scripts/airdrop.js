#!/usr/bin/env node

const https = require('https');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const TRACKING_FILE = path.join(os.homedir(), '.near-airdrop', 'tracking.json');

/**
 * Known airdrop sources
 */
const KNOWN_AIRDROPS = {
  aurora: {
    name: 'Aurora',
    checkUrl: 'https://api.aurora.dev/airdrop/eligibility',
    claimUrl: 'https://aurora.dev/claim'
  },
  ref: {
    name: 'Ref Finance',
    checkUrl: 'https://api.ref.finance/airdrop/eligibility',
    claimUrl: 'https://ref.finance/claim'
  },
  metapool: {
    name: 'Meta Pool',
    checkUrl: 'https://api.metapool.app/airdrop/eligibility',
    claimUrl: 'https://metapool.app/claim'
  }
};

/**
 * Load tracking data
 */
async function loadTracking() {
  try {
    const data = await fs.readFile(TRACKING_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return { claimed: [], checked: [] };
  }
}

/**
 * Save tracking data
 */
async function saveTracking(data) {
  await fs.mkdir(path.dirname(TRACKING_FILE), { recursive: true });
  await fs.writeFile(TRACKING_FILE, JSON.stringify(data, null, 2));
}

/**
 * Discover active airdrops
 */
async function discoverAirdrops(platform) {
  console.log('Active Airdrops:');
  console.log('');

  if (platform && platform !== 'all') {
    const airdrop = KNOWN_AIRDROPS[platform];
    if (airdrop) {
      console.log(`  ${airdrop.name} (${platform})`);
      console.log(`    Check: ${airdrop.checkUrl}`);
      console.log(`    Claim: ${airdrop.claimUrl}`);
    } else {
      console.log(`Unknown platform: ${platform}`);
    }
  } else {
    for (const [key, airdrop] of Object.entries(KNOWN_AIRDROPS)) {
      console.log(`  ${airdrop.name} (${key})`);
      console.log(`    Check: ${airdrop.checkUrl}`);
      console.log(`    Claim: ${airdrop.claimUrl}`);
      console.log('');
    }
  }

  return KNOWN_AIRDROPS;
}

/**
 * Check eligibility for an airdrop
 */
async function checkEligibility(accountId, airdropId) {
  const airdrop = KNOWN_AIRDROPS[airdropId];
  if (!airdrop) {
    throw new Error(`Unknown airdrop: ${airdropId}`);
  }

  console.log(`Checking eligibility for ${accountId} on ${airdrop.name}...`);
  console.log(`  Check URL: ${airdrop.checkUrl}`);
  console.log(`  Note: Visit the URL to check eligibility manually`);
  console.log(`  Integration with API requires endpoint-specific implementation`);

  return {
    airdrop: airdrop.name,
    account: accountId,
    status: 'check_required',
    message: 'Visit the check URL to verify eligibility'
  };
}

/**
 * Claim an airdrop
 */
async function claimAirdrop(accountId, airdropId) {
  const airdrop = KNOWN_AIRDROPS[airdropId];
  if (!airdrop) {
    throw new Error(`Unknown airdrop: ${airdropId}`);
  }

  console.log(`Claiming airdrop for ${accountId} on ${airdrop.name}...`);
  console.log(`  Claim URL: ${airdrop.claimUrl}`);
  console.log(`  Note: Visit the URL to claim manually`);
  console.log(`  Integration requires wallet connection and signing`);

  const tracking = await loadTracking();
  tracking.claimed.push({
    airdrop: airdropId,
    account: accountId,
    timestamp: new Date().toISOString()
  });
  await saveTracking(tracking);

  return {
    airdrop: airdrop.name,
    account: accountId,
    status: 'claim_required',
    message: 'Visit the claim URL to complete claiming'
  };
}

// CLI interface
const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

async function main() {
  try {
    switch (command) {
      case 'discover': {
        const platform = arg1 || 'all';
        await discoverAirdrops(platform);
        break;
      }

      case 'check': {
        if (!arg1 || !arg2) {
          console.error('Error: Account ID and airdrop ID required');
          console.error('Usage: near-airdrop check <account_id> <airdrop_id>');
          console.error('Available airdrops:', Object.keys(KNOWN_AIRDROPS).join(', '));
          process.exit(1);
        }
        await checkEligibility(arg1, arg2);
        break;
      }

      case 'claim': {
        if (!arg1 || !arg2) {
          console.error('Error: Account ID and airdrop ID required');
          console.error('Usage: near-airdrop claim <account_id> <airdrop_id>');
          console.error('Available airdrops:', Object.keys(KNOWN_AIRDROPS).join(', '));
          process.exit(1);
        }
        await claimAirdrop(arg1, arg2);
        console.log('✅ Claim tracked! Complete via the claim URL.');
        break;
      }

      case 'list': {
        const tracking = await loadTracking();
        if (tracking.claimed.length === 0) {
          console.log('No claimed airdrops yet');
        } else {
          console.log('Claimed Airdrops:');
          tracking.claimed.forEach(c => {
            console.log(`  ${c.airdrop} for ${c.account} at ${c.timestamp}`);
          });
        }
        break;
      }

      case 'track': {
        const tracking = await loadTracking();
        console.log(`Claimed: ${tracking.claimed.length}`);
        console.log(`Checked: ${tracking.checked.length}`);
        break;
      }

      default:
        console.log('NEAR Airdrop Hunter');
        console.log('');
        console.log('Commands:');
        console.log('  discover [platform]  Discover active airdrops');
        console.log('  check <account> <id>  Check eligibility');
        console.log('  claim <account> <id>  Claim airdrop');
        console.log('  list [account]       List claimed airdrops');
        console.log('  track                Show tracking stats');
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
