import { captureTemplatePreview } from '../browser/preview.js';
import { ensureBrowser, persistCookies } from '../providers/playwright.js';
import { saveTempImage } from '../utils/image.js';
import { getSession } from '../session/state.js';

export interface PreviewDesignInput {
    templateId?: string;
}

export interface PreviewDesignOutput {
    screenshotPath: string;
    templateId: string;
}

/** 预览模板或当前设计 */
export async function execute(input: PreviewDesignInput, sessionId?: string): Promise<PreviewDesignOutput> {
    const session = getSession(sessionId);
    const templateId = input.templateId || session.selectedTemplateId;

    if (!templateId) {
        throw new Error('请先搜索并选择一个模板');
    }

    const { page } = await ensureBrowser(sessionId);
    const screenshot = await captureTemplatePreview(page, templateId);
    const screenshotPath = saveTempImage(screenshot, 'preview');

    await persistCookies(sessionId);

    return { screenshotPath, templateId };
}
