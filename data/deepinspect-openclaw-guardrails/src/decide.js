const fs = require('fs');
const path = require('path');

function loadPolicy(policyPath) {
  const raw = fs.readFileSync(policyPath, 'utf8');
  return JSON.parse(raw);
}

function includesAny(haystack, needles) {
  const input = (haystack || '').toLowerCase();
  const compact = input.replace(/\s+/g, ' ').trim();
  const pipeNormalized = compact.replace(/\s*\|\s*/g, '|');

  return needles.some((n) => {
    const needle = String(n).toLowerCase();
    const needleCompact = needle.replace(/\s+/g, ' ').trim();
    const needlePipeNormalized = needleCompact.replace(/\s*\|\s*/g, '|');
    return (
      input.includes(needle) ||
      compact.includes(needleCompact) ||
      pipeNormalized.includes(needlePipeNormalized)
    );
  });
}

function pathOutsideWorkspace(command, workspaceRoots) {
  const lowered = (command || '').toLowerCase();
  const sensitive = ['/etc/', '/var/lib/', '/root/', '~/.ssh/', '.ssh'];
  if (includesAny(lowered, sensitive)) return true;
  if (lowered.includes('> /') || lowered.includes('>> /')) {
    return !workspaceRoots.some((root) => lowered.includes(root.toLowerCase()));
  }
  return false;
}

function hasRemoteExecPattern(command, patterns) {
  const normalized = (command || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const regexes = [
    /curl\b[^|\n]*\|\s*(sh|bash)\b/,
    /wget\b[^|\n]*\|\s*(sh|bash)\b/,
    /bash\s*<\s*\(\s*curl\b/,
    /powershell\s+-enc\b/
  ];
  if (regexes.some((r) => r.test(normalized))) return true;
  return includesAny(normalized, patterns || []);
}

function classify(input, policy) {
  const command = input.command || '';
  const reasons = [];

  if (hasRemoteExecPattern(command, policy.highRiskPatterns.remoteExec)) {
    reasons.push('REMOTE_EXEC_PATTERN');
  }

  if (includesAny(command, policy.highRiskPatterns.destructive)) {
    reasons.push('DESTRUCTIVE_PATTERN');
  }

  if (includesAny(command, policy.highRiskPatterns.privilege)) {
    reasons.push('PRIVILEGE_ESCALATION_PATTERN');
  }

  if (includesAny(command, policy.highRiskPatterns.systemMutation)) {
    reasons.push('SYSTEM_MUTATION_PATTERN');
  }

  if (includesAny(command, policy.highRiskPatterns.secretAccess)) {
    reasons.push('SECRET_ACCESS_PATTERN');
  }

  if (pathOutsideWorkspace(command, policy.workspaceRoots)) {
    reasons.push('OUTSIDE_WORKSPACE_PATH');
  }

  let decision = policy.actions.default;
  if (reasons.includes('REMOTE_EXEC_PATTERN') || reasons.includes('OUTSIDE_WORKSPACE_PATH')) {
    decision = policy.actions.critical;
  } else if (reasons.length > 0) {
    decision = policy.actions.highRisk;
  }

  return {
    decision,
    reasons,
    profile: policy.profile,
    command,
    evaluatedAt: new Date().toISOString()
  };
}

function decide(input, policyPath) {
  const policy = loadPolicy(policyPath);
  return classify(input, policy);
}

module.exports = { decide, classify, loadPolicy };
