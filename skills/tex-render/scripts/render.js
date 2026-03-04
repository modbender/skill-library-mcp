#!/usr/bin/env node
/**
 * tex-render: LaTeX → MathJax (SVG) → @svg-fns/svg2img → PNG/JPEG/WebP/AVIF
 * Run with --help for full usage.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const MathJax = require('mathjax');
const { svgToBuffer, svgToDataUrl } = require('@svg-fns/svg2img/server');

const DEFAULT_OUTPUT_DIR = path.join(os.homedir(), '.openclaw', 'media', 'tex-render');
const RASTER_FORMATS = ['png', 'jpeg', 'jpg', 'webp', 'avif'];

function help() {
  const script = path.basename(__filename);
  return `tex-render: LaTeX → MathJax (SVG) → raster image (PNG/JPEG/WebP/AVIF)

Usage:
  node ${script} [OPTIONS] "<LaTeX>" [output_base_path]
  echo "<LaTeX>" | node ${script} [OPTIONS] [output_base_path]

Arguments:
  LaTeX             The math expression (required unless from stdin).
                    Accepts $$...$$, $...$, \\frac{}{}, etc.
  output_base_path  Optional. Default: ~/.openclaw/media/tex-render/tex-<hash>

Options:
  -h, --help        Show this help
  --inline          Use inline-TeX (smaller, in-text style)
  --format FMT      Output format: png (default), jpeg, webp, avif
  --output MODE     Output mode: file (default) or dataurl
  --quality N       JPEG/WebP/AVIF quality 1-100 (default: 92)
  --width N         Scale output to width N (maintains aspect ratio)
  --height N        Scale output to height N (maintains aspect ratio)
  --zoom N          Scale by zoom factor N (default scale is 1x when no width/height/zoom)

Output:
  file mode (default): Writes {base}.svg and {base}.{png|jpeg|webp|avif}.
  dataurl mode: Prints Data URL to stdout (no image file written).

  Prints one JSON line:
  {"svg":"<path>","png":"<path>"} or {"svg":"<path>","jpeg":"<path>"} etc.
  With --output dataurl: {"svg":"<path>","dataurl":"data:image/...;base64,..."}

Examples:
  node ${script} 'E = mc^2'
  node ${script} --format webp --quality 85 '\\frac{F}{m}=a' ./out/formula
  node ${script} --format avif 'x^2 + y^2 = z^2'
  node ${script} --output dataurl 'E = mc^2'
  node ${script} --width 800 '\\int_0^\\infty e^{-x^2} dx'
  node ${script} --inline 'x^2 + y^2 = z^2'
`;
}

function shortHash(str) {
  return crypto.createHash('sha256').update(str).digest('hex').slice(0, 10);
}

/**
 * Normalize LaTeX: strip markdown/display delimiters ($$, $, \[ \], \( \))
 */
function normalizeLatex(input) {
  let s = String(input).trim();
  if (/^\$\$(.*)\$\$/s.test(s)) s = s.replace(/^\$\$(.*)\$\$/s, '$1').trim();
  if (/^\$(.*)\$$/s.test(s)) s = s.replace(/^\$(.*)\$$/s, '$1').trim();
  if (/^\\\[([\s\S]*)\\\]$/.test(s)) s = s.replace(/^\\\[([\s\S]*)\\\]$/, '$1').trim();
  if (/^\\\((.*)\\\)$/s.test(s)) s = s.replace(/^\\\((.*)\\\)$/s, '$1').trim();
  return s;
}

function parseViewBox(svgStr) {
  const m = svgStr.match(/viewBox=["']([^"']+)["']/i);
  if (!m) return null;
  const parts = m[1].trim().split(/\s+/).map(Number);
  if (parts.length >= 4) return { minX: parts[0], minY: parts[1], w: parts[2], h: parts[3] };
  return null;
}

function mergeInlineSvgs(html) {
  const cleaned = html.replace(/<mjx-break[^>]*>[\s\S]*?<\/mjx-break>/gi, '');
  const blocks = [];
  let re = /<svg([^>]*)>([\s\S]*?)<\/svg>/gi;
  let m;
  while ((m = re.exec(cleaned)) !== null) {
    const full = m[0];
    const vb = parseViewBox(full);
    const w = vb ? vb.w : 100;
    const h = vb ? vb.h : 100;
    const minY = vb ? vb.minY : 0;
    blocks.push({ full, w, h, minY, inner: m[2] });
  }
  if (blocks.length <= 1) return blocks[0]?.full || html;
  let x = 0;
  const maxH = Math.max(...blocks.map((b) => b.h));
  const minY = Math.min(...blocks.map((b) => b.minY));
  const groups = blocks.map((b) => {
    const g = `<g transform="translate(${x},0)">${b.inner}</g>`;
    x += b.w;
    return g;
  });
  // MathJax uses negative minY (e.g. 0 -833.9 965.6 1083.9); merged viewBox must include it
  const merged = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 ${minY} ${x} ${maxH}" width="${x}" height="${maxH}">${groups.join('')}</svg>`;
  return merged;
}

async function typeset(tex, opts = {}) {
  await MathJax.init({ loader: { load: ['input/tex', 'output/svg'] } });
  const node = await MathJax.tex2svgPromise(tex, { display: !opts.inline });
  const adaptor = MathJax.startup.adaptor;
  const html = adaptor.outerHTML(node);
  let svg;
  if (opts.inline && /<mjx-break/i.test(html)) {
    svg = mergeInlineSvgs(html);
  } else {
    const match = html.match(/<svg[\s\S]*?<\/svg>/i);
    svg = match ? match[0] : html;
  }
  if (svg && !svg.includes('xmlns=')) svg = svg.replace(/<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  return svg;
}

const DEFAULT_SCALE = 1; // 3x resolution for sharper output on high-DPI displays

function buildSvg2imgOpts(opts) {
  const o = {};
  const fmt = opts.format === 'jpg' ? 'jpeg' : opts.format;
  if (RASTER_FORMATS.includes(opts.format)) o.format = fmt;
  // quality: CLI 1-100 → library 0-1
  o.quality = typeof opts.quality === 'number' ? (opts.quality > 1 ? opts.quality / 100 : opts.quality) : 0.92;
  if (opts.width) o.width = opts.width;
  if (opts.height) o.height = opts.height;
  // Default scale when no width/height/zoom: higher resolution output
  if (opts.scale != null) o.scale = opts.scale;
  else if (!opts.width && !opts.height) o.scale = DEFAULT_SCALE;
  if (fmt === 'jpeg') o.background = opts.background || '#fff';
  // width/height with single dimension → fit contain
  if ((opts.width || opts.height) && !opts.fit) o.fit = 'contain';
  return o;
}

function parseArgs(argv) {
  const args = { inline: false, format: 'png', quality: 92, output: 'file', scale: null, width: null, height: null, latex: '', outBase: '' };
  const rest = [];
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-h' || a === '--help') return { help: true };
    if (a === '--inline') { args.inline = true; continue; }
    if (a === '--format' && argv[i + 1] !== undefined) { args.format = argv[++i]; continue; }
    if (a === '--output' && argv[i + 1] !== undefined) { args.output = argv[++i]; continue; }
    if (a === '--quality' && argv[i + 1] !== undefined) { args.quality = parseInt(argv[++i], 10) || 92; continue; }
    if (a === '--width' && argv[i + 1] !== undefined) { args.width = parseInt(argv[++i], 10) || null; continue; }
    if (a === '--height' && argv[i + 1] !== undefined) { args.height = parseInt(argv[++i], 10) || null; continue; }
    if (a === '--zoom' && argv[i + 1] !== undefined) { args.scale = parseFloat(argv[++i]) || 1; continue; }
    rest.push(a);
  }
  if (rest.length >= 1) args.latex = rest[0];
  if (rest.length >= 2) args.outBase = rest[1];
  return args;
}

async function main() {
  const parsed = parseArgs(process.argv);

  if (parsed.help) {
    console.log(help());
    process.exit(0);
  }

  let latex = parsed.latex;
  if (!latex && !process.stdin.isTTY) {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    latex = Buffer.concat(chunks).toString('utf8').trim();
  }
  if (!latex) {
    console.error(help());
    process.exit(1);
  }

  latex = normalizeLatex(latex);
  if (!latex) {
    console.error('Empty LaTeX after normalizing delimiters.');
    process.exit(1);
  }

  const cwd = process.cwd();
  const outBase = parsed.outBase;
  let outDir, base;

  if (!outBase) {
    base = `tex-${shortHash(latex)}`;
    outDir = DEFAULT_OUTPUT_DIR;
  } else if (path.isAbsolute(outBase)) {
    outDir = path.dirname(outBase);
    base = path.basename(outBase, path.extname(outBase));
  } else {
    outDir = path.dirname(outBase);
    base = path.basename(outBase, path.extname(outBase));
    if (outDir === '.') outDir = cwd;
    else outDir = path.join(cwd, outDir);
  }

  const fmt = parsed.format === 'jpeg' || parsed.format === 'jpg' ? 'jpeg' : parsed.format;
  const ext = RASTER_FORMATS.includes(parsed.format) ? fmt : 'png';
  const svgPath = path.join(outDir, base + '.svg');

  const opts = buildSvg2imgOpts({
    format: parsed.format,
    quality: parsed.quality,
    width: parsed.width,
    height: parsed.height,
    scale: parsed.scale,
  });

  try {
    const svg = await typeset(latex, { inline: parsed.inline });
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(svgPath, svg, 'utf8');

    const out = { svg: svgPath };

    if (parsed.output === 'dataurl') {
      const result = await svgToDataUrl(svg, opts);
      out.dataurl = result.dataUrl;
    } else {
      const result = await svgToBuffer(svg, opts);
      const imgPath = path.join(outDir, base + '.' + (result.format || ext));
      fs.writeFileSync(imgPath, result.buffer);
      out[result.format || ext] = imgPath;
    }

    console.log(JSON.stringify(out));
  } catch (err) {
    console.error('tex-render error:', err.message);
    process.exit(1);
  }
}

main();
