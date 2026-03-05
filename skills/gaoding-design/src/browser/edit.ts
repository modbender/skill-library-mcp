import type { Page } from 'playwright';

export interface TextReplacement {
    original: string;
    replacement: string;
}

/** 打开模板编辑器并替换文字内容 */
export async function editTemplate(
    page: Page,
    templateId: string,
    replacements: TextReplacement[],
): Promise<void> {
    // 进入编辑器
    await page.goto(
        `https://www.gaoding.com/design?id=${templateId}`,
        { waitUntil: 'networkidle', timeout: 30000 },
    );

    // 等待编辑器画布就绪
    await page.waitForSelector('[class*="editor"], [class*="canvas"]', {
        timeout: 15000,
    });

    // 逐个替换文字元素
    for (const { original, replacement } of replacements) {
        // 尝试通过文本内容定位元素并双击进入编辑
        const textEl = page.locator(`text="${original}"`).first();
        const visible = await textEl.isVisible().catch(() => false);

        if (!visible) continue;

        await textEl.dblclick();
        await page.keyboard.press('ControlOrMeta+a');
        await page.keyboard.type(replacement);
        // 点击空白区域确认编辑
        await page.mouse.click(10, 10);
        await page.waitForTimeout(500);
    }
}
