/**
 * Notification Service - Multi-channel Notifications
 *
 * Sends notifications via Telegram, Discord, or logs
 * for cleanup events and emergencies
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

class Notifier {
  constructor(config = {}) {
    this.config = {
      enabled: config.enabled !== false,
      channels: config.channels || ['log'],
      telegram: {
        botToken: config.telegram?.botToken || process.env.TELEGRAM_BOT_TOKEN,
        chatId: config.telegram?.chatId || process.env.TELEGRAM_CHAT_ID,
        ...config.telegram
      },
      discord: {
        webhookUrl: config.discord?.webhookUrl || process.env.DISCORD_WEBHOOK_URL,
        ...config.discord
      },
      log: {
        path: config.log?.path || path.join(os.homedir(), '.openclaw', 'logs', 'notifications.log'),
        ...config.log
      },
      ...config
    };

    this._ensureLogDir();
  }

  /**
   * Send notification to all configured channels
   * @param {Object} notification - Notification object
   * @returns {Promise<Object>} Results from all channels
   */
  async send(notification) {
    if (!this.config.enabled) {
      return { enabled: false, message: 'Notifications disabled' };
    }

    const {
      title,
      message,
      level = 'info', // info, warning, error, critical
      data = {}
    } = notification;

    const results = {
      sent: [],
      failed: [],
      timestamp: new Date().toISOString()
    };

    // Send to each configured channel
    for (const channel of this.config.channels) {
      try {
        switch (channel) {
          case 'telegram':
            await this._sendToTelegram(title, message, level, data);
            results.sent.push('telegram');
            break;

          case 'discord':
            await this._sendToDiscord(title, message, level, data);
            results.sent.push('discord');
            break;

          case 'log':
          default:
            await this._sendToLog(title, message, level, data);
            results.sent.push('log');
            break;
        }
      } catch (error) {
        results.failed.push({
          channel,
          error: error.message
        });
      }
    }

    return results;
  }

  /**
   * Send emergency notification (all channels)
   * @param {Object} report - Emergency cleanup report
   * @returns {Promise<Object>}
   */
  async sendEmergency(report) {
    const title = '🚨 EMERGENCY CLEANUP EXECUTED';

    const message = this._formatEmergencyMessage(report);

    return await this.send({
      title,
      message,
      level: 'critical',
      data: report
    });
  }

  /**
   * Send routine cleanup notification
   * @param {Object} result - Cleanup result
   * @returns {Promise<Object>}
   */
  async sendCleanup(result) {
    const title = '🧹 Automatic Cleanup Complete';

    const message = `
Session Cleanup Summary:
• Sessions pruned: ${result.sessionsPruned}
• Tokens freed: ${this._formatTokens(result.tokensFreed)}
• Strategy: ${result.strategy}

Context usage reduced successfully.
    `.trim();

    return await this.send({
      title,
      message,
      level: 'info',
      data: result
    });
  }

  /**
   * Send alert notification (high usage warning)
   * @param {Object} usage - Context usage data
   * @returns {Promise<Object>}
   */
  async sendAlert(usage) {
    const title = '⚠️ High Context Usage Alert';

    const message = `
Context usage is high:
• Current: ${this._formatTokens(usage.currentTokens)}/200k (${usage.utilizationPercent.toFixed(1)}%)
• Sessions: ${usage.sessions.length}
• Status: ${usage.status.emoji} ${usage.status.level}

${usage.status.message}
    `.trim();

    return await this.send({
      title,
      message,
      level: 'warning',
      data: usage
    });
  }

  /**
   * Send to Telegram
   * @private
   */
  async _sendToTelegram(title, message, level, data) {
    if (!this.config.telegram.botToken || !this.config.telegram.chatId) {
      throw new Error('Telegram configuration incomplete (missing botToken or chatId)');
    }

    const emoji = this._getLevelEmoji(level);
    const text = `${emoji} *${this._escapeMarkdown(title)}*\n\n${this._escapeMarkdown(message)}`;

    const payload = {
      chat_id: this.config.telegram.chatId,
      text: text,
      parse_mode: 'Markdown'
    };

    const url = `https://api.telegram.org/bot${this.config.telegram.botToken}/sendMessage`;

    return await this._makeHttpRequest(url, 'POST', payload);
  }

  /**
   * Send to Discord
   * @private
   */
  async _sendToDiscord(title, message, level, data) {
    if (!this.config.discord.webhookUrl) {
      throw new Error('Discord webhook URL not configured');
    }

    const color = this._getLevelColor(level);

    const payload = {
      embeds: [{
        title: title,
        description: message,
        color: color,
        timestamp: new Date().toISOString(),
        footer: {
          text: 'OpenClaw Janitor'
        }
      }]
    };

    return await this._makeHttpRequest(this.config.discord.webhookUrl, 'POST', payload);
  }

  /**
   * Send to log file
   * @private
   */
  async _sendToLog(title, message, level, data) {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] [${level.toUpperCase()}] ${title}\n${message}\n${JSON.stringify(data, null, 2)}\n\n`;

    await fs.promises.appendFile(this.config.log.path, logLine, 'utf-8');
  }

  /**
   * Make HTTP request
   * @private
   */
  async _makeHttpRequest(url, method, data) {
    return new Promise((resolve, reject) => {
      const parsedUrl = new URL(url);
      const protocol = parsedUrl.protocol === 'https:' ? https : http;

      const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port,
        path: parsedUrl.pathname + parsedUrl.search,
        method: method,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      const req = protocol.request(options, (res) => {
        let body = '';

        res.on('data', (chunk) => {
          body += chunk;
        });

        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve({ statusCode: res.statusCode, body });
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${body}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      if (data) {
        req.write(JSON.stringify(data));
      }

      req.end();
    });
  }

  /**
   * Format emergency message
   * @private
   */
  _formatEmergencyMessage(report) {
    const beforePercent = report.beforeUsage.percent.toFixed(1);
    const afterPercent = report.afterUsage.percent.toFixed(1);
    const tokensFreed = report.beforeUsage.tokens - report.afterUsage.tokens;

    return `
Reason: Context usage exceeded ${report.trigger === 'emergency' ? '95%' : 'threshold'}
Previous: ${this._formatTokens(report.beforeUsage.tokens)}/200k (${beforePercent}%)

Actions Taken:
✅ Archived ${report.actions[0]?.result?.archived || 0} sessions
✅ Removed old sessions
✅ Freed ${this._formatTokens(tokensFreed)} tokens

Current Status:
• Context: ${this._formatTokens(report.afterUsage.tokens)}/200k (${afterPercent}%)
• Active sessions: ${report.afterUsage.sessions}
• System: ${report.success ? '✅ OPERATIONAL' : '❌ NEEDS ATTENTION'}

Your conversation history is safe in archives.
Duration: ${report.duration}ms
    `.trim();
  }

  /**
   * Get emoji for notification level
   * @private
   */
  _getLevelEmoji(level) {
    const emojis = {
      info: 'ℹ️',
      warning: '⚠️',
      error: '❌',
      critical: '🚨'
    };

    return emojis[level] || 'ℹ️';
  }

  /**
   * Get color for Discord embed
   * @private
   */
  _getLevelColor(level) {
    const colors = {
      info: 0x3498db,     // Blue
      warning: 0xf39c12,  // Orange
      error: 0xe74c3c,    // Red
      critical: 0xc0392b  // Dark red
    };

    return colors[level] || colors.info;
  }

  /**
   * Escape Markdown characters for Telegram
   * @private
   */
  _escapeMarkdown(text) {
    return text.replace(/([_*\[\]()~`>#+\-=|{}.!])/g, '\\$1');
  }

  /**
   * Format tokens
   * @private
   */
  _formatTokens(tokens) {
    if (tokens < 1000) return `${tokens}`;
    if (tokens < 1000000) return `${(tokens / 1000).toFixed(1)}k`;
    return `${(tokens / 1000000).toFixed(1)}M`;
  }

  /**
   * Ensure log directory exists
   * @private
   */
  _ensureLogDir() {
    const logDir = path.dirname(this.config.log.path);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
  }

  /**
   * Test notification configuration
   */
  async test() {
    console.log('Testing notification configuration...\n');

    const testNotification = {
      title: '🧪 Test Notification',
      message: 'This is a test notification from OpenClaw Janitor.\nIf you see this, notifications are working correctly!',
      level: 'info',
      data: {
        test: true,
        timestamp: new Date().toISOString()
      }
    };

    const result = await this.send(testNotification);

    console.log('Test Results:');
    console.log(`  Sent to: ${result.sent.join(', ')}`);

    if (result.failed.length > 0) {
      console.log(`  Failed: ${result.failed.map(f => `${f.channel} (${f.error})`).join(', ')}`);
    }

    return result;
  }

  /**
   * Get configuration status
   */
  getStatus() {
    return {
      enabled: this.config.enabled,
      channels: this.config.channels,
      telegram: {
        configured: !!(this.config.telegram.botToken && this.config.telegram.chatId)
      },
      discord: {
        configured: !!this.config.discord.webhookUrl
      },
      log: {
        path: this.config.log.path
      }
    };
  }
}

module.exports = Notifier;
