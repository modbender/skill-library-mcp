// ============================================================================
// commands/issue.js — Create / list issues on an asset
// ============================================================================

'use strict';

const api = require('../api.js');
const auth = require('../auth.js');
const { ok, info, err, c, detail } = require('../ui.js');

/**
 * Format a timestamp to a readable date string
 */
function fmtDate(ts) {
  if (!ts) return '?';
  const d = new Date(ts);
  if (isNaN(d.getTime())) return String(ts);
  return d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
}

/**
 * Render issue status with color
 */
function renderStatus(status) {
  switch (status) {
    case 'open':   return c('green', '● open');
    case 'closed': return c('red', '● closed');
    default:       return c('dim', status || 'open');
  }
}

/**
 * openclawmp issue <assetRef> <title> [--body "..."] [--labels "bug,help"] [--as-agent]
 */
async function runIssue(args, flags) {
  if (args.length < 2) {
    err('Usage: openclawmp issue <assetRef> <title> [--body "..."] [--labels "bug,help"] [--as-agent]');
    console.log('  Example: openclawmp issue trigger/@xiaoyue/pdf-watcher "安装后无法启动" --body "详细描述..."');
    process.exit(1);
  }

  if (!auth.isAuthenticated()) {
    err('Authentication required. Run: openclawmp login');
    process.exit(1);
  }

  const asset = await api.resolveAssetRef(args[0]);
  const title = args.slice(1).join(' ');
  const displayName = asset.displayName || asset.name || args[0];

  const body = {
    title,
    authorType: flags['as-agent'] ? 'agent' : 'user',
  };

  if (flags.body) {
    body.bodyText = flags.body;
  }

  if (flags.labels) {
    body.labels = flags.labels.split(',').map(l => l.trim()).filter(Boolean);
  }

  const { status, data } = await api.post(`/api/assets/${asset.id}/issues`, body);

  if (status >= 200 && status < 300) {
    const issue = data.issue || data;
    const issueNum = issue.number || issue.id || '?';

    console.log('');
    ok(`Issue #${issueNum} 已创建于 ${c('bold', displayName)}`);
    detail('标题', title);
    if (flags.body) {
      detail('描述', flags.body.length > 60 ? flags.body.slice(0, 60) + '...' : flags.body);
    }
    if (flags.labels) {
      detail('标签', flags.labels);
    }
    console.log('');
  } else {
    err(`创建 Issue 失败 (${status}): ${data.error || data.message || JSON.stringify(data)}`);
    process.exit(1);
  }
}

/**
 * openclawmp issues <assetRef>
 */
async function runIssues(args) {
  if (args.length === 0) {
    err('Usage: openclawmp issues <assetRef>');
    console.log('  Example: openclawmp issues trigger/@xiaoyue/pdf-watcher');
    process.exit(1);
  }

  const asset = await api.resolveAssetRef(args[0]);
  const displayName = asset.displayName || asset.name || args[0];

  const result = await api.get(`/api/assets/${asset.id}/issues`);
  const issues = result?.data?.issues || result?.issues || [];

  console.log('');
  info(`${c('bold', displayName)} 的 Issues（${issues.length} 个）`);
  console.log(`  ${'─'.repeat(50)}`);

  if (issues.length === 0) {
    console.log(`  ${c('dim', '暂无 Issues。')}`);
  } else {
    for (const iss of issues) {
      const num = iss.number || iss.id || '?';
      const status = renderStatus(iss.status);
      const author = iss.author?.name || iss.authorName || iss.authorType || 'anonymous';
      const badge = iss.authorType === 'agent' ? c('magenta', ' 🤖') : '';
      const time = fmtDate(iss.createdAt || iss.created_at);
      const labels = (iss.labels || []).map(l => c('yellow', `[${l}]`)).join(' ');

      console.log('');
      console.log(`  ${status}  ${c('bold', `#${num}`)} ${iss.title} ${labels}`);
      console.log(`  ${c('dim', `by ${author}${badge} · ${time}`)}`);
    }
  }
  console.log('');
}

module.exports = { runIssue, runIssues };
