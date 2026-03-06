#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileP = promisify(execFile);

const DEFAULT_TASKS_ROOT = process.env.TASKS_ROOT || '/home/ds/.config/appdata/tasksmd/tasks';
const DEFAULT_FLATNOTES_ROOT = process.env.FLATNOTES_ROOT || '/home/ds/.config/appdata/flatnotes/data';
const OUT_MD = path.resolve('tmp/flatnotes-tasksmd-audit.md');
const OUT_JSON = path.resolve('tmp/flatnotes-tasksmd-audit.json');

const LANES = ['00 Inbox', '05 Backlog', '10 Next', '20 Doing', '30 Blocked', '40 Waiting', '90 Done'];

function argValue(flag, dflt = null) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return dflt;
  return process.argv[i + 1] ?? dflt;
}
function hasFlag(flag) {
  return process.argv.includes(flag);
}

const sinceDays = Number(argValue('--since-days', '30'));
const writeOutputs = hasFlag('--write');

function isoDateMinusDays(days) {
  const d = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  return d.toISOString().slice(0, 10);
}

function mdEscape(s) {
  return (s ?? '').replaceAll('|', '\\|');
}

async function readText(p) {
  return await fs.readFile(p, 'utf8');
}

async function listDirSafe(p) {
  try {
    return await fs.readdir(p, { withFileTypes: true });
  } catch {
    return null;
  }
}

function parseTags(txt) {
  const tags = [];
  const re = /\[tag:([^\]]+)\]/g;
  let m;
  while ((m = re.exec(txt))) {
    const t = m[1].trim();
    if (t) tags.push(t);
  }
  return tags;
}

function parseDue(txt) {
  const m = txt.match(/\[due:(\d{4}-\d{2}-\d{2})\]/);
  return m?.[1] ?? null;
}

function hasOutcomeSteps(txt) {
  const low = txt.toLowerCase();
  const hasOutcome = low.includes('**outcome:**');
  const hasSteps = low.includes('**steps:**') || low.includes('- [ ]');
  return { hasOutcome, hasSteps };
}

function extractUnblock(txt) {
  const lines = txt.split(/\r?\n/);
  for (const line of lines) {
    const m1 = line.match(/^\s*Unblock:\s*(.+)\s*$/i);
    if (m1) return m1[1].trim();
    const m2 = line.match(/^\s*- \[ \]\s*unblock\s*[:\-]?\s*(.+)\s*$/i);
    if (m2) return m2[1].trim();
  }
  return null;
}

function extractFlatnotesPointer(txt) {
  const lines = txt.split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/^\s*-\s*Flatnotes:\s*(.+)\s*$/i);
    if (m) return m[1].trim();
  }
  // fallback: any line containing "Flatnotes:" in Notes/Links
  const hit = lines.find(l => /Flatnotes:/i.test(l));
  return hit ? hit.trim() : null;
}

function parseRegistryTable(md) {
  // Expected rows:
  // | slug | status | hub title | [tag:proj-slug] | https://github.com/owner/repo |
  const lines = md.split(/\r?\n/);
  const projects = [];
  for (const line of lines) {
    if (!line.trim().startsWith('|')) continue;
    if (/^\|\s*Slug\s*\|/i.test(line)) continue;
    if (/^\|\s*-+\s*\|/.test(line)) continue;
    const cols = line.split('|').slice(1, -1).map(c => c.trim());
    if (cols.length < 5) continue;
    const [slug, status, hubTitle, tasksTag, repo] = cols;
    if (!slug || slug.toLowerCase() === 'slug') continue;
    if (!repo?.includes('github.com')) continue;
    const m = repo.match(/github\.com\/([^\s\)]+)\/?/);
    const ownerRepo = m ? m[1].replace(/\.git$/, '') : null;
    projects.push({ slug, status, hubTitle, tasksTag, repoUrl: repo, ownerRepo });
  }
  return projects;
}

function findSection(md, heading) {
  // returns section body (string) for a '## Heading' section
  const re = new RegExp(`^##\\s+${heading}\\s*$`, 'im');
  const m = re.exec(md);
  if (!m) return null;
  const start = m.index + m[0].length;
  const rest = md.slice(start);
  const next = rest.search(/^##\s+/m);
  return (next === -1 ? rest : rest.slice(0, next)).trim();
}

function extractAdrLinksFromDecisions(decisionsSection) {
  if (!decisionsSection) return [];
  const lines = decisionsSection.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  // Look for backticked ADR titles: `ADR slug - name`
  const out = [];
  for (const l of lines) {
    const m = l.match(/`(ADR\s+[^`]+)`/);
    if (m) out.push(m[1]);
  }
  return out;
}

async function ghJson(args, opts = {}) {
  try {
    const { stdout } = await execFileP('gh', args, { timeout: 30_000, maxBuffer: 10 * 1024 * 1024, ...opts });
    return { ok: true, data: JSON.parse(stdout) };
  } catch (err) {
    return { ok: false, error: String(err?.message || err) };
  }
}

async function collectTasks(tasksRoot) {
  const entries = await listDirSafe(tasksRoot);
  if (!entries) return { error: `Cannot read Tasks.md root: ${tasksRoot}` };

  const lanes = entries.filter(e => e.isDirectory()).map(e => e.name);
  const cards = [];

  for (const lane of lanes) {
    const lanePath = path.join(tasksRoot, lane);
    const kids = await listDirSafe(lanePath);
    if (!kids) continue;
    for (const e of kids) {
      if (!e.isFile()) continue;
      if (!e.name.toLowerCase().endsWith('.md')) continue;
      const cardPath = path.join(lanePath, e.name);
      const txt = await readText(cardPath);
      const tags = parseTags(txt);
      const due = parseDue(txt);
      const { hasOutcome, hasSteps } = hasOutcomeSteps(txt);
      const unblock = extractUnblock(txt);
      const flatPtr = extractFlatnotesPointer(txt);
      cards.push({
        lane,
        title: e.name.replace(/\.md$/i, ''),
        path: cardPath,
        tags,
        due,
        hasOutcome,
        hasSteps,
        unblock,
        flatnotesPointer: flatPtr,
        content: txt,
      });
    }
  }

  return { lanes, cards };
}

async function collectFlatnotes(flatRoot) {
  const entries = await listDirSafe(flatRoot);
  if (!entries) return { error: `Cannot read Flatnotes root: ${flatRoot}` };
  const mdFiles = entries.filter(e => e.isFile() && e.name.toLowerCase().endsWith('.md')).map(e => e.name);
  return { files: mdFiles };
}

function requiredPjtFiles(slug) {
  return {
    overview: `PJT ${slug} - 00 Overview.md`,
    research: `PJT ${slug} - 10 Research.md`,
    plan: `PJT ${slug} - 20 Plan.md`,
    log: `PJT ${slug} - 90 Log.md`,
  };
}

function normalizeRepo(ownerRepo) {
  if (!ownerRepo) return null;
  // strip trailing slash and fragments
  return ownerRepo.replace(/\/$/, '').trim();
}

function titleTokens(s) {
  return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(/\s+/).filter(Boolean);
}

function fuzzyIncludes(hay, needle) {
  // Very small heuristic: all needle tokens must appear somewhere in hay tokens.
  const h = new Set(titleTokens(hay));
  const n = titleTokens(needle);
  if (!n.length) return false;
  let hit = 0;
  for (const t of n) if (h.has(t)) hit++;
  return hit >= Math.min(4, n.length); // require up to 4 token matches
}

function findCardForPr(cards, pr) {
  const url = pr.url;
  const num = pr.number;
  const title = pr.title;
  // strongest: url match
  let hit = cards.find(c => c.content.includes(url));
  if (hit) return { kind: 'url', card: hit };
  // next: '#<num>' or 'PR #<num>'
  const re = new RegExp(`\\bPR\\s*#?${num}\\b|#${num}\\b`);
  hit = cards.find(c => re.test(c.content));
  if (hit) return { kind: 'number', card: hit };
  // fallback: fuzzy title match
  hit = cards.find(c => fuzzyIncludes(c.title, title));
  if (hit) return { kind: 'fuzzy', card: hit };
  return null;
}

async function main() {
  const tasksRoot = path.resolve(DEFAULT_TASKS_ROOT);
  const flatRoot = path.resolve(DEFAULT_FLATNOTES_ROOT);
  const since = isoDateMinusDays(sinceDays);

  const report = {
    meta: {
      generatedAt: new Date().toISOString(),
      sinceDays,
      sinceDate: since,
      tasksRoot,
      flatnotesRoot: flatRoot,
    },
    board: {},
    projects: [],
    errors: [],
  };

  // Registry
  const registryPath = path.join(flatRoot, 'SYS Workspace - Project Registry.md');
  let registryText = null;
  try {
    registryText = await readText(registryPath);
  } catch (e) {
    report.errors.push({ kind: 'registry_missing', path: registryPath, error: String(e?.message || e) });
  }
  const registry = registryText ? parseRegistryTable(registryText) : [];

  // Tasks scan
  const tasks = await collectTasks(tasksRoot);
  if (tasks.error) {
    report.errors.push({ kind: 'tasks_error', error: tasks.error });
  }
  const cards = tasks.cards ?? [];

  const laneCounts = {};
  for (const l of LANES) laneCounts[l] = 0;
  for (const c of cards) laneCounts[c.lane] = (laneCounts[c.lane] ?? 0) + 1;

  const doingCount = laneCounts['20 Doing'] ?? 0;
  const p2InNext = cards.filter(c => c.lane === '10 Next' && c.tags.includes('prio-p2'));
  const p01InBacklog = cards.filter(c => c.lane === '05 Backlog' && (c.tags.includes('prio-p0') || c.tags.includes('prio-p1')));

  const blockedMissingUnblock = cards.filter(c => c.lane === '30 Blocked' && !c.unblock);

  const projectCardsMissingFlatnotes = cards.filter(c => c.tags.some(t => t.startsWith('proj-')) && !c.flatnotesPointer);

  const formatMissing = cards.filter(c => !c.hasOutcome || !c.hasSteps);

  report.board = {
    lanesPresent: tasks.lanes ?? [],
    laneCounts,
    doingWipLimitOk: doingCount <= 3,
    p2InNextCount: p2InNext.length,
    p2InNext: p2InNext.map(c => ({ title: c.title, lane: c.lane, path: c.path })),
    p01InBacklogCount: p01InBacklog.length,
    p01InBacklog: p01InBacklog.map(c => ({ title: c.title, lane: c.lane, path: c.path })),
    blockedMissingUnblockCount: blockedMissingUnblock.length,
    blockedMissingUnblock: blockedMissingUnblock.map(c => ({ title: c.title, path: c.path })),
    projectCardsMissingFlatnotesCount: projectCardsMissingFlatnotes.length,
    projectCardsMissingFlatnotes: projectCardsMissingFlatnotes.map(c => ({ title: c.title, lane: c.lane, path: c.path })),
    formatMissingCount: formatMissing.length,
    formatMissing: formatMissing.map(c => ({ title: c.title, lane: c.lane, path: c.path, hasOutcome: c.hasOutcome, hasSteps: c.hasSteps })),
  };

  // Flatnotes scan
  const flat = await collectFlatnotes(flatRoot);
  if (flat.error) report.errors.push({ kind: 'flatnotes_error', error: flat.error });
  const flatFiles = new Set(flat.files ?? []);

  // GitHub availability
  // Use `gh auth status` (no JSON) as a cheap capability check.
  let githubAvailable = false;
  try {
    await execFileP('gh', ['auth', 'status'], { timeout: 15_000, maxBuffer: 2 * 1024 * 1024 });
    githubAvailable = true;
  } catch {
    githubAvailable = false;
  }

  const activeProjects = registry.filter(p => (p.status || '').toLowerCase() === 'active');

  for (const p of activeProjects) {
    const slug = p.slug;
    const req = requiredPjtFiles(slug);

    const missingFlatnotes = Object.values(req).filter(fn => !flatFiles.has(fn));

    let overviewText = null;
    let decisionsLinks = [];
    if (flatFiles.has(req.overview)) {
      overviewText = await readText(path.join(flatRoot, req.overview));
      const decisions = findSection(overviewText, 'Decisions');
      decisionsLinks = extractAdrLinksFromDecisions(decisions);
    }

    // Project log is the preferred place to record shipped PRs.
    // We use it to reconcile merged PRs so audits don't demand 1:1 Done cards.
    let logText = null;
    if (flatFiles.has(req.log)) {
      try {
        logText = await readText(path.join(flatRoot, req.log));
      } catch {
        logText = null;
      }
    }

    const adrMissing = [];
    for (const adrTitle of decisionsLinks) {
      const adrFile = `${adrTitle}.md`;
      if (!flatFiles.has(adrFile)) adrMissing.push(adrFile);
    }

    // Tasks for project
    const projTag = (p.tasksTag || '').match(/\[tag:([^\]]+)\]/)?.[1] || `proj-${slug}`;
    const projCards = cards.filter(c => c.tags.includes(projTag));

    // GitHub checks
    const ownerRepo = normalizeRepo(p.ownerRepo);
    let github = { ok: false, skipped: true, reason: 'SKIPPED_GITHUB', openPRs: [], mergedPRs: [], drift: [], warnings: [] };

    if (githubAvailable && ownerRepo) {
      github.skipped = false;
      const open = await ghJson(['pr', 'list', '--repo', ownerRepo, '--state', 'open', '--limit', '50', '--json', 'number,title,url,createdAt,updatedAt,headRefName,baseRefName,author']);
      const merged = await ghJson(['pr', 'list', '--repo', ownerRepo, '--state', 'merged', '--search', `merged:>=${since}`, '--limit', '50', '--json', 'number,title,url,mergedAt,closedAt,author']);

      if (!open.ok || !merged.ok) {
        github.ok = false;
        github.reason = `gh_error: open=${open.ok} merged=${merged.ok}`;
        if (!open.ok) github.drift.push({ kind: 'gh_open_error', error: open.error });
        if (!merged.ok) github.drift.push({ kind: 'gh_merged_error', error: merged.error });
      } else {
        github.ok = true;
        github.openPRs = open.data;
        github.mergedPRs = merged.data;

        // Orphan open PRs (no card match)
        for (const pr of github.openPRs) {
          const m = findCardForPr(projCards, pr);
          if (!m) github.drift.push({ kind: 'open_pr_missing_task', pr: { number: pr.number, title: pr.title, url: pr.url } });
        }

        // Merged PRs should be reflected as "shipped" either via:
        // - PR link in the Flatnotes project log (preferred), OR
        // - PR link/mention on a Done card.
        const doneCards = projCards.filter(c => c.lane === '90 Done');
        for (const pr of github.mergedPRs) {
          const prUrl = pr.url;
          const ownerRepoSlug = ownerRepo; // e.g. branexp/repo
          const canonicalUrl = ownerRepoSlug && pr.number
            ? `https://github.com/${ownerRepoSlug}/pull/${pr.number}`
            : prUrl;

          const inLog = !!logText && (logText.includes(prUrl) || (canonicalUrl && logText.includes(canonicalUrl)));
          if (inLog) continue;

          const m = findCardForPr(doneCards, pr);
          if (!m) {
            github.drift.push({ kind: 'merged_pr_missing_shipped_record', pr: { number: pr.number, title: pr.title, url: pr.url } });
          } else {
            // Not drift (it's recorded on a Done card), but we prefer the Flatnotes log.
            github.warnings.push({ kind: 'merged_pr_missing_flatnotes_log', pr: { number: pr.number, title: pr.title, url: pr.url } });
          }
        }

        // Traceability warning: Done cards missing *any* GitHub reference (PR link or commit hash).
        // This is a hygiene suggestion, not hard drift (some work lands via direct commits).
        for (const c of doneCards) {
          const hasPrLink = /github\.com\/[^\s]+\/pull\//.test(c.content);
          const hasCommit = /\b[0-9a-f]{7,40}\b/i.test(c.content);
          if (!hasPrLink && !hasCommit) {
            github.warnings.push({ kind: 'done_card_missing_github_ref', card: { title: c.title, path: c.path } });
          }
        }
      }
    }

    report.projects.push({
      slug,
      repo: ownerRepo,
      tasksTag: projTag,
      flatnotes: {
        required: req,
        missing: missingFlatnotes,
        decisionsAdrTitles: decisionsLinks,
        missingAdrFiles: adrMissing,
      },
      tasks: {
        totalCards: projCards.length,
        byLane: Object.fromEntries(LANES.map(l => [l, projCards.filter(c => c.lane === l).length])),
      },
      github,
    });
  }

  // Render Markdown
  const lines = [];
  lines.push(`# Flatnotes + Tasks.md Audit (GitHub truth)\n`);
  lines.push(`Generated: ${report.meta.generatedAt}`);
  lines.push(`Since: last ${sinceDays} day(s) (merged:>=${report.meta.sinceDate})\n`);

  lines.push(`## Board summary`);
  lines.push(`- Tasks root: \`${report.meta.tasksRoot}\``);
  lines.push(`- Flatnotes root: \`${report.meta.flatnotesRoot}\``);
  lines.push(`- Lane counts: ${LANES.map(l => `\`${l}\`: ${report.board.laneCounts?.[l] ?? 0}`).join(' | ')}`);
  lines.push(`- Doing WIP ≤ 3: ${report.board.doingWipLimitOk ? 'OK' : 'VIOLATION'}`);
  lines.push(`- prio-p2 in Next: ${report.board.p2InNextCount}`);
  lines.push(`- prio-p0/p1 in Backlog (review): ${report.board.p01InBacklogCount}`);
  lines.push(`- Blocked missing Unblock: ${report.board.blockedMissingUnblockCount}`);
  lines.push(`- Project cards missing Flatnotes pointer: ${report.board.projectCardsMissingFlatnotesCount}`);
  lines.push(`- Cards missing Outcome/Steps formatting: ${report.board.formatMissingCount}`);

  if (report.board.p2InNextCount) {
    lines.push(`\n**Lane violation:** prio-p2 in Next:`);
    for (const c of report.board.p2InNext.slice(0, 10)) lines.push(`- ${c.title}`);
  }
  if (report.board.p01InBacklogCount) {
    lines.push(`\n**Review:** prio-p0/p1 in Backlog:`);
    for (const c of report.board.p01InBacklog.slice(0, 10)) lines.push(`- ${c.title}`);
  }
  if (report.board.blockedMissingUnblockCount) {
    lines.push(`\n**Lane violation:** Blocked cards missing Unblock:`);
    for (const c of report.board.blockedMissingUnblock.slice(0, 10)) lines.push(`- ${c.title}`);
  }
  if (report.board.projectCardsMissingFlatnotesCount) {
    lines.push(`\n**Hygiene:** Project cards missing Flatnotes pointer:`);
    for (const c of report.board.projectCardsMissingFlatnotes.slice(0, 10)) lines.push(`- [${c.lane}] ${c.title}`);
  }
  if (report.board.formatMissingCount) {
    lines.push(`\n**Hygiene:** Cards missing Outcome/Steps formatting:`);
    for (const c of report.board.formatMissing.slice(0, 10)) lines.push(`- [${c.lane}] ${c.title}`);
  }

  if (report.errors.length) {
    lines.push(`\n## Errors`);
    for (const e of report.errors) lines.push(`- ${e.kind}: ${e.error || e.path || ''}`);
  }

  lines.push(`\n## Projects (active)`);
  lines.push(`| slug | repo | missing Flatnotes files | tasks (Next/Doing/Done) | GitHub drift |`);
  lines.push(`|---|---|---:|---:|---:|`);
  for (const p of report.projects) {
    const miss = p.flatnotes.missing.length;
    const n = p.tasks.byLane['10 Next'] ?? 0;
    const d = p.tasks.byLane['20 Doing'] ?? 0;
    const done = p.tasks.byLane['90 Done'] ?? 0;
    const ghDrift = p.github?.skipped ? 'SKIP' : String(p.github?.drift?.length ?? 0);
    lines.push(`| ${mdEscape(p.slug)} | ${mdEscape(p.repo || '')} | ${miss} | ${n}/${d}/${done} | ${ghDrift} |`);
  }

  for (const p of report.projects) {
    lines.push(`\n---\n\n## ${p.slug}`);
    lines.push(`Repo: ${p.repo || '(none)'}`);

    // Flatnotes
    lines.push(`\n### Flatnotes`);
    if (p.flatnotes.missing.length) {
      lines.push(`Missing expected project notes:`);
      for (const f of p.flatnotes.missing) lines.push(`- ${f}`);
    } else {
      lines.push(`All expected project notes present (00/10/20/90).`);
    }

    if (p.flatnotes.missingAdrFiles.length) {
      lines.push(`Missing ADR files referenced from hub Decisions:`);
      for (const f of p.flatnotes.missingAdrFiles) lines.push(`- ${f}`);
    }

    // GitHub
    lines.push(`\n### GitHub cross-check`);
    if (p.github.skipped) {
      lines.push(`GitHub checks: **SKIPPED** (${p.github.reason}).`);
    } else if (!p.github.ok) {
      lines.push(`GitHub checks: **ERROR** (${p.github.reason}).`);
      for (const d of p.github.drift) lines.push(`- ${d.kind}: ${d.error || ''}`);
    } else {
      lines.push(`Open PRs: ${p.github.openPRs.length} | Merged since ${since}: ${p.github.mergedPRs.length}`);
      if (!p.github.drift.length) {
        lines.push(`No GitHub↔Tasks drift detected by heuristics.`);
      } else {
        lines.push(`Drift findings:`);
        for (const d of p.github.drift.slice(0, 50)) {
          if (d.kind === 'open_pr_missing_task') lines.push(`- Open PR missing task: #${d.pr.number} ${d.pr.title} (${d.pr.url})`);
          else if (d.kind === 'merged_pr_missing_shipped_record') lines.push(`- Merged PR missing shipped record (Flatnotes log or Done card): #${d.pr.number} ${d.pr.title} (${d.pr.url})`);
          else lines.push(`- ${d.kind}`);
        }
      }

      if (p.github.warnings?.length) {
        lines.push(`Warnings (hygiene / traceability):`);
        for (const w of p.github.warnings.slice(0, 50)) {
          if (w.kind === 'done_card_missing_github_ref') {
            lines.push(`- Done card missing GitHub ref (PR/commit): ${w.card.title}`);
          } else if (w.kind === 'merged_pr_missing_flatnotes_log') {
            lines.push(`- Merged PR recorded on Done card but missing from Flatnotes log (preferred): #${w.pr.number} ${w.pr.title} (${w.pr.url})`);
          } else {
            lines.push(`- ${w.kind}`);
          }
        }
      }
    }
  }

  const md = lines.join('\n') + '\n';

  if (writeOutputs) {
    await fs.mkdir(path.dirname(OUT_MD), { recursive: true });
    await fs.writeFile(OUT_MD, md, 'utf8');
    await fs.writeFile(OUT_JSON, JSON.stringify(report, null, 2), 'utf8');
    console.log(`Wrote ${OUT_MD}`);
    console.log(`Wrote ${OUT_JSON}`);
  } else {
    process.stdout.write(md);
  }
}

main().catch(err => {
  console.error(err?.stack || String(err));
  process.exitCode = 1;
});
