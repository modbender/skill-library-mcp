import { getSession } from '../session/state.js';

export interface SelectTemplateInput {
    index: number;
}

export interface SelectTemplateOutput {
    templateId: string;
    title: string;
    previewUrl: string;
    message: string;
}

/** 从搜索结果中选择一个模板 */
export async function execute(input: SelectTemplateInput, sessionId?: string): Promise<SelectTemplateOutput> {
    const session = getSession(sessionId);
    const idx = input.index - 1; // 用户从 1 开始计数

    if (idx < 0 || idx >= session.lastSearchResults.length) {
        throw new Error(`没有第 ${input.index} 个模板，当前共 ${session.lastSearchResults.length} 个结果`);
    }

    const template = session.lastSearchResults[idx];
    session.selectedTemplateId = template.id;

    return {
        templateId: template.id,
        title: template.title,
        previewUrl: template.previewUrl,
        message: `已选择「${template.title}」，请告诉我需要修改的内容`,
    };
}
