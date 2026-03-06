/**
 * KB 文件写入器
 * 将条目追加到目标 kb/ 文件末尾，自动创建目录
 */
const fs = require('fs');
const path = require('path');

/**
 * 将条目格式化为 kb 存储格式
 * @param {object} entry - 解析后的日志条目
 * @returns {string} 格式化后的文本块
 */
function formatEntry(entry) {
    const lines = [];
    lines.push(`### [${entry.prefix}] ${entry.title}`);

    if (entry.body) {
        lines.push(entry.body);
    }

    const tagStr = entry.tags.length > 0
        ? entry.tags.map(t => `#${t}`).join(' ')
        : '';
    const source = `来源: ${entry.date} 日志`;
    lines.push(tagStr ? `${source} | ${tagStr}` : source);

    return lines.join('\n');
}

/**
 * 追加条目到目标文件
 * @param {string} targetPath - 目标 kb/ 文件路径
 * @param {object} entry - 日志条目
 * @param {boolean} [dryRun=false] - 预览模式不写入
 * @returns {{ targetPath: string, content: string }}
 */
function appendEntry(targetPath, entry, dryRun = false) {
    const formatted = formatEntry(entry);

    if (!dryRun) {
        const dir = path.dirname(targetPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        const separator = fs.existsSync(targetPath) ? '\n\n' : '';
        const existing = separator ? fs.readFileSync(targetPath, 'utf-8') : '';
        const header = existing ? '' : `# ${path.basename(targetPath, '.md')}\n\n`;

        fs.appendFileSync(targetPath, `${separator}${header}${formatted}\n`, 'utf-8');
    }

    return { targetPath, content: formatted };
}

/**
 * 批量导入条目（从 draft 文件）
 * @param {string} draftPath - 草稿文件路径
 * @param {object} config
 * @param {Function} classifyFn - 分类函数
 * @param {object} state - 去重状态
 * @param {Function} dedupFn - 去重检查函数
 * @returns {{ imported: number, skipped: number, results: Array }}
 */
function importDraft(draftPath, config, classifyFn, state, dedupFn) {
    const { parseLogContent } = require('./parser');
    const content = fs.readFileSync(draftPath, 'utf-8');
    const entries = parseLogContent(content, draftPath);
    const results = [];
    let imported = 0, skipped = 0;

    for (const entry of entries) {
        const { isDuplicate, hash } = dedupFn(entry, state);
        if (isDuplicate) {
            skipped++;
            continue;
        }

        const targetPath = classifyFn(entry, config);
        appendEntry(targetPath, entry);
        state.hashes[hash] = targetPath;
        imported++;
        results.push({ title: entry.title, targetPath });
    }

    return { imported, skipped, results };
}

module.exports = { formatEntry, appendEntry, importDraft };
