import { chromium, type BrowserContext, type Page } from 'playwright';
import { loadCookies, saveCookies } from './browser/auth.js';
import { searchTemplates, type TemplateInfo } from './browser/search.js';
import { editTemplate, type TextReplacement } from './browser/edit.js';
import { exportDesign, type ExportFormat } from './browser/export.js';
import { parseDesignIntent, type DesignIntent } from './llm/intent.js';
import { saveTempImage, cleanExpiredExports } from './utils/image.js';
import { buildTemplateListCard } from './utils/feishu.js';

/** 会话状态：跟踪当前搜索结果和选中模板 */
interface SessionState {
    lastSearchResults: TemplateInfo[];
    selectedTemplateId: string | null;
    context: BrowserContext | null;
    page: Page | null;
}

const state: SessionState = {
    lastSearchResults: [],
    selectedTemplateId: null,
    context: null,
    page: null,
};

/** 初始化浏览器实例并恢复登录态 */
async function ensureBrowser(): Promise<Page> {
    if (state.page && !state.page.isClosed()) return state.page;

    const browser = await chromium.launch({ headless: true });
    state.context = await browser.newContext();
    await loadCookies(state.context);
    state.page = await state.context.newPage();
    return state.page;
}

/** 处理搜索模板请求 */
async function handleSearch(intent: DesignIntent) {
    const page = await ensureBrowser();
    const query = intent.keywords || '';
    const result = await searchTemplates(page, query);

    state.lastSearchResults = result.templates;

    // 保存截图供发送
    const screenshotPath = saveTempImage(result.screenshot, 'search');

    // 构建飞书卡片消息
    const card = buildTemplateListCard(result.templates, query);

    if (state.context) await saveCookies(state.context);

    return { screenshotPath, card, templates: result.templates };
}

/** 处理选择模板请求 */
async function handleSelect(intent: DesignIntent) {
    const idx = (intent.templateIndex ?? 1) - 1;
    const template = state.lastSearchResults[idx];

    if (!template) {
        return { error: `没有第 ${idx + 1} 个模板，当前共 ${state.lastSearchResults.length} 个结果` };
    }

    state.selectedTemplateId = template.id;
    return {
        templateId: template.id,
        title: template.title,
        message: `已选择「${template.title}」，请告诉我需要替换的文案内容`,
    };
}

/**
 * 主入口：根据用户消息分发到对应处理函数
 * OpenClaw Agent 会调用此函数处理每条用户消息
 */
export async function handleMessage(userMessage: string) {
    cleanExpiredExports();

    const intent = parseDesignIntent(userMessage);

    switch (intent.action) {
        case 'search_template':
            return handleSearch(intent);
        case 'select_template':
            return handleSelect(intent);
        case 'edit_template':
            return handleEdit(intent);
        case 'export_design':
            return handleExport(intent);
        default:
            return { error: '无法理解你的请求，请描述你想要的设计类型' };
    }
}

export { parseDesignIntent, type DesignIntent } from './llm/intent.js';
export { type TemplateInfo } from './browser/search.js';

/** 处理编辑模板请求 */
async function handleEdit(intent: DesignIntent) {
    if (!state.selectedTemplateId) {
        return { error: '请先选择一个模板' };
    }

    const page = await ensureBrowser();
    const replacements: TextReplacement[] = Object.entries(intent.replacements || {})
        .map(([original, replacement]) => ({ original, replacement }));

    await editTemplate(page, state.selectedTemplateId, replacements);

    if (state.context) await saveCookies(state.context);

    return { message: '文案已替换完成，回复"导出"即可下载成品' };
}

/** 处理导出请求 */
async function handleExport(intent: DesignIntent) {
    if (!state.selectedTemplateId) {
        return { error: '请先选择并编辑一个模板' };
    }

    const page = await ensureBrowser();
    const format = intent.exportFormat || 'png';
    const result = await exportDesign(page, format);

    if (state.context) await saveCookies(state.context);

    return {
        filePath: result.filePath,
        message: `设计已导出为 ${format.toUpperCase()}`,
    };
}