/**
 * 知识摘要 + 空白检测
 * 纯本地统计，不调 LLM
 */
const fs = require('fs');
const path = require('path');

const ENTRY_HEADER_RE = /^### \[/;

/**
 * 统计单个 kb/ 文件的条目数和日期范围
 * @param {string} filePath
 * @returns {{ count: number, newest: string|null, oldest: string|null }}
 */
function analyzeFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content.split('\n');
        let count = 0;
        const dates = [];

        for (const line of lines) {
            if (ENTRY_HEADER_RE.test(line)) count++;
            const dateMatch = line.match(/(\d{4}-\d{2}-\d{2})/);
            if (dateMatch) dates.push(dateMatch[1]);
        }

        dates.sort();
        return {
            count,
            newest: dates.length > 0 ? dates[dates.length - 1] : null,
            oldest: dates.length > 0 ? dates[0] : null,
        };
    } catch {
        return { count: 0, newest: null, oldest: null };
    }
}

/**
 * 递归扫描 kb/ 目录，统计每个子目录/文件
 * @param {string} kbDir
 * @returns {object[]} [{ path, relativePath, ...stats }]
 */
function scanKbDir(kbDir) {
    const results = [];

    function walk(dir, rel) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            const relPath = path.join(rel, entry.name);

            if (entry.isDirectory()) {
                walk(fullPath, relPath);
            } else if (entry.name.endsWith('.md')) {
                const stats = analyzeFile(fullPath);
                results.push({ path: fullPath, relativePath: relPath, ...stats });
            }
        }
    }

    try {
        walk(kbDir, '');
    } catch {
        // kb/ 目录不存在
    }

    return results;
}

/**
 * 从日志文件中提取提到的项目/领域名称
 * @param {string} logDir
 * @param {number} days
 * @returns {Set<string>}
 */
function extractMentionedTopics(logDir, days) {
    const topics = new Set();
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffStr = cutoff.toISOString().slice(0, 10);

    try {
        const files = fs.readdirSync(logDir).filter(f => {
            const m = f.match(/^(\d{4}-\d{2}-\d{2})\.md$/);
            return m && m[1] >= cutoffStr;
        });

        for (const f of files) {
            const content = fs.readFileSync(path.join(logDir, f), 'utf-8');
            const matches = content.matchAll(/### \[\w+:([^\]]+)\]/g);
            for (const m of matches) {
                topics.add(m[1].trim());
            }
        }
    } catch {
        // 目录不存在
    }

    return topics;
}

/**
 * 生成知识摘要
 * @param {object} config
 * @param {object} options - { updateIndex?: boolean }
 * @returns {string} 格式化的摘要文本
 */
function generateDigest(config, options = {}) {
    const fileStats = scanKbDir(config._kbDirAbs);
    const totalEntries = fileStats.reduce((sum, f) => sum + f.count, 0);

    const allDates = fileStats
        .map(f => f.newest)
        .filter(Boolean)
        .sort();
    const newestDate = allDates.length > 0 ? allDates[allDates.length - 1] : '无';

    const lines = [
        '=== 知识库摘要 ===',
        `总条目数: ${totalEntries}`,
        `最近入库: ${newestDate}`,
        `KB 文件数: ${fileStats.length}`,
        '',
        '分布:',
    ];

    const dirStats = new Map();
    for (const f of fileStats) {
        const dir = path.dirname(f.relativePath) || '.';
        if (!dirStats.has(dir)) {
            dirStats.set(dir, { count: 0, newest: null, files: 0 });
        }
        const s = dirStats.get(dir);
        s.count += f.count;
        s.files++;
        if (!s.newest || (f.newest && f.newest > s.newest)) {
            s.newest = f.newest;
        }
    }

    for (const [dir, stats] of [...dirStats.entries()].sort()) {
        const dirName = dir === '.' ? '根目录' : `${dir}/`;
        const dateInfo = stats.newest ? `最新: ${stats.newest}` : '';
        lines.push(`  ${dirName.padEnd(16)} ${String(stats.count).padStart(3)} 条  ${stats.files} 个文件  ${dateInfo}`);
    }

    // 空白检测
    const topics = extractMentionedTopics(config._logDirAbs, 30);
    const kbFileNames = new Set(
        fileStats.map(f => path.basename(f.relativePath, '.md').toLowerCase())
    );

    const gaps = [];
    for (const topic of topics) {
        const normalized = topic.toLowerCase().replace(/\s+/g, '-');
        if (!kbFileNames.has(normalized)) {
            gaps.push(topic);
        }
    }

    if (gaps.length > 0) {
        lines.push('');
        lines.push('可能的知识空白:');
        for (const gap of gaps.slice(0, 10)) {
            lines.push(`  - 日志提到「${gap}」但 kb/ 无对应文件`);
        }
    }

    const digestText = lines.join('\n');

    if (options.updateIndex) {
        updateKbIndex(config, fileStats, totalEntries, newestDate);
    }

    return digestText;
}

/**
 * 更新 kb-index.md 知识注册表
 */
function updateKbIndex(config, fileStats, totalEntries, newestDate) {
    const indexPath = path.join(config._kbDirAbs, '..', 'kb-index.md');
    const lines = [
        '# 知识注册表',
        '',
        `> 自动生成于 ${new Date().toISOString().slice(0, 19)}，共 ${totalEntries} 条知识`,
        '',
        '| 文件 | 条目数 | 最新日期 |',
        '|------|--------|----------|',
    ];

    for (const f of fileStats.sort((a, b) => a.relativePath.localeCompare(b.relativePath))) {
        lines.push(`| ${f.relativePath} | ${f.count} | ${f.newest || '-'} |`);
    }

    lines.push('');
    fs.writeFileSync(indexPath, lines.join('\n'), 'utf-8');
}

module.exports = { generateDigest, scanKbDir, analyzeFile };
