/**
 * NotificationManager
 * Sends alerts to Telegram for executed decisions and errors
 * Notifies: decision execution, errors, APR changes
 */
const https = require('https');
const fs = require('fs');
const path = require('path');

class NotificationManager {
  constructor(config = {}) {
    this.telegramBotToken = config.telegramBotToken;
    this.telegramChatId = config.telegramChatId;
    this.enabled = config.enabled !== false && this.telegramBotToken && this.telegramChatId;
    
    this.notificationLog = [];
    this.aprThreshold = config.aprThreshold || 1.0; // Alert if APR changes by >1%
    this.lastAprValues = {}; // Track APR changes
    
    if (this.enabled) {
      console.log(`✓ Telegram notifications enabled (Chat: ${this.telegramChatId})`);
    } else {
      console.log('⚠️  Telegram notifications disabled (missing token or chat ID)');
    }
  }

  /**
   * Send notification to Telegram
   * @param {string} message - Message text (supports markdown)
   * @param {string} parseMode - 'Markdown' or 'HTML' (default: 'Markdown')
   * @returns {Promise<Object>} Response from Telegram API
   */
  async sendTelegram(message, parseMode = 'Markdown') {
    if (!this.enabled) {
      console.log('ℹ️  Notification skipped (disabled)');
      return { success: false, reason: 'disabled' };
    }

    return new Promise((resolve, reject) => {
      const payload = JSON.stringify({
        chat_id: this.telegramChatId,
        text: message,
        parse_mode: parseMode,
        disable_web_page_preview: true
      });

      const options = {
        hostname: 'api.telegram.org',
        port: 443,
        path: `/bot${this.telegramBotToken}/sendMessage`,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': payload.length
        }
      };

      const req = https.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            if (response.ok) {
              resolve({ success: true, messageId: response.result.message_id });
            } else {
              reject(new Error(`Telegram API error: ${response.description}`));
            }
          } catch (error) {
            reject(new Error(`Failed to parse Telegram response: ${error.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(new Error(`Telegram request failed: ${error.message}`));
      });

      req.write(payload);
      req.end();
    });
  }

  /**
   * Notify execution completion
   * @param {Object} execution - Execution result { status, tx_hash, action, vault_id, details, timestamp }
   */
  async notifyExecution(execution) {
    const { status, action, vault_id, details } = execution;
    
    let emoji = status === 'SUCCESS' ? '✅' : '❌';
    let message = `${emoji} *${action} ${status}*\n\n`;
    message += `🏛️ Vault: \`${vault_id}\`\n`;
    message += `⏱️ Time: \`${details.timestamp}\`\n`;

    if (status === 'SUCCESS') {
      message += `🔗 TxHash: \`${details.tx_hash.substring(0, 16)}...\`\n`;
      message += `📦 Gas: \`${details.gas_used}\`\n`;
      message += `✓ Block: \`${details.block_number}\``;
    } else {
      message += `❌ Error: \`${details.error}\``;
    }

    try {
      const result = await this.sendTelegram(message);
      this.logNotification('EXECUTION', action, vault_id, status, result);
      console.log(`✓ Execution notification sent`);
    } catch (error) {
      console.error(`✗ Failed to send execution notification: ${error.message}`);
      this.logNotification('EXECUTION', action, vault_id, status, { error: error.message });
    }
  }

  /**
   * Notify agent decision
   * @param {Object} decision - Agent decision { recommended_action, target_vault_id, confidence_score, rebalance_risk }
   */
  async notifyDecision(decision) {
    const {
      recommended_action,
      target_vault_id,
      confidence_score,
      rebalance_risk,
      cycle_number
    } = decision;

    let emoji = '🤖';
    let message = `${emoji} *Agent Decision*\n\n`;
    message += `📊 Cycle: \`#${cycle_number}\`\n`;
    message += `💡 Action: \`${recommended_action}\`\n`;
    message += `🎯 Vault: \`${target_vault_id}\`\n`;
    message += `📈 Confidence: \`${(confidence_score * 100).toFixed(1)}%\`\n`;
    message += `⚠️ Risk: \`${(rebalance_risk * 100).toFixed(1)}%\``;

    try {
      const result = await this.sendTelegram(message);
      this.logNotification('DECISION', recommended_action, target_vault_id, 'SENT', result);
      console.log(`✓ Decision notification sent`);
    } catch (error) {
      console.error(`✗ Failed to send decision notification: ${error.message}`);
      this.logNotification('DECISION', recommended_action, target_vault_id, 'FAILED', { error: error.message });
    }
  }

  /**
   * Notify APR change
   * @param {string} vaultId - Vault ID
   * @param {number} newAPR - New APR percentage
   * @param {number} oldAPR - Previous APR percentage
   */
  async notifyAPRChange(vaultId, newAPR, oldAPR = null) {
    // Check if change exceeds threshold
    if (oldAPR !== null) {
      const aprChange = Math.abs(newAPR - oldAPR);
      if (aprChange < this.aprThreshold) {
        return; // Change too small, skip notification
      }
    }

    this.lastAprValues[vaultId] = newAPR;

    const aprChange = oldAPR ? newAPR - oldAPR : 0;
    const aprChangeStr = aprChange > 0 ? `+${aprChange.toFixed(2)}%` : `${aprChange.toFixed(2)}%`;
    const changeEmoji = aprChange > 0 ? '📈' : '📉';

    let message = `${changeEmoji} *APR Change Alert*\n\n`;
    message += `🏛️ Vault: \`${vaultId}\`\n`;
    message += `💰 New APR: \`${newAPR.toFixed(2)}%\`\n`;
    
    if (oldAPR !== null) {
      message += `📊 Change: \`${aprChangeStr}\``;
    }

    try {
      const result = await this.sendTelegram(message);
      this.logNotification('APR_CHANGE', 'APR_UPDATE', vaultId, 'SENT', result);
      console.log(`✓ APR change notification sent`);
    } catch (error) {
      console.error(`✗ Failed to send APR notification: ${error.message}`);
      this.logNotification('APR_CHANGE', 'APR_UPDATE', vaultId, 'FAILED', { error: error.message });
    }
  }

  /**
   * Notify error/warning
   * @param {string} severity - 'ERROR', 'WARNING', 'INFO'
   * @param {string} component - Component name (scheduler, executor, reader, etc)
   * @param {string} message - Error message
   * @param {Object} context - Additional context data
   */
  async notifyError(severity, component, message, context = {}) {
    let emoji = '⚠️';
    if (severity === 'ERROR') emoji = '🔴';
    if (severity === 'INFO') emoji = 'ℹ️';

    let notifMessage = `${emoji} *${severity}*\n\n`;
    notifMessage += `🔧 Component: \`${component}\`\n`;
    notifMessage += `📝 Message: \`${message}\`\n`;

    if (Object.keys(context).length > 0) {
      notifMessage += `\n📋 Context:\n`;
      Object.entries(context).forEach(([key, value]) => {
        const valueStr = typeof value === 'string' ? value : JSON.stringify(value);
        notifMessage += `  • ${key}: \`${valueStr}\`\n`;
      });
    }

    try {
      const result = await this.sendTelegram(notifMessage);
      this.logNotification('ERROR', component, severity, 'SENT', result);
      console.log(`✓ Error notification sent`);
    } catch (error) {
      console.error(`✗ Failed to send error notification: ${error.message}`);
      this.logNotification('ERROR', component, severity, 'FAILED', { error: error.message });
    }
  }

  /**
   * Notify cycle completion
   * @param {Object} cycleRecord - Complete cycle record
   */
  async notifyCycleCompletion(cycleRecord) {
    const {
      cycle_number,
      status,
      duration_ms,
      executions,
      errors,
      decision
    } = cycleRecord;

    let emoji = status === 'SUCCESS' ? '✅' : '❌';
    let message = `${emoji} *Cycle #${cycle_number} Complete*\n\n`;
    message += `⏱️ Duration: \`${duration_ms}ms\`\n`;
    message += `📊 Status: \`${status}\`\n`;

    if (decision) {
      message += `\n🤖 Decision: \`${decision.recommended_action}\` → \`${decision.target_vault_id}\`\n`;
    }

    message += `\n📦 Executions: \`${executions.length}\`\n`;

    if (executions.length > 0) {
      executions.slice(0, 3).forEach(ex => {
        const exEmoji = ex.status === 'SUCCESS' ? '✓' : '✗';
        message += `  ${exEmoji} ${ex.action} ${ex.status}\n`;
      });
      
      if (executions.length > 3) {
        message += `  ... and ${executions.length - 3} more\n`;
      }
    }

    if (errors.length > 0) {
      message += `\n❌ Errors: \`${errors.length}\`\n`;
      errors.slice(0, 2).forEach(err => {
        message += `  • ${err.message.substring(0, 50)}...\n`;
      });
    }

    try {
      const result = await this.sendTelegram(message);
      this.logNotification('CYCLE_COMPLETE', `cycle_${cycle_number}`, status, 'SENT', result);
      console.log(`✓ Cycle completion notification sent`);
    } catch (error) {
      console.error(`✗ Failed to send cycle notification: ${error.message}`);
      this.logNotification('CYCLE_COMPLETE', `cycle_${cycle_number}`, status, 'FAILED', { error: error.message });
    }
  }

  /**
   * Send daily summary
   * @param {Array} cycles - Array of cycles from today
   * @param {Object} stats - Statistics object
   */
  async sendDailySummary(cycles, stats) {
    let message = `📅 *Daily Summary*\n\n`;
    message += `🔄 Cycles: \`${cycles.length}\`\n`;
    message += `✅ Success: \`${stats.success_count}\`\n`;
    message += `❌ Failed: \`${stats.failure_count}\`\n`;
    message += `📊 Success Rate: \`${stats.success_rate}%\`\n`;
    message += `⏱️ Avg Duration: \`${stats.average_cycle_duration_ms}ms\`\n`;
    message += `📦 Executions: \`${stats.total_executions}\`\n`;
    message += `⏰ Generated: \`${new Date().toISOString()}\``;

    try {
      const result = await this.sendTelegram(message);
      this.logNotification('DAILY_SUMMARY', 'scheduler', 'SENT', 'SENT', result);
      console.log(`✓ Daily summary notification sent`);
    } catch (error) {
      console.error(`✗ Failed to send daily summary: ${error.message}`);
      this.logNotification('DAILY_SUMMARY', 'scheduler', 'SENT', 'FAILED', { error: error.message });
    }
  }

  /**
   * Log notification attempt
   * @param {string} type - Notification type
   * @param {string} action - Action or component
   * @param {string} vault_id - Vault ID or context
   * @param {string} status - SENT, FAILED, SKIPPED
   * @param {Object} details - Additional details
   */
  logNotification(type, action, vault_id, status, details = {}) {
    const logEntry = {
      type,
      action,
      vault_id,
      status,
      details,
      timestamp: new Date().toISOString()
    };

    this.notificationLog.push(logEntry);

    // Keep only last 500 in memory
    if (this.notificationLog.length > 500) {
      this.notificationLog = this.notificationLog.slice(-500);
    }

    // Persist to file
    const logsPath = path.join(__dirname, 'notifications.log.json');
    try {
      let allLogs = [];
      if (fs.existsSync(logsPath)) {
        const content = fs.readFileSync(logsPath, 'utf8');
        allLogs = JSON.parse(content || '[]');
      }

      allLogs.push(logEntry);

      // Keep last 2000 entries
      if (allLogs.length > 2000) {
        allLogs = allLogs.slice(-2000);
      }

      fs.writeFileSync(logsPath, JSON.stringify(allLogs, null, 2));
    } catch (error) {
      console.error(`Failed to write notification log: ${error.message}`);
    }
  }

  /**
   * Get notification history
   * @param {string} type - Optional filter by type
   * @param {number} limit - Number of entries
   * @returns {Array} Recent notifications
   */
  getNotificationHistory(type = null, limit = 50) {
    let history = this.notificationLog;
    
    if (type) {
      history = history.filter(n => n.type === type);
    }
    
    return history.slice(-limit);
  }

  /**
   * Get notification stats
   * @returns {Object} Statistics about notifications
   */
  getStats() {
    const byType = {};
    const byStatus = {};

    this.notificationLog.forEach(log => {
      byType[log.type] = (byType[log.type] || 0) + 1;
      byStatus[log.status] = (byStatus[log.status] || 0) + 1;
    });

    return {
      total_notifications: this.notificationLog.length,
      by_type: byType,
      by_status: byStatus,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Test Telegram connection
   * @returns {Promise<boolean>} True if connection successful
   */
  async testConnection() {
    if (!this.enabled) {
      console.log('ℹ️  Notifications disabled - skipping test');
      return false;
    }

    try {
      const result = await this.sendTelegram('🧪 *Test Message* - Yield Farming Agent notifications working!');
      console.log('✓ Telegram connection test successful');
      return true;
    } catch (error) {
      console.error(`✗ Telegram connection test failed: ${error.message}`);
      return false;
    }
  }

  /**
   * Enable/disable notifications
   * @param {boolean} enabled - Enable or disable
   */
  setEnabled(enabled) {
    this.enabled = enabled && this.telegramBotToken && this.telegramChatId;
    console.log(`Notifications ${this.enabled ? 'enabled' : 'disabled'}`);
  }
}

module.exports = NotificationManager;
