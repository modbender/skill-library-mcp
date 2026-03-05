#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function usage(msg) {
  if (msg) console.error(msg);
  console.error('用法: node scripts/bocha.mjs <web|ai|agent|rerank> [参数]');
  process.exit(1);
}

function parseArgs(argv) {
  const out = {
    query: '', count: 10, freshness: 'noLimit', summary: true,
    page: '', offset: '', language: '', region: '', site: '',
    rawJson: '', timeout: 30, pretty: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    switch (k) {
      case '--query': out.query = v ?? ''; i++; break;
      case '--count': out.count = Number(v); i++; break;
      case '--freshness': out.freshness = v ?? 'noLimit'; i++; break;
      case '--summary':
        if (v !== 'true' && v !== 'false') usage('--summary 只能是 true/false');
        out.summary = v === 'true';
        i++;
        break;
      case '--page': out.page = v ?? ''; i++; break;
      case '--offset': out.offset = v ?? ''; i++; break;
      case '--language': out.language = v ?? ''; i++; break;
      case '--region': out.region = v ?? ''; i++; break;
      case '--site': out.site = v ?? ''; i++; break;
      case '--raw-json': out.rawJson = v ?? ''; i++; break;
      case '--timeout': out.timeout = Number(v); i++; break;
      case '--pretty': out.pretty = true; break;
      default: usage(`未知参数: ${k}`);
    }
  }

  if (!Number.isInteger(out.count)) usage('--count 必须是整数');
  out.count = Math.max(1, Math.min(50, out.count));

  if (!Number.isInteger(out.timeout) || out.timeout <= 0) usage('--timeout 必须是正整数秒');

  return out;
}

function loadApiKey() {
  if (process.env.BOCHA_API_KEY?.trim()) return process.env.BOCHA_API_KEY.trim();
  const configPath = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'config.json');
  try {
    const txt = fs.readFileSync(configPath, 'utf8');
    const cfg = JSON.parse(txt);
    const key = String(cfg.apiKey || '').trim();
    if (key) return key;
  } catch {}
  console.error('缺少 API Key。请设置 BOCHA_API_KEY 或在 skills/bocha-web-search/config.json 中配置 apiKey。');
  process.exit(2);
}

function endpointByMode(mode) {
  switch (mode) {
    case 'web': return 'https://api.bochaai.com/v1/web-search';
    case 'ai': return 'https://api.bochaai.com/v1/ai-search';
    case 'agent': return 'https://api.bochaai.com/v1/agent-search';
    case 'rerank': return 'https://api.bochaai.com/v1/semantic-reranker';
    default: usage(`不支持的模式: ${mode}（仅支持 web|ai|agent|rerank）`);
  }
}

async function main() {
  const mode = process.argv[2];
  if (!mode) usage();
  const args = parseArgs(process.argv.slice(3));
  if (mode !== 'rerank' && !args.query) usage('非 rerank 模式必须传 --query');

  const endpoint = endpointByMode(mode);
  const apiKey = loadApiKey();

  const payload = {
    ...(args.query ? { query: args.query } : {}),
    count: args.count,
    freshness: args.freshness,
    summary: args.summary,
    ...(args.page ? { page: args.page } : {}),
    ...(args.offset ? { offset: args.offset } : {}),
    ...(args.language ? { language: args.language } : {}),
    ...(args.region ? { region: args.region } : {}),
    ...(args.site ? { site: args.site } : {}),
  };

  if (args.rawJson) {
    try {
      Object.assign(payload, JSON.parse(args.rawJson));
    } catch (e) {
      console.error(`--raw-json 不是合法 JSON: ${e.message}`);
      process.exit(1);
    }
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), args.timeout * 1000);

  try {
    const resp = await fetch(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    const text = await resp.text();
    if (!resp.ok) {
      console.error(text || `HTTP ${resp.status}`);
      process.exit(1);
    }

    if (args.pretty) {
      try {
        const parsed = JSON.parse(text);
        console.log(JSON.stringify(parsed, null, 2));
      } catch {
        console.log(text);
      }
    } else {
      console.log(text);
    }
  } catch (e) {
    if (e.name === 'AbortError') {
      console.error(`请求超时（>${args.timeout}s）`);
    } else {
      console.error(`请求失败: ${e.message}`);
    }
    process.exit(1);
  } finally {
    clearTimeout(timer);
  }
}

main();
