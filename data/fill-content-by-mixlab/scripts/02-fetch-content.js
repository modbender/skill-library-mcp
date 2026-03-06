#!/usr/bin/env node

/**
 * 抓取正文并保存到 temp 目录
 * 根据 URL 获取全文，判断正确内容后存储
 * 文件名: temp/{cachedStoryId}.txt
 * 内容: 处理后的 content
 *
 * 用法: node scripts/02-fetch-content.js <temp/fill-content-{date}.json>
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 简单的内容提取（从 HTML 中提取文本）
function extractText(html) {
  // 移除 script 和 style 标签
  let text = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
  text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
  // 移除 HTML 标签
  text = text.replace(/<[^>]+>/g, '\n');
  // 替换实体
  text = text.replace(/&nbsp;/g, ' ');
  text = text.replace(/&amp;/g, '&');
  text = text.replace(/&lt;/g, '<');
  text = text.replace(/&gt;/g, '>');
  text = text.replace(/&quot;/g, '"');
  // 合并多个空行
  text = text.replace(/\n{3,}/g, '\n\n');
  // 去除首尾空白
  text = text.trim();
  return text;
}

// 判断是否为有效内容（非 404、登录页等）
function isValidContent(text) {
  if (!text || text.length < 100) return false;
  const lowerText = text.toLowerCase();
  if (
    lowerText.includes('404 not found') ||
    lowerText.includes('page not found') ||
    lowerText.includes('access denied') ||
    lowerText.includes('forbidden') ||
    lowerText.includes('sign in') ||
    lowerText.includes('log in')
  ) {
    return false;
  }
  return true;
}

// 使用 curl 获取页面
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const curl = spawn('curl', ['-sL', '--max-time', '30', url]);
    let data = '';
    let error = '';

    curl.stdout.on('data', (chunk) => { data += chunk; });
    curl.stderr.on('data', (chunk) => { error += chunk; });

    curl.on('close', (code) => {
      if (code !== 0 && !data) {
        reject(new Error(`curl failed: ${error}`));
      } else {
        resolve(data);
      }
    });

    curl.on('error', reject);
  });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('用法: node scripts/02-fetch-content.js <temp/fill-content-{date}.json>');
    console.error('示例: node scripts/02-fetch-content.js temp/fill-content-2026-02-17.json');
    process.exit(1);
  }

  const inputFile = args[0];
  if (!fs.existsSync(inputFile)) {
    console.error(`文件不存在: ${inputFile}`);
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  const items = data.items || [];
  const tempDir = path.join(__dirname, '..', 'temp');

  // 确保 temp 目录存在
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  console.log(`共 ${items.length} 条待处理\n`);

  let success = 0;
  let skipped = 0;
  let failed = 0;

  for (const item of items) {
    const { cachedStoryId, url, title, translatedTitle } = item;

    if (!url) {
      console.log(`[SKIP] ${cachedStoryId} - 无 URL`);
      skipped++;
      continue;
    }

    // 检查是否已有临时文件
    const tempFile = path.join(tempDir, `${cachedStoryId}.txt`);
    if (fs.existsSync(tempFile)) {
      console.log(`[EXISTS] ${cachedStoryId} - 已存在，跳过`);
      skipped++;
      continue;
    }

    console.log(`[FETCH] ${cachedStoryId}`);
    console.log(`  URL: ${url}`);
    console.log(`  Title: ${title}`);

    try {
      const html = await fetchUrl(url);
      const text = extractText(html);

      if (!isValidContent(text)) {
        console.log(`  [FAIL] 内容无效或太短`);
        failed++;
        continue;
      }

      // 保存到临时文件
      fs.writeFileSync(tempFile, text, 'utf8');
      console.log(`  [OK] 已保存到 temp/${cachedStoryId}.txt (${text.length} 字符)`);
      success++;

    } catch (err) {
      console.log(`  [ERROR] ${err.message}`);
      failed++;
    }

    // 避免请求过快
    await new Promise(r => setTimeout(r, 500));
  }

  console.log(`\n===== 完成 =====`);
  console.log(`成功: ${success}`);
  console.log(`跳过: ${skipped}`);
  console.log(`失败: ${failed}`);
}

main().catch(console.error);
