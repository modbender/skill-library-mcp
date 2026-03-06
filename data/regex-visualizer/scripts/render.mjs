#!/usr/bin/env node

import { execSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const skillRoot = resolve(scriptDir, "..");
const htmlPath = resolve(skillRoot, "assets", "regulex.html");

function parseArgs(argv) {
  const opts = {
    re: null,
    flags: "",
    out: null,
    svgOnly: false,
    pngOnly: false,
    scale: 2,
    timeoutMs: 30000,
    chromePath: process.env.CHROME_PATH || process.env.PUPPETEER_EXECUTABLE_PATH || null,
  };

  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    switch (k) {
      case "--re":
        opts.re = v;
        i++;
        break;
      case "--flags":
        opts.flags = v || "";
        i++;
        break;
      case "--out":
        opts.out = v;
        i++;
        break;
      case "--svg-only":
        opts.svgOnly = true;
        break;
      case "--png-only":
        opts.pngOnly = true;
        break;
      case "--scale":
        opts.scale = Number(v || "2");
        i++;
        break;
      case "--timeout":
        opts.timeoutMs = Number(v || "30000");
        i++;
        break;
      case "--chrome":
        opts.chromePath = v;
        i++;
        break;
      case "--help":
      case "-h":
        printHelp();
        process.exit(0);
    }
  }

  if (!opts.re) {
    console.error("Error: --re is required");
    printHelp();
    process.exit(1);
  }
  if (!opts.out) {
    console.error("Error: --out is required");
    printHelp();
    process.exit(1);
  }

  if (opts.svgOnly && opts.pngOnly) {
    console.error("Error: only one of --svg-only/--png-only may be set");
    process.exit(1);
  }

  return opts;
}

function printHelp() {
  console.log(`Regulex Regex Visualizer (Export Image)

Uses the Regulex-Plus web UI export logic (cmd=export) to output SVG/PNG.

Usage:
  node scripts/render.mjs --re "<regex>" --out "<path/base>" [options]

Options:
  --flags "<img>"      Flags: subset of i/m/g supported by the UI (default: "")
  --svg-only           Only write <out>.svg
  --png-only           Only write <out>.png
  --scale N            devicePixelRatio for PNG export (default: 2)
  --timeout MS         Timeout waiting for export (default: 30000)
  --chrome "<path>"    Chrome/Edge executable path (or set CHROME_PATH)
`);
}

function findChromeExecutable() {
  const candidates = [];
  if (process.env.CHROME_PATH) candidates.push(process.env.CHROME_PATH);
  if (process.env.PUPPETEER_EXECUTABLE_PATH) candidates.push(process.env.PUPPETEER_EXECUTABLE_PATH);

  if (process.platform === "win32") {
    const pf = process.env.ProgramFiles || "C:\\Program Files";
    const pfx86 = process.env["ProgramFiles(x86)"] || "C:\\Program Files (x86)";
    candidates.push(join(pf, "Google", "Chrome", "Application", "chrome.exe"));
    candidates.push(join(pfx86, "Google", "Chrome", "Application", "chrome.exe"));
    candidates.push(join(pf, "Microsoft", "Edge", "Application", "msedge.exe"));
    candidates.push(join(pfx86, "Microsoft", "Edge", "Application", "msedge.exe"));
  } else if (process.platform === "darwin") {
    candidates.push("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome");
    candidates.push("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge");
  } else {
    candidates.push("google-chrome");
    candidates.push("chromium");
    candidates.push("chromium-browser");
    candidates.push("microsoft-edge");
  }

  for (const p of candidates) {
    if (!p) continue;
    if (p.includes("\\") || p.includes("/") ) {
      if (existsSync(p)) return p;
    } else {
      return p; // rely on PATH
    }
  }
  return null;
}

async function loadPuppeteerCore() {
  try {
    return await import("puppeteer-core");
  } catch {}

  console.error("[puppeteer-core] Dependency not found.");
  console.error(`Run: cd ${skillRoot} && npm install`);
  process.exit(1);

  // Import via explicit file:// URL so Windows absolute paths work in ESM.
  const pkgPath = resolve(skillRoot, "node_modules", "puppeteer-core", "lib", "esm", "puppeteer", "puppeteer-core.js");
  if (existsSync(pkgPath)) {
    return await import(pathToFileURL(pkgPath).href);
  }
  return await import("puppeteer-core");
}

function ensureOutDir(outBase) {
  const outDir = resolve(dirname(outBase));
  if (!existsSync(outDir)) {
    mkdirSync(outDir, { recursive: true });
  }
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (!existsSync(htmlPath)) {
    console.error(`Error: missing asset HTML: ${htmlPath}`);
    process.exit(1);
  }

  const chrome = opts.chromePath || findChromeExecutable();
  if (!chrome) {
    console.error("Error: Chrome/Edge not found. Set --chrome <path> or CHROME_PATH.");
    process.exit(1);
  }

  ensureOutDir(opts.out);

  const { default: puppeteer } = await loadPuppeteerCore();

  const fileUrl = pathToFileURL(htmlPath).href;
  const hash =
    "#!cmd=export&flags=" +
    encodeURIComponent(opts.flags || "") +
    "&re=" +
    encodeURIComponent(opts.re);
  const url = fileUrl + hash;

  const browser = await puppeteer.launch({
    executablePath: chrome.includes("\\") || chrome.includes("/") ? chrome : undefined,
    headless: true,
    args: [
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage",
    ],
    defaultViewport: {
      width: 4096,
      height: 2160,
      deviceScaleFactor: Number.isFinite(opts.scale) && opts.scale > 0 ? opts.scale : 2,
    },
  });

  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "load", timeout: opts.timeoutMs });

    // Wait for either: exported canvas exists, or UI error is shown.
    await page.waitForFunction(() => {
      const canvas = document.querySelector("canvas.exportCanvas");
      const err = document.getElementById("errorBox");
      const hasErr = err && err.style && err.style.display !== "none";
      return Boolean(canvas) || Boolean(hasErr);
    }, { timeout: opts.timeoutMs });

    const errorText = await page.evaluate(() => {
      const err = document.getElementById("errorBox");
      if (!err) return "";
      if (err.style && err.style.display === "none") return "";
      return (err.textContent || "").trim();
    });
    if (errorText) {
      throw new Error(errorText);
    }

    const wantSvg = !opts.pngOnly;
    const wantPng = !opts.svgOnly;

    if (wantSvg) {
      const svg = await page.evaluate(() => {
        const ct = document.getElementById("graphCt");
        const svg = ct && ct.getElementsByTagName("svg")[0];
        if (!svg) return "";
        return new XMLSerializer().serializeToString(svg);
      });
      if (!svg) {
        throw new Error("Export failed: SVG not found in #graphCt");
      }
      writeFileSync(resolve(`${opts.out}.svg`), svg, "utf8");
    }

    if (wantPng) {
      const dataUrl = await page.evaluate(() => {
        const canvas = document.querySelector("canvas.exportCanvas");
        if (!canvas) return "";
        return canvas.toDataURL("image/png");
      });
      if (!dataUrl || !dataUrl.startsWith("data:image/png;base64,")) {
        throw new Error("Export failed: PNG data URL not available");
      }
      const b64 = dataUrl.slice("data:image/png;base64,".length);
      writeFileSync(resolve(`${opts.out}.png`), Buffer.from(b64, "base64"));
    }

    const wrote = [];
    if (!opts.pngOnly) wrote.push(`${resolve(`${opts.out}.svg`)}`);
    if (!opts.svgOnly) wrote.push(`${resolve(`${opts.out}.png`)}`);
    console.log(`Wrote: ${wrote.join(" , ")}`);
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  console.error("Error:", e.message || String(e));
  process.exit(1);
});
