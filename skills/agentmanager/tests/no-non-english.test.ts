import { readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const cjkRegex = /[\u3400-\u9FFF]/;
const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..');

const walkFiles = (path: string): string[] => {
  const entries = readdirSync(path);
  const files: string[] = [];

  for (const entry of entries) {
    const full = join(path, entry);
    const st = statSync(full);
    if (st.isDirectory()) {
      files.push(...walkFiles(full));
    } else {
      files.push(full);
    }
  }

  return files;
};

describe('repository language policy', () => {
  it('contains no CJK characters in README.md, src, and tests', () => {
    const files = [
      join(repoRoot, 'README.md'),
      ...walkFiles(join(repoRoot, 'src')),
      ...walkFiles(join(repoRoot, 'tests'))
    ];

    const offenders: string[] = [];
    for (const file of files) {
      const content = readFileSync(file, 'utf8');
      if (cjkRegex.test(content)) offenders.push(file);
    }

    expect(offenders, `CJK characters found in: ${offenders.join(', ')}`).toEqual([]);
  });
});
