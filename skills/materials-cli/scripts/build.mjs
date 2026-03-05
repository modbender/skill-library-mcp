import * as esbuild from 'esbuild';
import { readdirSync, statSync, mkdirSync } from 'fs';
import { join, relative } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcDir = join(__dirname, '../src');
const outDir = join(__dirname, '../dist');

function getAllTsFiles(dir, base = dir) {
  const files = [];
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      if (name !== 'node_modules') files.push(...getAllTsFiles(full, base));
    } else if (name.endsWith('.ts') && !name.endsWith('.d.ts')) {
      files.push(relative(base, full));
    }
  }
  return files;
}

const entryPoints = getAllTsFiles(srcDir).map((f) => join(srcDir, f));

await esbuild.build({
  entryPoints,
  outdir: outDir,
  outbase: srcDir,
  format: 'esm',
  platform: 'node',
  target: 'node18',
  sourcemap: true,
  packages: 'external',
});

console.log('Build done.');
