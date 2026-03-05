const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { computeHash, loadState, saveState, checkDuplicate, cleanupState } = require('./dedup');

let tmpDir;

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-dedup-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('computeHash', () => {
    it('相同内容产生相同 hash', () => {
        const entry = { title: '测试', date: '2026-02-24', body: '正文内容' };
        const h1 = computeHash(entry);
        const h2 = computeHash(entry);
        assert.equal(h1, h2);
    });

    it('不同标题产生不同 hash', () => {
        const e1 = { title: '标题A', date: '2026-02-24', body: '正文' };
        const e2 = { title: '标题B', date: '2026-02-24', body: '正文' };
        assert.notEqual(computeHash(e1), computeHash(e2));
    });

    it('不同日期产生不同 hash', () => {
        const e1 = { title: '标题', date: '2026-02-24', body: '正文' };
        const e2 = { title: '标题', date: '2026-02-25', body: '正文' };
        assert.notEqual(computeHash(e1), computeHash(e2));
    });

    it('不同正文产生不同 hash', () => {
        const e1 = { title: '标题', date: '2026-02-24', body: '正文A' };
        const e2 = { title: '标题', date: '2026-02-24', body: '正文B' };
        assert.notEqual(computeHash(e1), computeHash(e2));
    });

    it('hash 长度为 16', () => {
        const entry = { title: '测试', date: '2026-02-24', body: '正文' };
        assert.equal(computeHash(entry).length, 16);
    });

    it('body 只取前 200 字符', () => {
        const shortBody = '短'.repeat(100);
        const longBody = shortBody + '长'.repeat(500);
        const e1 = { title: '标题', date: '2026-02-24', body: shortBody + '长'.repeat(100) };
        const e2 = { title: '标题', date: '2026-02-24', body: shortBody + '长'.repeat(100) + '额外' };
        assert.equal(computeHash(e1), computeHash(e2));
    });

    it('body 为空时不报错', () => {
        const entry = { title: '标题', date: '2026-02-24', body: '' };
        assert.ok(computeHash(entry));
    });

    it('body 为 undefined 时不报错', () => {
        const entry = { title: '标题', date: '2026-02-24' };
        assert.ok(computeHash(entry));
    });

    it('中文标题正确 hash', () => {
        const entry = { title: '中文测试标题', date: '2026-02-24', body: '中文正文内容' };
        const hash = computeHash(entry);
        assert.match(hash, /^[a-f0-9]{16}$/);
    });
});

describe('loadState / saveState', () => {
    it('加载不存在的文件返回空状态', () => {
        const state = loadState(path.join(tmpDir, 'nonexistent.json'));
        assert.deepEqual(state.hashes, {});
        assert.equal(state.lastSync, null);
    });

    it('保存并重新加载状态', () => {
        const statePath = path.join(tmpDir, 'state.json');
        const state = { hashes: { abc123: '/some/path.md' }, lastSync: null };
        saveState(statePath, state);

        const loaded = loadState(statePath);
        assert.equal(loaded.hashes['abc123'], '/some/path.md');
        assert.ok(loaded.lastSync);
    });

    it('保存时自动设置 lastSync 时间戳', () => {
        const statePath = path.join(tmpDir, 'state.json');
        const state = { hashes: {}, lastSync: null };
        saveState(statePath, state);

        const loaded = loadState(statePath);
        assert.match(loaded.lastSync, /^\d{4}-\d{2}-\d{2}T/);
    });

    it('损坏的 JSON 文件返回空状态', () => {
        const statePath = path.join(tmpDir, 'bad.json');
        fs.writeFileSync(statePath, '{ invalid json !!!');
        const state = loadState(statePath);
        assert.deepEqual(state.hashes, {});
    });

    it('多次保存覆盖更新', () => {
        const statePath = path.join(tmpDir, 'state.json');
        saveState(statePath, { hashes: { a: '1' }, lastSync: null });
        saveState(statePath, { hashes: { a: '1', b: '2' }, lastSync: null });

        const loaded = loadState(statePath);
        assert.equal(Object.keys(loaded.hashes).length, 2);
    });
});

describe('checkDuplicate', () => {
    it('新条目不是重复', () => {
        const state = { hashes: {} };
        const entry = { title: '新条目', date: '2026-02-24', body: '内容' };
        const { isDuplicate, hash } = checkDuplicate(entry, state);
        assert.equal(isDuplicate, false);
        assert.ok(hash);
    });

    it('已存在的条目被标记为重复', () => {
        const entry = { title: '已存在', date: '2026-02-24', body: '内容' };
        const hash = computeHash(entry);
        const state = { hashes: { [hash]: '/some/path.md' } };

        const result = checkDuplicate(entry, state);
        assert.equal(result.isDuplicate, true);
        assert.equal(result.hash, hash);
    });

    it('标签不同但标题/日期/正文相同算重复', () => {
        const entry = { title: '标题', date: '2026-02-24', body: '正文', tags: ['a'] };
        const hash = computeHash(entry);
        const state = { hashes: { [hash]: '/path.md' } };

        const entry2 = { ...entry, tags: ['b', 'c'] };
        assert.equal(checkDuplicate(entry2, state).isDuplicate, true);
    });
});

describe('cleanupState', () => {
    it('移除引用不存在文件的条目', () => {
        const state = {
            hashes: {
                hash1: path.join(tmpDir, 'exists.md'),
                hash2: path.join(tmpDir, 'gone.md'),
            },
        };
        fs.writeFileSync(path.join(tmpDir, 'exists.md'), 'content');

        const { removed, state: cleaned } = cleanupState(state);
        assert.equal(removed, 1);
        assert.ok('hash1' in cleaned.hashes);
        assert.ok(!('hash2' in cleaned.hashes));
    });

    it('全部文件都存在时不移除', () => {
        const file1 = path.join(tmpDir, 'a.md');
        const file2 = path.join(tmpDir, 'b.md');
        fs.writeFileSync(file1, '');
        fs.writeFileSync(file2, '');

        const state = { hashes: { h1: file1, h2: file2 } };
        const { removed } = cleanupState(state);
        assert.equal(removed, 0);
    });

    it('空状态不报错', () => {
        const { removed, state: cleaned } = cleanupState({ hashes: {} });
        assert.equal(removed, 0);
        assert.deepEqual(cleaned.hashes, {});
    });

    it('所有文件都不存在时全部清除', () => {
        const state = {
            hashes: {
                h1: '/nonexistent/a.md',
                h2: '/nonexistent/b.md',
                h3: '/nonexistent/c.md',
            },
        };
        const { removed } = cleanupState(state);
        assert.equal(removed, 3);
    });
});
