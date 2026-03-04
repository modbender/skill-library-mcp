/**
 * Formatters for terminal and markdown output.
 */

// ─── Posts ────────────────────────────────────────────

export function formatPost(p: any, index?: number): string {
  const prefix = index != null ? `${index + 1}.` : "📌";
  const flair = p.flair ? ` [${p.flair}]` : "";
  const nsfw = p.isNsfw ? " 🔞" : "";
  const sticky = p.stickied ? " 📌" : "";
  const lines = [
    `${prefix} r/${p.subreddit} | ⬆️ ${fmtNum(p.score)} (${Math.round(p.upvoteRatio * 100)}%) | 💬 ${p.numComments}${flair}${nsfw}${sticky}`,
    `   ${p.title}`,
    `   by u/${p.author} • ${timeAgo(p.created)}`,
    `   ${p.permalink}`,
  ];
  if (p.selftext && p.selftext.length > 0) {
    lines.push(`   ${p.selftext.slice(0, 200).replace(/\n/g, " ")}${p.selftext.length > 200 ? "..." : ""}`);
  }
  return lines.join("\n");
}

export function formatPostCompact(p: any): string {
  return `⬆️ ${fmtNum(p.score).padStart(6)} | 💬 ${String(p.numComments).padStart(4)} | r/${p.subreddit.padEnd(20)} | ${p.title.slice(0, 70)}`;
}

// ─── Comments ─────────────────────────────────────────

export function formatComment(c: any): string {
  const indent = "  ".repeat(c.depth || 0);
  const op = c.isOp ? " [OP]" : "";
  const edited = c.edited ? " ✏️" : "";
  const controversial = c.controversiality ? " ⚡" : "";
  return [
    `${indent}⬆️ ${fmtNum(c.score)} | u/${c.author}${op}${edited}${controversial} • ${timeAgo(c.created)}`,
    `${indent}  ${c.body.slice(0, 300).replace(/\n/g, `\n${indent}  `)}${c.body.length > 300 ? "..." : ""}`,
  ].join("\n");
}

// ─── Thread ───────────────────────────────────────────

export function formatThread(data: any): string {
  const { post, comments } = data;
  const lines = [
    `# ${post.title}`,
    `r/${post.subreddit} | ⬆️ ${fmtNum(post.score)} (${Math.round(post.upvoteRatio * 100)}%) | 💬 ${post.numComments}`,
    `by u/${post.author} • ${timeAgo(post.created)}`,
    `${post.permalink}`,
    "",
  ];

  if (post.selftext) {
    lines.push(post.selftext.slice(0, 3000));
    lines.push("");
  }

  lines.push(`--- Top Comments (${comments.length}) ---`);
  lines.push("");

  for (const c of comments) {
    lines.push(formatComment(c));
    lines.push("");
  }

  return lines.join("\n");
}

// ─── User ─────────────────────────────────────────────

export function formatUser(u: any): string {
  return [
    `👤 u/${u.name}`,
    `   Karma: ${fmtNum(u.karma)} (${fmtNum(u.linkKarma)} post + ${fmtNum(u.commentKarma)} comment)`,
    `   Account age: ${timeAgo(u.created)}`,
    `   Verified: ${u.verified ? "✅" : "❌"}`,
    u.suspended ? "   ⚠️ SUSPENDED" : "",
  ]
    .filter(Boolean)
    .join("\n");
}

// ─── Subreddit ────────────────────────────────────────

export function formatSubreddit(s: any): string {
  return [
    `📋 r/${s.name} — ${s.title}`,
    `   ${fmtNum(s.subscribers)} subscribers | ${fmtNum(s.activeUsers)} online`,
    `   Created: ${timeAgo(s.created)}`,
    s.nsfw ? "   🔞 NSFW" : "",
    s.description ? `   ${s.description.slice(0, 200)}` : "",
  ]
    .filter(Boolean)
    .join("\n");
}

// ─── Markdown ─────────────────────────────────────────

export function toMarkdown(posts: any[], title?: string): string {
  const lines: string[] = [];
  if (title) lines.push(`# ${title}`, "");

  for (const p of posts) {
    const flair = p.flair ? ` \`${p.flair}\`` : "";
    lines.push(`### ${p.title}${flair}`);
    lines.push(`r/${p.subreddit} · ⬆️ ${fmtNum(p.score)} · 💬 ${p.numComments} · u/${p.author} · ${timeAgo(p.created)}`);
    lines.push(`[Link](${p.permalink})`);
    if (p.selftext) {
      lines.push("", `> ${p.selftext.slice(0, 300).replace(/\n/g, "\n> ")}`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

// ─── JSON ─────────────────────────────────────────────

export function toJson(data: any): string {
  return JSON.stringify(data, null, 2);
}

// ─── Helpers ──────────────────────────────────────────

function fmtNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function timeAgo(isoOrUnix: string | number): string {
  const ts = typeof isoOrUnix === "string" ? new Date(isoOrUnix).getTime() : isoOrUnix * 1000;
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;
  return `${Math.floor(months / 12)}y ago`;
}
