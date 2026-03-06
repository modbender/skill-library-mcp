#!/usr/bin/env node

/**
 * Kit Email Operator - API Client
 * 
 * Full-featured Kit (ConvertKit) API v4 client with:
 * - Rate limiting and retries
 * - Error handling
 * - All broadcast/tag/subscriber operations
 */

const https = require('https');
const { loadCredentials } = require('./credentials.js');

const BASE_URL = 'api.kit.com';
const API_VERSION = 'v4';

class KitAPI {
  constructor(credentials = null) {
    this.credentials = credentials || loadCredentials();
    this.rateLimitDelay = 1000; // 1 second between requests
    this.lastRequestTime = 0;
  }
  
  /**
   * Make authenticated request to Kit API
   */
  async request(method, endpoint, data = null) {
    // Rate limiting
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    if (timeSinceLastRequest < this.rateLimitDelay) {
      await this.sleep(this.rateLimitDelay - timeSinceLastRequest);
    }
    this.lastRequestTime = Date.now();
    
    const options = {
      hostname: BASE_URL,
      path: `/${API_VERSION}${endpoint}`,
      method: method.toUpperCase(),
      headers: {
        'Authorization': `Bearer ${this.credentials.apiKey}`,
        'Content-Type': 'application/json'
      }
    };
    
    return new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let body = '';
        
        res.on('data', chunk => {
          body += chunk;
        });
        
        res.on('end', () => {
          try {
            const response = body ? JSON.parse(body) : {};
            
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(response);
            } else {
              reject(new Error(`API Error ${res.statusCode}: ${response.message || body}`));
            }
          } catch (error) {
            reject(new Error(`Failed to parse response: ${error.message}`));
          }
        });
      });
      
      req.on('error', reject);
      
      if (data) {
        req.write(JSON.stringify(data));
      }
      
      req.end();
    });
  }
  
  /**
   * Retry wrapper for resilient API calls
   */
  async requestWithRetry(method, endpoint, data = null, maxRetries = 3) {
    let lastError;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await this.request(method, endpoint, data);
      } catch (error) {
        lastError = error;
        
        // Don't retry on auth errors (400, 401, 403)
        if (error.message.includes('401') || error.message.includes('403')) {
          throw error;
        }
        
        // Exponential backoff
        if (i < maxRetries - 1) {
          const delay = Math.pow(2, i) * 1000;
          await this.sleep(delay);
        }
      }
    }
    
    throw lastError;
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  // ===== BROADCASTS =====
  
  /**
   * Create a broadcast
   * @param {Object} data - { subject, content, description, send_at, public, tag_ids, segment_ids }
   */
  async createBroadcast(data) {
    return this.requestWithRetry('POST', '/broadcasts', data);
  }
  
  /**
   * Update a broadcast
   */
  async updateBroadcast(id, data) {
    return this.requestWithRetry('PUT', `/broadcasts/${id}`, data);
  }
  
  /**
   * Delete a broadcast
   */
  async deleteBroadcast(id) {
    return this.requestWithRetry('DELETE', `/broadcasts/${id}`);
  }
  
  /**
   * Get broadcast details
   */
  async getBroadcast(id) {
    return this.requestWithRetry('GET', `/broadcasts/${id}`);
  }
  
  /**
   * List broadcasts
   * @param {Object} options - { status: 'draft|scheduled|sent', page: 1, per_page: 50 }
   */
  async listBroadcasts(options = {}) {
    const params = new URLSearchParams(options);
    const endpoint = `/broadcasts?${params.toString()}`;
    return this.requestWithRetry('GET', endpoint);
  }
  
  /**
   * Get broadcast statistics
   */
  async getBroadcastStats(id) {
    return this.requestWithRetry('GET', `/broadcasts/${id}/stats`);
  }
  
  // ===== TAGS =====
  
  /**
   * List all tags
   */
  async listTags() {
    return this.requestWithRetry('GET', '/tags');
  }
  
  /**
   * Create a tag
   */
  async createTag(name) {
    return this.requestWithRetry('POST', '/tags', { name });
  }
  
  /**
   * Tag a subscriber
   */
  async tagSubscriber(email, tagId) {
    return this.requestWithRetry('POST', '/tags/{tagId}/subscribe', {
      email,
      tag_id: tagId
    });
  }
  
  /**
   * Untag a subscriber
   */
  async untagSubscriber(email, tagId) {
    return this.requestWithRetry('POST', `/tags/${tagId}/unsubscribe`, {
      email
    });
  }
  
  // ===== SUBSCRIBERS =====
  
  /**
   * List subscribers
   * @param {Object} options - { sort_order: 'asc|desc', page: 1, per_page: 50 }
   */
  async listSubscribers(options = {}) {
    const params = new URLSearchParams(options);
    const endpoint = `/subscribers?${params.toString()}`;
    return this.requestWithRetry('GET', endpoint);
  }
  
  /**
   * Get subscriber by ID
   */
  async getSubscriber(id) {
    return this.requestWithRetry('GET', `/subscribers/${id}`);
  }
  
  /**
   * Add subscriber
   */
  async addSubscriber(data) {
    return this.requestWithRetry('POST', '/subscribers', data);
  }
  
  /**
   * Update subscriber
   */
  async updateSubscriber(id, data) {
    return this.requestWithRetry('PUT', `/subscribers/${id}`, data);
  }
  
  /**
   * Unsubscribe a subscriber
   */
  async unsubscribeSubscriber(email) {
    return this.requestWithRetry('PUT', `/subscribers/${email}/unsubscribe`);
  }
  
  // ===== CUSTOM FIELDS =====
  
  /**
   * List custom fields
   */
  async listCustomFields() {
    return this.requestWithRetry('GET', '/custom_fields');
  }
  
  /**
   * Create custom field
   */
  async createCustomField(data) {
    return this.requestWithRetry('POST', '/custom_fields', data);
  }
  
  /**
   * Update subscriber custom field
   */
  async updateSubscriberField(subscriberId, fieldId, value) {
    return this.requestWithRetry('PUT', `/subscribers/${subscriberId}`, {
      fields: {
        [fieldId]: value
      }
    });
  }
  
  // ===== FORMS =====
  
  /**
   * List forms
   */
  async listForms() {
    return this.requestWithRetry('GET', '/forms');
  }
  
  /**
   * Get form details
   */
  async getForm(id) {
    return this.requestWithRetry('GET', `/forms/${id}`);
  }
  
  // ===== SEGMENTS =====
  
  /**
   * List segments (Note: May require higher-tier Kit plan)
   */
  async listSegments() {
    return this.requestWithRetry('GET', '/segments');
  }
  
  // ===== HELPER METHODS =====
  
  /**
   * Format broadcast stats for human reading
   */
  formatBroadcastStats(stats) {
    const { recipients, open, click, unsubscribe, bounce, complaint } = stats;
    
    const openRate = recipients > 0 ? (open.unique / recipients * 100).toFixed(1) : 0;
    const clickRate = open.unique > 0 ? (click.unique / open.unique * 100).toFixed(1) : 0;
    const unsubRate = recipients > 0 ? (unsubscribe / recipients * 100).toFixed(2) : 0;
    
    return {
      recipients,
      opens: {
        unique: open.unique,
        total: open.total,
        rate: `${openRate}%`
      },
      clicks: {
        unique: click.unique,
        total: click.total,
        rate: `${clickRate}%`
      },
      unsubscribes: {
        count: unsubscribe,
        rate: `${unsubRate}%`
      },
      bounces: bounce,
      complaints: complaint
    };
  }
  
  /**
   * Validate email format
   */
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
  
  /**
   * Test connection
   */
  async testConnection() {
    try {
      await this.listTags();
      return { success: true, message: 'Connection successful' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }
}

// CLI usage for testing
if (require.main === module) {
  const command = process.argv[2];
  const kit = new KitAPI();
  
  (async () => {
    try {
      if (command === 'test') {
        console.log('Testing Kit API connection...');
        const result = await kit.testConnection();
        console.log(result.success ? '✅ Connected' : `❌ Failed: ${result.message}`);
        
      } else if (command === 'tags') {
        console.log('Fetching tags...');
        const tags = await kit.listTags();
        console.log(JSON.stringify(tags, null, 2));
        
      } else if (command === 'subscribers') {
        console.log('Fetching subscribers...');
        const subs = await kit.listSubscribers({ per_page: 5 });
        console.log(JSON.stringify(subs, null, 2));
        
      } else if (command === 'broadcasts') {
        console.log('Fetching broadcasts...');
        const broadcasts = await kit.listBroadcasts({ per_page: 5 });
        console.log(JSON.stringify(broadcasts, null, 2));
        
      } else {
        console.log('Usage:');
        console.log('  node kit-api.js test         - Test connection');
        console.log('  node kit-api.js tags         - List tags');
        console.log('  node kit-api.js subscribers  - List subscribers');
        console.log('  node kit-api.js broadcasts   - List broadcasts');
      }
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  })();
}

module.exports = { KitAPI };
