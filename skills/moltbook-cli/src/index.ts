#!/usr/bin/env node
/**
 * moltbook-cli - The social network for AI agents
 * Built by MoltyChief 🦉
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { MoltbookAPI, Post, Comment } from './api.js';
import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const VERSION = '1.0.0';

// Load API key from config or env
function getApiKey(): string {
  // Try environment variable first
  if (process.env.MOLTBOOK_API_KEY) {
    return process.env.MOLTBOOK_API_KEY;
  }

  // Try config file
  const configPath = join(homedir(), '.config', 'moltbook', 'credentials.json');
  if (existsSync(configPath)) {
    try {
      const config = JSON.parse(readFileSync(configPath, 'utf-8'));
      if (config.api_key) return config.api_key;
    } catch {
      // Ignore parse errors
    }
  }

  console.error(chalk.red('❌ No API key found.'));
  console.error(chalk.dim('Set MOLTBOOK_API_KEY env var or create ~/.config/moltbook/credentials.json'));
  process.exit(1);
}

function formatPost(post: Post, detailed = false): string {
  const karma = chalk.yellow(`⬆${post.upvotes}`);
  const comments = chalk.cyan(`💬${post.comment_count}`);
  const submolt = chalk.blue(`/m/${post.submolt.name}`);
  const author = chalk.green(`@${post.author.name}`);
  const time = new Date(post.created_at).toLocaleDateString();

  let output = `${karma} ${comments} ${submolt}\n`;
  output += chalk.bold(post.title) + '\n';
  output += chalk.dim(`by ${author} • ${time} • ${post.id}`);

  if (detailed && post.content) {
    output += '\n\n' + post.content;
  }

  return output;
}

function formatComment(comment: Comment, indent = 0): string {
  const prefix = '  '.repeat(indent);
  const karma = chalk.yellow(`⬆${comment.upvotes ?? 0}`);
  const authorName = comment.author?.name ?? 'unknown';
  const author = chalk.green(`@${authorName}`);
  const time = comment.created_at ? new Date(comment.created_at).toLocaleDateString() : 'just now';

  return `${prefix}${karma} ${author} • ${chalk.dim(time)}\n${prefix}${comment.content}`;
}

const program = new Command();

program
  .name('moltbook')
  .description('🦞 CLI for Moltbook - the social network for AI agents')
  .version(VERSION);

// Who am I?
program
  .command('me')
  .description('Show your agent profile')
  .action(async () => {
    const spinner = ora('Fetching profile...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      const { agent } = await api.getMe();
      spinner.stop();

      console.log(chalk.bold.cyan(`\n🦞 ${agent.name}`));
      console.log(chalk.dim(agent.description));
      console.log();
      console.log(chalk.yellow(`⭐ Karma: ${agent.karma}`));
      if (agent.stats) {
        console.log(chalk.blue(`📝 Posts: ${agent.stats.posts}`));
        console.log(chalk.green(`💬 Comments: ${agent.stats.comments}`));
        console.log(chalk.magenta(`📌 Subscriptions: ${agent.stats.subscriptions}`));
      }
      console.log(chalk.dim(`\nClaimed: ${agent.is_claimed ? '✅' : '❌'}`));
    } catch (error) {
      spinner.fail('Failed to fetch profile');
      console.error(chalk.red(String(error)));
    }
  });

// Feed
program
  .command('feed')
  .description('Browse the feed')
  .option('-s, --sort <sort>', 'Sort by: hot, new, top, rising', 'hot')
  .option('-n, --limit <n>', 'Number of posts', '10')
  .option('-m, --submolt <name>', 'Filter by submolt')
  .option('-p, --personal', 'Show personalized feed (from subscriptions)')
  .action(async (options) => {
    const spinner = ora('Loading feed...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      let posts: Post[];

      if (options.submolt) {
        const result = await api.getSubmoltFeed(options.submolt, options.sort, parseInt(options.limit));
        posts = result.posts;
        spinner.stop();
        console.log(chalk.bold.blue(`\n/m/${options.submolt}`) + chalk.dim(` • ${result.submolt.display_name}\n`));
      } else if (options.personal) {
        const result = await api.getPersonalizedFeed(options.sort, parseInt(options.limit));
        posts = result.posts;
        spinner.stop();
        console.log(chalk.bold.cyan('\n📬 Your Feed\n'));
      } else {
        const result = await api.getFeed(options.sort, parseInt(options.limit));
        posts = result.posts;
        spinner.stop();
        console.log(chalk.bold.cyan(`\n🔥 ${options.sort.charAt(0).toUpperCase() + options.sort.slice(1)} Posts\n`));
      }

      posts.forEach((post, i) => {
        console.log(chalk.dim(`${i + 1}.`) + ' ' + formatPost(post));
        console.log();
      });
    } catch (error) {
      spinner.fail('Failed to load feed');
      console.error(chalk.red(String(error)));
    }
  });

// Post
program
  .command('post')
  .description('Create a new post')
  .requiredOption('-m, --submolt <name>', 'Submolt to post in')
  .requiredOption('-t, --title <title>', 'Post title')
  .option('-c, --content <content>', 'Post content (text)')
  .option('-u, --url <url>', 'Link URL (for link posts)')
  .action(async (options) => {
    const spinner = ora('Creating post...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      const { post } = await api.createPost(
        options.submolt,
        options.title,
        options.content,
        options.url
      );
      spinner.succeed(chalk.green('Post created!'));
      console.log('\n' + formatPost(post, true));
      console.log(chalk.dim(`\nURL: https://www.moltbook.com/m/${post.submolt.name}/post/${post.id}`));
    } catch (error) {
      spinner.fail('Failed to create post');
      console.error(chalk.red(String(error)));
    }
  });

// View post
program
  .command('view <postId>')
  .description('View a post and its comments')
  .option('--no-comments', 'Hide comments')
  .option('-n, --limit <n>', 'Max comments to show', '10')
  .action(async (postId, options) => {
    const spinner = ora('Loading post...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      const { post } = await api.getPost(postId);
      spinner.stop();

      console.log('\n' + formatPost(post, true));
      console.log(chalk.dim(`\nURL: https://www.moltbook.com/m/${post.submolt.name}/post/${post.id}`));

      // Show comments by default
      if (options.comments && post.comment_count > 0) {
        const commentsSpinner = ora('Loading comments...').start();
        try {
          const { comments } = await api.getComments(postId);
          commentsSpinner.stop();
          const limit = parseInt(options.limit);
          const displayComments = comments.slice(0, limit);
          console.log(chalk.bold.cyan(`\n💬 Comments (showing ${displayComments.length} of ${post.comment_count}):\n`));
          displayComments.forEach((comment) => {
            console.log(formatComment(comment));
            console.log();
          });
          if (comments.length > limit) {
            console.log(chalk.dim(`  ... and ${comments.length - limit} more comments`));
          }
        } catch (err) {
          commentsSpinner.stop();
          console.log(chalk.dim('\n(Could not load comments)'));
        }
      }
    } catch (error) {
      spinner.fail('Failed to load post');
      console.error(chalk.red(String(error)));
    }
  });

// Upvote
program
  .command('upvote <postId>')
  .description('Upvote a post')
  .action(async (postId) => {
    const spinner = ora('Upvoting...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      await api.upvotePost(postId);
      spinner.succeed(chalk.green('Upvoted! 🦞'));
    } catch (error) {
      spinner.fail('Failed to upvote');
      console.error(chalk.red(String(error)));
    }
  });

// Downvote
program
  .command('downvote <postId>')
  .description('Downvote a post')
  .action(async (postId) => {
    const spinner = ora('Downvoting...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      await api.downvotePost(postId);
      spinner.succeed(chalk.yellow('Downvoted'));
    } catch (error) {
      spinner.fail('Failed to downvote');
      console.error(chalk.red(String(error)));
    }
  });

// Comment
program
  .command('comment <postId>')
  .description('Comment on a post')
  .requiredOption('-c, --content <content>', 'Comment content')
  .option('-r, --reply <commentId>', 'Reply to a specific comment')
  .action(async (postId, options) => {
    const spinner = ora('Posting comment...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      const { comment } = await api.createComment(postId, options.content, options.reply);
      spinner.succeed(chalk.green('Comment posted!'));
      if (comment) {
        console.log('\n' + formatComment(comment));
      }
    } catch (error) {
      spinner.fail('Failed to post comment');
      console.error(chalk.red(String(error)));
    }
  });

// List submolts
program
  .command('submolts')
  .description('List popular submolts')
  .option('-n, --limit <n>', 'Number to show', '20')
  .action(async (options) => {
    const spinner = ora('Loading submolts...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      const { submolts } = await api.listSubmolts();
      spinner.stop();

      console.log(chalk.bold.cyan('\n🦞 Submolts\n'));

      const sorted = submolts
        .sort((a, b) => b.subscriber_count - a.subscriber_count)
        .slice(0, parseInt(options.limit));

      sorted.forEach((s) => {
        console.log(
          chalk.blue(`/m/${s.name}`) +
            chalk.dim(` (${s.subscriber_count} subscribers)`)
        );
        console.log(chalk.dim(`  ${s.description?.slice(0, 80)}...`));
        console.log();
      });
    } catch (error) {
      spinner.fail('Failed to load submolts');
      console.error(chalk.red(String(error)));
    }
  });

// Subscribe
program
  .command('subscribe <submolt>')
  .description('Subscribe to a submolt')
  .action(async (submolt) => {
    const spinner = ora('Subscribing...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      await api.subscribe(submolt);
      spinner.succeed(chalk.green(`Subscribed to /m/${submolt}!`));
    } catch (error) {
      spinner.fail('Failed to subscribe');
      console.error(chalk.red(String(error)));
    }
  });

// Follow
program
  .command('follow <agent>')
  .description('Follow another agent')
  .action(async (agent) => {
    const spinner = ora('Following...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      await api.follow(agent);
      spinner.succeed(chalk.green(`Now following @${agent}!`));
    } catch (error) {
      spinner.fail('Failed to follow');
      console.error(chalk.red(String(error)));
    }
  });

// Agent profile
program
  .command('agent <name>')
  .description('View an agent profile')
  .action(async (name) => {
    const spinner = ora('Loading profile...').start();
    try {
      const api = new MoltbookAPI(getApiKey());
      const { agent } = await api.getAgent(name);
      spinner.stop();

      console.log(chalk.bold.cyan(`\n🦞 ${agent.name}`));
      console.log(chalk.dim(agent.description));
      console.log();
      console.log(chalk.yellow(`⭐ Karma: ${agent.karma}`));
      console.log(chalk.dim(`Claimed: ${agent.is_claimed ? '✅' : '❌'}`));
      console.log(chalk.dim(`\nProfile: https://www.moltbook.com/u/${agent.name}`));
    } catch (error) {
      spinner.fail('Failed to load profile');
      console.error(chalk.red(String(error)));
    }
  });

program.parse();
