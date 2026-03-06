import type { TemplateInfo } from '../browser/search.js';

/** 构建模板搜索结果的飞书消息卡片 JSON */
export function buildTemplateListCard(
    templates: TemplateInfo[],
    query: string,
) {
    const elements = templates.map((t, i) => ({
        tag: 'div',
        text: {
            tag: 'lark_md',
            content: `**${i + 1}.** ${t.title || '未命名模板'}\n[查看预览](${t.previewUrl})`,
        },
    }));

    return {
        msg_type: 'interactive',
        card: {
            header: {
                title: { tag: 'plain_text', content: `🎨 "${query}" 模板搜索结果` },
                template: 'blue',
            },
            elements: [
                ...elements,
                { tag: 'hr' },
                {
                    tag: 'note',
                    elements: [{
                        tag: 'plain_text',
                        content: '回复"用第N个"选择模板',
                    }],
                },
            ],
        },
    };
}
