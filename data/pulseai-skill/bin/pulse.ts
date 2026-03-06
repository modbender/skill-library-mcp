#!/usr/bin/env node
import { Command } from 'commander';
import { setJsonMode } from '../src/lib/output.js';
import { browseCommand } from '../src/commands/browse.js';
import { agentCommand } from '../src/commands/agent.js';
import { jobCommand } from '../src/commands/job.js';
import { sellCommand } from '../src/commands/sell.js';
import { walletCommand } from '../src/commands/wallet.js';
import { serveCommand } from '../src/commands/serve.js';

const program = new Command()
  .name('pulse')
  .description('Pulse — Agent-to-agent commerce on MegaETH')
  .version('0.1.0');

// Register commands
program.addCommand(browseCommand);
program.addCommand(agentCommand);
program.addCommand(jobCommand);
program.addCommand(sellCommand);
program.addCommand(walletCommand);
program.addCommand(serveCommand);

// Set JSON mode from --json option on any command/subcommand
function installJsonHook(cmd: Command) {
  cmd.hook('preAction', (thisCommand) => {
    if (thisCommand.opts().json) setJsonMode(true);
  });
  for (const sub of cmd.commands) {
    installJsonHook(sub);
  }
}
installJsonHook(program);

program.parse();
