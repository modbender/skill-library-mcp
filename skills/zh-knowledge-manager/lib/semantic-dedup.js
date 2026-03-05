/**
 * 语义去重（bge-m3 via SiliconFlow / OpenAI compatible API）
 * 将条目文本转为向量，余弦相似度比较
 * 可选 opt-in，默认关闭
 */
const fs = require('fs');

/**
 * 调用 embedding API 获取文本向量
 * @param {string} text - 输入文本
 * @param {object} embConfig - config.ai.embedding
 * @returns {Promise<number[]>} 向量数组
 */
async function getEmbedding(text, embConfig) {
    const { endpoint, model, apiKey } = embConfig;
    if (!apiKey) throw new Error('Embedding API key 未配置');

    const body = { model, input: text };

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Embedding API 错误 (${response.status}): ${errText}`);
    }

    const result = await response.json();
    return result.data[0].embedding;
}

function cosineSimilarity(a, b) {
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * 加载向量缓存
 */
function loadEmbeddingsCache(cachePath) {
    try {
        const raw = fs.readFileSync(cachePath, 'utf-8');
        return JSON.parse(raw);
    } catch {
        return {};
    }
}

function saveEmbeddingsCache(cachePath, cache) {
    fs.writeFileSync(cachePath, JSON.stringify(cache), 'utf-8');
}

/**
 * 获取条目的向量（优先从缓存读取）
 * @param {object} entry
 * @param {string} hash - 条目的 content hash
 * @param {object} cache - 向量缓存
 * @param {object} embConfig
 * @returns {Promise<number[]>}
 */
async function getEntryEmbedding(entry, hash, cache, embConfig) {
    if (cache[hash]) return cache[hash];

    const text = `${entry.title} ${entry.body}`;
    const embedding = await getEmbedding(text, embConfig);
    cache[hash] = embedding;
    return embedding;
}

/**
 * 语义去重检查：将新条目与目标文件中的已有条目比较
 * @param {object} newEntry - 新条目
 * @param {string} newHash - 新条目的 hash
 * @param {string} targetPath - 目标 kb/ 文件路径
 * @param {object} state - 同步状态（hash → filePath）
 * @param {object} cache - 向量缓存
 * @param {object} embConfig - embedding 配置
 * @returns {Promise<{action:'write'|'suspect'|'skip', similar?:{hash:string, similarity:number}}>}
 */
async function semanticCheck(newEntry, newHash, targetPath, state, cache, embConfig) {
    const { threshold } = embConfig;
    const newVec = await getEntryEmbedding(newEntry, newHash, cache, embConfig);

    const existingHashes = Object.entries(state.hashes)
        .filter(([, p]) => p === targetPath)
        .map(([h]) => h);

    let maxSim = 0;
    let mostSimilarHash = null;

    for (const existingHash of existingHashes) {
        if (!cache[existingHash]) continue;
        const sim = cosineSimilarity(newVec, cache[existingHash]);
        if (sim > maxSim) {
            maxSim = sim;
            mostSimilarHash = existingHash;
        }
    }

    if (maxSim >= threshold.skip) {
        return { action: 'skip', similar: { hash: mostSimilarHash, similarity: maxSim } };
    }
    if (maxSim >= threshold.suspect) {
        return { action: 'suspect', similar: { hash: mostSimilarHash, similarity: maxSim } };
    }
    return { action: 'write' };
}

module.exports = {
    getEmbedding,
    cosineSimilarity,
    loadEmbeddingsCache,
    saveEmbeddingsCache,
    semanticCheck,
};
