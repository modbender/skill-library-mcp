/**
 * 冒烟测试：验证搜索模板流程
 */
import { chromium } from 'playwright';
import { searchTemplates } from '../src/browser/search.js';
import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

async function smokeTest() {
    console.log('=== 搜索模板冒烟测试 ===\n');

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        console.log('1. 搜索「电商海报」...');
        const result = await searchTemplates(page, '电商海报');

        console.log(`   截图大小: ${result.screenshot.length} bytes`);
        console.log(`   找到模板: ${result.templates.length} 个\n`);

        for (const t of result.templates) {
            console.log(`   - [${t.id}] ${t.title}`);
            console.log(`     预览: ${t.previewUrl.slice(0, 80)}...`);
        }

        // 保存截图
        const __dirname = path.dirname(fileURLToPath(import.meta.url));
        const outPath = path.join(__dirname, 'smoke-test-result.png');
        writeFileSync(outPath, Uint8Array.from(result.screenshot));
        console.log(`\n   截图已保存: ${outPath}`);

        if (result.templates.length > 0) {
            console.log('\n✅ 冒烟测试通过');
        } else {
            console.log('\n⚠️  搜索成功但未提取到模板信息，选择器可能需要调整');
        }
    } catch (err: any) {
        console.error('\n❌ 冒烟测试失败:', err.message);
    } finally {
        await browser.close();
    }
}

smokeTest();
