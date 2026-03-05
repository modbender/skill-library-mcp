const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { classify, sanitizeName, getKnownPrefixes } = require('./classifier');

const KB_DIR = path.resolve('/test/kb');
const CONFIG = {
    _kbDirAbs: KB_DIR,
    prefixMap: {
        PROJECT: 'projects/{name}.md',
        ISSUE: 'projects/{name}.md',
        INFRA: 'tech/infra.md',
        CONFIG: 'tech/config.md',
        RESEARCH: 'domains/{name}.md',
        KB: 'domains/{name}.md',
        BOSS: 'domains/{name}.md',
    },
};

describe('sanitizeName', () => {
    it('中文名保持不变', () => {
        assert.equal(sanitizeName('数据报表'), '数据报表');
    });

    it('空格转为连字符', () => {
        assert.equal(sanitizeName('数据 报表'), '数据-报表');
    });

    it('英文转小写', () => {
        assert.equal(sanitizeName('DataPipeline'), 'datapipeline');
    });

    it('移除特殊字符', () => {
        assert.equal(sanitizeName('报表(v2)'), '报表v2');
    });

    it('保留连字符', () => {
        assert.equal(sanitizeName('data-pipeline'), 'data-pipeline');
    });

    it('多个空格合并', () => {
        assert.equal(sanitizeName('a   b   c'), 'a-b-c');
    });

    it('中英文混合', () => {
        assert.equal(sanitizeName('AI助手v2'), 'ai助手v2');
    });

    it('空字符串', () => {
        assert.equal(sanitizeName(''), '');
    });
});

describe('classify - PREFIX 映射', () => {
    it('PROJECT → projects/{name}.md', () => {
        const result = classify({ prefix: 'PROJECT', name: '数据报表' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'projects', '数据报表.md'));
    });

    it('ISSUE → projects/{name}.md', () => {
        const result = classify({ prefix: 'ISSUE', name: '数据报表' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'projects', '数据报表.md'));
    });

    it('INFRA → tech/infra.md（固定路径，忽略 name）', () => {
        const result = classify({ prefix: 'INFRA', name: '随便什么' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'tech', 'infra.md'));
    });

    it('CONFIG → tech/config.md', () => {
        const result = classify({ prefix: 'CONFIG', name: '随便' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'tech', 'config.md'));
    });

    it('RESEARCH → domains/{name}.md', () => {
        const result = classify({ prefix: 'RESEARCH', name: '微服务' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'domains', '微服务.md'));
    });

    it('KB → domains/{name}.md', () => {
        const result = classify({ prefix: 'KB', name: '工具链' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'domains', '工具链.md'));
    });

    it('BOSS → domains/{name}.md', () => {
        const result = classify({ prefix: 'BOSS', name: '数据' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'domains', '数据.md'));
    });

    it('未知 PREFIX → uncategorized.md', () => {
        const result = classify({ prefix: 'UNKNOWN', name: '什么' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'uncategorized.md'));
    });

    it('name 含空格时转连字符', () => {
        const result = classify({ prefix: 'PROJECT', name: '数据 报表' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'projects', '数据-报表.md'));
    });

    it('name 含特殊字符时过滤', () => {
        const result = classify({ prefix: 'PROJECT', name: '报表(v2.0)' }, CONFIG);
        assert.equal(result, path.join(KB_DIR, 'projects', '报表v20.md'));
    });
});

describe('getKnownPrefixes', () => {
    it('返回所有已配置的 PREFIX', () => {
        const prefixes = getKnownPrefixes(CONFIG);
        assert.ok(prefixes.includes('PROJECT'));
        assert.ok(prefixes.includes('ISSUE'));
        assert.ok(prefixes.includes('INFRA'));
        assert.ok(prefixes.includes('CONFIG'));
        assert.ok(prefixes.includes('RESEARCH'));
        assert.ok(prefixes.includes('KB'));
        assert.ok(prefixes.includes('BOSS'));
        assert.equal(prefixes.length, 7);
    });
});
