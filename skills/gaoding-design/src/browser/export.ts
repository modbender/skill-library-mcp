import type { Page } from 'playwright';
import path from 'node:path';
import os from 'node:os';

export type ExportFormat = 'png' | 'jpg' | 'pdf';

export interface ExportResult {
    filePath: string;
    format: ExportFormat;
}

const EXPORT_DIR = path.join(os.homedir(), '.openclaw', 'skills', 'gaoding-design', 'exports');

/** 导出当前编辑器中的设计 */
export async function exportDesign(
    page: Page,
    format: ExportFormat = 'png',
): Promise<ExportResult> {
    // 点击下载/导出按钮
    const downloadBtn = page.locator('[class*="download"], [data-action="download"]').first();
    await downloadBtn.click();

    // 等待导出弹窗
    await page.waitForSelector('[class*="export"], [class*="download-dialog"]', {
        timeout: 5000,
    }).catch(() => null);

    // 选择导出格式
    const formatBtn = page.locator(`[data-format="${format}"], text="${format.toUpperCase()}"`).first();
    const formatVisible = await formatBtn.isVisible().catch(() => false);
    if (formatVisible) {
        await formatBtn.click();
    }

    // 监听下载事件
    const downloadPromise = page.waitForEvent('download', { timeout: 30000 });

    // 点击确认导出
    const confirmBtn = page.locator('[class*="confirm"], [class*="submit"], text="下载"').first();
    await confirmBtn.click();

    const download = await downloadPromise;
    const filePath = path.join(EXPORT_DIR, download.suggestedFilename());
    await download.saveAs(filePath);

    return { filePath, format };
}
