#!/usr/bin/env node
/**
 * Validation tests for tex-render. Run after modifying render.js.
 * Usage: node scripts/validate.js
 */

const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

const SKILL_DIR = path.resolve(__dirname, '..');
const RENDER = path.join(SKILL_DIR, 'scripts', 'render.js');
const MEDIA_DIR = path.join(process.env.HOME || require('os').homedir(), '.openclaw', 'media', 'tex-render');
const TMP_DIR = path.join(SKILL_DIR, '.validate-tmp');

function runRender(latex, outBase, extraArgs = []) {
  const args = [RENDER, ...extraArgs, latex];
  if (outBase) args.push(outBase);
  const result = spawnSync(process.execPath, args, {
    encoding: 'utf8',
    input: null,
    maxBuffer: 1024 * 1024,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(result.stderr || result.stdout || 'Non-zero exit');
  return JSON.parse(result.stdout.trim());
}

function runHelp() {
  const result = spawnSync(process.execPath, [RENDER, '--help'], {
    encoding: 'utf8',
    maxBuffer: 1024 * 1024,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error('--help should exit 0');
  return result.stdout;
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function setupTmp() {
  if (fs.existsSync(TMP_DIR)) fs.rmSync(TMP_DIR, { recursive: true });
  fs.mkdirSync(TMP_DIR, { recursive: true });
}

const tests = [
  {
    name: '--help prints usage and exits 0',
    run: () => {
      const out = runHelp();
      assert(out.includes('tex-render'), 'Help should mention tex-render');
      assert(out.includes('--help'), 'Help should list --help');
      assert(out.includes('--format'), 'Help should list --format');
      assert(out.includes('--width'), 'Help should list --width');
      assert(out.includes('--inline'), 'Help should list --inline');
      assert(out.includes('webp') || out.includes('avif'), 'Help should list webp/avif');
      assert(out.includes('dataurl'), 'Help should list --output dataurl');
    },
  },
  {
    name: 'Display formula with $$ (frac F/m = a)',
    latex: '$$\\frac{F}{m}=a$$',
    checkSvg: (svg) => {
      assert(svg.includes('<svg'), 'SVG should contain <svg');
      assert(svg.includes('</svg>'), 'SVG should close');
      const hasContent = svg.length > 500 && (svg.includes('F') || svg.includes('frac') || svg.includes('MathJax'));
      assert(hasContent, 'SVG should have substantial content');
    },
    checkImgSize: (buf) => assert(buf && buf.length > 200, 'PNG should be non-tiny'),
    checkOutput: (result) => {
      assert(result.svg && result.png, 'Script must output svg and png paths');
      assert(!result.jpeg, 'Default format should be PNG, not JPEG');
      assert(result.svg.startsWith(MEDIA_DIR) && result.png.startsWith(MEDIA_DIR), 'Output should be under media dir');
    },
  },
  {
    name: 'Raw \\frac without $$',
    latex: '\\frac{F}{m}=a',
    checkSvg: (svg) => {
      assert(svg.includes('<svg'), 'SVG should contain <svg');
      assert(svg.length > 500, 'SVG should have content');
    },
    checkImgSize: (buf) => assert(buf && buf.length > 200, 'PNG should exist'),
    checkOutput: (result) => assert(result.svg && result.png, 'Must output svg and png'),
  },
  {
    name: 'Simple equation E=mc^2',
    latex: 'E = mc^2',
    checkSvg: (svg) => {
      assert(svg.includes('<svg'), 'SVG root');
      assert(svg.length > 300, 'SVG not empty');
    },
    checkImgSize: (buf) => assert(buf && buf.length > 100, 'PNG exists'),
    checkOutput: (result) => assert(result.svg && result.png, 'Must output svg and png'),
  },
  {
    name: '--format jpeg outputs JPEG',
    latex: 'E = mc^2',
    extraArgs: ['--format', 'jpeg'],
    outBase: path.join(TMP_DIR, 'test-jpeg'),
    checkOutput: (result) => {
      assert(result.svg, 'Must output svg');
      assert(result.jpeg, 'Must output jpeg when --format jpeg');
      assert(!result.png, 'Should not output png when --format jpeg');
      assert(fs.existsSync(result.jpeg), `JPEG file must exist: ${result.jpeg}`);
      const buf = fs.readFileSync(result.jpeg);
      assert(buf && buf.length > 50, 'JPEG should be non-empty');
    },
  },
  {
    name: '--width scales output',
    latex: 'x^2',
    extraArgs: ['--width', '800'],
    outBase: path.join(TMP_DIR, 'test-width'),
    checkOutput: (result) => {
      assert(result.svg && result.png, 'Must output svg and png');
      const buf = fs.readFileSync(result.png);
      assert(buf && buf.length > 1000, 'Scaled PNG should be larger than default');
    },
  },
  {
    name: '--inline renders inline math',
    latex: 'a^2 + b^2 = c^2',
    extraArgs: ['--inline'],
    checkOutput: (result) => {
      assert(result.svg && result.png, 'Must output svg and png');
      const svg = fs.readFileSync(result.svg, 'utf8');
      assert(svg.length > 100, 'Inline SVG should have content');
    },
  },
  {
    name: '--format webp outputs WebP',
    latex: 'x^2',
    extraArgs: ['--format', 'webp'],
    outBase: path.join(TMP_DIR, 'test-webp'),
    checkOutput: (result) => {
      assert(result.svg && result.webp, 'Must output svg and webp');
      assert(fs.existsSync(result.webp), `WebP file must exist: ${result.webp}`);
      const buf = fs.readFileSync(result.webp);
      assert(buf.length > 50, 'WebP should be non-empty');
    },
  },
  {
    name: '--format avif outputs AVIF',
    latex: 'x^2',
    extraArgs: ['--format', 'avif'],
    outBase: path.join(TMP_DIR, 'test-avif'),
    checkOutput: (result) => {
      assert(result.svg && result.avif, 'Must output svg and avif');
      assert(fs.existsSync(result.avif), `AVIF file must exist: ${result.avif}`);
      const buf = fs.readFileSync(result.avif);
      assert(buf.length > 50, 'AVIF should be non-empty');
    },
  },
  {
    name: '--output dataurl prints Data URL',
    latex: 'E = mc^2',
    extraArgs: ['--output', 'dataurl'],
    checkOutput: (result) => {
      assert(result.svg && result.dataurl, 'Must output svg and dataurl');
      assert(result.dataurl.startsWith('data:image/'), 'dataurl should be a valid data URL');
    },
    checkImgFile: false, // no raster file written in dataurl mode
  },
];

function main() {
  console.log('tex-render validation tests\n');
  setupTmp();
  let passed = 0;
  let failed = 0;

  for (const t of tests) {
    process.stdout.write(`  ${t.name} ... `);
    try {
      if (t.run) {
        t.run();
      } else {
        const result = runRender(t.latex, t.outBase, t.extraArgs || []);

        if (t.checkOutput) t.checkOutput(result);

        const svgPath = result.svg;
        const imgPath = result.png || result.jpeg || result.webp || result.avif;
        assert(fs.existsSync(svgPath), `SVG file must exist: ${svgPath}`);
        if (t.checkImgFile !== false && imgPath) {
          assert(fs.existsSync(imgPath), `Image file must exist: ${imgPath}`);
        }

        const svgContent = fs.readFileSync(svgPath, 'utf8');
        if (imgPath && fs.existsSync(imgPath)) {
          const imgBuffer = fs.readFileSync(imgPath);
          if (t.checkPngSize || t.checkImgSize) (t.checkPngSize || t.checkImgSize)(imgBuffer);
        }

        if (t.checkSvg) t.checkSvg(svgContent);

        if (!t.outBase && imgPath) {
          const underMedia = svgPath.startsWith(MEDIA_DIR) && imgPath.startsWith(MEDIA_DIR);
          assert(underMedia, `Default output should be under ~/.openclaw/media/tex-render, got: ${svgPath}`);
        }
      }
      console.log('ok');
      passed++;
    } catch (err) {
      console.log('FAIL');
      console.error(`    ${err.message}`);
      failed++;
    }
  }

  if (fs.existsSync(TMP_DIR)) fs.rmSync(TMP_DIR, { recursive: true });
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

main();
