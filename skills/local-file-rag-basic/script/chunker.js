const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

// 移除顶层 require，改为延迟加载以适配自动安装
let pdfParser = null;
let mammoth = null;
let XLSX = null;

class FileChunker {
    constructor(workspaceDir) {
        this.workspaceDir = workspaceDir;
        this.dbDir = path.join(workspaceDir, '.storage');
        if (!fs.existsSync(this.dbDir)) {
            fs.mkdirSync(this.dbDir, { recursive: true });
        }
        this.dbPath = path.join(this.dbDir, 'code-rag.db');
        this.db = new DatabaseSync(this.dbPath);
        this.initDb();
    }

    /**
     * 延迟加载可选依赖，确保在 npm install 后能正确获取
     */
    loadOptionalDeps() {
        if (pdfParser && mammoth && XLSX) return true;
        try {
            const skillNodeModules = path.join(__dirname, 'node_modules');

            // 优先尝试从本级 node_modules 加载
            if (!pdfParser) {
                try { pdfParser = require(path.join(skillNodeModules, 'pdf-parse')); } catch (e) { }
            }
            if (!mammoth) {
                try { mammoth = require(path.join(skillNodeModules, 'mammoth')); } catch (e) { }
            }
            if (!XLSX) {
                try { XLSX = require(path.join(skillNodeModules, 'xlsx')); } catch (e) { }
            }

            if (pdfParser && mammoth && XLSX) return true;

            // 兜底：尝试全局/父级 require
            if (!pdfParser) { try { pdfParser = require('pdf-parse'); } catch (e) { } }
            if (!mammoth) { try { mammoth = require('mammoth'); } catch (e) { } }
            if (!XLSX) { try { XLSX = require('xlsx'); } catch (e) { } }

            return !!(pdfParser || mammoth || XLSX);
        } catch (err) {
            return !!(pdfParser || mammoth || XLSX);
        }
    }

    initDb() {
        // 创建文件指纹表和分片表
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS files(
                filePath TEXT PRIMARY KEY,
                mtimeMs REAL
            );
            CREATE TABLE IF NOT EXISTS chunks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filePath TEXT,
                startLine INTEGER,
                endLine INTEGER,
                content TEXT,
                is_header INTEGER,
                is_signature INTEGER,
                FOREIGN KEY(filePath) REFERENCES files(filePath) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunks(filePath);
        `);
    }

    /**
     * 自底向上扫描工作区并进行增量切片
     */
    async processWorkspace() {
        const files = this.walkDir(this.workspaceDir);
        for (const file of files) {
            try {
                await this.processFile(file);
            } catch (e) {
                console.error(`[LocalFileRAG] Error processing file ${file}:`, e);
            }
        }
    }

    walkDir(dir, fileList = []) {
        if (!fs.existsSync(dir)) return fileList;
        const files = fs.readdirSync(dir);

        for (const file of files) {
            // 过滤无用目录
            if (['node_modules', '.git', 'dist', 'build', '.storage', '.agents', '.openclaw', '.vscode'].includes(file)) continue;

            const absolutePath = path.join(dir, file);
            const stat = fs.statSync(absolutePath);

            if (stat.isDirectory()) {
                this.walkDir(absolutePath, fileList);
            } else {
                const ext = path.extname(file).toLowerCase();
                const isSupported = /\.(js|ts|jsx|tsx|py|html|vue|css|scss|less|md|json|yml|yaml|go|java|cpp|c|h|hpp|txt|csv|pdf|docx|xlsx|pptx|png|jpg|jpeg|gif|svg|webp|mp4|webm|mp3|wav|mov|mkv)$/i.test(file);
                if (isSupported) {
                    fileList.push(absolutePath);
                }
            }
        }
        return fileList;
    }

    /**
     * 单文件处理：支持文本解析、二进制元数据嗅探及深度文档提取
     */
    async processFile(absolutePath) {
        const relativePath = path.relative(this.workspaceDir, absolutePath).replace(/\\/g, '/');
        const stats = fs.statSync(absolutePath);

        // [Performance Guard] 限制：为保证检索流畅性，默认仅扫描 20MB 以内的文件
        const MAX_SIZE = 20 * 1024 * 1024;
        if (stats.size > MAX_SIZE) {
            console.log(`[LocalFileRAG] Skipping oversized file (>20MB): ${relativePath}`);
            return;
        }

        const mtimeMs = stats.mtimeMs;

        const fileRow = this.db.prepare('SELECT mtimeMs FROM files WHERE filePath = ?').get(relativePath);
        if (fileRow && fileRow.mtimeMs === mtimeMs) return;

        const ext = path.extname(absolutePath).toLowerCase();
        let chunks = [];

        // 区分文本、深度文档和普通二进制
        const isText = /\.(js|ts|jsx|tsx|py|html|vue|css|scss|less|md|json|yml|yaml|go|java|cpp|c|h|hpp|txt|csv|svg|xml)$/i.test(ext);
        const isDeepDoc = /\.(pdf|docx|xlsx|xls)$/i.test(ext);

        // 总是生成基础元数据
        const metadata = this.sniffMetadata(absolutePath, ext, stats);
        chunks.push({
            startLine: 1,
            endLine: 1,
            content: `[Binary Metadata] ${JSON.stringify(metadata, null, 2)}`,
            is_header: 1,
            is_signature: 1
        });

        if (isText) {
            const content = fs.readFileSync(absolutePath, 'utf8');
            const isCode = /\.(js|ts|jsx|tsx|py|go|java|cpp|c|h|hpp|vue|css|scss|less|sh)$/i.test(ext);
            if (isCode) {
                chunks.push(...this.chunkCode(content, relativePath));
            } else {
                chunks.push(...this.chunkDocument(content, relativePath));
            }
        } else if (isDeepDoc) {
            try {
                if (this.loadOptionalDeps()) {
                    let text = '';
                    if (ext === '.pdf' && pdfParser) {
                        const dataBuffer = fs.readFileSync(absolutePath);
                        const data = await pdfParser(dataBuffer);
                        text = data.text;
                    } else if (ext === '.docx' && mammoth) {
                        const result = await mammoth.extractRawText({ path: absolutePath });
                        text = result.value;
                    } else if ((ext === '.xlsx' || ext === '.xls') && XLSX) {
                        const workbook = XLSX.readFile(absolutePath);
                        text = workbook.SheetNames.map(name => {
                            const sheet = workbook.Sheets[name];
                            return `--- Sheet: ${name} ---\n` + XLSX.utils.sheet_to_csv(sheet);
                        }).join('\n\n');
                    }

                    if (text.trim()) {
                        chunks.push(...this.chunkDocument(text, relativePath));
                    }
                }
            } catch (e) {
                console.error(`[LocalFileRAG] Failed to extract text from ${relativePath}:`, e);
            }
        }

        this.db.exec('BEGIN EXCLUSIVE TRANSACTION');
        try {
            this.db.prepare('DELETE FROM files WHERE filePath = ?').run(relativePath);
            this.db.prepare('DELETE FROM chunks WHERE filePath = ?').run(relativePath);
            this.db.prepare('INSERT INTO files (filePath, mtimeMs) VALUES (?, ?)').run(relativePath, mtimeMs);

            const insertChunk = this.db.prepare('INSERT INTO chunks (filePath, startLine, endLine, content, is_header, is_signature) VALUES (?, ?, ?, ?, ?, ?)');
            for (const chunk of chunks) {
                insertChunk.run(relativePath, chunk.startLine, chunk.endLine, chunk.content, chunk.is_header, chunk.is_signature);
            }
            this.db.exec('COMMIT');
        } catch (e) {
            this.db.exec('ROLLBACK');
            throw e;
        }
    }

    sniffMetadata(filePath, ext, stats) {
        const info = {
            fileName: path.basename(filePath),
            extension: ext,
            sizeBytes: stats.size,
            lastModified: new Date(stats.mtime).toISOString()
        };

        try {
            const fd = fs.openSync(filePath, 'r');
            const buffer = Buffer.alloc(100);
            fs.readSync(fd, buffer, 0, 100, 0);
            fs.closeSync(fd);

            if (ext === '.png') {
                info.type = 'Image (PNG)';
                info.width = buffer.readUInt32BE(16);
                info.height = buffer.readUInt32BE(20);
            } else if (ext === '.jpg' || ext === '.jpeg') {
                info.type = 'Image (JPEG)';
            } else if (ext === '.gif') {
                info.type = 'Image (GIF)';
                info.width = buffer.readUInt16LE(6);
                info.height = buffer.readUInt16LE(8);
            } else if (ext === '.pdf') {
                info.type = 'Document (PDF)';
                const head = buffer.toString('utf8', 0, 10);
                if (head.startsWith('%PDF-')) info.pdfVersion = head.split('\n')[0];
            } else if (['.docx', '.xlsx', '.pptx', '.xls'].includes(ext)) {
                info.type = 'Office Open XML / Binary (Compressed)';
            }
        } catch (e) { }
        return info;
    }

    chunkCode(content, relativePath) {
        const lines = content.split('\n');
        const chunks = [];
        let headerEndLineIndex = -1;

        for (let i = 0; i < Math.min(lines.length, 30); i++) {
            const line = lines[i];
            const trimmed = line.trim();
            if (/^(?:import|require|export|from|#include|using|package)\b/.test(trimmed) ||
                trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*') || trimmed === '') {
                headerEndLineIndex = i;
            } else {
                break;
            }
        }

        if (headerEndLineIndex >= 0) {
            chunks.push({
                startLine: 1,
                endLine: headerEndLineIndex + 1,
                content: lines.slice(0, headerEndLineIndex + 1).join('\n'),
                is_header: 1,
                is_signature: 0
            });
        }

        const ext = path.extname(relativePath).toLowerCase();
        let buffer = [];
        let bufferStartLine = headerEndLineIndex + 2;
        let braceDepth = 0, inBraceBlock = false;
        let inPythonBlock = false, pyBaseIndent = 0;

        for (let i = headerEndLineIndex + 1; i < lines.length; i++) {
            const line = lines[i], trimmed = line.trim(), realLineNum = i + 1;

            const isJsSig = /^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:class|function)\s+[A-Za-z0-9_]+/.test(trimmed) ||
                /^(?:export\s+)?(?:const|let|var)\s+[A-Za-z0-9_]+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>/.test(trimmed) ||
                /^[A-Za-z0-9_]+\s*\([^)]*\)\s*\{/.test(trimmed);
            const isPySig = /^(?:async\s+)?(?:def|class)\s+[A-Za-z0-9_]+/.test(trimmed);

            if (isJsSig || isPySig) {
                if (buffer.length > 0 && realLineNum > bufferStartLine) {
                    const shouldSplit = (ext !== '.py' && braceDepth === 1) || (ext === '.py' && inPythonBlock);
                    if (shouldSplit) {
                        chunks.push({ startLine: bufferStartLine, endLine: realLineNum - 1, content: buffer.join('\n').trim(), is_header: 0, is_signature: 0 });
                        buffer = [];
                        bufferStartLine = realLineNum;
                    }
                }
                chunks.push({ startLine: realLineNum, endLine: realLineNum, content: line, is_header: 0, is_signature: 1 });
            }

            buffer.push(line);

            if (ext === '.py') {
                if (!inPythonBlock && isPySig) { inPythonBlock = true; pyBaseIndent = line.search(/\S|$/); }
                else if (inPythonBlock && trimmed !== '') {
                    const indent = line.search(/\S|$/);
                    if (indent <= pyBaseIndent) {
                        const lastLine = buffer.pop();
                        if (buffer.length > 0) chunks.push({ startLine: bufferStartLine, endLine: i, content: buffer.join('\n'), is_header: 0, is_signature: 0 });
                        buffer = [lastLine]; bufferStartLine = realLineNum;
                        if (isPySig) pyBaseIndent = indent; else inPythonBlock = false;
                    }
                }
            } else {
                const open = (line.match(/\{/g) || []).length, close = (line.match(/\}/g) || []).length;
                if (!inBraceBlock && (isJsSig || open > 0)) inBraceBlock = true;
                braceDepth += open; braceDepth -= close;

                if (inBraceBlock && braceDepth <= 0) {
                    chunks.push({ startLine: bufferStartLine, endLine: realLineNum, content: buffer.join('\n'), is_header: 0, is_signature: 0 });
                    buffer = []; bufferStartLine = realLineNum + 1; inBraceBlock = false; braceDepth = 0;
                } else if (inBraceBlock && braceDepth === 1 && trimmed === '' && buffer.length > 60) {
                    // 当在大函数内部遇到空行且长度超过 60 行时才允许切分，且不保留重叠
                    chunks.push({ startLine: bufferStartLine, endLine: realLineNum, content: buffer.join('\n'), is_header: 0, is_signature: 0 });
                    buffer = [];
                    bufferStartLine = realLineNum + 1;
                } else if (!inBraceBlock && (trimmed === '' && buffer.length > 80)) {
                    // 类外逻辑，超过 80 行才允许切分
                    chunks.push({ startLine: bufferStartLine, endLine: realLineNum, content: buffer.join('\n'), is_header: 0, is_signature: 0 });
                    buffer = [];
                    bufferStartLine = realLineNum + 1;
                }
            }
        }
        if (buffer.length > 0) chunks.push({ startLine: bufferStartLine, endLine: lines.length, content: buffer.join('\n'), is_header: 0, is_signature: 0 });
        return chunks;
    }

    chunkDocument(content, relativePath) {
        const paragraphs = content.split(/\n\s*\n/);
        const chunks = [];
        let currentLine = 1;
        const OVERLAP = 5;

        for (const para of paragraphs) {
            const trimmedPara = para.trim();
            if (!trimmedPara) continue;

            const paraLines = para.split('\n');
            const lineCount = paraLines.length;

            if (trimmedPara.length < 2500 && lineCount < 60) {
                chunks.push({ startLine: currentLine, endLine: currentLine + lineCount - 1, content: trimmedPara, is_header: 0, is_signature: 0 });
            } else {
                const CHUNK_SIZE = 50;
                for (let i = 0; i < paraLines.length; i += CHUNK_SIZE) {
                    const slice = paraLines.slice(i, i + CHUNK_SIZE);
                    if (slice.length < 5 && i > 0) break;
                    chunks.push({ startLine: currentLine + i, endLine: currentLine + i + slice.length - 1, content: slice.join('\n').trim(), is_header: 0, is_signature: 0 });
                    if (i + CHUNK_SIZE >= paraLines.length) break;
                }
            }
            currentLine += lineCount + 1;
        }
        return chunks;
    }
}

module.exports = { CodeChunker };
