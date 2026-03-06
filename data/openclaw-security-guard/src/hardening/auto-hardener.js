/**
 * 🔒 Auto Hardener
 * 
 * Automatically applies security fixes to OpenClaw configuration
 */

import fs from 'fs/promises';
import path from 'path';

export class AutoHardener {
  constructor(config = {}) {
    this.config = config;
  }
  
  async applyFixes(basePath, issues) {
    const configPath = path.join(basePath, 'openclaw.json');
    
    let config = {};
    try {
      config = JSON.parse(await fs.readFile(configPath, 'utf-8'));
    } catch {
      // Start with empty config
    }
    
    // Apply each auto-fixable issue
    for (const issue of issues) {
      if (issue.autoFixable && issue.autoFix) {
        config = issue.autoFix(config);
      }
    }
    
    // Write updated config
    await fs.writeFile(
      configPath,
      JSON.stringify(config, null, 2),
      'utf-8'
    );
    
    return config;
  }
  
  /**
   * Generate hardened config from scratch
   */
  generateSecureConfig() {
    return {
      gateway: {
        bind: 'loopback',
        auth: {
          mode: 'token'
        }
      },
      agents: {
        defaults: {
          sandbox: {
            mode: 'always',
            allowlist: ['read', 'write', 'sessions_list'],
            denylist: ['browser', 'canvas', 'nodes', 'gateway', 'cron']
          },
          tools: {
            elevated: {
              enabled: false,
              requireApproval: true
            }
          }
        }
      },
      channels: {
        whatsapp: {
          dmPolicy: 'pairing',
          groups: {
            '*': {
              requireMention: true,
              activation: 'mention'
            }
          }
        },
        telegram: {
          dmPolicy: 'pairing'
        },
        discord: {
          dm: {
            policy: 'pairing'
          }
        }
      },
      security: {
        rateLimiting: {
          enabled: true,
          maxRequestsPerMinute: 30,
          maxTokensPerHour: 100000
        },
        audit: {
          enabled: true,
          logLevel: 'info'
        }
      }
    };
  }
}

export default AutoHardener;
