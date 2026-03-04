#!/usr/bin/env node

/**
 * Daily Briefing: 获取数据并分组整理
 * - 拉取 https://www.mixdao.world/api/latest（需环境变量 MIXDAO_API_KEY，Bearer token）
 * - 解析并扁平化，按 source 分组，输出每组条目的完整信息（id、标题、摘要、URL）
 * - 可选：将原始数据保存到 temp/ 目录
 *
 * 用法: node scripts/01-fetch.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';

const __dirname = path.dirname(fileURLToPath(
    import.meta.url));
const API_URL = 'https://www.mixdao.world/api/latest';
const SKIP_KEYS = new Set(['sources', 'sourceLabels', 'hasMore', 'date']);

/** 与 api/latest 一致：日期按 Asia/Shanghai */
const DATE_TZ = 'Asia/Shanghai';

function getTodayDateStrInTz(tz) {
    return new Intl.DateTimeFormat('en-CA', {
        timeZone: tz,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    }).format(new Date());
}

function fetchLatest() {
    return new Promise((resolve, reject) => {
        const apiKey = process.env.MIXDAO_API_KEY;
        if (!apiKey) {
            reject(new Error('MIXDAO_API_KEY is not set.'));
            return;
        }
        const url = new URL(API_URL);
        const opts = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: 'GET',
            headers: { Authorization: `Bearer ${apiKey}` },
        };
        const req = https.request(opts, (res) => {
            res.setTimeout(15000, () => {
                req.destroy();
                reject(new Error('API 请求超时'));
            });
            const chunks = [];
            res.on('data', (c) => chunks.push(c));
            res.on('end', () => {
                const body = Buffer.concat(chunks).toString('utf8');
                if (res.statusCode !== 200) {
                    reject(new Error(`API returned ${res.statusCode}: ${body.slice(0, 200)}`));
                    return;
                }
                try {
                    resolve(JSON.parse(body));
                } catch (e) {
                    reject(new Error('Invalid JSON from API: ' + e.message));
                }
            });
        });
        req.on('error', reject);
        req.end();
    });
}

/** API 返回：{ hn: [], arxiv: [], ... }，扁平化为统一 id、标题、摘要等 */
function flatten(data) {
    const out = [];
    for (const key of Object.keys(data)) {
        if (SKIP_KEYS.has(key)) continue;
        const arr = Array.isArray(data[key]) ? data[key] : [];
        if (!arr.length) continue;
        for (const item of arr) {
            if (!item || (!item.title && !item.translatedTitle)) continue;
            const title = (item.title || item.translatedTitle || '').replace(/&#8217;/g, "'");
            const translatedTitle = (item.translatedTitle || item.title || '').replace(/&#8217;/g, "'");
            const url = item.url || item.link || '';
            if (!url && !title) continue;
            const id = item.cachedStoryId
            if (id) {
                out.push({
                    id,
                    title,
                    translatedTitle,
                    text: (item.text || '').trim(),
                    url
                });
            }

        }
    }
    return out;
}

function main() {
    fetchLatest()
        .then((raw) => {
            const date = raw.date || getTodayDateStrInTz(DATE_TZ);
            const items = flatten(raw);
            if (!items.length) {
                console.error('01-fetch.js: no items from API');
                process.exit(1);
            }
            const tempFileName = `briefing-${date}.json`;
            const tempFilePath = path.join(__dirname, '..', 'temp', tempFileName);

            const tempDir = path.join(__dirname, '..', 'temp');
            if (!fs.existsSync(tempDir)) {
                fs.mkdirSync(tempDir, { recursive: true });
            }

            const outputData = { date, items };

            fs.writeFileSync(tempFilePath, JSON.stringify(outputData, null, 2), 'utf8');

            console.log(`[FILE PATH] ${tempFilePath}`);
        })
        .catch((err) => {
            console.error('Error:', err.message);
            process.exit(1);
        });
}

main();