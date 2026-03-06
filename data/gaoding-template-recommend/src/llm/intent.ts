/** 用户意图解析结果 */
export interface DesignIntent {
    action: 'search_template' | 'select_template' | 'edit_template' | 'export_design';
    keywords?: string;
    category?: string;
    style?: string;
    size?: { width: number; height: number } | null;
    templateIndex?: number;
    replacements?: Record<string, string>;
    exportFormat?: 'png' | 'jpg' | 'pdf';
}

/**
 * 从用户自然语言中提取设计意图
 * 实际运行时由 OpenClaw Agent 的 LLM 层完成解析，
 * 这里提供结构定义和 fallback 的关键词匹配逻辑
 */
export function parseDesignIntent(userMessage: string): DesignIntent {
    const msg = userMessage.trim();

    // 选择模板：匹配 "用第N个"、"选N"
    const selectMatch = msg.match(/(?:用|选|要).*?第?\s*(\d+)/);
    if (selectMatch) {
        return {
            action: 'select_template',
            templateIndex: parseInt(selectMatch[1], 10),
        };
    }

    // 导出：匹配 "导出"、"下载"
    if (/导出|下载|发给我|发我/.test(msg)) {
        const format = /pdf/i.test(msg) ? 'pdf' : /jpg|jpeg/i.test(msg) ? 'jpg' : 'png';
        return { action: 'export_design', exportFormat: format };
    }

    // 编辑：匹配 "改成"、"替换"、"换成"
    if (/改成|替换|换成|修改/.test(msg)) {
        const replacements: Record<string, string> = {};
        // 简单匹配 "A改成B" 模式
        const pairs = msg.matchAll(/[""「]?(.+?)[""」]?\s*(?:改成|替换为?|换成)\s*[""「]?(.+?)[""」]?(?:[，,;；]|$)/g);
        for (const m of pairs) {
            replacements[m[1].trim()] = m[2].trim();
        }
        return { action: 'edit_template', replacements };
    }

    // 默认：搜索模板
    return {
        action: 'search_template',
        keywords: msg,
    };
}
