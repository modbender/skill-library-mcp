const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { cosineSimilarity, loadEmbeddingsCache, saveEmbeddingsCache } = require('./semantic-dedup');

let tmpDir;

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-semdedup-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('cosineSimilarity', () => {
    it('相同向量相似度为 1', () => {
        const v = [1, 2, 3, 4, 5];
        assert.ok(Math.abs(cosineSimilarity(v, v) - 1.0) < 1e-10);
    });

    it('正交向量相似度为 0', () => {
        const a = [1, 0, 0];
        const b = [0, 1, 0];
        assert.ok(Math.abs(cosineSimilarity(a, b)) < 1e-10);
    });

    it('反向向量相似度为 -1', () => {
        const a = [1, 0, 0];
        const b = [-1, 0, 0];
        assert.ok(Math.abs(cosineSimilarity(a, b) + 1.0) < 1e-10);
    });

    it('相似向量的相似度接近 1', () => {
        const a = [1, 2, 3, 4, 5];
        const b = [1.1, 2.05, 2.9, 4.1, 5.02];
        const sim = cosineSimilarity(a, b);
        assert.ok(sim > 0.99);
    });

    it('不同向量相似度 < 1', () => {
        const a = [1, 0, 0, 0];
        const b = [0, 0, 0, 1];
        assert.ok(cosineSimilarity(a, b) < 0.5);
    });

    it('高维向量计算正确', () => {
        const dim = 1024;
        const a = Array.from({ length: dim }, (_, i) => Math.sin(i));
        const b = Array.from({ length: dim }, (_, i) => Math.sin(i + 0.01));
        const sim = cosineSimilarity(a, b);
        assert.ok(sim > 0.99);
    });

    it('零向量处理（返回 NaN）', () => {
        const a = [0, 0, 0];
        const b = [1, 2, 3];
        const sim = cosineSimilarity(a, b);
        assert.ok(isNaN(sim));
    });
});

describe('embeddings cache', () => {
    it('加载不存在的缓存返回空对象', () => {
        const cache = loadEmbeddingsCache(path.join(tmpDir, 'nonexistent.json'));
        assert.deepEqual(cache, {});
    });

    it('保存并重新加载缓存', () => {
        const cachePath = path.join(tmpDir, 'cache.json');
        const cache = { hash1: [0.1, 0.2, 0.3], hash2: [0.4, 0.5, 0.6] };

        saveEmbeddingsCache(cachePath, cache);
        const loaded = loadEmbeddingsCache(cachePath);

        assert.deepEqual(loaded.hash1, [0.1, 0.2, 0.3]);
        assert.deepEqual(loaded.hash2, [0.4, 0.5, 0.6]);
    });

    it('损坏的缓存文件返回空对象', () => {
        const cachePath = path.join(tmpDir, 'bad.json');
        fs.writeFileSync(cachePath, 'not json!');
        const cache = loadEmbeddingsCache(cachePath);
        assert.deepEqual(cache, {});
    });

    it('空缓存保存和加载', () => {
        const cachePath = path.join(tmpDir, 'empty.json');
        saveEmbeddingsCache(cachePath, {});
        const loaded = loadEmbeddingsCache(cachePath);
        assert.deepEqual(loaded, {});
    });
});
