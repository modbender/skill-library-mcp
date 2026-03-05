/**
 * MCP Scanner - Security scanner for MCP server configurations
 * Ported from mcp-audit Python tool with ClawGuard threat database integration
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir, platform } from 'os';
import { URL } from 'url';
import { getDetector } from './detector.js';

// Severity levels
export const Severity = {
    CRITICAL: { value: 'CRITICAL', rank: 4, emoji: '🔴', color: '\x1b[91m' },
    HIGH: { value: 'HIGH', rank: 3, emoji: '🟠', color: '\x1b[31m' },
    MEDIUM: { value: 'MEDIUM', rank: 2, emoji: '🟡', color: '\x1b[33m' },
    LOW: { value: 'LOW', rank: 1, emoji: '🔵', color: '\x1b[36m' },
    INFO: { value: 'INFO', rank: 0, emoji: '⚪', color: '\x1b[37m' }
};

// Category types
export const Category = {
    SECRET_EXPOSURE: 'Secret Exposure',
    COMMAND_INJECTION: 'Command Injection',
    PROMPT_INJECTION: 'Prompt Injection',
    TRANSPORT_SECURITY: 'Transport Security',
    PERMISSION_SCOPE: 'Permission Scope',
    CONFIGURATION: 'Configuration',
    KNOWN_VULNERABILITY: 'Known Vulnerability',
    THREAT_DATABASE: 'Threat Database Match'
};

// Secret patterns - ported from Python
const SECRET_PATTERNS = [
    [/(?:sk-(?:proj|svcacct|org)-[a-zA-Z0-9_-]{20,})/gi, 'OpenAI Project/Service API Key'],
    [/(?:sk-ant-[a-zA-Z0-9-]{20,})/gi, 'Anthropic API Key'],
    [/(?:sk-[a-zA-Z0-9]{20,})/gi, 'OpenAI API Key (legacy)'],
    [/(?:ghp_[a-zA-Z0-9]{36})/gi, 'GitHub Personal Access Token'],
    [/(?:gho_[a-zA-Z0-9]{36})/gi, 'GitHub OAuth Token'],
    [/(?:glpat-[a-zA-Z0-9-]{20,})/gi, 'GitLab Access Token'],
    [/(?:xoxb-[0-9]{10,}-[a-zA-Z0-9-]+)/gi, 'Slack Bot Token'],
    [/(?:xoxp-[0-9]{10,}-[a-zA-Z0-9-]+)/gi, 'Slack User Token'],
    [/(?:AKIA[0-9A-Z]{16})/gi, 'AWS Access Key ID'],
    [/(?:eyJ[a-zA-Z0-9_-]{20,}\.eyJ[a-zA-Z0-9_-]{20,})/gi, 'JWT Token'],
    [/(?:[a-f0-9]{32,64})/gi, 'Possible hex secret (32+ chars)'],
    [/(?:AIza[0-9A-Za-z_-]{35})/gi, 'Google API Key'],
    [/(?:SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43})/gi, 'SendGrid API Key'],
    [/(?:sq0[a-z]{3}-[a-zA-Z0-9_-]{22,})/gi, 'Square Token']
];

// Environment variable names that typically hold secrets
const SECRET_ENV_NAMES = [
    /(?:api[_-]?key|apikey)/i,
    /(?:secret|token|password|passwd|credential)/i,
    /(?:auth[_-]?token)/i,
    /(?:private[_-]?key)/i,
    /(?:access[_-]?key)/i,
    /(?:client[_-]?secret)/i,
    /(?:signing[_-]?key)/i,
    /(?:database[_-]?url|db[_-]?password)/i,
    /(?:encryption[_-]?key)/i,
    /(?:webhook[_-]?secret)/i
];

// Dangerous command patterns
const DANGEROUS_COMMANDS = [
    [/\bsudo\b/i, 'sudo usage — runs with elevated privileges'],
    [/\brm\s+-rf?\b/i, 'recursive delete — data loss risk'],
    [/\bchmod\s+777\b/i, 'world-writable permissions'],
    [/\bcurl\b.*\|\s*(bash|sh|zsh)\b/i, 'pipe curl to shell — remote code execution'],
    [/\beval\b/i, 'eval — arbitrary code execution'],
    [/\bexec\b/i, 'exec — process replacement'],
    [/\b(nc|ncat|netcat)\b/i, 'netcat — network backdoor potential'],
    [/\bdd\b\s+if=/i, 'dd — raw disk write potential']
];

// Overly permissive shell commands
const OVERLY_PERMISSIVE_COMMANDS = [
    ['bash', 'Unrestricted bash shell access'],
    ['sh', 'Unrestricted shell access'],
    ['zsh', 'Unrestricted zsh shell access'],
    ['cmd', 'Unrestricted Windows command prompt'],
    ['powershell', 'Unrestricted PowerShell access'],
    ['pwsh', 'Unrestricted PowerShell Core access']
];

// Prompt injection patterns
const PROMPT_INJECTION_PATTERNS = [
    /(?:ignore\s+(?:previous|all|above)\s+(?:instructions?|prompts?|rules?))/i,
    /(?:you\s+are\s+now\s+)/i,
    /(?:disregard\s+(?:your|all|previous))/i,
    /(?:system\s*:\s*you\s+are)/i,
    /(?:new\s+instructions?:)/i,
    /(?:override\s+(?:previous|all))/i,
    /(?:forget\s+(?:everything|all|previous))/i,
    /(?:<\s*system\s*>)/i,
    /(?:\[\s*SYSTEM\s*\])/i
];

/**
 * Server information structure
 */
class ServerInfo {
    constructor(name, configPath = '') {
        this.name = name;
        this.command = '';
        this.args = [];
        this.env = {};
        this.url = '';
        this.transport = 'stdio';
        this.configPath = configPath;
    }
}

/**
 * Security finding structure
 */
class Finding {
    constructor(severity, category, serverName, title, description, evidence = '', fix = '', cwe = '') {
        this.severity = severity;
        this.category = category;
        this.serverName = serverName;
        this.title = title;
        this.description = description;
        this.evidence = evidence;
        this.fix = fix;
        this.cwe = cwe;
    }
}

/**
 * Audit report structure
 */
class AuditReport {
    constructor() {
        this.configsScanned = 0;
        this.serversScanned = 0;
        this.findings = [];
        this.servers = [];
        this.configPaths = [];
    }
}

/**
 * Discover MCP config files across known locations
 */
export function getMcpConfigPaths() {
    const home = homedir();
    const system = platform();
    const paths = [];

    let candidates = [];

    if (system === 'darwin') { // macOS
        candidates = [
            // Claude Desktop
            [join(home, 'Library/Application Support/Claude/claude_desktop_config.json'), 'Claude Desktop'],
            // Cursor
            [join(home, '.cursor/mcp.json'), 'Cursor'],
            [join(home, 'Library/Application Support/Cursor/User/globalStorage/mcp.json'), 'Cursor (Global)'],
            // VS Code
            [join(home, '.vscode/mcp.json'), 'VS Code'],
            [join(home, 'Library/Application Support/Code/User/globalStorage/mcp.json'), 'VS Code (Global)'],
            // Windsurf
            [join(home, '.windsurf/mcp.json'), 'Windsurf'],
            [join(home, '.codeium/windsurf/mcp_config.json'), 'Windsurf (Codeium)'],
            // Claude Code
            [join(home, '.claude.json'), 'Claude Code'],
            // Clawdbot
            [join(home, '.clawdbot/clawdbot.json'), 'Clawdbot']
        ];
    } else if (system === 'linux') {
        candidates = [
            [join(home, '.config/Claude/claude_desktop_config.json'), 'Claude Desktop'],
            [join(home, '.cursor/mcp.json'), 'Cursor'],
            [join(home, '.vscode/mcp.json'), 'VS Code'],
            [join(home, '.claude.json'), 'Claude Code']
        ];
    } else { // Windows
        const appdata = process.env.APPDATA || '';
        candidates = [
            [join(appdata, 'Claude/claude_desktop_config.json'), 'Claude Desktop'],
            [join(home, '.cursor/mcp.json'), 'Cursor'],
            [join(home, '.vscode/mcp.json'), 'VS Code'],
            [join(home, '.claude.json'), 'Claude Code']
        ];
    }

    // Also check CWD for project configs
    candidates.push(
        [join(process.cwd(), '.mcp.json'), 'Project (.mcp.json)'],
        [join(process.cwd(), 'mcp.json'), 'Project (mcp.json)']
    );

    for (const [path, name] of candidates) {
        if (existsSync(path)) {
            paths.push({ path, name });
        }
    }

    return paths;
}

/**
 * Parse an MCP config file and extract server definitions
 */
export function parseMcpConfig(configPath) {
    const servers = [];

    try {
        const content = readFileSync(configPath, 'utf8');
        const data = JSON.parse(content);

        // Handle different config formats
        let mcpServers = {};

        // Claude Desktop / Cursor / VS Code format: {"mcpServers": {...}}
        if (data.mcpServers) {
            mcpServers = data.mcpServers;
        }
        // Some configs use "servers"
        else if (data.servers) {
            mcpServers = data.servers;
        }
        // Clawdbot format: nested in plugins or MCP section
        else if (data.mcp && typeof data.mcp === 'object' && data.mcp.servers) {
            mcpServers = data.mcp.servers;
        }
        // Claude Code format: mcpServers can be in projects
        else if (data.projects) {
            for (const [projPath, projData] of Object.entries(data.projects)) {
                if (projData.mcpServers) {
                    for (const [name, srv] of Object.entries(projData.mcpServers)) {
                        servers.push(parseServerEntry(name, srv, configPath));
                    }
                }
            }
            return servers;
        }

        for (const [name, srv] of Object.entries(mcpServers)) {
            servers.push(parseServerEntry(name, srv, configPath));
        }
    } catch (error) {
        // Silently ignore parsing errors
        console.warn(`Warning: Could not parse config ${configPath}: ${error.message}`);
    }

    return servers;
}

/**
 * Parse a single server entry from config
 */
function parseServerEntry(name, srv, configPath) {
    const info = new ServerInfo(name, configPath);

    if (typeof srv === 'object' && srv !== null) {
        info.command = srv.command || '';
        info.args = srv.args || [];
        info.env = srv.env || {};
        info.url = srv.url || '';

        // Determine transport
        if (info.url) {
            if (info.url.toLowerCase().includes('sse') || info.url.startsWith('http')) {
                info.transport = 'sse';
            } else if (info.url.startsWith('ws')) {
                info.transport = 'websocket';
            }
        } else {
            info.transport = 'stdio';
        }
    }

    return info;
}

/**
 * Check for hardcoded secrets in env vars and args
 */
function checkSecretExposure(server) {
    const findings = [];

    // Check env var values for secret patterns
    for (const [key, value] of Object.entries(server.env)) {
        if (!value || value.startsWith('${') || value.startsWith('$')) {
            continue; // Skip env var references (good practice)
        }

        // Check if the env var NAME suggests it holds a secret
        const isSecretName = SECRET_ENV_NAMES.some(pattern => pattern.test(key));

        // Check if the VALUE looks like a secret
        for (const [pattern, secretType] of SECRET_PATTERNS) {
            const match = pattern.test(String(value));
            if (match) {
                const sev = isSecretName ? Severity.CRITICAL : Severity.HIGH;
                const masked = value.length > 12 ? value.substring(0, 4) + '...' + value.substring(value.length - 4) : '***';
                findings.push(new Finding(
                    sev,
                    Category.SECRET_EXPOSURE,
                    server.name,
                    `Hardcoded ${secretType} in env var '${key}'`,
                    `The environment variable '${key}' contains what appears to be a ${secretType}. ` +
                    `Secrets in config files can be exposed through logs, version control, or backups.`,
                    `${key}=${masked}`,
                    `Use environment variable references instead: "${key}": "\${env:${key}}" or set it in your shell profile.`,
                    'CWE-798'
                ));
                break; // Only report first match per env var
            }
        }

        // Even if pattern doesn't match, flag secret-named env vars with inline values
        if (isSecretName && !SECRET_PATTERNS.some(([pattern]) => pattern.test(String(value)))) {
            if (String(value).length > 8 && !value.startsWith('${')) {
                findings.push(new Finding(
                    Severity.MEDIUM,
                    Category.SECRET_EXPOSURE,
                    server.name,
                    `Potential secret in env var '${key}'`,
                    `The env var name '${key}' suggests it holds a secret, and the value is hardcoded.`,
                    `${key}=<redacted, ${String(value).length} chars>`,
                    `Move this to an environment variable or secrets manager.`,
                    'CWE-798'
                ));
            }
        }
    }

    // Check args for embedded secrets
    const argsStr = server.args.map(String).join(' ');
    for (const [pattern, secretType] of SECRET_PATTERNS.slice(0, 8)) { // Skip the generic hex one for args
        if (pattern.test(argsStr)) {
            findings.push(new Finding(
                Severity.HIGH,
                Category.SECRET_EXPOSURE,
                server.name,
                `Possible ${secretType} in command arguments`,
                'Command arguments may contain secrets. These can appear in process listings (ps) and logs.',
                `args contain pattern matching ${secretType}`,
                'Pass secrets via environment variables instead of command arguments.',
                'CWE-214'
            ));
        }
    }

    return findings;
}

/**
 * Check for command injection risks
 */
function checkCommandInjection(server) {
    const findings = [];
    const fullCmd = `${server.command} ${server.args.map(String).join(' ')}`;

    // Check if command is an unrestricted shell
    const cmdBase = server.command ? server.command.split('/').pop() : '';
    for (const [shell, desc] of OVERLY_PERMISSIVE_COMMANDS) {
        if (cmdBase === shell || server.args.some(arg => String(arg) === shell)) {
            findings.push(new Finding(
                Severity.HIGH,
                Category.COMMAND_INJECTION,
                server.name,
                `Unrestricted shell access via '${shell}'`,
                `${desc}. An AI model with access to this server can execute ANY command on your system.`,
                `command: ${server.command} ${server.args.slice(0, 3).map(String).join(' ')}`,
                'Use a purpose-built MCP server instead of raw shell access. If shell access is needed, use allowlists.',
                'CWE-78'
            ));
        }
    }

    // Check for dangerous command patterns in args
    for (const [pattern, desc] of DANGEROUS_COMMANDS) {
        if (pattern.test(fullCmd)) {
            findings.push(new Finding(
                Severity.MEDIUM,
                Category.COMMAND_INJECTION,
                server.name,
                `Dangerous command pattern: ${desc}`,
                'The server configuration includes potentially dangerous command patterns.',
                fullCmd.substring(0, 100),
                'Review if this level of access is necessary. Consider restricting to specific operations.',
                'CWE-78'
            ));
        }
    }

    // Check for wildcard in npx/uvx (auto-download from registry)
    if (['npx', 'uvx', 'bunx', 'pnpx'].includes(server.command)) {
        // Find the actual package name (skip flags like -y, --yes, -p)
        let packageName = 'unknown';
        for (const arg of server.args) {
            if (!String(arg).startsWith('-')) {
                packageName = String(arg);
                break;
            }
        }
        // Check if it's from a suspicious source or unversioned
        if (packageName !== 'unknown' && !packageName.split('/').pop().includes('@')) { // no version pin
            findings.push(new Finding(
                Severity.MEDIUM,
                Category.COMMAND_INJECTION,
                server.name,
                `Unversioned auto-download via ${server.command}`,
                `Using ${server.command} auto-downloads and executes '${packageName}' from the registry ` +
                `without a pinned version. Vulnerable to typosquatting and supply chain attacks.`,
                `${server.command} ${server.args.map(String).join(' ')}`,
                `Pin to a specific version: ${server.command} ${packageName}@<version>, or install locally first.`,
                'CWE-829'
            ));
        }
    }

    return findings;
}

/**
 * Check transport configuration for security issues
 */
function checkTransportSecurity(server) {
    const findings = [];

    if (server.url) {
        // Check for unencrypted HTTP
        if (server.url.startsWith('http://') && !server.url.includes('localhost') && !server.url.includes('127.0.0.1')) {
            findings.push(new Finding(
                Severity.HIGH,
                Category.TRANSPORT_SECURITY,
                server.name,
                'Unencrypted HTTP transport to remote server',
                'MCP traffic is sent over unencrypted HTTP to a non-localhost address. ' +
                'Tool calls, responses, and potentially secrets can be intercepted.',
                `url: ${server.url}`,
                'Use HTTPS (TLS) for remote MCP server connections.',
                'CWE-319'
            ));
        }

        // Check for wildcard/public-facing SSE endpoints
        if (server.url.includes('0.0.0.0')) {
            findings.push(new Finding(
                Severity.HIGH,
                Category.TRANSPORT_SECURITY,
                server.name,
                'MCP server bound to all interfaces (0.0.0.0)',
                'The server is accessible from all network interfaces, potentially exposing it to the network.',
                `url: ${server.url}`,
                'Bind to 127.0.0.1 (localhost) unless remote access is explicitly needed.',
                'CWE-668'
            ));
        }

        // Check for auth tokens in URL
        if (/[?&](token|key|auth|secret)=/i.test(server.url)) {
            findings.push(new Finding(
                Severity.MEDIUM,
                Category.TRANSPORT_SECURITY,
                server.name,
                'Authentication token in URL',
                'Credentials passed as URL parameters can be logged by proxies, browsers, and servers.',
                server.url.replace(/([?&](token|key|auth|secret)=)[^&]+/gi, '$1<REDACTED>'),
                'Pass authentication via headers instead of URL parameters.',
                'CWE-598'
            ));
        }
    }

    return findings;
}

/**
 * Check for overly broad permissions
 */
function checkPermissionScope(server) {
    const findings = [];
    const argsStr = server.args.map(String).join(' ');

    // Check for filesystem root access
    if (/(?:^|\s)\/$/.test(argsStr) || /["\s]\/\s/.test(argsStr) || /--root\s+\//.test(argsStr) || server.args.some(arg => String(arg) === '/')) {
        findings.push(new Finding(
            Severity.MEDIUM,
            Category.PERMISSION_SCOPE,
            server.name,
            'Root filesystem access',
            'The server has been given access to the root filesystem. This is unnecessarily broad.',
            argsStr.substring(0, 100),
            'Restrict to specific directories needed for the task.',
            'CWE-250'
        ));
    }

    // Check for home directory access when narrower would work
    const home = homedir();
    if (argsStr.includes(home) || argsStr.includes('~')) {
        findings.push(new Finding(
            Severity.LOW,
            Category.PERMISSION_SCOPE,
            server.name,
            'Full home directory access',
            'The server has access to the entire home directory. Consider narrowing to project directories.',
            `Path includes ${home} or ~`,
            'Restrict to specific project directories.'
        ));
    }

    // Docker without restrictions
    if (server.command.toLowerCase().includes('docker') || server.args.some(arg => String(arg).toLowerCase().includes('docker'))) {
        if (['--privileged', '-v /:/'].some(dangerous => argsStr.includes(dangerous)) || argsStr.includes('host')) {
            findings.push(new Finding(
                Severity.HIGH,
                Category.PERMISSION_SCOPE,
                server.name,
                'Privileged Docker access',
                'Docker is running with elevated privileges or host filesystem access.',
                argsStr.substring(0, 100),
                'Use non-privileged containers with minimal volume mounts.',
                'CWE-250'
            ));
        }
    }

    return findings;
}

/**
 * Check for general configuration problems
 */
function checkConfigurationIssues(server) {
    const findings = [];

    // Empty or missing command for stdio servers
    if (server.transport === 'stdio' && !server.command) {
        findings.push(new Finding(
            Severity.MEDIUM,
            Category.CONFIGURATION,
            server.name,
            'Missing command for stdio server',
            'No command specified for this stdio-transport server. It cannot start.',
            'command: (empty)',
            'Specify the command to launch the MCP server.'
        ));
    }

    // Node server without explicit node path
    if (['node', 'python', 'python3'].includes(server.command)) {
        const script = server.args[0] ? String(server.args[0]) : '';
        if (script && !script.startsWith('/')) {
            findings.push(new Finding(
                Severity.LOW,
                Category.CONFIGURATION,
                server.name,
                'Relative path for server script',
                `Using relative path '${script}' — this depends on the working directory at launch time.`,
                `${server.command} ${script}`,
                'Use absolute paths for reliability.'
            ));
        }
    }

    return findings;
}

/**
 * Check for prompt injection patterns embedded in config
 */
function checkPromptInjectionInConfig(server) {
    const findings = [];

    // Check all string values in the config for injection patterns
    const allStrings = [server.command, ...server.args.map(String), ...Object.values(server.env)];
    const combined = allStrings.join(' ');

    for (const pattern of PROMPT_INJECTION_PATTERNS) {
        const match = pattern.exec(combined);
        if (match) {
            findings.push(new Finding(
                Severity.CRITICAL,
                Category.PROMPT_INJECTION,
                server.name,
                'Prompt injection pattern in server config',
                'The server configuration contains text that matches known prompt injection patterns. ' +
                'This could manipulate the AI model\'s behavior.',
                match[0].substring(0, 80),
                'Remove or sanitize the suspicious text. If this is from a third-party server, consider not using it.',
                'CWE-74'
            ));
        }
    }

    return findings;
}

/**
 * Check server against ClawGuard threat database
 */
async function checkThreatDatabase(server) {
    const findings = [];
    const detector = getDetector();

    // Check server URL against threat database
    if (server.url) {
        try {
            const urlResult = await detector.checkUrl(server.url);
            if (urlResult.result !== 'safe' && urlResult.matches.length > 0) {
                for (const match of urlResult.matches) {
                    findings.push(new Finding(
                        Severity.CRITICAL,
                        Category.THREAT_DATABASE,
                        server.name,
                        `Threat database match: ${match.reason}`,
                        `The server URL '${server.url}' matches a known threat in ClawGuard's database: ${match.reason}. ` +
                        `Threat tier: ${match.tier}/6, Tags: ${match.tags || 'none'}.`,
                        `URL: ${server.url} (matched: ${match.matched_value})`,
                        'Remove this server from your configuration immediately. Use only trusted MCP servers.',
                        match.cwe || ''
                    ));
                }
            }
        } catch (error) {
            console.warn(`Warning: Could not check URL ${server.url} against threat database: ${error.message}`);
        }
    }

    // Check package name for npx/uvx commands
    if (['npx', 'uvx', 'bunx', 'pnpx'].includes(server.command)) {
        let packageName = 'unknown';
        for (const arg of server.args) {
            if (!String(arg).startsWith('-')) {
                packageName = String(arg);
                break;
            }
        }

        if (packageName !== 'unknown') {
            try {
                const skillResult = await detector.checkSkill(packageName);
                if (skillResult.result !== 'safe' && skillResult.matches.length > 0) {
                    for (const match of skillResult.matches) {
                        findings.push(new Finding(
                            Severity.CRITICAL,
                            Category.THREAT_DATABASE,
                            server.name,
                            `Malicious package detected: ${match.reason}`,
                            `The package '${packageName}' matches a known threat in ClawGuard's database: ${match.reason}. ` +
                            `Threat tier: ${match.tier}/6, Tags: ${match.tags || 'none'}.`,
                            `Package: ${packageName} (matched: ${match.matched_value})`,
                            'Do not install or use this package. Find an alternative from a trusted source.',
                            match.cwe || ''
                        ));
                    }
                }
            } catch (error) {
                console.warn(`Warning: Could not check package ${packageName} against threat database: ${error.message}`);
            }
        }
    }

    return findings;
}

/**
 * Run all security checks against a single server
 */
export async function auditServer(serverInfo) {
    const findings = [];
    findings.push(...checkSecretExposure(serverInfo));
    findings.push(...checkCommandInjection(serverInfo));
    findings.push(...checkTransportSecurity(serverInfo));
    findings.push(...checkPermissionScope(serverInfo));
    findings.push(...checkConfigurationIssues(serverInfo));
    findings.push(...checkPromptInjectionInConfig(serverInfo));
    findings.push(...(await checkThreatDatabase(serverInfo)));
    return findings;
}

/**
 * Run a full audit across all discovered configs
 */
export async function scanMcpConfigs(configPaths = null) {
    const report = new AuditReport();

    if (configPaths === null) {
        configPaths = getMcpConfigPaths();
    }

    report.configPaths = configPaths.map(c => c.path);
    report.configsScanned = configPaths.length;

    for (const config of configPaths) {
        const servers = parseMcpConfig(config.path);
        for (const server of servers) {
            report.servers.push(server);
            report.serversScanned++;
            const findings = await auditServer(server);
            report.findings.push(...findings);
        }
    }

    // Sort findings by severity
    report.findings.sort((a, b) => b.severity.rank - a.severity.rank);
    return report;
}