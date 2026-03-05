#!/usr/bin/env node
/**
 * review.js — Cross-model review helper for OpenClaw cross-model-review skill
 *
 * Subcommands:
 *   init         Create a review workspace
 *   parse-round  Parse reviewer response, update issue tracker
 *   finalize     Generate plan-final.md, changelog.md, summary.json
 *   status       Print current workspace state
 *   next-step    Get next action for autonomous loop (alternating mode)
 *   save-plan    Save a revised plan from writer sub-agent
 *
 * Exit codes: 0=approved/ok  1=revise/unapproved  2=error
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Argument parsing — minimal, no external deps
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next !== undefined && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function die(msg, code = 2) {
  console.error(`ERROR: ${msg}`);
  process.exit(code);
}

function info(msg) {
  console.log(msg);
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e) {
    die(`Failed to read JSON from ${filePath}: ${e.message}`);
  }
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

/** Atomic JSON write: write to .tmp then rename (POSIX atomic). */
function writeJsonAtomic(filePath, data) {
  const tmp = filePath + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2) + '\n', 'utf8');
  fs.renameSync(tmp, filePath);
}

function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    die(`Cannot read file ${filePath}: ${e.message}`);
  }
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

/**
 * Read one line from stdin synchronously (for TTY confirmation prompts).
 * Uses fs.readSync on fd 0 to avoid external deps or async complexity.
 */
function readLineSync() {
  const buf = Buffer.allocUnsafe(1);
  let result = '';
  try {
    while (true) {
      const bytesRead = fs.readSync(0, buf, 0, 1, null);
      if (bytesRead === 0) break;
      const char = buf.slice(0, 1).toString('utf8');
      if (char === '\n') break;
      if (char !== '\r') result += char;
    }
  } catch (_) {
    // stdin not readable (non-TTY, pipe, etc.)
  }
  return result.trim();
}

// ---------------------------------------------------------------------------
// Model family detection — prevent same-provider review
// ---------------------------------------------------------------------------
const PROVIDER_FAMILIES = {
  anthropic: ['claude', 'anthropic', 'sonnet', 'haiku', 'opus'],
  openai:    ['gpt', 'openai', 'codex', 'o1', 'o3', 'davinci'],
  google:    ['gemini', 'google', 'bard', 'palm'],
  mistral:   ['mistral', 'mixtral'],
  meta:      ['llama', 'meta'],
  cohere:    ['command', 'cohere'],
};

function detectFamily(modelId) {
  const lower = modelId.toLowerCase();
  for (const [family, keywords] of Object.entries(PROVIDER_FAMILIES)) {
    for (const kw of keywords) {
      if (lower.includes(kw)) return family;
    }
  }
  // Fall back to the first path segment (e.g. "myprovider/model-name" → "myprovider")
  const firstSegment = lower.split('/')[0];
  return (firstSegment && firstSegment !== lower) ? firstSegment : 'unknown';
}

// ---------------------------------------------------------------------------
// Jaccard similarity for dedup
// ---------------------------------------------------------------------------
function normalizeText(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function tokenize(text) {
  return new Set(normalizeText(text).split(' ').filter(Boolean));
}

function jaccardSimilarity(a, b) {
  const setA = tokenize(a);
  const setB = tokenize(b);
  if (setA.size === 0 && setB.size === 0) return 1;
  let intersection = 0;
  for (const w of setA) { if (setB.has(w)) intersection++; }
  const union = setA.size + setB.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

// ---------------------------------------------------------------------------
// Issue ID generation
// ---------------------------------------------------------------------------
function nextIssueId(issues) {
  const nums = issues.map(iss => {
    const m = iss.id.match(/ISS-(\d+)/);
    return m ? parseInt(m[1], 10) : 0;
  });
  const max = nums.length ? Math.max(...nums) : 0;
  return `ISS-${String(max + 1).padStart(3, '0')}`;
}

// ---------------------------------------------------------------------------
// Review schema validation
// ---------------------------------------------------------------------------
const VALID_VERDICTS   = new Set(['APPROVED', 'REVISE']);
const VALID_SEVERITIES = new Set(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']);
const VALID_STATUSES   = new Set(['resolved', 'still-open', 'regressed', 'not-applicable']);
const RUBRIC_DIMENSIONS = [
  'security', 'data_integrity', 'concurrency',
  'error_handling', 'scalability', 'completeness', 'maintainability',
];

function validateReviewResponse(obj) {
  const errors = [];
  if (!VALID_VERDICTS.has(obj.verdict)) {
    errors.push(`verdict must be APPROVED or REVISE, got: ${obj.verdict}`);
  }
  if (!Array.isArray(obj.prior_issues)) {
    errors.push('prior_issues must be an array');
  } else {
    obj.prior_issues.forEach((pi, i) => {
      if (!pi.id || typeof pi.id !== 'string') errors.push(`prior_issues[${i}].id missing`);
      if (!VALID_STATUSES.has(pi.status)) errors.push(`prior_issues[${i}].status invalid: ${pi.status}`);
    });
  }
  if (!Array.isArray(obj.new_issues)) {
    errors.push('new_issues must be an array');
  } else {
    obj.new_issues.forEach((ni, i) => {
      if (!VALID_SEVERITIES.has(ni.severity)) errors.push(`new_issues[${i}].severity invalid: ${ni.severity}`);
      if (!ni.location) errors.push(`new_issues[${i}].location missing`);
      if (!ni.problem)  errors.push(`new_issues[${i}].problem missing`);
      if (!ni.fix)      errors.push(`new_issues[${i}].fix missing`);
    });
  }
  if (typeof obj.summary !== 'string') {
    errors.push('summary must be a string');
  }

  // Rubric validation (optional for backward compat, but validated if present)
  if (obj.rubric !== undefined && obj.rubric !== null) {
    if (typeof obj.rubric !== 'object' || Array.isArray(obj.rubric)) {
      errors.push('rubric must be an object');
    } else {
      let scoredCount = 0;
      for (const dim of RUBRIC_DIMENSIONS) {
        const entry = obj.rubric[dim];
        if (entry === undefined) {
          errors.push(`rubric.${dim} is missing`);
          continue;
        }
        if (typeof entry !== 'object' || entry === null) {
          errors.push(`rubric.${dim} must be an object with score and rationale`);
          continue;
        }
        if (entry.score !== null) {
          if (typeof entry.score !== 'number' || entry.score < 0 || entry.score > 5 || !Number.isInteger(entry.score)) {
            errors.push(`rubric.${dim}.score must be an integer 0-5 or null, got: ${entry.score}`);
          } else {
            scoredCount++;
          }
        }
        if (typeof entry.rationale !== 'string' || entry.rationale.length === 0) {
          errors.push(`rubric.${dim}.rationale must be a non-empty string`);
        }
      }
      if (scoredCount < 3) {
        errors.push(`rubric must have at least 3 scored (non-null) dimensions, got: ${scoredCount}`);
      }
    }
  }

  return errors;
}

// ---------------------------------------------------------------------------
// Parse reviewer response text → JSON, stripping fences if needed
// ---------------------------------------------------------------------------
function extractJson(raw) {
  // Try direct parse first
  try {
    return JSON.parse(raw.trim());
  } catch (_) {}

  // Strip markdown fences
  const fenceMatch = raw.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fenceMatch) {
    try {
      return JSON.parse(fenceMatch[1].trim());
    } catch (_) {}
  }

  // Find first { ... } block
  const start = raw.indexOf('{');
  const end   = raw.lastIndexOf('}');
  if (start !== -1 && end !== -1 && end > start) {
    try {
      return JSON.parse(raw.slice(start, end + 1));
    } catch (_) {}
  }

  throw new Error('Could not extract valid JSON from reviewer response');
}

// ---------------------------------------------------------------------------
// Workspace state helpers
// ---------------------------------------------------------------------------
function getWorkspaceMeta(wsDir) {
  const metaPath = path.join(wsDir, 'meta.json');
  if (!fs.existsSync(metaPath)) die(`Not a review workspace: ${wsDir}`);
  return readJson(metaPath);
}

function getIssues(wsDir) {
  const p = path.join(wsDir, 'issues.json');
  return fs.existsSync(p) ? readJson(p) : [];
}

function saveIssues(wsDir, issues) {
  writeJson(path.join(wsDir, 'issues.json'), issues);
}

function getOpenBlockers(issues) {
  return issues.filter(iss =>
    (iss.severity === 'CRITICAL' || iss.severity === 'HIGH') &&
    (iss.status === 'open' || iss.status === 'still-open' || iss.status === 'regressed')
  );
}

// ---------------------------------------------------------------------------
// COMMAND: init
// ---------------------------------------------------------------------------
function cmdInit(args) {
  const mode          = args['mode'] || 'static';
  const planPath      = args['plan'];
  const outBase       = args['out'] || path.join(process.cwd(), 'tasks/reviews');
  const maxRounds     = parseInt(args['max-rounds'] || (mode === 'alternating' ? '8' : '5'), 10);
  const tokenBudget   = parseInt(args['token-budget'] || '8000', 10);
  const projectCtx    = args['project-context'] || '';

  if (!planPath) die('--plan <file> is required');
  if (!['static', 'alternating'].includes(mode)) die('--mode must be "static" or "alternating"');

  if (isNaN(maxRounds) || maxRounds < 1)   die('--max-rounds must be a positive integer');
  if (isNaN(tokenBudget) || tokenBudget < 1) die('--token-budget must be a positive integer');
  if (!fs.existsSync(planPath)) die(`Plan file not found: ${planPath}`);

  let reviewerModel, plannerModel, rFamily, pFamily, modelA, modelB, familyA, familyB;

  if (mode === 'alternating') {
    modelA = args['model-a'];
    modelB = args['model-b'];
    if (!modelA) die('--model-a <model> is required for alternating mode');
    if (!modelB) die('--model-b <model> is required for alternating mode');
    familyA = detectFamily(modelA);
    familyB = detectFamily(modelB);
    if (familyA !== 'unknown' && familyB !== 'unknown' && familyA === familyB) {
      die(`Model A and Model B are from the same provider family (${familyA}). Cross-provider review required.`);
    }
    // For backward compat, set reviewer/planner to modelB/modelA
    reviewerModel = modelB;
    plannerModel  = modelA;
    rFamily = familyB;
    pFamily = familyA;
  } else {
    reviewerModel = args['reviewer-model'];
    plannerModel  = args['planner-model'];
    if (!reviewerModel) die('--reviewer-model <model> is required');
    if (!plannerModel)  die('--planner-model <model> is required');
    rFamily = detectFamily(reviewerModel);
    pFamily = detectFamily(plannerModel);
    modelA = plannerModel;
    modelB = reviewerModel;
    familyA = pFamily;
    familyB = rFamily;
  }

  if (rFamily === 'unknown' && pFamily === 'unknown') {
    console.warn(`WARNING: Both models resolved to unknown provider family. Cannot verify cross-provider constraint. Proceeding anyway.`);
  } else if (rFamily === 'unknown') {
    console.warn(`WARNING: Reviewer model resolved to unknown provider family. Proceeding anyway.`);
  } else if (pFamily === 'unknown') {
    console.warn(`WARNING: Planner model resolved to unknown provider family. Proceeding anyway.`);
  } else if (mode === 'static' && rFamily === pFamily) {
    die(`Reviewer and planner are from the same provider family (${rFamily}). Cross-provider review required.`);
  }

  ensureDir(outBase);

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const uuid      = Math.random().toString(36).slice(2, 10);
  const wsDir     = path.join(outBase, `${timestamp}-${uuid}`);
  ensureDir(wsDir);

  // Copy plan as v1
  const planContent = readFile(planPath);
  fs.writeFileSync(path.join(wsDir, 'plan-v1.md'), planContent, 'utf8');

  // Write meta
  const meta = {
    created:        new Date().toISOString(),
    mode,
    modelA,
    modelB,
    familyA,
    familyB,
    reviewerModel,
    plannerModel,
    reviewerFamily: rFamily,
    plannerFamily:  pFamily,
    maxRounds,
    tokenBudget,
    projectContext: projectCtx,
    currentRound:   0,
    verdict:        'PENDING',
    needsRevision:  false,
    wsDir,
  };
  writeJsonAtomic(path.join(wsDir, 'meta.json'), meta);

  // Initialize issue tracker and changelog
  writeJson(path.join(wsDir, 'issues.json'), []);
  fs.writeFileSync(path.join(wsDir, 'changelog.md'), `# Review Changelog\n\nWorkspace: ${wsDir}\nStarted: ${meta.created}\nMode: ${mode}\nModel A: ${modelA}\nModel B: ${modelB}\n\n`, 'utf8');

  info(wsDir);
  return 0;
}

// ---------------------------------------------------------------------------
// COMMAND: parse-round
// ---------------------------------------------------------------------------
function cmdParseRound(args) {
  const wsDir    = args['workspace'];
  const round    = parseInt(args['round'], 10);
  const respPath = args['response'];

  if (!wsDir)    die('--workspace <dir> is required');
  if (!round || isNaN(round)) die('--round <n> is required');
  if (!respPath) die('--response <file> is required');

  if (!fs.existsSync(wsDir))    die(`Workspace not found: ${wsDir}`);
  if (!fs.existsSync(respPath)) die(`Response file not found: ${respPath}`);

  const raw = readFile(respPath);
  let parsed;
  try {
    parsed = extractJson(raw);
  } catch (e) {
    die(`JSON extraction failed: ${e.message}`);
  }

  const schemaErrors = validateReviewResponse(parsed);
  if (schemaErrors.length > 0) {
    console.error('Schema validation errors:');
    schemaErrors.forEach(e => console.error(`  - ${e}`));
    die(`Response failed schema validation (${schemaErrors.length} errors)`);
  }

  const issues = getIssues(wsDir);

  // ---- Process prior issue status updates ----
  const priorUpdateMap = {};
  for (const pu of (parsed.prior_issues || [])) {
    priorUpdateMap[pu.id] = pu;
  }

  for (const iss of issues) {
    if (priorUpdateMap[iss.id]) {
      const update = priorUpdateMap[iss.id];
      iss.status = update.status;
      if (update.status === 'resolved' || update.status === 'not-applicable') {
        iss.round_resolved = round;
      }
      iss.last_evidence = update.evidence || null;
    }
  }

  // ---- Dedup check on new issues ----
  // Check each new issue against: (a) existing open issues AND (b) other new issues in this batch
  const openIssues = issues.filter(i => i.status === 'open' || i.status === 'still-open' || i.status === 'regressed');
  const dedupWarnings = [];
  const assignedNewIssues = [];

  for (let idx = 0; idx < (parsed.new_issues || []).length; idx++) {
    const ni = parsed.new_issues[idx];
    let maxSim = 0;
    let dupOf  = null;

    // Check against existing open issues from prior rounds
    for (const open of openIssues) {
      const sim = jaccardSimilarity(ni.problem, open.problem);
      if (sim > maxSim) {
        maxSim = sim;
        dupOf  = open.id;
      }
    }

    // Check against other new issues already assigned in this same batch (intra-batch dedup)
    for (const prev of assignedNewIssues) {
      const sim = jaccardSimilarity(ni.problem, prev.problem);
      if (sim > maxSim) {
        maxSim = sim;
        dupOf  = prev.id;
      }
    }

    if (maxSim >= 0.6) {
      dedupWarnings.push({
        new_issue_index:       idx,
        possible_duplicate_of: dupOf,
        similarity:            Math.round(maxSim * 100) / 100,
        note: `New issue overlaps significantly with ${dupOf}. Confirm if distinct.`,
      });
    }

    // Assign stable ID and add to issues regardless (human reviews dedup warnings)
    const newId = nextIssueId([...issues, ...assignedNewIssues]);
    const newIssue = {
      id:             newId,
      severity:       ni.severity,
      location:       ni.location,
      problem:        ni.problem,
      fix:            ni.fix,
      status:         'open',
      round_found:    round,
      round_resolved: null,
      last_evidence:  null,
    };
    assignedNewIssues.push(newIssue);
    issues.push(newIssue);
  }

  saveIssues(wsDir, issues);

  // ---- Rubric scoring ----
  let rubric = null;
  let rubricWarnings = [];
  if (parsed.rubric && typeof parsed.rubric === 'object') {
    rubric = {};
    const scores = [];
    for (const dim of RUBRIC_DIMENSIONS) {
      const entry = parsed.rubric[dim];
      if (entry && typeof entry === 'object') {
        rubric[dim] = {
          score: entry.score !== undefined ? entry.score : null,
          rationale: entry.rationale || '',
        };
        if (entry.score !== null && typeof entry.score === 'number') {
          scores.push(entry.score);
          if (entry.score < 2) {
            rubricWarnings.push(`${dim} scored ${entry.score}/5 — critical weakness`);
          }
        }
      }
    }
    if (scores.length > 0) {
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      rubric._average = Math.round(avg * 100) / 100;
      rubric._scored_dimensions = scores.length;
      if (avg < 3.0) {
        rubricWarnings.push(`Average rubric score ${rubric._average}/5 is below threshold (3.0)`);
      }
    }
  }

  // ---- Approval gate ----
  const blockers   = getOpenBlockers(issues);
  let finalVerdict = parsed.verdict;

  if (finalVerdict === 'APPROVED' && blockers.length > 0) {
    console.error(`WARNING: Reviewer said APPROVED but ${blockers.length} CRITICAL/HIGH issue(s) are still open.`);
    console.error('Overriding verdict to REVISE.');
    finalVerdict = 'REVISE';
  }

  // ---- Save round output ----
  const roundOutput = {
    round,
    verdict:       finalVerdict,
    reviewVerdict: parsed.verdict,
    summary:       parsed.summary,
    rubric:        rubric,
    rubricWarnings,
    newIssues:     assignedNewIssues.map(i => i.id),
    dedupWarnings,
    blockers:      blockers.map(i => i.id),
  };
  writeJson(path.join(wsDir, `round-${round}-output.json`), roundOutput);

  // ---- Update meta ----
  const meta = getWorkspaceMeta(wsDir);
  meta.currentRound = round;
  meta.verdict = finalVerdict;
  meta.needsRevision = (finalVerdict === 'REVISE');
  writeJsonAtomic(path.join(wsDir, 'meta.json'), meta);

  // ---- Append to changelog ----
  const openCount     = issues.filter(i => i.status === 'open' || i.status === 'still-open').length;
  const resolvedCount = issues.filter(i => i.status === 'resolved').length;
  const rubricLine = rubric && rubric._average !== undefined
    ? `Rubric: avg ${rubric._average}/5 (${rubric._scored_dimensions} dimensions)${rubricWarnings.length ? ' ⚠️ ' + rubricWarnings.join('; ') : ''}`
    : 'Rubric: not provided';
  const changeEntry   = [
    `\n## Round ${round} — ${new Date().toISOString()}`,
    `Verdict: **${finalVerdict}**`,
    `Summary: ${parsed.summary}`,
    rubricLine,
    `New issues: ${assignedNewIssues.length} (${assignedNewIssues.map(i => `${i.id} ${i.severity}`).join(', ') || 'none'})`,
    `Dedup warnings: ${dedupWarnings.length}`,
    `Open blockers: ${blockers.length}`,
    `Total open: ${openCount} | Resolved: ${resolvedCount}`,
    '',
  ].join('\n');
  fs.appendFileSync(path.join(wsDir, 'changelog.md'), changeEntry, 'utf8');

  // ---- Print result ----
  info(JSON.stringify({
    verdict: finalVerdict,
    round,
    rubric: rubric ? {
      average: rubric._average,
      scored: rubric._scored_dimensions,
      warnings: rubricWarnings,
      dimensions: Object.fromEntries(
        RUBRIC_DIMENSIONS.map(d => [d, rubric[d] || null])
      ),
    } : null,
    newIssues: assignedNewIssues.length,
    dedupWarnings: dedupWarnings.length,
    blockers: blockers.length,
    dedupWarningDetails: dedupWarnings,
  }, null, 2));

  return finalVerdict === 'APPROVED' ? 0 : 1;
}

// ---------------------------------------------------------------------------
// COMMAND: finalize
// ---------------------------------------------------------------------------
function cmdFinalize(args) {
  const wsDir          = args['workspace'];
  const overrideReason = args['override-reason'];
  const ciForce        = !!args['ci-force'];

  if (!wsDir) die('--workspace <dir> is required');
  if (!fs.existsSync(wsDir)) die(`Workspace not found: ${wsDir}`);

  const meta     = getWorkspaceMeta(wsDir);
  const issues   = getIssues(wsDir);
  const blockers = getOpenBlockers(issues);

  let forceApproveLog = null;

  if (blockers.length > 0) {
    if (!overrideReason) {
      die(
        `Cannot finalize: ${blockers.length} CRITICAL/HIGH issue(s) still open (${blockers.map(i => i.id).join(', ')}).\n` +
        'Use --override-reason "text" to force-approve.'
      );
    }

    if (overrideReason.length < 10) {
      die('--override-reason must be at least 10 characters.');
    }

    const isTTY = process.stdin.isTTY && process.stdout.isTTY;

    if (isTTY && !ciForce) {
      // Interactive confirmation via readline (no execSync dependency)
      const warning = [
        '',
        '⚠️  FORCE APPROVE: This will bypass unresolved CRITICAL/HIGH issues.',
        `Unresolved: ${blockers.map(i => `${i.id}(${i.severity})`).join(', ')}`,
        `Override reason: "${overrideReason}"`,
        'Type CONFIRM to proceed, or Ctrl-C to abort: ',
      ].join('\n');
      process.stderr.write(warning);

      const input = readLineSync();
      if (input !== 'CONFIRM') {
        die('Force-approve aborted (did not receive CONFIRM).', 1);
      }
    } else if (!ciForce) {
      // Non-interactive without --ci-force: reject
      die(
        'Force-approve in non-interactive mode requires both --override-reason and --ci-force.',
        2
      );
    }
    // If ciForce is set, skip confirmation (non-interactive CI path)

    forceApproveLog = {
      actor:             process.env.USER || process.env.CI_ACTOR || 'unknown',
      reason:            overrideReason,
      timestamp:         new Date().toISOString(),
      unresolved_issues: blockers.map(i => i.id),
      tty_confirmed:     (isTTY && !ciForce),
      ci_force:          ciForce,
    };

    // Mark blockers as force-approved
    for (const iss of issues) {
      if (blockers.find(b => b.id === iss.id)) {
        iss.status = 'force-approved';
        iss.round_resolved = meta.currentRound;
      }
    }
    saveIssues(wsDir, issues);
  }

  // ---- Find latest plan version ----
  const planVersions = fs.readdirSync(wsDir)
    .filter(f => /^plan-v\d+\.md$/.test(f))
    .sort((a, b) => {
      const na = parseInt(a.match(/(\d+)/)[1], 10);
      const nb = parseInt(b.match(/(\d+)/)[1], 10);
      return na - nb;
    });

  if (planVersions.length === 0) die('No plan versions found in workspace.');
  const latestPlan = readFile(path.join(wsDir, planVersions[planVersions.length - 1]));

  // plan-final.md — clean copy without review comments
  const finalPlan = latestPlan
    .replace(/<!--[\s\S]*?-->/g, '')  // strip HTML comments
    .replace(/\n{3,}/g, '\n\n')       // collapse extra blank lines
    .trim() + '\n';
  fs.writeFileSync(path.join(wsDir, 'plan-final.md'), finalPlan, 'utf8');

  // ---- Summary ----
  const totalFound    = issues.length;
  const totalResolved = issues.filter(i => ['resolved', 'not-applicable', 'force-approved'].includes(i.status)).length;
  const bySeverity    = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const iss of issues) {
    const key = iss.severity.toLowerCase();
    if (key in bySeverity) bySeverity[key]++;
  }

  // ---- Aggregate rubric scores across rounds ----
  let latestRubric = null;
  for (let r = meta.currentRound; r >= 1; r--) {
    const roundOutPath = path.join(wsDir, `round-${r}-output.json`);
    if (fs.existsSync(roundOutPath)) {
      const roundOut = readJson(roundOutPath);
      if (roundOut.rubric) {
        latestRubric = roundOut.rubric;
        break;
      }
    }
  }

  const isTTY = process.stdin.isTTY && process.stdout.isTTY;
  const summary = {
    rounds:            meta.currentRound,
    plannerModel:      meta.plannerModel,
    reviewerModel:     meta.reviewerModel,
    totalIssuesFound:  totalFound,
    issuesBySeverity:  bySeverity,
    issuesResolved:    totalResolved,
    issuesUnresolved:  totalFound - totalResolved,
    rubric:            latestRubric ? {
      average:    latestRubric._average,
      scored:     latestRubric._scored_dimensions,
      dimensions: Object.fromEntries(
        RUBRIC_DIMENSIONS.map(d => [d, latestRubric[d] || null])
      ),
    } : null,
    finalVerdict:      blockers.length > 0 && forceApproveLog ? 'FORCE_APPROVED' : 'APPROVED',
    completedAt:       new Date().toISOString(),
    force_approve_log: forceApproveLog,
  };
  writeJson(path.join(wsDir, 'summary.json'), summary);

  // ---- Finalize changelog ----
  const finalEntry = [
    `\n## FINAL — ${summary.completedAt}`,
    `Verdict: **${summary.finalVerdict}**`,
    `Rounds: ${summary.rounds}`,
    `Issues found: ${totalFound} | Resolved: ${totalResolved} | Unresolved: ${summary.issuesUnresolved}`,
    forceApproveLog ? `Force-approved by: ${forceApproveLog.actor} — "${forceApproveLog.reason}"` : '',
    '',
  ].filter(l => l !== undefined).join('\n');
  fs.appendFileSync(path.join(wsDir, 'changelog.md'), finalEntry, 'utf8');

  // Update meta
  meta.verdict = summary.finalVerdict;
  meta.completedAt = summary.completedAt;
  writeJsonAtomic(path.join(wsDir, 'meta.json'), meta);

  info(JSON.stringify({
    verdict:        summary.finalVerdict,
    planFinal:      path.join(wsDir, 'plan-final.md'),
    summaryJson:    path.join(wsDir, 'summary.json'),
    changelogMd:    path.join(wsDir, 'changelog.md'),
    issuesJson:     path.join(wsDir, 'issues.json'),
    rounds:         summary.rounds,
    issuesFound:    totalFound,
    issuesResolved: totalResolved,
    forceApproved:  !!forceApproveLog,
  }, null, 2));

  return 0;
}

// ---------------------------------------------------------------------------
// COMMAND: status
// ---------------------------------------------------------------------------
function cmdStatus(args) {
  const wsDir = args['workspace'];
  if (!wsDir) die('--workspace <dir> is required');
  if (!fs.existsSync(wsDir)) die(`Workspace not found: ${wsDir}`);

  const meta     = getWorkspaceMeta(wsDir);
  const issues   = getIssues(wsDir);
  const open     = issues.filter(i => i.status === 'open' || i.status === 'still-open' || i.status === 'regressed');
  const resolved = issues.filter(i => ['resolved', 'not-applicable', 'force-approved'].includes(i.status));
  const blockers = getOpenBlockers(issues);

  // Fetch latest rubric from most recent round output
  let latestRubric = null;
  for (let r = meta.currentRound; r >= 1; r--) {
    const roundOutPath = path.join(wsDir, `round-${r}-output.json`);
    if (fs.existsSync(roundOutPath)) {
      const roundOut = readJson(roundOutPath);
      if (roundOut.rubric) {
        latestRubric = roundOut.rubric;
        break;
      }
    }
  }

  const out = {
    workspace:      wsDir,
    verdict:        meta.verdict,
    currentRound:   meta.currentRound,
    reviewerModel:  meta.reviewerModel,
    plannerModel:   meta.plannerModel,
    totalIssues:    issues.length,
    openIssues:     open.length,
    resolvedIssues: resolved.length,
    rubric:         latestRubric ? {
      average:    latestRubric._average,
      scored:     latestRubric._scored_dimensions,
      dimensions: Object.fromEntries(
        RUBRIC_DIMENSIONS.map(d => [d, latestRubric[d] || null])
      ),
    } : null,
    blockers:       blockers.map(i => ({ id: i.id, severity: i.severity, problem: i.problem })),
    allIssues:      issues.map(i => ({
      id:       i.id,
      severity: i.severity,
      status:   i.status,
      location: i.location,
      problem:  i.problem.slice(0, 80) + (i.problem.length > 80 ? '...' : ''),
    })),
  };

  info(JSON.stringify(out, null, 2));
  return meta.verdict === 'APPROVED' || meta.verdict === 'FORCE_APPROVED' ? 0 : 1;
}

// ---------------------------------------------------------------------------
// COMMAND: next-step (alternating mode orchestrator)
// ---------------------------------------------------------------------------
function cmdNextStep(args) {
  const wsDir = args['workspace'];
  if (!wsDir) die('--workspace <dir> is required');

  // Error states returned as JSON instead of dying (orchestrator needs machine-readable errors)
  if (!fs.existsSync(wsDir)) {
    info(JSON.stringify({ action: 'error', reason: `workspace not found: ${wsDir}` }));
    return 2;
  }

  const metaPath = path.join(wsDir, 'meta.json');
  if (!fs.existsSync(metaPath)) {
    info(JSON.stringify({ action: 'error', reason: 'meta.json missing or corrupt' }));
    return 2;
  }

  let meta;
  try { meta = readJson(metaPath); } catch (e) {
    info(JSON.stringify({ action: 'error', reason: `meta.json parse error: ${e.message}` }));
    return 2;
  }

  const issues = getIssues(wsDir);

  // Sanity: needsRevision but no rounds completed
  if (meta.needsRevision && meta.currentRound === 0) {
    info(JSON.stringify({ action: 'error', reason: 'needsRevision set but no rounds completed' }));
    return 2;
  }

  // Already finalized?
  if (meta.verdict === 'APPROVED' || meta.verdict === 'FORCE_APPROVED') {
    info(JSON.stringify({ action: 'done', reason: 'already approved' }));
    return 0;
  }

  const mode = meta.mode || 'static';
  const round = meta.currentRound;
  const templateDir = path.join(__dirname, '..', 'templates');

  // --- Determine state ---
  // needsRevision: last parse-round returned REVISE, writer hasn't produced next plan yet
  if (meta.needsRevision) {
    // Writer needs to produce plan-v(round+1).md
    const nextPlanVersion = round + 1;
    const nextPlanPath = path.join(wsDir, `plan-v${nextPlanVersion}.md`);

    // Who writes? In alternating: the reviewer of the last round (they implement their own fixes)
    // Round N reviewer: odd=B, even=A. So the writer for revision after round N is:
    let writerModel;
    if (mode === 'alternating') {
      writerModel = (round % 2 === 1) ? meta.modelB : meta.modelA;
    } else {
      writerModel = meta.plannerModel;  // static mode: planner always writes
    }

    // Build writer prompt
    const currentPlanVersion = getLatestPlanVersion(wsDir);
    const planContent = readFile(path.join(wsDir, currentPlanVersion));

    // Get last round's review summary
    const roundOutPath = path.join(wsDir, `round-${round}-output.json`);
    let reviewSummary = 'No review summary available.';
    if (fs.existsSync(roundOutPath)) {
      const roundOut = readJson(roundOutPath);
      reviewSummary = roundOut.summary || reviewSummary;
    }

    // Get open issues
    const openIssues = issues
      .filter(i => ['open', 'still-open', 'regressed'].includes(i.status))
      .map(i => `- [${i.severity}] ${i.id}: ${i.location} — ${i.problem}\n  Fix: ${i.fix}`)
      .join('\n');

    // Load writer prompt template
    const writerTemplatePath = path.join(templateDir, 'writer-prompt.md');
    let writerPrompt;
    if (fs.existsSync(writerTemplatePath)) {
      writerPrompt = readFile(writerTemplatePath)
        .replace('{plan_content}', planContent)
        .replace('{review_summary}', reviewSummary)
        .replace('{open_issues}', openIssues || 'No open issues.');
    } else {
      writerPrompt = `Rewrite this plan addressing the review feedback.\n\nPlan:\n${planContent}\n\nFeedback: ${reviewSummary}\n\nIssues:\n${openIssues}`;
    }

    info(JSON.stringify({
      action:      'revise',
      model:       writerModel,
      round:       round,
      planVersion: nextPlanVersion,
      saveTo:      nextPlanPath,
      prompt:      writerPrompt,
    }));
    return 0;
  }

  // Not pending revision — need to do a review
  const nextRound = round + 1;

  // Max rounds check
  if (nextRound > meta.maxRounds) {
    info(JSON.stringify({ action: 'max-rounds', reason: `reached max rounds (${meta.maxRounds})`, round }));
    return 1;
  }

  // Who reviews?
  let reviewerModel;
  if (mode === 'alternating') {
    // Odd rounds: B reviews. Even rounds: A reviews.
    reviewerModel = (nextRound % 2 === 1) ? meta.modelB : meta.modelA;
  } else {
    reviewerModel = meta.reviewerModel;
  }

  // Build reviewer prompt
  const currentPlanVersion = getLatestPlanVersion(wsDir);
  const planContent = readFile(path.join(wsDir, currentPlanVersion));

  // Choose template
  const templateName = (mode === 'alternating') ? 'alternating-reviewer-prompt.md' : 'reviewer-prompt.md';
  const templatePath = path.join(templateDir, templateName);
  let reviewerPrompt;

  const priorIssuesJson = (issues.length === 0)
    ? '"First review — no prior issues"'
    : JSON.stringify(issues.map(i => ({
        id: i.id, severity: i.severity, location: i.location,
        problem: i.problem, fix: i.fix, status: i.status, round_found: i.round_found,
      })), null, 2);

  if (fs.existsSync(templatePath)) {
    reviewerPrompt = readFile(templatePath)
      .replace('{plan_content}', planContent)
      .replace('{round}', String(nextRound))
      .replace('{prior_issues_json}', priorIssuesJson)
      .replace('{codebase_context_or_"None provided"}', meta.projectContext || 'None provided')
      .replace('{project_context}', meta.projectContext || 'None provided');
  } else {
    reviewerPrompt = `Review this plan (round ${nextRound}):\n\n${planContent}\n\nPrior issues: ${priorIssuesJson}`;
  }

  info(JSON.stringify({
    action:      'review',
    model:       reviewerModel,
    round:       nextRound,
    planVersion: currentPlanVersion,
    prompt:      reviewerPrompt,
  }));
  return 0;
}

// Helper: find latest plan-vN.md in workspace
function getLatestPlanVersion(wsDir) {
  const planVersions = fs.readdirSync(wsDir)
    .filter(f => /^plan-v\d+\.md$/.test(f))
    .sort((a, b) => {
      const na = parseInt(a.match(/(\d+)/)[1], 10);
      const nb = parseInt(b.match(/(\d+)/)[1], 10);
      return na - nb;
    });
  if (planVersions.length === 0) die('No plan versions found in workspace.');
  return planVersions[planVersions.length - 1];
}

// ---------------------------------------------------------------------------
// COMMAND: save-plan (save a revised plan from writer sub-agent)
// ---------------------------------------------------------------------------
function cmdSavePlan(args) {
  const wsDir   = args['workspace'];
  const planPath = args['plan'];
  const version  = parseInt(args['version'], 10);

  if (!wsDir)   die('--workspace <dir> is required');
  if (!planPath) die('--plan <file> is required');
  if (!version || isNaN(version)) die('--version <n> is required');
  if (!fs.existsSync(wsDir))    die(`Workspace not found: ${wsDir}`);
  if (!fs.existsSync(planPath)) die(`Plan file not found: ${planPath}`);

  const planContent = readFile(planPath);

  // Validate: reject empty/garbage output
  if (planContent.length < 50) {
    die(`Plan file too small (${planContent.length} bytes) — likely empty or failed output. Min 50 bytes.`, 1);
  }
  if (!/^#\s/m.test(planContent)) {
    die('Plan file contains no markdown heading (# ...). Likely not a valid plan.', 1);
  }

  const destPath = path.join(wsDir, `plan-v${version}.md`);
  fs.writeFileSync(destPath, planContent, 'utf8');

  // Update meta: revision done, ready for next review
  const meta = getWorkspaceMeta(wsDir);
  meta.needsRevision = false;
  writeJsonAtomic(path.join(wsDir, 'meta.json'), meta);

  // Append to changelog
  const entry = `\n## Plan v${version} — ${new Date().toISOString()}\nRevised plan saved (${planContent.length} chars)\n`;
  fs.appendFileSync(path.join(wsDir, 'changelog.md'), entry, 'utf8');

  info(JSON.stringify({ saved: destPath, version, chars: planContent.length }));
  return 0;
}

// ---------------------------------------------------------------------------
// Help
// ---------------------------------------------------------------------------
function printHelp() {
  const text = `
review.js — Cross-model review helper

Usage: node review.js <command> [options]

Commands:
  init           Create a review workspace
  parse-round    Parse a reviewer response, update issue tracker
  finalize       Generate plan-final.md, changelog.md, summary.json
  status         Print current workspace state
  next-step      Get next action for autonomous loop (any mode)
  save-plan      Save a revised plan version from writer output

Global options:
  --help         Show this help

init options:
  --plan <file>            Path to plan file (required)
  --mode <m>               "static" (default) or "alternating"
  --reviewer-model <m>     Reviewer model (static mode, required)
  --planner-model <m>      Planner model (static mode, required)
  --model-a <m>            Model A — writes first, reviews second (alternating mode)
  --model-b <m>            Model B — reviews first, writes second (alternating mode)
  --project-context <s>    Brief project context for reviewer calibration
  --out <dir>              Output base directory (default: tasks/reviews)
  --max-rounds <n>         Maximum rounds (default: 5 static, 8 alternating)
  --token-budget <n>       Token budget for codebase context (default: 8000)

parse-round options:
  --workspace <dir>        Path to review workspace (required)
  --round <n>              Round number (required)
  --response <file>        Path to raw reviewer response file (required)

finalize options:
  --workspace <dir>        Path to review workspace (required)
  --override-reason <s>    Reason for force-approving with open issues (min 10 chars)
  --ci-force               Required in non-TTY mode when using --override-reason

status options:
  --workspace <dir>        Path to review workspace (required)

next-step options:
  --workspace <dir>        Path to review workspace (required)

save-plan options:
  --workspace <dir>        Path to review workspace (required)
  --plan <file>            Path to revised plan file (required)
  --version <n>            Plan version number (required, e.g. 2, 3, 4)

Exit codes:
  0   Approved / OK
  1   Revise / Unapproved
  2   Error (parse failure, bad flags, etc.)

Examples:
  node review.js init --plan /tmp/plan.md --reviewer-model openai/gpt-4 --planner-model anthropic/claude-sonnet-4-6
  node review.js init --plan "/tmp/my plan.md" --reviewer-model openai/gpt-4 --planner-model anthropic/claude-sonnet-4-6 --max-rounds 3 --token-budget 4000
  node review.js parse-round --workspace tasks/reviews/2025-01-01T00-00-00-abc123 --round 1 --response /tmp/resp.json
  node review.js finalize --workspace tasks/reviews/2025-01-01T00-00-00-abc123
  node review.js status --workspace tasks/reviews/2025-01-01T00-00-00-abc123
`.trim();
  console.log(text);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);
  const cmd  = args._[0];

  if (!cmd || args['help']) {
    printHelp();
    process.exit(0);
  }

  let exitCode;
  switch (cmd) {
    case 'init':        exitCode = cmdInit(args); break;
    case 'parse-round': exitCode = cmdParseRound(args); break;
    case 'finalize':    exitCode = cmdFinalize(args); break;
    case 'status':      exitCode = cmdStatus(args); break;
    case 'next-step':   exitCode = cmdNextStep(args); break;
    case 'save-plan':   exitCode = cmdSavePlan(args); break;
    default:
      console.error(`Unknown command: ${cmd}`);
      printHelp();
      process.exit(2);
  }

  process.exit(exitCode || 0);
}

main();
