import { exportDesign, type ExportFormat } from '../browser/export.js';
import { ensureBrowser, persistCookies } from '../providers/playwright.js';
import { getSession } from '../session/state.js';

export interface ExportDesignInput {
    format?: ExportFormat;
}

export interface ExportDesignOutput {
    filePath: string;
    format: string;
    message: string;
}

/**
 * 导出当前设计为文件
 *
 * 注意：当前实现基于 Playwright DOM 操作，选择器可能需要 Phase 2 验证。
 */
export async function execute(input: ExportDesignInput, sessionId?: string): Promise<ExportDesignOutput> {
    const session = getSession(sessionId);

    if (!session.selectedTemplateId) {
        throw new Error('请先选择并编辑一个模板');
    }

    const { page } = await ensureBrowser(sessionId);
    const format = input.format || 'png';
    const result = await exportDesign(page, format);

    await persistCookies(sessionId);

    return {
        filePath: result.filePath,
        format: result.format,
        message: `设计已导出为 ${format.toUpperCase()}`,
    };
}
