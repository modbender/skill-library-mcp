#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Paths
const EDITORIAL_DIR = path.join(__dirname, '..', 'editorial');
const REGISTRY_PATH = path.join(EDITORIAL_DIR, 'registry.json');
const LEDGER_PATH = path.join(EDITORIAL_DIR, 'ledger.json');
const TIMELINE_PATH = path.join(EDITORIAL_DIR, 'timeline.json');
const CLAIMS_DIR = path.join(EDITORIAL_DIR, 'claims');
const CLAIMS_ARCHIVE_DIR = path.join(CLAIMS_DIR, 'archive');

// Helpers
function readJSON(filepath) {
  if (!fs.existsSync(filepath)) return null;
  return JSON.parse(fs.readFileSync(filepath, 'utf8'));
}

function writeJSON(filepath, data) {
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

function gitCommit(message) {
  try {
    execSync(`git -C ${EDITORIAL_DIR} add .`, { stdio: 'ignore' });
    execSync(`git -C ${EDITORIAL_DIR} commit -m "${message}"`, { stdio: 'ignore' });
  } catch (e) {
    // Ignore commit failures (no changes, not in git repo, etc.)
  }
}

function getActiveClaims() {
  if (!fs.existsSync(CLAIMS_DIR)) return [];
  const claims = [];
  const files = fs.readdirSync(CLAIMS_DIR).filter(f => f.endsWith('.claim'));
  
  for (const file of files) {
    try {
      const claim = readJSON(path.join(CLAIMS_DIR, file));
      if (claim && claim.claimed_at) {
        // Check if claim is still valid (2 hour TTL)
        const claimedAt = new Date(claim.claimed_at);
        const now = new Date();
        const ageHours = (now - claimedAt) / (1000 * 60 * 60);
        
        if (ageHours < 2) {
          claim.filename = file;
          claims.push(claim);
        } else {
          // Auto-expire old claims
          archiveClaim(file);
        }
      }
    } catch (e) {
      // Skip invalid claim files
    }
  }
  
  return claims;
}

function archiveClaim(filename) {
  const srcPath = path.join(CLAIMS_DIR, filename);
  const dstPath = path.join(CLAIMS_ARCHIVE_DIR, filename);
  if (fs.existsSync(srcPath)) {
    fs.renameSync(srcPath, dstPath);
  }
}

function findConflict(contentId, channel, currentAgent) {
  const claims = getActiveClaims();
  return claims.find(c => 
    c.content_id === contentId && 
    c.channel === channel && 
    c.agent !== currentAgent
  );
}

// Commands

function cmdClaim(contentId, action, channel) {
  if (!contentId || !action || !channel) {
    console.error('Usage: editorial claim <content-id> <action> <channel>');
    process.exit(1);
  }
  
  // Determine agent from environment or default to "unknown"
  const agent = process.env.OPENCLAW_AGENT || process.env.USER || 'unknown';
  
  // Check for conflicts
  const conflict = findConflict(contentId, channel, agent);
  if (conflict) {
    console.error(`⚠️  CONFLICT: ${conflict.agent} already claimed ${contentId} on ${channel}`);
    process.exit(1);
  }
  
  const claim = {
    agent,
    content_id: contentId,
    action,
    channel,
    claimed_at: new Date().toISOString()
  };
  
  const filename = `${contentId}-${agent}.claim`;
  const filepath = path.join(CLAIMS_DIR, filename);
  
  writeJSON(filepath, claim);
  gitCommit(`editorial: ${agent} claimed ${contentId} for ${action} on ${channel}`);
  
  console.log(`✓ Claimed: ${contentId} (${action} on ${channel})`);
}

function cmdRelease(contentId) {
  if (!contentId) {
    console.error('Usage: editorial release <content-id>');
    process.exit(1);
  }
  
  const agent = process.env.OPENCLAW_AGENT || process.env.USER || 'unknown';
  const filename = `${contentId}-${agent}.claim`;
  
  archiveClaim(filename);
  gitCommit(`editorial: ${agent} released claim on ${contentId}`);
  
  console.log(`✓ Released: ${contentId}`);
}

function cmdPublish(contentId, channel, url, title) {
  if (!contentId || !channel || !url) {
    console.error('Usage: editorial publish <content-id> <channel> <url> [title]');
    process.exit(1);
  }
  
  const agent = process.env.OPENCLAW_AGENT || process.env.USER || 'unknown';
  const publishedAt = new Date().toISOString();
  
  // Add to ledger
  const ledger = readJSON(LEDGER_PATH) || [];
  ledger.push({
    content_id: contentId,
    title: title || contentId,
    channel,
    author: agent,
    published_at: publishedAt,
    url,
    status: 'published'
  });
  writeJSON(LEDGER_PATH, ledger);
  
  // Update or add to registry
  const registry = readJSON(REGISTRY_PATH) || [];
  let entry = registry.find(e => e.id === contentId);
  
  if (!entry) {
    entry = {
      id: contentId,
      title: title || contentId,
      type: 'post',
      status: 'published',
      author: agent,
      channels_published: [channel],
      created_at: publishedAt,
      published_at: publishedAt
    };
    registry.push(entry);
  } else {
    entry.status = 'published';
    if (!entry.channels_published) entry.channels_published = [];
    if (!entry.channels_published.includes(channel)) {
      entry.channels_published.push(channel);
    }
    entry.published_at = publishedAt;
  }
  
  writeJSON(REGISTRY_PATH, registry);
  
  // Release claim
  const filename = `${contentId}-${agent}.claim`;
  archiveClaim(filename);
  
  gitCommit(`editorial: ${agent} published ${contentId} on ${channel}`);
  
  console.log(`✓ Published: ${contentId} on ${channel}`);
  console.log(`  URL: ${url}`);
}

function cmdCheck(contentId, channel) {
  if (!contentId || !channel) {
    console.error('Usage: editorial check <content-id> <channel>');
    process.exit(1);
  }
  
  const agent = process.env.OPENCLAW_AGENT || process.env.USER || 'unknown';
  
  // Check for conflicts
  const conflict = findConflict(contentId, channel, agent);
  if (conflict) {
    console.log(`❌ CONFLICT: ${conflict.agent} already claimed ${contentId} on ${channel}`);
    console.log(`   Claimed at: ${conflict.claimed_at}`);
    process.exit(1);
  }
  
  // Check if already published
  const ledger = readJSON(LEDGER_PATH) || [];
  const published = ledger.find(e => e.content_id === contentId && e.channel === channel);
  if (published) {
    console.log(`ℹ️  Already published: ${contentId} on ${channel}`);
    console.log(`   Published at: ${published.published_at}`);
    console.log(`   URL: ${published.url}`);
    process.exit(0);
  }
  
  console.log(`✓ Safe to publish: ${contentId} on ${channel}`);
}

function cmdStatus() {
  console.log('📊 Editorial Status\n');
  
  // Active claims
  const claims = getActiveClaims();
  if (claims.length > 0) {
    console.log('🔥 Active Claims:');
    for (const claim of claims) {
      const age = Math.round((new Date() - new Date(claim.claimed_at)) / (1000 * 60));
      console.log(`   ${claim.agent}: ${claim.content_id} (${claim.action} on ${claim.channel}) — ${age}m ago`);
    }
    console.log('');
  }
  
  // Recent publications
  const ledger = readJSON(LEDGER_PATH) || [];
  const recent = ledger
    .filter(e => {
      const age = (new Date() - new Date(e.published_at)) / (1000 * 60 * 60);
      return age < 48; // Last 48 hours
    })
    .sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
  
  if (recent.length > 0) {
    console.log('📰 Recent Publications (48h):');
    for (const pub of recent) {
      const date = new Date(pub.published_at).toISOString().split('T')[0];
      console.log(`   ${date} | ${pub.channel.padEnd(10)} | ${pub.author.padEnd(8)} | ${pub.title}`);
    }
    console.log('');
  }
  
  // Timeline status
  const timeline = readJSON(TIMELINE_PATH);
  if (timeline && timeline.series) {
    console.log('📅 Timeline Status:');
    for (const [seriesName, series] of Object.entries(timeline.series)) {
      const lastDay = series.days[series.days.length - 1];
      console.log(`   ${seriesName}: Day ${lastDay.day} (${lastDay.date}) — "${lastDay.title}"`);
    }
    console.log('');
  }
  
  // Summary
  const registry = readJSON(REGISTRY_PATH) || [];
  console.log(`📊 Registry: ${registry.length} total entries`);
  console.log(`📋 Ledger: ${ledger.length} publications`);
  console.log(`🔥 Claims: ${claims.length} active`);
}

// Main
const command = process.argv[2];

switch (command) {
  case 'claim':
    cmdClaim(process.argv[3], process.argv[4], process.argv[5]);
    break;
  case 'release':
    cmdRelease(process.argv[3]);
    break;
  case 'publish':
    cmdPublish(process.argv[3], process.argv[4], process.argv[5], process.argv[6]);
    break;
  case 'check':
    cmdCheck(process.argv[3], process.argv[4]);
    break;
  case 'status':
    cmdStatus();
    break;
  default:
    console.log('Usage: editorial <command> [args]');
    console.log('');
    console.log('Commands:');
    console.log('  claim <content-id> <action> <channel>  — Claim work on content');
    console.log('  release <content-id>                    — Release a claim');
    console.log('  publish <content-id> <channel> <url> [title] — Record publication');
    console.log('  check <content-id> <channel>            — Check for conflicts');
    console.log('  status                                  — Show editorial state');
    process.exit(1);
}
