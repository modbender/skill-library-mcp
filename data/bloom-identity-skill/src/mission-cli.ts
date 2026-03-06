/**
 * Bloom Mission Skill - CLI Entry Point
 *
 * OpenClaw skill wrapper for bloom-mission-skill
 *
 * Usage:
 *   npx tsx src/mission-cli.ts --wallet <addr>                    # basic
 *   npx tsx src/mission-cli.ts --wallet <addr> --agent-id 12345   # with taste matching
 *   npx tsx src/mission-cli.ts --wallet <addr> --status           # check submissions
 */

import 'dotenv/config';
import { Command } from 'commander';
import { BloomMissionSkill } from './bloom-mission-skill';

const program = new Command();

program
  .name('bloom-missions')
  .description('Discover and track Bloom Protocol missions')
  .version('2.0.0')
  .requiredOption('--wallet <address>', 'Agent wallet address for heartbeat')
  .option('--context <text>', 'Conversation context for personalization')
  .option('--agent-id <id>', 'Agent user ID for taste-profile matching')
  .option('--status', 'Check submission status instead of discovering missions')
  .option('--agent-name <name>', 'Agent name (used for submission status)')
  .parse(process.argv);

const options = program.opts();

async function main() {
  try {
    const skill = new BloomMissionSkill();

    // Status check mode
    if (options.status) {
      const agentName = options.agentName || `agent-${options.wallet.slice(0, 8)}`;
      const result = await skill.checkSubmissionStatus(agentName);

      if (!result.success) {
        console.error('Failed to check submission status');
        process.exit(1);
      }

      const data = result.data;
      console.log(`Submission Status for ${data?.agentId}`);
      console.log('='.repeat(40));
      console.log(`Total: ${data?.total || 0} submissions`);
      console.log('');

      for (const sub of data?.submissions || []) {
        console.log(`  Mission: ${sub.missionId}`);
        console.log(`  Status: ${sub.status}`);
        console.log(`  Submitted: ${sub.submittedAt}`);
        if (sub.dropsStatus) console.log(`  Drops: ${JSON.stringify(sub.dropsStatus)}`);
        if (sub.tokenStatus) console.log(`  Tokens: ${JSON.stringify(sub.tokenStatus)}`);
        console.log('');
      }
      return;
    }

    // Discovery mode (default)
    const agentUserId = options.agentId ? parseInt(options.agentId) : undefined;
    const result = await skill.execute(options.wallet, options.context, agentUserId);

    console.log(result.formattedOutput);

    if (!result.success) {
      console.error(`Error: ${result.error}`);
      process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

main();
