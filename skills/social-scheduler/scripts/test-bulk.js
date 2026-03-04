#!/usr/bin/env node

/**
 * Test suite for bulk scheduler
 */

const { parseCSV, parseJSON, schedulePost } = require('./bulk.js');
const fs = require('fs').promises;
const path = require('path');

async function runTests() {
  console.log('🧪 Bulk Scheduler Test Suite\n');
  
  let passed = 0;
  let failed = 0;
  
  // Test 1: Parse simple CSV
  try {
    const testCSV = `datetime,platform,content,media
2026-02-04T10:00:00,twitter,Hello world!,
2026-02-04T15:30:00,reddit,Test post,/path/to/image.jpg`;
    
    const tmpFile = path.join(__dirname, '..', 'storage', 'test.csv');
    await fs.writeFile(tmpFile, testCSV);
    
    const posts = await parseCSV(tmpFile);
    
    if (posts.length === 2 && 
        posts[0].datetime === '2026-02-04T10:00:00' &&
        posts[0].platform === 'twitter' &&
        posts[1].media === '/path/to/image.jpg') {
      console.log('✅ CSV parsing works');
      passed++;
    } else {
      console.log('❌ CSV parsing failed');
      failed++;
    }
    
    await fs.unlink(tmpFile);
  } catch (err) {
    console.log(`❌ CSV parsing error: ${err.message}`);
    failed++;
  }
  
  // Test 2: Parse CSV with quoted fields (commas in content)
  try {
    const testCSV = `datetime,platform,content,media
2026-02-04T10:00:00,twitter,"Hello, world! This has commas.",`;
    
    const tmpFile = path.join(__dirname, '..', 'storage', 'test2.csv');
    await fs.writeFile(tmpFile, testCSV);
    
    const posts = await parseCSV(tmpFile);
    
    if (posts.length === 1 && posts[0].content === 'Hello, world! This has commas.') {
      console.log('✅ CSV quoted fields parsing works');
      passed++;
    } else {
      console.log('❌ CSV quoted fields parsing failed');
      console.log('  Got:', posts[0].content);
      failed++;
    }
    
    await fs.unlink(tmpFile);
  } catch (err) {
    console.log(`❌ CSV quoted fields error: ${err.message}`);
    failed++;
  }
  
  // Test 3: Parse JSON
  try {
    const testJSON = [
      {
        datetime: '2026-02-04T10:00:00',
        platform: 'twitter',
        content: 'Test post',
        media: null
      }
    ];
    
    const tmpFile = path.join(__dirname, '..', 'storage', 'test.json');
    await fs.writeFile(tmpFile, JSON.stringify(testJSON, null, 2));
    
    const posts = await parseJSON(tmpFile);
    
    if (posts.length === 1 && posts[0].platform === 'twitter') {
      console.log('✅ JSON parsing works');
      passed++;
    } else {
      console.log('❌ JSON parsing failed');
      failed++;
    }
    
    await fs.unlink(tmpFile);
  } catch (err) {
    console.log(`❌ JSON parsing error: ${err.message}`);
    failed++;
  }
  
  // Test 4: Validate post with missing datetime
  try {
    const result = await schedulePost({
      platform: 'twitter',
      content: 'Test'
    }, true);
    
    if (!result.success && result.error.includes('datetime')) {
      console.log('✅ Missing datetime validation works');
      passed++;
    } else {
      console.log('❌ Missing datetime validation failed');
      failed++;
    }
  } catch (err) {
    console.log(`❌ Missing datetime validation error: ${err.message}`);
    failed++;
  }
  
  // Test 5: Validate post with invalid datetime
  try {
    const result = await schedulePost({
      datetime: 'not-a-date',
      platform: 'twitter',
      content: 'Test'
    }, true);
    
    if (!result.success && result.error.includes('Invalid datetime')) {
      console.log('✅ Invalid datetime validation works');
      passed++;
    } else {
      console.log('❌ Invalid datetime validation failed');
      failed++;
    }
  } catch (err) {
    console.log(`❌ Invalid datetime validation error: ${err.message}`);
    failed++;
  }
  
  // Test 6: Validate post with past datetime
  try {
    const result = await schedulePost({
      datetime: '2020-01-01T10:00:00',
      platform: 'twitter',
      content: 'Test'
    }, true);
    
    if (!result.success && result.error.includes('past')) {
      console.log('✅ Past datetime validation works');
      passed++;
    } else {
      console.log('❌ Past datetime validation failed');
      failed++;
    }
  } catch (err) {
    console.log(`❌ Past datetime validation error: ${err.message}`);
    failed++;
  }
  
  // Test 7: Validate post with unknown platform
  try {
    const result = await schedulePost({
      datetime: '2026-12-31T10:00:00',
      platform: 'fakebook',
      content: 'Test'
    }, true);
    
    if (!result.success && result.error.includes('Unknown platform')) {
      console.log('✅ Unknown platform validation works');
      passed++;
    } else {
      console.log('❌ Unknown platform validation failed');
      failed++;
    }
  } catch (err) {
    console.log(`❌ Unknown platform validation error: ${err.message}`);
    failed++;
  }
  
  // Test 8: Validate post with missing content
  try {
    const result = await schedulePost({
      datetime: '2026-12-31T10:00:00',
      platform: 'twitter',
      content: ''
    }, true);
    
    if (!result.success && result.error.includes('content')) {
      console.log('✅ Missing content validation works');
      passed++;
    } else {
      console.log('❌ Missing content validation failed');
      failed++;
    }
  } catch (err) {
    console.log(`❌ Missing content validation error: ${err.message}`);
    failed++;
  }
  
  // Summary
  console.log(`\n📊 Test Results:`);
  console.log(`  ✅ Passed: ${passed}`);
  console.log(`  ❌ Failed: ${failed}`);
  
  if (failed === 0) {
    console.log('\n✨ All bulk scheduler tests passed!');
  } else {
    console.log(`\n⚠️ ${failed} test(s) failed`);
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('Test suite error:', err);
  process.exit(1);
});
