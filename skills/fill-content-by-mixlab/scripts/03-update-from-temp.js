#!/usr/bin/env node

/**
 * 从 temp 文件读取内容并更新到 mixdao
 * 读取 temp/{cachedStoryId}.txt，批量 PATCH（body: { items: [{ cachedStoryId, content }, ...] }）
 *
 * 用法: node scripts/03-update-from-temp.js list <temp/fill-content-{date}.json>   # 列出待更新（必须传 JSON）
 *       node scripts/03-update-from-temp.js <id1> [<id2> ...]                      # 批量更新指定的一条或多条（必须传至少一个 id）
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';
import Anthropic from '@anthropic-ai/sdk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const API_URL = 'https://www.mixdao.world/api/latest/recommendation';
const tempDir = path.join(__dirname, '..', 'temp');
const BATCH_SIZE = 50; // 单次 PATCH 最多条数，与 recommendation 接口一致
const MODEL = 'MiniMax-M2.5';
const SUMMARIZE_MAX_TOKENS = 1024;
const BODY_TRUNCATE = 6000; // 送入模型的正文最大字符数

/** 批量 PATCH：body 为 { items: [{ cachedStoryId, content }, ...] }，返回 { ok, results: [{ cachedStoryId, ok }, ...] } */
function batchUpdateContent(items) {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.MIXDAO_API_KEY;
    if (!apiKey) {
      reject(new Error('MIXDAO_API_KEY is not set.'));
      return;
    }
    if (!items.length) {
      resolve({ ok: true, results: [] });
      return;
    }

    const url = new URL(API_URL);
    const body = JSON.stringify({ items });

    const opts = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body, 'utf8'),
      },
    };

    const req = https.request(opts, (res) => {
      res.setTimeout(15000, () => {
        req.destroy();
        reject(new Error('API 请求超时'));
      });
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const responseBody = Buffer.concat(chunks).toString('utf8');
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const data = JSON.parse(responseBody || '{}');
            resolve(data);
          } catch (e) {
            resolve({ ok: true, results: [] });
          }
        } else {
          reject(new Error(`API returned ${res.statusCode}: ${responseBody.slice(0, 200)}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body, 'utf8');
    req.end();
  });
}

/** 从 temp 目录读取并校验，返回可提交的 items: [{ cachedStoryId, content }, ...]，无效的会打 log 并跳过 */
function collectItems(ids) {
  const items = [];
  const minContentLen = 50;
  for (const id of ids) {
    const cachedStoryId = id.trim();
    const tempFile = path.join(tempDir, `${cachedStoryId}.txt`);
    if (!fs.existsSync(tempFile)) {
      console.error(`[SKIP] temp/${cachedStoryId}.txt 不存在`);
      continue;
    }
    const content = fs.readFileSync(tempFile, 'utf8');
    if (!content || content.trim().length < minContentLen) {
      console.error(`[SKIP] 内容太短: ${cachedStoryId} (${(content || '').length} 字符)`);
      continue;
    }
    items.push({ cachedStoryId, content });
  }
  return items;
}

function getClient() {
  const baseURL = process.env.ANTHROPIC_BASE_URL;
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY is not set.');
  return new Anthropic({
    baseURL: baseURL || 'https://api.minimaxi.com/anthropic',
    apiKey,
  });
}

/** 从模型返回的 content 中取出完整文本（忽略 thinking 块） */
function getTextFromContent(content) {
  if (!Array.isArray(content)) return '';
  let text = '';
  for (const block of content) {
    if (block.type === 'text' && block.text) text += block.text;
  }
  return text.trim();
}

async function callMiniMax(client, system, userText, options = {}) {
  const { max_tokens = 4096 } = typeof options === 'number' ? { max_tokens: options } : options;
  const message = await client.messages.create({
    model: MODEL,
    max_tokens,
    system,
    messages: [{ role: 'user', content: userText }],
  });
  return getTextFromContent(message.content);
}

/**
 * 用 AI 将正文梳理为约 250 字、简体中文、突出人物/公司等实体的案例描述，用于替代原文上传。
 */
async function summarizeAsCase(client, rawContent) {
  const system = `你是写作与案例整理助手。请将用户提供的正文梳理为一段约 250 字的描述，要求：
- 统一使用简体中文；
- 重点描述人物、公司、产品、事件等重要实体及其关系或结论；
- 可直接作为「案例」或文章写作素材使用；
- 只输出这一段描述，不要标题、不要列举、不要解释。`;

  const truncated = rawContent.trim().slice(0, BODY_TRUNCATE);
  const userText =
    truncated.length < rawContent.length
      ? truncated + '\n\n（上文已截断，请基于此部分梳理。）'
      : truncated;

  const text = await callMiniMax(client, system, userText, {
    max_tokens: SUMMARIZE_MAX_TOKENS,
  });
  const cleaned = text.trim().replace(/\n+/g, ' ').slice(0, 300);
  return cleaned.length >= 50 ? cleaned : text.trim();
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('用法:');
    console.error('  node scripts/03-update-from-temp.js list <temp/fill-content-{date}.json>   # 列出待更新（必须传 JSON）');
    console.error('  node scripts/03-update-from-temp.js <id1> [<id2> ...]                    # 更新指定的一条或多条（必须传至少一个 id）');
    process.exit(1);
  }

  const command = args[0];

  // list：必须传 JSON 路径，输出 title/translatedTitle/text 与正文摘要供 Agent 做语义判断
  if (command === 'list') {
    const jsonPath = args[1];
    if (!jsonPath) {
      console.error('[ERROR] list 模式必须传入 JSON 文件路径（步骤 1 输出的 fill-content-{date}.json）');
      console.error('示例: node scripts/03-update-from-temp.js list temp/fill-content-2026-02-17.json');
      process.exit(1);
    }
    if (!fs.existsSync(jsonPath)) {
      console.error(`[ERROR] 文件不存在: ${jsonPath}`);
      process.exit(1);
    }
    let metaById;
    try {
      const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
      const items = data.items || [];
      metaById = Object.fromEntries(items.map(it => [it.cachedStoryId, it]));
    } catch (e) {
      console.error(`[ERROR] 无法解析 JSON: ${e.message}`);
      process.exit(1);
    }
    if (!fs.existsSync(tempDir)) {
      console.log('暂无待更新的内容（temp 目录不存在或为空）');
      return;
    }

    const files = fs.readdirSync(tempDir).filter(f => f.endsWith('.txt'));
    console.log(`共 ${files.length} 条待更新:\n`);
    const TEXT_MAX = 200;
    const PREVIEW_MAX = 300;

    files.forEach(f => {
      const cachedStoryId = f.replace('.txt', '');
      const content = fs.readFileSync(path.join(tempDir, f), 'utf8');
      const meta = metaById[cachedStoryId];
      if (meta) {
        const title = (meta.title || '').slice(0, TEXT_MAX);
        const translatedTitle = (meta.translatedTitle || '').slice(0, TEXT_MAX);
        const text = (meta.text || '').slice(0, TEXT_MAX);
        const preview = content.trim().slice(0, PREVIEW_MAX);
        console.log('---');
        console.log(`cachedStoryId: ${cachedStoryId}`);
        console.log(`title: ${title}`);
        console.log(`translatedTitle: ${translatedTitle}`);
        console.log(`text: ${text}`);
        console.log(`contentLength: ${content.length}`);
        console.log(`contentPreview: ${preview}${content.length > PREVIEW_MAX ? '...' : ''}`);
      } else {
        console.log(`- ${cachedStoryId} (${content.length} 字符) [无元数据，不在本次 JSON 中]`);
      }
    });
    console.log('---');
    console.log('（以上含 title/translatedTitle/text 与正文摘要，供 Agent 判断是否与文章主题一致）');
    return;
  }

  // 更新：必须传至少一个 id（Agent 判断后传入要更新的 id 列表），批量 PATCH
  const ids = args.filter(a => a.trim().length > 0);
  if (ids.length === 0) {
    console.error('[ERROR] 更新模式必须传入至少一个 cachedStoryId');
    console.error('示例: node scripts/03-update-from-temp.js cmlpr8xsb005al70adaskpzl4 cmlpr8xd7002jl70ax1ytgrrt');
    process.exit(1);
  }
  const items = collectItems(ids);
  if (items.length === 0) {
    console.error('[ERROR] 没有可更新的条目（文件缺失或内容过短）');
    process.exit(1);
  }

  const client = getClient();
  console.log(`共 ${ids.length} 个 id，有效 ${items.length} 条。正在用 AI 梳理正文（约 250 字）…\n`);
  for (let i = 0; i < items.length; i++) {
    try {
      items[i].content = await summarizeAsCase(client, items[i].content);
      console.log(`[梳理] ${items[i].cachedStoryId}`);
    } catch (err) {
      console.error(`[SKIP] 梳理失败 ${items[i].cachedStoryId}: ${err.message}，保留原文`);
    }
  }

  console.log('\n批量提交…\n');
  let success = 0;
  let failed = 0;
  for (let i = 0; i < items.length; i += BATCH_SIZE) {
    const chunk = items.slice(i, i + BATCH_SIZE);
    try {
      const data = await batchUpdateContent(chunk);
      const results = data.results || [];
      for (const r of results) {
        if (r.ok) {
          success++;
          console.log(`[OK] ${r.cachedStoryId}`);
        } else {
          failed++;
          console.error(`[FAIL] ${r.cachedStoryId}`);
        }
      }
    } catch (err) {
      console.error(`[ERROR] 批量请求失败: ${err.message}`);
      failed += chunk.length;
    }
  }
  console.log(`\n===== 完成 =====`);
  console.log(`成功: ${success}`);
  console.log(`失败: ${failed}`);
}

main().catch(console.error);
