#!/usr/bin/env npx tsx
/**
 * CLI: 搜索稿定模板
 * Usage: npx tsx scripts/search.ts <关键词> [--max <数量>]
 */
import { chromium } from 'playwright';
import { searchTemplates } from '../src/browser/search.js';
import { ensureLoggedIn } from '../src/browser/auth.js';
import { writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const args = process.argv.slice(2);
const query = args.filter(a => !a.startsWith('--'))[0];
const maxIdx = args.indexOf('--max');
const max = maxIdx >= 0 ? parseInt(args[maxIdx + 1], 10) : 6;

if (!query) {
    console.error('Usage: npx tsx scripts/search.ts <关键词> [--max <数量>]');
    process.exit(1);
}

const OUT_DIR = path.join(os.homedir(), '.openclaw', 'skills', 'gaoding-design', 'output');
mkdirSync(OUT_DIR, { recursive: true });

async function main() {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    await ensureLoggedIn(context);
    const page = await context.newPage();

    try {
        const result = await searchTemplates(page, query, max);

        // 保存截图
        const screenshotPath = path.join(OUT_DIR, 'search-result.png');
        writeFileSync(screenshotPath, result.screenshot);

        // 输出 JSON 结果
        const output = {
            query,
            count: result.templates.length,
            screenshotPath,
            templates: result.templates,
        };
        console.log(JSON.stringify(output, null, 2));
    } finally {
        await browser.close();
    }
}

main().catch(err => {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
});
