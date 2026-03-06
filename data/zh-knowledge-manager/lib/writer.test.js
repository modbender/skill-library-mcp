const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { formatEntry, appendEntry, importDraft } = require('./writer');
const { computeHash } = require('./dedup');

let tmpDir;

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-writer-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('formatEntry', () => {
    it('格式化完整条目', () => {
        const entry = {
            prefix: 'PROJECT',
            title: '自动化报表',
            body: 'crontab 每日执行',
            tags: ['报表', '自动化'],
            date: '2026-02-24',
        };
        const result = formatEntry(entry);
        assert.ok(result.includes('### [PROJECT] 自动化报表'));
        assert.ok(result.includes('crontab 每日执行'));
        assert.ok(result.includes('来源: 2026-02-24 日志'));
        assert.ok(result.includes('#报表 #自动化'));
    });

    it('无标签时只显示来源', () => {
        const entry = {
            prefix: 'INFRA',
            title: '服务器升级',
            body: '升级到 Ubuntu 24',
            tags: [],
            date: '2026-02-24',
        };
        const result = formatEntry(entry);
        assert.ok(result.includes('来源: 2026-02-24 日志'));
        assert.ok(!result.includes('|'));
    });

    it('无正文时正确格式化', () => {
        const entry = {
            prefix: 'KB',
            title: '简短记录',
            body: '',
            tags: ['记录'],
            date: '2026-02-24',
        };
        const result = formatEntry(entry);
        const lines = result.split('\n');
        assert.equal(lines[0], '### [KB] 简短记录');
        assert.ok(lines[1].includes('来源'));
    });

    it('多行正文保持格式', () => {
        const entry = {
            prefix: 'RESEARCH',
            title: '调研',
            body: '第一行\n第二行\n第三行',
            tags: [],
            date: '2026-02-24',
        };
        const result = formatEntry(entry);
        assert.ok(result.includes('第一行\n第二行\n第三行'));
    });
});

describe('appendEntry', () => {
    it('创建新文件并写入（自动创建目录）', () => {
        const targetPath = path.join(tmpDir, 'sub', 'dir', 'test.md');
        const entry = {
            prefix: 'PROJECT',
            title: '测试',
            body: '内容',
            tags: ['test'],
            date: '2026-02-24',
        };

        appendEntry(targetPath, entry);

        assert.ok(fs.existsSync(targetPath));
        const content = fs.readFileSync(targetPath, 'utf-8');
        assert.ok(content.includes('# test'));
        assert.ok(content.includes('### [PROJECT] 测试'));
    });

    it('追加到已有文件', () => {
        const targetPath = path.join(tmpDir, 'existing.md');
        fs.writeFileSync(targetPath, '# existing\n\n### [KB] 旧条目\n内容\n');

        const entry = {
            prefix: 'KB',
            title: '新条目',
            body: '新内容',
            tags: ['new'],
            date: '2026-02-24',
        };

        appendEntry(targetPath, entry);

        const content = fs.readFileSync(targetPath, 'utf-8');
        assert.ok(content.includes('旧条目'));
        assert.ok(content.includes('新条目'));
        assert.ok(content.includes('新内容'));
    });

    it('dry-run 模式不写入文件', () => {
        const targetPath = path.join(tmpDir, 'dry-run.md');
        const entry = {
            prefix: 'PROJECT',
            title: '测试',
            body: '内容',
            tags: [],
            date: '2026-02-24',
        };

        const result = appendEntry(targetPath, entry, true);

        assert.ok(!fs.existsSync(targetPath));
        assert.ok(result.content.includes('### [PROJECT] 测试'));
        assert.equal(result.targetPath, targetPath);
    });

    it('返回值包含 targetPath 和 content', () => {
        const targetPath = path.join(tmpDir, 'ret.md');
        const entry = {
            prefix: 'KB',
            title: '返回值测试',
            body: '正文',
            tags: ['tag'],
            date: '2026-02-24',
        };

        const result = appendEntry(targetPath, entry);
        assert.equal(result.targetPath, targetPath);
        assert.ok(result.content.includes('返回值测试'));
    });

    it('多次追加不会覆盖', () => {
        const targetPath = path.join(tmpDir, 'multi.md');
        for (let i = 1; i <= 3; i++) {
            appendEntry(targetPath, {
                prefix: 'KB',
                title: `条目${i}`,
                body: `内容${i}`,
                tags: [],
                date: '2026-02-24',
            });
        }

        const content = fs.readFileSync(targetPath, 'utf-8');
        assert.ok(content.includes('条目1'));
        assert.ok(content.includes('条目2'));
        assert.ok(content.includes('条目3'));
    });

    it('中文文件名和路径正常工作', () => {
        const targetPath = path.join(tmpDir, '项目', '数据报表.md');
        appendEntry(targetPath, {
            prefix: 'PROJECT',
            title: '中文路径测试',
            body: '正文',
            tags: [],
            date: '2026-02-24',
        });

        assert.ok(fs.existsSync(targetPath));
        const content = fs.readFileSync(targetPath, 'utf-8');
        assert.ok(content.includes('中文路径测试'));
    });
});

describe('importDraft', () => {
    it('导入草稿文件中的条目', () => {
        const draftPath = path.join(tmpDir, 'draft.md');
        fs.writeFileSync(draftPath, `### [BOSS:数据] 业务规则
GMV 口径不含退款。
#数据 #口径

### [BOSS:人事] 团队结构
张三负责数据组。
#人事`);

        const kbDir = path.join(tmpDir, 'kb');
        const config = {
            _kbDirAbs: kbDir,
            prefixMap: { BOSS: 'domains/{name}.md' },
        };

        const state = { hashes: {} };
        const classifyFn = (entry, cfg) => {
            const name = entry.name.toLowerCase().replace(/\s+/g, '-');
            return path.join(cfg._kbDirAbs, 'domains', `${name}.md`);
        };
        const dedupFn = (entry, st) => {
            const hash = computeHash(entry);
            return { isDuplicate: hash in st.hashes, hash };
        };

        const result = importDraft(draftPath, config, classifyFn, state, dedupFn);
        assert.equal(result.imported, 2);
        assert.equal(result.skipped, 0);
        assert.equal(result.results.length, 2);
    });

    it('重复条目被跳过', () => {
        const draftPath = path.join(tmpDir, 'draft.md');
        fs.writeFileSync(draftPath, `### [KB:工具] 测试条目
内容
#test`);

        const entry = { title: '测试条目', date: new Date().toISOString().slice(0, 10), body: '内容' };
        const hash = computeHash(entry);
        const state = { hashes: { [hash]: '/old/path.md' } };

        const config = { _kbDirAbs: path.join(tmpDir, 'kb'), prefixMap: { KB: 'domains/{name}.md' } };
        const classifyFn = () => path.join(tmpDir, 'kb', 'test.md');
        const dedupFn = (e, st) => {
            const h = computeHash(e);
            return { isDuplicate: h in st.hashes, hash: h };
        };

        const result = importDraft(draftPath, config, classifyFn, state, dedupFn);
        assert.equal(result.imported, 0);
        assert.equal(result.skipped, 1);
    });
});
