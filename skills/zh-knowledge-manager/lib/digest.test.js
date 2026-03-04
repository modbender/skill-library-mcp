const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { generateDigest, scanKbDir, analyzeFile } = require('./digest');

let tmpDir;

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-digest-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

function setupKb() {
    const kbDir = path.join(tmpDir, 'kb');
    const logDir = path.join(tmpDir, 'memory');
    fs.mkdirSync(path.join(kbDir, 'projects'), { recursive: true });
    fs.mkdirSync(path.join(kbDir, 'domains'), { recursive: true });
    fs.mkdirSync(path.join(kbDir, 'tech'), { recursive: true });
    fs.mkdirSync(logDir, { recursive: true });
    return { kbDir, logDir };
}

describe('analyzeFile', () => {
    it('统计 ### [ 开头的条目数', () => {
        const filePath = path.join(tmpDir, 'test.md');
        fs.writeFileSync(filePath, `# Test

### [PROJECT] 条目1
来源: 2026-02-20 日志

### [PROJECT] 条目2
来源: 2026-02-24 日志

### [PROJECT] 条目3
来源: 2026-02-22 日志
`);
        const result = analyzeFile(filePath);
        assert.equal(result.count, 3);
        assert.equal(result.oldest, '2026-02-20');
        assert.equal(result.newest, '2026-02-24');
    });

    it('空文件返回 0', () => {
        const filePath = path.join(tmpDir, 'empty.md');
        fs.writeFileSync(filePath, '');
        const result = analyzeFile(filePath);
        assert.equal(result.count, 0);
        assert.equal(result.newest, null);
    });

    it('无日期信息时 newest/oldest 为 null', () => {
        const filePath = path.join(tmpDir, 'nodate.md');
        fs.writeFileSync(filePath, `### [KB] 无日期条目\n内容\n`);
        const result = analyzeFile(filePath);
        assert.equal(result.count, 1);
        assert.equal(result.newest, null);
    });

    it('文件不存在时返回 count=0', () => {
        const result = analyzeFile(path.join(tmpDir, 'nonexistent.md'));
        assert.equal(result.count, 0);
    });
});

describe('scanKbDir', () => {
    it('递归扫描 md 文件', () => {
        const { kbDir } = setupKb();
        fs.writeFileSync(path.join(kbDir, 'projects', 'a.md'), '### [PROJECT] A\n来源: 2026-02-24 日志\n');
        fs.writeFileSync(path.join(kbDir, 'domains', 'b.md'), '### [RESEARCH] B\n来源: 2026-02-23 日志\n');
        fs.writeFileSync(path.join(kbDir, 'people.md'), '### [KB] 张三\n来源: 2026-02-22 日志\n');

        const results = scanKbDir(kbDir);
        assert.equal(results.length, 3);
    });

    it('忽略非 md 文件', () => {
        const { kbDir } = setupKb();
        fs.writeFileSync(path.join(kbDir, 'sync-state.json'), '{}');
        fs.writeFileSync(path.join(kbDir, 'projects', 'test.md'), '');

        const results = scanKbDir(kbDir);
        assert.ok(results.every(r => r.relativePath.endsWith('.md')));
    });

    it('目录不存在时返回空数组', () => {
        const results = scanKbDir(path.join(tmpDir, 'nonexistent'));
        assert.deepEqual(results, []);
    });
});

describe('generateDigest', () => {
    it('生成完整的摘要文本', () => {
        const { kbDir, logDir } = setupKb();
        fs.writeFileSync(
            path.join(kbDir, 'projects', 'report.md'),
            `### [PROJECT] 报表
来源: 2026-02-24 日志

### [PROJECT] 数据导出
来源: 2026-02-23 日志
`);
        fs.writeFileSync(
            path.join(kbDir, 'tech', 'infra.md'),
            `### [INFRA] 服务器
来源: 2026-02-24 日志
`);

        const config = {
            _kbDirAbs: kbDir,
            _logDirAbs: logDir,
        };

        const text = generateDigest(config);
        assert.ok(text.includes('知识库摘要'));
        assert.ok(text.includes('总条目数: 3'));
        assert.ok(text.includes('2026-02-24'));
    });

    it('空知识库显示 0 条目', () => {
        const { kbDir, logDir } = setupKb();
        const config = { _kbDirAbs: kbDir, _logDirAbs: logDir };
        const text = generateDigest(config);
        assert.ok(text.includes('总条目数: 0'));
    });

    it('检测知识空白', () => {
        const { kbDir, logDir } = setupKb();

        const today = new Date().toISOString().slice(0, 10);
        fs.writeFileSync(
            path.join(logDir, `${today}.md`),
            `### [PROJECT:商品货盘] 货盘分析
内容
#分析`
        );

        const config = { _kbDirAbs: kbDir, _logDirAbs: logDir };
        const text = generateDigest(config);
        assert.ok(text.includes('商品货盘'));
        assert.ok(text.includes('知识空白'));
    });

    it('updateIndex 选项生成 kb-index.md', () => {
        const { kbDir, logDir } = setupKb();
        fs.writeFileSync(
            path.join(kbDir, 'people.md'),
            '### [KB] 张三\n来源: 2026-02-24 日志\n'
        );

        const config = { _kbDirAbs: kbDir, _logDirAbs: logDir };
        generateDigest(config, { updateIndex: true });

        const indexPath = path.join(kbDir, '..', 'kb-index.md');
        assert.ok(fs.existsSync(indexPath));
        const content = fs.readFileSync(indexPath, 'utf-8');
        assert.ok(content.includes('知识注册表'));
        assert.ok(content.includes('people.md'));
    });

    it('已有对应 kb 文件的主题不报告为空白', () => {
        const { kbDir, logDir } = setupKb();

        const today = new Date().toISOString().slice(0, 10);
        fs.writeFileSync(
            path.join(logDir, `${today}.md`),
            '### [PROJECT:报表] 报表开发\n内容'
        );
        fs.writeFileSync(
            path.join(kbDir, 'projects', '报表.md'),
            '### [PROJECT] 报表\n来源: 2026-02-24 日志\n'
        );

        const config = { _kbDirAbs: kbDir, _logDirAbs: logDir };
        const text = generateDigest(config);
        assert.ok(!text.includes('知识空白') || !text.includes('报表'));
    });
});
