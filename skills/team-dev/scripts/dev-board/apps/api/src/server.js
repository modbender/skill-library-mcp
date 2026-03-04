const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');
const { spawnSync } = require('child_process');
const { progressForTask } = require('../../../packages/shared');

const PORT = Number(process.env.PORT || 4310);
const ROOT = path.resolve(__dirname, '../../..');
const WEB_DIR = path.join(ROOT, 'apps/web/src');
function detectDefaultSkillDir() {
  const bundledSkillDir = path.resolve(ROOT, '..');
  const bundledMarkers = [
    path.join(bundledSkillDir, 'SKILL.md'),
    path.join(bundledSkillDir, 'scripts', 'spawn-agent.sh')
  ];
  if (bundledMarkers.every((file) => fs.existsSync(file))) {
    return bundledSkillDir;
  }

  const home = process.env.HOME || '/Users/Vint';
  const candidates = [
    '/Users/Vint/仓库/skills/dev-team',
    path.join(home, '.openclaw', 'workspace', 'skills', 'dev-team'),
    path.join(home, '.openclaw', 'workspace', 'skills', 'team-dev')
  ];

  for (const candidate of candidates) {
    const markers = [
      path.join(candidate, 'SKILL.md'),
      path.join(candidate, 'scripts', 'spawn-agent.sh')
    ];
    if (markers.every((file) => fs.existsSync(file))) {
      return candidate;
    }
  }

  return candidates[0];
}

const DEFAULT_SKILL_DIR = detectDefaultSkillDir();
const TEAM_DEV_SKILL_DIR = process.env.TEAM_DEV_SKILL_DIR || DEFAULT_SKILL_DIR;
const ARCHIVES_DIR = path.join(TEAM_DEV_SKILL_DIR, 'assets', 'logs', 'archives');
const RECENT_COMPLETED_WINDOW_MS = 7 * 24 * 60 * 60 * 1000;

const STATUS_LABELS = {
  running: '执行中',
  queued: '排队中',
  done: '已完成',
  waiting_review: '等待评审',
  approved: '已批准',
  merged: '已合并',
  cleaned: '已清理',
  failed: '失败',
  cancelled: '已取消',
  changes_requested: '需修改',
  stopped_unexpectedly: '异常中止',
  unknown: '未知'
};

const STATUS_CATEGORY_LABELS = {
  active: '进行中',
  recent_completed: '近期完成',
  completed: '已完成',
  failed: '失败',
  cleaned: '已清理',
  cancelled: '已取消',
  unknown: '未知'
};

const PHASE_LABELS = {
  queued: '排队中',
  running: '执行中',
  pr_created: '已创建 PR',
  awaiting_review: '等待评审',
  reviewed: '已评审',
  approved: '已批准',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
  changes_requested: '需修改'
};

function json(res, status, payload) {
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store'
  });
  res.end(JSON.stringify(payload, null, 2));
}

function text(res, status, payload, type = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(payload);
}

function toNumber(value) {
  if (value === null || value === undefined) return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function ensureString(value) {
  if (value === null || value === undefined) return '';
  return String(value);
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  if (value === null || value === undefined) return [];
  return [value];
}

function getPath(obj, pathParts) {
  let current = obj;
  for (const part of pathParts) {
    if (current === null || current === undefined) return undefined;
    current = current[part];
  }
  return current;
}

function firstDefined(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null) return value;
  }
  return null;
}

function firstNonEmptyString(...values) {
  for (const value of values) {
    if (value === undefined || value === null) continue;
    const text = String(value).trim();
    if (text) return text;
  }
  return '';
}

function boolFrom(value) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    if (!normalized) return false;
    if (['true', '1', 'yes', 'y', 'posted', 'done', 'ok'].includes(normalized)) return true;
    if (['false', '0', 'no', 'n', 'none'].includes(normalized)) return false;
  }
  return Boolean(value);
}

function fileMeta(filePath) {
  if (!filePath) return { path: null, exists: false, mtimeMs: null, size: null, error: 'missing_path' };
  try {
    const stat = fs.statSync(filePath);
    return { path: filePath, exists: true, mtimeMs: stat.mtimeMs, size: stat.size, error: null };
  } catch (error) {
    return { path: filePath, exists: false, mtimeMs: null, size: null, error: error.message || String(error) };
  }
}

function safeReadJson(filePath, fallback) {
  try {
    if (!fs.existsSync(filePath)) return fallback;
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return { ...fallback, _error: String(error.message || error) };
  }
}

function fileMtime(filePath) {
  try {
    return fs.statSync(filePath).mtimeMs;
  } catch {
    return null;
  }
}

function normalizeTimestampMs(value) {
  if (value === null || value === undefined || value === '') return null;
  if (value instanceof Date && Number.isFinite(value.getTime())) return value.getTime();

  if (typeof value === 'number') {
    if (!Number.isFinite(value)) return null;
    // Treat small epoch values as seconds and normalize to milliseconds.
    if (Math.abs(value) > 0 && Math.abs(value) < 1e11) return Math.round(value * 1000);
    return Math.round(value);
  }

  if (typeof value === 'string') {
    const raw = value.trim();
    if (!raw) return null;
    if (/^-?\d+(\.\d+)?$/.test(raw)) {
      return normalizeTimestampMs(Number(raw));
    }
    const parsed = Date.parse(raw);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

function toIsoStringOrNull(value) {
  const ts = normalizeTimestampMs(value);
  if (!ts) return null;
  try {
    return new Date(ts).toISOString();
  } catch {
    return null;
  }
}

function tailFile(filePath, lines = 200) {
  if (!filePath) return '';
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const list = raw.split(/\r?\n/);
    return list.slice(Math.max(0, list.length - lines)).join('\n');
  } catch (error) {
    return `无法读取日志: ${error.message}`;
  }
}

function normalizeStringList(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) => firstNonEmptyString(item))
      .filter(Boolean);
  }
  if (typeof value === 'string') {
    const raw = value.trim();
    if (!raw) return [];
    if (raw.includes(',')) {
      return raw.split(',').map((item) => item.trim()).filter(Boolean);
    }
    return [raw];
  }
  return [];
}

function normalizeQueueStatus(value) {
  const normalized = ensureString(value).trim().toLowerCase();
  if (!normalized) return 'unknown';
  if (['pending', 'waiting'].includes(normalized)) return 'queued';
  if (normalized === 'in_progress') return 'running';
  return normalized;
}

function normalizeQueuePriority(value) {
  const normalized = ensureString(value).trim().toLowerCase();
  if (!normalized) return 'normal';
  if (['p0', 'urgent', 'critical'].includes(normalized)) return 'urgent';
  if (['p1', 'high'].includes(normalized)) return 'high';
  if (['p2', 'medium', 'normal'].includes(normalized)) return 'normal';
  if (['p3', 'low'].includes(normalized)) return 'low';
  return normalized;
}

function findLinkedActiveTask(rawQueueTask, activeTasks) {
  if (!Array.isArray(activeTasks) || activeTasks.length === 0) return null;
  const activeTaskId = firstNonEmptyString(rawQueueTask && rawQueueTask.activeTaskId);
  const linkedTmuxSession = firstNonEmptyString(rawQueueTask && rawQueueTask.linkedTmuxSession);
  const tmuxSession = firstNonEmptyString(rawQueueTask && rawQueueTask.tmuxSession);
  const branch = firstNonEmptyString(rawQueueTask && rawQueueTask.branch);

  return activeTasks.find((task) => (
    (activeTaskId && ensureString(task.id) === activeTaskId) ||
    (linkedTmuxSession && ensureString(task.tmuxSession) === linkedTmuxSession) ||
    (tmuxSession && ensureString(task.tmuxSession) === tmuxSession) ||
    (branch && ensureString(task.branch) === branch)
  )) || null;
}

function normalizeQueueItem(rawQueueTask, context = {}) {
  const raw = isPlainObject(rawQueueTask) ? rawQueueTask : {};
  const activeTask = findLinkedActiveTask(raw, context.activeTasks || []);
  const preferredAgents = normalizeStringList(firstDefined(raw.preferredAgents, raw.preferred, raw.agentPreferred));
  const allowedAgents = normalizeStringList(firstDefined(raw.allowedAgents, raw.allowed, raw.agentAllowed));
  const claimRequestedAgent = firstNonEmptyString(raw.claimRequestedAgent, raw.requestedAgent) || null;
  const selectedAgent = firstNonEmptyString(raw.selectedAgent, raw.assignedAgent) || null;
  const claimedByAgent = firstNonEmptyString(raw.claimedByAgent) || null;
  const linkedAgent = firstNonEmptyString(raw.linkedAgent, activeTask && activeTask.agent) || null;

  const createdAt = normalizeTimestampMs(firstDefined(raw.createdAt, raw.created_at));
  const claimedAt = normalizeTimestampMs(firstDefined(raw.claimedAt, raw.claimed_at));
  const dispatchedAt = normalizeTimestampMs(firstDefined(raw.dispatchedAt, raw.lastDispatchAt, raw.last_dispatch_at));
  const updatedAt = normalizeTimestampMs(firstDefined(
    raw.updatedAt,
    raw.lastSyncedAt,
    raw.lastDispatchAt,
    raw.dispatchedAt,
    raw.claimedAt,
    raw.createdAt
  ));
  const linkedAt = normalizeTimestampMs(firstDefined(raw.linkedAt, raw.lastSyncedAt));

  const status = normalizeQueueStatus(firstDefined(
    raw.status,
    raw.effectiveStatus,
    raw.activeStatus,
    activeTask && activeTask.effectiveStatus,
    activeTask && activeTask.status
  ));

  const phase = firstNonEmptyString(raw.phase, raw.stage) || 'unknown';
  const priority = normalizeQueuePriority(raw.priority);
  const id = firstNonEmptyString(raw.id, raw.taskId, raw.activeTaskId, raw.branch, raw.tmuxSession) || `queue-item-${context.index || 0}`;
  const title = firstNonEmptyString(raw.title, raw.name) || id;
  const description = firstNonEmptyString(raw.description, raw.summary);

  const linkedActive = activeTask ? {
    id: activeTask.id || null,
    status: activeTask.status || null,
    effectiveStatus: activeTask.effectiveStatus || null,
    live: Boolean(activeTask.live),
    agent: activeTask.agent || null,
    branch: activeTask.branch || null,
    repoPath: activeTask.repoPath || null,
    tmuxSession: activeTask.tmuxSession || null,
    startedAt: normalizeTimestampMs(activeTask.startedAt),
    startedAtIso: toIsoStringOrNull(activeTask.startedAt),
    lastEventAt: normalizeTimestampMs(activeTask.lastEventAt),
    lastEventAtIso: toIsoStringOrNull(activeTask.lastEventAt),
    linkedAt,
    linkedAtIso: toIsoStringOrNull(linkedAt)
  } : (
    raw.activeStatus || raw.effectiveStatus || raw.activeTaskId || raw.linkedTmuxSession || raw.linkedWorktree || raw.linkedAgent
      ? {
          id: firstNonEmptyString(raw.activeTaskId) || null,
          status: firstNonEmptyString(raw.activeStatus) || null,
          effectiveStatus: firstNonEmptyString(raw.effectiveStatus, raw.activeStatus) || null,
          live: null,
          agent: linkedAgent,
          branch: firstNonEmptyString(raw.branch) || null,
          repoPath: firstNonEmptyString(raw.repoPath, raw.linkedWorktree) || null,
          tmuxSession: firstNonEmptyString(raw.linkedTmuxSession, raw.tmuxSession) || null,
          startedAt: null,
          startedAtIso: null,
          lastEventAt: linkedAt,
          lastEventAtIso: toIsoStringOrNull(linkedAt),
          linkedAt,
          linkedAtIso: toIsoStringOrNull(linkedAt)
        }
      : null
  );

  return {
    id,
    title,
    description,
    phase,
    priority,
    status,
    agent: selectedAgent || claimedByAgent || linkedAgent || claimRequestedAgent || (preferredAgents[0] || null),
    agents: {
      preferred: preferredAgents,
      allowed: allowedAgents,
      requested: claimRequestedAgent,
      selected: selectedAgent,
      claimedByAgent,
      linkedAgent
    },
    branch: firstNonEmptyString(raw.branch) || '',
    repoPath: firstNonEmptyString(raw.repoPath) || '',
    repo: firstNonEmptyString(raw.repo) || '',
    worktree: firstNonEmptyString(raw.worktree) || '',
    tmuxSession: firstNonEmptyString(raw.tmuxSession) || '',
    activeStatus: firstNonEmptyString(raw.activeStatus, linkedActive && linkedActive.status) || null,
    effectiveStatus: firstNonEmptyString(raw.effectiveStatus, linkedActive && linkedActive.effectiveStatus, status) || null,
    linkedActive,
    attempts: toNumber(raw.attempts) || 0,
    dispatchAttemptCount: toNumber(raw.dispatchAttemptCount) || 0,
    createdAt,
    claimedAt,
    dispatchedAt,
    updatedAt,
    linkedAt,
    lastSyncedAt: normalizeTimestampMs(raw.lastSyncedAt),
    createdAtIso: toIsoStringOrNull(createdAt),
    claimedAtIso: toIsoStringOrNull(claimedAt),
    dispatchedAtIso: toIsoStringOrNull(dispatchedAt),
    updatedAtIso: toIsoStringOrNull(updatedAt),
    linkedAtIso: toIsoStringOrNull(linkedAt),
    lastSyncedAtIso: toIsoStringOrNull(raw.lastSyncedAt),
    raw: rawQueueTask
  };
}

function computeQueueCounts(items) {
  const counts = {
    total: Array.isArray(items) ? items.length : 0,
    queued: 0,
    claimed: 0,
    dispatched: 0,
    running: 0,
    completed: 0,
    failed: 0,
    cancelled: 0,
    linked: 0,
    unlinked: 0,
    byStatus: {},
    byPhase: {},
    byPriority: {}
  };

  for (const item of Array.isArray(items) ? items : []) {
    const status = normalizeQueueStatus(item && item.status);
    const phase = firstNonEmptyString(item && item.phase) || 'unknown';
    const priority = normalizeQueuePriority(item && item.priority);
    counts.byStatus[status] = (counts.byStatus[status] || 0) + 1;
    counts.byPhase[phase] = (counts.byPhase[phase] || 0) + 1;
    counts.byPriority[priority] = (counts.byPriority[priority] || 0) + 1;

    if (status === 'queued') counts.queued += 1;
    if (status === 'running') counts.running += 1;
    if (['done', 'completed', 'approved', 'merged'].includes(status)) counts.completed += 1;
    if (['failed', 'error', 'stopped_unexpectedly'].includes(status)) counts.failed += 1;
    if (status === 'cancelled') counts.cancelled += 1;
    if (item && item.claimedAt) counts.claimed += 1;
    if (item && item.dispatchedAt) counts.dispatched += 1;
    if (item && item.linkedActive) counts.linked += 1;
  }

  counts.unlinked = Math.max(0, counts.total - counts.linked);
  return counts;
}

function summarizeQueueState(queueState) {
  return {
    counts: queueState.counts,
    updatedAt: queueState.updatedAt,
    updatedAtIso: queueState.updatedAtIso,
    sourcePath: queueState.sourcePath,
    sourceMeta: queueState.sourceMeta,
    registryError: queueState.registryError
  };
}

function loadQueueState(options = {}) {
  const sourcePath = path.join(TEAM_DEV_SKILL_DIR, 'assets', 'tasks.json');
  const sourceMeta = fileMeta(sourcePath);
  const rawRegistry = safeReadJson(sourcePath, { items: [], updatedAt: null, queueStats: null });

  let rawItems = [];
  if (Array.isArray(rawRegistry)) rawItems = rawRegistry;
  else if (isPlainObject(rawRegistry) && Array.isArray(rawRegistry.items)) rawItems = rawRegistry.items;
  else if (isPlainObject(rawRegistry) && Array.isArray(rawRegistry.tasks)) rawItems = rawRegistry.tasks;
  else if (isPlainObject(rawRegistry) && Array.isArray(rawRegistry.queue)) rawItems = rawRegistry.queue;

  const items = rawItems.map((item, index) => normalizeQueueItem(item, {
    index,
    activeTasks: options.activeTasks || []
  }));
  const counts = computeQueueCounts(items);
  const updatedAt = normalizeTimestampMs(firstDefined(rawRegistry && rawRegistry.updatedAt, sourceMeta.mtimeMs));

  return {
    items,
    counts,
    updatedAt,
    updatedAtIso: toIsoStringOrNull(updatedAt),
    sourcePath,
    sourceMeta,
    queueStats: isPlainObject(rawRegistry && rawRegistry.queueStats) ? rawRegistry.queueStats : null,
    registryError: rawRegistry && rawRegistry._error ? rawRegistry._error : null
  };
}

function tailFileWithMeta(filePath, lines = 200) {
  if (!filePath) {
    return { content: '', error: 'missing_path', meta: fileMeta(filePath) };
  }
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const list = raw.split(/\r?\n/);
    return {
      content: list.slice(Math.max(0, list.length - lines)).join('\n'),
      error: null,
      meta: fileMeta(filePath)
    };
  } catch (error) {
    return {
      content: '',
      error: error.message || String(error),
      meta: fileMeta(filePath)
    };
  }
}

function humanDuration(ms) {
  if (!Number.isFinite(ms) || ms === null) return null;
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (days > 0) return `${days}天${hours}小时`;
  if (hours > 0) return `${hours}小时${minutes}分钟`;
  if (minutes > 0) return `${minutes}分钟${seconds}秒`;
  return `${seconds}秒`;
}

function lastEventAtForTask(task, logMtime) {
  const candidates = [
    toNumber(task.lastEventAt),
    toNumber(task.updatedAt),
    toNumber(task.completedAt),
    toNumber(task.failedAt),
    toNumber(task.cancelledAt),
    toNumber(task.startedAt),
    toNumber(logMtime)
  ].filter((value) => Number.isFinite(value));
  if (candidates.length === 0) return null;
  return Math.max(...candidates);
}

function normalizeStatus(status) {
  if (!status) return 'unknown';
  return ensureString(status).toLowerCase();
}

function statusLabelFor(status) {
  return STATUS_LABELS[status] || STATUS_LABELS.unknown;
}

function phaseLabelFor(progressStage, statusLabel) {
  if (!progressStage) return statusLabel;
  return PHASE_LABELS[progressStage] || statusLabel;
}

function collectTaskSources(task) {
  const checks = isPlainObject(task && task.checks) ? task.checks : {};
  return [task || {}, checks];
}

function pickValue(sources, pathOptions) {
  for (const source of sources) {
    for (const pathOption of pathOptions) {
      const parts = Array.isArray(pathOption) ? pathOption : String(pathOption).split('.');
      const value = getPath(source, parts);
      if (value !== undefined && value !== null) return value;
    }
  }
  return null;
}

function pickObject(sources, pathOptions) {
  const value = pickValue(sources, pathOptions);
  return isPlainObject(value) ? value : null;
}

function normalizePrState(value) {
  if (value === null || value === undefined) return null;
  const raw = String(value).trim();
  if (!raw) return null;
  return raw.toLowerCase();
}

function normalizeReviewDecision(value) {
  if (value === null || value === undefined) return null;
  const raw = String(value).trim();
  if (!raw) return null;
  const normalized = raw.toLowerCase();
  if (normalized === 'changes_requested' || normalized === 'changes-requested') return 'changes_requested';
  if (normalized === 'approved' || normalized === 'approve') return 'approved';
  if (normalized === 'review_required' || normalized === 'review-required' || normalized === 'required') return 'review_required';
  return normalized;
}

function normalizeMergeStateStatus(value) {
  if (value === null || value === undefined) return null;
  const raw = String(value).trim();
  if (!raw) return null;
  return raw.toLowerCase();
}

function extractPrStatus(task) {
  const sources = collectTaskSources(task);
  const prNumberRaw = pickValue(sources, [
    'prNumber',
    'pr.number',
    'pullRequest.number',
    'checks.prNumber',
    'checks.pr.number',
    'checks.pullRequest.number',
    'checks.github.pr.number',
    'checks.github.pullRequest.number'
  ]);
  const prNumber = toNumber(prNumberRaw) || (prNumberRaw ? Number(prNumberRaw) || null : null);
  const prUrl = firstNonEmptyString(
    pickValue(sources, [
      'prUrl',
      'pr.url',
      'pr.htmlUrl',
      'pullRequest.url',
      'pullRequest.htmlUrl',
      'checks.prUrl',
      'checks.pr.url',
      'checks.pullRequest.url',
      'checks.github.pr.url',
      'checks.github.pr.htmlUrl',
      'checks.github.pullRequest.url',
      'checks.github.pullRequest.htmlUrl'
    ])
  ) || null;
  const prState = normalizePrState(pickValue(sources, [
    'prState',
    'pr.state',
    'pullRequest.state',
    'checks.prState',
    'checks.pr.state',
    'checks.pullRequest.state',
    'checks.github.pr.state',
    'checks.github.pullRequest.state'
  ]));
  const reviewDecision = normalizeReviewDecision(pickValue(sources, [
    'reviewDecision',
    'pr.reviewDecision',
    'pullRequest.reviewDecision',
    'checks.reviewDecision',
    'checks.pr.reviewDecision',
    'checks.pullRequest.reviewDecision',
    'checks.github.pr.reviewDecision',
    'checks.github.pullRequest.reviewDecision'
  ]));
  const mergeStateStatus = normalizeMergeStateStatus(pickValue(sources, [
    'mergeStateStatus',
    'pr.mergeStateStatus',
    'pullRequest.mergeStateStatus',
    'checks.mergeStateStatus',
    'checks.pr.mergeStateStatus',
    'checks.pullRequest.mergeStateStatus',
    'checks.github.pr.mergeStateStatus',
    'checks.github.pullRequest.mergeStateStatus'
  ]));

  return { prNumber, prUrl, prState, reviewDecision, mergeStateStatus };
}

function normalizeCheckState(value) {
  if (value === null || value === undefined) return 'unknown';
  const normalized = String(value).trim().toLowerCase();
  if (!normalized) return 'unknown';
  if (['success', 'successful', 'passed', 'pass', 'ok', 'completed', 'neutral', 'skipped'].includes(normalized)) return 'pass';
  if (['failure', 'failed', 'fail', 'error', 'timed_out', 'timedout', 'cancelled', 'action_required', 'startup_failure'].includes(normalized)) return 'fail';
  if (['pending', 'queued', 'in_progress', 'in-progress', 'requested', 'expected', 'waiting', 'running'].includes(normalized)) return 'pending';
  return normalized;
}

function normalizeRequiredCheckEntry(entry) {
  if (!entry) return null;
  if (typeof entry === 'string') {
    return { name: entry, state: 'pending', required: true };
  }
  if (!isPlainObject(entry)) return null;
  const name = firstNonEmptyString(entry.name, entry.context, entry.title, entry.id, entry.key) || 'unnamed';
  const state = normalizeCheckState(firstDefined(
    entry.bucket,
    entry.status,
    entry.state,
    entry.conclusion,
    entry.result,
    entry.outcome
  ));
  const required = entry.required === undefined ? true : boolFrom(entry.required);
  return { name, state, required };
}

function collectRequiredCheckEntries(task) {
  const checks = isPlainObject(task && task.checks) ? task.checks : {};
  const candidates = [];
  const pushCandidate = (value) => {
    if (value === null || value === undefined) return;
    candidates.push(value);
  };

  pushCandidate(checks.requiredChecks);
  pushCandidate(checks.required_checks);
  pushCandidate(getPath(checks, ['ci', 'requiredChecks']));
  pushCandidate(getPath(checks, ['ci', 'checks']));
  pushCandidate(getPath(checks, ['pr', 'requiredChecks']));
  pushCandidate(getPath(checks, ['pullRequest', 'requiredChecks']));
  pushCandidate(getPath(checks, ['github', 'requiredChecks']));
  pushCandidate(getPath(checks, ['github', 'checks']));
  pushCandidate(getPath(checks, ['statusCheckRollup', 'contexts', 'nodes']));
  pushCandidate(getPath(checks, ['statusCheckRollup', 'contexts']));

  const entries = [];
  for (const candidate of candidates) {
    let list = [];
    if (Array.isArray(candidate)) {
      list = candidate;
    } else if (isPlainObject(candidate) && Array.isArray(candidate.nodes)) {
      list = candidate.nodes;
    } else if (isPlainObject(candidate) && Array.isArray(candidate.checks)) {
      list = candidate.checks;
    } else if (isPlainObject(candidate)) {
      list = Object.values(candidate);
    }
    for (const item of list) {
      const normalized = normalizeRequiredCheckEntry(item);
      if (normalized && normalized.required) entries.push(normalized);
    }
    if (entries.length > 0) break;
  }
  return entries;
}

function buildCiStatus(task) {
  const requiredChecks = collectRequiredCheckEntries(task);
  const stats = { total: 0, passed: 0, failed: 0, pending: 0, other: 0 };

  for (const item of requiredChecks) {
    stats.total += 1;
    if (item.state === 'pass') stats.passed += 1;
    else if (item.state === 'fail') stats.failed += 1;
    else if (item.state === 'pending') stats.pending += 1;
    else stats.other += 1;
  }

  let bucket = 'none';
  if (stats.total > 0) {
    if (stats.failed > 0) bucket = 'fail';
    else if (stats.pending > 0 || stats.passed < stats.total) bucket = 'pending';
    else bucket = 'pass';
  }

  let summary = '无必需检查';
  if (stats.total > 0) {
    const parts = [`${stats.passed}/${stats.total} 通过`];
    if (stats.failed > 0) parts.push(`${stats.failed} 失败`);
    if (stats.pending > 0) parts.push(`${stats.pending} 等待`);
    if (stats.other > 0) parts.push(`${stats.other} 未知`);
    summary = parts.join('，');
  }

  return {
    ciStatus: {
      requiredChecksBucket: bucket,
      requiredChecksSummary: summary,
      requiredChecksStats: stats
    }
  };
}

function normalizeVerdict(value) {
  if (value === null || value === undefined) return null;
  const raw = String(value).trim();
  if (!raw) return null;
  return raw.toLowerCase();
}

function extractReviewStatus(task) {
  const sources = collectTaskSources(task);
  const aggregateSource = pickObject(sources, [
    'reviewAggregate',
    'checks.reviewAggregate',
    'checks.aiReview.aggregate',
    'checks.ai_review.aggregate',
    'checks.aiReview',
    'checks.ai_review',
    'checks.review.aggregate'
  ]) || {};

  const verdict = normalizeVerdict(firstDefined(
    aggregateSource.verdict,
    getPath(aggregateSource, ['result', 'verdict'])
  ));
  const taskStatus = normalizeVerdict(firstDefined(
    aggregateSource.taskStatus,
    aggregateSource.status,
    getPath(aggregateSource, ['task', 'status'])
  ));
  const recommendedAction = normalizeVerdict(firstDefined(
    aggregateSource.recommendedAction,
    aggregateSource.action,
    getPath(aggregateSource, ['task', 'recommendedAction'])
  ));

  const reviewSummaryCandidates = [
    pickValue(sources, ['reviewSummary', 'checks.reviewSummary', 'checks.aiReview.reviewSummary', 'checks.ai_review.reviewSummary']),
    pickValue(sources, ['checks.aiReview.reviewers', 'checks.ai_review.reviewers', 'checks.reviewers', 'checks.review.summary'])
  ];

  let reviewSummary = [];
  for (const candidate of reviewSummaryCandidates) {
    const items = asArray(candidate)
      .map((item) => {
        if (!item) return null;
        if (typeof item === 'string') {
          return { reviewer: item, verdict: null, posted: false };
        }
        if (!isPlainObject(item)) return null;
        const reviewer = firstNonEmptyString(item.reviewer, item.name, item.id, item.agent, item.login) || 'unknown';
        const itemVerdict = normalizeVerdict(firstDefined(item.verdict, item.result, item.status));
        const postedAt = toNumber(firstDefined(item.postedAt, item.createdAt, item.updatedAt));
        const posted = item.posted !== undefined
          ? boolFrom(item.posted)
          : Boolean(postedAt || firstNonEmptyString(item.url, item.commentUrl, item.reviewUrl));
        return {
          reviewer,
          verdict: itemVerdict,
          posted,
          postedAt: postedAt || null
        };
      })
      .filter(Boolean);
    if (items.length) {
      reviewSummary = items;
      break;
    }
  }

  return {
    reviewAggregate: {
      verdict,
      taskStatus,
      recommendedAction
    },
    reviewSummary
  };
}

function extractFixupStatus(task, reviewAggregate) {
  const sources = collectTaskSources(task);
  const fixup = pickObject(sources, [
    'fixup',
    'checks.fixup',
    'checks.aiReview.fixup',
    'checks.ai_review.fixup',
    'checks.review.fixup'
  ]) || {};

  const target = isPlainObject(fixup.target) ? fixup.target : {};
  const fixupSuggestedRaw = firstDefined(
    fixup.suggested,
    fixup.fixupSuggested,
    fixup.shouldCreateFixup,
    reviewAggregate && reviewAggregate.recommendedAction === 'request_fixup'
  );
  const fixupSuggested = fixupSuggestedRaw === null ? false : boolFrom(fixupSuggestedRaw);
  const fixupRecommendation = firstNonEmptyString(
    fixup.recommendation,
    fixup.fixupRecommendation,
    fixup.reason,
    fixup.message
  ) || null;
  const fixupTargetAgent = firstNonEmptyString(target.agent, fixup.targetAgent, fixup.agent) || null;
  const fixupTargetBranch = firstNonEmptyString(target.branch, fixup.targetBranch, fixup.branch) || null;
  const fixupRequestedAt = toNumber(firstDefined(
    fixup.requestedAt,
    fixup.fixupRequestedAt,
    fixup.createdAt
  ));
  const fixupRequestMode = firstNonEmptyString(
    fixup.requestMode,
    fixup.fixupRequestMode,
    fixup.mode
  ) || null;

  return {
    fixupSuggested,
    fixupRecommendation,
    fixupTarget: {
      agent: fixupTargetAgent,
      branch: fixupTargetBranch
    },
    fixupRequestedAt: fixupRequestedAt || null,
    fixupRequestMode
  };
}

const PIPELINE_STAGE_LABELS = {
  coding: '编码中',
  pr_open: 'PR 已打开',
  ci_waiting: '等待 CI',
  ai_review: 'AI 评审中',
  human_approve: '等待人工批准',
  merge_ready: '可合并',
  merged: '已合并',
  cleaned: '已清理'
};

const ATTENTION_LEVEL_LABELS = {
  normal: '正常',
  warning: '注意',
  critical: '紧急'
};

function derivePipelineStatus(task, aggregates) {
  const status = normalizeStatus(task.status);
  const effectiveStatus = normalizeStatus(task.effectiveStatus || task.status);
  const hasPr = Boolean(aggregates.prNumber || aggregates.prUrl);
  const prOpen = ['open', 'opened'].includes(aggregates.prState || '');
  const reviewDecision = aggregates.reviewDecision || null;
  const mergeStateStatus = aggregates.mergeStateStatus || null;
  const ciBucket = aggregates.ciStatus && aggregates.ciStatus.requiredChecksBucket || 'none';
  const aiTaskStatus = aggregates.reviewAggregate && aggregates.reviewAggregate.taskStatus || null;
  const aiVerdict = aggregates.reviewAggregate && aggregates.reviewAggregate.verdict || null;

  let pipelineStage = 'coding';
  if (effectiveStatus === 'cleaned') {
    pipelineStage = 'cleaned';
  } else if (effectiveStatus === 'merged' || aggregates.prState === 'merged') {
    pipelineStage = 'merged';
  } else if (!hasPr) {
    pipelineStage = 'coding';
  } else if (prOpen && (ciBucket === 'pending' || ciBucket === 'fail')) {
    pipelineStage = 'ci_waiting';
  } else if (prOpen && (aiTaskStatus === 'running' || aiTaskStatus === 'pending' || aiVerdict === 'pending')) {
    pipelineStage = 'ai_review';
  } else if (prOpen && (reviewDecision === 'approved')) {
    pipelineStage = ciBucket === 'pass' ? 'merge_ready' : 'human_approve';
  } else if (prOpen && ciBucket === 'pass' && ['clean', 'has_hooks', 'unstable'].includes(mergeStateStatus || '')) {
    pipelineStage = 'human_approve';
  } else if (prOpen) {
    pipelineStage = 'pr_open';
  }

  let attentionLevel = 'normal';
  if (pipelineStage === 'merge_ready' || pipelineStage === 'merged' || pipelineStage === 'cleaned') {
    attentionLevel = 'normal';
  } else if (['failed', 'stopped_unexpectedly', 'cancelled'].includes(effectiveStatus) || ciBucket === 'fail') {
    attentionLevel = 'critical';
  } else if (
    ['waiting_review', 'changes_requested'].includes(effectiveStatus) ||
    ciBucket === 'pending' ||
    Boolean(aggregates.fixupSuggested) ||
    reviewDecision === 'changes_requested' ||
    aiVerdict === 'reject'
  ) {
    attentionLevel = 'warning';
  }

  let nextActionHint = '继续推进任务';
  if (effectiveStatus === 'cleaned') nextActionHint = '任务已清理，无需操作';
  else if (effectiveStatus === 'merged' || aggregates.prState === 'merged') nextActionHint = '等待归档或清理工作树';
  else if (attentionLevel === 'critical' && ciBucket === 'fail') nextActionHint = '修复 CI 失败后重试';
  else if (attentionLevel === 'critical' && ['failed', 'stopped_unexpectedly'].includes(effectiveStatus)) nextActionHint = '检查日志并恢复任务执行';
  else if (!hasPr) nextActionHint = status === 'queued' ? '等待任务开始编码并创建 PR' : '继续编码并创建 PR';
  else if (ciBucket === 'pending') nextActionHint = '等待必需 CI 检查完成';
  else if (aggregates.reviewAggregate && ['running', 'pending'].includes(aggregates.reviewAggregate.taskStatus || '')) nextActionHint = '等待 AI review 结果';
  else if (aggregates.fixupSuggested) nextActionHint = '根据 fixup 建议处理后更新 PR';
  else if (reviewDecision === 'changes_requested') nextActionHint = '处理 review 修改意见';
  else if (reviewDecision === 'approved' && ciBucket === 'pass') nextActionHint = '可执行合并';
  else if (prOpen) nextActionHint = '等待人工评审/批准';

  return {
    pipelineStage,
    pipelineStageLabel: PIPELINE_STAGE_LABELS[pipelineStage] || pipelineStage,
    attentionLevel,
    attentionLevelLabel: ATTENTION_LEVEL_LABELS[attentionLevel] || attentionLevel,
    nextActionHint
  };
}

function deriveBoardSignals(task, effectiveStatusValue) {
  const taskLike = { ...task, effectiveStatus: effectiveStatusValue };
  const pr = extractPrStatus(taskLike);
  const { ciStatus } = buildCiStatus(taskLike);
  const review = extractReviewStatus(taskLike);
  const fixup = extractFixupStatus(taskLike, review.reviewAggregate);
  const pipeline = derivePipelineStatus(taskLike, {
    ...pr,
    ciStatus,
    reviewAggregate: review.reviewAggregate,
    fixupSuggested: fixup.fixupSuggested
  });

  return {
    ...pr,
    ciStatus,
    reviewAggregate: review.reviewAggregate,
    reviewSummary: review.reviewSummary,
    ...fixup,
    ...pipeline
  };
}

function statusCategoryFor(status, effectiveStatus) {
  const normalized = normalizeStatus(effectiveStatus || status);
  if (normalized === 'running' || normalized === 'queued') return 'active';
  if (normalized === 'cleaned') return 'cleaned';
  if (normalized === 'failed' || normalized === 'stopped_unexpectedly') return 'failed';
  if (normalized === 'cancelled') return 'cancelled';
  if (['done', 'waiting_review', 'approved', 'merged'].includes(normalized)) return 'recent_completed';
  return 'unknown';
}

function isTerminalStatus(status) {
  const normalized = normalizeStatus(status);
  return ['done', 'waiting_review', 'approved', 'merged', 'cleaned', 'failed', 'cancelled'].includes(normalized);
}

function isActionNeededFor(status, effectiveStatus) {
  const normalized = normalizeStatus(effectiveStatus || status);
  return ['failed', 'changes_requested', 'stopped_unexpectedly', 'waiting_review'].includes(normalized);
}

function deriveDurations(task, now) {
  const startedAt = toNumber(task.startedAt);
  const completedAt = toNumber(task.completedAt || task.failedAt || task.cancelledAt);
  if (!startedAt) return { durationMs: null, humanDuration: null };
  const end = completedAt || now;
  const durationMs = end - startedAt;
  return { durationMs, humanDuration: humanDuration(durationMs) };
}

function parseJsonLine(line) {
  if (!line) return null;
  try {
    return JSON.parse(line);
  } catch (error) {
    return { _error: error.message || String(error), _raw: line };
  }
}

function readJsonlFile(filePath, limit = 200) {
  const meta = fileMeta(filePath);
  if (!meta.exists) {
    return { items: [], meta: { ...meta, parsed: 0, errors: 0 } };
  }
  const raw = fs.readFileSync(filePath, 'utf8');
  const lines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
  const sliceStart = Math.max(0, lines.length - limit);
  const selected = lines.slice(sliceStart);
  const items = [];
  let errors = 0;
  for (let i = 0; i < selected.length; i += 1) {
    const line = selected[i];
    const parsed = parseJsonLine(line);
    const lineNumber = sliceStart + i + 1;
    if (parsed && parsed._error) errors += 1;
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      items.push({ ...parsed, __line: lineNumber });
    } else if (parsed !== null) {
      items.push({ value: parsed, __line: lineNumber });
    }
  }
  return { items, meta: { ...meta, parsed: items.length, errors } };
}

function tmuxSessionAlive(sessionName) {
  if (!sessionName) return false;
  const proc = spawnSync('tmux', ['has-session', '-t', sessionName], { stdio: 'ignore' });
  return proc.status === 0;
}

function resolveLogPath(task) {
  if (!task) return null;
  if (task.logFile) {
    if (path.isAbsolute(task.logFile)) return task.logFile;
    return path.resolve(TEAM_DEV_SKILL_DIR, task.logFile);
  }
  if (task.tmuxSession) {
    return path.join(TEAM_DEV_SKILL_DIR, 'assets', 'logs', `${task.tmuxSession}.log`);
  }
  return null;
}

function deriveTask(task) {
  const logPath = resolveLogPath(task);
  const progress = progressForTask(task);
  const live = tmuxSessionAlive(task.tmuxSession);
  const status = normalizeStatus(task.status);
  const effectiveStatus = status === 'running' && !live ? 'stopped_unexpectedly' : status;
  const lastEventAt = lastEventAtForTask(task, fileMtime(logPath));
  const { durationMs, humanDuration: durationLabel } = deriveDurations(task, Date.now());
  const statusCategory = statusCategoryFor(status, effectiveStatus);
  const statusLabel = statusLabelFor(effectiveStatus);
  const phaseLabel = phaseLabelFor(progress.stage, statusLabel);
  const boardSignals = deriveBoardSignals(task, effectiveStatus);

  return {
    id: task.id || task.branch || task.tmuxSession,
    agent: task.agent || 'unknown',
    description: ensureString(task.description),
    repo: ensureString(task.repo),
    repoPath: ensureString(task.repoPath),
    worktree: ensureString(task.worktree),
    branch: ensureString(task.branch),
    tmuxSession: ensureString(task.tmuxSession),
    status,
    effectiveStatus,
    live,
    retryCount: Number(task.retryCount || 0),
    checks: task.checks || {},
    startedAt: task.startedAt || null,
    completedAt: task.completedAt || task.failedAt || task.cancelledAt || null,
    logFile: logPath,
    logMtime: fileMtime(logPath),
    notifyOnComplete: Boolean(task.notifyOnComplete),
    progress,
    statusLabel,
    statusCategory,
    statusCategoryLabel: STATUS_CATEGORY_LABELS[statusCategory] || STATUS_CATEGORY_LABELS.unknown,
    phaseLabel,
    durationMs,
    humanDuration: durationLabel,
    isTerminal: isTerminalStatus(effectiveStatus),
    isActionNeeded: isActionNeededFor(status, effectiveStatus),
    lastEventAt,
    ...boardSignals,
    raw: task
  };
}

function deriveHistoricalTask(task, sourceMeta) {
  const logPath = resolveLogPath(task);
  const progress = progressForTask(task);
  const status = normalizeStatus(task.status);
  const effectiveStatus = status;
  const logMtime = fileMtime(logPath);
  const lastEventAt = lastEventAtForTask(task, logMtime);
  const { durationMs, humanDuration: durationLabel } = deriveDurations(task, Date.now());
  const statusCategory = statusCategoryFor(status, effectiveStatus);
  const statusLabel = statusLabelFor(effectiveStatus);
  const phaseLabel = phaseLabelFor(progress.stage, statusLabel);
  const boardSignals = deriveBoardSignals(task, effectiveStatus);

  return {
    id: task.id || task.branch || task.tmuxSession || task.__line,
    agent: task.agent || 'unknown',
    description: ensureString(task.description),
    repo: ensureString(task.repo),
    repoPath: ensureString(task.repoPath),
    worktree: ensureString(task.worktree),
    branch: ensureString(task.branch),
    tmuxSession: ensureString(task.tmuxSession),
    status,
    effectiveStatus,
    live: false,
    retryCount: Number(task.retryCount || 0),
    checks: task.checks || {},
    startedAt: task.startedAt || null,
    completedAt: task.completedAt || task.failedAt || task.cancelledAt || null,
    logFile: logPath,
    logMtime,
    notifyOnComplete: Boolean(task.notifyOnComplete),
    progress,
    statusLabel,
    statusCategory,
    statusCategoryLabel: STATUS_CATEGORY_LABELS[statusCategory] || STATUS_CATEGORY_LABELS.unknown,
    phaseLabel,
    durationMs,
    humanDuration: durationLabel,
    isTerminal: isTerminalStatus(effectiveStatus),
    isActionNeeded: isActionNeededFor(status, effectiveStatus),
    lastEventAt,
    ...boardSignals,
    source: sourceMeta,
    raw: task
  };
}

function computeCounts(tasks, now = Date.now()) {
  const counts = {
    total: tasks.length,
    running: 0,
    queued: 0,
    live: 0,
    active: 0,
    failed: 0,
    cleaned: 0,
    cancelled: 0,
    done: 0,
    waitingReview: 0,
    approved: 0,
    merged: 0,
    completed: 0,
    terminal: 0,
    actionNeeded: 0,
    recentCompleted: 0
  };
  for (const task of tasks) {
    const status = normalizeStatus(task.status);
    if (status === 'running') counts.running += 1;
    if (status === 'queued') counts.queued += 1;
    if (task.live) counts.live += 1;
    if (task.statusCategory === 'active') counts.active += 1;
    if (task.statusCategory === 'failed') counts.failed += 1;
    if (task.statusCategory === 'cleaned') counts.cleaned += 1;
    if (task.statusCategory === 'cancelled') counts.cancelled += 1;
    if (status === 'done') counts.done += 1;
    if (status === 'waiting_review') counts.waitingReview += 1;
    if (status === 'approved') counts.approved += 1;
    if (status === 'merged') counts.merged += 1;
    if (['done', 'waiting_review', 'approved', 'merged'].includes(status)) counts.completed += 1;
    if (task.isTerminal) counts.terminal += 1;
    if (task.isActionNeeded) counts.actionNeeded += 1;

    if (['done', 'waiting_review', 'approved', 'merged'].includes(status)) {
      const completedAt = toNumber(task.completedAt) || toNumber(task.lastEventAt);
      if (!completedAt || completedAt >= now - RECENT_COMPLETED_WINDOW_MS) {
        counts.recentCompleted += 1;
      }
    }
  }
  return counts;
}

function loadBoardState() {
  const tasksFile = path.join(TEAM_DEV_SKILL_DIR, 'assets', 'active-tasks.json');
  const notifyFile = path.join(TEAM_DEV_SKILL_DIR, 'assets', 'notifications.json');
  const cronLog = path.join(TEAM_DEV_SKILL_DIR, 'assets', 'logs', 'cron.log');
  const cleanupLog = path.join(TEAM_DEV_SKILL_DIR, 'assets', 'logs', 'cleanup.log');

  const registry = safeReadJson(tasksFile, { agents: [], activeCount: 0 });
  const notifications = safeReadJson(notifyFile, []);
  const rawTasks = Array.isArray(registry.agents) ? registry.agents : [];
  const tasks = rawTasks.map(deriveTask).sort((a, b) => (b.startedAt || 0) - (a.startedAt || 0));
  const counts = computeCounts(tasks);
  const orchestratorStatus = counts.active > 0 ? 'active' : (counts.failed > 0 ? 'attention' : 'idle');

  return {
    meta: {
      generatedAt: Date.now(),
      teamDevSkillDir: TEAM_DEV_SKILL_DIR,
      tasksFile,
      notificationsFile: notifyFile,
      cronLog,
      cleanupLog,
      registryError: registry._error || null,
      notificationsError: notifications && notifications._error ? notifications._error : null
    },
    mainAgent: {
      id: 'dev-team-orchestrator',
      name: 'dev-team orchestrator',
      status: orchestratorStatus,
      activeCount: counts.active,
      liveCount: counts.live,
      failedCount: counts.failed,
      doneCount: counts.completed + counts.cleaned,
      totalTasks: counts.total,
      counts,
      notificationsPending: Array.isArray(notifications) ? notifications.length : 0,
      monitors: {
        tasksRegistryExists: fs.existsSync(tasksFile),
        cronLogExists: fs.existsSync(cronLog),
        cleanupLogExists: fs.existsSync(cleanupLog)
      }
    },
    tasks,
    notifications: Array.isArray(notifications) ? notifications : []
  };
}

function listArchiveFiles() {
  try {
    if (!fs.existsSync(ARCHIVES_DIR)) return [];
    const entries = fs.readdirSync(ARCHIVES_DIR);
    const files = entries
      .filter((name) => name.endsWith('.jsonl'))
      .map((name) => {
        const filePath = path.join(ARCHIVES_DIR, name);
        const meta = fileMeta(filePath);
        return { name, path: filePath, meta };
      })
      .filter((entry) => entry.meta.exists)
      .sort((a, b) => (b.meta.mtimeMs || 0) - (a.meta.mtimeMs || 0));
    return files;
  } catch (error) {
    return [];
  }
}

function loadArchives(options = {}) {
  const limit = Math.max(1, Math.min(5000, Number(options.limit || 200)));
  const fileName = options.file ? String(options.file) : null;
  const files = listArchiveFiles();
  const selectedFiles = fileName
    ? files.filter((entry) => entry.name === fileName)
    : files;
  const items = [];
  const archives = [];

  for (const entry of selectedFiles) {
    if (items.length >= limit) break;
    const remaining = limit - items.length;
    const parsed = readJsonlFile(entry.path, remaining);
    archives.push({
      name: entry.name,
      path: entry.path,
      mtimeMs: entry.meta.mtimeMs,
      size: entry.meta.size,
      parsed: parsed.meta.parsed,
      errors: parsed.meta.errors
    });

    for (const record of parsed.items) {
      if (items.length >= limit) break;
      const sourceMeta = {
        type: 'archive',
        file: entry.name,
        filePath: entry.path,
        fileMtimeMs: entry.meta.mtimeMs,
        line: record.__line || null
      };
      if (record._error) {
        items.push({
          id: `parse_error:${entry.name}:${record.__line || 'unknown'}`,
          status: 'unknown',
          statusLabel: STATUS_LABELS.unknown,
          statusCategory: 'unknown',
          statusCategoryLabel: STATUS_CATEGORY_LABELS.unknown,
          phaseLabel: STATUS_LABELS.unknown,
          isTerminal: false,
          isActionNeeded: true,
          lastEventAt: entry.meta.mtimeMs || null,
          description: '归档记录解析失败',
          error: record._error,
          rawLine: record._raw,
          source: sourceMeta,
          raw: record
        });
        continue;
      }
      items.push(deriveHistoricalTask(record, sourceMeta));
    }
  }

  items.sort((a, b) => (b.lastEventAt || 0) - (a.lastEventAt || 0));

  return {
    meta: {
      generatedAt: Date.now(),
      archivesDir: ARCHIVES_DIR,
      availableFiles: files.map((entry) => entry.name),
      selectedFile: fileName
    },
    archives,
    items
  };
}

function buildBoardView(tasks, now = Date.now()) {
  const active = [];
  const recentCompleted = [];
  const failed = [];
  const cleaned = [];
  const cancelled = [];
  const unknown = [];
  const olderCompleted = [];

  for (const task of tasks) {
    if (task.statusCategory === 'active') {
      active.push(task);
      continue;
    }
    if (task.statusCategory === 'failed') {
      failed.push(task);
      continue;
    }
    if (task.statusCategory === 'cleaned') {
      cleaned.push(task);
      continue;
    }
    if (task.statusCategory === 'cancelled') {
      cancelled.push(task);
      continue;
    }
    if (task.statusCategory === 'recent_completed') {
      const completedAt = toNumber(task.completedAt) || toNumber(task.lastEventAt);
      if (!completedAt || completedAt >= now - RECENT_COMPLETED_WINDOW_MS) {
        recentCompleted.push(task);
      } else {
        olderCompleted.push(task);
      }
      continue;
    }
    unknown.push(task);
  }

  return {
    active,
    recentCompleted,
    failed,
    cleaned,
    cancelled,
    olderCompleted,
    unknown,
    counts: computeCounts(tasks, now),
    recentWindowMs: RECENT_COMPLETED_WINDOW_MS
  };
}

function serveStatic(reqPath, res) {
  const target = reqPath === '/' ? '/index.html' : reqPath;
  const safePath = path.normalize(target).replace(/^\.+/, '');
  const filePath = path.join(WEB_DIR, safePath);
  if (!filePath.startsWith(WEB_DIR)) {
    text(res, 403, 'Forbidden');
    return;
  }
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    const indexPath = path.join(WEB_DIR, 'index.html');
    return text(res, 200, fs.readFileSync(indexPath), 'text/html; charset=utf-8');
  }

  const ext = path.extname(filePath).toLowerCase();
  const types = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8'
  };
  text(res, 200, fs.readFileSync(filePath), types[ext] || 'application/octet-stream');
}

const LOCAL_ACTIONS_ENABLED = process.env.ENABLE_LOCAL_ACTIONS === '1';
const ACTION_TIMEOUT_MS_DEFAULT = 60 * 1000;
const ACTION_TIMEOUT_MS_MAX = 5 * 60 * 1000;
const ACTION_OUTPUT_MAX_BYTES = 20 * 1024;
const ALLOWED_REVIEWERS = new Set(['codex', 'claude', 'gemini', 'cursor']);
const ACTION_SCRIPT_ALLOWLIST = Object.freeze({
  'check-agents': 'check-agents.sh',
  cleanup: 'cleanup-worktrees.sh',
  'ai-review': 'review-agent.sh',
  fixup: 'request-fixup.sh'
});

function readJsonBody(req, options = {}) {
  const maxBytes = Math.max(1024, Math.min(1024 * 1024, Number(options.maxBytes || 64 * 1024)));
  return new Promise((resolve, reject) => {
    let raw = '';
    let size = 0;

    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > maxBytes) {
        reject(Object.assign(new Error('request body too large'), { statusCode: 413, code: 'body_too_large' }));
        req.destroy();
        return;
      }
      raw += chunk.toString('utf8');
    });

    req.on('end', () => {
      if (!raw.trim()) return resolve({});
      try {
        const parsed = JSON.parse(raw);
        if (!isPlainObject(parsed)) {
          return reject(Object.assign(new Error('JSON body must be an object'), { statusCode: 400, code: 'invalid_body' }));
        }
        resolve(parsed);
      } catch (error) {
        reject(Object.assign(new Error(`invalid JSON body: ${error.message}`), { statusCode: 400, code: 'invalid_json' }));
      }
    });

    req.on('error', (error) => {
      reject(Object.assign(new Error(error.message || String(error)), { statusCode: 400, code: 'request_stream_error' }));
    });
  });
}

function normalizeActionTimeoutMs(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return ACTION_TIMEOUT_MS_DEFAULT;
  return Math.max(1000, Math.min(ACTION_TIMEOUT_MS_MAX, Math.floor(num)));
}

function truncateOutput(value, maxBytes = ACTION_OUTPUT_MAX_BYTES) {
  const text = ensureString(value);
  const buffer = Buffer.from(text, 'utf8');
  if (buffer.length <= maxBytes) return text;
  const truncated = buffer.subarray(0, maxBytes).toString('utf8');
  return `${truncated}\n...[truncated ${buffer.length - maxBytes} bytes]`;
}

function validateBranch(branch, required = false) {
  if (branch === undefined || branch === null || branch === '') {
    if (required) throw Object.assign(new Error('branch is required'), { statusCode: 400, code: 'invalid_branch' });
    return '';
  }
  const value = String(branch).trim();
  if (!value) {
    if (required) throw Object.assign(new Error('branch is required'), { statusCode: 400, code: 'invalid_branch' });
    return '';
  }
  if (value.length > 200) throw Object.assign(new Error('branch is too long'), { statusCode: 400, code: 'invalid_branch' });
  if (value.startsWith('-') || value.includes('..') || /[\0-\x1f\x7f\s]/.test(value)) {
    throw Object.assign(new Error('branch contains invalid characters'), { statusCode: 400, code: 'invalid_branch' });
  }
  if (!/^[A-Za-z0-9._/-]+$/.test(value)) {
    throw Object.assign(new Error('branch contains unsupported characters'), { statusCode: 400, code: 'invalid_branch' });
  }
  return value;
}

function validateReviewers(reviewers) {
  if (reviewers === undefined || reviewers === null) return [];
  if (!Array.isArray(reviewers)) {
    throw Object.assign(new Error('reviewers must be an array'), { statusCode: 400, code: 'invalid_reviewers' });
  }
  const normalized = [];
  const seen = new Set();
  for (const item of reviewers) {
    const reviewer = String(item || '').trim().toLowerCase();
    if (!reviewer) continue;
    if (!ALLOWED_REVIEWERS.has(reviewer)) {
      throw Object.assign(new Error(`unsupported reviewer: ${reviewer}`), { statusCode: 400, code: 'invalid_reviewer' });
    }
    if (seen.has(reviewer)) continue;
    seen.add(reviewer);
    normalized.push(reviewer);
  }
  return normalized;
}

function ensureTeamDevActionsReady() {
  const resolvedSkillDir = path.resolve(TEAM_DEV_SKILL_DIR);
  if (!fs.existsSync(resolvedSkillDir) || !fs.statSync(resolvedSkillDir).isDirectory()) {
    throw Object.assign(new Error(`TEAM_DEV_SKILL_DIR not found: ${resolvedSkillDir}`), {
      statusCode: 500,
      code: 'team_dev_dir_missing'
    });
  }
  const scriptsDir = path.join(resolvedSkillDir, 'scripts');
  if (!fs.existsSync(scriptsDir) || !fs.statSync(scriptsDir).isDirectory()) {
    throw Object.assign(new Error(`scripts directory not found: ${scriptsDir}`), {
      statusCode: 500,
      code: 'team_dev_scripts_missing'
    });
  }
  return { skillDir: resolvedSkillDir, scriptsDir };
}

function resolveAllowedActionScript(action) {
  const fileName = ACTION_SCRIPT_ALLOWLIST[action];
  if (!fileName) {
    throw Object.assign(new Error(`action not allowed: ${action}`), { statusCode: 404, code: 'action_not_found' });
  }
  const { skillDir, scriptsDir } = ensureTeamDevActionsReady();
  const scriptPath = path.resolve(scriptsDir, fileName);
  if (!scriptPath.startsWith(`${scriptsDir}${path.sep}`)) {
    throw Object.assign(new Error('script path escape rejected'), { statusCode: 500, code: 'script_path_invalid' });
  }
  if (!fs.existsSync(scriptPath) || !fs.statSync(scriptPath).isFile()) {
    throw Object.assign(new Error(`script not found: ${scriptPath}`), { statusCode: 500, code: 'script_missing' });
  }
  return { skillDir, scriptsDir, scriptPath, fileName };
}

function inferRepoFromBranch(branch) {
  if (!branch) return { repo: null, reason: 'missing_branch' };
  const state = loadBoardState();
  const matches = state.tasks.filter((task) => task.branch === branch);
  const repoCandidates = [];
  for (const task of matches) {
    const repo = firstNonEmptyString(task.repo, task.raw && task.raw.repo, task.checks && task.checks.ghRepo);
    if (repo && !repoCandidates.includes(repo)) repoCandidates.push(repo);
  }
  if (repoCandidates.length === 1) return { repo: repoCandidates[0], reason: 'active_task_match' };
  if (repoCandidates.length > 1) return { repo: null, reason: 'ambiguous_repo', candidates: repoCandidates };
  return { repo: null, reason: 'repo_not_found' };
}

function buildActionHints(action, payload, execResult) {
  if (action === 'ai-review') {
    return [
      'review-agent 需要可用的 gh 登录态与 reviewer CLI（codex/claude/gemini/cursor）',
      '若 reviewer 数量不足 3，team-dev 脚本会拒绝执行（除非脚本参数允许调试模式）'
    ];
  }
  if (action === 'fixup') {
    return [
      payload && payload.dryRun ? 'dryRun=true 时仅生成/预览 fixup 指令，不会发送到 tmux 或拉起 subagent' : '确保 review 聚合结果已生成，否则 fixup 可能提示无可处理项'
    ];
  }
  if (action === 'cleanup') {
    return [
      'cleanup 当前主要按 team-dev 注册表与仓库状态清理，body.branch 仅用于校验与前端上下文展示'
    ];
  }
  if (action === 'check-agents' && execResult && execResult.exitCode !== 0) {
    return ['检查 gh / git / python3 环境以及 team-dev active-tasks.json 是否存在'];
  }
  return [];
}

function execLocalAction(action, scriptPath, args, options = {}) {
  const timeoutMs = normalizeActionTimeoutMs(options.timeoutMs);
  const startedAt = Date.now();
  const commandPreview = [scriptPath, ...args].map((part) => JSON.stringify(String(part))).join(' ');
  let result;
  try {
    result = spawnSync(scriptPath, args, {
      cwd: options.cwd || path.dirname(scriptPath),
      env: { ...process.env, ...(options.env || {}) },
      encoding: 'utf8',
      timeout: timeoutMs,
      maxBuffer: Math.max(64 * 1024, ACTION_OUTPUT_MAX_BYTES * 4)
    });
  } catch (error) {
    const finishedAt = Date.now();
    return {
      ok: false,
      action,
      exitCode: null,
      command: commandPreview,
      cmd: commandPreview,
      stdout: '',
      stderr: '',
      startedAt,
      finishedAt,
      durationMs: finishedAt - startedAt,
      error: 'spawn_failed',
      message: error.message || String(error)
    };
  }

  const finishedAt = Date.now();
  const timedOut = Boolean(result.error && result.error.code === 'ETIMEDOUT');
  const stdout = truncateOutput(result.stdout);
  const stderr = truncateOutput(result.stderr);
  const exitCode = typeof result.status === 'number' ? result.status : null;
  const ok = !timedOut && exitCode === 0;
  const payload = {
    ok,
    action,
    exitCode,
    command: commandPreview,
    cmd: commandPreview,
    stdout,
    stderr,
    startedAt,
    finishedAt,
    durationMs: finishedAt - startedAt
  };

  if (timedOut) {
    payload.error = 'timeout';
    payload.message = `action timed out after ${timeoutMs}ms`;
  } else if (result.error) {
    payload.error = result.error.code || 'exec_error';
    payload.message = result.error.message || String(result.error);
  } else if (!ok) {
    payload.error = 'command_failed';
    payload.message = `command exited with code ${exitCode}`;
  }

  return payload;
}

function actionHealthPayload() {
  const scriptsReady = (() => {
    try {
      ensureTeamDevActionsReady();
      return true;
    } catch {
      return false;
    }
  })();
  return {
    ok: true,
    enabled: LOCAL_ACTIONS_ENABLED && scriptsReady,
    teamDevSkillDir: TEAM_DEV_SKILL_DIR,
    actions: Object.keys(ACTION_SCRIPT_ALLOWLIST)
  };
}

async function runActionRoute(req, urlObj, res) {
  const action = urlObj.pathname.replace('/api/actions/', '');
  if (action === 'health') {
    if (req.method !== 'GET') return json(res, 405, { error: 'method_not_allowed', message: 'Use GET' });
    return json(res, 200, actionHealthPayload());
  }

  if (req.method !== 'POST') {
    return json(res, 405, { error: 'method_not_allowed', message: 'Use POST', action });
  }

  if (!LOCAL_ACTIONS_ENABLED) {
    return json(res, 501, {
      ok: false,
      action,
      error: 'local_actions_disabled',
      message: '当前实例未启用本地操作 API（设置 ENABLE_LOCAL_ACTIONS=1）'
    });
  }

  let body = {};
  try {
    body = await readJsonBody(req);
  } catch (error) {
    return json(res, error.statusCode || 400, {
      ok: false,
      action,
      error: error.code || 'invalid_body',
      message: error.message || String(error)
    });
  }

  try {
    const { skillDir, scriptPath } = resolveAllowedActionScript(action);
    const timeoutMs = normalizeActionTimeoutMs(body.timeoutMs);
    const args = [];
    const meta = {};

    if (action === 'check-agents') {
      // No extra args. team-dev script uses its own registry/config.
    } else if (action === 'cleanup') {
      meta.branch = validateBranch(body.branch, true);
    } else if (action === 'ai-review') {
      const branch = validateBranch(body.branch, true);
      const reviewers = validateReviewers(body.reviewers);
      const inferred = inferRepoFromBranch(branch);
      if (!inferred.repo) {
        const detail = inferred.candidates && inferred.candidates.length ? ` candidates=${inferred.candidates.join(',')}` : '';
        throw Object.assign(new Error(`cannot infer repo from branch: ${branch} (${inferred.reason})${detail}`), {
          statusCode: 400,
          code: 'repo_inference_failed'
        });
      }
      args.push('--repo', inferred.repo, '--branch', branch, '--no-post');
      if (reviewers.length > 0) args.push('--reviewers', reviewers.join(','));
      meta.branch = branch;
      meta.reviewers = reviewers;
      meta.repo = inferred.repo;
      meta.repoSource = inferred.reason;
    } else if (action === 'fixup') {
      const branch = validateBranch(body.branch, true);
      const dryRun = Boolean(body.dryRun);
      args.push('--branch', branch);
      if (dryRun) args.push('--dry-run');
      meta.branch = branch;
      meta.dryRun = dryRun;
    } else {
      throw Object.assign(new Error(`unsupported action: ${action}`), { statusCode: 404, code: 'action_not_found' });
    }

    const execResult = execLocalAction(action, scriptPath, args, { cwd: skillDir, timeoutMs });
    const status = execResult.ok ? 200 : (execResult.error === 'timeout' ? 504 : 200);
    return json(res, status, {
      ...execResult,
      ...meta,
      actionHints: buildActionHints(action, meta, execResult)
    });
  } catch (error) {
    return json(res, error.statusCode || 500, {
      ok: false,
      action,
      exitCode: null,
      command: null,
      cmd: null,
      stdout: '',
      stderr: '',
      error: error.code || 'action_error',
      message: error.message || String(error)
    });
  }
}

async function handleApi(req, urlObj, res) {
  const state = loadBoardState();

  if (urlObj.pathname === '/api/health') {
    return json(res, 200, {
      ok: true,
      service: 'dev-board-api',
      port: PORT,
      generatedAt: state.meta.generatedAt,
      teamDevSkillDir: state.meta.teamDevSkillDir,
      registryError: state.meta.registryError
    });
  }

  if (urlObj.pathname === '/api/summary') {
    const counts = computeCounts(state.tasks);
    return json(res, 200, {
      meta: state.meta,
      mainAgent: state.mainAgent,
      counts: {
        total: counts.total,
        running: counts.running,
        queued: counts.queued,
        live: counts.live,
        active: counts.active,
        done: counts.done,
        waitingReview: counts.waitingReview,
        approved: counts.approved,
        merged: counts.merged,
        completed: counts.completed,
        cleaned: counts.cleaned,
        failed: counts.failed,
        cancelled: counts.cancelled,
        terminal: counts.terminal,
        actionNeeded: counts.actionNeeded,
        recentCompleted: counts.recentCompleted
      },
      labels: {
        status: STATUS_LABELS,
        statusCategory: STATUS_CATEGORY_LABELS,
        recentCompletedWindowMs: RECENT_COMPLETED_WINDOW_MS
      },
      notifications: state.notifications.slice(0, 10)
    });
  }

  if (urlObj.pathname === '/api/tasks') {
    return json(res, 200, { items: state.tasks });
  }

  if (urlObj.pathname === '/api/queue') {
    const queue = loadQueueState({ activeTasks: state.tasks });
    return json(res, 200, {
      items: queue.items,
      counts: queue.counts,
      updatedAt: queue.updatedAt,
      updatedAtIso: queue.updatedAtIso,
      sourcePath: queue.sourcePath,
      sourceMeta: queue.sourceMeta,
      queueStats: queue.queueStats,
      registryError: queue.registryError
    });
  }

  if (urlObj.pathname === '/api/board') {
    const board = buildBoardView(state.tasks);
    const queue = loadQueueState({ activeTasks: state.tasks });
    board.queueSummary = summarizeQueueState(queue);
    return json(res, 200, {
      meta: state.meta,
      mainAgent: state.mainAgent,
      board,
      queueSummary: summarizeQueueState(queue)
    });
  }

  if (urlObj.pathname === '/api/history') {
    const limit = urlObj.searchParams.get('limit');
    const file = urlObj.searchParams.get('file');
    const history = loadArchives({ limit, file });
    return json(res, 200, history);
  }

  if (urlObj.pathname.startsWith('/api/tasks/') && urlObj.pathname.endsWith('/log')) {
    const parts = urlObj.pathname.split('/');
    const taskId = decodeURIComponent(parts[3] || '');
    const task = state.tasks.find((t) => t.id === taskId || t.branch === taskId || t.tmuxSession === taskId);
    if (!task) return json(res, 404, { error: 'task not found', taskId });
    const lines = Math.max(20, Math.min(1000, Number(urlObj.searchParams.get('lines') || 200)));
    const tail = tailFileWithMeta(task.logFile, lines);
    return json(res, 200, {
      taskId: task.id,
      lines,
      logFile: task.logFile,
      logMeta: tail.meta,
      error: tail.error,
      content: tail.content
    });
  }

  if (urlObj.pathname === '/api/logs/orchestrator') {
    const type = urlObj.searchParams.get('type') === 'cleanup' ? 'cleanup' : 'cron';
    const file = type === 'cleanup' ? state.meta.cleanupLog : state.meta.cronLog;
    const lines = Math.max(20, Math.min(1000, Number(urlObj.searchParams.get('lines') || 200)));
    const tail = tailFileWithMeta(file, lines);
    return json(res, 200, {
      type,
      lines,
      file,
      logMeta: tail.meta,
      error: tail.error,
      content: tail.content
    });
  }

  if (urlObj.pathname.startsWith('/api/actions/')) {
    return runActionRoute(req, urlObj, res);
  }

  return json(res, 404, { error: 'not found' });
}

const server = http.createServer((req, res) => {
  const urlObj = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (urlObj.pathname.startsWith('/api/')) {
    return Promise.resolve(handleApi(req, urlObj, res)).catch((error) => {
      console.error('[dev-board] api error', error);
      if (!res.headersSent) {
        return json(res, 500, {
          ok: false,
          error: 'internal_error',
          message: error && error.message ? error.message : String(error)
        });
      }
      try {
        res.end();
      } catch {
        // ignore secondary errors while closing the response
      }
    });
  }
  return serveStatic(urlObj.pathname, res);
});

server.listen(PORT, () => {
  console.log(`[dev-board] listening on http://localhost:${PORT}`);
  console.log(`[dev-board] team-dev skill dir: ${TEAM_DEV_SKILL_DIR}`);
});
