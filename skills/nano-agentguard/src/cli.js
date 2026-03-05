#!/usr/bin/env node

/**
 * AgentGuard CLI
 */

const { Command } = require('commander');
const AgentGuard = require('./index');
const { LEVELS, DANGEROUS_OPERATIONS, READ_OPERATIONS } = require('./scope');

// Simple chalk replacement (ESM compatible)
const chalk = {
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  blue: (s) => `\x1b[34m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  cyan: (s) => `\x1b[36m${s}\x1b[0m`,
  gray: (s) => `\x1b[90m${s}\x1b[0m`,
  bold: (s) => `\x1b[1m${s}\x1b[0m`
};

const program = new Command();

// Get master password from env or prompt
function getMasterPassword() {
  return process.env.AGENTGUARD_PASSWORD || 'default-password-change-me';
}

// Create AgentGuard instance
async function createGuard() {
  const guard = new AgentGuard({
    masterPassword: getMasterPassword()
  });
  await guard.init();
  return guard;
}

// Format output
function print(data) {
  console.log(JSON.stringify(data, null, 2));
}

function success(msg) {
  console.log(chalk.green('✓'), msg);
}

function error(msg) {
  console.error(chalk.red('✗'), msg);
}

function info(msg) {
  console.log(chalk.blue('ℹ'), msg);
}

program
  .name('agentguard')
  .description('Agent Identity & Permission Guardian')
  .version('0.1.0');

// ============ INIT ============
program
  .command('init')
  .description('Initialize AgentGuard')
  .action(async () => {
    try {
      const guard = await createGuard();
      success('AgentGuard initialized');
      info(`Data directory: ${process.env.HOME}/.agentguard`);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ REGISTER ============
program
  .command('register <agentId>')
  .description('Register a new agent')
  .option('-o, --owner <email>', 'Owner email')
  .option('-l, --level <level>', 'Permission level (read/write/admin/dangerous)', 'read')
  .option('-d, --dangerous <policy>', 'Dangerous policy (require-approval/auto-approve/never-allow)', 'require-approval')
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const agent = await guard.registerAgent(agentId, {
        owner: options.owner,
        level: options.level,
        dangerous: options.dangerous
      });
      success(`Agent registered: ${agentId}`);
      print(agent);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ LIST ============
program
  .command('list')
  .description('List all agents')
  .option('-o, --owner <email>', 'Filter by owner')
  .option('-s, --status <status>', 'Filter by status')
  .option('-l, --level <level>', 'Filter by permission level')
  .action(async (options) => {
    try {
      const guard = await createGuard();
      const agents = await guard.listAgents(options);

      if (agents.length === 0) {
        info('No agents found');
        return;
      }

      console.log(chalk.bold('\nAgents:\n'));
      for (const agent of agents) {
        console.log(`  ${chalk.cyan(agent.id)}`);
        console.log(`    Owner: ${agent.owner}`);
        console.log(`    Level: ${agent.permissions.level}`);
        console.log(`    Dangerous: ${agent.permissions.dangerous}`);
        console.log(`    Operations: ${agent.stats.operations}`);
        console.log('');
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ VAULT ============
const vaultCmd = program.command('vault').description('Credential vault operations');

vaultCmd
  .command('store <agentId> <key> <value>')
  .description('Store a credential')
  .action(async (agentId, key, value) => {
    try {
      const guard = await createGuard();
      await guard.storeCredential(agentId, key, value);
      success(`Credential stored: ${agentId}/${key}`);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

vaultCmd
  .command('get <agentId> <key>')
  .description('Get a credential')
  .action(async (agentId, key) => {
    try {
      const guard = await createGuard();
      const value = await guard.getCredential(agentId, key);
      console.log(value);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

vaultCmd
  .command('list <agentId>')
  .description('List credential keys for an agent')
  .action(async (agentId) => {
    try {
      const guard = await createGuard();
      const keys = await guard.vault.listKeys(agentId);
      if (keys.length === 0) {
        info('No credentials stored');
        return;
      }
      print(keys);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ SCOPE ============
const scopeCmd = program.command('scope').description('Permission scope operations');

scopeCmd
  .command('set <agentId>')
  .description('Set permission level')
  .option('-l, --level <level>', 'Permission level')
  .option('-d, --dangerous <policy>', 'Dangerous policy')
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();

      if (options.level) {
        await guard.setPermissionLevel(agentId, options.level);
        success(`Permission level set: ${options.level}`);
      }

      if (options.dangerous) {
        await guard.setDangerousPolicy(agentId, options.dangerous);
        success(`Dangerous policy set: ${options.dangerous}`);
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

scopeCmd
  .command('info <agentId>')
  .description('Get permission info')
  .action(async (agentId) => {
    try {
      const guard = await createGuard();
      const info = await guard.scope.getInfo(agentId);
      print(info);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

scopeCmd
  .command('operations')
  .description('List all available operations')
  .action(() => {
    console.log(chalk.bold('\nRead Operations (auto-approved):'));
    READ_OPERATIONS.forEach(op => console.log(`  ${chalk.green(op)}`));

    console.log(chalk.bold('\nDangerous Operations (require approval):'));
    DANGEROUS_OPERATIONS.forEach(op => console.log(`  ${chalk.yellow(op)}`));
  });

// ============ APPROVE/DENY ============
program
  .command('approve <requestId>')
  .description('Approve a pending request')
  .option('-b, --by <who>', 'Who approved', 'owner')
  .action(async (requestId, options) => {
    try {
      const guard = await createGuard();
      const request = await guard.approveRequest(requestId, options.by);
      success(`Request approved: ${requestId}`);
      print(request);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

program
  .command('deny <requestId>')
  .description('Deny a pending request')
  .option('-b, --by <who>', 'Who denied', 'owner')
  .option('-r, --reason <reason>', 'Denial reason', '')
  .action(async (requestId, options) => {
    try {
      const guard = await createGuard();
      const request = await guard.denyRequest(requestId, options.by, options.reason);
      success(`Request denied: ${requestId}`);
      print(request);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

program
  .command('pending')
  .description('List pending approval requests')
  .option('-a, --agent <agentId>', 'Filter by agent')
  .action(async (options) => {
    try {
      const guard = await createGuard();
      const pending = await guard.listPendingRequests(options.agent);

      if (pending.length === 0) {
        info('No pending requests');
        return;
      }

      console.log(chalk.bold('\nPending Requests:\n'));
      for (const req of pending) {
        console.log(`  ${chalk.cyan(req.id)}`);
        console.log(`    Agent: ${req.agentId}`);
        console.log(`    Operation: ${req.operation}`);
        console.log(`    Expires: ${req.expiresAt}`);
        console.log('');
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ AUDIT ============
const auditCmd = program.command('audit').description('Audit log operations');

auditCmd
  .command('show <agentId>')
  .description('Show audit logs')
  .option('-n, --last <n>', 'Last N entries', parseInt)
  .option('-o, --operation <op>', 'Filter by operation')
  .option('--from <date>', 'From date (YYYY-MM-DD)')
  .option('--to <date>', 'To date (YYYY-MM-DD)')
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const logs = await guard.getAuditLogs(agentId, {
        last: options.last,
        operation: options.operation,
        from: options.from,
        to: options.to
      });

      if (logs.length === 0) {
        info('No audit logs found');
        return;
      }

      for (const entry of logs) {
        console.log(chalk.gray(entry.timestamp), chalk.cyan(entry.operation));
        if (Object.keys(entry.details).length > 0) {
          console.log('  ', JSON.stringify(entry.details));
        }
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

auditCmd
  .command('verify <agentId> <date>')
  .description('Verify audit log integrity')
  .action(async (agentId, date) => {
    try {
      const guard = await createGuard();
      const result = await guard.verifyAudit(agentId, date);

      if (result.valid) {
        success(`Audit log verified: ${result.entries} entries`);
      } else {
        error(`Audit log corrupted: ${result.reason}`);
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

auditCmd
  .command('stats <agentId>')
  .description('Show agent statistics')
  .option('-d, --days <days>', 'Number of days', parseInt, 7)
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const stats = await guard.getStats(agentId, options.days);
      print(stats);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

auditCmd
  .command('export <agentId>')
  .description('Export audit logs')
  .option('--from <date>', 'From date')
  .option('--to <date>', 'To date')
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const exported = await guard.audit.export(agentId, {
        from: options.from,
        to: options.to
      });
      print(exported);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ CHECK ============
program
  .command('check <agentId> <operation>')
  .description('Check if operation is allowed')
  .action(async (agentId, operation) => {
    try {
      const guard = await createGuard();
      const result = await guard.scope.check(agentId, operation);

      if (result.allowed) {
        if (result.requiresApproval) {
          console.log(chalk.yellow('⚠ Requires approval'), '-', result.reason);
        } else {
          success(result.reason);
        }
      } else {
        error(result.reason);
      }

      print(result);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ 1PASSWORD ============
const opCmd = program.command('op').description('1Password integration');

opCmd
  .command('status')
  .description('Check 1Password status')
  .action(async () => {
    try {
      const guard = await createGuard();
      const status = await guard.get1PasswordStatus();

      if (status.available) {
        if (status.signedIn) {
          success(`1Password connected: ${status.account}`);
        } else {
          info('1Password CLI installed but not signed in');
          console.log('Run: op signin');
        }
      } else {
        info(status.reason);
        console.log('Install: brew install 1password-cli');
      }

      print(status);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

opCmd
  .command('enable')
  .description('Enable 1Password integration')
  .option('-a, --account <account>', '1Password account')
  .option('-v, --vault <vault>', 'Vault name', 'Private')
  .action(async (options) => {
    try {
      const guard = await createGuard();
      const status = await guard.enable1Password({
        opAccount: options.account,
        opVault: options.vault
      });

      if (status.available && status.signedIn) {
        success('1Password integration enabled');
      } else {
        info('1Password integration enabled but requires sign-in');
      }

      print(status);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

opCmd
  .command('sync <agentId>')
  .description('Sync credentials from 1Password')
  .action(async (agentId) => {
    try {
      const guard = await createGuard();
      const result = await guard.syncFrom1Password(agentId);
      success(`Synced ${result.synced} credentials from 1Password`);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

opCmd
  .command('ref <agentId> <key>')
  .description('Get 1Password reference for a credential')
  .action(async (agentId, key) => {
    try {
      const guard = await createGuard();
      const ref = guard.getOpReference(agentId, key);
      console.log(ref);
      info('Use with: op read "' + ref + '"');
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

opCmd
  .command('store <agentId> <key>')
  .description('Store credential in 1Password (interactive)')
  .action(async (agentId, key) => {
    try {
      const guard = await createGuard();

      // Check if 1Password is available
      const status = await guard.get1PasswordStatus();
      if (!status.available || !status.signedIn) {
        error('1Password not available. Run: agentguard op enable');
        process.exit(1);
      }

      // Read value from stdin
      let value = '';
      process.stdin.setEncoding('utf8');
      for await (const chunk of process.stdin) {
        value += chunk;
      }
      value = value.trim();

      if (!value) {
        error('No value provided. Use: echo "value" | agentguard op store agent key');
        process.exit(1);
      }

      const result = await guard.storeCredential(agentId, key, value);
      success(`Stored in 1Password+local: ${agentId}/${key}`);
      print(result);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ CREDIT SCORE ============
const creditCmd = program.command('credit').description('Agent credit score system');

creditCmd
  .command('score <agentId>')
  .description('Calculate credit score for an agent')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 30)
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const score = await guard.getCreditScore(agentId, options.days);

      console.log(chalk.bold(`\n${score.tier.emoji} Credit Score: ${score.score}/100`));
      console.log(chalk.gray(`Tier: ${score.tier.name} (${score.tier.level})`));
      console.log(chalk.gray(`Period: ${score.period}`));

      console.log(chalk.bold('\nStatistics:'));
      console.log(`  Days Active: ${score.stats.daysActive}`);
      console.log(`  Task Success: ${score.stats.taskSuccess}`);
      console.log(`  Task Failure: ${score.stats.taskFailure}`);
      console.log(`  Approvals Granted: ${score.stats.approvalsGranted}`);
      console.log(`  Approvals Denied: ${score.stats.approvalsDenied}`);
      console.log(`  Dangerous Ops: ${score.stats.dangerousOps}`);

      console.log(chalk.bold('\nScore Factors:'));
      for (const factor of score.factors.slice(0, 5)) {
        const sign = factor.impact >= 0 ? '+' : '';
        console.log(`  ${factor.factor}: ${sign}${factor.impact}`);
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

creditCmd
  .command('report <agentId>')
  .description('Generate full credit report')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 30)
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const report = await guard.getCreditReport(agentId, options.days);
      print(report);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

creditCmd
  .command('rank')
  .description('Rank all agents by credit score')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 30)
  .action(async (options) => {
    try {
      const guard = await createGuard();
      const result = await guard.getAgentRankings(options.days);

      console.log(chalk.bold('\n🏆 Agent Rankings:\n'));

      for (const agent of result.ranking) {
        const tier = guard.creditScore.getTier(agent.score);
        console.log(`  ${tier.emoji} #${agent.rank} ${agent.agentId}: ${agent.score}/100 (${tier.level})`);
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

creditCmd
  .command('compare <agentIds...>')
  .description('Compare credit scores of multiple agents')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 30)
  .action(async (agentIds, options) => {
    try {
      const guard = await createGuard();
      const result = await guard.compareCreditScores(agentIds, options.days);
      print(result.ranking);
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// ============ COMPLIANCE ============
const complianceCmd = program.command('compliance').description('Compliance reporting');

complianceCmd
  .command('gdpr <agentId>')
  .description('Generate GDPR compliance report')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 90)
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const report = await guard.getGDPRReport(agentId, { days: options.days });

      console.log(chalk.bold('\n📋 GDPR Compliance Report\n'));
      console.log(`Agent: ${agentId}`);
      console.log(`Generated: ${report.generatedAt}`);
      console.log(`\nCompliance Score: ${report.summary.complianceScore}/100`);

      console.log(chalk.bold('\nData Processing:'));
      console.log(`  Total Activities: ${report.summary.totalProcessingActivities}`);
      console.log(`  Data Subjects: ${report.summary.uniqueDataSubjects}`);

      console.log(chalk.bold('\nConsent:'));
      console.log(`  Records: ${report.summary.consentRecords}`);
      console.log(`  Coverage: ${report.consent.coverage}%`);

      if (report.risks.length > 0) {
        console.log(chalk.bold('\n⚠️  Risks:'));
        for (const risk of report.risks.slice(0, 3)) {
          console.log(`  [${risk.level.toUpperCase()}] ${risk.description}`);
        }
      }

      if (report.recommendations.length > 0) {
        console.log(chalk.bold('\n📝 Recommendations:'));
        for (const rec of report.recommendations.slice(0, 3)) {
          console.log(`  [${rec.priority.toUpperCase()}] ${rec.action}`);
        }
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

complianceCmd
  .command('ccpa <agentId>')
  .description('Generate CCPA compliance report')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 90)
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const report = await guard.getCCPAReport(agentId, { days: options.days });

      console.log(chalk.bold('\n📋 CCPA Compliance Report\n'));
      console.log(`Agent: ${agentId}`);
      console.log(`Generated: ${report.generatedAt}`);
      console.log(`\nCompliance Score: ${report.summary.complianceScore}/100`);

      console.log(chalk.bold('\nData Sales:'));
      console.log(`  Activities: ${report.summary.dataSales}`);
      console.log(`  Opt-out Mechanism: ${report.dataSales.optOutMechanism ? 'Yes' : 'No'}`);

      console.log(chalk.bold('\nConsumer Rights:'));
      console.log(`  Requests: ${report.summary.consumerRequests}`);
      console.log(`  Fulfillment Rate: ${report.consumerRights.fulfillment.rate}%`);

      if (report.risks.length > 0) {
        console.log(chalk.bold('\n⚠️  Risks:'));
        for (const risk of report.risks.slice(0, 3)) {
          console.log(`  [${risk.level.toUpperCase()}] ${risk.description}`);
        }
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

complianceCmd
  .command('full <agentId>')
  .description('Generate full compliance report (GDPR + CCPA)')
  .option('-d, --days <days>', 'Number of days to analyze', parseInt, 90)
  .action(async (agentId, options) => {
    try {
      const guard = await createGuard();
      const report = await guard.getFullComplianceReport(agentId, { days: options.days });

      console.log(chalk.bold('\n📋 Full Compliance Report\n'));
      console.log(`Agent: ${agentId}`);
      console.log(`Generated: ${report.generatedAt}`);
      console.log(`\nOverall Score: ${report.overallScore}/100`);

      console.log(chalk.bold('\nGDPR Score:'), report.gdpr.summary.complianceScore);
      console.log(chalk.bold('CCPA Score:'), report.ccpa.summary.complianceScore);

      if (report.allRisks.length > 0) {
        console.log(chalk.bold('\n⚠️  All Risks:'));
        for (const risk of report.allRisks.slice(0, 5)) {
          console.log(`  [${risk.level.toUpperCase()}] ${risk.description}`);
        }
      }

      if (report.allRecommendations.length > 0) {
        console.log(chalk.bold('\n📝 All Recommendations:'));
        for (const rec of report.allRecommendations.slice(0, 5)) {
          console.log(`  [${rec.priority.toUpperCase()}] ${rec.action}`);
        }
      }
    } catch (e) {
      error(e.message);
      process.exit(1);
    }
  });

// Parse arguments
program.parse();
