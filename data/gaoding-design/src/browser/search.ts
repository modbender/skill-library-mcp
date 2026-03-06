import type { Page } from 'playwright';

export interface TemplateInfo {
    id: string;
    title: string;
    previewUrl: string;
}

export interface SearchResult {
    screenshot: Buffer;
    templates: TemplateInfo[];
}

/** 在稿定搜索模板并返回结果 */
export async function searchTemplates(
    page: Page,
    query: string,
    maxResults = 6,
): Promise<SearchResult> {
    // 设置较大视口确保搜索按钮可见（按钮在小屏幕下隐藏）
    await page.setViewportSize({ width: 1920, height: 1080 });

    // 先打开模板页，再通过搜索框提交查询（URL ?q= 参数不生效）
    await page.goto('https://www.gaoding.com/templates', { waitUntil: 'networkidle', timeout: 30000 });

    // 在搜索框中输入关键词
    const input = page.locator('input.search-input-v1__input').first();
    await input.click();
    await input.fill(query);

    // 点击"搜索"按钮触发搜索（按钮是 type="button"，Enter 不会触发表单提交）
    const searchBtn = page.locator('button.global-search-experiment-v1__search-button').first();
    await searchBtn.click({ timeout: 5000 }).catch(async () => {
        // 按钮不可见时，通过 JS 直接触发点击
        await page.evaluate(() => {
            const btn = document.querySelector('button.global-search-experiment-v1__search-button');
            if (btn) (btn as HTMLElement).click();
        });
    });

    // 等待搜索结果页导航完成
    await page.waitForURL(/\/(scenes|templates)\/.*/, { timeout: 10000 })
        .catch((e) => console.warn('[search] URL navigation timeout:', e.message));
    await page.waitForLoadState('networkidle', { timeout: 15000 })
        .catch((e) => console.warn('[search] networkidle timeout:', e.message));

    // 等待瀑布流模板卡片加载
    await page.waitForSelector('.js-waterfall__item', { timeout: 10000 })
        .catch((e) => console.warn('[search] waterfall items not found:', e.message));

    // 截图搜索结果区域
    const screenshot = await page.screenshot({
        fullPage: false,
        type: 'png',
    });

    // 提取模板卡片信息
    const templates = await page.evaluate((max) => {
        const cards = document.querySelectorAll('.js-waterfall__item');
        return Array.from(cards).slice(0, max).map((card) => {
            const link = card.querySelector('a[href*="/template/"]') as HTMLAnchorElement | null;
            const img = card.querySelector('picture img') as HTMLImageElement | null;
            const href = link?.getAttribute('href') || '';
            const id = href.match(/\/template\/(\d+)/)?.[1] || '';
            const title = (link?.textContent?.trim() || '')
                .replace(/详情$/, '').trim();
            return {
                id,
                title,
                previewUrl: img?.src || '',
            };
        }).filter(t => t.id);
    }, maxResults);

    return { screenshot, templates };
}
