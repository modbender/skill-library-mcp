function normalizeStatus(status) {
  if (!status) return 'unknown';
  return String(status).toLowerCase();
}

function progressForTask(task) {
  const status = normalizeStatus(task.status);
  const checks = task.checks || {};

  if (status === 'merged' || status === 'cleaned') return { pct: 100, stage: 'completed' };
  if (status === 'approved') return { pct: 90, stage: 'approved' };
  if (status === 'waiting_review' || status === 'done') {
    return { pct: checks.codeReviewDone ? 90 : 80, stage: checks.codeReviewDone ? 'reviewed' : 'awaiting_review' };
  }
  if (status === 'changes_requested') return { pct: 70, stage: 'changes_requested' };
  if (status === 'failed') return { pct: 100, stage: 'failed' };
  if (status === 'cancelled') return { pct: 100, stage: 'cancelled' };
  if (status === 'queued') return { pct: 10, stage: 'queued' };
  if (status === 'running') {
    const retryCount = Number(task.retryCount || 0);
    const base = checks.prCreated ? 75 : 40;
    const pct = Math.max(20, Math.min(79, base + retryCount * 5));
    return { pct, stage: checks.prCreated ? 'pr_created' : 'running' };
  }

  return { pct: 0, stage: status };
}

module.exports = {
  normalizeStatus,
  progressForTask
};
