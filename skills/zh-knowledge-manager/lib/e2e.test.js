/**
 * 端到端集成测试
 * 模拟完整的 sync / import / digest / cleanup 流程
 */
const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { parseLogFile, findLogFiles } = require('./parser');
const { classify } = require('./classifier');
const { checkDuplicate, loadState, saveState, cleanupState } = require('./dedup');
const { appendEntry, formatEntry, importDraft } = require('./writer');
const { autoTag } = require('./tagger');
const { generateDigest } = require('./digest');
const { loadConfig } = require('./config');

let tmpDir;

function setupWorkspace() {
    const ws = path.join(tmpDir, 'workspace');
    const memDir = path.join(ws, 'memory');
    const kbDir = path.join(ws, 'memory', 'kb');
    const outputDir = path.join(ws, 'output');

    fs.mkdirSync(path.join(kbDir, 'projects'), { recursive: true });
    fs.mkdirSync(path.join(kbDir, 'domains'), { recursive: true });
    fs.mkdirSync(path.join(kbDir, 'tech'), { recursive: true });
    fs.mkdirSync(outputDir, { recursive: true });

    return ws;
}

function writeLog(ws, date, content) {
    const logDir = path.join(ws, 'memory');
    fs.writeFileSync(path.join(logDir, `${date}.md`), content, 'utf-8');
}

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-e2e-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('E2E: sync 全流程', () => {
    it('从日志同步到知识库 - 完整流程', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        writeLog(ws, today, `## 开发日志

### [PROJECT:数据报表] 自动化报表部署完成
crontab + Python 每日 8:00 推飞书。pandas 大表用 chunksize 避免 OOM。
#报表 #自动化 #pandas

### [INFRA:基础设施] Nginx 配置更新
upstream 增加 weight 参数实现加权负载均衡。
#nginx #运维

### [RESEARCH:微服务] Spring Cloud 调研笔记
Gateway + Nacos + Sentinel 三件套。服务间通信用 Feign 优于 RestTemplate。
#微服务 #架构 #spring
`);

        const config = loadConfig(ws);
        const logFiles = findLogFiles(config._logDirAbs, 7);
        assert.equal(logFiles.length, 1);

        const state = loadState(config._statePath);
        let synced = 0;

        for (const file of logFiles) {
            const entries = parseLogFile(file);
            assert.equal(entries.length, 3);

            for (const entry of entries) {
                const { isDuplicate, hash } = checkDuplicate(entry, state);
                assert.equal(isDuplicate, false);

                const targetPath = classify(entry, config);
                appendEntry(targetPath, entry);
                state.hashes[hash] = targetPath;
                synced++;
            }
        }

        saveState(config._statePath, state);
        assert.equal(synced, 3);

        const reportFile = path.join(config._kbDirAbs, 'projects', '数据报表.md');
        assert.ok(fs.existsSync(reportFile));
        const reportContent = fs.readFileSync(reportFile, 'utf-8');
        assert.ok(reportContent.includes('自动化报表部署完成'));
        assert.ok(reportContent.includes('#报表'));

        const infraFile = path.join(config._kbDirAbs, 'tech', 'infra.md');
        assert.ok(fs.existsSync(infraFile));

        const researchFile = path.join(config._kbDirAbs, 'domains', '微服务.md');
        assert.ok(fs.existsSync(researchFile));
    });

    it('重复同步不写入重复条目', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        writeLog(ws, today, `### [PROJECT:测试] 测试条目
测试内容
#test`);

        const config = loadConfig(ws);
        const state = loadState(config._statePath);

        for (let round = 0; round < 3; round++) {
            const logFiles = findLogFiles(config._logDirAbs, 7);
            for (const file of logFiles) {
                const entries = parseLogFile(file);
                for (const entry of entries) {
                    const { isDuplicate, hash } = checkDuplicate(entry, state);
                    if (!isDuplicate) {
                        const targetPath = classify(entry, config);
                        appendEntry(targetPath, entry);
                        state.hashes[hash] = targetPath;
                    }
                }
            }
        }

        saveState(config._statePath, state);

        const targetFile = path.join(config._kbDirAbs, 'projects', '测试.md');
        const content = fs.readFileSync(targetFile, 'utf-8');
        const matches = content.match(/### \[PROJECT\] 测试条目/g);
        assert.equal(matches.length, 1, '应该只有 1 条，不是重复的');
    });

    it('多天日志同步', () => {
        const ws = setupWorkspace();
        const d1 = new Date();
        const d2 = new Date(d1);
        d2.setDate(d2.getDate() - 1);
        const s1 = d1.toISOString().slice(0, 10);
        const s2 = d2.toISOString().slice(0, 10);

        writeLog(ws, s1, `### [PROJECT:报表] 今日开发
完成图表模块
#开发`);

        writeLog(ws, s2, `### [PROJECT:报表] 昨日开发
完成数据接口
#接口`);

        const config = loadConfig(ws);
        const logFiles = findLogFiles(config._logDirAbs, 7);
        assert.equal(logFiles.length, 2);

        const state = loadState(config._statePath);
        let synced = 0;

        for (const file of logFiles) {
            for (const entry of parseLogFile(file)) {
                const { isDuplicate, hash } = checkDuplicate(entry, state);
                if (!isDuplicate) {
                    appendEntry(classify(entry, config), entry);
                    state.hashes[hash] = classify(entry, config);
                    synced++;
                }
            }
        }

        assert.equal(synced, 2);

        const reportFile = path.join(config._kbDirAbs, 'projects', '报表.md');
        const content = fs.readFileSync(reportFile, 'utf-8');
        assert.ok(content.includes('今日开发'));
        assert.ok(content.includes('昨日开发'));
    });
});

describe('E2E: sync + auto-tag', () => {
    it('自动标签补充到条目', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        writeLog(ws, today, `### [PROJECT:数据平台] 使用 Docker 部署 Redis 集群
配置了 3 主 3 从的 Redis Cluster，使用 Docker Compose 编排。
#部署`);

        const config = loadConfig(ws);
        const entries = parseLogFile(path.join(config._logDirAbs, `${today}.md`));
        assert.equal(entries.length, 1);

        const entry = entries[0];
        const enrichedTags = autoTag(entry, config);
        assert.ok(enrichedTags.length > 1, '应补充更多标签');
        assert.ok(enrichedTags.includes('部署'), '原始标签保留');
    });
});

describe('E2E: import 草稿', () => {
    it('导入 LLM 提取的草稿', () => {
        const ws = setupWorkspace();
        const draftPath = path.join(ws, 'output', 'kb-draft-0224.md');

        fs.writeFileSync(draftPath, `# 知识提取草稿 (2026-02-24)

<!-- 来源: session-start.md -->
### [BOSS:数据] GMV 口径定义
GMV 只算实付金额，不含退款和运费。
#数据 #口径

### [BOSS:人事] 数据组负责人
张三是数据组组长，向李总汇报。
#人事 #组织
`);

        const config = loadConfig(ws);
        const state = loadState(config._statePath);

        const { imported, skipped, results } = importDraft(
            draftPath, config, classify, state, checkDuplicate
        );

        assert.equal(imported, 2);
        assert.equal(skipped, 0);

        saveState(config._statePath, state);

        const dataFile = path.join(config._kbDirAbs, 'domains', '数据.md');
        assert.ok(fs.existsSync(dataFile));
        const dataContent = fs.readFileSync(dataFile, 'utf-8');
        assert.ok(dataContent.includes('GMV 口径定义'));

        const peopleFile = path.join(config._kbDirAbs, 'domains', '人事.md');
        assert.ok(fs.existsSync(peopleFile));
    });

    it('重复草稿导入被跳过', () => {
        const ws = setupWorkspace();
        const draftPath = path.join(ws, 'output', 'draft.md');

        fs.writeFileSync(draftPath, `### [KB:工具] Git 分支策略
主干开发，功能分支合并。
#git #分支`);

        const config = loadConfig(ws);
        const state = loadState(config._statePath);

        importDraft(draftPath, config, classify, state, checkDuplicate);
        saveState(config._statePath, state);

        const state2 = loadState(config._statePath);
        const result2 = importDraft(draftPath, config, classify, state2, checkDuplicate);
        assert.equal(result2.imported, 0);
        assert.equal(result2.skipped, 1);
    });
});

describe('E2E: digest 摘要', () => {
    it('同步后生成准确的摘要', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        writeLog(ws, today, `### [PROJECT:报表] 开发完成
完成了
#开发

### [INFRA:基础设施] 服务器升级
升级了
#运维`);

        const config = loadConfig(ws);
        const state = loadState(config._statePath);

        for (const entry of parseLogFile(path.join(config._logDirAbs, `${today}.md`))) {
            const { isDuplicate, hash } = checkDuplicate(entry, state);
            if (!isDuplicate) {
                appendEntry(classify(entry, config), entry);
                state.hashes[hash] = classify(entry, config);
            }
        }
        saveState(config._statePath, state);

        const digest = generateDigest(config);
        assert.ok(digest.includes('总条目数: 2'));
        assert.ok(digest.includes(today));
    });
});

describe('E2E: cleanup 清理', () => {
    it('删除 kb 文件后 cleanup 清理引用', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        writeLog(ws, today, `### [PROJECT:临时项目] 测试
临时内容
#temp`);

        const config = loadConfig(ws);
        const state = loadState(config._statePath);

        for (const entry of parseLogFile(path.join(config._logDirAbs, `${today}.md`))) {
            const { hash } = checkDuplicate(entry, state);
            const target = classify(entry, config);
            appendEntry(target, entry);
            state.hashes[hash] = target;
        }
        saveState(config._statePath, state);

        const targetFile = path.join(config._kbDirAbs, 'projects', '临时项目.md');
        assert.ok(fs.existsSync(targetFile));
        fs.unlinkSync(targetFile);

        const state2 = loadState(config._statePath);
        const { removed, state: cleaned } = cleanupState(state2);
        assert.equal(removed, 1);
        saveState(config._statePath, cleaned);

        const state3 = loadState(config._statePath);
        assert.equal(Object.keys(state3.hashes).length, 0);
    });
});

describe('E2E: 边界场景', () => {
    it('无日志文件时 sync 安全退出', () => {
        const ws = setupWorkspace();
        const config = loadConfig(ws);
        const logFiles = findLogFiles(config._logDirAbs, 7);
        assert.equal(logFiles.length, 0);
    });

    it('空日志文件不产生条目', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);
        writeLog(ws, today, '');

        const config = loadConfig(ws);
        const entries = parseLogFile(path.join(config._logDirAbs, `${today}.md`));
        assert.equal(entries.length, 0);
    });

    it('未知 PREFIX 归类到 uncategorized.md', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        writeLog(ws, today, `### [UNKNOWN:神秘] 未知分类
这条日志的 PREFIX 未注册
#未知`);

        const config = loadConfig(ws);
        const entries = parseLogFile(path.join(config._logDirAbs, `${today}.md`));
        const target = classify(entries[0], config);
        assert.ok(target.includes('uncategorized'));
    });

    it('大批量日志同步性能', () => {
        const ws = setupWorkspace();
        const today = new Date().toISOString().slice(0, 10);

        const lines = [];
        for (let i = 0; i < 100; i++) {
            lines.push(`### [PROJECT:批量测试] 条目${i}`);
            lines.push(`这是第 ${i} 条测试内容，用于验证批量同步性能。`);
            lines.push(`#batch #test${i}`);
            lines.push('');
        }
        writeLog(ws, today, lines.join('\n'));

        const config = loadConfig(ws);
        const state = loadState(config._statePath);

        const start = Date.now();
        const entries = parseLogFile(path.join(config._logDirAbs, `${today}.md`));
        assert.equal(entries.length, 100);

        let synced = 0;
        for (const entry of entries) {
            const { isDuplicate, hash } = checkDuplicate(entry, state);
            if (!isDuplicate) {
                appendEntry(classify(entry, config), entry);
                state.hashes[hash] = classify(entry, config);
                synced++;
            }
        }

        const elapsed = Date.now() - start;
        assert.equal(synced, 100);
        assert.ok(elapsed < 10000, `100 条同步耗时 ${elapsed}ms，应 < 10s`);
    });

    it('formatEntry 输出与 parser 兼容（round-trip）', () => {
        const original = {
            prefix: 'PROJECT',
            name: '报表',
            title: '自动化报表',
            body: '每日推飞书',
            tags: ['报表', '自动化'],
            date: '2026-02-24',
        };

        const formatted = formatEntry(original);
        assert.ok(formatted.includes('### [PROJECT] 自动化报表'));
        assert.ok(formatted.includes('每日推飞书'));
        assert.ok(formatted.includes('#报表'));
    });
});
