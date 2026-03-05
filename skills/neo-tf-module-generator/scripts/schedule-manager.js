#!/usr/bin/env node
/**
 * Schedule Manager for Terraform Module Generator
 *
 * Usage: node schedule-manager.js <command> [options]
 *
 * Commands:
 *   list [--json]                       List scheduled jobs
 *   add <provider> <output> <resources...> [options]
 *                                      Add a new scheduled job
 *   remove <job-id>                     Remove a scheduled job
 *   enable <job-id>                      Enable a job
 *   disable <job-id>                     Disable a job
 *   run <job-id>                        Run a job immediately
 *
 * Add options:
 *   --cron "<cron expr>"                Cron expression (e.g. "0 2 * * *")
 *   --every <duration>                  Interval (e.g. "10m", "1h")
 *   --region <region>                   Region (optional)
 *   --name <name>                       Job name
 *   --description <text>                Description
 *   --agent <agent-id>                  Agent ID (default: tf-module-generator)
 *   --session <target>                  Session target: isolated or main (default: isolated)
 *   --model <model>                     Model override for agent jobs
 *   --thinking <level>                  Thinking level (off|minimal|low|medium|high)
 *
 * This script wraps OpenClaw's cron facility to schedule module generation jobs.
 */

const { execFile } = require('child_process');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Run an openclaw cron command via execFile to avoid shell quoting issues
function execOpenClaw(argsArray, opts = {}) {
  return new Promise((resolve, reject) => {
    execFile('openclaw', ['cron', ...argsArray], { ...opts, maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
      if (err) {
        reject(new Error(stderr || err.message));
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

// Command implementations
async function runList(args) {
  try {
    const { stdout } = await execOpenClaw(['list', '--json']);
    const jobs = JSON.parse(stdout);
    if (args.json) {
      console.log(stdout);
    } else {
      console.log('Scheduled jobs:');
      if (jobs.length === 0) {
        console.log('  (none)');
      } else {
        jobs.forEach(job => {
          console.log(`  ${job.id} | ${job.name || '(no name)'} | ${job.cron || job.every || 'one-shot'} | ${job.enabled ? 'enabled' : 'disabled'}`);
          console.log(`    Agent: ${job.agent || 'default'} | Next: ${job.nextRun || 'N/A'} | Last: ${job.lastRun || 'never'}`);
        });
      }
    }
  } catch (err) {
    console.error('Error listing jobs:', err.message);
    process.exit(1);
  }
}

async function runAdd(args) {
  const { provider, output, resources, region, cron, every, name, description, agent, session, model, thinking } = args;

  if (!cron && !every) {
    console.error('Error: must specify either --cron or --every');
    process.exit(1);
  }
  if (cron && every) {
    console.error('Error: --cron and --every are mutually exclusive');
    process.exit(1);
  }

  // Build payload for agent
  const payload = {
    task: 'generate-module',
    arguments: {
      provider,
      resources,
      output,
      region: region || undefined
    }
  };

  const message = JSON.stringify(payload);

  // Build argument array for openclaw cron add
  const cliArgs = ['cron', 'add'];
  cliArgs.push('--agent', agent || 'tf-module-generator');
  cliArgs.push('--message', message);
  cliArgs.push('--session', session || 'isolated');
  if (name) cliArgs.push('--name', name);
  if (description) cliArgs.push('--description', description);
  if (cron) cliArgs.push('--cron', cron);
  if (every) cliArgs.push('--every', every);
  if (model) cliArgs.push('--model', model);
  if (thinking) cliArgs.push('--thinking', thinking);
  // By default, no announce (--no-deliver is optional; default false is fine)

  try {
    const { stdout } = await execOpenClaw(cliArgs);
    const jobId = stdout.trim();
    console.log(`Scheduled job created: ${jobId}`);
  } catch (err) {
    console.error('Error adding job:', err.message);
    process.exit(1);
  }
}

async function runRemove(args) {
  try {
    await execOpenClaw(['rm', args.jobId]);
    console.log(`Removed job ${args.jobId}`);
  } catch (err) {
    console.error('Error removing job:', err.message);
    process.exit(1);
  }
}

async function runEnable(args) {
  try {
    await execOpenClaw(['enable', args.jobId]);
    console.log(`Enabled job ${args.jobId}`);
  } catch (err) {
    console.error('Error enabling job:', err.message);
    process.exit(1);
  }
}

async function runDisable(args) {
  try {
    await execOpenClaw(['disable', args.jobId]);
    console.log(`Disabled job ${args.jobId}`);
  } catch (err) {
    console.error('Error disabling job:', err.message);
    process.exit(1);
  }
}

async function runRun(args) {
  try {
    const { stdout } = await execOpenClaw(['run', args.jobId]);
    console.log(`Job ${args.jobId} executed:`);
    console.log(stdout);
  } catch (err) {
    console.error('Error running job:', err.message);
    process.exit(1);
  }
}

// Yargs command setup
yargs(hideBin(process.argv))
  .command('list [json]', 'List scheduled jobs', (y) => {
    return y.option('json', { type: 'boolean', description: 'Output as JSON' });
  }, runList)
  .command('add <provider> <output> <resources...>', 'Add a scheduled job', (y) => {
    return y
      .positional('provider', { type: 'string', choices: ['aws','azure','gcp'] })
      .positional('output', { type: 'string', describe: 'Output directory' })
      .positional('resources', { type: 'string', describe: 'Resource types to scan' })
      .option('region', { type: 'string', description: 'Cloud region' })
      .option('cron', { type: 'string', description: 'Cron expression' })
      .option('every', { type: 'string', description: 'Interval duration (e.g. 10m, 1h)' })
      .option('name', { type: 'string', description: 'Job name' })
      .option('description', { type: 'string', description: 'Job description' })
      .option('agent', { type: 'string', default: 'tf-module-generator', description: 'Agent ID' })
      .option('session', { type: 'string', default: 'isolated', description: 'Session target (isolated or main)' })
      .option('model', { type: 'string', description: 'Model override' })
      .option('thinking', { type: 'string', description: 'Thinking level (off|minimal|low|medium|high)' });
  }, runAdd)
  .command('remove <jobId>', 'Remove a scheduled job', (y) => {
    return y.positional('jobId', { type: 'string', describe: 'Job ID to remove' });
  }, runRemove)
  .command('enable <jobId>', 'Enable a job', (y) => {
    return y.positional('jobId', { type: 'string' });
  }, runEnable)
  .command('disable <jobId>', 'Disable a job', (y) => {
    return y.positional('jobId', { type: 'string' });
  }, runDisable)
  .command('run <jobId>', 'Run a job immediately', (y) => {
    return y.positional('jobId', { type: 'string' });
  }, runRun)
  .demandCommand(1, 'Command required')
  .help()
  .argv;
