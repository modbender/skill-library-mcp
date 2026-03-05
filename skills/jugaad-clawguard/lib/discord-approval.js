/**
 * ClawGuard Discord Approval Handler
 * Sends approval requests to Discord for warnings
 */

import { loadConfig } from './config.js';

// Note: Actual approval request logic lives in openclaw-plugin.js which has
// access to the OpenClaw message context. This module exports only the
// message formatter for use by the plugin.

/**
 * Format the approval message
 */
function formatApprovalMessage(input, type, threat) {
    const emoji = {
        url: '🔗',
        command: '⚡',
        skill: '🧩',
        message: '💬'
    };
    
    let message = `⚠️ **ClawGuard Warning - Approval Required**\n\n`;
    message += `${emoji[type] || '🔍'} **Type:** ${type.toUpperCase()}\n`;
    message += `**Input:** \`${input.substring(0, 200)}${input.length > 200 ? '...' : ''}\`\n\n`;
    
    if (threat) {
        message += `**Threat Detected:** ${threat.name}\n`;
        message += `**Severity:** ${threat.severity.toUpperCase()}\n`;
        message += `**ID:** ${threat.id}\n\n`;
        
        if (threat.teaching_prompt) {
            message += `**Why this is flagged:**\n${threat.teaching_prompt.substring(0, 300)}${threat.teaching_prompt.length > 300 ? '...' : ''}\n\n`;
        }
    }
    
    message += `**Do you want to proceed?**\n`;
    message += `React with ✅ to approve or ❌ to deny (timeout: ${Math.floor((loadConfig().discord.timeout || 60000) / 1000)}s)`;
    
    return message;
}

export { formatApprovalMessage };
