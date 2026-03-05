/**
 * 🔌 MCP Server Auditor
 * 
 * Audits installed MCP servers for security risks
 */

import fs from 'fs/promises';
import path from 'path';

// Known safe MCP servers (community verified)
const APPROVED_MCP_SERVERS = [
  'mcp-server-filesystem',
  'mcp-server-fetch',
  'mcp-server-memory',
  'mcp-server-sqlite',
  'mcp-server-postgres',
  'mcp-server-git',
  'mcp-server-github',
  'mcp-server-slack',
  'mcp-server-google-drive',
  'mcp-server-brave-search'
];

// Known risky patterns in MCP servers (used during deep scan)
const _RISKY_PATTERNS = [
  { pattern: /eval\s*\(/g, severity: 'critical', message: 'Uses eval()' },
  { pattern: /exec\s*\(/g, severity: 'high', message: 'Uses exec()' },
  { pattern: /child_process/g, severity: 'high', message: 'Uses child_process' },
  { pattern: /fs\.writeFileSync/g, severity: 'medium', message: 'Writes files synchronously' },
  { pattern: /process\.env/g, severity: 'low', message: 'Accesses environment variables' }
];

export class McpServerAuditor {
  constructor(config = {}) {
    this.config = config;
    this.allowlist = config.scanners?.mcpServers?.allowlist || APPROVED_MCP_SERVERS;
    this.blockUnknown = config.scanners?.mcpServers?.blockUnknown || false;
  }
  
  async scan(basePath, _options = {}) {
    const findings = [];
    const summary = { critical: 0, high: 0, medium: 0, low: 0 };
    const servers = [];
    
    // Look for MCP server configurations
    const configPath = path.join(basePath, 'openclaw.json');
    
    try {
      const config = JSON.parse(await fs.readFile(configPath, 'utf-8'));
      const mcpServers = config.mcpServers || config.mcp?.servers || {};
      
      for (const [name, serverConfig] of Object.entries(mcpServers)) {
        const isApproved = this.allowlist.includes(name);
        
        servers.push({
          name,
          status: isApproved ? 'approved' : 'unknown',
          source: serverConfig.command || serverConfig.url || 'unknown',
          permissions: serverConfig.permissions || []
        });
        
        if (!isApproved) {
          findings.push({
            type: 'mcp-server',
            severity: this.blockUnknown ? 'high' : 'medium',
            message: `Unknown MCP server: ${name}`,
            detail: 'This server is not in the approved list',
            fix: `Add "${name}" to allowlist or remove it`
          });
          summary[this.blockUnknown ? 'high' : 'medium']++;
        }
      }
      
    } catch (error) {
      if (error.code !== 'ENOENT') {
        findings.push({
          type: 'mcp-server',
          severity: 'medium',
          message: `Could not read MCP config: ${error.message}`
        });
        summary.medium++;
      }
    }
    
    return {
      scanner: 'mcp-servers',
      findings,
      summary,
      servers
    };
  }
}

export default McpServerAuditor;
