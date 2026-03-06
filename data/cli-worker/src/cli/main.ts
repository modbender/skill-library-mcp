#!/usr/bin/env node

const args = process.argv.slice(2);

function printHelp(): void {
  console.log(`
cli-worker - OpenClaw skill for CLI agents in isolated worktrees

Usage:
  cli-worker <command> [options]

Commands:
  execute <prompt>   Run a task with CLI agent
  status <taskId>    Show task status from report (use --provider if task used claude/opencode)
  verify             Verify CLI agent is installed and authenticated
  worktree list      List active worktrees
  worktree remove <taskId>  Remove a worktree
  cleanup [--older-than N]  Remove worktrees older than N hours (default 24)
  --help, -h         Show this help

Providers:
  The skill supports multiple CLI providers:
  - kimi (default)    Kimi CLI
  - claude            Claude Code (Anthropic)
  - opencode          OpenCode CLI

  Use --provider <id> with execute and verify commands.
  Provider resolution order:
  1. --provider flag
  2. OPENCLAW_CLI_PROVIDER environment variable
  3. openclaw.json config (cliWorker.provider or skills["cli-worker"].provider)
  4. Default: kimi

Examples:
  cli-worker verify
  cli-worker verify --provider claude
  cli-worker execute "Reply OK"
  cli-worker execute "Create hello.py" --constraint "Python 3.11"
  cli-worker execute "Create API" --provider claude --timeout 30
  cli-worker status <taskId>
  cli-worker worktree list
  cli-worker cleanup --older-than 24
`);
}

async function main(): Promise<number> {
  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    printHelp();
    return 0;
  }

  const cmd = args[0];
  const rest = args.slice(1);

  switch (cmd) {
    case "execute": {
      const { runExecute } = await import("../cli/execute.js");
      return runExecute(rest);
    }
    case "status": {
      const { runStatus } = await import("../cli/status.js");
      return runStatus(rest);
    }
    case "verify": {
      // Check if --provider is in the rest args
      let providerFlag: string | undefined;
      const providerIdx = rest.indexOf("--provider");
      if (providerIdx !== -1 && rest[providerIdx + 1]) {
        providerFlag = rest[providerIdx + 1];
      }
      const { runVerify } = await import("../cli/verify.js");
      return runVerify(providerFlag);
    }
    case "worktree": {
      const { runWorktree } = await import("../cli/worktree.js");
      return runWorktree(rest);
    }
    case "cleanup": {
      const { runCleanup } = await import("../cli/cleanup.js");
      return runCleanup(rest);
    }
    default:
      console.error(`Unknown command: ${cmd}`);
      printHelp();
      return 1;
  }
}

main()
  .then((code) => process.exit(code))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
