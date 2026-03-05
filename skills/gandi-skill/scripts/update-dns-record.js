#!/usr/bin/env node

/**
 * Update DNS record via Gandi LiveDNS API
 * 
 * Note: This is a convenience wrapper around add-dns-record.js
 * The Gandi API uses PUT which creates OR updates records.
 * 
 * Usage:
 *   node update-dns-record.js <domain> <type> <name> <value> [ttl]
 * 
 * Examples:
 *   node update-dns-record.js example.com A www 192.0.2.10
 *   node update-dns-record.js example.com TXT @ "v=spf1 include:_spf.example.com ~all"
 */

import {
  createDnsRecord,
  getDnsRecord,
  validateRecordValue,
  isValidTTL,
  createSnapshot
} from './gandi-api.js';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 4) {
  console.error('Usage: node update-dns-record.js <domain> <type> <name> <value> [ttl]');
  console.error('');
  console.error('Examples:');
  console.error('  node update-dns-record.js example.com A www 192.0.2.10');
  console.error('  node update-dns-record.js example.com CNAME blog newhost.example.com. 3600');
  console.error('  node update-dns-record.js example.com TXT @ "v=spf1 ..."');
  console.error('');
  console.error('💡 This script updates existing records. To add new records, use add-dns-record.js');
  console.error('   (In practice, both work the same - PUT is idempotent)');
  process.exit(1);
}

const domain = args[0];
const type = args[1].toUpperCase();
const name = args[2];
const value = args[3];
const ttl = args[4] ? parseInt(args[4], 10) : 10800;

// Validate inputs
if (!domain || !type || !name || !value) {
  console.error('❌ Error: Missing required arguments');
  process.exit(1);
}

if (!isValidTTL(ttl)) {
  console.error(`❌ Error: Invalid TTL ${ttl}. Must be between 300 and 2592000 seconds.`);
  process.exit(1);
}

const validation = validateRecordValue(type, value);
if (!validation.valid) {
  console.error(`❌ Error: ${validation.error}`);
  process.exit(1);
}

// Main function
async function main() {
  try {
    console.log(`📝 Updating DNS record for ${domain}`);
    console.log(`   Type: ${type}`);
    console.log(`   Name: ${name}`);
    console.log(`   New Value: ${value}`);
    console.log(`   TTL: ${ttl} seconds`);
    console.log('');
    
    // Check if record exists
    let currentRecord;
    try {
      currentRecord = await getDnsRecord(domain, name, type);
      console.log('📋 Current record:');
      console.log(`   Values: ${currentRecord.rrset_values.join(', ')}`);
      console.log(`   TTL: ${currentRecord.rrset_ttl}`);
      console.log('');
      
      // Create automatic snapshot before updating
      const snapshotName = `Before updating ${name}.${domain} ${type} - ${new Date().toISOString()}`;
      console.log('📸 Creating automatic snapshot...');
      try {
        const snapshot = await createSnapshot(domain, snapshotName);
        console.log(`✅ Snapshot created: ${snapshot.id || 'success'}`);
      } catch (snapErr) {
        console.warn('⚠️  Could not create snapshot (continuing anyway):', snapErr.message);
      }
      console.log('');
      
    } catch (err) {
      if (err.statusCode === 404) {
        console.log('⚠️  Record does not exist. Creating new record instead...');
        console.log('');
      } else {
        throw err;
      }
    }
    
    // Update the record
    const result = await createDnsRecord(domain, name, type, [value], ttl);
    
    if (result.statusCode === 201 || result.statusCode === 204) {
      console.log('✅ DNS record successfully updated!');
      console.log('');
      console.log('📋 New record:');
      console.log(`   Value: ${value}`);
      console.log(`   TTL: ${ttl} seconds`);
      console.log('');
      console.log('⏱️  DNS Propagation:');
      console.log('   - Gandi nameservers: immediate');
      console.log('   - Local cache: ~5 minutes');
      const oldTtl = currentRecord ? currentRecord.rrset_ttl : ttl;
      console.log(`   - Global: up to ${oldTtl} seconds (old TTL)`);
      console.log('');
      console.log('🔍 Verify with:');
      console.log(`   dig ${name === '@' ? domain : name + '.' + domain} ${type}`);
      console.log(`   dig @ns1.gandi.net ${name === '@' ? domain : name + '.' + domain} ${type}`);
    } else {
      console.log(`⚠️  Unexpected response: HTTP ${result.statusCode}`);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Ensure your API token has LiveDNS: write scope.');
      console.error('Create a new token at: https://admin.gandi.net/organizations/account/pat');
    } else if (error.statusCode === 404) {
      console.error('');
      console.error('Domain not found or not using Gandi LiveDNS.');
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
