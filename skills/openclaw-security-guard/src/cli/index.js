#!/usr/bin/env node

/**
 * 🛡️ OpenClaw Security Guard
 * 
 * Complete security layer for OpenClaw:
 * - CLI Scanner for audits
 * - Live Dashboard for monitoring
 * - Auto-fix for issues
 * 
 * Author: Miloud Belarebia
 * Website: https://2pidata.com
 * 
 * NO TELEMETRY - 100% PRIVATE
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import boxen from 'boxen';
import { table } from 'table';
import inquirer from 'inquirer';
import fs from 'fs/promises';

// Import scanners
import { SecretsScanner } from '../scanners/secrets-scanner.js';
import { ConfigAuditor } from '../scanners/config-auditor.js';
import { PromptInjectionDetector } from '../scanners/prompt-injection-detector.js';
import { DependencyScanner } from '../scanners/dependency-scanner.js';
import { McpServerAuditor } from '../scanners/mcp-server-auditor.js';

// Import other modules
import { AutoHardener } from '../hardening/auto-hardener.js';
import { startDashboard } from '../dashboard/server.js';
import { loadConfig, getOpenClawPath, formatDuration } from '../utils/helpers.js';
import { i18n } from '../utils/i18n.js';

// ============================================================
// CONSTANTS
// ============================================================

const VERSION = '1.0.0';
const AUTHOR = 'Miloud Belarebia';
const WEBSITE = 'https://2pidata.com';

const BANNER = chalk.cyan(`
╔═══════════════════════════════════════════════════════════════╗
║  🛡️  OpenClaw Security Guard v${VERSION}                         ║
║  The security layer your AI assistant needs                   ║
║                                                               ║
║  By ${AUTHOR} • ${WEBSITE}                     ║
╚═══════════════════════════════════════════════════════════════╝
`);

const program = new Command();

// ============================================================
// MAIN PROGRAM
// ============================================================

program
  .name('openclaw-guard')
  .description('🛡️ Complete security layer for OpenClaw - CLI Scanner + Live Dashboard')
  .version(VERSION)
  .option('-c, --config <path>', 'Path to config file')
  .option('-l, --lang <lang>', 'Language (en|fr|ar)', 'en')
  .option('-v, --verbose', 'Verbose output')
  .option('-q, --quiet', 'Quiet mode (no banner)')
  .hook('preAction', (thisCommand, actionCommand) => {
    if (!thisCommand.opts().quiet && actionCommand.name() !== 'dashboard') {
      console.log(BANNER);
    }
  });

// ============================================================
// AUDIT COMMAND
// ============================================================

program
  .command('audit')
  .description('Run a complete security audit')
  .option('--deep', 'Deep scan (slower but thorough)')
  .option('--quick', 'Quick scan (faster)')
  .option('-o, --output <path>', 'Output file')
  .option('-f, --format <format>', 'Output format (text|json|html|md)', 'text')
  .option('--ci', 'CI mode (exit 1 on critical issues)')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    const _t = i18n(program.opts().lang);
    const startTime = Date.now();
    const openclawPath = await getOpenClawPath();
    
    console.log(chalk.dim(`📍 Scanning: ${openclawPath}\n`));
    
    const results = {
      timestamp: new Date().toISOString(),
      version: VERSION,
      path: openclawPath,
      scanners: {},
      summary: { critical: 0, high: 0, medium: 0, low: 0 }
    };
    
    // Define scanners
    const scanners = [
      { name: 'secrets', Scanner: SecretsScanner, icon: '🔍', label: 'Secrets Scanner' },
      { name: 'config', Scanner: ConfigAuditor, icon: '🔧', label: 'Config Auditor' },
      { name: 'prompts', Scanner: PromptInjectionDetector, icon: '💉', label: 'Injection Detector' },
      { name: 'deps', Scanner: DependencyScanner, icon: '📦', label: 'Dependency Scanner' },
      { name: 'mcp', Scanner: McpServerAuditor, icon: '🔌', label: 'MCP Auditor' }
    ];
    
    // Run each scanner
    for (const { name, Scanner, icon, label } of scanners) {
      const spinner = ora(`${icon} ${label}...`).start();
      
      try {
        const scanner = new Scanner(config);
        const result = await scanner.scan(openclawPath, options);
        results.scanners[name] = result;
        
        // Update summary
        results.summary.critical += result.summary?.critical || 0;
        results.summary.high += result.summary?.high || 0;
        results.summary.medium += result.summary?.medium || 0;
        results.summary.low += result.summary?.low || 0;
        
        // Show result
        const hasIssues = (result.summary?.critical || 0) + (result.summary?.high || 0) > 0;
        if (hasIssues) {
          spinner.fail(`${icon} ${label}`);
        } else if (result.summary?.medium > 0) {
          spinner.warn(`${icon} ${label}`);
        } else {
          spinner.succeed(`${icon} ${label}`);
        }
        
        // Show findings in verbose mode
        if (program.opts().verbose && result.findings?.length > 0) {
          for (const f of result.findings.slice(0, 5)) {
            const color = f.severity === 'critical' ? chalk.red :
                         f.severity === 'high' ? chalk.yellow : chalk.dim;
            console.log(color(`   → ${f.message}`));
          }
        }
        
      } catch (error) {
        spinner.fail(`${icon} ${label} - Error: ${error.message}`);
        results.scanners[name] = { error: error.message };
      }
    }
    
    // Calculate security score
    const score = calculateScore(results);
    results.securityScore = score;
    
    // Display summary
    console.log('\n' + chalk.dim('━'.repeat(50)));
    displaySummary(results);
    
    // Duration
    console.log(chalk.dim(`\n⏱️  Completed in ${formatDuration(Date.now() - startTime)}`));
    
    // Save report if requested
    if (options.output) {
      await saveReport(results, options.output, options.format);
      console.log(chalk.green(`\n📄 Report saved: ${options.output}`));
    }
    
    // CI mode exit code
    if (options.ci && results.summary.critical > 0) {
      process.exit(1);
    }
  });

// ============================================================
// DASHBOARD COMMAND
// ============================================================

program
  .command('dashboard')
  .description('Start the real-time security dashboard')
  .option('-p, --port <port>', 'Dashboard port', '18790')
  .option('-g, --gateway <url>', 'OpenClaw Gateway URL', 'ws://127.0.0.1:18789')
  .option('--no-browser', 'Don\'t open browser automatically')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    
    console.log(BANNER);
    
    await startDashboard({
      port: parseInt(options.port),
      gatewayUrl: options.gateway,
      openBrowser: options.browser,
      config
    });
  });

// ============================================================
// FIX COMMAND
// ============================================================

program
  .command('fix')
  .description('Fix security issues automatically')
  .option('--auto', 'Auto-fix without prompts')
  .option('--interactive', 'Interactive mode')
  .option('--backup', 'Create backup before changes', true)
  .option('--dry-run', 'Preview changes without applying')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    const openclawPath = await getOpenClawPath();
    
    console.log(chalk.bold('🔧 Security Fix\n'));
    
    // Run config audit to find fixable issues
    const auditor = new ConfigAuditor(config);
    const auditResult = await auditor.scan(openclawPath, {});
    
    const fixable = auditResult.findings.filter(f => f.autoFixable);
    
    if (fixable.length === 0) {
      console.log(chalk.green('✅ No auto-fixable issues found'));
      return;
    }
    
    console.log(chalk.yellow(`Found ${fixable.length} fixable issue(s):\n`));
    
    for (const issue of fixable) {
      const icon = issue.severity === 'critical' ? '🔴' : '🟡';
      console.log(`${icon} ${issue.message}`);
      console.log(chalk.dim(`   Fix: ${issue.fix}`));
    }
    
    if (options.dryRun) {
      console.log(chalk.blue('\n[Dry Run] No changes made'));
      return;
    }
    
    // Confirm unless auto mode
    if (!options.auto) {
      const { proceed } = await inquirer.prompt([{
        type: 'confirm',
        name: 'proceed',
        message: 'Apply these fixes?',
        default: false
      }]);
      
      if (!proceed) {
        console.log(chalk.dim('Cancelled'));
        return;
      }
    }
    
    // Backup
    if (options.backup) {
      const backupPath = `${openclawPath}/openclaw.json.backup.${Date.now()}`;
      try {
        await fs.copyFile(`${openclawPath}/openclaw.json`, backupPath);
        console.log(chalk.dim(`📦 Backup: ${backupPath}`));
      } catch (_e) {
        // No existing config to backup
      }
    }
    
    // Apply fixes
    const hardener = new AutoHardener(config);
    await hardener.applyFixes(openclawPath, fixable);
    
    console.log(boxen(
      chalk.green.bold('✅ Fixes Applied\n\n') +
      chalk.white('Restart OpenClaw for changes to take effect:\n') +
      chalk.cyan('openclaw gateway --restart'),
      { padding: 1, borderColor: 'green', borderStyle: 'round' }
    ));
  });

// ============================================================
// SCAN COMMAND (individual scanners)
// ============================================================

const scanCmd = program
  .command('scan')
  .description('Run individual security scans');

scanCmd
  .command('secrets')
  .description('Scan for exposed secrets')
  .option('--quick', 'Quick scan')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    const openclawPath = await getOpenClawPath();
    
    const spinner = ora('🔍 Scanning for secrets...').start();
    const scanner = new SecretsScanner(config);
    const result = await scanner.scan(openclawPath, options);
    
    if (result.findings.length === 0) {
      spinner.succeed('No secrets found');
    } else {
      spinner.warn(`Found ${result.findings.length} potential secret(s)`);
      for (const f of result.findings) {
        console.log(chalk.yellow(`   ⚠️ ${f.message}`));
        console.log(chalk.dim(`      ${f.location}`));
      }
    }
  });

scanCmd
  .command('config')
  .description('Audit OpenClaw configuration')
  .option('--strict', 'Strict mode')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    const openclawPath = await getOpenClawPath();
    
    const spinner = ora('🔧 Auditing configuration...').start();
    const auditor = new ConfigAuditor(config);
    const result = await auditor.scan(openclawPath, options);
    spinner.stop();
    
    console.log(chalk.bold('\n🔧 Configuration Audit:\n'));
    for (const f of result.findings) {
      const icon = f.severity === 'critical' ? '❌' : f.severity === 'high' ? '⚠️' : '✅';
      const color = f.severity === 'critical' ? chalk.red :
                   f.severity === 'high' ? chalk.yellow : chalk.green;
      console.log(color(`${icon} ${f.message}`));
    }
  });

scanCmd
  .command('prompts')
  .description('Detect prompt injection patterns')
  .option('-s, --sensitivity <level>', 'Sensitivity (low|medium|high)', 'medium')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    const openclawPath = await getOpenClawPath();
    
    const spinner = ora('💉 Scanning for injection patterns...').start();
    const detector = new PromptInjectionDetector(config);
    const result = await detector.scan(openclawPath, options);
    
    if (result.findings.length === 0) {
      spinner.succeed('No injection patterns detected');
    } else {
      spinner.warn(`Found ${result.findings.length} suspicious pattern(s)`);
      for (const f of result.findings) {
        console.log(chalk.yellow(`   ⚠️ ${f.message}`));
      }
    }
  });

// ============================================================
// REPORT COMMAND
// ============================================================

program
  .command('report')
  .description('Generate security report')
  .option('-f, --format <format>', 'Format (html|json|md)', 'html')
  .option('-o, --output <path>', 'Output path', './security-report')
  .action(async (options) => {
    const config = await loadConfig(program.opts().config);
    const openclawPath = await getOpenClawPath();
    
    console.log(chalk.bold('📊 Generating Security Report...\n'));
    
    const spinner = ora('Running full audit...').start();
    
    const results = { timestamp: new Date().toISOString(), scanners: {}, summary: { critical: 0, high: 0, medium: 0, low: 0 } };
    
    const scanners = [
      { name: 'secrets', Scanner: SecretsScanner },
      { name: 'config', Scanner: ConfigAuditor },
      { name: 'prompts', Scanner: PromptInjectionDetector }
    ];
    
    for (const { name, Scanner } of scanners) {
      const scanner = new Scanner(config);
      const result = await scanner.scan(openclawPath, {});
      results.scanners[name] = result;
      results.summary.critical += result.summary?.critical || 0;
      results.summary.high += result.summary?.high || 0;
      results.summary.medium += result.summary?.medium || 0;
      results.summary.low += result.summary?.low || 0;
    }
    
    results.securityScore = calculateScore(results);
    
    spinner.succeed('Audit complete');
    
    const outputPath = `${options.output}.${options.format}`;
    await saveReport(results, outputPath, options.format);
    
    console.log(chalk.green(`✅ Report saved: ${outputPath}`));
  });

// ============================================================
// HOOKS COMMAND
// ============================================================

program
  .command('hooks <action>')
  .description('Manage git hooks (install|uninstall|status)')
  .action(async (action) => {
    const hookPath = '.git/hooks/pre-commit';
    
    switch (action) {
      case 'install':
        const script = `#!/bin/bash
# OpenClaw Security Guard - Pre-commit Hook
# Scans for secrets before allowing commit

echo "🛡️ Running security scan..."
npx openclaw-guard scan secrets --quick

if [ $? -ne 0 ]; then
  echo "❌ Security check failed! Commit blocked."
  echo "   Run 'openclaw-guard scan secrets' for details."
  exit 1
fi

echo "✅ Security check passed"
`;
        try {
          await fs.mkdir('.git/hooks', { recursive: true });
          await fs.writeFile(hookPath, script, { mode: 0o755 });
          console.log(chalk.green('✅ Pre-commit hook installed'));
          console.log(chalk.dim('   Secrets will be scanned before each commit'));
        } catch (e) {
          console.log(chalk.red('❌ Failed to install hook:'), e.message);
        }
        break;
        
      case 'uninstall':
        try {
          await fs.unlink(hookPath);
          console.log(chalk.green('✅ Hook removed'));
        } catch {
          console.log(chalk.yellow('No hook to remove'));
        }
        break;
        
      case 'status':
        try {
          await fs.access(hookPath);
          console.log(chalk.green('✅ Pre-commit hook is installed'));
        } catch {
          console.log(chalk.yellow('⚠️ No pre-commit hook installed'));
          console.log(chalk.dim('   Run: openclaw-guard hooks install'));
        }
        break;
        
      default:
        console.log(chalk.red('Unknown action. Use: install|uninstall|status'));
    }
  });

// ============================================================
// ABOUT COMMAND
// ============================================================

program
  .command('about')
  .description('About this tool')
  .action(() => {
    console.log(boxen(
      chalk.cyan.bold('🛡️ OpenClaw Security Guard\n\n') +
      chalk.white(`Version:  ${VERSION}\n`) +
      chalk.white(`Author:   ${AUTHOR}\n`) +
      chalk.white(`Website:  ${WEBSITE}\n\n`) +
      chalk.dim('━'.repeat(40) + '\n\n') +
      chalk.green('✅ No telemetry\n') +
      chalk.green('✅ No tracking\n') +
      chalk.green('✅ 100% private\n') +
      chalk.green('✅ Open source\n\n') +
      chalk.dim('━'.repeat(40) + '\n\n') +
      chalk.white('Need help? Visit:\n') +
      chalk.cyan(`${WEBSITE}`),
      { padding: 1, borderColor: 'cyan', borderStyle: 'round' }
    ));
  });

// ============================================================
// HELPER FUNCTIONS
// ============================================================

function calculateScore(results) {
  let score = 100;
  
  // Config issues
  const configStatus = results.scanners.config?.configStatus || {};
  if (configStatus.sandboxMode !== 'always') score -= 20;
  if (configStatus.dmPolicy === 'open') score -= 15;
  if (configStatus.gatewayBind !== 'loopback') score -= 15;
  if (configStatus.elevated === 'enabled') score -= 10;
  
  // Findings
  score -= (results.summary?.critical || 0) * 10;
  score -= (results.summary?.high || 0) * 5;
  score -= (results.summary?.medium || 0) * 2;
  
  return Math.max(0, Math.min(100, score));
}

function displaySummary(results) {
  const score = results.securityScore;
  const scoreColor = score >= 80 ? chalk.green : score >= 60 ? chalk.yellow : chalk.red;
  const scoreIcon = score >= 80 ? '🟢' : score >= 60 ? '🟡' : '🔴';
  
  console.log(chalk.bold('\n📊 Security Summary'));
  
  // Score
  console.log(boxen(
    scoreColor.bold(`${scoreIcon} Security Score: ${score}/100`),
    { padding: { left: 2, right: 2, top: 0, bottom: 0 }, borderStyle: 'round' }
  ));
  
  // Findings table
  const data = [
    [chalk.red('Critical'), chalk.yellow('High'), chalk.blue('Medium'), chalk.dim('Low')],
    [
      results.summary.critical.toString(),
      results.summary.high.toString(),
      results.summary.medium.toString(),
      results.summary.low.toString()
    ]
  ];
  
  console.log(table(data, {
    columns: { 0: { alignment: 'center' }, 1: { alignment: 'center' }, 2: { alignment: 'center' }, 3: { alignment: 'center' } }
  }));
  
  // Recommendation
  if (results.summary.critical > 0) {
    console.log(chalk.red.bold('🔴 Critical issues found!'));
    console.log(chalk.white(`   Run: ${chalk.cyan('openclaw-guard fix')}`));
  } else if (results.summary.high > 0) {
    console.log(chalk.yellow.bold('🟡 Review recommended'));
  } else {
    console.log(chalk.green.bold('🟢 Looking good!'));
  }
}

async function saveReport(results, outputPath, format) {
  let content;
  
  switch (format) {
    case 'json':
      content = JSON.stringify(results, null, 2);
      break;
      
    case 'md':
      content = `# 🛡️ OpenClaw Security Report

**Generated:** ${results.timestamp}  
**Tool:** OpenClaw Security Guard v${VERSION}  
**Author:** ${AUTHOR} ([${WEBSITE}](${WEBSITE}))

---

## Security Score: ${results.securityScore}/100

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | ${results.summary?.critical || 0} |
| 🟡 High | ${results.summary?.high || 0} |
| 🔵 Medium | ${results.summary?.medium || 0} |
| ⚪ Low | ${results.summary?.low || 0} |

## Findings

${Object.entries(results.scanners).map(([name, data]) => `
### ${name.charAt(0).toUpperCase() + name.slice(1)}

${(data.findings || []).length === 0 ? '✅ No issues found' : (data.findings || []).map(f => `- **${f.severity}**: ${f.message}`).join('\n')}
`).join('\n')}

---

*Generated by [OpenClaw Security Guard](https://github.com/2pidata/openclaw-security-guard)*
`;
      break;
      
    case 'html':
    default:
      const scoreColor = results.securityScore >= 80 ? '#22c55e' : results.securityScore >= 60 ? '#eab308' : '#ef4444';
      content = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenClaw Security Report</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px; margin: 0; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { border-bottom: 2px solid ${scoreColor}; padding-bottom: 10px; }
    .meta { color: #64748b; font-size: 14px; margin-bottom: 30px; }
    .score-card { background: #1e293b; padding: 30px; border-radius: 12px; text-align: center; margin: 20px 0; border: 1px solid ${scoreColor}; }
    .score { font-size: 4em; font-weight: bold; color: ${scoreColor}; }
    .card { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
    .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center; }
    .summary-item { padding: 15px; border-radius: 8px; background: #334155; }
    .critical { color: #ef4444; }
    .high { color: #f97316; }
    .medium { color: #eab308; }
    .low { color: #64748b; }
    .finding { padding: 10px; border-left: 3px solid #64748b; margin: 10px 0; background: #0f172a; }
    .finding.critical { border-color: #ef4444; }
    .finding.high { border-color: #f97316; }
    footer { text-align: center; margin-top: 40px; color: #64748b; font-size: 14px; }
    a { color: #06b6d4; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🛡️ OpenClaw Security Report</h1>
    <div class="meta">
      Generated: ${results.timestamp}<br>
      Tool: OpenClaw Security Guard v${VERSION}<br>
      Author: <a href="${WEBSITE}">${AUTHOR}</a>
    </div>
    
    <div class="score-card">
      <div class="score">${results.securityScore}</div>
      <div>Security Score</div>
    </div>
    
    <div class="card">
      <h2>Summary</h2>
      <div class="summary-grid">
        <div class="summary-item">
          <div class="critical" style="font-size: 2em; font-weight: bold;">${results.summary?.critical || 0}</div>
          <div>Critical</div>
        </div>
        <div class="summary-item">
          <div class="high" style="font-size: 2em; font-weight: bold;">${results.summary?.high || 0}</div>
          <div>High</div>
        </div>
        <div class="summary-item">
          <div class="medium" style="font-size: 2em; font-weight: bold;">${results.summary?.medium || 0}</div>
          <div>Medium</div>
        </div>
        <div class="summary-item">
          <div class="low" style="font-size: 2em; font-weight: bold;">${results.summary?.low || 0}</div>
          <div>Low</div>
        </div>
      </div>
    </div>
    
    ${Object.entries(results.scanners).map(([name, data]) => `
    <div class="card">
      <h3>${name.charAt(0).toUpperCase() + name.slice(1)}</h3>
      ${(data.findings || []).length === 0 ? '<p>✅ No issues found</p>' : (data.findings || []).map(f => `
        <div class="finding ${f.severity}">
          <strong>${f.severity.toUpperCase()}</strong>: ${f.message}
        </div>
      `).join('')}
    </div>
    `).join('')}
    
    <footer>
      Generated by <a href="https://github.com/2pidata/openclaw-security-guard">OpenClaw Security Guard</a><br>
      Created by <a href="${WEBSITE}">${AUTHOR}</a>
    </footer>
  </div>
</body>
</html>`;
      break;
  }
  
  await fs.writeFile(outputPath, content, 'utf-8');
}

// ============================================================
// RUN
// ============================================================

program.parse();
