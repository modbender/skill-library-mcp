#!/usr/bin/env node

/**
 * Arena Agent CLI
 * 
 * Usage:
 *   arena-agent daemon              Start 24/7 monitoring daemon
 *   arena-agent notifications       Show recent notifications
 *   arena-agent post "content"      Create a new post
 *   arena-agent reply <id> "text"   Reply to a thread
 *   arena-agent like <threadId>     Like a thread
 *   arena-agent trending            Show trending posts
 *   arena-agent feed                Show your feed
 *   arena-agent status              Show agent status
 *   arena-agent process-mentions    Process pending mentions (one-shot)
 */

const path = require('path');
const fs = require('fs');

// Load .env if exists
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  for (const line of envContent.split('\n')) {
    const [key, ...valueParts] = line.split('=');
    if (key && valueParts.length) {
      process.env[key.trim()] = valueParts.join('=').trim().replace(/^["']|["']$/g, '');
    }
  }
}

// ============================================================================
// Simple API Client (JavaScript version for CLI)
// ============================================================================

class ArenaApiClient {
  constructor(apiKey, baseUrl = 'https://api.starsarena.com/agents') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'X-API-Key': this.apiKey,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Arena API error ${response.status}: ${error}`);
    }

    return response.json();
  }

  async getMe() {
    const result = await this.request('/user/me');
    return result.user;
  }

  async createThread(content, parentThreadId) {
    const body = { content, files: [], privacyType: 0 };
    if (parentThreadId) body.parentThreadId = parentThreadId;
    return this.request('/threads', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getNotifications(page = 1, pageSize = 20) {
    return this.request(`/notifications?page=${page}&pageSize=${pageSize}`);
  }

  async getUnseenCount() {
    const result = await this.request('/notifications/unseen');
    return { unseenCount: result.count };
  }

  async markNotificationSeen(notificationId) {
    return this.request(`/notifications/seen?notificationId=${notificationId}`);
  }

  async markAllNotificationsSeen() {
    return this.request('/notifications/seen/all');
  }

  async getTrending(page = 1, pageSize = 20) {
    return this.request(`/threads/feed/trendingPosts?page=${page}&pageSize=${pageSize}`);
  }

  async getMyFeed(page = 1, pageSize = 20) {
    return this.request(`/threads/feed/my?page=${page}&pageSize=${pageSize}`);
  }

  async likeThread(threadId) {
    return this.request('/threads/like', {
      method: 'POST',
      body: JSON.stringify({ threadId }),
    });
  }
}

// ============================================================================
// State Manager
// ============================================================================

class StateManager {
  constructor(statePath) {
    this.statePath = statePath;
    this.state = this.loadState();
  }

  loadState() {
    const defaultState = {
      processedNotifications: [],
      lastPollTime: 0,
      lastPostTime: 0,
      postsToday: 0,
      dailyResetTime: this.getStartOfDay(),
      rateLimits: {
        postsRemaining: 3,
        postsResetAt: Date.now() + 3600000,
      },
    };

    try {
      if (fs.existsSync(this.statePath)) {
        const data = fs.readFileSync(this.statePath, 'utf-8');
        const loaded = JSON.parse(data);
        return { ...defaultState, ...loaded };
      }
    } catch (e) {
      console.error('Failed to load state:', e.message);
    }

    return defaultState;
  }

  saveState() {
    try {
      const dir = path.dirname(this.statePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.statePath, JSON.stringify(this.state, null, 2), { mode: 0o600 });
    } catch (e) {
      console.error('Failed to save state:', e.message);
    }
  }

  getStartOfDay() {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  }

  isNotificationProcessed(id) {
    return this.state.processedNotifications.includes(id);
  }

  markNotificationProcessed(id) {
    if (!this.state.processedNotifications.includes(id)) {
      this.state.processedNotifications.push(id);
      if (this.state.processedNotifications.length > 1000) {
        this.state.processedNotifications = this.state.processedNotifications.slice(-1000);
      }
      this.saveState();
    }
  }

  updateLastPollTime() {
    this.state.lastPollTime = Date.now();
    this.saveState();
  }

  canPost() {
    const startOfDay = this.getStartOfDay();
    if (startOfDay > this.state.dailyResetTime) {
      this.state.dailyResetTime = startOfDay;
      this.state.postsToday = 0;
    }

    if (Date.now() > this.state.rateLimits.postsResetAt) {
      this.state.rateLimits.postsRemaining = 3;
      this.state.rateLimits.postsResetAt = Date.now() + 3600000;
    }

    return this.state.rateLimits.postsRemaining > 0;
  }

  recordPost() {
    this.state.lastPostTime = Date.now();
    this.state.postsToday++;
    this.state.rateLimits.postsRemaining--;
    this.saveState();
  }

  getState() {
    return { ...this.state };
  }
}

// ============================================================================
// Content Generator
// ============================================================================

function generateReply(notification) {
  const user = notification.user;
  const threadContent = notification.thread?.content || '';
  
  const templates = [
    `Hey @${user.handle}! Thanks for the mention 🙌`,
    `@${user.handle} Great point! Love the discussion here 💡`,
    `Appreciate you @${user.handle}! Let's keep building 🚀`,
    `@${user.handle} Interesting perspective! What do you think about the long-term implications?`,
    `Thanks for bringing this up @${user.handle}! 🎯`,
  ];

  if (threadContent.toLowerCase().includes('ai') || threadContent.toLowerCase().includes('agent')) {
    return `@${user.handle} AI agents are definitely the future! Excited to be part of this space 🤖✨`;
  }
  
  if (threadContent.toLowerCase().includes('defi') || threadContent.toLowerCase().includes('crypto')) {
    return `@${user.handle} The crypto space keeps evolving! Always bullish on innovation 📈`;
  }

  return templates[Math.floor(Math.random() * templates.length)];
}

// ============================================================================
// CLI Commands
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const apiKey = process.env.ARENA_API_KEY;
  if (!apiKey) {
    console.error('Error: ARENA_API_KEY environment variable is required');
    console.error('Set it in .env file or export ARENA_API_KEY=ak_live_...');
    process.exit(1);
  }

  const client = new ArenaApiClient(apiKey);
  const statePath = process.env.ARENA_STATE_PATH || path.join(process.env.HOME || '', '.arena-agent-state.json');
  const state = new StateManager(statePath);

  try {
    switch (command) {
      case 'daemon': {
        console.log('Arena Agent Daemon');
        console.log('==================');
        
        const interval = parseInt(args[1] || process.env.ARENA_POLL_INTERVAL || '180000');
        const autoReply = !args.includes('--no-auto-reply');
        const autoPost = !args.includes('--no-auto-post');
        
        const me = await client.getMe();
        console.log(`Agent: @${me.handle} (${me.userName})`);
        console.log(`Poll interval: ${interval}ms`);
        console.log(`Auto-reply: ${autoReply}`);
        console.log(`Auto-post: ${autoPost}`);
        console.log('');
        
        const runCycle = async () => {
          console.log(`[${new Date().toISOString()}] Polling...`);
          
          // Process notifications
          const { notifications } = await client.getNotifications(1, 50);
          let processed = 0;
          let replied = 0;
          
          for (const n of notifications) {
            if (state.isNotificationProcessed(n.id)) continue;
            
            processed++;
            console.log(`  [${n.type}] @${n.user.handle}: ${n.message}`);
            
            if (autoReply && ['mention', 'reply', 'quote'].includes(n.type) && n.threadId) {
              if (state.canPost()) {
                try {
                  const reply = generateReply(n);
                  await client.createThread(reply, n.threadId);
                  state.recordPost();
                  replied++;
                  console.log(`    → Replied: ${reply}`);
                } catch (e) {
                  console.error(`    → Reply failed: ${e.message}`);
                }
              }
            }
            
            state.markNotificationProcessed(n.id);
            await client.markNotificationSeen(n.id);
          }
          
          console.log(`  Processed: ${processed}, Replied: ${replied}`);
          state.updateLastPollTime();
        };
        
        // Initial run
        await runCycle();
        
        // Schedule
        setInterval(runCycle, interval);
        
        // Keep alive
        process.on('SIGINT', () => {
          console.log('\nShutting down...');
          process.exit(0);
        });
        
        // Keep process running
        await new Promise(() => {});
        break;
      }

      case 'notifications': {
        const { notifications } = await client.getNotifications(1, 20);
        const { unseenCount } = await client.getUnseenCount();
        
        console.log(`Notifications (${unseenCount} unseen)`);
        console.log('='.repeat(40));
        
        for (const n of notifications) {
          const seen = n.isSeen ? ' ' : '●';
          const time = new Date(n.createdAt).toLocaleString();
          console.log(`${seen} [${n.type}] @${n.user.handle} - ${n.message}`);
          console.log(`  ${time}`);
          if (n.threadId) console.log(`  Thread: ${n.threadId}`);
          console.log('');
        }
        break;
      }

      case 'post': {
        const content = args.slice(1).join(' ');
        if (!content) {
          console.error('Usage: arena-agent post "Your content here"');
          process.exit(1);
        }
        
        if (!state.canPost()) {
          console.error('Rate limited. Try again later.');
          process.exit(1);
        }
        
        const result = await client.createThread(content);
        state.recordPost();
        console.log('Posted successfully!');
        console.log(`Thread ID: ${result.thread.id}`);
        break;
      }

      case 'reply': {
        const threadId = args[1];
        const content = args.slice(2).join(' ');
        
        if (!threadId || !content) {
          console.error('Usage: arena-agent reply <threadId> "Your reply"');
          process.exit(1);
        }
        
        if (!state.canPost()) {
          console.error('Rate limited. Try again later.');
          process.exit(1);
        }
        
        const result = await client.createThread(content, threadId);
        state.recordPost();
        console.log('Replied successfully!');
        console.log(`Reply ID: ${result.thread.id}`);
        break;
      }

      case 'like': {
        const threadId = args[1];
        if (!threadId) {
          console.error('Usage: arena-agent like <threadId>');
          process.exit(1);
        }
        
        await client.likeThread(threadId);
        console.log('Liked!');
        break;
      }

      case 'trending': {
        const { threads } = await client.getTrending(1, 10);
        
        console.log('Trending Posts');
        console.log('='.repeat(40));
        
        for (const t of threads) {
          console.log(`@${t.user?.handle || 'unknown'}: ${t.content.substring(0, 100)}...`);
          console.log(`  ❤️ ${t.likeCount} | 🔄 ${t.repostCount} | 💬 ${t.replyCount}`);
          console.log(`  ID: ${t.id}`);
          console.log('');
        }
        break;
      }

      case 'feed': {
        const { threads } = await client.getMyFeed(1, 10);
        
        console.log('Your Feed');
        console.log('='.repeat(40));
        
        for (const t of threads) {
          console.log(`@${t.user?.handle || 'unknown'}: ${t.content.substring(0, 100)}...`);
          console.log(`  ❤️ ${t.likeCount} | 🔄 ${t.repostCount} | 💬 ${t.replyCount}`);
          console.log(`  ID: ${t.id}`);
          console.log('');
        }
        break;
      }

      case 'status': {
        const me = await client.getMe();
        const { unseenCount } = await client.getUnseenCount();
        const currentState = state.getState();
        
        console.log('Arena Agent Status');
        console.log('='.repeat(40));
        console.log(`Agent: @${me.handle} (${me.userName})`);
        console.log(`Followers: ${me.followerCount}`);
        console.log(`Following: ${me.followingsCount}`);
        console.log('');
        console.log('Notifications:');
        console.log(`  Unseen: ${unseenCount}`);
        console.log(`  Processed: ${currentState.processedNotifications.length}`);
        console.log('');
        console.log('Rate Limits:');
        console.log(`  Posts remaining (hour): ${currentState.rateLimits.postsRemaining}`);
        console.log(`  Posts today: ${currentState.postsToday}`);
        console.log(`  Resets at: ${new Date(currentState.rateLimits.postsResetAt).toLocaleString()}`);
        break;
      }

      case 'process-mentions': {
        console.log('Processing mentions...');
        
        const { notifications } = await client.getNotifications(1, 50);
        let processed = 0;
        let replied = 0;
        
        for (const n of notifications) {
          if (state.isNotificationProcessed(n.id)) continue;
          if (!['mention', 'reply', 'quote'].includes(n.type)) {
            state.markNotificationProcessed(n.id);
            continue;
          }
          
          processed++;
          console.log(`[${n.type}] @${n.user.handle}: ${n.message}`);
          
          if (n.threadId && state.canPost()) {
            try {
              const reply = generateReply(n);
              await client.createThread(reply, n.threadId);
              state.recordPost();
              replied++;
              console.log(`  → Replied: ${reply}`);
            } catch (e) {
              console.error(`  → Failed: ${e.message}`);
            }
          }
          
          state.markNotificationProcessed(n.id);
          await client.markNotificationSeen(n.id);
        }
        
        console.log(`Done. Processed: ${processed}, Replied: ${replied}`);
        break;
      }

      case 'help':
      default: {
        console.log(`
Arena Agent CLI - Autonomous AI agent for Arena.social

Usage:
  arena-agent daemon              Start 24/7 monitoring daemon
  arena-agent notifications       Show recent notifications  
  arena-agent post "content"      Create a new post
  arena-agent reply <id> "text"   Reply to a thread
  arena-agent like <threadId>     Like a thread
  arena-agent trending            Show trending posts
  arena-agent feed                Show your feed
  arena-agent status              Show agent status
  arena-agent process-mentions    Process pending mentions (one-shot)
  arena-agent help                Show this help

Environment Variables:
  ARENA_API_KEY         Required. Your Arena agent API key
  ARENA_POLL_INTERVAL   Poll interval in ms (default: 180000)
  ARENA_AUTO_REPLY      Enable auto-reply (default: true)
  ARENA_AUTO_POST       Enable auto-post (default: true)
  ARENA_STATE_PATH      State file path (default: ~/.arena-agent-state.json)

Daemon Options:
  --no-auto-reply       Disable automatic replies
  --no-auto-post        Disable scheduled posts
`);
        break;
      }
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

main();
