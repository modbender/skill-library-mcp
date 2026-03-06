#!/usr/bin/env node

require('dotenv').config();
const { TwitterApi } = require('twitter-api-v2');
const { program } = require('commander');

// Initialize Twitter client from environment variables
function initializeClient() {
  const apiKey = process.env.X_API_KEY;
  const apiSecret = process.env.X_API_SECRET;
  const accessToken = process.env.X_ACCESS_TOKEN;
  const accessTokenSecret = process.env.X_ACCESS_TOKEN_SECRET;

  if (!apiKey || !apiSecret || !accessToken || !accessTokenSecret) {
    console.error('❌ Missing X API credentials. Set these environment variables:');
    console.error('  X_API_KEY');
    console.error('  X_API_SECRET');
    console.error('  X_ACCESS_TOKEN');
    console.error('  X_ACCESS_TOKEN_SECRET');
    process.exit(1);
  }

  const client = new TwitterApi({
    appKey: apiKey,
    appSecret: apiSecret,
    accessToken: accessToken,
    accessSecret: accessTokenSecret,
  });

  return client.readWrite;
}

// Get current user info (used for mentions and other user-dependent calls)
async function getCurrentUser(client) {
  try {
    const user = await client.v2.me({
      'user.fields': 'public_metrics,created_at,description',
    });
    return user.data;
  } catch (error) {
    throw new Error('Failed to get current user: ' + error.message);
  }
}

// Post command
program
  .command('post <text>')
  .option('--reply-to <id>', 'Reply to tweet ID')
  .option('--quote <id>', 'Quote tweet ID')
  .option('--media <file>', 'Media file to attach')
  .description('Post a tweet')
  .action(async (text, options) => {
    try {
      const client = initializeClient();
      
      const payload = { text };

      if (options.replyTo) {
        payload.reply = { in_reply_to_tweet_id: options.replyTo };
      }

      if (options.quote) {
        payload.quote_tweet_id = options.quote;
      }

      const tweet = await client.v2.tweet(payload);
      
      console.log('✅ Tweet posted');
      console.log(`ID: ${tweet.data.id}`);
      console.log(`URL: https://x.com/i/status/${tweet.data.id}`);
    } catch (error) {
      console.error('❌ Failed to post tweet:', error.message);
      process.exit(1);
    }
  });

// Thread command
program
  .command('thread <tweets...>')
  .description('Post a tweet thread')
  .action(async (tweets) => {
    try {
      const client = initializeClient();
      
      let previousTweetId = null;
      const threadTweets = [];

      for (const text of tweets) {
        const payload = { text };

        if (previousTweetId) {
          payload.reply = { in_reply_to_tweet_id: previousTweetId };
        }

        const tweet = await client.v2.tweet(payload);
        previousTweetId = tweet.data.id;
        threadTweets.push({
          id: tweet.data.id,
          text: text,
        });

        // Small delay between tweets
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      console.log('✅ Thread posted');
      threadTweets.forEach((tweet, i) => {
        console.log(`  ${i + 1}. ${tweet.text}`);
        console.log(`     https://x.com/i/status/${tweet.id}`);
      });
    } catch (error) {
      console.error('❌ Failed to post thread:', error.message);
      process.exit(1);
    }
  });

// Mentions command
program
  .command('mentions')
  .option('--limit <n>', 'Number of mentions', '10')
  .option('--since <id>', 'Only mentions after this ID')
  .option('--format <format>', 'Output format (text|json)', 'text')
  .description('Get recent mentions (requires Basic+ tier)')
  .action(async (options) => {
    try {
      const client = initializeClient();
      
      // Get current user ID
      const user = await getCurrentUser(client);
      const userId = process.env.X_USER_ID || user.id;
      
      const query = {
        max_results: Math.min(parseInt(options.limit), 100),
      };

      if (options.since) {
        query.since_id = options.since;
      }

      const mentions = await client.v2.userMentionTimeline(userId, {
        ...query,
        'tweet.fields': 'created_at,author_id,public_metrics',
      });

      if (options.format === 'json') {
        console.log(JSON.stringify(mentions.data || [], null, 2));
      } else {
        console.log(`📬 Recent mentions of @${user.username} (${mentions.data?.length || 0}):`);
        (mentions.data || []).forEach(tweet => {
          console.log(`  @${tweet.author_id}: ${tweet.text}`);
          console.log(`    ${new Date(tweet.created_at).toLocaleDateString()}`);
          console.log();
        });
      }
    } catch (error) {
      if (error.message.includes('400')) {
        console.error('❌ Mentions failed: This endpoint requires a paid X API tier (Basic+).');
        console.error('   Free tier only supports posting tweets and account lookup.');
        console.error('   Error:', error.message);
      } else {
        console.error('❌ Failed to fetch mentions:', error.message);
      }
      process.exit(1);
    }
  });

// Search command
program
  .command('search <query>')
  .option('--limit <n>', 'Number of results', '10')
  .option('--format <format>', 'Output format (text|json)', 'text')
  .description('Search recent tweets (requires Basic+ tier)')
  .action(async (query, options) => {
    try {
      const client = initializeClient();
      
      // Note: Search requires Basic tier or higher on X API v2
      const results = await client.v2.search(query, {
        max_results: Math.min(parseInt(options.limit), 100),
        'tweet.fields': 'created_at,author_id,public_metrics',
      });

      if (options.format === 'json') {
        console.log(JSON.stringify(results.data || [], null, 2));
      } else {
        console.log(`🔍 Search results for "${query}" (${results.data?.length || 0}):`);
        (results.data || []).forEach(tweet => {
          console.log(`  ${tweet.text}`);
          console.log(`    ❤️  ${tweet.public_metrics.like_count} | 🔄 ${tweet.public_metrics.retweet_count}`);
          console.log();
        });
      }
    } catch (error) {
      if (error.message.includes('400')) {
        console.error('❌ Search failed: This endpoint may require a paid X API tier.');
        console.error('   Free tier only supports posting tweets and account lookup.');
        console.error('   Error:', error.message);
      } else {
        console.error('❌ Failed to search:', error.message);
      }
      process.exit(1);
    }
  });

// Delete command
program
  .command('delete <id>')
  .description('Delete a tweet')
  .action(async (id) => {
    try {
      const client = initializeClient();
      
      await client.v2.deleteTweet(id);
      
      console.log('✅ Tweet deleted');
    } catch (error) {
      console.error('❌ Failed to delete tweet:', error.message);
      process.exit(1);
    }
  });

// Account info command (replaces rate-limits which isn't available in v2)
program
  .command('me')
  .description('Show current account info')
  .action(async () => {
    try {
      const client = initializeClient();
      
      const user = await getCurrentUser(client);
      
      console.log('👤 Account Info:');
      console.log(`  Name: ${user.name}`);
      console.log(`  Username: @${user.username}`);
      console.log(`  ID: ${user.id}`);
      console.log(`  Created: ${new Date(user.created_at).toLocaleDateString()}`);
      if (user.public_metrics) {
        console.log(`  Followers: ${user.public_metrics.followers_count || 0}`);
        console.log(`  Following: ${user.public_metrics.following_count || 0}`);
        console.log(`  Tweets: ${user.public_metrics.tweet_count || 0}`);
      }
      console.log(`\n  X_USER_ID=${user.id} (add this to your .env for faster mentions)`);
    } catch (error) {
      console.error('❌ Failed to fetch account info:', error.message);
      process.exit(1);
    }
  });

// Help and default
program
  .version('1.0.0')
  .description('X (Twitter) API client using OAuth 1.0a')
  .helpOption('-h, --help', 'display help for command')
  .parse(process.argv);

if (!process.argv.slice(2).length) {
  program.outputHelp();
}
