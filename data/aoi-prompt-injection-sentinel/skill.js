#!/usr/bin/env node
/**
 * AOI Prompt Injection Sentinel
 * S-DNA: AOI-2026-0215-SDNA-PG01
 * License: MIT
 */

import crypto from 'node:crypto';

const __sdna__ = {
  protocol: 'aoineco-sdna-v1',
  id: 'AOI-2026-0215-SDNA-PG01',
  org: 'aoineco-co',
  classification: 'public-safe',
};

const Severity = {
  SAFE: 0,
  LOW: 1,
  MED: 2,
  HIGH: 3,
  CRIT: 4,
};

const Action = {
  ALLOW: 'allow',
  LOG: 'log',
  WARN: 'warn',
  BLOCK: 'block',
};

// Note: These rules are AOI-original, intentionally lightweight.
// Expand over time with verified sources + tests.
const RULES = [
  {
    id: 'R1_SYSTEM_OVERRIDE',
    severity: Severity.HIGH,
    action: Action.BLOCK,
    re: /\b(ignore|disregard|override)\b\s+(the\s+)?(system|developer)\s+(prompt|instructions)/i,
    reason: 'Attempt to override system/developer instructions',
  },
  {
    id: 'R2_SECRET_EXFIL',
    severity: Severity.CRIT,
    action: Action.BLOCK,
    re: /\b(api\s*key|token|password|secret|private\s*key|seed\s*phrase|mnemonic)\b/i,
    reason: 'Attempt to access or exfiltrate secrets',
  },
  {
    id: 'R3_FILE_HARVEST',
    severity: Severity.HIGH,
    action: Action.BLOCK,
    re: /(\.env\b|id_rsa\b|openclaw\.json\b|ssh\/|~\/.ssh\b)/i,
    reason: 'Sensitive file/path harvesting',
  },
  {
    id: 'R4_SHELL_EXEC',
    severity: Severity.MED,
    action: Action.WARN,
    re: /\b(rm\s+-rf|curl\s+http|wget\s+http|chmod\s+\+x|bash\s+-c|powershell)\b/i,
    reason: 'Shell execution / download instruction pattern',
  },
  {
    id: 'R5_SOCIAL_ENGINEERING',
    severity: Severity.MED,
    action: Action.WARN,
    re: /\b(you already approved|keep going|do the rest|no need to ask|trust me)\b/i,
    reason: 'Social-engineering style escalation attempt',
  },
];

function fingerprint(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function parseArgs(argv) {
  const [cmd, ...rest] = argv;
  const args = {};
  for (const r of rest) {
    if (r.startsWith('--')) {
      const [k, v = 'true'] = r.slice(2).split('=');
      args[k] = v;
    }
  }
  return { cmd, args };
}

async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => (data += c));
    process.stdin.on('end', () => resolve(data));
  });
}

function analyze(text) {
  const reasons = [];
  const matched = [];

  let maxSeverity = Severity.SAFE;
  let chosenAction = Action.ALLOW;

  for (const rule of RULES) {
    if (rule.re.test(text)) {
      matched.push(rule.id);
      reasons.push(rule.reason);
      if (rule.severity > maxSeverity) maxSeverity = rule.severity;
      // action precedence: block > warn > log > allow
      const rank = { allow: 0, log: 1, warn: 2, block: 3 };
      if (rank[rule.action] > rank[chosenAction]) chosenAction = rule.action;
    }
  }

  return {
    __sdna__,
    kind: 'prompt-injection-sentinel',
    severity: maxSeverity,
    action: chosenAction,
    reasons,
    matched_rules: matched,
    fingerprint: fingerprint(text),
  };
}

async function main() {
  const { cmd, args } = parseArgs(process.argv.slice(2));

  if (!cmd || ['-h', '--help', 'help'].includes(cmd)) {
    console.log(JSON.stringify({
      __sdna__,
      usage: {
        analyze: 'node skill.js analyze --text="..." | OR: echo ... | node skill.js analyze --stdin=true'
      }
    }, null, 2));
    return;
  }

  if (cmd !== 'analyze') throw new Error(`Unknown command: ${cmd}`);

  let text = '';
  if (args.stdin === 'true') text = await readStdin();
  else text = args.text || '';

  const out = analyze(text);
  console.log(JSON.stringify(out, null, 2));
}

main();
