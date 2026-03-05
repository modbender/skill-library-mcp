#!/usr/bin/env node
/**
 * Post a single tweet by ID from approved queue
 * Usage: node scripts/post-single.js <id>
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function postTweet(text) {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:18792');
  const context = browser.contexts()[0];
  const page = await context.newPage();
  
  try {
    console.log(`📱 Posting: "${text.substring(0, 50)}..."`);
    
    await page.goto('https://x.com/compose/tweet', { waitUntil: 'networkidle' });
    await page.waitForSelector('[data-testid="tweetTextarea_0"]', { timeout: 10000 });
    
    await page.fill('[data-testid="tweetTextarea_0"]', text);
    
    // Human-like delay
    await page.waitForTimeout(1000 + Math.random() * 2000);
    
    await page.click('[data-testid="tweetButtonInline"]');
    await page.waitForTimeout(3000);
    
    console.log('✅ Posted successfully!');
    
    await page.close();
    await browser.close();
    
    return true;
  } catch (error) {
    console.error('❌ Error posting:', error.message);
    await page.close();
    await browser.close();
    return false;
  }
}

async function main() {
  const tweetId = parseInt(process.argv[2]);
  
  if (!tweetId) {
    console.error('❌ Usage: node scripts/post-single.js <id>');
    process.exit(1);
  }
  
  const queueFile = path.join(__dirname, '..', 'data', 'approved-queue.json');
  
  if (!fs.existsSync(queueFile)) {
    console.log('📭 No approved tweets in queue');
    return;
  }
  
  let queue = JSON.parse(fs.readFileSync(queueFile, 'utf8'));
  const tweetIndex = queue.findIndex(t => t.id === tweetId);
  
  if (tweetIndex === -1) {
    console.error(`❌ Tweet #${tweetId} not found in queue`);
    process.exit(1);
  }
  
  const tweet = queue[tweetIndex];
  console.log(`📬 Posting tweet #${tweetId}`);
  
  const success = await postTweet(tweet.text);
  
  if (success) {
    // Move to history
    const historyFile = path.join(__dirname, '..', 'data', 'tweet-history.json');
    let history = [];
    
    if (fs.existsSync(historyFile)) {
      history = JSON.parse(fs.readFileSync(historyFile, 'utf8'));
    }
    
    tweet.posted = true;
    tweet.postedAt = new Date().toISOString();
    history.push(tweet);
    
    fs.writeFileSync(historyFile, JSON.stringify(history, null, 2));
    
    // Remove from queue
    queue.splice(tweetIndex, 1);
    fs.writeFileSync(queueFile, JSON.stringify(queue, null, 2));
    
    console.log('🎉 Tweet posted and moved to history!');
  } else {
    console.error('❌ Failed to post tweet');
    process.exit(1);
  }
}

main();
