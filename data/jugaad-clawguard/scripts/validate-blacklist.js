#!/usr/bin/env node
/**
 * OSBS Blacklist Validator
 * Validates JSONL files against database schema requirements
 * 
 * Usage: node validate-blacklist.js [path-to-jsonl]
 */

import { readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_PATH = join(__dirname, '../db/blacklist-full.jsonl');

// Schema requirements
const REQUIRED_FIELDS = ['id', 'name', 'description', 'tier', 'severity', 'response'];
const VALID_TIERS = [1, 2, 3, 4, 5, 6];
const VALID_SEVERITIES = ['critical', 'high', 'medium', 'low', 'info'];
const VALID_STATUSES = ['active', 'deprecated', 'under_review', 'false_positive'];
const VALID_ACTIONS = ['block', 'warn', 'educate', 'log'];
const VALID_MATCH_TYPES = ['exact', 'prefix', 'suffix', 'contains', 'regex', 'semantic', 'hash'];

function validateThreat(threat, lineNum) {
  const errors = [];
  const warnings = [];
  
  // Required fields
  for (const field of REQUIRED_FIELDS) {
    if (!threat[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  
  // ID format
  if (threat.id && !threat.id.match(/^OSA-\d{4}-\d{3}$/)) {
    warnings.push(`Non-standard ID format: ${threat.id} (expected OSA-YYYY-XXX)`);
  }
  
  // Tier validation
  if (threat.tier && !VALID_TIERS.includes(threat.tier)) {
    errors.push(`Invalid tier: ${threat.tier} (must be 1-6)`);
  }
  
  // Severity validation
  if (threat.severity && !VALID_SEVERITIES.includes(threat.severity.toLowerCase())) {
    errors.push(`Invalid severity: ${threat.severity}`);
  }
  
  // Status validation
  if (threat.status && !VALID_STATUSES.includes(threat.status)) {
    errors.push(`Invalid status: ${threat.status}`);
  }
  
  // Response validation
  if (threat.response) {
    if (typeof threat.response !== 'object') {
      errors.push('Response must be an object');
    } else {
      if (!threat.response.action) {
        errors.push('Missing response.action');
      } else if (!VALID_ACTIONS.includes(threat.response.action)) {
        errors.push(`Invalid response.action: ${threat.response.action}`);
      }
    }
  }
  
  // Confidence validation
  if (threat.confidence !== undefined) {
    if (typeof threat.confidence !== 'number' || threat.confidence < 0 || threat.confidence > 1) {
      errors.push(`Invalid confidence: ${threat.confidence} (must be 0-1)`);
    }
  }
  
  // False positive rate validation
  if (threat.false_positive_rate !== undefined) {
    if (typeof threat.false_positive_rate !== 'number' || 
        threat.false_positive_rate < 0 || 
        threat.false_positive_rate > 1) {
      errors.push(`Invalid false_positive_rate: ${threat.false_positive_rate} (must be 0-1)`);
    }
  }
  
  // Indicators validation
  if (threat.indicators) {
    if (!Array.isArray(threat.indicators)) {
      errors.push('Indicators must be an array');
    } else {
      for (let i = 0; i < threat.indicators.length; i++) {
        const ind = threat.indicators[i];
        if (!ind.type) {
          errors.push(`Indicator ${i}: missing type`);
        }
        if (!ind.value) {
          errors.push(`Indicator ${i}: missing value`);
        }
        if (ind.match_type && !VALID_MATCH_TYPES.includes(ind.match_type)) {
          errors.push(`Indicator ${i}: invalid match_type: ${ind.match_type}`);
        }
        if (ind.weight !== undefined && (ind.weight < 0 || ind.weight > 1)) {
          errors.push(`Indicator ${i}: invalid weight: ${ind.weight}`);
        }
      }
    }
  }
  
  // Date validation
  if (threat.created && !isValidISODate(threat.created)) {
    warnings.push(`Non-standard date format for created: ${threat.created}`);
  }
  if (threat.updated && !isValidISODate(threat.updated)) {
    warnings.push(`Non-standard date format for updated: ${threat.updated}`);
  }
  
  // Teaching prompt warning
  if (!threat.teaching_prompt) {
    warnings.push('Missing teaching_prompt (recommended for AI response)');
  }
  
  return { errors, warnings };
}

function isValidISODate(str) {
  const date = new Date(str);
  return !isNaN(date.getTime());
}

function main() {
  const inputPath = process.argv[2] || DEFAULT_PATH;
  
  console.log('🔍 OSBS Blacklist Validator');
  console.log('=' .repeat(50));
  console.log(`📁 Validating: ${inputPath}`);
  console.log('');
  
  if (!existsSync(inputPath)) {
    console.error(`❌ File not found: ${inputPath}`);
    process.exit(1);
  }
  
  const lines = readFileSync(inputPath, 'utf8')
    .split('\n')
    .filter(l => l.trim() && !l.startsWith('#'));
  
  console.log(`📊 Found ${lines.length} entries to validate`);
  console.log('');
  
  let totalErrors = 0;
  let totalWarnings = 0;
  const threats = [];
  const idSet = new Set();
  const duplicateIds = [];
  
  for (let i = 0; i < lines.length; i++) {
    const lineNum = i + 1;
    
    try {
      const threat = JSON.parse(lines[i]);
      threats.push(threat);
      
      // Check for duplicate IDs
      if (idSet.has(threat.id)) {
        duplicateIds.push({ id: threat.id, line: lineNum });
      }
      idSet.add(threat.id);
      
      const { errors, warnings } = validateThreat(threat, lineNum);
      
      if (errors.length > 0) {
        console.log(`❌ Line ${lineNum} (${threat.id || 'NO ID'}):`);
        for (const err of errors) {
          console.log(`   - ${err}`);
        }
        totalErrors += errors.length;
      }
      
      if (warnings.length > 0 && process.argv.includes('--verbose')) {
        console.log(`⚠️  Line ${lineNum} (${threat.id || 'NO ID'}):`);
        for (const warn of warnings) {
          console.log(`   - ${warn}`);
        }
        totalWarnings += warnings.length;
      }
      
    } catch (e) {
      console.log(`❌ Line ${lineNum}: Invalid JSON - ${e.message}`);
      totalErrors++;
    }
  }
  
  // Check for duplicate IDs
  if (duplicateIds.length > 0) {
    console.log('');
    console.log('🔄 DUPLICATE IDs FOUND:');
    for (const dup of duplicateIds) {
      console.log(`   - ${dup.id} (line ${dup.line})`);
    }
    totalErrors += duplicateIds.length;
  }
  
  // Summary
  console.log('');
  console.log('📊 VALIDATION SUMMARY');
  console.log('=' .repeat(50));
  console.log(`   Total entries:    ${lines.length}`);
  console.log(`   Unique IDs:       ${idSet.size}`);
  console.log(`   Errors:           ${totalErrors}`);
  console.log(`   Warnings:         ${totalWarnings}`);
  
  // Stats
  if (threats.length > 0) {
    const tierCounts = {};
    const sevCounts = {};
    const actionCounts = {};
    let indicatorCount = 0;
    
    for (const t of threats) {
      tierCounts[t.tier] = (tierCounts[t.tier] || 0) + 1;
      sevCounts[t.severity] = (sevCounts[t.severity] || 0) + 1;
      if (t.response?.action) {
        actionCounts[t.response.action] = (actionCounts[t.response.action] || 0) + 1;
      }
      if (t.indicators) {
        indicatorCount += t.indicators.length;
      }
    }
    
    console.log('');
    console.log('📈 STATISTICS:');
    console.log(`   Total indicators: ${indicatorCount}`);
    console.log('');
    console.log('   By Tier:');
    for (let i = 1; i <= 6; i++) {
      console.log(`     T${i}: ${tierCounts[i] || 0}`);
    }
    console.log('');
    console.log('   By Severity:');
    for (const sev of ['critical', 'high', 'medium', 'low', 'info']) {
      if (sevCounts[sev]) {
        console.log(`     ${sev}: ${sevCounts[sev]}`);
      }
    }
    console.log('');
    console.log('   By Action:');
    for (const action of ['block', 'warn', 'educate', 'log']) {
      if (actionCounts[action]) {
        console.log(`     ${action}: ${actionCounts[action]}`);
      }
    }
  }
  
  console.log('');
  if (totalErrors === 0) {
    console.log('✅ VALIDATION PASSED - All entries are valid!');
    process.exit(0);
  } else {
    console.log(`❌ VALIDATION FAILED - ${totalErrors} errors found`);
    process.exit(1);
  }
}

main();
