/**
 * Universal Content Publisher
 * 
 * Handles posting to TikTok (and other platforms) via Postiz API.
 * Abstracts away platform-specific settings and provides unified interface.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class Publisher {
  constructor(config) {
    this.config = config;
    this.postiz = config.postiz || {};
    // Prefer env var over config file for API key
    this.postiz.apiKey = process.env.POSTIZ_API_KEY || this.postiz.apiKey;
    
    if (!this.postiz.apiKey) {
      throw new Error('Postiz API key required — set POSTIZ_API_KEY env var or config.postiz.apiKey');
    }
  }

  /**
   * Post content to TikTok via Postiz
   * 
   * @param {Object} content - Generated content object
   * @param {string} caption - Post caption
   * @param {Object} options - Publishing options
   * @returns {Promise<Object>} Post result
   */
  async post(content, caption, options = {}) {
    const {
      platform = 'tiktok',
      schedule = null,
      draft = false,
      title = caption,
      settings = {}
    } = options;

    // Get platform integration ID
    const integrationId = this.postiz.integrationIds[platform] || this.postiz.integrationId;
    if (!integrationId) {
      throw new Error(`No integration ID configured for platform: ${platform}`);
    }

    // Upload media files
    const mediaUrls = await this._uploadMedia(content.slides || content.media || []);
    
    // Merge platform settings
    const platformSettings = {
      ...this.config.posting?.defaultSettings?.[platform],
      ...this.config.platforms?.[platform]?.settings,
      ...settings
    };

    // Build Postiz command
    const cmd = this._buildPostizCommand({
      integrationId,
      mediaUrls,
      caption,
      title,
      schedule,
      settings: platformSettings,
      draft
    });

    try {
      console.log(`📤 Publishing to ${platform}...`);
      const output = execSync(cmd, { encoding: 'utf8' });
      const result = this._parsePostizOutput(output);
      
      // Save post metadata
      await this._savePostMetadata(content, result, {
        platform,
        caption,
        settings: platformSettings,
        timestamp: new Date().toISOString()
      });

      return result;
      
    } catch (error) {
      console.error('❌ Publishing failed:', error.message);
      throw error;
    }
  }

  /**
   * Schedule batch of posts
   * 
   * @param {Array} contentBatch - Array of content objects
   * @param {Object} scheduleOptions - Scheduling preferences
   * @returns {Promise<Array>} Scheduled posts
   */
  async scheduleBatch(contentBatch, scheduleOptions = {}) {
    const {
      spacing = 3, // hours between posts
      startTime = null,
      optimalHours = this.config.posting?.optimalHours || [12, 18, 21],
      timezone = this.config.posting?.timezone || 'UTC'
    } = scheduleOptions;

    const results = [];
    let currentTime = startTime ? new Date(startTime) : this._getNextOptimalTime(optimalHours);

    for (const content of contentBatch) {
      const caption = content.caption || content.hook || 'New post';
      
      try {
        const result = await this.post(content, caption, {
          schedule: currentTime.toISOString()
        });
        
        results.push({ content, result, scheduledFor: currentTime.toISOString() });
        
        // Advance to next posting slot
        currentTime = new Date(currentTime.getTime() + spacing * 60 * 60 * 1000);
        
      } catch (error) {
        console.error(`Failed to schedule post:`, error.message);
        results.push({ content, error: error.message });
      }
    }

    return results;
  }

  /**
   * Upload media files to Postiz
   * @private
   */
  async _uploadMedia(mediaPaths) {
    const mediaUrls = [];
    
    for (const mediaPath of mediaPaths) {
      if (!fs.existsSync(mediaPath)) {
        throw new Error(`Media file not found: ${mediaPath}`);
      }
      
      try {
        console.log(`📎 Uploading ${path.basename(mediaPath)}...`);
        const cmd = `POSTIZ_API_KEY=${this._shellEscape(this.postiz.apiKey)} postiz upload ${this._shellEscape(mediaPath)}`;
        const output = execSync(cmd, { encoding: 'utf8' });
        const url = output.trim().split('\n').pop(); // Get last line (URL)
        mediaUrls.push(url);
      } catch (error) {
        throw new Error(`Failed to upload ${mediaPath}: ${error.message}`);
      }
    }
    
    return mediaUrls;
  }

  /**
   * Build Postiz CLI command
   * @private
   */
  /**
   * Escape a string for safe use in shell arguments.
   * Wraps in single quotes and escapes any embedded single quotes.
   * @private
   */
  _shellEscape(str) {
    if (typeof str !== 'string') str = String(str);
    return "'" + str.replace(/'/g, "'\\''") + "'";
  }

  _buildPostizCommand(params) {
    const { integrationId, mediaUrls, caption, title, schedule, settings, draft } = params;
    
    const args = [
      'postiz', 'posts:create',
      '-c', this._shellEscape(caption),
      '-i', this._shellEscape(integrationId),
      '--title', this._shellEscape(title)
    ];
    
    if (mediaUrls.length > 0) {
      args.push('-m', this._shellEscape(mediaUrls.join(',')));
    }
    
    if (schedule) {
      args.push('-s', this._shellEscape(schedule));
    }
    
    if (draft) {
      args.push('--draft');
    }
    
    if (settings && Object.keys(settings).length > 0) {
      args.push('--settings', this._shellEscape(JSON.stringify(settings)));
    }
    
    return `POSTIZ_API_KEY=${this._shellEscape(this.postiz.apiKey)} ${args.join(' ')}`;
  }

  /**
   * Parse Postiz command output
   * @private
   */
  _parsePostizOutput(output) {
    // Parse the JSON response from Postiz CLI
    try {
      const lines = output.trim().split('\n');
      const jsonLine = lines.find(line => line.startsWith('{'));
      return jsonLine ? JSON.parse(jsonLine) : { success: true, output };
    } catch (error) {
      return { success: true, rawOutput: output };
    }
  }

  /**
   * Save post metadata for analytics
   * @private
   */
  async _savePostMetadata(content, result, postInfo) {
    const metadataDir = path.join(content.outputDir || '.', '.metadata');
    if (!fs.existsSync(metadataDir)) {
      fs.mkdirSync(metadataDir, { recursive: true });
    }
    
    const metadata = {
      content: {
        type: content.contentType,
        generator: content.generator,
        duration: content.duration
      },
      post: postInfo,
      result,
      timestamp: new Date().toISOString()
    };
    
    const filename = `post-${Date.now()}.json`;
    fs.writeFileSync(
      path.join(metadataDir, filename), 
      JSON.stringify(metadata, null, 2)
    );
  }

  /**
   * Get next optimal posting time
   * @private
   */
  _getNextOptimalTime(optimalHours) {
    const now = new Date();
    const currentHour = now.getHours();
    
    // Find next optimal hour today or tomorrow
    const nextHour = optimalHours.find(h => h > currentHour) || optimalHours[0];
    
    const nextTime = new Date(now);
    if (nextHour <= currentHour) {
      nextTime.setDate(nextTime.getDate() + 1); // Tomorrow
    }
    nextTime.setHours(nextHour, 0, 0, 0);
    
    return nextTime;
  }
}

module.exports = Publisher;