const fs = require('fs');
const path = require('path');
const { extractLinks, downloadFile } = require('./scripts/extract');

function renderResponse(ctx, data) {
    return ctx.renderResponse ? ctx.renderResponse(data) : data;
}

module.exports = {
    name: 'terabox-link-extractor',
    version: '1.4.0',
    description: 'TeraBox Link Extractor - XAPIverse Edition',

    commands: {
        extract: {
            description: 'Extract direct links from a TeraBox URL',
            params: {
                url: { type: 'string', description: 'The TeraBox link to process', required: true }
            },
            handler: async (ctx) => {
                const url = ctx.params.url;
                const keys = ctx.env.TERABOX_API_KEY;
                const result = await extractLinks(url, keys);

                if (!result.success) {
                    return renderResponse(ctx, {
                        text: `❌ **Extraction Failed**\n\nSir, I encountered an issue: \`${result.error}\``
                    });
                }

                const res = result.data;
                const files = res.list || [];
                if (files.length === 0) return renderResponse(ctx, { text: '🔍 No files found in this link, Sir.' });

                let responseText = '';
                for (const file of files) {
                    responseText += `📦 **Name**: ${file.name}\n`;
                    responseText += `📁 **Type**: ${file.type || 'N/A'} | 📺 **Quality**: ${file.quality || 'N/A'}\n`;
                    responseText += `📏 **Size**: ${file.size_formatted} | ⏱️ **Duration**: ${file.duration || 'N/A'}\n`;
                    responseText += `🔗 **Links**:\n`;
                    responseText += ` - [▶️ Slow Stream](${file.stream_url})\n`;
                    if (file.fast_stream_url) {
                        Object.entries(file.fast_stream_url).forEach(([res, link]) => {
                            responseText += ` - [▶️ Fast ${res} Stream](${link})\n`;
                        });
                    }
                    responseText += ` - [⬇️ Fast Download](${file.fast_download_link || 'N/A'})\n`;
                    responseText += ` - [⬇️ Slow Download](${file.download_link})\n`;
                    responseText += `\n`;
                }

                responseText += `💳 **Credits Remaining**: ${res.free_credits_remaining}`;

                return renderResponse(ctx, { text: responseText });
            }
        }
    },

    async onMessage(ctx, next) {
        let text = ctx.message?.text?.trim();
        if (!text && ctx.callback_query?.data) text = ctx.callback_query.data;

        // Protocols are handled by LLM instructions in SKILL.md
        // This handler ensures manual commands still work and auto-detection is possible if permitted.
        if (text && (text.includes('terabox.com') || text.includes('1024tera.com'))) {
            // Let the LLM handle the consent flow as per SKILL.md instructions
            return next();
        }

        return next();
    }
};
