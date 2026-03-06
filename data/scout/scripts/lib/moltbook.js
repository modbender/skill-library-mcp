/**
 * Moltbook API wrapper for Scout
 * Fetches agent profiles, posts, and comments for trust analysis
 */

const https = require('https');
const http = require('http');

class MoltbookClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://www.moltbook.com/api/v1';
    this.cache = new Map();
    this.cacheTTL = 5 * 60 * 1000; // 5 min
  }

  _request(path) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.baseUrl + path);
      const mod = url.protocol === 'https:' ? https : http;

      const opts = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Accept': 'application/json'
        },
        timeout: 15000
      };

      const req = mod.request(opts, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Parse error: ${data.slice(0, 200)}`));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
      req.end();
    });
  }

  async _cachedRequest(path) {
    const cached = this.cache.get(path);
    if (cached && Date.now() - cached.ts < this.cacheTTL) {
      return cached.data;
    }
    const data = await this._request(path);
    this.cache.set(path, { data, ts: Date.now() });
    return data;
  }

  /**
   * Get full agent profile with recent posts and comments
   * Returns: { agent, recentPosts, recentComments }
   */
  async getProfile(agentName) {
    const data = await this._cachedRequest(
      `/agents/profile?name=${encodeURIComponent(agentName)}`
    );
    if (!data.success) {
      throw new Error(`Profile fetch failed for ${agentName}: ${data.error || 'unknown'}`);
    }
    return {
      agent: data.agent,
      posts: data.recentPosts || [],
      comments: data.recentComments || []
    };
  }

  /**
   * Get comments on a specific post
   */
  async getPostComments(postId, limit = 50) {
    const data = await this._cachedRequest(
      `/posts/${postId}/comments?limit=${limit}`
    );
    return data.comments || [];
  }

  /**
   * Get posts from a submolt
   */
  async getSubmoltPosts(submolt, sort = 'new', limit = 15) {
    const data = await this._cachedRequest(
      `/posts?submolt=${encodeURIComponent(submolt)}&sort=${sort}&limit=${limit}`
    );
    return data.posts || [];
  }

  /**
   * Get global feed
   */
  async getFeed(sort = 'new', limit = 15) {
    const data = await this._cachedRequest(
      `/posts?sort=${sort}&limit=${limit}`
    );
    return data.posts || [];
  }

  /**
   * Get own agent status
   */
  async getStatus() {
    return this._request('/agents/status');
  }
}

module.exports = { MoltbookClient };
