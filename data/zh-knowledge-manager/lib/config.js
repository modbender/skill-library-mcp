/**
 * 配置加载与默认值管理
 * 支持 km.config.json 自定义，未配置项使用默认值
 */
const fs = require('fs');
const path = require('path');

const DEFAULT_CONFIG = {
    logDir: 'memory',
    kbDir: 'memory/kb',
    outputDir: 'output',
    backupDir: 'backups',
    logFormat: 'prefix',

    prefixMap: {
        PROJECT: 'projects/{name}.md',
        ISSUE: 'projects/{name}.md',
        INFRA: 'tech/infra.md',
        CONFIG: 'tech/config.md',
        RESEARCH: 'domains/{name}.md',
        KB: 'domains/{name}.md',
        BOSS: 'domains/{name}.md',
    },

    ai: {
        embedding: {
            provider: 'siliconflow',
            model: 'BAAI/bge-m3',
            apiKey: '${SILICONFLOW_API_KEY}',
            endpoint: 'https://api.siliconflow.cn/v1/embeddings',
            threshold: { suspect: 0.85, skip: 0.95 },
        },
        llm: {
            provider: 'volcengine',
            model: 'deepseek-v3',
            apiKey: '${ARK_API_KEY}',
            endpoint: '',
            extractPrompt: 'default',
        },
    },

    synonyms: 'default',
    autoTag: { topN: 5 },
    stateFile: 'sync-state.json',
    embeddingsCacheFile: 'embeddings-cache.json',
};

function resolveEnvVar(value) {
    if (typeof value !== 'string') return value;
    return value.replace(/\$\{(\w+)\}/g, (_, name) => process.env[name] || '');
}

function resolveEnvVarsDeep(obj) {
    if (typeof obj === 'string') return resolveEnvVar(obj);
    if (Array.isArray(obj)) return obj.map(resolveEnvVarsDeep);
    if (obj && typeof obj === 'object') {
        const result = {};
        for (const [k, v] of Object.entries(obj)) {
            result[k] = resolveEnvVarsDeep(v);
        }
        return result;
    }
    return obj;
}

function deepMerge(target, source) {
    const result = { ...target };
    for (const [key, value] of Object.entries(source)) {
        if (value && typeof value === 'object' && !Array.isArray(value)
            && target[key] && typeof target[key] === 'object') {
            result[key] = deepMerge(target[key], value);
        } else {
            result[key] = value;
        }
    }
    return result;
}

/**
 * 加载配置。优先级：
 * 1. 指定路径的 km.config.json
 * 2. workspace 根目录的 km.config.json
 * 3. DEFAULT_CONFIG
 */
function loadConfig(workspaceRoot, configPath) {
    let userConfig = {};
    const candidates = [
        configPath,
        path.join(workspaceRoot, 'km.config.json'),
    ].filter(Boolean);

    for (const p of candidates) {
        try {
            const raw = fs.readFileSync(p, 'utf-8');
            userConfig = JSON.parse(raw);
            break;
        } catch {
            // 文件不存在或解析失败，继续
        }
    }

    const merged = deepMerge(DEFAULT_CONFIG, userConfig);
    const resolved = resolveEnvVarsDeep(merged);

    resolved._workspaceRoot = workspaceRoot;
    resolved._logDirAbs = path.resolve(workspaceRoot, resolved.logDir);
    resolved._kbDirAbs = path.resolve(workspaceRoot, resolved.kbDir);
    resolved._outputDirAbs = path.resolve(workspaceRoot, resolved.outputDir);
    resolved._backupDirAbs = path.resolve(workspaceRoot, resolved.backupDir);
    resolved._statePath = path.resolve(workspaceRoot, resolved.kbDir, resolved.stateFile);
    resolved._embCachePath = path.resolve(workspaceRoot, resolved.kbDir, resolved.embeddingsCacheFile);

    return resolved;
}

module.exports = { loadConfig, DEFAULT_CONFIG };
