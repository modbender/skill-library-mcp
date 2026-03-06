const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { loadConfig, DEFAULT_CONFIG } = require('./config');

let tmpDir;

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-config-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('loadConfig - 默认配置', () => {
    it('无配置文件时返回默认值', () => {
        const config = loadConfig(tmpDir);
        assert.equal(config.logDir, 'memory');
        assert.equal(config.kbDir, 'memory/kb');
        assert.equal(config.logFormat, 'prefix');
    });

    it('包含所有必要的 prefixMap', () => {
        const config = loadConfig(tmpDir);
        assert.ok(config.prefixMap.PROJECT);
        assert.ok(config.prefixMap.ISSUE);
        assert.ok(config.prefixMap.INFRA);
        assert.ok(config.prefixMap.CONFIG);
        assert.ok(config.prefixMap.RESEARCH);
        assert.ok(config.prefixMap.KB);
        assert.ok(config.prefixMap.BOSS);
    });

    it('生成正确的绝对路径', () => {
        const config = loadConfig(tmpDir);
        assert.equal(config._workspaceRoot, tmpDir);
        assert.equal(config._logDirAbs, path.resolve(tmpDir, 'memory'));
        assert.equal(config._kbDirAbs, path.resolve(tmpDir, 'memory/kb'));
        assert.equal(config._outputDirAbs, path.resolve(tmpDir, 'output'));
        assert.equal(config._backupDirAbs, path.resolve(tmpDir, 'backups'));
    });

    it('statePath 和 embCachePath 在 kb 目录下', () => {
        const config = loadConfig(tmpDir);
        assert.ok(config._statePath.includes('sync-state.json'));
        assert.ok(config._embCachePath.includes('embeddings-cache.json'));
    });
});

describe('loadConfig - 自定义配置', () => {
    it('从 workspace 根目录加载 km.config.json', () => {
        const customConfig = { logDir: 'logs', kbDir: 'knowledge' };
        fs.writeFileSync(
            path.join(tmpDir, 'km.config.json'),
            JSON.stringify(customConfig)
        );

        const config = loadConfig(tmpDir);
        assert.equal(config.logDir, 'logs');
        assert.equal(config.kbDir, 'knowledge');
        assert.equal(config.logFormat, 'prefix');
    });

    it('自定义配置与默认配置深度合并', () => {
        const customConfig = {
            ai: {
                embedding: { model: 'custom-model' },
            },
        };
        fs.writeFileSync(
            path.join(tmpDir, 'km.config.json'),
            JSON.stringify(customConfig)
        );

        const config = loadConfig(tmpDir);
        assert.equal(config.ai.embedding.model, 'custom-model');
        assert.equal(config.ai.embedding.provider, 'siliconflow');
        assert.equal(config.ai.llm.model, 'deepseek-v3');
    });

    it('指定配置文件路径优先', () => {
        const otherConfig = { logDir: 'other-logs' };
        const otherPath = path.join(tmpDir, 'other.json');
        fs.writeFileSync(otherPath, JSON.stringify(otherConfig));

        fs.writeFileSync(
            path.join(tmpDir, 'km.config.json'),
            JSON.stringify({ logDir: 'default-logs' })
        );

        const config = loadConfig(tmpDir, otherPath);
        assert.equal(config.logDir, 'other-logs');
    });

    it('自定义 prefixMap 会合并', () => {
        const customConfig = {
            prefixMap: { CUSTOM: 'custom/{name}.md' },
        };
        fs.writeFileSync(
            path.join(tmpDir, 'km.config.json'),
            JSON.stringify(customConfig)
        );

        const config = loadConfig(tmpDir);
        assert.ok(config.prefixMap.CUSTOM);
        assert.ok(config.prefixMap.PROJECT);
    });
});

describe('loadConfig - 环境变量解析', () => {
    it('解析 ${VAR} 格式的环境变量', () => {
        const original = process.env.KM_TEST_KEY;
        process.env.KM_TEST_KEY = 'test-api-key-12345';

        const customConfig = {
            ai: {
                embedding: { apiKey: '${KM_TEST_KEY}' },
            },
        };
        fs.writeFileSync(
            path.join(tmpDir, 'km.config.json'),
            JSON.stringify(customConfig)
        );

        const config = loadConfig(tmpDir);
        assert.equal(config.ai.embedding.apiKey, 'test-api-key-12345');

        if (original === undefined) delete process.env.KM_TEST_KEY;
        else process.env.KM_TEST_KEY = original;
    });

    it('未设置的环境变量替换为空字符串', () => {
        delete process.env.NONEXISTENT_KM_VAR_XYZ;
        const config = loadConfig(tmpDir);
        assert.equal(config.ai.embedding.apiKey, '');
    });
});

describe('loadConfig - 错误处理', () => {
    it('损坏的 JSON 配置文件使用默认值', () => {
        fs.writeFileSync(
            path.join(tmpDir, 'km.config.json'),
            '{ bad json !!!'
        );

        const config = loadConfig(tmpDir);
        assert.equal(config.logDir, 'memory');
    });

    it('空配置文件使用默认值', () => {
        fs.writeFileSync(path.join(tmpDir, 'km.config.json'), '{}');
        const config = loadConfig(tmpDir);
        assert.equal(config.logDir, 'memory');
        assert.equal(config.kbDir, 'memory/kb');
    });
});
