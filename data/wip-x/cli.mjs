#!/usr/bin/env node

/**
 * wip-x/cli.mjs
 * CLI for X Platform API. Sensor (read) + Actuator (write).
 */

import {
  fetch_post,
  search_recent,
  get_bookmarks,
  get_user,
  get_me,
  post_tweet,
  delete_tweet,
  bookmark_post,
  upload_media,
} from './core.mjs';

const args = process.argv.slice(2);
const command = args[0];

function flag(name) {
  const prefix = `--${name}=`;
  const found = args.find(a => a.startsWith(prefix));
  return found ? found.slice(prefix.length) : null;
}

function usage() {
  console.log(`wip-x ... X Platform API. Sensor + Actuator.

Sensor (read):
  wip-x fetch <url_or_id>                   Fetch a single post
  wip-x search <query> [--max=10]           Search recent tweets
  wip-x bookmarks [--max=20]                Get your bookmarks
  wip-x user <username>                      Get user profile
  wip-x me                                   Get your profile

Actuator (write):
  wip-x post <text> [--reply-to=id] [--media=file] [--quote=id]
  wip-x delete <id>                          Delete a tweet
  wip-x bookmark <tweet_id>                  Bookmark a post
  wip-x upload <file>                        Upload media, get media ID`);
}

async function main() {
  if (!command || command === '--help' || command === '-h') {
    usage();
    process.exit(0);
  }

  try {
    switch (command) {
      case 'fetch': {
        const target = args[1];
        if (!target) { console.error('Usage: wip-x fetch <url_or_id>'); process.exit(1); }
        const result = await fetch_post({ id_or_url: target });
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'search': {
        const query = args[1];
        if (!query) { console.error('Usage: wip-x search <query>'); process.exit(1); }
        const max = flag('max') ? parseInt(flag('max'), 10) : undefined;
        const result = await search_recent({ query, max_results: max });
        if (result.data) {
          for (const tweet of result.data) {
            const author = result.includes?.users?.find(u => u.id === tweet.author_id);
            console.log(`@${author?.username || tweet.author_id}: ${tweet.text}`);
            console.log(`  ${tweet.created_at}  id:${tweet.id}`);
            console.log();
          }
          console.log(`${result.data.length} results`);
        } else {
          console.log('No results.');
        }
        break;
      }

      case 'bookmarks': {
        const max = flag('max') ? parseInt(flag('max'), 10) : undefined;
        const result = await get_bookmarks({ max_results: max });
        if (result.data) {
          for (const tweet of result.data) {
            const author = result.includes?.users?.find(u => u.id === tweet.author_id);
            console.log(`@${author?.username || tweet.author_id}: ${tweet.text}`);
            console.log(`  ${tweet.created_at}  id:${tweet.id}`);
            console.log();
          }
          console.log(`${result.data.length} bookmarks`);
        } else {
          console.log('No bookmarks.');
        }
        break;
      }

      case 'user': {
        const target = args[1];
        if (!target) { console.error('Usage: wip-x user <username>'); process.exit(1); }
        const result = await get_user({ username_or_id: target });
        if (result.data) {
          const u = result.data;
          console.log(`@${u.username} (${u.name})`);
          if (u.description) console.log(u.description);
          if (u.public_metrics) {
            console.log(`Followers: ${u.public_metrics.followers_count}  Following: ${u.public_metrics.following_count}  Posts: ${u.public_metrics.tweet_count}`);
          }
          console.log(`ID: ${u.id}  Created: ${u.created_at}`);
        } else {
          console.log('User not found.');
        }
        break;
      }

      case 'me': {
        const result = await get_me();
        if (result.data) {
          const u = result.data;
          console.log(`@${u.username} (${u.name})`);
          if (u.description) console.log(u.description);
          if (u.public_metrics) {
            console.log(`Followers: ${u.public_metrics.followers_count}  Following: ${u.public_metrics.following_count}  Posts: ${u.public_metrics.tweet_count}`);
          }
          console.log(`ID: ${u.id}`);
        }
        break;
      }

      case 'post': {
        const text = args[1];
        if (!text) { console.error('Usage: wip-x post <text>'); process.exit(1); }
        const replyTo = flag('reply-to');
        const quote = flag('quote');
        const mediaFile = flag('media');

        let mediaIds;
        if (mediaFile) {
          const upload = await upload_media({ file_path: mediaFile });
          if (upload.data?.id) mediaIds = [upload.data.id];
        }

        const result = await post_tweet({ text, reply_to: replyTo, media_ids: mediaIds, quote_tweet_id: quote });
        if (result.data) {
          console.log(`Posted: https://x.com/i/status/${result.data.id}`);
        } else {
          console.error('Failed to post:', result.errors);
        }
        break;
      }

      case 'delete': {
        const id = args[1];
        if (!id) { console.error('Usage: wip-x delete <id>'); process.exit(1); }
        const result = await delete_tweet({ id });
        console.log(result.data?.deleted ? 'Deleted.' : 'Failed to delete.');
        break;
      }

      case 'bookmark': {
        const tweetId = args[1];
        if (!tweetId) { console.error('Usage: wip-x bookmark <tweet_id>'); process.exit(1); }
        const result = await bookmark_post({ tweet_id: tweetId });
        console.log(result.data?.bookmarked ? 'Bookmarked.' : 'Failed to bookmark.');
        break;
      }

      case 'upload': {
        const file = args[1];
        if (!file) { console.error('Usage: wip-x upload <file>'); process.exit(1); }
        const result = await upload_media({ file_path: file });
        if (result.data) {
          console.log(`Media ID: ${result.data.id}`);
        } else {
          console.error('Upload failed:', result.errors);
        }
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        usage();
        process.exit(1);
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
