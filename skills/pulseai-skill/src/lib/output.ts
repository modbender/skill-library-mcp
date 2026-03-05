import chalk from 'chalk';

let jsonMode = false;

export function setJsonMode(enabled: boolean) {
  jsonMode = enabled;
}

export function isJsonMode(): boolean {
  return jsonMode;
}

/** Print data as JSON or formatted table/key-value. */
export function output(data: unknown) {
  if (jsonMode) {
    console.log(JSON.stringify(data, bigintReplacer, 2));
  } else if (Array.isArray(data)) {
    printTable(data);
  } else if (typeof data === 'object' && data !== null) {
    printKeyValue(data as Record<string, unknown>);
  } else {
    console.log(data);
  }
}

export function success(msg: string) {
  if (!jsonMode) {
    console.log(chalk.green('✓') + ' ' + msg);
  }
}

export function error(msg: string): never {
  if (jsonMode) {
    console.error(JSON.stringify({ error: msg }));
  } else {
    console.error(chalk.red('✗') + ' ' + msg);
  }
  process.exit(1);
}

export function info(msg: string) {
  if (!jsonMode) {
    console.log(chalk.blue('ℹ') + ' ' + msg);
  }
}

function printKeyValue(obj: Record<string, unknown>) {
  const maxKey = Math.max(...Object.keys(obj).map((k) => k.length));
  for (const [key, val] of Object.entries(obj)) {
    const label = chalk.bold(key.padEnd(maxKey));
    console.log(`  ${label}  ${formatValue(val)}`);
  }
}

function printTable(rows: Record<string, unknown>[]) {
  if (rows.length === 0) {
    console.log('  (no data)');
    return;
  }
  const keys = Object.keys(rows[0]);
  const widths = keys.map((k) =>
    Math.max(k.length, ...rows.map((r) => String(r[k] ?? '').length)),
  );

  const header = keys.map((k, i) => chalk.bold(k.padEnd(widths[i]))).join('  ');
  console.log('  ' + header);
  console.log('  ' + widths.map((w) => '─'.repeat(w)).join('  '));

  for (const row of rows) {
    const line = keys.map((k, i) => String(row[k] ?? '').padEnd(widths[i])).join('  ');
    console.log('  ' + line);
  }
}

function formatValue(val: unknown): string {
  if (typeof val === 'bigint') return val.toString();
  if (val === undefined || val === null) return chalk.dim('—');
  return String(val);
}

function bigintReplacer(_key: string, value: unknown): unknown {
  return typeof value === 'bigint' ? value.toString() : value;
}
