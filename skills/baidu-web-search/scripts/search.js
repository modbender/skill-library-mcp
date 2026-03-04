#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const axios = require('axios');

const SEARCH_URL = 'https://qianfan.baidubce.com/v2/ai_search/web_search';
const SKILL_ROOT = path.resolve(__dirname, '..');
const CONFIG_PATH = path.join(SKILL_ROOT, 'config.json');
const DEFAULT_NUM_RESULTS = 20;
const MAX_NUM_RESULTS = 50;
const TIMEOUT_MS = 15000;

/**
 * Resolve apiKey with priority:
 * 1. BAIDU_API_KEY env var (injected by OpenClaw/ClawHub platform)
 * 2. Local config.json (for local / self-hosted use)
 */
function resolveApiKey() {
  const envKey = (process.env.BAIDU_API_KEY || '').trim();
  if (envKey) return envKey;

  if (!fs.existsSync(CONFIG_PATH)) return '';
  try {
    const cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    return (cfg.apiKey || '').trim();
  } catch (e) {
    return '';
  }
}

function emptyResult(query, errorMsg) {
  return { results: [], total: 0, query: query || '', error: errorMsg };
}

async function main() {
  const args = process.argv.slice(2);
  const query = (args[0] || '').trim();
  const numResults = Math.min(
    Math.max(Number(args[1]) || DEFAULT_NUM_RESULTS, 1),
    MAX_NUM_RESULTS
  );

  if (!query) {
    console.log(JSON.stringify(emptyResult('', '搜索查询为空。')));
    process.exit(1);
  }

  const apiKey = resolveApiKey();
  if (!apiKey) {
    console.log(JSON.stringify(emptyResult(query, '未配置 apiKey，请在 OpenClaw Skills 配置页面填入 BAIDU_API_KEY，或本地编辑 config.json 填入 apiKey。')));
    process.exit(1);
  }

  try {
    const body = {
      messages: [{ role: 'user', content: query }],
      search_source: 'baidu_search_v2',
      resource_type_filter: [{ type: 'web', top_k: numResults }],
    };
    const { data } = await axios.post(SEARCH_URL, body, {
      timeout: TIMEOUT_MS,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
    });

    if (data && data.code) {
      console.log(JSON.stringify(emptyResult(query, '搜索服务暂时不可用，请稍后重试。')));
      process.exit(1);
    }

    const refs = data?.references || [];
    const results = refs
      .filter((r) => r && r.type === 'web')
      .map((r) => ({
        title: r.title || '',
        url: r.url || '',
        snippet: r.snippet ?? r.content ?? '',
      }));

    const output = {
      results,
      total: results.length,
      query,
      engine: 'baidu',
    };
    console.log(JSON.stringify(output));
  } catch (e) {
    console.log(JSON.stringify(emptyResult(query, '搜索服务暂时不可用，请检查 BAIDU_API_KEY 环境变量或 config.json 中的 apiKey，以及网络连接。')));
    process.exit(1);
  }
}

main();
