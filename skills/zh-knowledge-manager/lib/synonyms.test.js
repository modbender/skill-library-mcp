const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { normalize, normalizeTags, loadSynonyms, DEFAULT_SYNONYMS } = require('./synonyms');

describe('normalize', () => {
    it('变体归一到规范形式 - DB → 数据库', () => {
        assert.equal(normalize('DB'), '数据库');
        assert.equal(normalize('db'), '数据库');
        assert.equal(normalize('database'), '数据库');
        assert.equal(normalize('mysql'), '数据库');
    });

    it('LLM 相关变体归一', () => {
        assert.equal(normalize('LLM'), '大模型');
        assert.equal(normalize('llm'), '大模型');
        assert.equal(normalize('大语言模型'), '大模型');
    });

    it('飞书变体归一', () => {
        assert.equal(normalize('feishu'), '飞书');
        assert.equal(normalize('lark'), '飞书');
        assert.equal(normalize('Lark'), '飞书');
    });

    it('容器相关变体归一', () => {
        assert.equal(normalize('docker'), '容器');
        assert.equal(normalize('Docker'), '容器');
        assert.equal(normalize('k8s'), '容器');
        assert.equal(normalize('kubernetes'), '容器');
    });

    it('规范形式本身返回规范形式', () => {
        assert.equal(normalize('数据库'), '数据库');
        assert.equal(normalize('飞书'), '飞书');
    });

    it('未知术语原样返回', () => {
        assert.equal(normalize('完全未知的词'), '完全未知的词');
        assert.equal(normalize('randomword'), 'randomword');
    });

    it('大小写不敏感', () => {
        assert.equal(normalize('DOCKER'), '容器');
        assert.equal(normalize('Redis'), '缓存');
        assert.equal(normalize('REDIS'), '缓存');
    });

    it('自定义同义词表覆盖默认', () => {
        const custom = { '自定义': ['customTag', 'myTag'] };
        assert.equal(normalize('customTag', custom), '自定义');
        assert.equal(normalize('myTag', custom), '自定义');
    });
});

describe('normalizeTags', () => {
    it('去重 + 归一化', () => {
        const tags = ['Docker', 'docker', 'k8s'];
        const result = normalizeTags(tags);
        assert.equal(result.length, 1);
        assert.equal(result[0], '容器');
    });

    it('混合已知和未知标签', () => {
        const tags = ['Docker', '自定义标签', 'mysql'];
        const result = normalizeTags(tags);
        assert.ok(result.includes('容器'));
        assert.ok(result.includes('自定义标签'));
        assert.ok(result.includes('数据库'));
    });

    it('空数组', () => {
        assert.deepEqual(normalizeTags([]), []);
    });

    it('保持顺序（第一个出现的优先）', () => {
        const tags = ['报表', '数据报表', '自动化'];
        const result = normalizeTags(tags);
        assert.equal(result[0], '报表');
    });

    it('多个同义词全部归一到同一个', () => {
        const tags = ['mysql', 'PostgreSQL', 'sqlite', 'DB'];
        const result = normalizeTags(tags);
        assert.equal(result.length, 1);
        assert.equal(result[0], '数据库');
    });
});

describe('loadSynonyms', () => {
    it('"default" 返回默认表', () => {
        const s = loadSynonyms('default');
        assert.deepEqual(s, DEFAULT_SYNONYMS);
    });

    it('null / undefined 返回默认表', () => {
        assert.deepEqual(loadSynonyms(null), DEFAULT_SYNONYMS);
        assert.deepEqual(loadSynonyms(undefined), DEFAULT_SYNONYMS);
    });

    it('不存在的文件路径返回默认表', () => {
        assert.deepEqual(loadSynonyms('/nonexistent/path.json'), DEFAULT_SYNONYMS);
    });
});

describe('DEFAULT_SYNONYMS 完整性检查', () => {
    it('覆盖常用中文技术术语', () => {
        const keys = Object.keys(DEFAULT_SYNONYMS);
        const expected = ['数据库', '大模型', '飞书', '报表', '自动化', '部署', '监控', '缓存', 'API'];
        for (const k of expected) {
            assert.ok(keys.includes(k), `缺少 "${k}" 同义词组`);
        }
    });

    it('每个规范形式至少有 2 个变体', () => {
        for (const [key, variants] of Object.entries(DEFAULT_SYNONYMS)) {
            assert.ok(variants.length >= 2, `"${key}" 变体数量不足 (${variants.length})`);
        }
    });
});
