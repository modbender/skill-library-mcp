/**
 * PREFIX 日志格式解析器
 *
 * 输入：memory/YYYY-MM-DD.md 文件内容
 * 输出：结构化条目数组 [{ prefix, name, title, body, tags, date, raw }]
 *
 * 日志格式：
 *   ### [PREFIX:Name] Title
 *   正文（可多行）
 *   #tag1 #tag2
 */
const fs = require('fs');
const path = require('path');

const HEADER_RE = /^###\s+\[(\w+):([^\]]+)\]\s+(.+)/;
const TAG_LINE_RE = /^#[^\s#]/;

function extractTags(line) {
    const matches = line.match(/#([^\s#]+)/g);
    return matches ? matches.map(t => t.slice(1)) : [];
}

function extractDateFromFilename(filename) {
    const m = path.basename(filename).match(/^(\d{4}-\d{2}-\d{2})/);
    return m ? m[1] : null;
}

/**
 * 解析单个日志文件
 * @param {string} filePath - memory/YYYY-MM-DD.md 路径
 * @returns {Array<{prefix:string, name:string, title:string, body:string, tags:string[], date:string, raw:string, sourceLine:number}>}
 */
function parseLogFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    return parseLogContent(content, filePath);
}

/**
 * 解析日志文本内容
 * @param {string} content - 日志文本
 * @param {string} [source] - 来源文件路径
 * @returns {Array}
 */
function parseLogContent(content, source = '') {
    const lines = content.split('\n');
    const entries = [];
    let current = null;
    const date = extractDateFromFilename(source);

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const headerMatch = line.match(HEADER_RE);

        if (headerMatch) {
            if (current) {
                finalizeEntry(current);
                entries.push(current);
            }
            current = {
                prefix: headerMatch[1],
                name: headerMatch[2].trim(),
                title: headerMatch[3].trim(),
                bodyLines: [],
                tags: [],
                date: date || new Date().toISOString().slice(0, 10),
                raw: line,
                source,
                sourceLine: i + 1,
            };
        } else if (current) {
            current.raw += '\n' + line;
            if (TAG_LINE_RE.test(line)) {
                current.tags.push(...extractTags(line));
            } else if (/^#{1,2}\s/.test(line)) {
                // skip markdown section headers (# / ##) — not part of entry content
            } else {
                current.bodyLines.push(line);
            }
        }
    }

    if (current) {
        finalizeEntry(current);
        entries.push(current);
    }

    return entries;
}

function finalizeEntry(entry) {
    // 移除末尾已被识别为 tag 行的内容
    while (entry.bodyLines.length > 0) {
        const last = entry.bodyLines[entry.bodyLines.length - 1];
        if (TAG_LINE_RE.test(last) && !last.startsWith('###')) {
            entry.tags.push(...extractTags(last));
            entry.bodyLines.pop();
        } else {
            break;
        }
    }
    entry.body = entry.bodyLines.join('\n').trim();
    delete entry.bodyLines;
}

/**
 * 扫描日志目录，返回最近 N 天的日志文件路径
 * @param {string} logDir - memory/ 目录路径
 * @param {number} days - 扫描天数
 * @returns {string[]} 文件路径列表
 */
function findLogFiles(logDir, days) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffStr = cutoff.toISOString().slice(0, 10);

    try {
        return fs.readdirSync(logDir)
            .filter(f => {
                const m = f.match(/^(\d{4}-\d{2}-\d{2})\.md$/);
                return m && m[1] >= cutoffStr;
            })
            .sort()
            .map(f => path.join(logDir, f));
    } catch {
        return [];
    }
}

module.exports = { parseLogFile, parseLogContent, findLogFiles, extractTags };
