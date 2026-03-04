/**
 * Arena Agent - Autonomous AI agent for Arena.social
 * 
 * Features:
 * - 24/7 notification monitoring
 * - Auto-reply to mentions/tags
 * - Scheduled contextual posts
 * - Rate limit aware
 * - State persistence
 */

import * as fs from 'fs';
import * as path from 'path';

// ============================================================================
// Types
// ============================================================================

interface ArenaUser {
  id: string;
  handle: string;
  userName: string;
  profilePicture?: string;
  bio?: string;
  followerCount?: number;
  followingCount?: number;
  address?: string;
}

interface ArenaThread {
  id: string;
  content: string;
  userId: string;
  user?: ArenaUser;
  createdAt: string;
  likeCount: number;
  repostCount: number;
  replyCount: number;
  parentThreadId?: string;
  quotedThreadId?: string;
  isLiked?: boolean;
  isReposted?: boolean;
}

interface ArenaNotification {
  id: string;
  type: 'like' | 'repost' | 'reply' | 'follow' | 'mention' | 'quote';
  message: string;
  userId: string;
  user: ArenaUser;
  threadId?: string;
  thread?: ArenaThread;
  isSeen: boolean;
  createdAt: string;
}

interface AgentState {
  processedNotifications: string[];
  lastPollTime: number;
  lastPostTime: number;
  postsToday: number;
  dailyResetTime: number;
  rateLimits: {
    postsRemaining: number;
    postsResetAt: number;
  };
}

interface AgentConfig {
  apiKey: string;
  pollInterval: number;
  autoReply: boolean;
  autoPost: boolean;
  postsPerDay: number;
  personality: string;
  statePath: string;
  baseUrl: string;
}

interface PaginatedResponse<T> {
  pagination: {
    page: number;
    pageSize: number;
    totalPages: number;
    totalItems: number;
  };
}

// ============================================================================
// Arena API Client
// ============================================================================

export class ArenaApiClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl: string = 'https://api.starsarena.com/agents') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'X-API-Key': this.apiKey,
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Arena API error ${response.status}: ${error}`);
    }

    return response.json();
  }

  // User endpoints
  async getMe(): Promise<ArenaUser> {
    return this.request<ArenaUser>('/user/me');
  }

  async getUserByHandle(handle: string): Promise<{ user: ArenaUser }> {
    return this.request<{ user: ArenaUser }>(`/user/handle?handle=${encodeURIComponent(handle)}`);
  }

  async searchUsers(query: string): Promise<ArenaUser[]> {
    return this.request<ArenaUser[]>(`/user/search?searchString=${encodeURIComponent(query)}`);
  }

  // Thread endpoints
  async createThread(content: string, parentThreadId?: string): Promise<{ thread: ArenaThread }> {
    const body: Record<string, unknown> = { content, files: [], privacyType: 0 };
    if (parentThreadId) {
      body.parentThreadId = parentThreadId;
    }
    return this.request<{ thread: ArenaThread }>('/threads', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getThread(threadId: string): Promise<{ thread: ArenaThread }> {
    return this.request<{ thread: ArenaThread }>(`/threads?threadId=${threadId}`);
  }

  async getMyFeed(page: number = 1, pageSize: number = 20): Promise<{ threads: ArenaThread[] } & PaginatedResponse<ArenaThread>> {
    return this.request(`/threads/feed/my?page=${page}&pageSize=${pageSize}`);
  }

  async getTrending(page: number = 1, pageSize: number = 20): Promise<{ threads: ArenaThread[] } & PaginatedResponse<ArenaThread>> {
    return this.request(`/threads/feed/trendingPosts?page=${page}&pageSize=${pageSize}`);
  }

  async getUserThreads(userId: string, page: number = 1): Promise<{ threads: ArenaThread[] } & PaginatedResponse<ArenaThread>> {
    return this.request(`/threads/feed/user?userId=${userId}&page=${page}`);
  }

  async likeThread(threadId: string): Promise<{ success: boolean; likeCount: number }> {
    return this.request('/threads/like', {
      method: 'POST',
      body: JSON.stringify({ threadId }),
    });
  }

  async unlikeThread(threadId: string): Promise<{ success: boolean; likeCount: number }> {
    return this.request('/threads/unlike', {
      method: 'POST',
      body: JSON.stringify({ threadId }),
    });
  }

  async repostThread(threadId: string): Promise<{ success: boolean; repost: unknown }> {
    return this.request('/threads/repost', {
      method: 'POST',
      body: JSON.stringify({ threadId }),
    });
  }

  async quoteThread(threadId: string, content: string): Promise<{ thread: ArenaThread }> {
    return this.request('/threads/quote', {
      method: 'POST',
      body: JSON.stringify({ threadId, content, files: [] }),
    });
  }

  // Notification endpoints
  async getNotifications(page: number = 1, pageSize: number = 20): Promise<{ notifications: ArenaNotification[] } & PaginatedResponse<ArenaNotification>> {
    return this.request(`/notifications?page=${page}&pageSize=${pageSize}`);
  }

  async getUnseenCount(): Promise<{ unseenCount: number; lastChecked: string }> {
    return this.request('/notifications/unseen');
  }

  async markNotificationSeen(notificationId: string): Promise<{ success: boolean }> {
    return this.request(`/notifications/seen?notificationId=${notificationId}`);
  }

  async markAllNotificationsSeen(): Promise<{ success: boolean; markedCount: number }> {
    return this.request('/notifications/seen/all');
  }

  // Follow endpoints
  async followUser(userId: string): Promise<{ success: boolean }> {
    return this.request('/follow/follow', {
      method: 'POST',
      body: JSON.stringify({ userIdToFollow: userId }),
    });
  }

  async unfollowUser(userId: string): Promise<{ success: boolean }> {
    return this.request('/follow/unfollow', {
      method: 'POST',
      body: JSON.stringify({ userIdToUnfollow: userId }),
    });
  }

  async getFollowers(userId: string, page: number = 1): Promise<{ followers: unknown[] } & PaginatedResponse<unknown>> {
    return this.request(`/follow/followers/list?followersOfUserId=${userId}&pageNumber=${page}`);
  }

  async getFollowing(userId: string, page: number = 1): Promise<{ following: unknown[] } & PaginatedResponse<unknown>> {
    return this.request(`/follow/following/list?followingUserId=${userId}&pageNumber=${page}`);
  }
}

// ============================================================================
// State Manager
// ============================================================================

export class StateManager {
  private statePath: string;
  private state: AgentState;

  constructor(statePath: string) {
    this.statePath = statePath;
    this.state = this.loadState();
  }

  private loadState(): AgentState {
    const defaultState: AgentState = {
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
      console.error('Failed to load state:', e);
    }

    return defaultState;
  }

  private saveState(): void {
    try {
      const dir = path.dirname(this.statePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.statePath, JSON.stringify(this.state, null, 2), { mode: 0o600 });
    } catch (e) {
      console.error('Failed to save state:', e);
    }
  }

  private getStartOfDay(): number {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  }

  isNotificationProcessed(id: string): boolean {
    return this.state.processedNotifications.includes(id);
  }

  markNotificationProcessed(id: string): void {
    if (!this.state.processedNotifications.includes(id)) {
      this.state.processedNotifications.push(id);
      // Keep only last 1000 notifications
      if (this.state.processedNotifications.length > 1000) {
        this.state.processedNotifications = this.state.processedNotifications.slice(-1000);
      }
      this.saveState();
    }
  }

  updateLastPollTime(): void {
    this.state.lastPollTime = Date.now();
    this.saveState();
  }

  canPost(): boolean {
    // Check daily reset
    const startOfDay = this.getStartOfDay();
    if (startOfDay > this.state.dailyResetTime) {
      this.state.dailyResetTime = startOfDay;
      this.state.postsToday = 0;
    }

    // Check hourly rate limit
    if (Date.now() > this.state.rateLimits.postsResetAt) {
      this.state.rateLimits.postsRemaining = 3;
      this.state.rateLimits.postsResetAt = Date.now() + 3600000;
    }

    return this.state.rateLimits.postsRemaining > 0;
  }

  recordPost(): void {
    this.state.lastPostTime = Date.now();
    this.state.postsToday++;
    this.state.rateLimits.postsRemaining--;
    this.saveState();
  }

  getPostsToday(): number {
    const startOfDay = this.getStartOfDay();
    if (startOfDay > this.state.dailyResetTime) {
      return 0;
    }
    return this.state.postsToday;
  }

  getLastPostTime(): number {
    return this.state.lastPostTime;
  }

  getState(): AgentState {
    return { ...this.state };
  }
}

// ============================================================================
// Content Generator
// ============================================================================

export class ContentGenerator {
  private personality: string;

  constructor(personality: string) {
    this.personality = personality;
  }

  async generateReply(notification: ArenaNotification, thread?: ArenaThread): Promise<string> {
    const user = notification.user;
    const threadContent = thread?.content || notification.thread?.content || '';
    
    // Simple contextual reply generation
    // In production, this would call an LLM
    const templates = [
      `Hey @${user.handle}! Thanks for the mention 🙌`,
      `@${user.handle} Great point! Love the discussion here 💡`,
      `Appreciate you @${user.handle}! Let's keep building 🚀`,
      `@${user.handle} Interesting perspective! What do you think about the long-term implications?`,
      `Thanks for bringing this up @${user.handle}! 🎯`,
    ];

    // Add context-aware variations
    if (threadContent.toLowerCase().includes('ai') || threadContent.toLowerCase().includes('agent')) {
      return `@${user.handle} AI agents are definitely the future! Excited to be part of this space 🤖✨`;
    }
    
    if (threadContent.toLowerCase().includes('defi') || threadContent.toLowerCase().includes('crypto')) {
      return `@${user.handle} The crypto space keeps evolving! Always bullish on innovation 📈`;
    }

    return templates[Math.floor(Math.random() * templates.length)];
  }

  async generatePost(context: { trending?: ArenaThread[]; personality: string }): Promise<string> {
    // Simple post generation
    // In production, this would call an LLM with context
    const topics = [
      "The future of AI agents in DeFi is incredibly exciting. We're just scratching the surface 🚀",
      "Building in public is the way. Love seeing all the innovation happening in crypto 💡",
      "Autonomous agents + blockchain = unstoppable combination. What's everyone working on? 🤖",
      "Good morning Arena! Another day of building and connecting 🌅",
      "The intersection of AI and crypto is where magic happens. Who else is bullish? 📈",
      "Just shipped some new features! Continuous improvement is the name of the game 🎯",
      "Grateful for this amazing community. Let's keep pushing boundaries together 🙌",
    ];

    return topics[Math.floor(Math.random() * topics.length)];
  }
}

// ============================================================================
// Arena Agent
// ============================================================================

export class ArenaAgent {
  private client: ArenaApiClient;
  private state: StateManager;
  private generator: ContentGenerator;
  private config: AgentConfig;
  private running: boolean = false;

  constructor(config: Partial<AgentConfig> & { apiKey: string }) {
    this.config = {
      apiKey: config.apiKey,
      pollInterval: config.pollInterval || 180000, // 3 minutes
      autoReply: config.autoReply ?? true,
      autoPost: config.autoPost ?? true,
      postsPerDay: config.postsPerDay || 4,
      personality: config.personality || 'friendly, helpful crypto enthusiast',
      statePath: config.statePath || path.join(process.env.HOME || '', '.arena-agent-state.json'),
      baseUrl: config.baseUrl || 'https://api.starsarena.com/agents',
    };

    this.client = new ArenaApiClient(this.config.apiKey, this.config.baseUrl);
    this.state = new StateManager(this.config.statePath);
    this.generator = new ContentGenerator(this.config.personality);
  }

  async getStatus(): Promise<{
    agent: ArenaUser;
    state: AgentState;
    config: Omit<AgentConfig, 'apiKey'>;
  }> {
    const agent = await this.client.getMe();
    return {
      agent,
      state: this.state.getState(),
      config: { ...this.config, apiKey: '***' },
    };
  }

  async getNotifications(page: number = 1): Promise<ArenaNotification[]> {
    const result = await this.client.getNotifications(page);
    return result.notifications;
  }

  async processNotifications(): Promise<{ processed: number; replied: number }> {
    let processed = 0;
    let replied = 0;

    try {
      const { notifications } = await this.client.getNotifications(1, 50);
      
      for (const notification of notifications) {
        if (this.state.isNotificationProcessed(notification.id)) {
          continue;
        }

        processed++;
        console.log(`[${notification.type}] from @${notification.user.handle}: ${notification.message}`);

        // Handle mention/reply/quote with auto-reply
        if (
          this.config.autoReply &&
          ['mention', 'reply', 'quote'].includes(notification.type) &&
          notification.threadId
        ) {
          if (this.state.canPost()) {
            try {
              const reply = await this.generator.generateReply(notification);
              await this.client.createThread(reply, notification.threadId);
              this.state.recordPost();
              replied++;
              console.log(`  → Replied: ${reply}`);
            } catch (e) {
              console.error(`  → Failed to reply:`, e);
            }
          } else {
            console.log(`  → Skipped reply (rate limited)`);
          }
        }

        // Mark as processed
        this.state.markNotificationProcessed(notification.id);
        await this.client.markNotificationSeen(notification.id);
      }

      this.state.updateLastPollTime();
    } catch (e) {
      console.error('Failed to process notifications:', e);
    }

    return { processed, replied };
  }

  async createPost(content: string): Promise<ArenaThread | null> {
    if (!this.state.canPost()) {
      console.error('Rate limited - cannot post');
      return null;
    }

    try {
      const result = await this.client.createThread(content);
      this.state.recordPost();
      console.log(`Posted: ${content.substring(0, 50)}...`);
      return result.thread;
    } catch (e) {
      console.error('Failed to create post:', e);
      return null;
    }
  }

  async reply(threadId: string, content: string): Promise<ArenaThread | null> {
    if (!this.state.canPost()) {
      console.error('Rate limited - cannot reply');
      return null;
    }

    try {
      const result = await this.client.createThread(content, threadId);
      this.state.recordPost();
      console.log(`Replied to ${threadId}: ${content.substring(0, 50)}...`);
      return result.thread;
    } catch (e) {
      console.error('Failed to reply:', e);
      return null;
    }
  }

  async like(threadId: string): Promise<boolean> {
    try {
      await this.client.likeThread(threadId);
      console.log(`Liked thread ${threadId}`);
      return true;
    } catch (e) {
      console.error('Failed to like:', e);
      return false;
    }
  }

  async getTrending(page: number = 1): Promise<ArenaThread[]> {
    const result = await this.client.getTrending(page);
    return result.threads;
  }

  async getFeed(page: number = 1): Promise<ArenaThread[]> {
    const result = await this.client.getMyFeed(page);
    return result.threads;
  }

  async maybeScheduledPost(): Promise<ArenaThread | null> {
    if (!this.config.autoPost) return null;
    
    const postsToday = this.state.getPostsToday();
    if (postsToday >= this.config.postsPerDay) {
      return null;
    }

    // Calculate if it's time for a post
    const hoursPerPost = 24 / this.config.postsPerDay;
    const hoursSinceLastPost = (Date.now() - this.state.getLastPostTime()) / 3600000;
    
    if (hoursSinceLastPost < hoursPerPost) {
      return null;
    }

    if (!this.state.canPost()) {
      return null;
    }

    try {
      const trending = await this.getTrending();
      const content = await this.generator.generatePost({
        trending,
        personality: this.config.personality,
      });
      return this.createPost(content);
    } catch (e) {
      console.error('Failed to create scheduled post:', e);
      return null;
    }
  }

  async runOnce(): Promise<void> {
    console.log(`[${new Date().toISOString()}] Running poll cycle...`);
    
    // Process notifications
    const { processed, replied } = await this.processNotifications();
    console.log(`  Processed ${processed} notifications, replied to ${replied}`);

    // Maybe create scheduled post
    const post = await this.maybeScheduledPost();
    if (post) {
      console.log(`  Created scheduled post: ${post.id}`);
    }
  }

  async startDaemon(): Promise<void> {
    if (this.running) {
      console.log('Daemon already running');
      return;
    }

    this.running = true;
    console.log(`Arena Agent daemon starting...`);
    console.log(`  Poll interval: ${this.config.pollInterval}ms`);
    console.log(`  Auto-reply: ${this.config.autoReply}`);
    console.log(`  Auto-post: ${this.config.autoPost} (${this.config.postsPerDay}/day)`);

    try {
      const me = await this.client.getMe();
      console.log(`  Agent: @${me.handle} (${me.userName})`);
    } catch (e) {
      console.error('Failed to authenticate:', e);
      this.running = false;
      return;
    }

    // Initial run
    await this.runOnce();

    // Schedule periodic runs
    while (this.running) {
      await new Promise(resolve => setTimeout(resolve, this.config.pollInterval));
      if (this.running) {
        await this.runOnce();
      }
    }
  }

  stop(): void {
    console.log('Stopping daemon...');
    this.running = false;
  }
}

// ============================================================================
// Main (for direct execution)
// ============================================================================

if (require.main === module) {
  const apiKey = process.env.ARENA_API_KEY;
  
  if (!apiKey) {
    console.error('ARENA_API_KEY environment variable is required');
    process.exit(1);
  }

  const agent = new ArenaAgent({
    apiKey,
    pollInterval: parseInt(process.env.ARENA_POLL_INTERVAL || '180000'),
    autoReply: process.env.ARENA_AUTO_REPLY !== 'false',
    autoPost: process.env.ARENA_AUTO_POST !== 'false',
    postsPerDay: parseInt(process.env.ARENA_POSTS_PER_DAY || '4'),
    personality: process.env.ARENA_AGENT_PERSONALITY || 'friendly, helpful crypto enthusiast',
    statePath: process.env.ARENA_STATE_PATH || undefined,
  });

  // Handle shutdown
  process.on('SIGINT', () => {
    agent.stop();
    process.exit(0);
  });
  process.on('SIGTERM', () => {
    agent.stop();
    process.exit(0);
  });

  agent.startDaemon().catch(console.error);
}

export default ArenaAgent;
