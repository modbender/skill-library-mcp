#!/usr/bin/env node
import { execa } from 'execa';

// Wrapper around planka-cli that returns JSON for whoami.
// This keeps the adapter CLI-auth compliant while avoiding brittle parsing in TS.

const bin = process.env.PLANKA_CLI_BIN || 'planka-cli';

async function main() {
  const { stdout } = await execa(bin, ['status'], { stdout: 'pipe', stderr: 'pipe' });
  const text = String(stdout || '').trim();

  // Best-effort parsing for voydz/planka-cli output.
  // Typical output includes a line like:
  //   User: Jane Doe (jane@example.com)
  // or:
  //   Logged in as: Jane Doe
  const line = text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .find((l) => /^user:/i.test(l) || /logged in as/i.test(l));

  const name = line ? line.replace(/^user:/i, '').replace(/^logged in as:/i, '').trim() : undefined;

  process.stdout.write(`${JSON.stringify({ name }, null, 2)}\n`);
}

main().catch((err) => {
  process.stderr.write(`${err?.message ?? String(err)}\n`);
  process.exit(1);
});
