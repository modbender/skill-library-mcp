/**
 * ClawGuard OpenClaw Plugin
 * Hooks into before_tool_call to auto-check commands and URLs
 */

import { getDetector, RESULT, EXIT_CODE } from './lib/detector.js';
import { loadConfig } from './lib/config.js';
import { formatApprovalMessage } from './lib/discord-approval.js';

/**
 * Plugin metadata
 */
export const metadata = {
    name: 'clawguard-security',
    version: '1.3.0',
    description: 'Automatic security checks for all tool calls with graduated approval levels',
    hooks: ['before_tool_call']
};

/**
 * Extract commands from exec tool calls
 */
function extractCommand(toolCall) {
    if (toolCall.tool === 'exec' && toolCall.parameters?.command) {
        return toolCall.parameters.command;
    }
    return null;
}

/**
 * Extract URLs from browser/web_fetch tool calls
 */
function extractUrls(toolCall) {
    const urls = [];
    
    if (toolCall.tool === 'web_fetch' && toolCall.parameters?.url) {
        urls.push(toolCall.parameters.url);
    }
    
    if (toolCall.tool === 'browser') {
        if (toolCall.parameters?.targetUrl) {
            urls.push(toolCall.parameters.targetUrl);
        }
        if (toolCall.parameters?.action === 'open' && toolCall.parameters?.targetUrl) {
            urls.push(toolCall.parameters.targetUrl);
        }
    }
    
    return urls;
}

/**
 * Send Discord approval request and wait for response
 * This function expects to be called from OpenClaw context with access to message tool
 */
async function requestDiscordApproval(message, channelId, timeout, context) {
    if (!context || !context.message) {
        console.error('ClawGuard: message tool not available in context');
        return false;
    }
    
    try {
        // Send approval request
        const sentMessage = await context.message({
            action: 'send',
            target: channelId,
            message: message
        });
        
        if (!sentMessage || !sentMessage.messageId) {
            console.error('ClawGuard: Failed to send approval message');
            return false;
        }
        
        // Add reaction prompts
        await context.message({
            action: 'react',
            messageId: sentMessage.messageId,
            emoji: '✅'
        });
        
        await context.message({
            action: 'react',
            messageId: sentMessage.messageId,
            emoji: '❌'
        });
        
        // Get bot's own user ID to filter out its reactions
        const botUserId = context.botUserId || null;
        
        // Wait for reaction with timeout
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
            // Poll for reactions
            const reactions = await context.message({
                action: 'reactions',
                messageId: sentMessage.messageId
            });
            
            if (reactions) {
                // Filter out bot's own reactions — only count human reactions
                const humanReaction = (r, emoji) => {
                    if (r.emoji !== emoji) return false;
                    const humanUsers = botUserId 
                        ? r.users.filter(u => u.id !== botUserId)
                        : r.users;
                    return humanUsers.length > 0;
                };
                
                // Check for approval (✅) from a human
                if (reactions.find(r => humanReaction(r, '✅'))) {
                    return true;
                }
                
                // Check for denial (❌) from a human
                if (reactions.find(r => humanReaction(r, '❌'))) {
                    return false;
                }
            }
            
            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Timeout
        await context.message({
            action: 'send',
            target: channelId,
            message: '⏱️ Approval request timed out. Denying action for safety.'
        });
        
        return false;
        
    } catch (error) {
        console.error(`ClawGuard approval error: ${error.message}`);
        return false; // Deny on error
    }
}

/**
 * Check if a tool call is a read-only operation (allowed at all levels)
 */
function isReadOnlyOperation(toolCall) {
    // File reads
    if (toolCall.tool === 'Read') {
        return true;
    }
    
    // Web fetch GETs (but not POSTs)
    if (toolCall.tool === 'web_fetch') {
        return true; // web_fetch is read-only by design
    }
    
    return false;
}

/**
 * Check if URL is in the known-safe list
 */
function isKnownSafeUrl(url) {
    try {
        const parsed = new URL(url);
        const hostname = parsed.hostname.toLowerCase();
        
        // Known safe domains
        const safeDomains = [
            'github.com',
            'gitlab.com',
            'npmjs.com',
            'pypi.org',
            'rubygems.org',
            'crates.io',
            'docker.com',
            'anthropic.com',
            'openai.com',
            'google.com',
            'microsoft.com',
            'stackoverflow.com',
            'wikipedia.org'
        ];
        
        for (const safe of safeDomains) {
            if (hostname === safe || hostname.endsWith('.' + safe)) {
                return true;
            }
        }
        
        return false;
    } catch {
        return false;
    }
}

/**
 * Before tool call hook
 */
export async function before_tool_call(toolCall, context) {
    const config = loadConfig();
    const detector = getDetector();
    const level = config.level || 0; // Default to level 0 (silent)
    
    // Level 3 (paranoid): Ask approval for everything except reads
    if (level === 3) {
        if (!isReadOnlyOperation(toolCall)) {
            // Need approval for this operation
            const message = `🔒 **ClawGuard Level 3 (Paranoid) - Approval Required**\n\n` +
                           `**Tool:** ${toolCall.tool}\n` +
                           `**Action:** ${JSON.stringify(toolCall.parameters, null, 2).substring(0, 300)}\n\n` +
                           `React with ✅ to approve or ❌ to deny`;
            
            if (config.discord.enabled && config.discord.channelId) {
                const approved = await requestDiscordApproval(
                    message,
                    config.discord.channelId,
                    config.discord.timeout || 60000,
                    context
                );
                
                if (!approved) {
                    console.log(`🛡️ ClawGuard Level 3: User denied approval`);
                    return {
                        block: true,
                        reason: 'Level 3 (paranoid): User approval required'
                    };
                }
                
                console.log(`✅ ClawGuard Level 3: User approved`);
            } else {
                console.log(`⚠️ ClawGuard Level 3: Discord approval not configured, blocking by default`);
                return {
                    block: true,
                    reason: 'Level 3 (paranoid): Discord approval not configured'
                };
            }
        }
    }
    
    // Extract what to check
    const command = extractCommand(toolCall);
    const urls = extractUrls(toolCall);
    
    // Level 2 (strict): Ask approval for ALL exec/shell commands and unknown URLs
    if (level >= 2) {
        if (command) {
            // All commands need approval at level 2
            const message = `⚠️ **ClawGuard Level 2 (Strict) - Command Approval**\n\n` +
                           `**Command:** \`${command.substring(0, 200)}${command.length > 200 ? '...' : ''}\`\n\n` +
                           `React with ✅ to approve or ❌ to deny`;
            
            if (config.discord.enabled && config.discord.channelId) {
                const approved = await requestDiscordApproval(
                    message,
                    config.discord.channelId,
                    config.discord.timeout || 60000,
                    context
                );
                
                if (!approved) {
                    console.log(`🛡️ ClawGuard Level 2: Command denied by user`);
                    return {
                        block: true,
                        reason: 'Level 2 (strict): User denied command execution'
                    };
                }
                
                console.log(`✅ ClawGuard Level 2: Command approved`);
            } else {
                console.log(`⚠️ ClawGuard Level 2: Discord approval not configured, blocking command`);
                return {
                    block: true,
                    reason: 'Level 2 (strict): Discord approval not configured'
                };
            }
        }
        
        // Check for unknown URLs at level 2
        for (const url of urls) {
            if (!isKnownSafeUrl(url)) {
                const message = `⚠️ **ClawGuard Level 2 (Strict) - Unknown URL**\n\n` +
                               `**URL:** ${url}\n\n` +
                               `This URL is not in the known-safe list.\n` +
                               `React with ✅ to approve or ❌ to deny`;
                
                if (config.discord.enabled && config.discord.channelId) {
                    const approved = await requestDiscordApproval(
                        message,
                        config.discord.channelId,
                        config.discord.timeout || 60000,
                        context
                    );
                    
                    if (!approved) {
                        console.log(`🛡️ ClawGuard Level 2: Unknown URL denied by user`);
                        return {
                            block: true,
                            reason: 'Level 2 (strict): User denied unknown URL'
                        };
                    }
                    
                    console.log(`✅ ClawGuard Level 2: Unknown URL approved`);
                } else {
                    console.log(`⚠️ ClawGuard Level 2: Discord approval not configured, blocking unknown URL`);
                    return {
                        block: true,
                        reason: 'Level 2 (strict): Discord approval not configured'
                    };
                }
            }
        }
    }
    
    // ALWAYS run threat DB checks (at all levels)
    // Check command if present
    if (command) {
        const result = await detector.checkCommand(command);
        
        if (result.exitCode === EXIT_CODE.BLOCK) {
            // BLOCKED - prevent execution at ALL levels
            console.log(`🛡️ ClawGuard BLOCKED: ${result.message}`);
            if (result.primaryThreat) {
                console.log(`   Threat: ${result.primaryThreat.name} (${result.primaryThreat.id})`);
            }
            return { 
                block: true,
                reason: `Security threat detected: ${result.primaryThreat?.name || 'Unknown threat'}`
            };
        }
        
        if (result.exitCode === EXIT_CODE.WARN) {
            // WARNING - behavior depends on level
            if (level === 0) {
                // Level 0 (silent): Log but allow
                console.log(`⚠️ ClawGuard WARNING (Level 0 - logged, allowing): ${result.message}`);
                if (result.primaryThreat) {
                    console.log(`   Threat: ${result.primaryThreat.name} (${result.primaryThreat.id})`);
                }
                return { allow: true };
            } else {
                // Level 1+ (cautious/strict/paranoid): Request approval
                if (config.discord.enabled && config.discord.channelId) {
                    console.log(`⚠️ ClawGuard WARNING: Requesting Discord approval...`);
                    
                    const approvalMessage = formatApprovalMessage(command, 'command', result.primaryThreat);
                    const approved = await requestDiscordApproval(
                        approvalMessage,
                        config.discord.channelId,
                        config.discord.timeout || 60000,
                        context
                    );
                    
                    if (!approved) {
                        console.log(`🛡️ ClawGuard: Discord approval denied/timeout`);
                        return {
                            block: true,
                            reason: 'User denied or approval timeout'
                        };
                    }
                    
                    console.log(`✅ ClawGuard: Discord approval granted`);
                    return { allow: true };
                } else {
                    // No Discord - behavior depends on level
                    if (level === 0) {
                        console.log(`⚠️ ClawGuard WARNING: ${result.message}`);
                        console.log(`   Level 0: Allowing (logged to audit trail)`);
                        return { allow: true };
                    } else {
                        console.log(`⚠️ ClawGuard WARNING: Discord approval not configured, blocking at level ${level}`);
                        return {
                            block: true,
                            reason: `Level ${level}: Discord approval required but not configured`
                        };
                    }
                }
            }
        }
    }
    
    // Check URLs if present
    for (const url of urls) {
        const result = await detector.checkUrl(url);
        
        if (result.exitCode === EXIT_CODE.BLOCK) {
            // BLOCKED - prevent execution at ALL levels
            console.log(`🛡️ ClawGuard BLOCKED URL: ${result.message}`);
            if (result.primaryThreat) {
                console.log(`   Threat: ${result.primaryThreat.name} (${result.primaryThreat.id})`);
            }
            return {
                block: true,
                reason: `Malicious URL detected: ${result.primaryThreat?.name || 'Unknown threat'}`
            };
        }
        
        if (result.exitCode === EXIT_CODE.WARN) {
            // WARNING - behavior depends on level
            if (level === 0) {
                // Level 0 (silent): Log but allow
                console.log(`⚠️ ClawGuard WARNING URL (Level 0 - logged, allowing): ${result.message}`);
                if (result.primaryThreat) {
                    console.log(`   Threat: ${result.primaryThreat.name} (${result.primaryThreat.id})`);
                }
                return { allow: true };
            } else {
                // Level 1+ (cautious/strict/paranoid): Request approval
                if (config.discord.enabled && config.discord.channelId) {
                    console.log(`⚠️ ClawGuard WARNING: Requesting Discord approval for URL...`);
                    
                    const approvalMessage = formatApprovalMessage(url, 'url', result.primaryThreat);
                    const approved = await requestDiscordApproval(
                        approvalMessage,
                        config.discord.channelId,
                        config.discord.timeout || 60000,
                        context
                    );
                    
                    if (!approved) {
                        console.log(`🛡️ ClawGuard: Discord approval denied/timeout`);
                        return {
                            block: true,
                            reason: 'User denied or approval timeout'
                        };
                    }
                    
                    console.log(`✅ ClawGuard: Discord approval granted`);
                    return { allow: true };
                } else {
                    if (level === 0) {
                        console.log(`⚠️ ClawGuard WARNING: ${result.message}`);
                        console.log(`   Level 0: Allowing (logged to audit trail)`);
                        return { allow: true };
                    } else {
                        console.log(`⚠️ ClawGuard WARNING: Discord approval not configured, blocking at level ${level}`);
                        return {
                            block: true,
                            reason: `Level ${level}: Discord approval required but not configured`
                        };
                    }
                }
            }
        }
    }
    
    // All checks passed
    return { allow: true };
}

/**
 * Plugin initialization
 */
export function init(context) {
    console.log('🛡️ ClawGuard security plugin loaded (v1.3.0)');
    
    const config = loadConfig();
    const level = config.level || 0;
    const levelNames = ['silent', 'cautious', 'strict', 'paranoid'];
    
    console.log(`   Security level: ${level} (${levelNames[level]})`);
    
    if (level === 0) {
        console.log('   → Threat DB checks only, warnings logged silently');
    } else if (level === 1) {
        console.log('   → Asking approval for WARNING-level threats');
    } else if (level === 2) {
        console.log('   → Asking approval for warnings + all commands/unknown URLs');
    } else if (level === 3) {
        console.log('   → Asking approval for everything (paranoid mode)');
    }
    
    if (config.discord.enabled && config.discord.channelId) {
        console.log(`   Discord approval enabled (channel: ${config.discord.channelId})`);
    } else {
        if (level > 0) {
            console.log('   ⚠️  Discord approval NOT configured (higher levels need it!)');
        }
    }
    
    if (config.audit.enabled) {
        console.log('   Audit trail enabled');
    }
}

export default {
    metadata,
    init,
    before_tool_call
};
