/**
 * Project Health Check
 * Monitors project document completeness and freshness
 */

import * as fs from 'fs';
import * as path from 'path';

export interface HealthCheckInput {
  projectDir: string;
  maxRiskRegisterAge?: number;  // Days (default: 7)
}

export interface HealthCheckOutput {
  status: 'GREEN' | 'AMBER' | 'RED';
  issues: number;
  warnings: number;
  checks: Array<{
    name: string;
    status: 'pass' | 'warn' | 'fail';
    message: string;
    details?: string;
  }>;
  timestamp: string;
}

export const REQUIRED_DOCUMENTS = [
  'project-charter.md',
  'wbs.md',
  'risk-register.md',
  'gantt-schedule.md',
  'raci-matrix.md',
];

export const OPTIONAL_DOCUMENTS = [
  'communications-plan.md',
  'stakeholder-register.md',
  'evm-dashboard.md',
  'change-request.md',
  'lessons-learned.md',
];

/**
 * Run project health check
 */
export function checkHealth(input: HealthCheckInput): HealthCheckOutput {
  const { projectDir, maxRiskRegisterAge = 7 } = input;
  const checks: HealthCheckOutput['checks'] = [];
  let issues = 0;
  let warnings = 0;
  
  // Check required documents
  for (const doc of REQUIRED_DOCUMENTS) {
    const filePath = path.join(projectDir, doc);
    if (fs.existsSync(filePath)) {
      checks.push({
        name: doc,
        status: 'pass',
        message: 'Found',
      });
    } else {
      checks.push({
        name: doc,
        status: 'fail',
        message: 'Missing',
      });
      issues++;
    }
  }
  
  // Check optional documents
  for (const doc of OPTIONAL_DOCUMENTS) {
    const filePath = path.join(projectDir, doc);
    if (fs.existsSync(filePath)) {
      checks.push({
        name: doc,
        status: 'pass',
        message: 'Found',
      });
    } else {
      checks.push({
        name: doc,
        status: 'warn',
        message: 'Not found (optional)',
      });
      warnings++;
    }
  }
  
  // Check risk register freshness
  const riskRegisterPath = path.join(projectDir, 'risk-register.md');
  if (fs.existsSync(riskRegisterPath)) {
    const stats = fs.statSync(riskRegisterPath);
    const ageDays = (Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60 * 24);
    
    if (ageDays > maxRiskRegisterAge) {
      checks.push({
        name: 'Risk register freshness',
        status: 'warn',
        message: `Not updated in ${Math.floor(ageDays)} days`,
        details: `Last updated: ${stats.mtime.toISOString().split('T')[0]}`,
      });
      warnings++;
    } else {
      checks.push({
        name: 'Risk register freshness',
        status: 'pass',
        message: `Current (${Math.floor(ageDays)} days old)`,
      });
    }
  }
  
  // Determine overall status
  let status: 'GREEN' | 'AMBER' | 'RED';
  if (issues > 0) {
    status = 'RED';
  } else if (warnings > 2) {
    status = 'AMBER';
  } else {
    status = 'GREEN';
  }
  
  return {
    status,
    issues,
    warnings,
    checks,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Format health check as Markdown
 */
export function formatHealthMarkdown(result: HealthCheckOutput): string {
  const emoji = result.status === 'GREEN' ? '🟢' : result.status === 'AMBER' ? '🟡' : '🔴';
  
  let md = `# Project Health Check\n\n`;
  md += `**Status:** ${emoji} **${result.status}**\n\n`;
  md += `**Issues:** ${result.issues} | **Warnings:** ${result.warnings}\n\n`;
  md += `**Checked:** ${result.timestamp}\n\n`;
  
  md += `## Checks\n\n`;
  md += `| Check | Status | Message |\n`;
  md += `|-------|--------|---------|\n`;
  
  for (const check of result.checks) {
    const statusEmoji = check.status === 'pass' ? '✅' : check.status === 'warn' ? '⚠️' : '❌';
    md += `| ${check.name} | ${statusEmoji} ${check.status} | ${check.message} |\n`;
  }
  
  return md;
}

/**
 * Format health check as JSON
 */
export function formatHealthJson(result: HealthCheckOutput): string {
  return JSON.stringify(result, null, 2);
}
