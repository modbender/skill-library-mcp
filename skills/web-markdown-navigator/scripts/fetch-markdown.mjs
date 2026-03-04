#!/usr/bin/env node
import { JSDOM } from "jsdom";
import { Readability } from "@mozilla/readability";
import TurndownService from "turndown";

function printErr(msg) {
  process.stderr.write(`${msg}\n`);
}

function usage() {
  printErr("Usage: fetch-markdown.mjs <url> [--max-chars N] [--timeout-ms N] [--json]");
}

function isPrivateHost(hostname) {
  const h = hostname.toLowerCase();
  if (["localhost", "127.0.0.1", "::1", "0.0.0.0"].includes(h)) return true;

  const ipv4 = h.match(/^(\d{1,3}\.){3}\d{1,3}$/);
  if (!ipv4) return false;

  const [a, b] = h.split(".").map(Number);
  if (a === 10) return true;
  if (a === 127) return true;
  if (a === 169 && b === 254) return true;
  if (a === 172 && b >= 16 && b <= 31) return true;
  if (a === 192 && b === 168) return true;
  return false;
}

function parseArgs(argv) {
  const out = {
    url: "",
    maxChars: 50000,
    timeoutMs: 15000,
    json: false,
  };

  const args = [...argv];
  if (args.length === 0) return out;

  out.url = args.shift();

  while (args.length > 0) {
    const flag = args.shift();
    if (flag === "--max-chars") {
      out.maxChars = Number(args.shift() ?? "0");
    } else if (flag === "--timeout-ms") {
      out.timeoutMs = Number(args.shift() ?? "0");
    } else if (flag === "--json") {
      out.json = true;
    } else {
      throw new Error(`unknown argument: ${flag}`);
    }
  }

  return out;
}

function normalizeWhitespace(md) {
  return md
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]+\n/g, "\n")
    .trim();
}

function fallbackPlainMarkdown(document) {
  const title = document.querySelector("title")?.textContent?.trim() ?? "";
  const bodyText = document.body?.textContent?.replace(/\s+/g, " ").trim() ?? "";
  if (!bodyText) return "";
  return `${title ? `# ${title}\n\n` : ""}${bodyText}`.trim();
}

function toJson(obj) {
  return JSON.stringify(obj, null, 2);
}

async function main() {
  let cfg;
  try {
    cfg = parseArgs(process.argv.slice(2));
  } catch (err) {
    usage();
    printErr(`ERROR: ${String(err.message || err)}`);
    process.exit(1);
  }

  if (!cfg.url) {
    usage();
    process.exit(1);
  }

  let u;
  try {
    u = new URL(cfg.url);
  } catch {
    printErr("ERROR: invalid URL");
    process.exit(2);
  }

  if (!["http:", "https:"].includes(u.protocol)) {
    printErr("ERROR: URL must be http/https");
    process.exit(2);
  }

  if (isPrivateHost(u.hostname)) {
    printErr("ERROR: private/local hosts are blocked");
    process.exit(2);
  }

  if (!Number.isFinite(cfg.maxChars) || cfg.maxChars < 0) {
    printErr("ERROR: --max-chars must be >= 0");
    process.exit(1);
  }
  if (!Number.isFinite(cfg.timeoutMs) || cfg.timeoutMs <= 0) {
    printErr("ERROR: --timeout-ms must be > 0");
    process.exit(1);
  }

  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), cfg.timeoutMs);

  let html = "";
  let fetchedUrl = u.toString();
  try {
    const res = await fetch(u, {
      signal: ac.signal,
      redirect: "follow",
      headers: {
        "user-agent": "web-markdown-navigator/1.0 (+OpenClaw skill)",
        accept: "text/html,application/xhtml+xml",
      },
    });

    fetchedUrl = res.url || fetchedUrl;

    const finalUrl = new URL(fetchedUrl);
    if (isPrivateHost(finalUrl.hostname)) {
      printErr("ERROR: redirected to private/local host");
      process.exit(2);
    }

    if (!res.ok) {
      printErr(`ERROR: fetch failed (${res.status} ${res.statusText})`);
      process.exit(3);
    }

    const ctype = res.headers.get("content-type") || "";
    if (!ctype.includes("text/html") && !ctype.includes("application/xhtml+xml")) {
      printErr(`ERROR: unsupported content-type: ${ctype || "unknown"}`);
      process.exit(3);
    }

    html = await res.text();
    if (html.length > 5_000_000) {
      printErr("ERROR: response too large");
      process.exit(3);
    }
  } catch (err) {
    if (String(err).toLowerCase().includes("aborted")) {
      printErr("ERROR: timeout");
    } else {
      printErr(`ERROR: network/fetch failure: ${String(err.message || err)}`);
    }
    process.exit(3);
  } finally {
    clearTimeout(timer);
  }

  let markdown = "";
  let method = "readability";

  try {
    const dom = new JSDOM(html, { url: fetchedUrl });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();

    if (article?.content) {
      const td = new TurndownService({
        headingStyle: "atx",
        codeBlockStyle: "fenced",
        bulletListMarker: "-",
      });
      markdown = td.turndown(article.content);
      if (article.title) markdown = `# ${article.title}\n\n${markdown}`;
    }

    if (!markdown || markdown.replace(/\s+/g, " ").trim().length < 200) {
      method = "fallback-text";
      markdown = fallbackPlainMarkdown(dom.window.document);
    }
  } catch (err) {
    printErr(`ERROR: extraction failure: ${String(err.message || err)}`);
    process.exit(4);
  }

  markdown = normalizeWhitespace(markdown);

  if (!markdown || markdown.length < 80) {
    printErr("ERROR: extracted content too thin/empty");
    process.exit(4);
  }

  let truncated = false;
  if (cfg.maxChars > 0 && markdown.length > cfg.maxChars) {
    markdown = `${markdown.slice(0, cfg.maxChars)}\n\n[TRUNCATED to ${cfg.maxChars} chars]`;
    truncated = true;
  }

  if (cfg.json) {
    process.stdout.write(
      toJson({
        ok: true,
        url: fetchedUrl,
        method,
        truncated,
        chars: markdown.length,
        markdown,
      }),
    );
  } else {
    process.stdout.write(`Source: ${fetchedUrl}\nMethod: ${method}\n\n${markdown}`);
  }
}

main().catch((err) => {
  printErr(`ERROR: unexpected failure: ${String(err.message || err)}`);
  process.exit(4);
});
