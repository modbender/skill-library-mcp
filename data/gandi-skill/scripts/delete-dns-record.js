#!/usr/bin/env node

/**
 * Delete a DNS record
 * Usage: node delete-dns-record.js <domain> <name> <type> [--force]
 * Examples:
 *   node delete-dns-record.js example.com old A
 *   node delete-dns-record.js example.com test CNAME --force
 */

import { deleteDnsRecord, getDnsRecord, sanitizeDomain, sanitizeRecordName } from './gandi-api.js';
import readline from 'readline';

const args = process.argv.slice(2);
const force = args.includes('--force');
const [rawDomain, rawName, type] = args.filter(arg => !arg.startsWith('--'));

// Check required arguments
if (!rawDomain || !rawName || !type) {
  console.error('❌ Usage: node delete-dns-record.js <domain> <name> <type> [--force]');
  console.error('');
  console.error('Examples:');
  console.error('  node delete-dns-record.js example.com old A');
  console.error('  node delete-dns-record.js example.com test CNAME --force');
  console.error('');
  console.error('Options:');
  console.error('  --force    Skip confirmation prompt');
  process.exit(1);
}

// Sanitize inputs for security
let domain, name;
try {
  domain = sanitizeDomain(rawDomain);
  name = sanitizeRecordName(rawName);
} catch (error) {
  console.error(`❌ Invalid input: ${error.message}`);
  process.exit(1);
}

async function confirmDelete() {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question('⚠️  Are you sure you want to delete this record? (yes/no): ', (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'yes' || answer.toLowerCase() === 'y');
    });
  });
}

async function main() {
  try {
    console.log(`🔍 Checking ${type} record for ${name}.${domain}...`);
    console.log('');
    
    // Check if record exists
    let existingRecord;
    try {
      existingRecord = await getDnsRecord(domain, name, type);
    } catch (error) {
      if (error.statusCode === 404) {
        console.error(`❌ Record not found: ${name} ${type}`);
        console.error('   The record may have already been deleted.');
        process.exit(1);
      }
      throw error;
    }
    
    // Show existing record
    console.log('📋 Record to be deleted:');
    console.log(`   Domain: ${domain}`);
    console.log(`   Name: ${name}`);
    console.log(`   Type: ${type}`);
    console.log(`   Value(s): ${existingRecord.rrset_values.join(', ')}`);
    console.log(`   TTL: ${existingRecord.rrset_ttl}s`);
    console.log('');
    
    // Confirm deletion (unless --force)
    if (!force) {
      const confirmed = await confirmDelete();
      if (!confirmed) {
        console.log('❌ Deletion cancelled.');
        process.exit(0);
      }
      console.log('');
    }
    
    // Delete the record
    console.log('🗑️  Deleting record...');
    await deleteDnsRecord(domain, name, type);
    
    console.log('✅ DNS record deleted successfully!');
    console.log('');
    console.log('⏱️  DNS propagation may take a few minutes.');
    console.log('   The old record may still resolve until TTL expires.');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('   Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('   Permission denied. Ensure your token has LiveDNS write access.');
    } else if (error.statusCode === 404) {
      console.error(`   Domain ${domain} not found or not using Gandi LiveDNS.`);
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
