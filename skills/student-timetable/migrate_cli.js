#!/usr/bin/env node

const { resolveWorkspaceRoot } = require('./workspace_root.js');
const { migrateKidSchedule, migrateLegacyZian } = require('./migrate.js');

function usage() {
  process.stdout.write('student-timetable migrate\n');
  process.stdout.write('Usage:\n');
  process.stdout.write('  node skills/student-timetable/migrate_cli.js kid-schedule [--dry-run]\n');
  process.stdout.write('  node skills/student-timetable/migrate_cli.js legacy-zian [--dry-run]\n');
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') args.dryRun = true;
    else args._.push(a);
  }
  return args;
}

(async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];
  if (!cmd) {
    usage();
    process.exit(1);
  }

  const workspaceRoot = resolveWorkspaceRoot();
  let report;
  if (cmd === 'kid-schedule') {
    report = migrateKidSchedule(workspaceRoot, { dryRun: !!args.dryRun });
  } else if (cmd === 'legacy-zian') {
    report = migrateLegacyZian(workspaceRoot, { dryRun: !!args.dryRun });
  } else {
    usage();
    process.exit(1);
  }

  process.stdout.write(JSON.stringify(report, null, 2) + '\n');
})();
