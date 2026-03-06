import type { Tweet, UserInfo, TrendItem } from './api.js';

const C = {
  reset: '\x1b[0m', bold: '\x1b[1m', dim: '\x1b[2m',
  cyan: '\x1b[36m', yellow: '\x1b[33m', green: '\x1b[32m',
  magenta: '\x1b[35m', white: '\x1b[37m', blue: '\x1b[34m',
  red: '\x1b[31m',
};

function fmtNum(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

function relTime(date: string): string {
  const ms = Date.now() - new Date(date).getTime();
  if (ms < 0) return 'just now';
  const mins = Math.floor(ms / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

function tweetUrl(t: Tweet): string {
  return t.url || `https://x.com/${t.author.userName}/status/${t.id}`;
}

export function formatTweet(t: Tweet, i?: number): string {
  const idx = i !== undefined ? `${C.dim}${i + 1}.${C.reset} ` : '';
  const user = `${C.cyan}@${t.author.userName}${C.reset}`;
  const verified = t.author.isBlueVerified ? ` ${C.blue}✓${C.reset}` : '';
  const text = t.text.length > 280 ? t.text.slice(0, 277) + '...' : t.text;
  const metrics = [
    `❤ ${fmtNum(t.likeCount)}`,
    `🔁 ${fmtNum(t.retweetCount)}`,
    `💬 ${fmtNum(t.replyCount)}`,
    `👁 ${fmtNum(t.viewCount)}`,
  ];
  if (t.quoteCount > 0) metrics.push(`📎 ${fmtNum(t.quoteCount)}`);
  if (t.bookmarkCount > 0) metrics.push(`🔖 ${fmtNum(t.bookmarkCount)}`);
  const metricsStr = `${C.yellow}${metrics.join('  ')}${C.reset}`;
  const time = `${C.dim}${relTime(t.createdAt)}${C.reset}`;
  const url = `${C.dim}${tweetUrl(t)}${C.reset}`;
  const lang = t.lang && t.lang !== 'en' ? ` ${C.dim}[${t.lang}]${C.reset}` : '';
  return `${idx}${user}${verified} ${time}${lang}\n${text}\n${metricsStr}\n${url}\n`;
}

export function formatProfile(u: UserInfo): string {
  const automated = u.isAutomated ? ` ${C.dim}[automated]${C.reset}` : '';
  return [
    `${C.bold}${C.cyan}@${u.userName}${C.reset} ${u.name}${u.isBlueVerified ? ' ✓' : ''}${automated}`,
    `${C.dim}${u.description}${C.reset}`,
    `${C.yellow}Followers: ${fmtNum(u.followers)}  Following: ${fmtNum(u.following)}  Tweets: ${fmtNum(u.tweetsCount)}${C.reset}`,
    u.mediaCount ? `${C.dim}Media: ${fmtNum(u.mediaCount)}  Likes: ${fmtNum(u.favouritesCount || 0)}${C.reset}` : '',
    u.location ? `📍 ${u.location}` : '',
    u.url ? `🔗 ${u.url}` : '',
    `${C.dim}Joined: ${u.createdAt}${C.reset}`,
  ].filter(Boolean).join('\n');
}

export function formatUserCompact(u: UserInfo, i?: number): string {
  const idx = i !== undefined ? `${C.dim}${i + 1}.${C.reset} ` : '';
  const verified = u.isBlueVerified ? ` ${C.blue}✓${C.reset}` : '';
  const desc = u.description ? ` — ${u.description.slice(0, 80)}${u.description.length > 80 ? '...' : ''}` : '';
  return `${idx}${C.cyan}@${u.userName}${C.reset}${verified} (${fmtNum(u.followers)} followers)${desc}`;
}

export function formatTrend(t: TrendItem, i: number): string {
  const count = t.tweet_count ? ` ${C.dim}(${fmtNum(t.tweet_count)} tweets)${C.reset}` : '';
  return `${C.dim}${i + 1}.${C.reset} ${C.bold}${t.name}${C.reset}${count}`;
}

export function formatCost(cost: number): string {
  return `\n${C.dim}💰 Estimated cost: $${cost.toFixed(4)}${C.reset}`;
}

// Markdown formatters
export function tweetToMarkdown(t: Tweet, i?: number): string {
  const idx = i !== undefined ? `### ${i + 1}. ` : '### ';
  const metrics = [`❤ ${fmtNum(t.likeCount)}`, `🔁 ${fmtNum(t.retweetCount)}`, `💬 ${fmtNum(t.replyCount)}`, `👁 ${fmtNum(t.viewCount)}`];
  if (t.quoteCount > 0) metrics.push(`📎 ${fmtNum(t.quoteCount)}`);
  return [
    `${idx}@${t.author.userName} — ${relTime(t.createdAt)}`,
    '',
    t.text,
    '',
    metrics.join(' | '),
    '',
    `[View tweet](${tweetUrl(t)})`,
    '',
    '---',
  ].join('\n');
}

export function profileToMarkdown(u: UserInfo): string {
  return [
    `# @${u.userName} — ${u.name}`,
    '',
    u.description,
    '',
    `| Followers | Following | Tweets | Media |`,
    `|-----------|-----------|--------|-------|`,
    `| ${fmtNum(u.followers)} | ${fmtNum(u.following)} | ${fmtNum(u.tweetsCount)} | ${fmtNum(u.mediaCount || 0)} |`,
  ].join('\n');
}

export function userToMarkdown(u: UserInfo, i?: number): string {
  const idx = i !== undefined ? `${i + 1}. ` : '- ';
  return `${idx}**@${u.userName}** (${fmtNum(u.followers)} followers) — ${(u.description || '').slice(0, 100)}`;
}
