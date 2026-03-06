#!/usr/bin/env node
/**
 * daily-ops.js — GitHub Daily Health Check + Dependabot Auto-Merge
 *
 * Usage:
 *   node daily-ops.js --org Zero2Ai-hub --report
 *   node daily-ops.js --org Zero2Ai-hub --merge-dependabot
 *   node daily-ops.js --repos "repo1,repo2" --report --merge-dependabot
 *
 * Env vars:
 *   GITHUB_TOKEN  — GitHub PAT (or reads from ~/.github_token)
 *   GITHUB_ORG    — default org if --org not passed
 */

const https = require('https');
const fs = require('fs');
const os = require('os');
const path = require('path');

// ── Config ───────────────────────────────────────────────────────────────────
function getToken() {
  if (process.env.GITHUB_TOKEN) return process.env.GITHUB_TOKEN;
  const tokenFile = path.join(os.homedir(), '.github_token');
  if (fs.existsSync(tokenFile)) return fs.readFileSync(tokenFile, 'utf8').trim();
  throw new Error('No GitHub token. Set GITHUB_TOKEN env or create ~/.github_token');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { repos: null, mergeDependabot: false, report: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--org') opts.org = args[++i];
    else if (args[i] === '--repos') opts.repos = args[++i].split(',').map(r => r.trim());
    else if (args[i] === '--merge-dependabot') opts.mergeDependabot = true;
    else if (args[i] === '--report') opts.report = true;
  }
  opts.org = opts.org || process.env.GITHUB_ORG;
  return opts;
}

// ── GitHub API ────────────────────────────────────────────────────────────────
function ghRequest(token, path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      path,
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'jarvis-daily-ops/1.0',
        'Content-Type': 'application/json',
      },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: data ? JSON.parse(data) : {} });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function listRepos(token, org) {
  const all = [];
  let page = 1;
  while (true) {
    const { body } = await ghRequest(token, `/orgs/${org}/repos?per_page=100&page=${page}`);
    if (!Array.isArray(body) || body.length === 0) break;
    all.push(...body.map(r => r.name));
    page++;
  }
  return all;
}

async function getRepoInfo(token, org, repo) {
  const [prs, issues, commits, alerts] = await Promise.all([
    ghRequest(token, `/repos/${org}/${repo}/pulls?state=open&per_page=100`),
    ghRequest(token, `/repos/${org}/${repo}/issues?state=open&per_page=100&filter=all`),
    ghRequest(token, `/repos/${org}/${repo}/commits?per_page=1`),
    ghRequest(token, `/repos/${org}/${repo}/vulnerability-alerts`).catch(() => ({ status: 404 })),
  ]);

  const openPRs = Array.isArray(prs.body) ? prs.body : [];
  const openIssues = Array.isArray(issues.body)
    ? issues.body.filter(i => !i.pull_request)
    : [];
  const lastCommit = Array.isArray(commits.body) && commits.body[0]
    ? commits.body[0].commit?.committer?.date || 'unknown'
    : 'unknown';

  const dependabotPRs = openPRs.filter(pr =>
    pr.user?.login === 'dependabot[bot]' || pr.user?.login === 'dependabot'
  );

  return { openPRs, openIssues, lastCommit, dependabotPRs };
}

async function getPRChecks(token, org, repo, pr) {
  const ref = pr.head?.sha;
  if (!ref) return { passing: false };
  const { body } = await ghRequest(token, `/repos/${org}/${repo}/commits/${ref}/check-runs`);
  const runs = body?.check_runs || [];
  if (runs.length === 0) return { passing: true }; // No CI = assume ok
  const passing = runs.every(r => r.conclusion === 'success' || r.conclusion === 'skipped' || r.status === 'in_progress');
  return { passing };
}

function getSeverityFromTitle(title) {
  const low = /low/i.test(title);
  const medium = /moderate|medium/i.test(title);
  const high = /high|critical/i.test(title);
  if (high) return 'HIGH';
  if (medium) return 'MEDIUM';
  if (low) return 'LOW';
  return 'UNKNOWN';
}

async function mergePR(token, org, repo, pr) {
  const { status } = await ghRequest(token,
    `/repos/${org}/${repo}/pulls/${pr.number}/merge`,
    'PUT',
    { merge_method: 'squash', commit_title: `chore: ${pr.title} (auto-merge)` }
  );
  return status === 200;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();
  const token = getToken();

  if (!opts.org && !opts.repos) {
    console.error('❌ Provide --org or --repos');
    process.exit(1);
  }

  let repos = opts.repos;
  if (!repos) {
    console.log(`📋 Fetching repos for org: ${opts.org} ...`);
    repos = await listRepos(token, opts.org);
    console.log(`   Found ${repos.length} repos\n`);
  }

  const org = opts.org || 'unknown';
  const results = [];
  let totalMerged = 0, totalSkipped = 0;

  for (const repo of repos) {
    process.stdout.write(`🔍 ${repo} ... `);
    try {
      const info = await getRepoInfo(token, org, repo);
      process.stdout.write(`✅\n`);
      results.push({ repo, ...info });

      if (opts.mergeDependabot && info.dependabotPRs.length > 0) {
        for (const pr of info.dependabotPRs) {
          const severity = getSeverityFromTitle(pr.title);
          if (severity === 'HIGH') {
            console.log(`  ⛔ Skip HIGH CVE PR #${pr.number}: ${pr.title} (human review required)`);
            totalSkipped++;
            continue;
          }
          const { passing } = await getPRChecks(token, org, repo, pr);
          if (!passing) {
            console.log(`  ⏳ Skip PR #${pr.number}: CI not passing yet`);
            totalSkipped++;
            continue;
          }
          console.log(`  🔀 Merging PR #${pr.number}: ${pr.title}`);
          const merged = await mergePR(token, org, repo, pr);
          if (merged) {
            console.log(`     ✅ Merged`);
            totalMerged++;
          } else {
            console.log(`     ❌ Merge failed`);
            totalSkipped++;
          }
        }
      }
    } catch (e) {
      process.stdout.write(`❌ ${e.message}\n`);
      results.push({ repo, error: e.message });
    }
  }

  // ── Report ─────────────────────────────────────────────────────────────────
  if (opts.report) {
    const now = new Date().toISOString().slice(0, 10);
    let md = `# GitHub Daily Ops Report — ${now}\n\n`;
    md += `**Org:** ${org} | **Repos:** ${repos.length}\n\n`;
    md += `| Repo | Open PRs | Open Issues | Last Commit | Dependabot PRs |\n`;
    md += `|---|---|---|---|---|\n`;

    for (const r of results) {
      if (r.error) {
        md += `| ${r.repo} | ❌ error | — | — | — |\n`;
      } else {
        const lastCommit = r.lastCommit?.slice(0, 10) || '—';
        md += `| ${r.repo} | ${r.openPRs.length} | ${r.openIssues.length} | ${lastCommit} | ${r.dependabotPRs.length} |\n`;
      }
    }

    if (opts.mergeDependabot) {
      md += `\n## Dependabot Auto-Merge\n`;
      md += `- Merged: ${totalMerged}\n`;
      md += `- Skipped (HIGH/CI): ${totalSkipped}\n`;
    }

    console.log('\n' + md);
  }

  if (opts.mergeDependabot) {
    console.log(`\n✅ Dependabot: merged ${totalMerged}, skipped ${totalSkipped}`);
  }
}

main().catch(err => {
  console.error(`FATAL: ${err.message}`);
  process.exit(1);
});
