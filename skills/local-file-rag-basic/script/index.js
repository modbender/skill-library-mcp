const fs = require('node:fs');
const path = require('node:path');
// 屏蔽 Node.js 实验性功能警告 (如 SQLite)
process.removeAllListeners('warning');
const { FileChunker } = require('./chunker');
const { BM25SearchEngine } = require('./bm25');

/**
 * Code RAG Skill Entrance
 * 负责组装“骨骼+分片”逻辑，并执行防幻觉协议
 */
class LocalFileRAGSkill {
    constructor(initialWorkspaceDir = process.cwd()) {
        this.ensureDependencies();
        this.setupWorkspace(initialWorkspaceDir);
    }

    /**
     * 自动检测并安装缺失的文档解析依赖 (实现即用即装)
     */
    ensureDependencies() {
        const skillDir = __dirname;
        const deps = ['mammoth', 'pdf-parse', 'xlsx'];
        const missingDeps = deps.filter(dep => {
            try {
                require.resolve(dep, { paths: [path.join(skillDir, 'node_modules'), skillDir] });
                return false;
            } catch (e) {
                return true;
            }
        });

        if (missingDeps.length > 0) {
            try {
                const { execSync } = require('node:child_process');
                // 使用 --no-save 避免修改正在运行的工程 package.json
                execSync(`npm install --no-save ${missingDeps.join(' ')}`, {
                    cwd: skillDir,
                    stdio: 'ignore', // 静默安装
                    shell: true
                });
            } catch (err) {
                console.error(`[LocalFileRAG] Failed to auto-install dependencies: ${err.message}`);
                console.warn(`[LocalFileRAG] Manual install required: cd ${skillDir} && npm install`);
            }
        }
    }

    /**
     * 设置或切换当前的工作区上下文
     */
    setupWorkspace(workspaceDir) {
        this.workspaceDir = path.resolve(workspaceDir);
        this.chunker = new FileChunker(this.workspaceDir);
        this.searchEngine = new BM25SearchEngine(this.chunker.db);
    }

    /**
     * 核心公开工具：执行本地代码检索
     * @param {string} query - 搜索关键词或语义描述
     * @param {string} targetFile - 可选的限定文件路径（相对路径）
     * @param {string} rootDir - 可选的自定义根目录（支持动态切换扫描范围）
     */
    async search(query, targetFile = null, rootDir = null) {
        // 如果提供了新的 rootDir，则动态切换上下文
        if (rootDir && path.resolve(rootDir) !== path.resolve(this.workspaceDir)) {
            console.log(`[LocalFileRAG] Switching workspace to: ${rootDir}`);
            this.setupWorkspace(path.resolve(rootDir));
        }

        // 1. 增量更新/构建索引
        await this.chunker.processWorkspace();
        this.searchEngine.buildIndex();

        // 2. 执行 BM25 搜索
        const queryTokens = BM25SearchEngine.tokenize(query);
        const searchResults = this.searchEngine.search(query, 300);

        // 3. 结果预分组
        const THRESHOLD = 5.0;
        const fileCandidates = {};

        for (const res of searchResults) {
            if (res.score < THRESHOLD) continue;

            const filePath = res.chunk.filePath;
            const normalizedTarget = targetFile ? targetFile.trim().replace(/\\/g, '/') : null;
            if (normalizedTarget) {
                const cleanFilePath = filePath.toLowerCase().replace(/\s/g, '');
                const cleanTarget = normalizedTarget.toLowerCase().replace(/\s/g, '');
                if (!cleanFilePath.includes(cleanTarget)) continue;
            }

            if (!fileCandidates[filePath]) {
                fileCandidates[filePath] = {
                    maxScore: res.score,
                    chunks: []
                };
            }

            // 记录得分并存储 chunk (透传分数)
            res.chunk.score = res.score;
            fileCandidates[filePath].chunks.push(res.chunk);
        }

        // 4. 按文件最高得分排序
        const sortedFiles = Object.keys(fileCandidates)
            .sort((a, b) => fileCandidates[b].maxScore - fileCandidates[a].maxScore)
            .slice(0, targetFile ? 1 : 5);

        // 5. 组装最终结果
        let output = '';
        const MAX_FILES = 5;
        for (const filePath of sortedFiles) {
            const absPath = path.resolve(this.workspaceDir, filePath);
            const ext = path.extname(filePath).toLowerCase();
            const isTextFile = /\.(js|ts|jsx|tsx|py|go|java|cpp|c|h|hpp|vue|css|scss|less|sh|md|txt|json|yml|yaml|csv|xml|bat|ps1|sql|html)$/i.test(ext);

            if (isTextFile && fs.existsSync(absPath)) {
                const content = fs.readFileSync(absPath, 'utf8');
                const lineCount = content.split('\n').length;
                if (lineCount < 100) {
                    output += `\n--- [FILE]: ${filePath} ---\n`;
                    output += content + '\n';
                    output += `--- [END OF ${filePath}] ---\n`;
                    continue;
                }
            }

            // 挑选最相关的代码片段：聚类高分分片，确保连续性
            const matchedChunks = fileCandidates[filePath].chunks;

            // 自动补全：如果命中了函数签名，主动拉取紧随其后的实现块 (Body)
            const expandedChunks = [...matchedChunks];
            const seenStarts = new Set(matchedChunks.map(c => c.startLine));
            for (const chunk of matchedChunks) {
                if (chunk.is_signature === 1) {
                    const nextChunk = this.chunker.db.prepare('SELECT * FROM chunks WHERE filePath = ? AND startLine = ?').get(filePath, chunk.endLine + 1);
                    if (nextChunk && !seenStarts.has(nextChunk.startLine)) {
                        nextChunk.score = chunk.score * 0.9;
                        expandedChunks.push(nextChunk);
                        seenStarts.add(nextChunk.startLine);
                    }
                }
            }

            const finalChunks = expandedChunks
                .sort((a, b) => b.score - a.score)
                .slice(0, 15);

            output += this.assembleFileResult(filePath, finalChunks, queryTokens);
        }

        if (!output) return 'No relevant code snippets found in the workspace.';
        return output;
    }

    /**
     * 防幻觉协议与多模态组装逻辑
     */
    assembleFileResult(filePath, matchedChunks, queryTokens = []) {
        const absPath = path.join(this.workspaceDir, filePath);
        if (!fs.existsSync(absPath)) return '';

        const ext = path.extname(filePath).toLowerCase();

        // 分类定义
        const isCode = /\.(js|ts|jsx|tsx|py|go|java|cpp|c|h|hpp|vue|html|css|scss|less|sh)$/i.test(ext);
        const isTextDoc = /\.(txt|md|csv|json|yml|yaml|xml)$/i.test(ext);
        const isBinaryDoc = /\.(pdf|docx|xlsx|pptx)$/i.test(ext);
        const isMultimedia = /\.(png|jpg|jpeg|gif|svg|webp|mp4|webm|mp3|wav|mov|mkv)$/i.test(ext);

        let fileOutput = `\n--- [FILE]: ${filePath} ---\n`;

        // A. 二进制或多媒体：直接显示元数据
        if (isBinaryDoc || isMultimedia) {
            let metaChunk = matchedChunks.find(c => c.content.includes('[Binary Metadata]'));
            // 如果搜索结果里没带出元数据分片（可能分值不够），则从数据库补全
            if (!metaChunk) {
                metaChunk = this.chunker.db.prepare('SELECT content FROM chunks WHERE filePath = ? AND is_header = 1 LIMIT 1').get(filePath);
            }

            fileOutput += `[Type]: ${isBinaryDoc ? 'Binary Document' : 'Media Asset'}\n`;
            fileOutput += `${metaChunk ? metaChunk.content : '[Metadata Not Found]'}\n`;

            // 如果是二进制文档且有除元数据外的命中的文本内容
            if (isBinaryDoc) {
                const contentChunks = matchedChunks.filter(c => !c.content.includes('[Binary Metadata]'));
                if (contentChunks.length > 0) {
                    fileOutput += `\n// [Relevant Content Extracted]\n`;
                    contentChunks.slice(0, 3).forEach(c => {
                        let text = c.content.trim();
                        if (text.length > 1000) text = text.substring(0, 1000) + '... [Content Truncated]'; // Modified
                        fileOutput += `[Match] (Score: ${c.score.toFixed(1)}): ${text}\n`; // Modified
                    });
                } else {
                    fileOutput += `[Note]: This is a binary file; content indexing is enabled but no matching text found in this search.\n`;
                }
            }

            fileOutput += `\n--- [END OF ${filePath}] ---\n`;
            return fileOutput;
        }

        // 仅对文本/代码类文件执行读取操作
        const fullContent = fs.readFileSync(absPath, 'utf8');
        const lines = fullContent.split('\n');
        const totalLines = lines.length;
        const isSmallFile = totalLines < 100;

        // B. 小文件策略
        if ((isCode || isTextDoc) && isSmallFile) {
            fileOutput += `[Mode]: Full Context (Small File)\n`;
            lines.forEach((l, i) => { fileOutput += `L${i + 1}: ${l}\n`; });
        }
        // C. 大代码文件 RAG 模式
        else if (isCode) {
            fileOutput += `[Mode]: RAG Skeleton\n`;
            const allChunks = this.chunker.db.prepare('SELECT * FROM chunks WHERE filePath = ? ORDER BY startLine ASC').all(filePath);
            const header = allChunks.find(c => c.is_header === 1);
            const signatures = allChunks.filter(c => c.is_signature === 1);

            if (header) fileOutput += `// [Header]\n${header.content}\n`;

            fileOutput += `\n// [Structure Map]\n`;
            if (signatures.length > 40) {
                signatures.slice(0, 20).forEach(s => { fileOutput += `L${s.startLine}: ${s.content}\n`; });
                fileOutput += `// ... [${signatures.length - 30} Signatures Omitted] ...\n`;
                signatures.slice(-10).forEach(s => { fileOutput += `L${s.startLine}: ${s.content}\n`; });
            } else {
                signatures.forEach(s => { fileOutput += `L${s.startLine}: ${s.content}\n`; });
            }

            fileOutput += `\n// [Relevant Snippets (Focused)]\n`;
            fileOutput += this.renderContextChunks(absPath, matchedChunks, queryTokens);
        }
        // D. 大文本文件片段模式
        else if (isTextDoc) {
            fileOutput += `[Type]: Doc Fragments\n`;
            fileOutput += this.renderContextChunks(absPath, matchedChunks, queryTokens);
        }
        // E. 兜底
        else {
            fileOutput += `[Type]: Other\n`;
            fileOutput += this.renderContextChunks(absPath, matchedChunks, queryTokens);
        }

        fileOutput += `\n--- [END OF ${filePath}] ---\n`;
        return fileOutput;
    }

    /**
     * 高级渲染：聚类高分片段，并针对代码逻辑进行“掐头去尾”去噪
     */
    renderContextChunks(absPath, matchedChunks, queryTokens = []) {
        if (!fs.existsSync(absPath)) return '';
        const fullContent = fs.readFileSync(absPath, 'utf8');
        const lines = fullContent.split('\n');

        // 1. 聚类：将物理位置相近的命中分块合并为“窗格”
        let rawRanges = matchedChunks.map(c => ({ start: c.startLine, end: c.endLine, score: c.score }));
        rawRanges.sort((a, b) => a.start - b.start);

        const clusters = [];
        if (rawRanges.length > 0) {
            let cur = { start: rawRanges[0].start, end: rawRanges[0].end, totalScore: rawRanges[0].score };
            for (let i = 1; i < rawRanges.length; i++) {
                if (rawRanges[i].start <= cur.end + 10) { // 聚类阈值 10 行
                    cur.end = Math.max(cur.end, rawRanges[i].end);
                    cur.totalScore += rawRanges[i].score;
                } else {
                    clusters.push(cur);
                    cur = { start: rawRanges[i].start, end: rawRanges[i].end, totalScore: rawRanges[i].score };
                }
            }
            clusters.push(cur);
        }

        // 2. 排序聚类窗格：按内部总分排序，取 Top 2 (确保大块展示)
        clusters.sort((a, b) => b.totalScore - a.totalScore);
        const topClusters = clusters.slice(0, 2).sort((a, b) => a.start - b.start);

        let output = '';
        let lastPrinted = -1;

        // 3. 渲染与多维去噪
        topClusters.forEach(cluster => {
            let start = cluster.start;
            let end = cluster.end;

            // 头部裁剪：如果起始行不含关键词且属于内部逻辑特征，则裁掉直至遇到注释/签名
            while (start < end) {
                const line = lines[start - 1];
                const trimmed = line.trim();

                // 如果命中关键词，绝对保留
                const hasKeyword = queryTokens.some(t => trimmed.toLowerCase().includes(t));
                if (hasKeyword) break;

                // 如果是“结构性入口”（注释、签名特征），保留
                if (trimmed.startsWith('/**') || trimmed.startsWith('//') || trimmed.startsWith('#') ||
                    trimmed.includes('class ') || trimmed.includes('function ') || (trimmed.includes('(') && trimmed.includes('{'))) {
                    break;
                }

                // 其余情况（逻辑行、闭合行、赋值行且不含关键词）一律视为前序垃圾，裁掉
                start++;
            }

            if (lastPrinted !== -1 && start > lastPrinted + 1) {
                output += `\n// ... [Lines ${lastPrinted + 1}-${start - 1} Omitted] ...\n`;
            }

            for (let i = start; i <= end; i++) {
                output += `L${i}: ${lines[i - 1] || ''}\n`;
            }
            lastPrinted = end;
        });

        return output;
    }
}

// CLI 自测逻辑
if (require.main === module) {
    const rag = new LocalFileRAGSkill();
    const query = process.argv[2] || 'search component handle';
    const targetFile = process.argv[3] || null;
    const customRoot = process.argv[4] || null;

    rag.search(query, targetFile, customRoot).then(res => {
        console.log(res);
    });
}

module.exports = { LocalFileRAGSkill };
