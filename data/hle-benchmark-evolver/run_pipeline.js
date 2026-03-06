#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function parseArgs(argv) {
  const out = {};
  for (const a of argv.slice(2)) {
    if (!a.startsWith('--')) continue;
    const i = a.indexOf('=');
    if (i === -1) out[a.slice(2)] = true;
    else out[a.slice(2, i)] = a.slice(i + 1);
  }
  return out;
}

function getArg(args, name, fallback) {
  if (Object.prototype.hasOwnProperty.call(args, name)) return args[name];
  const alt = String(name || '').replace(/_/g, '-');
  if (Object.prototype.hasOwnProperty.call(args, alt)) return args[alt];
  const alt2 = String(name || '').replace(/-/g, '_');
  if (Object.prototype.hasOwnProperty.call(args, alt2)) return args[alt2];
  return fallback;
}

function toAbs(input, cwd) {
  const v = String(input || '').trim();
  if (!v) return '';
  return path.isAbsolute(v) ? v : path.resolve(cwd, v);
}

function toInt(value, fallback) {
  const n = parseInt(String(value == null ? '' : value), 10);
  return Number.isFinite(n) ? n : fallback;
}

function sleepMs(ms) {
  const end = Date.now() + Math.max(0, Number(ms) || 0);
  while (Date.now() < end) {}
}

function runNode(args, cwd, extraEnv) {
  const r = spawnSync(process.execPath, args, {
    cwd,
    encoding: 'utf8',
    env: Object.assign({}, process.env, extraEnv || {}),
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  return {
    ok: r.status === 0,
    code: r.status,
    stdout: String(r.stdout || ''),
    stderr: String(r.stderr || ''),
  };
}

function runShell(command, cwd, extraEnv) {
  // Optimization: For simple commands, run directly to avoid file I/O overhead
  if (!command.includes('\n') && !command.includes("'") && command.length < 1000) {
    const r = spawnSync('bash', ['-c', command], {
      cwd,
      encoding: 'utf8',
      env: Object.assign({}, process.env, extraEnv || {}),
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return {
      ok: r.status === 0,
      code: r.status,
      stdout: String(r.stdout || ''),
      stderr: String(r.stderr || ''),
    };
  }

  // Safe execution: Write command to temporary script to avoid argument length limits and quoting issues
  const tmpScript = path.join(cwd, `.hle_exec_${Date.now()}_${Math.random().toString(36).substring(2)}.sh`);
  try {
    fs.writeFileSync(tmpScript, command, { mode: 0o700 });
    const r = spawnSync('bash', ['-l', tmpScript], {
      cwd,
      encoding: 'utf8',
      env: Object.assign({}, process.env, extraEnv || {}),
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return {
      ok: r.status === 0,
      code: r.status,
      stdout: String(r.stdout || ''),
      stderr: String(r.stderr || ''),
    };
  } catch (e) {
    return {
      ok: false,
      code: -1,
      stdout: '',
      stderr: `Script execution error: ${e.message}`,
    };
  } finally {
    if (fs.existsSync(tmpScript)) {
      try { fs.unlinkSync(tmpScript); } catch (e) {}
    }
  }
}

function tailText(text, maxChars) {
  const s = String(text || '');
  if (s.length <= maxChars) return s;
  return s.slice(s.length - maxChars);
}

function main() {
  const args = parseArgs(process.argv);
  const workspaceRoot = process.cwd();
  const skillDir = __dirname;
  const skillsDir = path.resolve(skillDir, '..');
  const capabilityDir = path.join(skillsDir, 'capability-evolver');
  const feishuWrapperDir = path.join(skillsDir, 'feishu-evolver-wrapper');
  
  // Patch: benchmarkReward moved to feishu-evolver-wrapper
  let rewardMod;
  try {
    rewardMod = require(path.join(capabilityDir, 'src', 'gep', 'benchmarkReward.js'));
  } catch (e) {
    rewardMod = require(path.join(feishuWrapperDir, 'src', 'gep', 'benchmarkReward.js'));
  }

  const cycles = Math.max(1, toInt(args.cycles, 1));
  const intervalMs = Math.max(0, toInt(getArg(args, 'interval_ms', getArg(args, 'interval', 0)), 0));
  const evolveEnabled = String(getArg(args, 'skip_evolve', '')).toLowerCase() !== 'true';
  const solidifyEnabled = String(getArg(args, 'skip_solidify', '')).toLowerCase() !== 'true';
  const solidifyDryRun = String(getArg(args, 'solidify_dry_run', 'true')).toLowerCase() !== 'false';
  const reportDefault = path.join(skillDir, 'assets', 'hle_report.sample.json');
  const reportPath = toAbs(getArg(args, 'report', getArg(args, 'file', reportDefault)), workspaceRoot);
  const evalCmdTemplate = String(getArg(args, 'eval_cmd', '')).trim();

  if (!fs.existsSync(reportPath) && !evalCmdTemplate) {
    console.error(`[HLE_PIPELINE] missing report: ${reportPath}`);
    console.error('[HLE_PIPELINE] provide --report=/abs/path.json or --eval_cmd="...{{report}}..."');
    process.exit(2);
  }
  
  // Optimization: Log start of pipeline
  console.log(`[HLE_PIPELINE] Starting ${cycles} cycle(s) with interval ${intervalMs}ms`);
  console.log(`[HLE_PIPELINE] Report path: ${reportPath}`);
  console.log(`[HLE_PIPELINE] Evolve: ${evolveEnabled}, Solidify: ${solidifyEnabled} (DryRun: ${solidifyDryRun})`);

  const runLog = [];
  for (let i = 0; i < cycles; i++) {
    const cycle = i + 1;
    const cycleLog = { cycle, report_path: reportPath };

    if (evalCmdTemplate) {
      const evalCmd = evalCmdTemplate.replace(/\{\{report\}\}/g, reportPath);
      const evalRes = runShell(evalCmd, workspaceRoot, {});
      cycleLog.eval = {
        ok: evalRes.ok,
        code: evalRes.code,
        stdout_tail: tailText(evalRes.stdout, 1600),
        stderr_tail: tailText(evalRes.stderr, 1600),
      };
      if (!evalRes.ok) {
        const combined = `${evalRes.stdout}\n${evalRes.stderr}`;
        if (
          combined.includes('QUOTA_EXHAUSTED_PERSISTENT') ||
          combined.includes('[HLE_EVAL_ACTION_REQUIRED]')
        ) {
          cycleLog.action_required =
            '检测到API配额/额度不足且重试失败。请增加额度后重试本流水线。';
        }
        runLog.push(cycleLog);
        break;
      }
    }

    if (!fs.existsSync(reportPath)) {
      cycleLog.error = `report_not_found_after_eval:${reportPath}`;
      runLog.push(cycleLog);
      break;
    }

    let parsed;
    try {
      parsed = rewardMod.parseBenchmarkReportFile(reportPath);
    } catch (e) {
      cycleLog.error = `report_parse_failed:${e && e.message ? e.message : e}`;
      runLog.push(cycleLog);
      break;
    }
    const ingested = rewardMod.ingestBenchmarkReport(parsed);
    const state = ingested && ingested.state ? ingested.state : rewardMod.readState();
    cycleLog.benchmark = {
      benchmark_id: state && state.benchmark_id ? state.benchmark_id : null,
      run_id: state && state.latest_run ? state.latest_run.run_id : null,
      accuracy: state && state.latest_run ? state.latest_run.accuracy : null,
      reward: state && state.reward ? state.reward.latest : null,
      trend: state && state.reward ? state.reward.trend : null,
      curriculum_stage: state && state.curriculum ? state.curriculum.stage : null,
      queue_size: state && state.curriculum && Array.isArray(state.curriculum.queue)
        ? state.curriculum.queue.length
        : 0,
      next_questions: state && state.curriculum && Array.isArray(state.curriculum.next_questions)
        ? state.curriculum.next_questions.slice(0, 8)
        : [],
    };

    if (evolveEnabled) {
      const evolveRes = runNode(['index.js', 'run'], capabilityDir, {
        EVOLVE_BRIDGE: 'true',
        EVOLVE_PRINT_PROMPT: 'false',
      });
      cycleLog.evolve = {
        ok: evolveRes.ok,
        code: evolveRes.code,
        stdout_tail: tailText(evolveRes.stdout, 1600),
        stderr_tail: tailText(evolveRes.stderr, 1600),
      };
    }

    if (solidifyEnabled) {
      const solidifyArgs = ['index.js', 'solidify', `--benchmark-report=${reportPath}`, '--intent=innovate', '--summary=HLE reward linked evolution cycle'];
      if (solidifyDryRun) solidifyArgs.push('--dry-run');
      const s = runNode(solidifyArgs, capabilityDir, {});
      cycleLog.solidify = {
        ok: s.ok,
        code: s.code,
        mode: solidifyDryRun ? 'dry-run' : 'commit',
        stdout_tail: tailText(s.stdout, 1600),
        stderr_tail: tailText(s.stderr, 1600),
      };
    }

    runLog.push(cycleLog);
    if (intervalMs > 0 && cycle < cycles) sleepMs(intervalMs);
  }

  const finalState = rewardMod.readState();
  const output = {
    ok: runLog.every(x => !x.error && (!x.eval || x.eval.ok !== false)),
    cycles_requested: cycles,
    cycles_finished: runLog.length,
    state_path: rewardMod.getStatePath(),
    final: {
      benchmark_id: finalState && finalState.benchmark_id ? finalState.benchmark_id : null,
      accuracy:
        finalState && finalState.latest_run && Number.isFinite(Number(finalState.latest_run.accuracy))
          ? Number(finalState.latest_run.accuracy)
          : null,
      reward:
        finalState && finalState.reward && Number.isFinite(Number(finalState.reward.latest))
          ? Number(finalState.reward.latest)
          : null,
      trend: finalState && finalState.reward ? finalState.reward.trend || 'stable' : 'stable',
      curriculum_stage:
        finalState && finalState.curriculum && finalState.curriculum.stage
          ? finalState.curriculum.stage
          : 'easy',
      queue_size:
        finalState && finalState.curriculum && Array.isArray(finalState.curriculum.queue)
          ? finalState.curriculum.queue.length
          : 0,
      next_questions:
        finalState && finalState.curriculum && Array.isArray(finalState.curriculum.next_questions)
          ? finalState.curriculum.next_questions.slice(0, 10)
          : [],
    },
    cycles: runLog,
  };

  console.log('[HLE_PIPELINE] DONE');
  console.log(JSON.stringify(output, null, 2));
}

main();
