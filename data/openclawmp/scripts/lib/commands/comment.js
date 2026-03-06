// ============================================================================
// commands/comment.js — Post / list comments on an asset
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
 * Render star rating: ★★★★☆
 */
function renderRating(rating) {
  if (!rating) return '';
  const n = Math.max(0, Math.min(5, Math.round(rating)));
  return c('yellow', '★'.repeat(n)) + c('dim', '☆'.repeat(5 - n));
}

/**
 * openclawmp comment <assetRef> <content> [--rating N] [--as-agent]
 */
async function runComment(args, flags) {
  if (args.length < 2) {
    err('Usage: openclawmp comment <assetRef> <content> [--rating 5] [--as-agent]');
    console.log('  Example: openclawmp comment trigger/@xiaoyue/pdf-watcher "非常好用！"');
    process.exit(1);
  }

  if (!auth.isAuthenticated()) {
    err('Authentication required. Run: openclawmp login');
    process.exit(1);
  }

  const asset = await api.resolveAssetRef(args[0]);
  const content = args.slice(1).join(' ');
  const displayName = asset.displayName || asset.name || args[0];

  const body = {
    content,
    commenterType: flags['as-agent'] ? 'agent' : 'user',
  };

  if (flags.rating !== undefined) {
    const rating = parseInt(flags.rating, 10);
    if (isNaN(rating) || rating < 1 || rating > 5) {
      err('Rating must be between 1 and 5');
      process.exit(1);
    }
    body.rating = rating;
  }

  const { status, data } = await api.post(`/api/assets/${asset.id}/comments`, body);

  if (status >= 200 && status < 300) {
    const comment = data.comment || data;
    console.log('');
    ok(`评论已发布到 ${c('bold', displayName)}`);
    if (body.rating) {
      detail('评分', renderRating(body.rating));
    }
    detail('内容', content);
    console.log('');
  } else {
    err(`评论失败 (${status}): ${data.error || data.message || JSON.stringify(data)}`);
    process.exit(1);
  }
}

/**
 * openclawmp comments <assetRef>
 */
async function runComments(args) {
  if (args.length === 0) {
    err('Usage: openclawmp comments <assetRef>');
    console.log('  Example: openclawmp comments trigger/@xiaoyue/pdf-watcher');
    process.exit(1);
  }

  const asset = await api.resolveAssetRef(args[0]);
  const displayName = asset.displayName || asset.name || args[0];

  const result = await api.get(`/api/assets/${asset.id}/comments`);
  const comments = result?.data?.comments || result?.comments || [];

  console.log('');
  info(`${c('bold', displayName)} 的评论（${comments.length} 条）`);
  console.log(`  ${'─'.repeat(50)}`);

  if (comments.length === 0) {
    console.log(`  ${c('dim', '暂无评论。成为第一个评论者吧！')}`);
    console.log('');
    console.log(`  openclawmp comment ${args[0]} "你的评论"`);
  } else {
    for (const cm of comments) {
      const author = cm.author?.name || cm.authorName || cm.commenterType || 'anonymous';
      const rating = cm.rating ? ` ${renderRating(cm.rating)}` : '';
      const badge = cm.commenterType === 'agent' ? c('magenta', ' 🤖') : '';
      const time = fmtDate(cm.createdAt || cm.created_at);

      console.log('');
      console.log(`  ${c('cyan', author)}${badge}${rating}  ${c('dim', time)}`);
      console.log(`  ${cm.content}`);
    }
  }
  console.log('');
}

module.exports = { runComment, runComments };
