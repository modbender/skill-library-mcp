#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = {};
  for (const a of argv.slice(2)) {
    if (!a.startsWith('--')) continue;
    const idx = a.indexOf('=');
    if (idx === -1) {
      out[a.slice(2)] = true;
      continue;
    }
    out[a.slice(2, idx)] = a.slice(idx + 1);
  }
  return out;
}

function toAbs(input, cwd) {
  const v = String(input || '').trim();
  if (!v) return '';
  return path.isAbsolute(v) ? v : path.resolve(cwd, v);
}

function main() {
  const args = parseArgs(process.argv);
  const skillDir = __dirname;
  const workspaceSkillsDir = path.resolve(skillDir, '..');
  const capabilityDir = path.join(workspaceSkillsDir, 'capability-evolver');
  const defaultReport = path.join(capabilityDir, 'assets', 'gep', 'hle_report.template.json');
  const reportPath = toAbs(args.report || args.file || defaultReport, process.cwd());
  const outFile = args.out ? toAbs(args.out, process.cwd()) : null;

  if (!fs.existsSync(reportPath)) {
    console.error(`[HLE_RESULT] report not found: ${reportPath}`);
    process.exit(2);
  }

  const modPath = path.join(capabilityDir, 'src', 'gep', 'benchmarkReward.js');
  if (!fs.existsSync(modPath)) {
    console.error(`[HLE_RESULT] benchmarkReward module not found: ${modPath}`);
    process.exit(2);
  }

  const reward = require(modPath);
  let report;
  try {
    report = reward.parseBenchmarkReportFile(reportPath);
  } catch (e) {
    console.error(`[HLE_RESULT] invalid report JSON: ${e && e.message ? e.message : e}`);
    process.exit(2);
  }

  const ingested = reward.ingestBenchmarkReport(report);
  const state = ingested && ingested.state ? ingested.state : reward.readState();
  const latest = state && state.latest_run ? state.latest_run : {};
  const curriculum = state && state.curriculum ? state.curriculum : {};

  const summary = {
    benchmark_id: state && state.benchmark_id ? state.benchmark_id : null,
    run_id: latest && latest.run_id ? latest.run_id : null,
    accuracy: Number.isFinite(Number(latest.accuracy)) ? Number(latest.accuracy) : null,
    reward:
      state && state.reward && Number.isFinite(Number(state.reward.latest))
        ? Number(state.reward.latest)
        : null,
    trend: state && state.reward ? state.reward.trend || 'stable' : 'stable',
    curriculum_stage: curriculum && curriculum.stage ? curriculum.stage : 'easy',
    queue_size: Array.isArray(curriculum.queue) ? curriculum.queue.length : 0,
    focus_subjects: Array.isArray(curriculum.focus_subjects) ? curriculum.focus_subjects.slice(0, 5) : [],
    focus_modalities: Array.isArray(curriculum.focus_modalities) ? curriculum.focus_modalities.slice(0, 3) : [],
    next_questions: Array.isArray(curriculum.next_questions) ? curriculum.next_questions.slice(0, 10) : [],
    state_path: reward.getStatePath(),
    report_path: reportPath,
  };

  console.log('[HLE_RESULT] OK');
  console.log(JSON.stringify(summary, null, 2));

  if (outFile) {
    fs.writeFileSync(outFile, JSON.stringify(summary, null, 2));
    console.log(`[HLE_RESULT] wrote output to: ${outFile}`);
  }
}

main();
