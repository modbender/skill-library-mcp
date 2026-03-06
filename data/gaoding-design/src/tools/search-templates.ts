import { searchTemplates, type TemplateInfo } from '../browser/search.js';
import { ensureBrowser, persistCookies } from '../providers/playwright.js';
import { saveTempImage, cleanExpiredExports } from '../utils/image.js';
import { getSession } from '../session/state.js';

export interface SearchTemplatesInput {
    keywords: string;
    type?: string;
    max?: number;
}

export interface SearchTemplatesOutput {
    query: string;
    count: number;
    screenshotPath: string;
    templates: TemplateInfo[];
}

/** 搜索稿定设计模板 */
export async function execute(input: SearchTemplatesInput, sessionId?: string): Promise<SearchTemplatesOutput> {
    cleanExpiredExports();

    const { page } = await ensureBrowser(sessionId);
    const query = input.keywords;
    const max = input.max ?? 6;

    const result = await searchTemplates(page, query, max);

    // 保存搜索结果到会话
    const session = getSession(sessionId);
    session.lastSearchResults = result.templates;

    // 保存截图
    const screenshotPath = saveTempImage(result.screenshot, 'search');

    await persistCookies(sessionId);

    return {
        query,
        count: result.templates.length,
        screenshotPath,
        templates: result.templates,
    };
}
