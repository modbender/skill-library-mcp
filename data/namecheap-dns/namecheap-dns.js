#!/usr/bin/env node

import axios from 'axios';
import { writeFileSync, readFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { homedir } from 'os';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));

const API_BASE = 'https://api.namecheap.com/xml.response';

// Configurable backup directory
function getBackupDir() {
  if (process.env.NAMECHEAP_BACKUP_DIR) {
    return process.env.NAMECHEAP_BACKUP_DIR;
  }
  // Default fallback
  return join(__dirname, 'backups');
}

const BACKUP_DIR = getBackupDir();

// Ensure backup directory exists
if (!existsSync(BACKUP_DIR)) {
  mkdirSync(BACKUP_DIR, { recursive: true });
}

// Parse CLI args
const args = process.argv.slice(2);
const command = args[0];
const domain = args[1];

function getEnv(key) {
  const value = process.env[key];
  if (!value) {
    console.error(`❌ Error: ${key} environment variable not set`);
    console.error(`   Add to ~/.zshrc: export ${key}="your-value"`);
    process.exit(1);
  }
  return value;
}

// Only require env vars for actual commands, not help
let API_KEY, USERNAME, API_USER;
if (command && command !== 'help' && args[1]) {
  API_KEY = getEnv('NAMECHEAP_API_KEY');
  USERNAME = getEnv('NAMECHEAP_USERNAME');
  API_USER = getEnv('NAMECHEAP_API_USER');
}

// Get client IP
async function getClientIP() {
  try {
    const response = await axios.get('https://ifconfig.me/ip');
    return response.data.trim();
  } catch (error) {
    console.error('❌ Failed to get client IP:', error.message);
    process.exit(1);
  }
}

// Parse domain into SLD and TLD
function parseDomain(fullDomain) {
  const parts = fullDomain.split('.');
  if (parts.length < 2) {
    console.error(`❌ Invalid domain: ${fullDomain}`);
    process.exit(1);
  }
  return {
    sld: parts.slice(0, -1).join('.'),
    tld: parts[parts.length - 1],
  };
}

// Make API request
async function apiRequest(command, extraParams = {}) {
  const clientIp = await getClientIP();
  const params = {
    ApiUser: API_USER,
    ApiKey: API_KEY,
    UserName: USERNAME,
    Command: command,
    ClientIp: clientIp,
    ...extraParams,
  };

  try {
    const response = await axios.get(API_BASE, { params });
    const xml = response.data;

    // Check for API errors
    if (xml.includes('<Status>ERROR</Status>')) {
      const errorMatch = xml.match(/<Error[^>]*>(.*?)<\/Error>/);
      const error = errorMatch ? errorMatch[1] : 'Unknown error';
      throw new Error(error);
    }

    return xml;
  } catch (error) {
    if (error.message.includes('IP not whitelisted')) {
      console.error('❌ API Error: Your IP is not whitelisted');
      console.error(`   Current IP: ${clientIp}`);
      console.error('   Add it at: https://ap.www.namecheap.com/settings/tools/apiaccess/');
    } else {
      console.error('❌ API Error:', error.message);
    }
    process.exit(1);
  }
}

// Get current DNS hosts
async function getHosts(fullDomain) {
  const { sld, tld } = parseDomain(fullDomain);
  const xml = await apiRequest('namecheap.domains.dns.getHosts', { SLD: sld, TLD: tld });

  // Debug: log raw XML if DEBUG env var is set
  if (process.env.DEBUG) {
    console.error('[DEBUG] Raw XML response:', xml);
  }

  const hosts = [];
  const hostRegex = /<host ([^>]*)\/>/g;
  let match;

  while ((match = hostRegex.exec(xml)) !== null) {
    const attrs = match[1];
    const getAttr = (name) => {
      const m = attrs.match(new RegExp(`${name}="([^"]*)"`));
      return m ? m[1] : '';
    };

    hosts.push({
      hostId: getAttr('HostId'),
      name: getAttr('Name'),
      type: getAttr('Type'),
      address: getAttr('Address'),
      mxPref: getAttr('MXPref') || '10',
      ttl: getAttr('TTL') || '1800',
    });
  }

  return hosts;
}

// Set DNS hosts (replaces ALL records)
async function setHosts(fullDomain, hosts) {
  const { sld, tld } = parseDomain(fullDomain);
  const params = { SLD: sld, TLD: tld };

  hosts.forEach((host, i) => {
    const idx = i + 1;
    params[`HostName${idx}`] = host.name;
    params[`RecordType${idx}`] = host.type;
    params[`Address${idx}`] = host.address;
    if (host.type === 'MX') {
      params[`MXPref${idx}`] = host.mxPref;
    }
    params[`TTL${idx}`] = host.ttl;
  });

  await apiRequest('namecheap.domains.dns.setHosts', params);
}

// Query live DNS records via dig
function queryLiveDNS(fullDomain) {
  const types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS'];
  const records = [];

  for (const type of types) {
    try {
      const output = execSync(`dig +short ${fullDomain} ${type}`, { 
        encoding: 'utf8',
        timeout: 5000,
        stdio: ['pipe', 'pipe', 'ignore'] // suppress stderr
      }).trim();

      if (!output) continue;

      const lines = output.split('\n').filter(l => l.trim());
      
      for (const line of lines) {
        if (type === 'MX') {
          // Format: "10 mail.example.com."
          const match = line.match(/^(\d+)\s+(.+)$/);
          if (match) {
            records.push({
              name: '@',
              type: 'MX',
              address: match[2].replace(/\.$/, ''),
              mxPref: match[1],
            });
          }
        } else if (type === 'TXT') {
          // Remove quotes from TXT records
          records.push({
            name: '@',
            type: 'TXT',
            address: line.replace(/^"(.*)"$/, '$1'),
          });
        } else {
          records.push({
            name: '@',
            type: type,
            address: line.replace(/\.$/, ''),
          });
        }
      }
    } catch (error) {
      // dig failed or timed out - skip this type
      continue;
    }
  }

  // Also query common subdomains
  const subdomains = ['www', 'mail', 'email', 'smtp', 'imap', 'pop', 'ftp'];
  for (const sub of subdomains) {
    for (const type of ['A', 'CNAME', 'MX', 'TXT']) {
      try {
        const output = execSync(`dig +short ${sub}.${fullDomain} ${type}`, {
          encoding: 'utf8',
          timeout: 3000,
          stdio: ['pipe', 'pipe', 'ignore']
        }).trim();

        if (!output) continue;

        const lines = output.split('\n').filter(l => l.trim());
        for (const line of lines) {
          if (type === 'MX') {
            const match = line.match(/^(\d+)\s+(.+)$/);
            if (match) {
              records.push({
                name: sub,
                type: 'MX',
                address: match[2].replace(/\.$/, ''),
                mxPref: match[1],
              });
            }
          } else if (type === 'TXT') {
            records.push({
              name: sub,
              type: 'TXT',
              address: line.replace(/^"(.*)"$/, '$1'),
            });
          } else {
            records.push({
              name: sub,
              type: type,
              address: line.replace(/\.$/, ''),
            });
          }
        }
      } catch (error) {
        continue;
      }
    }
  }

  return records;
}

// Compare API records with live DNS
function findGhostRecords(apiHosts, liveRecords) {
  const apiSet = new Set();
  
  apiHosts.forEach(h => {
    const name = h.name || '@';
    const key = `${name}:${h.type}:${h.address.toLowerCase()}`;
    apiSet.add(key);
  });

  const ghosts = [];
  
  liveRecords.forEach(live => {
    const name = live.name || '@';
    const key = `${name}:${live.type}:${live.address.toLowerCase()}`;
    
    if (!apiSet.has(key)) {
      ghosts.push(live);
    }
  });

  return ghosts;
}

// Verify DNS and check for ghost records
async function verifyDNS(fullDomain, silent = false) {
  if (!silent) {
    console.log(`🔍 Verifying DNS for ${fullDomain}...`);
  }

  const apiHosts = await getHosts(fullDomain);
  
  if (!silent) {
    console.log(`📡 Querying live DNS...`);
  }
  
  const liveRecords = queryLiveDNS(fullDomain);
  const ghosts = findGhostRecords(apiHosts, liveRecords);

  if (!silent) {
    console.log(`\n📊 Results:`);
    console.log(`   API records: ${apiHosts.length}`);
    console.log(`   Live DNS records: ${liveRecords.length}`);
    console.log(`   Ghost records: ${ghosts.length}`);
  }

  if (ghosts.length > 0 && !silent) {
    console.log(`\n⚠️  Ghost Records Detected (in DNS but NOT in API):\n`);
    ghosts.forEach(g => {
      const name = g.name || '@';
      const mxPref = g.type === 'MX' ? ` [${g.mxPref}]` : '';
      console.log(`   ${g.type.padEnd(6)} ${name.padEnd(25)} → ${g.address}${mxPref}`);
    });
    console.log(`\n⚠️  WARNING: These records are managed by Namecheap subsystems`);
    console.log(`   (email forwarding, URL redirects, etc.) and are INVISIBLE to the API.`);
    console.log(`   Using setHosts will DELETE these records!`);
  } else if (!silent) {
    console.log(`\n✅ No ghost records detected - API and DNS are in sync`);
  }

  return ghosts;
}

// Safety check before setHosts - returns true if safe to proceed
async function safetyCheck(fullDomain, force = false) {
  const ghosts = await verifyDNS(fullDomain, true);
  
  if (ghosts.length === 0) {
    return true;
  }

  console.log(`\n⚠️  SAFETY CHECK FAILED: Ghost records detected!\n`);
  console.log(`   The following records exist in DNS but are NOT visible to the API:\n`);
  
  ghosts.forEach(g => {
    const name = g.name || '@';
    const mxPref = g.type === 'MX' ? ` [${g.mxPref}]` : '';
    console.log(`   ${g.type.padEnd(6)} ${name.padEnd(25)} → ${g.address}${mxPref}`);
  });

  console.log(`\n   These records will be DELETED if you proceed!`);
  console.log(`   They are likely managed by Namecheap subsystems:`);
  console.log(`   - Email forwarding (MX, SPF, DKIM records)`);
  console.log(`   - URL Redirect records`);
  console.log(`   - Domain parking records\n`);

  if (force) {
    console.log(`⚠️  --force flag detected: Proceeding anyway (you've been warned!)\n`);
    return true;
  }

  console.log(`❌ REFUSING to proceed. To override, use --force flag.\n`);
  return false;
}

// Create backup with DNS snapshot
function createBackup(fullDomain, hosts) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T').join('-').slice(0, -5);
  const filename = `${fullDomain}-${timestamp}.json`;
  const path = join(BACKUP_DIR, filename);

  // Also capture live DNS state
  const liveDNS = queryLiveDNS(fullDomain);

  const backup = {
    domain: fullDomain,
    timestamp,
    apiHosts: hosts,
    liveDNS: liveDNS,
    note: 'apiHosts = records visible to Namecheap API; liveDNS = actual DNS records via dig'
  };

  writeFileSync(path, JSON.stringify(backup, null, 2));
  console.log(`📦 Backup created: ${filename}`);
  console.log(`   - API records: ${hosts.length}`);
  console.log(`   - Live DNS records: ${liveDNS.length}`);
  return filename;
}

// List backups
function listBackups(fullDomain) {
  if (!existsSync(BACKUP_DIR)) {
    return [];
  }

  return readdirSync(BACKUP_DIR)
    .filter(f => f.startsWith(fullDomain) && f.endsWith('.json'))
    .sort()
    .reverse();
}

// Load backup
function loadBackup(filename) {
  const path = join(BACKUP_DIR, filename);
  if (!existsSync(path)) {
    console.error(`❌ Backup not found: ${filename}`);
    process.exit(1);
  }
  const backup = JSON.parse(readFileSync(path, 'utf8'));
  
  // Support old format (hosts) and new format (apiHosts)
  if (!backup.apiHosts && backup.hosts) {
    backup.apiHosts = backup.hosts;
  }
  
  return backup;
}

// Show diff
function showDiff(oldHosts, newHosts) {
  const oldSet = new Set(oldHosts.map(h => `${h.name}:${h.type}:${h.address}`));
  const newSet = new Set(newHosts.map(h => `${h.name}:${h.type}:${h.address}`));

  const added = newHosts.filter(h => !oldSet.has(`${h.name}:${h.type}:${h.address}`));
  const removed = oldHosts.filter(h => !newSet.has(`${h.name}:${h.type}:${h.address}`));

  if (added.length === 0 && removed.length === 0) {
    console.log('✅ No changes');
    return false;
  }

  console.log('\n📋 Changes:');
  if (added.length > 0) {
    console.log('\n  ➕ Added:');
    added.forEach(h => console.log(`     ${h.type.padEnd(6)} ${h.name || '@'} → ${h.address}`));
  }
  if (removed.length > 0) {
    console.log('\n  ➖ Removed:');
    removed.forEach(h => console.log(`     ${h.type.padEnd(6)} ${h.name || '@'} → ${h.address}`));
  }
  console.log();

  return true;
}

// Parse record arg (format: "host=value" or "host=priority value" for MX)
function parseRecord(arg, type) {
  const [name, ...valueParts] = arg.split('=');
  const value = valueParts.join('=');

  if (type === 'MX') {
    // Format: "host=10 mx.example.com"
    const match = value.match(/^(\d+)\s+(.+)$/);
    if (!match) {
      console.error(`❌ Invalid MX format: ${arg}`);
      console.error('   Expected: host=10 mx.example.com');
      process.exit(1);
    }
    return { name, mxPref: match[1], address: match[2] };
  }

  return { name, address: value };
}

// Commands

async function cmdVerify() {
  if (!domain) {
    console.error('Usage: namecheap-dns verify <domain>');
    process.exit(1);
  }

  await verifyDNS(domain, false);
}

async function cmdList() {
  if (!domain) {
    console.error('Usage: namecheap-dns list <domain>');
    process.exit(1);
  }

  console.log(`🔍 Fetching DNS records for ${domain}...`);
  const hosts = await getHosts(domain);

  if (hosts.length === 0) {
    console.log('  (no records)');
    return;
  }

  console.log(`\n📋 Current records (${hosts.length}):\n`);
  hosts.forEach(h => {
    const name = h.name || '@';
    const mxPref = h.type === 'MX' ? ` [${h.mxPref}]` : '';
    console.log(`  ${h.type.padEnd(6)} ${name.padEnd(25)} → ${h.address}${mxPref}`);
  });
  console.log();
}

async function cmdAdd() {
  if (!domain) {
    console.error('Usage: namecheap-dns add <domain> [options]');
    console.error('Options:');
    console.error('  --txt "host=value"');
    console.error('  --cname "host=target"');
    console.error('  --mx "host=10 mx.example.com"');
    console.error('  --a "host=1.2.3.4"');
    console.error('  --dry-run');
    console.error('  --force     (override safety check for ghost records)');
    process.exit(1);
  }

  const dryRun = args.includes('--dry-run');
  const force = args.includes('--force');
  const newRecords = [];

  for (let i = 2; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--dry-run' || arg === '--force') continue;

    const nextArg = args[i + 1];
    if (!nextArg || nextArg.startsWith('--')) {
      console.error(`❌ Missing value for ${arg}`);
      process.exit(1);
    }

    const type = arg.replace('--', '').toUpperCase();
    const parsed = parseRecord(nextArg, type);

    newRecords.push({
      name: parsed.name === '@' ? '' : parsed.name,
      type,
      address: parsed.address,
      mxPref: parsed.mxPref || '10',
      ttl: '1800',
    });

    i++; // skip next arg
  }

  if (newRecords.length === 0) {
    console.error('❌ No records to add');
    process.exit(1);
  }

  console.log(`🔍 Fetching current DNS records for ${domain}...`);
  const currentHosts = await getHosts(domain);

  // Merge (skip duplicates)
  const merged = [...currentHosts];
  newRecords.forEach(newRec => {
    const exists = currentHosts.some(
      h => h.name === newRec.name && h.type === newRec.type && h.address === newRec.address
    );
    if (!exists) {
      merged.push(newRec);
    }
  });

  const hasChanges = showDiff(currentHosts, merged);
  if (!hasChanges) {
    console.log('✅ All records already exist, nothing to do');
    return;
  }

  if (dryRun) {
    console.log('🔍 Dry-run mode: No changes applied');
    return;
  }

  // Safety check for ghost records
  const safe = await safetyCheck(domain, force);
  if (!safe) {
    process.exit(1);
  }

  // Create backup before applying
  createBackup(domain, currentHosts);

  console.log('⚙️  Applying changes...');
  await setHosts(domain, merged);
  console.log('✅ DNS records updated successfully');
}

async function cmdRemove() {
  if (!domain) {
    console.error('Usage: namecheap-dns remove <domain> --host <name> --type <type> [--dry-run] [--force]');
    process.exit(1);
  }

  const hostIdx = args.indexOf('--host');
  const typeIdx = args.indexOf('--type');
  const dryRun = args.includes('--dry-run');
  const force = args.includes('--force');

  if (hostIdx === -1 || typeIdx === -1) {
    console.error('❌ Missing --host or --type');
    process.exit(1);
  }

  const hostName = args[hostIdx + 1] === '@' ? '' : args[hostIdx + 1];
  const hostType = args[typeIdx + 1].toUpperCase();

  console.log(`🔍 Fetching current DNS records for ${domain}...`);
  const currentHosts = await getHosts(domain);

  const filtered = currentHosts.filter(h => !(h.name === hostName && h.type === hostType));

  const hasChanges = showDiff(currentHosts, filtered);
  if (!hasChanges) {
    console.log('✅ Record not found, nothing to remove');
    return;
  }

  if (dryRun) {
    console.log('🔍 Dry-run mode: No changes applied');
    return;
  }

  // Safety check for ghost records
  const safe = await safetyCheck(domain, force);
  if (!safe) {
    process.exit(1);
  }

  // Create backup before applying
  createBackup(domain, currentHosts);

  console.log('⚙️  Applying changes...');
  await setHosts(domain, filtered);
  console.log('✅ DNS records updated successfully');
}

async function cmdBackup() {
  if (!domain) {
    console.error('Usage: namecheap-dns backup <domain>');
    process.exit(1);
  }

  console.log(`🔍 Fetching current DNS records for ${domain}...`);
  const hosts = await getHosts(domain);
  createBackup(domain, hosts);
}

async function cmdBackups() {
  if (!domain) {
    console.error('Usage: namecheap-dns backups <domain>');
    process.exit(1);
  }

  const backups = listBackups(domain);
  if (backups.length === 0) {
    console.log(`📦 No backups found for ${domain}`);
    return;
  }

  console.log(`\n📦 Backups for ${domain} (${backups.length}):\n`);
  backups.forEach((b, i) => {
    const label = i === 0 ? ' [latest]' : '';
    console.log(`  ${b}${label}`);
  });
  console.log();
}

async function cmdRestore() {
  if (!domain) {
    console.error('Usage: namecheap-dns restore <domain> [--backup <filename>] [--force]');
    process.exit(1);
  }

  const backupIdx = args.indexOf('--backup');
  const force = args.includes('--force');
  let backupFile;

  if (backupIdx === -1) {
    // Use latest
    const backups = listBackups(domain);
    if (backups.length === 0) {
      console.error(`❌ No backups found for ${domain}`);
      process.exit(1);
    }
    backupFile = backups[0];
    console.log(`📦 Using latest backup: ${backupFile}`);
  } else {
    backupFile = args[backupIdx + 1];
  }

  const backup = loadBackup(backupFile);
  console.log(`📦 Loaded backup from ${backup.timestamp}`);

  console.log(`🔍 Fetching current DNS records for ${domain}...`);
  const currentHosts = await getHosts(domain);

  const hasChanges = showDiff(currentHosts, backup.apiHosts);
  if (!hasChanges) {
    console.log('✅ DNS already matches backup, nothing to restore');
    return;
  }

  console.log('⚠️  About to restore DNS from backup. Continue? (Ctrl+C to cancel)');
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Safety check for ghost records
  const safe = await safetyCheck(domain, force);
  if (!safe) {
    process.exit(1);
  }

  // Create backup of current state before restoring
  createBackup(domain, currentHosts);

  console.log('⚙️  Restoring from backup...');
  await setHosts(domain, backup.apiHosts);
  console.log('✅ DNS records restored successfully');
}

// Main
(async () => {
  try {
    switch (command) {
      case 'verify':
        await cmdVerify();
        break;
      case 'list':
        await cmdList();
        break;
      case 'add':
        await cmdAdd();
        break;
      case 'remove':
        await cmdRemove();
        break;
      case 'backup':
        await cmdBackup();
        break;
      case 'backups':
        await cmdBackups();
        break;
      case 'restore':
        await cmdRestore();
        break;
      default:
        console.log('Namecheap DNS Manager v1.1.0');
        console.log('');
        console.log('Usage: namecheap-dns <command> [options]');
        console.log('');
        console.log('Commands:');
        console.log('  verify <domain>                  Verify DNS and detect ghost records');
        console.log('  list <domain>                    List current DNS records (API only)');
        console.log('  add <domain> [options]           Add DNS records (merges with existing)');
        console.log('  remove <domain> [options]        Remove DNS records');
        console.log('  backup <domain>                  Create manual backup (includes DNS snapshot)');
        console.log('  backups <domain>                 List available backups');
        console.log('  restore <domain> [options]       Restore from backup');
        console.log('');
        console.log('Safety Options:');
        console.log('  --force                          Override ghost record safety check');
        console.log('  --dry-run                        Preview changes without applying');
        console.log('');
        console.log('Examples:');
        console.log('  namecheap-dns verify example.com');
        console.log('  namecheap-dns list example.com');
        console.log('  namecheap-dns add example.com --txt "mail=v=spf1 include:mailgun.org ~all"');
        console.log('  namecheap-dns add example.com --cname "www=example.com" --dry-run');
        console.log('  namecheap-dns add example.com --txt "test=value" --force');
        console.log('  namecheap-dns remove example.com --host "old" --type "TXT"');
        console.log('  namecheap-dns restore example.com');
        process.exit(command ? 1 : 0);
    }
  } catch (error) {
    console.error('❌ Fatal error:', error.message);
    process.exit(1);
  }
})();
