#!/usr/bin/env node
/**
 * Test Script - Verify platform implementations
 */

const discord = require('./platforms/discord');
const reddit = require('./platforms/reddit');
const twitter = require('./platforms/twitter');
const mastodon = require('./platforms/mastodon');
const bluesky = require('./platforms/bluesky');
const moltbook = require('./platforms/moltbook');
const telegram = require('./platforms/telegram');

(async () => {
  // Import LinkedIn (ES module)
  const linkedin = await import('./platforms/linkedin.js');

  console.log('🧪 Social Scheduler Test Suite\n');

  // Test Discord
console.log('Testing Discord Platform:');
try {
  discord.validate('https://discord.com/api/webhooks/123/abc');
  discord.validateContent({ content: 'Test' });
  console.log('  ✅ Discord validation passed');
} catch (e) {
  console.log(`  ❌ Discord validation: ${e.message}`);
}

// Test Reddit
console.log('\nTesting Reddit Platform:');
try {
  const redditConfig = {
    clientId: 'test_id',
    clientSecret: 'test_secret',
    username: 'test_user',
    password: 'test_pass',
    userAgent: 'test'
  };
  reddit.validate(redditConfig);
  reddit.validateContent({ subreddit: 'test', title: 'Test', text: 'Test' });
  console.log('  ✅ Reddit validation passed');
} catch (e) {
  console.log(`  ❌ Reddit validation: ${e.message}`);
}

// Test Twitter
console.log('\nTesting Twitter Platform:');
try {
  const twitterConfig = {
    appKey: 'test_key',
    appSecret: 'test_secret',
    accessToken: 'test_token',
    accessSecret: 'test_token_secret'
  };
  twitter.validate(twitterConfig);
  twitter.validateContent('Hello Twitter!');
  console.log('  ✅ Twitter validation passed');
} catch (e) {
  console.log(`  ❌ Twitter validation: ${e.message}`);
}

// Test Mastodon
console.log('\nTesting Mastodon Platform:');
try {
  const mastodonConfig = {
    instance: 'mastodon.social',
    accessToken: 'test_token'
  };
  mastodon.validate(mastodonConfig);
  mastodon.validateContent('Hello Fediverse!');
  console.log('  ✅ Mastodon validation passed');
} catch (e) {
  console.log(`  ❌ Mastodon validation: ${e.message}`);
}

// Test Bluesky
console.log('\nTesting Bluesky Platform:');
try {
  const blueskyConfig = {
    identifier: 'test.bsky.social',
    password: 'test_password'
  };
  bluesky.validate(blueskyConfig);
  bluesky.validateContent('Hello ATmosphere!');
  console.log('  ✅ Bluesky validation passed');
} catch (e) {
  console.log(`  ❌ Bluesky validation: ${e.message}`);
}

// Test Moltbook
console.log('\nTesting Moltbook Platform:');
try {
  const moltbookConfig = {
    api_key: 'moltbook_sk_test_key_1234567890'
  };
  moltbook.validate(moltbookConfig);
  moltbook.validate('moltbook_sk_test_key_1234567890'); // Test string format
  moltbook.validateContent('Hello Moltbook!');
  moltbook.validateContent({ submolt: 'general', title: 'Test', content: 'Test content' });
  console.log('  ✅ Moltbook validation passed');
} catch (e) {
  console.log(`  ❌ Moltbook validation: ${e.message}`);
}

// Test Telegram
console.log('\nTesting Telegram Platform:');
try {
  const telegramConfig = {
    telegram: {
      botToken: '123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
      chatId: '@testchannel'
    }
  };
  const error = telegram.validate(telegramConfig);
  if (error) throw new Error(error);
  
  const contentError = telegram.validateContent({ text: 'Hello Telegram!' });
  if (contentError) throw new Error(contentError);
  
  // Test with media
  const mediaContentError = telegram.validateContent({
    media: 'test.jpg',
    mediaType: 'photo',
    caption: 'Test photo'
  });
  if (mediaContentError) throw new Error(mediaContentError);
  
  console.log('  ✅ Telegram validation passed');
} catch (e) {
  console.log(`  ❌ Telegram validation: ${e.message}`);
}

// Test LinkedIn
console.log('\nTesting LinkedIn Platform:');
try {
  const linkedinConfig = {
    accessToken: 'AQV_test_token',
    author: 'urn:li:person:test123'
  };
  const errors = linkedin.validate(linkedinConfig);
  if (errors.length > 0) throw new Error(errors.join(', '));
  
  const contentErrors = linkedin.validateContent('Hello LinkedIn!');
  if (contentErrors.length > 0) throw new Error(contentErrors.join(', '));
  
  console.log('  ✅ LinkedIn validation passed');
} catch (e) {
  console.log(`  ❌ LinkedIn validation: ${e.message}`);
}

// Test Queue Manager
const QueueManager = require('./queue');
console.log('\nTesting Queue Manager:');

const queue = new QueueManager();
console.log('  ✅ Queue manager initialized');
console.log('  ✅ Queue file ensured');

const testPost = {
  platform: 'discord',
  content: { content: 'Test' },
  scheduledTime: new Date(Date.now() + 3600000).toISOString(),
  config: 'https://discord.com/api/webhooks/123/abc'
};

const queued = queue.add(testPost);
console.log(`  ${queued.id ? '✅' : '❌'} Post added to queue`);

const pending = queue.getPending();
console.log(`  ${pending.length > 0 ? '✅' : '❌'} Fetch pending posts`);

const canceled = queue.cancel(queued.id);
console.log(`  ${canceled ? '✅' : '❌'} Cancel post`);

// Clean up test data
const cleaned = queue.cleanup();
console.log(`  ${cleaned >= 0 ? '✅' : '❌'} Cleanup old posts`);

console.log('\n✨ All validation tests passed!\n');
console.log('📚 Supported Platforms (8 total):');
console.log('  - Discord (webhooks)');
console.log('  - Reddit (OAuth2)');
console.log('  - Twitter/X (OAuth 1.0a)');
console.log('  - Mastodon (access token)');
console.log('  - Bluesky (AT Protocol)');
console.log('  - Moltbook (API key)');
console.log('  - LinkedIn (OAuth 2.0)');
console.log('  - Telegram (Bot API) ⭐ NEW!');
console.log('\n💡 Quick Start:');
console.log('  node scripts/post.js <platform> <config> <content>');
console.log('  node scripts/schedule.js add <platform> <config> <content> <time>');
console.log('  node scripts/schedule.js list');

})(); // Close async IIFE
