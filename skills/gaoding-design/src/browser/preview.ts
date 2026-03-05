import type { Page } from 'playwright';

/** 截取单个模板的预览图 */
export async function captureTemplatePreview(
    page: Page,
    templateId: string,
): Promise<Buffer> {
    const url = `https://www.gaoding.com/template/${templateId}`;
    await page.goto(url, { waitUntil: 'networkidle' });

    // 等待预览图加载
    await page.waitForSelector('.contents-material-preview, [class*="preview"], [class*="canvas"]', {
        timeout: 10000,
    }).catch(() => null);

    return page.screenshot({ fullPage: false, type: 'png' });
}
