import { editTemplate, type TextReplacement } from '../browser/edit.js';
import { ensureBrowser, persistCookies } from '../providers/playwright.js';
import { getSession } from '../session/state.js';

export interface EditTextInput {
    replacements: Record<string, string>;
    templateId?: string;
}

export interface EditTextOutput {
    message: string;
    templateId: string;
}

/**
 * 编辑设计中的文字内容
 *
 * 注意：当前实现基于 Playwright DOM 操作，稿定编辑器是 canvas-based，
 * 文字定位可能不可靠。Phase 2 需要验证并修复选择器。
 */
export async function execute(input: EditTextInput, sessionId?: string): Promise<EditTextOutput> {
    const session = getSession(sessionId);
    const templateId = input.templateId || session.selectedTemplateId;

    if (!templateId) {
        throw new Error('请先搜索并选择一个模板');
    }

    const { page } = await ensureBrowser(sessionId);

    const replacements: TextReplacement[] = Object.entries(input.replacements)
        .map(([original, replacement]) => ({ original, replacement }));

    await editTemplate(page, templateId, replacements);

    await persistCookies(sessionId);

    return {
        message: `文案已替换完成（${replacements.length} 处），回复"导出"即可下载成品`,
        templateId,
    };
}
