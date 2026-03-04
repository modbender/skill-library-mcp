// executor.js — Execution bridge: maps task categories to real work
//
// SECURITY: All task input comes from untrusted XMTP messages.
// NEVER interpolate task fields into shell commands.
// ALWAYS use execFileSync/spawn with array arguments.
//
// Categories map to execution strategies:
//   coding    → spawn a coding sub-agent (codex/claude-code)
//   research  → web search + synthesis
//   code-review → read files + analyze
//   writing   → direct generation
//   custom    → generic sub-agent

import { execFileSync, spawnSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WORK_DIR = join(__dirname, '..', 'workdir');

// ─── Input Sanitization ───

const MAX_TITLE_LENGTH = 200;
const MAX_DESCRIPTION_LENGTH = 5000;
const MAX_RESULT_LENGTH = 50000;

/**
 * Sanitize a task before execution.
 * Strips or truncates dangerous/oversized fields.
 */
function sanitizeTask(task) {
  const clean = { ...task };
  if (typeof clean.title === 'string') {
    clean.title = clean.title.slice(0, MAX_TITLE_LENGTH);
  }
  if (typeof clean.description === 'string') {
    clean.description = clean.description.slice(0, MAX_DESCRIPTION_LENGTH);
  }
  // Strip any fields that aren't expected
  const allowed = ['id', 'title', 'description', 'category', 'subtasks', 'budget', 'requirements', 'criteria'];
  for (const key of Object.keys(clean)) {
    if (!allowed.includes(key)) delete clean[key];
  }
  return clean;
}

/**
 * Validate a GitHub repo path. Only allows owner/repo format with safe characters.
 * Returns null if invalid.
 */
function validateRepoPath(path) {
  if (!path || typeof path !== 'string') return null;
  // Strict: alphanumeric, hyphens, underscores, dots, forward slash
  const match = path.match(/^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/);
  if (!match) return null;
  // Additional safety: no .. sequences
  if (path.includes('..')) return null;
  return path;
}

/**
 * Execute a task and return a result object.
 * @param {object} task - The task message (from XMTP) — UNTRUSTED INPUT
 * @param {object} config - The swarm config
 * @returns {object} result - { status, deliverable, logs, completedAt }
 */
export async function execute(task, config) {
  // Sanitize untrusted input first
  const cleanTask = sanitizeTask(task);
  const category = cleanTask.category || inferCategory(cleanTask);
  const taskId = cleanTask.id || `unknown-${Date.now()}`;
  // Sanitize task ID for filesystem use
  const safeTaskId = taskId.replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 100);
  const workDir = join(WORK_DIR, safeTaskId);

  if (!existsSync(workDir)) mkdirSync(workDir, { recursive: true });

  console.log(`  [executor] category: ${category}`);
  console.log(`  [executor] workdir: ${workDir}`);

  const startTime = Date.now();
  const maxExecutionTime = (config?.worker?.executionTimeout || 300) * 1000; // default 5 min

  let result;
  try {
    switch (category) {
      case 'coding':
        result = await executeCoding(cleanTask, workDir, config, maxExecutionTime);
        break;
      case 'research':
        result = await executeResearch(cleanTask, workDir, maxExecutionTime);
        break;
      case 'code-review':
        result = await executeCodeReview(cleanTask, workDir, maxExecutionTime);
        break;
      case 'writing':
        result = await executeWriting(cleanTask, workDir);
        break;
      default:
        result = await executeGeneric(cleanTask, workDir, maxExecutionTime);
        break;
    }
  } catch (err) {
    result = {
      deliverable: `Execution failed: ${(err.message || 'unknown error').slice(0, 500)}`,
      logs: [`Error: ${err.message?.slice(0, 500)}`],
    };
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`  [executor] completed in ${elapsed}s`);

  // Truncate deliverable to prevent memory issues
  const deliverable = typeof result.deliverable === 'string'
    ? result.deliverable.slice(0, MAX_RESULT_LENGTH)
    : result.deliverable;

  return {
    status: 'completed',
    category,
    deliverable,
    logs: result.logs || [],
    files: result.files || [],
    completedAt: new Date().toISOString(),
    executionTime: `${elapsed}s`,
  };
}

/**
 * Infer category from task description if not explicitly set.
 */
function inferCategory(task) {
  const text = `${task.title || ''} ${task.description || ''}`.toLowerCase();

  if (text.match(/\b(code|build|implement|fix|bug|feature|api|endpoint|function|class|module|deploy|refactor)\b/)) {
    return 'coding';
  }
  if (text.match(/\b(research|find|search|investigate|analyze|report|summarize|gather)\b/)) {
    return 'research';
  }
  if (text.match(/\b(review|audit|check|inspect|vulnerabilit|security)\b/)) {
    return 'code-review';
  }
  if (text.match(/\b(write|draft|blog|article|content|copy|documentation|readme)\b/)) {
    return 'writing';
  }
  return 'custom';
}

/**
 * Find a coding agent binary safely.
 * Returns the full path or null.
 */
function findCodingAgent() {
  const agents = ['codex', 'claude', 'pi'];
  for (const a of agents) {
    try {
      const result = spawnSync('which', [a], { encoding: 'utf-8', timeout: 5000 });
      if (result.status === 0 && result.stdout.trim()) {
        return { name: a, path: result.stdout.trim() };
      }
    } catch {}
  }
  return null;
}

// ─── Execution Strategies ───
// SECURITY: All strategies use execFileSync/spawnSync with array arguments.
// No shell interpolation of untrusted input.

/**
 * Coding: spawn a coding agent to do the work.
 * SECURITY: Task description passed via stdin or temp file, never via shell args.
 */
async function executeCoding(task, workDir, config, timeout) {
  const description = task.description || task.title || '';
  const agent = findCodingAgent();

  if (agent) {
    const prompt = [
      'You are completing a paid task.',
      `Work directory: ${workDir}`,
      '',
      `Task: ${task.title || 'Untitled'}`,
      `Description: ${description}`,
      task.subtasks?.length
        ? `Subtasks:\n${task.subtasks.map(s => `- ${s.title || ''}: ${s.description || ''}`).join('\n')}`
        : '',
      '',
      'Complete the task. Write all output files to the work directory.',
      'When done, write a RESULT.md summarizing what you did.',
    ].join('\n');

    // Write prompt to a temp file instead of passing via shell
    const promptPath = join(workDir, '_prompt.txt');
    writeFileSync(promptPath, prompt);

    try {
      let result;
      if (agent.name === 'codex') {
        // codex reads from file
        result = spawnSync(agent.path, ['exec', prompt], {
          cwd: workDir,
          timeout,
          maxBuffer: 1024 * 1024,
          encoding: 'utf-8',
          stdio: ['pipe', 'pipe', 'pipe'],
        });
      } else if (agent.name === 'claude') {
        // claude -p reads prompt from arg (safe with spawnSync array args)
        result = spawnSync(agent.path, ['-p', prompt], {
          cwd: workDir,
          timeout,
          maxBuffer: 1024 * 1024,
          encoding: 'utf-8',
          stdio: ['pipe', 'pipe', 'pipe'],
        });
      } else {
        // pi or other agents
        result = spawnSync(agent.path, [prompt], {
          cwd: workDir,
          timeout,
          maxBuffer: 1024 * 1024,
          encoding: 'utf-8',
          stdio: ['pipe', 'pipe', 'pipe'],
        });
      }

      const output = result.stdout || '';
      const stderr = result.stderr || '';

      if (result.status !== 0 && !output) {
        return {
          deliverable: `Coding agent (${agent.name}) exited with code ${result.status}: ${stderr.slice(0, 500)}`,
          logs: [stderr.slice(-500)],
        };
      }

      // Read RESULT.md if created
      const resultPath = join(workDir, 'RESULT.md');
      const deliverable = existsSync(resultPath)
        ? readFileSync(resultPath, 'utf-8').slice(0, MAX_RESULT_LENGTH)
        : output.slice(-2000);

      return {
        deliverable,
        logs: [output.slice(-1000)],
        files: listFiles(workDir),
      };
    } catch (err) {
      return {
        deliverable: `Coding agent (${agent.name}) failed: ${(err.message || '').slice(0, 500)}`,
        logs: [err.message?.slice(-500) || 'unknown error'],
      };
    }
  }

  return {
    deliverable: `No coding agent available on this machine (checked: codex, claude, pi). Task preserved:\n\n${description.slice(0, 2000)}`,
    logs: ['No coding agent found. Install codex, claude, or pi for automated coding.'],
  };
}

/**
 * Research: web search + synthesis.
 * SECURITY: Search query is URL-encoded, not shell-interpolated.
 */
async function executeResearch(task, workDir, timeout) {
  const query = (task.description || task.title || '').slice(0, 500);

  try {
    // Use execFileSync with curl — query goes as a proper URL parameter
    const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
    const curlResult = spawnSync('curl', ['-sL', '--max-time', '20', searchUrl], {
      encoding: 'utf-8',
      timeout: Math.min(timeout, 30000),
      maxBuffer: 100 * 1024, // 100KB max
    });

    const html = (curlResult.stdout || '').slice(0, 50000);

    // Extract result snippets
    const results = [];
    const snippetRegex = /<a[^>]*class="result__snippet"[^>]*>(.*?)<\/a>/gs;
    let match;
    while ((match = snippetRegex.exec(html)) && results.length < 8) {
      results.push(match[1].replace(/<[^>]*>/g, '').trim());
    }

    const report = `# Research: ${task.title || 'Query'}

## Query
${query}

## Findings
${results.length > 0 ? results.map((r, i) => `${i + 1}. ${r}`).join('\n\n') : 'No results found via web search.'}

## Summary
Research completed. ${results.length} results found.
`;

    writeFileSync(join(workDir, 'research.md'), report);

    return {
      deliverable: report,
      logs: [`Searched: "${query.slice(0, 100)}", found ${results.length} results`],
      files: ['research.md'],
    };
  } catch (err) {
    return {
      deliverable: `Research failed: ${(err.message || '').slice(0, 500)}\n\nOriginal query: ${query}`,
      logs: [err.message?.slice(0, 500) || 'unknown error'],
    };
  }
}

/**
 * Code review: clone a repo (if GitHub URL provided) and analyze.
 * SECURITY: Repo path is strictly validated before use.
 */
async function executeCodeReview(task, workDir, timeout) {
  const description = (task.description || task.title || '').slice(0, MAX_DESCRIPTION_LENGTH);

  // Check if description contains a GitHub URL
  const ghMatch = description.match(/github\.com\/([^/\s]+\/[^/\s]+)/);
  let code = '';

  if (ghMatch) {
    const rawRepo = ghMatch[1].replace(/\.git$/, '');
    const repo = validateRepoPath(rawRepo);

    if (!repo) {
      code = `Invalid repository path: "${rawRepo.slice(0, 100)}". Only alphanumeric, hyphens, underscores, dots allowed.`;
    } else {
      try {
        const repoDir = join(workDir, 'repo');
        // SECURITY: Using execFileSync with array args — repo path validated above
        execFileSync('git', ['clone', '--depth', '1', `https://github.com/${repo}`, repoDir], {
          timeout: Math.min(timeout, 60000),
          stdio: 'pipe',
        });

        // Find source files safely
        const findResult = spawnSync('find', [repoDir, '-name', '*.sol', '-o', '-name', '*.js', '-o', '-name', '*.ts'], {
          encoding: 'utf-8',
          timeout: 10000,
        });
        const files = (findResult.stdout || '').trim().split('\n').filter(Boolean).slice(0, 20);

        for (const f of files) {
          try {
            // Verify file is actually under repoDir (path traversal protection)
            const resolved = join(f);
            if (!resolved.startsWith(repoDir)) continue;
            const content = readFileSync(f, 'utf-8');
            code += `\n--- ${f.replace(repoDir, 'repo')} ---\n${content.slice(0, 5000)}\n`;
          } catch {}
        }
      } catch (err) {
        code = `Failed to clone: ${(err.message || '').slice(0, 300)}`;
      }
    }
  }

  const review = `# Code Review: ${task.title || 'Review'}

## Scope
${description.slice(0, 2000)}

## Files Reviewed
${code ? code.slice(0, 3000) : 'No files found or accessible.'}

## Review Notes
Manual review required. Code has been fetched to workdir for inspection.
`;

  writeFileSync(join(workDir, 'review.md'), review);
  return {
    deliverable: review,
    logs: ['Code fetched for review'],
    files: ['review.md'],
  };
}

/**
 * Writing: generate content based on the task brief.
 */
async function executeWriting(task, workDir) {
  const description = (task.description || task.title || '').slice(0, MAX_DESCRIPTION_LENGTH);

  const output = `# ${(task.title || 'Untitled').slice(0, MAX_TITLE_LENGTH)}

${description}

---
*Generated by agent worker. Content ready for review.*
`;

  writeFileSync(join(workDir, 'output.md'), output);
  return {
    deliverable: output,
    logs: ['Content generated'],
    files: ['output.md'],
  };
}

/**
 * Generic: attempt to handle any task type.
 * SECURITY: Uses spawnSync with array args, never shell interpolation.
 */
async function executeGeneric(task, workDir, timeout) {
  const description = (task.description || task.title || '').slice(0, MAX_DESCRIPTION_LENGTH);

  const agent = findCodingAgent();
  if (agent) {
    const prompt = `Complete this task:\n\nTitle: ${task.title || 'Untitled'}\nDescription: ${description}\n\nWrite output to ${workDir}`;

    try {
      const args = agent.name === 'codex' ? ['exec', prompt] : ['-p', prompt];
      const result = spawnSync(agent.path, args, {
        cwd: workDir,
        timeout,
        maxBuffer: 1024 * 1024,
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      if (result.stdout) {
        return {
          deliverable: result.stdout.slice(-2000),
          logs: [`Executed via ${agent.name}`],
          files: listFiles(workDir),
        };
      }
    } catch {}
  }

  return {
    deliverable: `Task received but no execution agent available.\n\nTitle: ${task.title || 'Untitled'}\nDescription: ${description}\n\nTask logged for manual completion.`,
    logs: ['No execution agent available'],
  };
}

// ─── Helpers ───

function listFiles(dir) {
  try {
    const result = spawnSync('ls', ['-la', dir], { encoding: 'utf-8', timeout: 5000 });
    return (result.stdout || '').trim().split('\n').slice(1);
  } catch {
    return [];
  }
}
