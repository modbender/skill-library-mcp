import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFileCallback);

export interface ExecResult {
  stdout: string;
  stderr: string;
}

const ALLOWED_COMMANDS = new Set([
  'git',
  'curl',
  'tar',
  'clawhub',
]);

const COMMAND_TIMEOUTS: Record<string, number> = {
  git: 60_000,
  curl: 30_000,
  tar: 10_000,
  clawhub: 60_000,
};

export async function execSafe(
  command: string,
  args: string[],
  opts: { cwd?: string; timeout?: number } = {},
): Promise<ExecResult> {
  if (!ALLOWED_COMMANDS.has(command)) {
    throw new Error(`Command "${command}" is not permitted`);
  }

  for (const arg of args) {
    // Block shell metacharacters in all arguments (even flags)
    // Note: execFile doesn't invoke a shell, so these wouldn't be interpreted,
    // but we block them anyway as defense-in-depth and to catch malformed input
    if (/[;&|`$(){}[\]<>]/.test(arg)) {
      throw new Error(`Argument contains shell metacharacters: "${arg.substring(0, 20)}"`);
    }
    // Block null bytes which could cause truncation issues
    if (arg.includes('\0')) {
      throw new Error('Argument contains null byte');
    }
  }

  const timeout = opts.timeout ?? COMMAND_TIMEOUTS[command] ?? 30_000;

  try {
    const result = await execFileAsync(command, args, {
      cwd: opts.cwd,
      timeout,
      maxBuffer: 10 * 1024 * 1024,
      env: {
        PATH: process.platform === 'win32'
          ? process.env['PATH'] ?? ''
          : '/usr/local/bin:/usr/bin:/bin',
        HOME: process.env['HOME'] ?? process.env['USERPROFILE'] ?? '',
        LANG: process.env['LANG'] ?? 'en_US.UTF-8',
      },
    });

    return {
      stdout: result.stdout?.toString() ?? '',
      stderr: result.stderr?.toString() ?? '',
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    throw new Error(`Command "${command}" failed: ${message}`);
  }
}
