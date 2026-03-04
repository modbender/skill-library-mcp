const state = {
  summary: null,
  tasks: [],
  history: [],
  queue: null,
  queueError: null,
  selectedTaskId: null,
  pinnedTaskId: null,
  timer: null,
  filters: {
    query: '',
    group: 'all',
    groupMode: 'default',
    quickFocus: 'all',
    agent: 'all',
    repo: 'all',
    status: 'all'
  },
  collapsedGroups: new Set(),
  expandedReviewers: new Set(),
  autoFreezeUntil: 0,
  opsApiAvailable: null,
  opsActionResult: null,
  opsActionLoading: null,
  opsActionResultTaskId: null,
  opsReviewers: ['codex', 'gemini', 'claude'],
  opsFixupDryRun: true,
  opsExpandedStdout: false,
  opsExpandedStderr: false
};

const els = {
  refreshBtn: document.getElementById('refreshBtn'),
  autoRefresh: document.getElementById('autoRefresh'),
  freezeLog: document.getElementById('freezeLog'),
  generatedAt: document.getElementById('generatedAt'),
  kpiGrid: document.getElementById('kpiGrid'),
  attentionList: document.getElementById('attentionList'),
  orchestratorMeta: document.getElementById('orchestratorMeta'),
  taskCount: document.getElementById('taskCount'),
  taskList: document.getElementById('taskList'),
  detailTitle: document.getElementById('detailTitle'),
  detailSubtitle: document.getElementById('detailSubtitle'),
  taskDetail: document.getElementById('taskDetail'),
  logTitle: document.getElementById('logTitle'),
  logContent: document.getElementById('logContent'),
  logMeta: document.getElementById('logMeta'),
  logSource: document.getElementById('logSource'),
  lineCount: document.getElementById('lineCount'),
  searchInput: document.getElementById('searchInput'),
  agentFilter: document.getElementById('agentFilter'),
  repoFilter: document.getElementById('repoFilter'),
  statusFilter: document.getElementById('statusFilter'),
  viewModeChips: document.getElementById('viewModeChips'),
  quickFocusChips: document.getElementById('quickFocusChips'),
  groupChips: document.getElementById('groupChips'),
  pinTaskBtn: document.getElementById('pinTaskBtn'),
  opsPanel: document.getElementById('opsPanel'),
  queueView: document.getElementById('queueView')
};

const STATUS_LABELS = {
  running: '进行中',
  working: '进行中',
  queued: '排队中',
  pending: '待开始',
  failed: '失败',
  error: '失败',
  stopped_unexpectedly: '异常停止',
  cancelled: '已取消',
  timeout: '超时',
  done: '已完成',
  completed: '已完成',
  merged: '已合并',
  approved: '已批准',
  waiting_review: '待验收',
  cleaned: '已清理',
  idle: '空闲',
  unknown: '未知'
};

const QUEUE_STATE_LABELS = {
  queued: '排队中',
  claimed: '已领取',
  dispatched: '执行中'
};

function friendlyValue(value, fallback = '—') {
  if (value === null || value === undefined) return fallback;
  const s = String(value).trim();
  return s || fallback;
}

const DEFAULT_GROUPS = [
  { key: 'attention', label: '需关注', hint: '失败/CI 阻塞/评审需人工处理' },
  { key: 'running', label: '进行中', hint: '运行/排队/待开始' },
  { key: 'recent', label: '近期完成', hint: '48 小时内完成/合并/验收' },
  { key: 'history', label: '已清理/历史', hint: '清理或较早完成' }
];

const REVIEW_OPS_GROUPS = [
  { key: 'waiting_checks', label: '等待检查', hint: 'PR 已创建，等待 CI/required checks' },
  { key: 'checks_failed', label: '检查失败', hint: 'CI 失败或 required checks 未通过' },
  { key: 'waiting_review', label: '等待评审', hint: 'AI/人工评审尚未完成' },
  { key: 'review_changes_requested', label: '需返工', hint: 'AI/人工评审要求修改' },
  { key: 'review_human_attention', label: '人工关注', hint: '冲突/异常/需人工判断' },
  { key: 'waiting_human_approve', label: '待人工批准', hint: 'AI 建议通过，等待人工 approve' },
  { key: 'merge_ready', label: '可合并', hint: '检查通过且评审完成，可进入合并' }
];

const GROUP_MODE_LABELS = {
  default: '概览分组',
  review_ops: '审核运营'
};

function escapeHtml(input) {
  return String(input ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function fmtTs(ts) {
  if (!ts) return '-';
  try { return new Date(ts).toLocaleString(); } catch { return String(ts); }
}

function fmtRelative(ts) {
  if (!ts) return '-';
  const delta = Date.now() - Number(ts);
  if (!Number.isFinite(delta)) return '-';
  const sec = Math.floor(delta / 1000);
  if (sec < 30) return '刚刚';
  if (sec < 60) return `${sec} 秒前`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min} 分钟前`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} 小时前`;
  const day = Math.floor(hr / 24);
  return `${day} 天前`;
}

function fmtDuration(ms) {
  if (!ms || ms < 0) return '-';
  const sec = Math.floor(ms / 1000);
  if (sec < 60) return `${sec}s`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ${sec % 60}s`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ${min % 60}m`;
  const day = Math.floor(hr / 24);
  return `${day}d ${hr % 24}h`;
}

function humanStatus(status) {
  return STATUS_LABELS[String(status || 'unknown')] || status || '未知';
}

function pickFirst(...values) {
  for (const value of values) {
    if (value !== null && value !== undefined && value !== '') return value;
  }
  return null;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function asObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}

function toBool(value) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    if (!normalized) return false;
    return ['1', 'true', 'yes', 'y', 'on'].includes(normalized);
  }
  return false;
}

function normalizeCiStatus(rawTask) {
  const raw = asObject(pickFirst(rawTask.ciStatus, rawTask.ci_status, rawTask.raw?.ciStatus, rawTask.raw?.ci_status));
  const checks = asObject(rawTask.checks);
  const bucket = String(
    pickFirst(
      raw.requiredChecksBucket,
      raw.required_checks_bucket,
      raw.bucket,
      checks.requiredChecksBucket,
      checks.required_checks_bucket
    ) || ''
  ).toLowerCase();

  const summary = pickFirst(
    raw.summary,
    raw.statusSummary,
    raw.requiredChecksSummary,
    rawTask.raw?.requiredChecksSummary
  );

  const counts = asObject(pickFirst(raw.counts, raw.checkCounts, rawTask.raw?.checkCounts));

  let derivedBucket = bucket;
  if (!derivedBucket) {
    if (checks.error || checks.failed || raw.failed) derivedBucket = 'failed';
    else if (checks.running || raw.running) derivedBucket = 'pending';
    else if (checks.ok || raw.passed) derivedBucket = 'passed';
    else if (rawTask.prNumber || rawTask.raw?.prNumber || rawTask.raw?.prUrl) derivedBucket = 'unknown';
    else derivedBucket = 'missing';
  }

  return {
    ...raw,
    requiredChecksBucket: derivedBucket,
    summary: summary || '',
    counts
  };
}

function normalizeReviewAggregate(rawTask) {
  const raw = asObject(pickFirst(rawTask.reviewAggregate, rawTask.review_aggregate, rawTask.raw?.reviewAggregate, rawTask.raw?.review_aggregate));
  const verdict = String(pickFirst(raw.verdict, raw.result, raw.status) || '').toLowerCase();
  const recommendedAction = pickFirst(raw.recommendedAction, raw.recommended_action, raw.nextAction);
  const label = pickFirst(raw.label, raw.verdictLabel);

  return {
    ...raw,
    verdict,
    verdictLabel: label || '',
    recommendedAction: recommendedAction || ''
  };
}

function normalizeReviewSummary(rawTask) {
  const rawList = asArray(pickFirst(rawTask.reviewSummary, rawTask.review_summary, rawTask.raw?.reviewSummary, rawTask.raw?.review_summary));
  return rawList
    .map((item, index) => {
      const raw = asObject(item);
      const reviewer = String(pickFirst(raw.reviewer, raw.name, raw.engine, raw.provider, raw.model) || `reviewer-${index + 1}`);
      const verdict = String(pickFirst(raw.verdict, raw.result, raw.status) || '').toLowerCase();
      const commented = toBool(pickFirst(raw.commented, raw.hasCommented, raw.commentPosted));
      return {
        reviewer,
        verdict,
        verdictLabel: pickFirst(raw.verdictLabel, raw.resultLabel, raw.statusLabel) || '',
        commented,
        summary: pickFirst(raw.summary, raw.message, raw.note) || '',
        raw
      };
    })
    .filter((item) => item.reviewer);
}

function ciBucketLabel(bucket) {
  const map = {
    passed: 'CI 通过',
    success: 'CI 通过',
    green: 'CI 通过',
    pending: 'CI 进行中',
    running: 'CI 进行中',
    waiting: 'CI 待触发',
    failed: 'CI 失败',
    error: 'CI 失败',
    blocked: 'CI 阻塞',
    missing: 'CI 暂无数据',
    unknown: 'CI 待接入'
  };
  return map[String(bucket || '').toLowerCase()] || 'CI 未知';
}

function reviewVerdictLabel(verdict) {
  const map = {
    approve: '建议通过',
    approved: '建议通过',
    pass: '建议通过',
    changes_requested: '需修改',
    request_changes: '需修改',
    reject: '不通过',
    comment: '有评论',
    pending: '待评审',
    conflict: '评审冲突',
    mixed: '评审分歧',
    human_attention: '人工关注',
    unknown: '待接入'
  };
  return map[String(verdict || '').toLowerCase()] || '暂无结论';
}

function reviewerVerdictLabel(verdict) {
  const map = {
    approve: '通过',
    approved: '通过',
    pass: '通过',
    changes_requested: '修改',
    request_changes: '修改',
    reject: '拒绝',
    comment: '评论',
    pending: '待评',
    conflict: '冲突'
  };
  return map[String(verdict || '').toLowerCase()] || '未知';
}

function normalizeAttentionLevel(rawTask) {
  const rawLevel = String(pickFirst(rawTask.attentionLevel, rawTask.raw?.attentionLevel) || '').toLowerCase();
  const rawLabel = pickFirst(rawTask.attentionLevelLabel, rawTask.raw?.attentionLevelLabel);
  if (rawLevel) return { level: rawLevel, label: rawLabel || rawLevel };
  return { level: '', label: rawLabel || '' };
}

function normalizePipelineStage(rawTask, status) {
  const stage = String(pickFirst(rawTask.pipelineStage, rawTask.raw?.pipelineStage, rawTask.progress?.stage) || '').toLowerCase();
  const label = pickFirst(rawTask.pipelineStageLabel, rawTask.raw?.pipelineStageLabel, rawTask.progress?.summary, rawTask.progress?.stage) || '';
  if (stage || label) return { stage, label: label || stage };
  return { stage: '', label: humanStatus(status) };
}

function deriveReviewOpsSignals(taskLike) {
  const ciBucket = String(taskLike.ciStatus?.requiredChecksBucket || '').toLowerCase();
  const reviewVerdict = String(taskLike.reviewAggregate?.verdict || '').toLowerCase();
  const hasReviewData = Boolean(taskLike.reviewAggregate?.verdict || taskLike.reviewSummary?.length);
  const hasPr = Boolean(taskLike.prNumber || taskLike.prUrl);
  const status = String(taskLike.effectiveStatus || taskLike.status || '').toLowerCase();
  const pipelineStage = String(taskLike.pipelineStage || '').toLowerCase();
  const fixupSuggested = Boolean(taskLike.fixupSuggested);
  const fixupText = String(taskLike.fixupRecommendation || '').toLowerCase();

  let group = 'waiting_review';
  if (!hasPr) group = isAttentionTask(taskLike) ? 'review_human_attention' : 'waiting_review';
  else if (['failed', 'error', 'blocked'].includes(ciBucket)) group = 'checks_failed';
  else if (reviewVerdict === 'conflict' || reviewVerdict === 'mixed' || reviewVerdict === 'human_attention') group = 'review_human_attention';
  else if (reviewVerdict === 'changes_requested' || reviewVerdict === 'request_changes' || fixupSuggested || fixupText) group = 'review_changes_requested';
  else if (['passed', 'success', 'green'].includes(ciBucket) && ['approve', 'approved', 'pass'].includes(reviewVerdict)) group = 'waiting_human_approve';
  else if (status === 'merged' || pipelineStage === 'merge_ready' || taskLike.raw?.mergeReady === true) group = 'merge_ready';
  else if (['pending', 'running', 'waiting', 'unknown', 'missing'].includes(ciBucket) && hasPr) group = 'waiting_checks';
  else if (!hasReviewData && hasPr) group = 'waiting_review';
  else if (['approve', 'approved', 'pass'].includes(reviewVerdict) && ['passed', 'success', 'green'].includes(ciBucket)) group = 'waiting_human_approve';
  else if (hasPr && !hasReviewData) group = 'waiting_review';

  if (status === 'merged' || status === 'done' || taskLike.raw?.mergeReady === true) {
    if (group !== 'checks_failed' && group !== 'review_human_attention' && group !== 'review_changes_requested') {
      group = 'merge_ready';
    }
  }

  const waitingHumanApprove = group === 'waiting_human_approve';
  const needsRework = group === 'review_changes_requested';
  const needsHumanAttention = ['checks_failed', 'review_human_attention', 'waiting_human_approve', 'review_changes_requested'].includes(group);

  return { group, waitingHumanApprove, needsRework, needsHumanAttention };
}

function reviewOpsGroupLabel(key) {
  const found = REVIEW_OPS_GROUPS.find((item) => item.key === key);
  return found?.label || key || '未知';
}

function normalizeTask(raw) {
  const status = raw.effectiveStatus || raw.status || raw.state || 'unknown';
  const progress = raw.progress || {};
  const startedAt = raw.startedAt || raw.createdAt || null;
  const completedAt = raw.completedAt || raw.failedAt || raw.cancelledAt || null;
  const logMtime = raw.logMtime || raw.updatedAt || null;
  const pipelineInfo = normalizePipelineStage(raw, status);
  const attentionInfo = normalizeAttentionLevel(raw);
  const prNumber = pickFirst(raw.prNumber, raw.pr_number, raw.pullRequestNumber, raw.pr?.number);
  const prUrl = pickFirst(raw.prUrl, raw.pr_url, raw.pullRequestUrl, raw.pr?.url, raw.pr?.htmlUrl);
  const reviewSummary = normalizeReviewSummary(raw);
  const reviewAggregate = normalizeReviewAggregate(raw);
  const baseTask = {
    id: raw.id || raw.branch || raw.tmuxSession || raw.session || `task-${Math.random().toString(16).slice(2)}`,
    agent: raw.agent || raw.owner || 'unknown',
    description: raw.description || raw.title || '',
    repo: raw.repo || raw.repository || '',
    repoPath: raw.repoPath || raw.repo_path || '',
    worktree: raw.worktree || '',
    branch: raw.branch || raw.gitBranch || '',
    tmuxSession: raw.tmuxSession || raw.session || '',
    status,
    effectiveStatus: raw.effectiveStatus || status,
    live: Boolean(raw.live),
    retryCount: Number(raw.retryCount || 0),
    checks: raw.checks || {},
    startedAt,
    completedAt,
    logFile: raw.logFile || raw.log_path || '',
    logMtime,
    notifyOnComplete: Boolean(raw.notifyOnComplete),
    progress,
    pipelineStage: pipelineInfo.stage,
    pipelineStageLabel: pipelineInfo.label,
    attentionLevel: attentionInfo.level,
    attentionLevelLabel: attentionInfo.label,
    nextActionHint: pickFirst(raw.nextActionHint, raw.next_action_hint, raw.nextAction, raw.reviewAggregate?.recommendedAction) || '',
    prNumber: prNumber == null ? null : String(prNumber),
    prUrl: prUrl || '',
    ciStatus: { requiredChecksBucket: 'missing', summary: '', counts: {} },
    reviewAggregate,
    reviewSummary,
    fixupSuggested: toBool(pickFirst(raw.fixupSuggested, raw.fixup_suggested)),
    fixupRecommendation: pickFirst(raw.fixupRecommendation, raw.fixup_recommendation) || '',
    fixupTarget: pickFirst(raw.fixupTarget, raw.fixup_target) || '',
    raw
  };

  baseTask.ciStatus = normalizeCiStatus(baseTask);
  const reviewOpsSignals = deriveReviewOpsSignals(baseTask);
  return {
    ...baseTask,
    reviewOpsGroup: reviewOpsSignals.group,
    reviewOpsGroupLabel: reviewOpsGroupLabel(reviewOpsSignals.group),
    needsHumanAttention: reviewOpsSignals.needsHumanAttention,
    waitingHumanApprove: reviewOpsSignals.waitingHumanApprove,
    needsRework: reviewOpsSignals.needsRework
  };
}

function taskUpdatedAt(task) {
  return task.logMtime || task.completedAt || task.startedAt || null;
}

const STALE_TERMINAL_MS = 48 * 60 * 60 * 1000; // 48h

function isStaleTerminalTask(task) {
  const status = String(task.effectiveStatus || task.status || '').toLowerCase();
  if (!['done', 'completed', 'merged', 'approved', 'cleaned', 'cancelled'].includes(status)) return false;
  const completedAt = Number(task.completedAt || task.logMtime || 0);
  if (!Number.isFinite(completedAt)) return false;
  return Date.now() - completedAt > STALE_TERMINAL_MS;
}

function isRealBlockerTask(task) {
  const status = String(task.effectiveStatus || task.status || '').toLowerCase();
  const ciBucket = String(task.ciStatus?.requiredChecksBucket || '').toLowerCase();
  const reviewVerdict = String(task.reviewAggregate?.verdict || '').toLowerCase();

  if (['failed', 'error', 'stopped_unexpectedly', 'timeout'].includes(status)) return true;
  if (ciBucket === 'failed' || ciBucket === 'error' || ciBucket === 'blocked') return true;
  if (['conflict', 'mixed', 'human_attention'].includes(reviewVerdict)) return true;
  if (['changes_requested', 'request_changes'].includes(reviewVerdict)) return true;
  if (Boolean(task.needsHumanAttention)) return true;
  if (Boolean(task.checks?.error)) return true;
  if (task.reviewOpsGroup === 'checks_failed' || task.reviewOpsGroup === 'review_human_attention' || task.reviewOpsGroup === 'review_changes_requested') return true;

  return false;
}

function isAttentionTask(task) {
  if (isStaleTerminalTask(task)) return false;
  return isRealBlockerTask(task);
}

function isRunningTask(task) {
  const status = String(task.status || '').toLowerCase();
  return ['running', 'working', 'queued', 'pending'].includes(status) || task.live;
}

function isCompletedTask(task) {
  const status = String(task.status || '').toLowerCase();
  return ['done', 'completed', 'merged', 'approved', 'waiting_review', 'cleaned'].includes(status);
}

function isRecentTask(task) {
  if (!task.completedAt) return false;
  const delta = Date.now() - Number(task.completedAt);
  return delta >= 0 && delta < 48 * 60 * 60 * 1000;
}

function groupTaskDefault(task) {
  if (isAttentionTask(task)) return 'attention';
  if (isRunningTask(task)) return 'running';
  if (isCompletedTask(task) && isRecentTask(task)) return 'recent';
  return 'history';
}

function groupTaskReviewOps(task) {
  return task.reviewOpsGroup || 'waiting_review';
}

function groupTask(task, mode = state.filters.groupMode) {
  return mode === 'review_ops' ? groupTaskReviewOps(task) : groupTaskDefault(task);
}

function getActiveGroups() {
  return state.filters.groupMode === 'review_ops' ? REVIEW_OPS_GROUPS : DEFAULT_GROUPS;
}

async function fetchJsonMaybe(url) {
  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return { ok: false, status: res.status };
    const data = await res.json();
    return { ok: true, data };
  } catch (error) {
    return { ok: false, error };
  }
}

function normalizeBoardPayload(payload) {
  const summary = payload.summary || payload.meta || {};
  const mainAgent = payload.mainAgent || summary.mainAgent || payload.orchestrator || {};
  const board = asObject(payload.board);
  const counts = payload.counts || summary.counts || board.counts || {};
  const notifications = payload.notifications || summary.notifications || [];
  const rawTasks = pickFirst(
    payload.tasks,
    payload.items,
    payload.active,
    board.active && [].concat(board.active || [], board.recentCompleted || [], board.failed || [])
  ) || [];
  const rawHistory = pickFirst(
    payload.history,
    payload.cleaned,
    payload.archived,
    board.history && [].concat(board.history || []),
    [].concat(board.cleaned || [], board.cancelled || [], board.olderCompleted || [], board.unknown || [])
  ) || [];

  const tasks = Array.isArray(rawTasks) ? rawTasks.map(normalizeTask) : [];
  const history = Array.isArray(rawHistory) ? rawHistory.map(normalizeTask) : [];

  return {
    meta: summary.meta || payload.meta || {},
    mainAgent,
    counts,
    notifications,
    queueSummary: payload.queueSummary || board.queueSummary || null,
    tasks,
    history
  };
}

function deriveCounts(tasks) {
  return {
    total: tasks.length,
    running: tasks.filter(isRunningTask).length,
    attention: tasks.filter(isAttentionTask).length,
    done: tasks.filter((t) => isCompletedTask(t) && !isAttentionTask(t)).length
  };
}

function queueStageForItem(item) {
  const status = String(item?.effectiveStatus || item?.status || '').toLowerCase();
  if (['queued', 'pending', 'waiting'].includes(status)) return 'queued';
  if (item?.dispatchedAt || item?.tmuxSession || item?.worktree || item?.linkedActive) return 'dispatched';
  if (item?.claimedAt || item?.agents?.selected || item?.agents?.requested || item?.agents?.claimedByAgent) return 'claimed';
  if (['running', 'working'].includes(status)) return 'dispatched';
  return 'queued';
}

function deriveQueueFromTasks(tasks) {
  const items = tasks
    .filter((task) => {
      const status = String(task.effectiveStatus || task.status || '').toLowerCase();
      return ['queued', 'pending', 'running', 'working'].includes(status);
    })
    .map((task) => ({
      id: task.id,
      title: task.description || task.id,
      description: task.description || '',
      branch: task.branch || '',
      priority: task.raw?.priority || null,
      phase: task.raw?.phase || task.pipelineStage || '',
      agent: task.agent || '',
      status: task.effectiveStatus || task.status,
      linkedActive: {
        id: task.id,
        branch: task.branch || '',
        agent: task.agent || '',
        status: task.status || '',
        effectiveStatus: task.effectiveStatus || task.status || '',
        lastEventAt: task.lastEventAt || task.logMtime || task.completedAt || task.startedAt || null
      },
      createdAt: task.startedAt || null,
      updatedAt: task.lastEventAt || task.logMtime || task.completedAt || task.startedAt || null,
      claimedAt: task.live ? null : (task.startedAt || null),
      dispatchedAt: task.live ? (task.startedAt || null) : null,
      _derived: true
    }));

  return buildQueueStateFromItems(items, {
    degraded: true,
    sourcePath: null,
    updatedAt: Date.now(),
    counts: null,
    registryError: 'queue_api_unavailable'
  });
}

function normalizeQueueItem(item) {
  const raw = item?.raw || item;
  const linkedActive = asObject(item?.linkedActive || raw?.linkedActive);
  const linkedActiveId = pickFirst(linkedActive.id, raw?.activeTaskId, raw?.linkedActiveId);
  const linkedBranch = pickFirst(linkedActive.branch, raw?.branch);
  const phaseRaw = pickFirst(
    item?.phaseLabel,
    raw?.phaseLabel,
    item?.phase,
    raw?.phase,
    item?.pipelineStageLabel,
    raw?.pipelineStageLabel,
    item?.progress?.stage,
    raw?.progress?.stage
  );
  const titleRaw = pickFirst(item?.title, raw?.title, item?.description, raw?.description);
  const descriptionRaw = pickFirst(item?.description, raw?.description, item?.title, raw?.title, item?.agent, raw?.agent);
  const lastEventAt = pickFirst(
    item?.updatedAt,
    raw?.updatedAt,
    linkedActive.lastEventAt,
    raw?.lastEventAt,
    item?.dispatchedAt,
    raw?.dispatchedAt,
    item?.claimedAt,
    raw?.claimedAt,
    item?.createdAt,
    raw?.createdAt,
    item?.logMtime,
    raw?.logMtime,
    item?.completedAt,
    raw?.completedAt,
    item?.startedAt,
    raw?.startedAt
  );

  return {
    id: item?.id || raw?.id || item?.branch || raw?.branch || '',
    title: titleRaw || '',
    description: descriptionRaw || '',
    branch: pickFirst(item?.branch, raw?.branch) || '',
    priority: pickFirst(item?.priority, raw?.priority, item?.raw?.priority) ?? null,
    phaseLabel: phaseRaw || '',
    agent: pickFirst(item?.agent, raw?.agent, linkedActive.agent, raw?.linkedAgent) || '',
    status: pickFirst(item?.status, raw?.status, item?.effectiveStatus, raw?.effectiveStatus) || '',
    lastEventAt: lastEventAt ?? null,
    linkedActiveId: linkedActiveId || '',
    linkedBranch: linkedBranch || '',
    selectableTaskId: linkedActiveId || (linkedBranch || '')
  };
}

function buildQueueStateFromItems(items, meta = {}) {
  const buckets = { queued: [], claimed: [], dispatched: [], other: [] };
  const list = asArray(items);
  for (const item of list) {
    const stage = queueStageForItem(item);
    if (stage === 'queued') buckets.queued.push(item);
    else if (stage === 'claimed') buckets.claimed.push(item);
    else if (stage === 'dispatched') buckets.dispatched.push(item);
    else buckets.other.push(item);
  }

  const sortByLastEvent = (a, b) => {
    const aTs = Number(normalizeQueueItem(a).lastEventAt || 0);
    const bTs = Number(normalizeQueueItem(b).lastEventAt || 0);
    return bTs - aTs;
  };
  Object.values(buckets).forEach((arr) => arr.sort(sortByLastEvent));

  return {
    ...buckets,
    counts: meta.counts || {
      total: list.length,
      queued: buckets.queued.length,
      claimed: buckets.claimed.length,
      dispatched: buckets.dispatched.length
    },
    updatedAt: meta.updatedAt || null,
    sourcePath: meta.sourcePath || null,
    registryError: meta.registryError || null,
    degraded: Boolean(meta.degraded)
  };
}

function normalizeQueuePayload(payload) {
  if (payload && payload.queue) {
    return {
      queued: asArray(payload.queue.queued),
      claimed: asArray(payload.queue.claimed),
      dispatched: asArray(payload.queue.dispatched),
      other: [],
      counts: {
        total: asArray(payload.queue.queued).length + asArray(payload.queue.claimed).length + asArray(payload.queue.dispatched).length,
        queued: asArray(payload.queue.queued).length,
        claimed: asArray(payload.queue.claimed).length,
        dispatched: asArray(payload.queue.dispatched).length
      },
      updatedAt: payload.meta?.generatedAt || Date.now(),
      sourcePath: null,
      registryError: null,
      degraded: false
    };
  }

  if (payload && Array.isArray(payload.items)) {
    return buildQueueStateFromItems(payload.items, {
      counts: payload.counts || null,
      updatedAt: payload.updatedAt || payload.updatedAtIso || payload.sourceMeta?.mtimeMs || Date.now(),
      sourcePath: payload.sourcePath || null,
      registryError: payload.registryError || null,
      degraded: false
    });
  }

  return null;
}

function renderQueueView() {
  const el = els.queueView;
  if (!el) return;

  const queue = state.queue;
  if (!queue) {
    if (state.queueError) {
      el.innerHTML = `<div class="queue-error muted">队列接口暂时不可用，请稍后重试。</div>`;
    } else {
      el.innerHTML = '<div class="queue-loading muted">加载中…</div>';
    }
    return;
  }

  const metaLineParts = [];
  if (queue.sourcePath) metaLineParts.push(`源: ${queue.sourcePath}`);
  if (queue.updatedAt) metaLineParts.push(`更新: ${fmtTs(queue.updatedAt)}`);
  const metaLine = metaLineParts.length
    ? `<div class="queue-meta-line muted">${escapeHtml(metaLineParts.join(' · '))}</div>`
    : '';

  const renderColumn = (key, items, label) => {
    const itemsHtml = items.length
      ? items.map((task) => {
          const n = normalizeQueueItem(task);
          const title = friendlyValue(n.title, friendlyValue(n.description, '未命名任务'));
          const branch = friendlyValue(n.branch, '—');
          const priority = friendlyValue(n.priority, '—');
          const phase = friendlyValue(n.phaseLabel, '—');
          const agent = friendlyValue(n.agent, '未知');
          const updatedAt = fmtRelative(n.lastEventAt);
          const canSelect = Boolean(n.selectableTaskId);
          return `
            <div class="queue-item${canSelect ? '' : ' is-passive'}"
              ${canSelect ? `data-task-id="${escapeHtml(n.selectableTaskId)}"` : ''}
              ${n.linkedBranch ? `data-queue-branch="${escapeHtml(n.linkedBranch)}"` : (n.branch ? `data-queue-branch="${escapeHtml(n.branch)}"` : '')}>
              <div class="queue-item-title">${escapeHtml(title)}</div>
              <div class="queue-item-meta">
                <span>分支: ${escapeHtml(branch)}</span>
                <span>优先级: ${escapeHtml(priority)}</span>
                <span>阶段: ${escapeHtml(phase)}</span>
                <span>agent: ${escapeHtml(agent)}</span>
                <span>更新: ${escapeHtml(updatedAt)}</span>
              </div>
            </div>
          `;
        }).join('')
      : `<div class="empty">暂无</div>`;

    return `
      <div class="queue-column" data-queue-state="${key}">
        <div class="queue-column-header">
          <strong>${escapeHtml(QUEUE_STATE_LABELS[key] || label)}</strong>
          <span class="queue-count">${items.length}</span>
        </div>
        <div class="queue-column-body">${itemsHtml}</div>
      </div>
    `;
  };

  const degradedHint = state.queueError
    ? '<div class="queue-degraded muted">队列接口暂不可用，当前为从任务列表推断的队列</div>'
    : '';

  const html = `
    ${degradedHint}
    ${metaLine}
    <div class="queue-columns">
      ${renderColumn('queued', queue.queued || [], '排队中')}
      <div class="queue-columns-group">
        ${renderColumn('claimed', queue.claimed || [], '已领取')}
        ${renderColumn('dispatched', queue.dispatched || [], '执行中')}
      </div>
    </div>
  `;
  el.innerHTML = html;
}

function renderOverview() {
  if (!state.summary) return;
  const { meta, mainAgent, counts } = state.summary;
  const derived = deriveCounts(state.tasks);
  const live = Number(mainAgent.liveCount || counts.live || 0);
  const total = Number(counts.total || derived.total || 0);
  const queueCounts = state.queue?.counts || state.summary.queueSummary?.counts || {};
  const queueInFlight = Number(
    (queueCounts.queued || 0)
    + (queueCounts.claimed || 0)
    + (queueCounts.dispatched || 0)
  );

  els.generatedAt.textContent = `更新: ${fmtTs(meta.generatedAt || Date.now())}`;

  const cards = [
    { label: '运行中', value: counts.running ?? derived.running, tone: 'running' },
    { label: '需关注', value: counts.attention ?? derived.attention, tone: 'attention' },
    { label: '近期完成', value: counts.done ?? derived.done, tone: 'done' },
    { label: '队列中', value: queueInFlight, tone: 'warn' },
    { label: '存活会话', value: live, tone: 'info' },
    { label: '总任务', value: total, tone: 'muted' },
    { label: '通知', value: mainAgent.notificationsPending ?? 0, tone: 'warn' }
  ];

  els.kpiGrid.innerHTML = cards.map((card) => `
    <div class="kpi-card tone-${card.tone}">
      <div class="kpi-label">${escapeHtml(card.label)}</div>
      <div class="kpi-value">${escapeHtml(friendlyValue(card.value, '—'))}</div>
    </div>
  `).join('');

  const attentionTasks = state.tasks
    .filter(isAttentionTask)
    .sort((a, b) => {
      const priority = (t) => {
        const s = String(t.effectiveStatus || t.status || '').toLowerCase();
        const ci = String(t.ciStatus?.requiredChecksBucket || '').toLowerCase();
        const rv = String(t.reviewAggregate?.verdict || '').toLowerCase();
        const grp = String(t.reviewOpsGroup || '').toLowerCase();
        if (['failed', 'error', 'stopped_unexpectedly', 'timeout'].includes(s)) return 0;
        if (ci === 'failed' || ci === 'error' || ci === 'blocked' || grp === 'checks_failed') return 1;
        if (['conflict', 'mixed', 'human_attention'].includes(rv) || grp === 'review_human_attention') return 2;
        if (['changes_requested', 'request_changes'].includes(rv) || grp === 'review_changes_requested') return 3;
        return 4;
      };
      const pa = priority(a);
      const pb = priority(b);
      if (pa !== pb) return pa - pb;
      return Number(taskUpdatedAt(b) || 0) - Number(taskUpdatedAt(a) || 0);
    })
    .slice(0, 4);
  if (!attentionTasks.length) {
    els.attentionList.innerHTML = '<div class="empty">当前无需处理项</div>';
  } else {
    els.attentionList.innerHTML = attentionTasks.map((task) => `
      <div class="attention-item" data-task-id="${escapeHtml(task.id)}">
        <div>
          <div class="attention-title">${escapeHtml(task.description || task.id)}</div>
          <div class="attention-meta">${escapeHtml(task.agent)} · ${escapeHtml(task.repo || '-')}/${escapeHtml(task.branch || '-')}</div>
        </div>
        <span class="pill pill-attention">${escapeHtml(humanStatus(task.effectiveStatus || task.status))}</span>
      </div>
    `).join('');
  }

  els.orchestratorMeta.textContent = JSON.stringify({
    status: mainAgent.status || 'unknown',
    tasksFile: meta.tasksFile,
    teamDevSkillDir: meta.teamDevSkillDir,
    registryError: meta.registryError,
    monitors: mainAgent.monitors
  }, null, 2);
}

function filterTasks(tasks) {
  const query = state.filters.query.trim().toLowerCase();
  return tasks.filter((task) => {
    const group = groupTask(task);
    if (state.filters.group !== 'all' && group !== state.filters.group) return false;
    if (state.filters.quickFocus === 'human_attention' && !task.needsHumanAttention) return false;
    if (state.filters.quickFocus === 'my_approve' && !task.waitingHumanApprove) return false;
    if (state.filters.quickFocus === 'rework' && !task.needsRework) return false;
    if (state.filters.agent !== 'all' && task.agent !== state.filters.agent) return false;
    if (state.filters.repo !== 'all' && task.repo !== state.filters.repo) return false;
    if (state.filters.status !== 'all' && String(task.status) !== state.filters.status) return false;
    if (!query) return true;
    const hay = [
      task.description,
      task.id,
      task.agent,
      task.repo,
      task.branch,
      task.tmuxSession,
      task.prNumber,
      task.pipelineStageLabel,
      task.nextActionHint,
      task.reviewAggregate?.recommendedAction,
      task.fixupRecommendation
    ].join(' ').toLowerCase();
    return hay.includes(query);
  });
}

function renderFilters(tasks) {
  const agents = Array.from(new Set(tasks.map((t) => t.agent).filter(Boolean))).sort();
  const repos = Array.from(new Set(tasks.map((t) => t.repo).filter(Boolean))).sort();
  const statuses = Array.from(new Set(tasks.map((t) => String(t.status)).filter(Boolean))).sort();

  state.filters.agent = agents.includes(state.filters.agent) ? state.filters.agent : 'all';
  state.filters.repo = repos.includes(state.filters.repo) ? state.filters.repo : 'all';
  state.filters.status = statuses.includes(state.filters.status) ? state.filters.status : 'all';

  const buildOptions = (items, label) => {
    return ['<option value="all">全部' + label + '</option>']
      .concat(items.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`))
      .join('');
  };

  els.agentFilter.innerHTML = buildOptions(agents, 'Agent');
  els.repoFilter.innerHTML = buildOptions(repos, 'Repo');
  els.statusFilter.innerHTML = buildOptions(statuses, '状态');

  els.agentFilter.value = state.filters.agent;
  els.repoFilter.value = state.filters.repo;
  els.statusFilter.value = state.filters.status;
  els.searchInput.value = state.filters.query;
}

function renderGroups() {
  const combined = [...state.tasks, ...state.history];
  const filtered = filterTasks(combined);
  const groups = getActiveGroups();
  const groupBuckets = groups.reduce((acc, group) => {
    acc[group.key] = [];
    return acc;
  }, {});

  filtered.forEach((task) => {
    const key = groupTask(task);
    if (!groupBuckets[key]) groupBuckets[key] = [];
    groupBuckets[key].push(task);
  });

  Object.values(groupBuckets).forEach((items) => {
    items.sort((a, b) => {
      const aAttention = Number(Boolean(a.needsHumanAttention));
      const bAttention = Number(Boolean(b.needsHumanAttention));
      if (bAttention !== aAttention) return bAttention - aAttention;
      return Number(taskUpdatedAt(b) || 0) - Number(taskUpdatedAt(a) || 0);
    });
  });

  els.taskCount.textContent = `显示 ${filtered.length} / 总 ${combined.length} 个任务`;

  els.taskList.innerHTML = groups.map((group) => {
    const items = groupBuckets[group.key];
    const collapsed = state.collapsedGroups.has(group.key);
    const body = items.length
      ? items.map(renderTaskCard).join('')
      : `<div class="empty">暂无${group.label}任务</div>`;

    return `
      <section class="group" data-group="${group.key}">
        <button class="group-toggle" data-action="toggle-group" data-group="${group.key}">
          <span>
            <strong>${group.label}</strong>
            <span class="group-hint">${group.hint}</span>
          </span>
          <span class="group-count">${items.length}</span>
        </button>
        <div class="group-body${collapsed ? ' is-collapsed' : ''}">
          ${body}
        </div>
      </section>
    `;
  }).join('');
}

function attentionTone(level) {
  const normalized = String(level || '').toLowerCase();
  if (['high', 'critical', 'urgent'].includes(normalized)) return 'danger';
  if (['medium', 'warning'].includes(normalized)) return 'warn';
  if (['low', 'info'].includes(normalized)) return 'info';
  return 'muted';
}

function reviewerTone(verdict) {
  const normalized = String(verdict || '').toLowerCase();
  if (['approve', 'approved', 'pass'].includes(normalized)) return 'success';
  if (['changes_requested', 'request_changes', 'reject', 'conflict'].includes(normalized)) return 'danger';
  if (['pending'].includes(normalized)) return 'warn';
  return 'muted';
}

function renderReviewSummary(task) {
  if (!Array.isArray(task.reviewSummary) || !task.reviewSummary.length) {
    return '<div class="compat-note">AI reviewer：待接入 / 暂无数据</div>';
  }

  const expanded = state.expandedReviewers.has(task.id);
  const items = expanded ? task.reviewSummary : task.reviewSummary.slice(0, 2);
  const rows = items.map((item) => `
    <div class="reviewer-pill tone-${reviewerTone(item.verdict)}">
      <span>${escapeHtml(item.reviewer)}</span>
      <span>${escapeHtml(item.verdictLabel || reviewerVerdictLabel(item.verdict))}</span>
      <span>${item.commented ? '已评论' : '未评论'}</span>
    </div>
  `).join('');
  const more = task.reviewSummary.length > 2 ? `
    <button class="mini-link" data-action="toggle-reviewers" data-task-id="${escapeHtml(task.id)}">
      ${expanded ? '收起 reviewer 结果' : `展开 reviewer 结果 (${task.reviewSummary.length})`}
    </button>
  ` : '';
  return `<div class="reviewer-list">${rows}</div>${more}`;
}

function renderTaskCard(task) {
  const selected = task.id === state.selectedTaskId ? ' selected' : '';
  const status = humanStatus(task.effectiveStatus || task.status);
  const stage = task.pipelineStageLabel || task.progress?.summary || task.progress?.stage || '';
  const pct = task.progress?.pct ?? 0;
  const updatedAt = taskUpdatedAt(task);
  const ciLabel = ciBucketLabel(task.ciStatus?.requiredChecksBucket);
  const reviewVerdict = task.reviewAggregate?.verdict;
  const reviewLabel = task.reviewAggregate?.verdictLabel || reviewVerdictLabel(reviewVerdict);
  const reviewAction = task.reviewAggregate?.recommendedAction || task.nextActionHint || '';
  const prLabel = task.prNumber ? `#${task.prNumber}` : '未创建 PR';
  const duration = task.completedAt
    ? fmtDuration(task.completedAt - (task.startedAt || task.completedAt))
    : fmtDuration(Date.now() - (task.startedAt || Date.now()));

  return `
    <article class="task-card${selected}" data-task-id="${escapeHtml(task.id)}">
      <div class="task-card-head">
        <div>
          <div class="task-title">${escapeHtml(task.description || task.id)}</div>
          <div class="task-sub">${escapeHtml(task.agent)} · ${escapeHtml(task.repo || '-')}/${escapeHtml(task.branch || '-')}</div>
        </div>
        <span class="pill pill-${escapeHtml(String(task.effectiveStatus || task.status).toLowerCase())}">${escapeHtml(status)}</span>
      </div>
      <div class="task-ops-badges">
        <span class="pill pill-${escapeHtml(String(task.reviewOpsGroup || '').toLowerCase())}">${escapeHtml(task.reviewOpsGroupLabel || '审核运营')}</span>
        <span class="pill tone-${escapeHtml(attentionTone(task.attentionLevel))}">${escapeHtml(task.attentionLevelLabel || '关注度待接入')}</span>
        <span class="pill">${escapeHtml(prLabel)}</span>
      </div>
      <div class="task-metrics">
        <div>阶段: ${escapeHtml(stage || '未标记')}</div>
        <div>耗时: ${escapeHtml(duration || '—')}</div>
        <div>更新: ${escapeHtml(fmtRelative(updatedAt) || '—')}</div>
        <div>重试: ${escapeHtml(friendlyValue(task.retryCount, '0'))}</div>
        <div>CI: ${escapeHtml(ciLabel || '—')}</div>
        <div>Review: ${escapeHtml(reviewLabel || '—')}</div>
      </div>
      <div class="ops-summary-grid">
        <div class="ops-line"><span>CI 摘要</span><strong>${escapeHtml(task.ciStatus?.summary || '待接入 / 暂无数据')}</strong></div>
        <div class="ops-line"><span>下一步</span><strong>${escapeHtml(task.nextActionHint || reviewAction || '待接入 / 暂无提示')}</strong></div>
        <div class="ops-line"><span>Fixup</span><strong>${escapeHtml(task.fixupRecommendation || (task.fixupSuggested ? '建议执行 fixup' : '无'))}</strong></div>
      </div>
      ${renderReviewSummary(task)}
      <div class="progress-wrap">
        <div class="progress-bar"><span style="width:${pct}%"></span></div>
        <div class="progress-row"><span>${escapeHtml(stage || status)}</span><span>${escapeHtml(pct)}%</span></div>
      </div>
      <div class="task-actions">
        <button data-action="copy-branch" data-value="${escapeHtml(task.branch || '')}">复制分支</button>
        <button data-action="copy-pr" data-value="${escapeHtml(task.prUrl || '')}" ${task.prUrl ? '' : 'disabled'}>复制 PR 链接</button>
        <button data-action="copy-log" data-value="${escapeHtml(task.logFile || '')}">复制日志路径</button>
        <button data-action="select-task" data-task-id="${escapeHtml(task.id)}">查看详情</button>
      </div>
    </article>
  `;
}

const OPS_ACTIONS = [
  { key: 'check-agents', label: '刷新监控', risk: false, needsBranch: false, needsPr: false },
  { key: 'cleanup', label: '清理 worktree', risk: true, needsBranch: true, needsPr: false },
  { key: 'ai-review', label: '发起 AI review', risk: false, needsBranch: false, needsPr: true },
  { key: 'fixup', label: '请求 fixup', risk: false, needsBranch: false, needsPr: true }
];

async function probeOpsApi() {
  try {
    const res = await fetch('/api/actions/health', { method: 'GET', cache: 'no-store' });
    state.opsApiAvailable = res.ok && res.status === 200;
  } catch {
    state.opsApiAvailable = false;
  }
}

function renderOpsPanel(task) {
  if (!els.opsPanel) return;
  const available = state.opsApiAvailable === true;
  const loading = state.opsActionLoading;
  const result = state.opsActionResult;
  const resultForTask = result && state.opsActionResultTaskId === task?.id;
  const hasBranch = Boolean(task?.branch);
  const hasPr = Boolean(task?.prNumber || task?.prUrl);

  if (!task) {
    els.opsPanel.innerHTML = '<div class="ops-panel-placeholder empty">选择任务后显示操作台。</div>';
    return;
  }

  let apiStatusHtml = '';
  if (state.opsApiAvailable === null) {
    apiStatusHtml = '<span class="ops-api-status muted">检测中…</span>';
  } else if (!available) {
    apiStatusHtml = '<span class="ops-api-status tone-warn">当前实例未启用本地操作 API</span>';
  }

  const actionButtons = OPS_ACTIONS.map((a) => {
    const disabled = !available || loading;
    const needsBranchDisabled = a.needsBranch && !hasBranch;
    const needsPrDisabled = a.needsPr && !hasPr;
    const isDisabled = disabled || needsBranchDisabled || needsPrDisabled;
    let reason = '';
    if (needsBranchDisabled) reason = '任务无分支信息';
    else if (needsPrDisabled) reason = '任务未创建 PR';

    return `
      <button class="ops-btn ops-btn-${a.risk ? 'risk' : 'normal'}"
        data-ops-action="${escapeHtml(a.key)}"
        ${isDisabled ? 'disabled' : ''}
        title="${reason ? escapeHtml(reason) : ''}">
        ${escapeHtml(a.label)}
        ${reason ? ` <span class="ops-disabled-hint">(${escapeHtml(reason)})</span>` : ''}
      </button>
    `;
  }).join('');

  const reviewerOpts = ['codex', 'gemini', 'claude'];
  const reviewersHtml = reviewerOpts.map((r) => `
    <label class="ops-reviewer-chk">
      <input type="checkbox" value="${escapeHtml(r)}" ${state.opsReviewers.includes(r) ? 'checked' : ''} data-ops-reviewer="${escapeHtml(r)}" />
      <span>${escapeHtml(r)}</span>
    </label>
  `).join('');

  let resultHtml = '';
  if (resultForTask && result) {
    const statusCls = result.ok ? 'tone-success' : 'tone-danger';
    const statusText = result.ok ? '成功' : '失败';
    const metaParts = [];
    if (result.durationMs != null) metaParts.push(`耗时 ${result.durationMs}ms`);
    if (result.exitCode != null) metaParts.push(`exit ${result.exitCode}`);
    if (result.command) metaParts.push(`命令: ${escapeHtml(result.command)}`);

    const stdoutContent = (result.stdout || '').trim();
    const stderrContent = (result.stderr || '').trim();
    const hasStdout = stdoutContent.length > 0;
    const hasStderr = stderrContent.length > 0;

    resultHtml = `
      <div class="ops-result">
        <div class="ops-result-status ${statusCls}">${escapeHtml(statusText)}</div>
        <div class="ops-result-meta">${metaParts.join(' · ')}</div>
        ${result.command ? `<pre class="ops-result-cmd">${escapeHtml(result.command)}</pre>` : ''}
        ${hasStdout ? `
          <details class="ops-result-details" ${state.opsExpandedStdout ? 'open' : ''}>
            <summary>stdout (${stdoutContent.split('\n').length} 行)</summary>
            <pre class="ops-result-output">${escapeHtml(stdoutContent)}</pre>
          </details>
        ` : ''}
        ${hasStderr ? `
          <details class="ops-result-details" ${state.opsExpandedStderr ? 'open' : ''}>
            <summary>stderr (${stderrContent.split('\n').length} 行)</summary>
            <pre class="ops-result-output ops-result-stderr">${escapeHtml(stderrContent)}</pre>
          </details>
        ` : ''}
        ${result.error ? `<div class="ops-result-error">${escapeHtml(result.error)}</div>` : ''}
      </div>
    `;
  } else if (loading) {
    resultHtml = '<div class="ops-result ops-result-loading">执行中…</div>';
  }

  els.opsPanel.innerHTML = `
    <div class="ops-panel-inner">
      <h4 class="ops-title">操作台</h4>
      ${apiStatusHtml}
      <div class="ops-actions" role="group" aria-label="可用操作">
        ${actionButtons}
      </div>
      <div class="ops-params">
        <div class="ops-param-row">
          <span class="ops-param-label">Review 评审者</span>
          <div class="ops-reviewers">${reviewersHtml}</div>
        </div>
        <div class="ops-param-row">
          <label class="ops-fixup-dryrun">
            <input type="checkbox" ${state.opsFixupDryRun ? 'checked' : ''} data-ops-fixup-dryrun />
            <span>Fixup dry-run（仅预览，不实际执行）</span>
          </label>
        </div>
      </div>
      <div class="ops-result-wrap" style="min-height: ${result || loading ? '80px' : '0'};">
        ${resultHtml}
      </div>
    </div>
  `;
}

async function runOpsAction(actionKey, task) {
  if (!task || state.opsActionLoading) return;
  state.opsActionLoading = actionKey;
  state.opsActionResult = null;
  state.opsActionResultTaskId = task.id;
  renderDetail();

  const selectedReviewers = Array.from(document.querySelectorAll('[data-ops-reviewer]:checked'))
    .map((el) => el.value).filter(Boolean);
  const dryRun = document.querySelector('[data-ops-fixup-dryrun]')?.checked ?? true;

  const body = {
    taskId: task.id,
    branch: task.branch,
    prNumber: task.prNumber,
    reviewers: selectedReviewers.length ? selectedReviewers : ['codex', 'gemini', 'claude'],
    dryRun: actionKey === 'fixup' ? dryRun : undefined
  };

  const start = Date.now();
  try {
    const res = await fetch(`/api/actions/${actionKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      cache: 'no-store'
    });
    const durationMs = Date.now() - start;
    const data = await res.json().catch(() => ({}));

    if (res.status === 404 || res.status === 501) {
      state.opsActionResult = {
        ok: false,
        error: data.message || '当前实例未启用本地操作 API',
        durationMs
      };
    } else if (!res.ok) {
      state.opsActionResult = {
        ok: false,
        error: data.error || data.message || `HTTP ${res.status}`,
        durationMs,
        stdout: data.stdout,
        stderr: data.stderr
      };
    } else {
      state.opsActionResult = {
        ok: Boolean(data.ok !== false),
        durationMs,
        exitCode: data.exitCode ?? data.exit_code,
        command: data.command || data.cmd,
        stdout: data.stdout || '',
        stderr: data.stderr || '',
        error: data.error || (data.ok === false ? (data.message || '执行失败') : null)
      };
    }
  } catch (err) {
    state.opsActionResult = {
      ok: false,
      error: err.message || String(err),
      durationMs: Date.now() - start
    };
  }

  state.opsActionLoading = null;
  renderDetail();
}

function onOpsPanelClick(event) {
  const btn = event.target.closest('[data-ops-action]');
  if (!btn || btn.disabled) return;

  const actionKey = btn.dataset.opsAction;
  const task = state.tasks.find((t) => t.id === state.selectedTaskId)
    || state.history.find((t) => t.id === state.selectedTaskId);
  if (!task) return;

  const action = OPS_ACTIONS.find((a) => a.key === actionKey);
  const isFixupNonDryRun = actionKey === 'fixup' && !(document.querySelector('[data-ops-fixup-dryrun]')?.checked ?? true);

  if (action?.risk || isFixupNonDryRun) {
    const msg = actionKey === 'cleanup' ? '确认清理该任务 worktree？此操作不可逆。' : '确认执行 fixup（非 dry-run）？将实际修改代码。';
    if (!confirm(msg)) return;
  }
  runOpsAction(actionKey, task);
}

function onOpsPanelChange(event) {
  const target = event.target;
  if (target.matches('[data-ops-reviewer]')) {
    const checked = Array.from(document.querySelectorAll('[data-ops-reviewer]:checked')).map((el) => el.value);
    state.opsReviewers = checked.length ? checked : ['codex', 'gemini', 'claude'];
  }
  if (target.matches('[data-ops-fixup-dryrun]')) {
    state.opsFixupDryRun = target.checked;
  }
}

function renderDetail() {
  const task = state.tasks.find((t) => t.id === state.selectedTaskId)
    || state.history.find((t) => t.id === state.selectedTaskId);

  if (!task) {
    els.detailTitle.textContent = '任务详情';
    els.detailSubtitle.textContent = '请选择任务查看详情';
    els.taskDetail.innerHTML = '<div class="empty">当前没有选中的任务。</div>';
    renderOpsPanel(null);
    return;
  }

  const status = humanStatus(task.effectiveStatus || task.status);
  const updatedAt = taskUpdatedAt(task);
  const ciLabel = ciBucketLabel(task.ciStatus?.requiredChecksBucket);
  const reviewVerdict = task.reviewAggregate?.verdict;
  const reviewLabel = task.reviewAggregate?.verdictLabel || reviewVerdictLabel(reviewVerdict);
  const duration = task.completedAt
    ? fmtDuration(task.completedAt - (task.startedAt || task.completedAt))
    : fmtDuration(Date.now() - (task.startedAt || Date.now()));

  els.detailTitle.textContent = task.description || task.id;
  els.detailSubtitle.textContent = `${status} · ${task.agent} · ${task.repo || '-'} / ${task.branch || '-'}`;
  els.taskDetail.innerHTML = `
    <div class="detail-item">
      <div class="label">状态</div>
      <div class="value">${escapeHtml(status)}</div>
    </div>
    <div class="detail-item">
      <div class="label">阶段</div>
      <div class="value">${escapeHtml(task.pipelineStageLabel || task.progress?.stage || '未标记')}</div>
    </div>
    <div class="detail-item">
      <div class="label">审核运营分组</div>
      <div class="value">${escapeHtml(task.reviewOpsGroupLabel || '待接入')}</div>
    </div>
    <div class="detail-item">
      <div class="label">关注级别</div>
      <div class="value">${escapeHtml(task.attentionLevelLabel || '待接入 / 暂无数据')}</div>
    </div>
    <div class="detail-item">
      <div class="label">最近更新</div>
      <div class="value">${escapeHtml(fmtTs(updatedAt))}</div>
    </div>
    <div class="detail-item">
      <div class="label">耗时</div>
      <div class="value">${escapeHtml(duration)}</div>
    </div>
    <div class="detail-item">
      <div class="label">仓库</div>
      <div class="value">${escapeHtml(task.repo || '-')}</div>
    </div>
    <div class="detail-item">
      <div class="label">分支</div>
      <div class="value">${escapeHtml(task.branch || '-')}</div>
    </div>
    <div class="detail-item">
      <div class="label">PR</div>
      <div class="value">${escapeHtml(task.prNumber ? `#${task.prNumber}` : '未创建 PR')}</div>
      <div class="value-sub">${escapeHtml(task.prUrl || '待接入 / 暂无链接')}</div>
    </div>
    <div class="detail-item">
      <div class="label">CI 状态</div>
      <div class="value">${escapeHtml(ciLabel)}</div>
      <div class="value-sub">${escapeHtml(task.ciStatus?.summary || '待接入 / 暂无数据')}</div>
    </div>
    <div class="detail-item">
      <div class="label">AI Review 聚合</div>
      <div class="value">${escapeHtml(reviewLabel)}</div>
      <div class="value-sub">${escapeHtml(task.reviewAggregate?.recommendedAction || '待接入 / 暂无建议')}</div>
    </div>
    <div class="detail-item">
      <div class="label">下一步提示</div>
      <div class="value">${escapeHtml(task.nextActionHint || '待接入 / 暂无提示')}</div>
    </div>
    <div class="detail-item">
      <div class="label">Fixup 建议</div>
      <div class="value">${escapeHtml(task.fixupSuggested ? '建议执行 fixup' : '无 fixup 建议')}</div>
      <div class="value-sub">${escapeHtml(task.fixupRecommendation || '待接入 / 暂无数据')}</div>
    </div>
    <div class="detail-item">
      <div class="label">Fixup 目标</div>
      <div class="value">${escapeHtml(task.fixupTarget || '待接入 / 暂无数据')}</div>
    </div>
    <div class="detail-item">
      <div class="label">TMUX</div>
      <div class="value">${escapeHtml(task.tmuxSession || '-')}</div>
    </div>
    <div class="detail-item">
      <div class="label">日志路径</div>
      <div class="value">${escapeHtml(task.logFile || '-')}</div>
    </div>
    <div class="detail-item detail-item-wide">
      <div class="label">Reviewer 结果</div>
      ${Array.isArray(task.reviewSummary) && task.reviewSummary.length ? `
        <div class="detail-review-list">${task.reviewSummary.map((item) => `
          <div class="reviewer-row">
            <span class="pill tone-${escapeHtml(reviewerTone(item.verdict))}">${escapeHtml(item.reviewer)}</span>
            <span>${escapeHtml(item.verdictLabel || reviewerVerdictLabel(item.verdict))}</span>
            <span>${item.commented ? '已评论' : '未评论'}</span>
            <span class="muted">${escapeHtml(item.summary || '')}</span>
          </div>
        `).join('')}</div>
      ` : '<div class="compat-note">待接入 / 暂无数据</div>'}
    </div>
  `;

  renderOpsPanel(task);

  const pinned = state.pinnedTaskId === task.id;
  els.pinTaskBtn.textContent = pinned ? '已固定' : '固定任务';
}

function renderViewModeChips() {
  if (!els.viewModeChips) return;
  els.viewModeChips.innerHTML = [
    { key: 'default', label: GROUP_MODE_LABELS.default },
    { key: 'review_ops', label: GROUP_MODE_LABELS.review_ops }
  ].map((item) => `
    <button data-view-mode="${item.key}" class="chip${state.filters.groupMode === item.key ? ' active' : ''}">${escapeHtml(item.label)}</button>
  `).join('');
}

function renderQuickFocusChips() {
  if (!els.quickFocusChips) return;
  const items = [
    { key: 'all', label: '全部任务' },
    { key: 'human_attention', label: '需人工处理' },
    { key: 'my_approve', label: '待我 approve' },
    { key: 'rework', label: '待返工' }
  ];
  els.quickFocusChips.innerHTML = items.map((item) => `
    <button data-quick-focus="${item.key}" class="chip${state.filters.quickFocus === item.key ? ' active' : ''}">${escapeHtml(item.label)}</button>
  `).join('');
}

function updateFilterChips() {
  const groups = getActiveGroups();
  if (state.filters.group !== 'all' && !groups.some((g) => g.key === state.filters.group)) {
    state.filters.group = 'all';
  }
  els.groupChips.innerHTML = [
    `<button data-group="all" class="chip${state.filters.group === 'all' ? ' active' : ''}">全部</button>`,
    ...groups.map((group) => `<button data-group="${escapeHtml(group.key)}" class="chip${state.filters.group === group.key ? ' active' : ''}">${escapeHtml(group.label)}</button>`)
  ].join('');
  renderViewModeChips();
  renderQuickFocusChips();
}

function setSelection(taskId) {
  if (!taskId) return;
  if (state.selectedTaskId !== taskId) {
    state.opsActionResult = null;
    state.opsActionResultTaskId = null;
  }
  state.selectedTaskId = taskId;
  renderGroups();
  renderDetail();
  refreshLog({ force: true }).catch(showError);
}

function ensureSelection() {
  if (state.pinnedTaskId) {
    if (state.selectedTaskId !== state.pinnedTaskId) {
      state.opsActionResult = null;
      state.opsActionResultTaskId = null;
    }
    state.selectedTaskId = state.pinnedTaskId;
    return;
  }
  const combined = filterTasks([...state.tasks, ...state.history]);
  if (!combined.length) {
    state.selectedTaskId = null;
    state.opsActionResult = null;
    state.opsActionResultTaskId = null;
    return;
  }
  if (!state.selectedTaskId || !combined.some((t) => t.id === state.selectedTaskId)) {
    const prevId = state.selectedTaskId;
    state.selectedTaskId = combined[0].id;
    if (prevId !== state.selectedTaskId) {
      state.opsActionResult = null;
      state.opsActionResultTaskId = null;
    }
  }
}

function shouldSkipLogRefresh() {
  const freezeByToggle = els.freezeLog.checked;
  const freezeByInteraction = Date.now() < state.autoFreezeUntil;
  return freezeByToggle || freezeByInteraction;
}

async function refreshLog({ force = false } = {}) {
  if (!force && shouldSkipLogRefresh()) return;
  const lines = Number(els.lineCount.value || 200);
  const source = els.logSource.value;

  els.logContent.classList.remove('log-error', 'log-empty');

  if (source === 'cron' || source === 'cleanup') {
    els.logTitle.textContent = source === 'cron' ? '编排者监控日志' : '编排者清理日志';
    const payload = await fetchJsonMaybe(`/api/logs/orchestrator?type=${encodeURIComponent(source)}&lines=${lines}`);
    if (!payload.ok) throw new Error('无法读取编排者日志');
    els.logMeta.innerHTML = renderLogMeta({
      file: payload.data.file,
      updatedAt: payload.data.mtime,
      source: source === 'cron' ? 'cron' : 'cleanup',
      lines
    });
    els.logContent.textContent = `File: ${payload.data.file || '-'}\n\n${payload.data.content || ''}`;
    return;
  }

  if (!state.selectedTaskId) {
    els.logTitle.textContent = '日志查看器';
    els.logMeta.innerHTML = '';
    els.logContent.textContent = '请选择任务或切换日志来源。';
    els.logContent.classList.add('log-empty');
    return;
  }

  els.logTitle.textContent = `任务日志`;
  const payload = await fetchJsonMaybe(`/api/tasks/${encodeURIComponent(state.selectedTaskId)}/log?lines=${lines}`);
  if (!payload.ok) throw new Error('无法读取任务日志');
  const currentTask = state.tasks.find((t) => t.id === state.selectedTaskId)
    || state.history.find((t) => t.id === state.selectedTaskId);
  els.logMeta.innerHTML = renderLogMeta({
    file: payload.data.logFile,
    updatedAt: payload.data.mtime || taskUpdatedAt(currentTask),
    source: 'task',
    lines
  });
  els.logContent.textContent = `File: ${payload.data.logFile || '-'}\n\n${payload.data.content || ''}`;
}

function renderLogMeta({ file, updatedAt, source, lines }) {
  return `
    <div>
      <div class="meta-label">来源</div>
      <div class="meta-value">${escapeHtml(source || '-')}</div>
    </div>
    <div>
      <div class="meta-label">日志路径</div>
      <div class="meta-value">${escapeHtml(file || '-')}</div>
    </div>
    <div>
      <div class="meta-label">行数</div>
      <div class="meta-value">${escapeHtml(lines)}</div>
    </div>
    <div>
      <div class="meta-label">更新时间</div>
      <div class="meta-value">${escapeHtml(fmtTs(updatedAt))}</div>
    </div>
  `;
}

function showError(error) {
  console.error(error);
  els.logContent.textContent = `加载失败: ${error.message || error}`;
  els.logContent.classList.add('log-error');
}

async function refreshAll({ skipLog } = {}) {
  const boardRes = await fetchJsonMaybe('/api/board');
  let payload;
  if (boardRes.ok) {
    payload = normalizeBoardPayload(boardRes.data);
  } else {
    const [summaryRes, tasksRes, historyRes] = await Promise.all([
      fetchJsonMaybe('/api/summary'),
      fetchJsonMaybe('/api/tasks'),
      fetchJsonMaybe('/api/history')
    ]);

    const summary = summaryRes.ok ? summaryRes.data : { meta: {}, mainAgent: {}, counts: {} };
    const tasks = tasksRes.ok ? (tasksRes.data.items || tasksRes.data.tasks || []) : [];
    const history = historyRes.ok ? (historyRes.data.items || historyRes.data.history || []) : [];

    payload = normalizeBoardPayload({
      summary,
      tasks,
      history
    });
  }

  state.summary = payload;
  state.tasks = payload.tasks || [];
  state.history = payload.history || [];

  const queueRes = await fetchJsonMaybe('/api/queue');
  const normalizedQueue = queueRes.ok ? normalizeQueuePayload(queueRes.data) : null;
  if (normalizedQueue) {
    state.queue = normalizedQueue;
    state.queueError = Boolean(queueRes.data?.registryError);
  } else {
    state.queueError = true;
    state.queue = deriveQueueFromTasks([...state.tasks]);
  }

  if (state.opsApiAvailable === null) {
    await probeOpsApi();
  }

  renderFilters([...state.tasks, ...state.history]);
  updateFilterChips();
  renderQueueView();
  renderOverview();
  ensureSelection();
  renderGroups();
  renderDetail();

  if (!skipLog) {
    await refreshLog();
  }
}

function setupAutoRefresh() {
  if (state.timer) clearInterval(state.timer);
  if (!els.autoRefresh.checked) return;
  state.timer = setInterval(() => {
    const skipLog = shouldSkipLogRefresh();
    refreshAll({ skipLog }).catch(showError);
  }, 3000);
}

function onFilterChange() {
  state.filters.query = els.searchInput.value;
  state.filters.agent = els.agentFilter.value;
  state.filters.repo = els.repoFilter.value;
  state.filters.status = els.statusFilter.value;
  updateFilterChips();
  ensureSelection();
  renderGroups();
  renderDetail();
  refreshLog({ force: true }).catch(showError);
}

function onGroupChipClick(event) {
  const btn = event.target.closest('[data-group]');
  if (!btn) return;
  state.filters.group = btn.dataset.group;
  updateFilterChips();
  ensureSelection();
  renderGroups();
  renderDetail();
  refreshLog({ force: true }).catch(showError);
}

function onViewModeChipClick(event) {
  const btn = event.target.closest('[data-view-mode]');
  if (!btn) return;
  const nextMode = btn.dataset.viewMode;
  if (!['default', 'review_ops'].includes(nextMode)) return;
  state.filters.groupMode = nextMode;
  state.filters.group = 'all';
  ensureSelection();
  updateFilterChips();
  renderGroups();
  renderDetail();
}

function onQuickFocusChipClick(event) {
  const btn = event.target.closest('[data-quick-focus]');
  if (!btn) return;
  state.filters.quickFocus = btn.dataset.quickFocus || 'all';
  ensureSelection();
  updateFilterChips();
  renderGroups();
  renderDetail();
  refreshLog({ force: true }).catch(showError);
}

function onTaskListClick(event) {
  const action = event.target.closest('[data-action]');
  const card = event.target.closest('[data-task-id]');

  if (action) {
    const type = action.dataset.action;
    if (type === 'toggle-group') {
      const key = action.dataset.group;
      if (state.collapsedGroups.has(key)) {
        state.collapsedGroups.delete(key);
      } else {
        state.collapsedGroups.add(key);
      }
      renderGroups();
      return;
    }
    if (type === 'copy-branch' || type === 'copy-log' || type === 'copy-pr') {
      const value = action.dataset.value || '';
      if (!value) return;
      navigator.clipboard?.writeText(value).catch(() => {});
      return;
    }
    if (type === 'toggle-reviewers' && action.dataset.taskId) {
      const taskId = action.dataset.taskId;
      if (state.expandedReviewers.has(taskId)) state.expandedReviewers.delete(taskId);
      else state.expandedReviewers.add(taskId);
      renderGroups();
      return;
    }
    if (type === 'select-task' && action.dataset.taskId) {
      setSelection(action.dataset.taskId);
      return;
    }
  }

  if (card && card.dataset.taskId) {
    setSelection(card.dataset.taskId);
  }
}

function onAttentionClick(event) {
  const item = event.target.closest('[data-task-id]');
  if (!item) return;
  setSelection(item.dataset.taskId);
}

function onQueueViewClick(event) {
  const item = event.target.closest('.queue-item[data-task-id]');
  if (item?.dataset?.taskId) {
    const taskId = item.dataset.taskId;
    const exact = state.tasks.find((t) => t.id === taskId) || state.history.find((t) => t.id === taskId);
    if (exact) {
      setSelection(exact.id);
      return;
    }
  }

  const branch = event.target.closest('.queue-item')?.dataset?.queueBranch;
  if (!branch) return;
  const byBranch = state.tasks.find((t) => t.branch === branch) || state.history.find((t) => t.branch === branch);
  if (byBranch) setSelection(byBranch.id);
}

function onGlobalAction(event) {
  const btn = event.target.closest('[data-action]');
  if (!btn) return;
  const action = btn.dataset.action;
  if (action === 'collapse-all') {
    getActiveGroups().forEach((g) => state.collapsedGroups.add(g.key));
    renderGroups();
  }
  if (action === 'expand-all') {
    state.collapsedGroups.clear();
    renderGroups();
  }
  if (action === 'pin-task') {
    if (state.pinnedTaskId) {
      state.pinnedTaskId = null;
    } else {
      state.pinnedTaskId = state.selectedTaskId;
    }
    renderDetail();
  }
  if (action === 'copy-branch') {
    const task = state.tasks.find((t) => t.id === state.selectedTaskId)
      || state.history.find((t) => t.id === state.selectedTaskId);
    if (task?.branch) navigator.clipboard?.writeText(task.branch).catch(() => {});
  }
  if (action === 'copy-repo') {
    const task = state.tasks.find((t) => t.id === state.selectedTaskId)
      || state.history.find((t) => t.id === state.selectedTaskId);
    if (task?.repo) navigator.clipboard?.writeText(task.repo).catch(() => {});
  }
  if (action === 'copy-pr') {
    const task = state.tasks.find((t) => t.id === state.selectedTaskId)
      || state.history.find((t) => t.id === state.selectedTaskId);
    if (task?.prUrl) navigator.clipboard?.writeText(task.prUrl).catch(() => {});
  }
}

function initEvents() {
  els.refreshBtn.addEventListener('click', () => refreshAll().catch(showError));
  els.autoRefresh.addEventListener('change', setupAutoRefresh);
  els.logSource.addEventListener('change', () => refreshLog({ force: true }).catch(showError));
  els.lineCount.addEventListener('change', () => refreshLog({ force: true }).catch(showError));
  els.freezeLog.addEventListener('change', () => {
    if (!els.freezeLog.checked) refreshLog({ force: true }).catch(showError);
  });
  els.searchInput.addEventListener('input', onFilterChange);
  els.agentFilter.addEventListener('change', onFilterChange);
  els.repoFilter.addEventListener('change', onFilterChange);
  els.statusFilter.addEventListener('change', onFilterChange);
  els.viewModeChips?.addEventListener('click', onViewModeChipClick);
  els.quickFocusChips?.addEventListener('click', onQuickFocusChipClick);
  els.groupChips.addEventListener('click', onGroupChipClick);
  els.taskList.addEventListener('click', onTaskListClick);
  els.attentionList.addEventListener('click', onAttentionClick);
  els.queueView?.addEventListener('click', onQueueViewClick);
  document.body.addEventListener('click', onGlobalAction);

  els.opsPanel?.addEventListener('click', onOpsPanelClick);
  els.opsPanel?.addEventListener('change', onOpsPanelChange);

  els.logContent.addEventListener('scroll', () => {
    state.autoFreezeUntil = Date.now() + 60 * 1000;
  });
}

initEvents();
refreshAll().then(setupAutoRefresh).catch(showError);
