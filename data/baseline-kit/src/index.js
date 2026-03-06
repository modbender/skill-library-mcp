import fs from 'node:fs';
import path from 'node:path';

export const TOOL = 'baseline-kit';
export const VERSION = '0.1.0';

const COMPLIANCE = {
  NET_EXPOSURE: ['SOC2', 'ISO27001', 'NIST CSF'],
  AUTH_RATE_LIMIT: ['SOC2', 'NIST CSF'],
  SOURCE_RESTRICTION: ['ISO27001', 'NIST CSF'],
  AUDIT_LOGGING: ['SOC2', 'ISO27001'],
  BACKUP_HINT: ['ISO27001'],
  SECRET_HYGIENE: ['SOC2', 'NIST CSF']
};

function nowIso() {
  return new Date().toISOString();
}

function makeEnvelope(status, data = {}, errors = []) {
  return {
    tool: TOOL,
    version: VERSION,
    timestamp: nowIso(),
    status,
    data,
    errors
  };
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      args._.push(token);
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

function writeJsonFile(outPath, data) {
  const resolved = path.resolve(outPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  fs.writeFileSync(resolved, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
  return resolved;
}

function getByPath(obj, dottedPath) {
  return dottedPath.split('.').reduce((acc, key) => (acc && key in acc ? acc[key] : undefined), obj);
}

function collectPotentialSecrets(obj, currentPath = '', found = []) {
  if (!obj || typeof obj !== 'object') {
    return found;
  }

  const secretKeyPattern = /(secret|token|api[_-]?key|password)/i;

  for (const [key, value] of Object.entries(obj)) {
    const nextPath = currentPath ? `${currentPath}.${key}` : key;
    if (secretKeyPattern.test(key) && typeof value === 'string') {
      const looksLikePlaceholder = /^\$\{.+\}$/.test(value) || /<redacted>/i.test(value);
      if (!looksLikePlaceholder && value.trim().length >= 8) {
        found.push({ path: nextPath, sample: `${value.slice(0, 4)}***` });
      }
    }
    if (value && typeof value === 'object') {
      collectPotentialSecrets(value, nextPath, found);
    }
  }

  return found;
}

export function generateProfile(profile) {
  const base = {
    gateway: {
      bind: '127.0.0.1',
      auth: {
        enabled: true,
        rateLimit: {
          maxAttempts: 5,
          windowMs: 60_000
        }
      }
    },
    skills: {
      allowedSources: ['clawhub.com'],
      requireVerification: true
    },
    logging: {
      audit: true,
      retentionDays: 30
    },
    backup: {
      enabled: true,
      intervalHours: 24,
      target: './backups/openclaw'
    }
  };

  switch (profile) {
    case 'development':
      return {
        ...base,
        gateway: {
          ...base.gateway,
          auth: {
            ...base.gateway.auth,
            rateLimit: {
              maxAttempts: 20,
              windowMs: 60_000
            }
          }
        },
        logging: {
          ...base.logging,
          retentionDays: 7
        }
      };
    case 'team':
      return {
        ...base,
        gateway: {
          ...base.gateway,
          auth: {
            ...base.gateway.auth,
            rateLimit: {
              maxAttempts: 10,
              windowMs: 60_000
            }
          }
        },
        logging: {
          ...base.logging,
          retentionDays: 30
        }
      };
    case 'enterprise':
      return {
        ...base,
        gateway: {
          ...base.gateway,
          auth: {
            ...base.gateway.auth,
            rateLimit: {
              maxAttempts: 5,
              windowMs: 300_000
            }
          }
        },
        logging: {
          ...base.logging,
          retentionDays: 90
        },
        recovery: {
          drRunbook: './docs/disaster-recovery.md'
        }
      };
    case 'airgapped':
      return {
        ...base,
        gateway: {
          ...base.gateway,
          bind: '127.0.0.1',
          networkMode: 'airgapped'
        },
        skills: {
          ...base.skills,
          allowedSources: ['local-mirror'],
          requireVerification: true
        },
        logging: {
          ...base.logging,
          retentionDays: 180
        }
      };
    default:
      throw new Error(`Unsupported profile: ${profile}`);
  }
}

function addFinding(findings, id, severity, reason, evidencePath, recommendation) {
  findings.push({
    id,
    severity,
    reason,
    evidencePath,
    recommendation,
    complianceTags: COMPLIANCE[id] || []
  });
}

export function auditConfig(config, configPath = 'openclaw.json') {
  const findings = [];

  const bind = getByPath(config, 'gateway.bind');
  if (!['127.0.0.1', 'localhost', 'loopback'].includes(String(bind))) {
    addFinding(
      findings,
      'NET_EXPOSURE',
      'high',
      'Gateway bind is not loopback-only, increasing network exposure.',
      'gateway.bind',
      'Set gateway.bind to 127.0.0.1, localhost, or loopback.'
    );
  }

  const rateLimit = getByPath(config, 'gateway.auth.rateLimit');
  if (!rateLimit || typeof rateLimit.maxAttempts !== 'number' || typeof rateLimit.windowMs !== 'number') {
    addFinding(
      findings,
      'AUTH_RATE_LIMIT',
      'high',
      'Authentication rate-limit is missing or incomplete.',
      'gateway.auth.rateLimit',
      'Define maxAttempts and windowMs under gateway.auth.rateLimit.'
    );
  }

  const allowedSources = getByPath(config, 'skills.allowedSources');
  if (!Array.isArray(allowedSources) || allowedSources.length === 0 || allowedSources.includes('*')) {
    addFinding(
      findings,
      'SOURCE_RESTRICTION',
      'medium',
      'Skill source restriction is too broad or undefined.',
      'skills.allowedSources',
      'Restrict skills.allowedSources to trusted domains only.'
    );
  }

  const auditEnabled = getByPath(config, 'logging.audit');
  if (auditEnabled !== true) {
    addFinding(
      findings,
      'AUDIT_LOGGING',
      'medium',
      'Audit logging is disabled or not configured.',
      'logging.audit',
      'Enable logging.audit and define retention policy.'
    );
  }

  const backupEnabled = getByPath(config, 'backup.enabled');
  if (backupEnabled !== true) {
    addFinding(
      findings,
      'BACKUP_HINT',
      'low',
      'Backup/recovery hints are missing.',
      'backup.enabled',
      'Set backup.enabled=true and provide backup destination.'
    );
  }

  const potentialSecrets = collectPotentialSecrets(config);
  for (const hit of potentialSecrets) {
    addFinding(
      findings,
      'SECRET_HYGIENE',
      'high',
      `Potential plaintext secret detected at ${hit.path}.`,
      hit.path,
      'Move secrets to env vars or secret manager placeholders.'
    );
  }

  const summary = { low: 0, medium: 0, high: 0 };
  for (const finding of findings) {
    summary[finding.severity] += 1;
  }

  return {
    configPath,
    generatedAt: nowIso(),
    findings,
    summary
  };
}

function reportStatus(report) {
  if (report.summary.high > 0) return 'warning';
  if (report.summary.medium > 0) return 'warning';
  return 'ok';
}

function formatAuditTable(report) {
  const lines = [];
  lines.push(`Baseline Kit Audit: ${report.configPath}`);
  lines.push(`Findings -> high:${report.summary.high} medium:${report.summary.medium} low:${report.summary.low}`);
  lines.push('');
  if (report.findings.length === 0) {
    lines.push('No findings. Configuration looks healthy.');
    return lines.join('\n');
  }
  for (const finding of report.findings) {
    lines.push(
      `- [${finding.severity.toUpperCase()}] ${finding.id}: ${finding.reason} | evidence=${finding.evidencePath}`
    );
  }
  return lines.join('\n');
}

function printHelp() {
  console.log(`baseline-kit usage:
  baseline-kit generate --profile <development|team|enterprise|airgapped> --out <path> [--format <table|json>]
  baseline-kit audit --config <path> [--format <table|json>]`);
}

export async function runCli(argv) {
  const args = parseArgs(argv);
  const command = args._[0];

  if (!command || args.help) {
    printHelp();
    return command ? 0 : 1;
  }

  try {
    if (command === 'generate') {
      const profile = args.profile || 'development';
      const outPath = args.out;
      const format = args.format || 'table';
      if (!outPath) {
        const envelope = makeEnvelope('error', {}, ['--out is required']);
        console.error(JSON.stringify(envelope, null, 2));
        return 1;
      }
      const config = generateProfile(profile);
      const resolvedPath = writeJsonFile(outPath, config);
      const payload = { profile, outPath: resolvedPath, config };

      if (format === 'json') {
        console.log(JSON.stringify(makeEnvelope('ok', payload), null, 2));
      } else {
        console.log(`Generated ${profile} baseline at ${resolvedPath}`);
      }
      return 0;
    }

    if (command === 'audit') {
      const configPath = args.config;
      const format = args.format || 'table';
      if (!configPath) {
        const envelope = makeEnvelope('error', {}, ['--config is required']);
        console.error(JSON.stringify(envelope, null, 2));
        return 1;
      }
      const resolved = path.resolve(configPath);
      if (!fs.existsSync(resolved)) {
        const envelope = makeEnvelope('error', {}, [`Config not found: ${resolved}`]);
        console.error(JSON.stringify(envelope, null, 2));
        return 1;
      }
      const parsed = JSON.parse(fs.readFileSync(resolved, 'utf8'));
      const report = auditConfig(parsed, resolved);
      if (format === 'json') {
        console.log(JSON.stringify(makeEnvelope(reportStatus(report), report), null, 2));
      } else {
        console.log(formatAuditTable(report));
      }
      return 0;
    }

    printHelp();
    return 1;
  } catch (error) {
    const envelope = makeEnvelope('error', {}, [error instanceof Error ? error.message : String(error)]);
    console.error(JSON.stringify(envelope, null, 2));
    return 1;
  }
}
