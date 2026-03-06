#!/usr/bin/env node
/**
 * install.js - OpenClaw Quickstart One-Click Installer
 *
 * Sets up everything needed for the onboarding experience:
 *   1. Injects quickstart check into HEARTBEAT.md (every 30min auto-detect)
 *   2. Creates quickstart-reminder cron (daily 9 AM push notification)
 *
 * Usage:
 *   node install.js [--workspace /path] [--hour 9] [--minute 0] [--dry-run]
 *
 * Options:
 *   --workspace <path>  Workspace directory (default: ~/.openclaw/workspace)
 *   --hour <n>          Hour for daily reminder (default: 9)
 *   --minute <n>        Minute for daily reminder (default: 0)
 *   --dry-run           Preview changes without writing anything
 */

const fs        = require('fs');
const path      = require('path');
const { spawnSync } = require('child_process');

// ── Args ──────────────────────────────────────────────────────────────────────
const args      = process.argv.slice(2);
const wsIdx     = args.indexOf('--workspace');
const workspace = wsIdx !== -1 ? args[wsIdx + 1] : path.join(process.env.HOME, '.openclaw', 'workspace');
const hourIdx   = args.indexOf('--hour');
const hour      = hourIdx !== -1 ? parseInt(args[hourIdx + 1], 10) : 9;
const minIdx    = args.indexOf('--minute');
const minute    = minIdx !== -1 ? parseInt(args[minIdx + 1], 10) : 0;
const dryRun    = args.includes('--dry-run');

const scriptsDir = path.resolve(__dirname);

console.log(`\n🦐 OpenClaw Quickstart Installer`);
console.log(`   Workspace: ${workspace}`);
console.log(`   Daily reminder: ${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')}`);
if (dryRun) console.log(`   Mode: DRY RUN (no changes will be made)\n`);
else console.log('');

let allOk = true;

// ── Step 1: HEARTBEAT.md ──────────────────────────────────────────────────────
const heartbeatFile = path.join(workspace, 'HEARTBEAT.md');
const heartbeatBlock = `
## OpenClaw Quickstart Progress Check

Run the following and parse the JSON output:
\`\`\`
node ${scriptsDir}/check_progress.js --workspace ${workspace} --mark-done
\`\`\`

- If \`all_done\` is true:
  1. Run \`node ${scriptsDir}/cleanup_crons.js\` to remove all quickstart crons
  2. Remove the quickstart block from HEARTBEAT.md (delete lines between "## OpenClaw Quickstart" and "## End OpenClaw Quickstart")
  3. Send the user this message: "🎓 恭喜！你已完成全部 8 个新手任务，OpenClaw 你玩明白了！（提醒已自动关闭）"
- If \`newly_completed\` has entries: send "✅ 新手任务更新：任务[N]「任务名」已自动标记完成！"
- Otherwise: stay silent (HEARTBEAT_OK)

## End OpenClaw Quickstart
`;

console.log('📝 Step 1: Updating HEARTBEAT.md...');

let heartbeatContent = '';
try { heartbeatContent = fs.readFileSync(heartbeatFile, 'utf8'); } catch {}

const alreadyInstalled = heartbeatContent.includes('## OpenClaw Quickstart Progress Check');

if (alreadyInstalled) {
  console.log('   ℹ️  Quickstart block already present in HEARTBEAT.md, skipping.\n');
} else {
  const newContent = heartbeatContent.trimEnd() + '\n' + heartbeatBlock;
  if (dryRun) {
    console.log('   [DRY RUN] Would append to HEARTBEAT.md:');
    console.log(heartbeatBlock.split('\n').map(l => '   | ' + l).join('\n'));
  } else {
    try {
      fs.writeFileSync(heartbeatFile, newContent, 'utf8');
      console.log('   ✅ HEARTBEAT.md updated\n');
    } catch (e) {
      console.error(`   ⚠️  Failed to write HEARTBEAT.md: ${e.message}\n`);
      allOk = false;
    }
  }
}

// ── Step 2: Daily Reminder Cron ───────────────────────────────────────────────
console.log('⏰ Step 2: Creating daily reminder cron (quickstart-reminder)...');

// Check if cron already exists
function openclaw(...cmdArgs) {
  const result = spawnSync('openclaw', cmdArgs, { encoding: 'utf8' });
  if (result.error?.code === 'ENOENT') return { error: 'not-found' };
  const raw = result.stdout || '';
  const start = raw.split('\n').findIndex(l => l.trimStart().startsWith('{'));
  if (start === -1) return { raw, status: result.status };
  try { return { data: JSON.parse(raw.split('\n').slice(start).join('\n')), status: result.status }; }
  catch { return { raw, status: result.status }; }
}

const listResult = openclaw('cron', 'list', '--json');
if (listResult.error === 'not-found') {
  console.error('   ⚠️  openclaw CLI not found. Please run setup_reminder_cron.js manually.\n');
  allOk = false;
} else {
  const jobs = listResult.data?.jobs || [];
  const existing = jobs.find(j => j.name === 'quickstart-reminder');

  if (existing) {
    console.log(`   ℹ️  Cron "quickstart-reminder" already exists (id: ${existing.id}), skipping.\n`);
  } else {
    const reminderTask = [
      `Run: node ${scriptsDir}/check_progress.js --workspace ${workspace}`,
      'Parse the JSON output.',
      'If all_done is true: run cleanup_crons.js, remove quickstart block from HEARTBEAT.md, send 🎓 graduation message.',
      'Otherwise: send a friendly reminder listing ✅ completed and ⬜ pending tasks, highlight next_task, encourage user to complete it.',
    ].join(' ');

    if (dryRun) {
      console.log(`   [DRY RUN] Would create cron: quickstart-reminder @ ${minute} ${hour} * * *\n`);
    } else {
      const addResult = openclaw(
        'cron', 'add',
        '--name', 'quickstart-reminder',
        '--cron', `${minute} ${hour} * * *`,
        '--tz', 'Asia/Shanghai',
        '--announce',
        '--message', reminderTask,
        '--json'
      );

      if (addResult.data?.id) {
        console.log(`   ✅ Created "quickstart-reminder" (id: ${addResult.data.id})\n`);
      } else {
        console.warn(`   ⚠️  Unexpected response:`, JSON.stringify(addResult.data || addResult.raw || '').slice(0, 200));
        allOk = false;
      }
    }
  }
}

// ── Step 3: Summary ───────────────────────────────────────────────────────────
console.log('─'.repeat(50));
if (dryRun) {
  console.log('✅ Dry run complete. Re-run without --dry-run to apply.\n');
} else if (allOk) {
  console.log(`✅ Installation complete!

   What's set up:
   🫀 Heartbeat (every 30min): auto-detects task completions, marks done, graduates when all done
   ⏰ Daily Cron (${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')} CST): reminds you of pending tasks each morning

   When all 8 tasks are done, both will automatically shut down. 🎓
`);
} else {
  console.log('⚠️  Installation completed with some warnings. Check the output above.\n');
}
