#!/usr/bin/env node

/**
 * View saved contact information
 * 
 * Usage:
 *   node view-contact.js
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

const CONFIG_DIR = path.join(os.homedir(), '.config', 'gandi');
const CONTACT_FILE = path.join(CONFIG_DIR, 'contact.json');

function main() {
  console.log('👤 Saved Contact Information\n');
  
  if (!fs.existsSync(CONTACT_FILE)) {
    console.log('❌ No contact information found.');
    console.log('');
    console.log('Run setup to create contact:');
    console.log('   node setup-contact.js');
    console.log('');
    process.exit(1);
  }
  
  let contact;
  try {
    contact = JSON.parse(fs.readFileSync(CONTACT_FILE, 'utf8'));
  } catch (err) {
    console.error('❌ Error reading contact file:', err.message);
    process.exit(1);
  }
  
  console.log('═══════════════════════════════════════════════════════');
  console.log('📋 CONTACT DETAILS');
  console.log('═══════════════════════════════════════════════════════');
  console.log(`   Name: ${contact.given} ${contact.family}`);
  console.log(`   Email: ${contact.email}`);
  console.log(`   Phone: ${contact.phone}`);
  console.log(`   Address: ${contact.streetaddr}`);
  console.log(`            ${contact.city}, ${contact.state || ''} ${contact.zip}`);
  console.log(`            ${contact.country}`);
  console.log(`   Type: ${contact.type}`);
  console.log('═══════════════════════════════════════════════════════');
  console.log('');
  console.log(`📁 Location: ${CONTACT_FILE}`);
  console.log('');
  console.log('✏️  To edit: node setup-contact.js');
  console.log('');
}

main();
