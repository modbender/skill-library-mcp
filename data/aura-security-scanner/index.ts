/**
 * AURA Security Scanner - OpenClaw Skill Handler
 *
 * Scans AI agent skills for malware, prompt injection, and dangerous permissions.
 * Calls the AURA Security API for comprehensive analysis.
 */

// Configuration
const AURA_API_URL = process.env.AURA_API_URL || 'https://api.aurasecurity.io';
const SCAN_TIMEOUT = 30000; // 30 seconds

// Types
interface SkillScanResult {
  skillId: string;
  name: string;
  source: string;
  sourceUrl?: string;
  verdict: 'SAFE' | 'WARNING' | 'DANGEROUS' | 'BLOCKED';
  riskScore: number;
  malwarePatterns: Array<{
    match: string;
    severity: string;
    category: string;
    description: string;
  }>;
  permissionIssues: Array<{
    permission: string;
    severity: string;
    reason: string;
  }>;
  promptInjectionRisks: Array<{
    match: string;
    severity: string;
    description: string;
  }>;
  networkRisks: Array<{
    url: string;
    severity: string;
    reason: string;
  }>;
  verifiedBadge: boolean;
  badgeReason: string;
  summary: string;
  recommendations: string[];
  scanTime: number;
}

interface ScanRequest {
  skillUrl: string;
  format?: 'openclaw' | 'mcp' | 'langchain' | 'auto';
  includeRepoTrust?: boolean;
}

// Main handler - called by OpenClaw
export async function handler(input: { query: string; context?: any }): Promise<string> {
  const { query } = input;

  // Extract URL from query
  const skillUrl = extractUrl(query);

  if (!skillUrl) {
    return formatNoUrlResponse();
  }

  try {
    const result = await scanSkill({
      skillUrl,
      format: 'auto',
      includeRepoTrust: true,
    });

    return formatScanResult(result);
  } catch (error: any) {
    return formatErrorResponse(error.message);
  }
}

// Extract GitHub/skill URL from natural language query
function extractUrl(query: string): string | null {
  // GitHub patterns
  const githubMatch = query.match(/https?:\/\/github\.com\/[^\s<>"']+/i);
  if (githubMatch) return githubMatch[0];

  // ClawHub patterns
  const clawhubMatch = query.match(/https?:\/\/(clawhub\.xyz|clawhub\.io)\/[^\s<>"']+/i);
  if (clawhubMatch) return clawhubMatch[0];

  // Generic URL
  const urlMatch = query.match(/https?:\/\/[^\s<>"']+/i);
  if (urlMatch) return urlMatch[0];

  return null;
}

// Call AURA API to scan the skill
async function scanSkill(request: ScanRequest): Promise<SkillScanResult> {
  const response = await fetch(`${AURA_API_URL}/tools`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tool: 'scan-skill',
      arguments: {
        skillUrl: request.skillUrl,
        format: request.format || 'auto',
        includeRepoTrust: request.includeRepoTrust ?? true,
      },
    }),
    signal: AbortSignal.timeout(SCAN_TIMEOUT),
  });

  if (!response.ok) {
    throw new Error(`AURA API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json() as { result?: SkillScanResult } | SkillScanResult;
  return ('result' in data && data.result) ? data.result : data as SkillScanResult;
}

// Format scan result for display
function formatScanResult(result: SkillScanResult): string {
  const lines: string[] = [];

  // Header
  lines.push(`## AURA Skill Scan: ${result.name}`);
  lines.push('');

  // Verdict with emoji
  const verdictEmoji = {
    'SAFE': '',
    'WARNING': '',
    'DANGEROUS': '',
    'BLOCKED': '',
  }[result.verdict] || '';

  lines.push(`**Verdict:** ${verdictEmoji} ${result.verdict}`);
  lines.push(`**Risk Score:** ${result.riskScore}/100`);
  lines.push(`**AURA Verified:** ${result.verifiedBadge ? 'Yes' : 'No'}`);
  lines.push('');

  // Summary
  lines.push(`**Summary:** ${result.summary}`);
  lines.push('');

  // Findings (if any)
  const totalFindings =
    result.malwarePatterns.length +
    result.promptInjectionRisks.length +
    result.permissionIssues.length +
    result.networkRisks.length;

  if (totalFindings > 0) {
    lines.push('### Findings');
    lines.push('');

    // Malware
    for (const finding of result.malwarePatterns) {
      lines.push(`- **${finding.severity}:** ${finding.description}`);
      lines.push(`  - Match: \`${truncate(finding.match, 50)}\``);
    }

    // Prompt Injection
    for (const risk of result.promptInjectionRisks) {
      lines.push(`- **${risk.severity}:** ${risk.description}`);
      lines.push(`  - Pattern: \`${truncate(risk.match, 50)}\``);
    }

    // Permission Issues
    for (const issue of result.permissionIssues) {
      lines.push(`- **${issue.severity}:** ${issue.reason}`);
      lines.push(`  - Permission: \`${issue.permission}\``);
    }

    // Network Risks
    for (const risk of result.networkRisks) {
      lines.push(`- **${risk.severity}:** ${risk.reason}`);
      lines.push(`  - URL: \`${truncate(risk.url, 50)}\``);
    }

    lines.push('');
  }

  // Recommendations
  if (result.recommendations.length > 0) {
    lines.push('### Recommendations');
    lines.push('');
    for (const rec of result.recommendations) {
      lines.push(`- ${rec}`);
    }
    lines.push('');
  }

  // Badge reason
  if (!result.verifiedBadge) {
    lines.push(`**Why not verified:** ${result.badgeReason}`);
    lines.push('');
  }

  // Footer
  lines.push('---');
  lines.push(`*Scanned by [AURA Security](https://aurasecurity.io) in ${result.scanTime}ms*`);

  return lines.join('\n');
}

function formatNoUrlResponse(): string {
  return `## AURA Security Scanner

I need a skill URL to scan. Please provide a GitHub URL or ClawHub link.

**Examples:**
- "Scan https://github.com/user/my-skill for security issues"
- "Is https://clawhub.xyz/skill/weather-api safe?"
- "Check this skill: https://github.com/org/mcp-tool"

I'll analyze it for malware, prompt injection, and dangerous permissions.`;
}

function formatErrorResponse(message: string): string {
  return `## AURA Scan Error

Failed to scan skill: ${message}

Please check:
- The URL is accessible
- The skill repository exists
- The URL points to a valid skill (has SKILL.md, package.json, or index file)

If the issue persists, try again or report at https://github.com/aurasecurityio/aura-security/issues`;
}

function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + '...';
}

// Export for direct use
export { scanSkill, formatScanResult, extractUrl };
export type { SkillScanResult, ScanRequest };
